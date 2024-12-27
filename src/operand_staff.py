'''
JsonMidiCreator - Json Midi Creator is intended to be used
in conjugation with the Json Midi Player to Play composed Elements
Original Copyright (c) 2024 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
https://github.com/ruiseixasm/JsonMidiCreator
https://github.com/ruiseixasm/JsonMidiPlayer
'''
# Example using typing.Union (compatible with Python < 3.10)
from typing import Union, TypeVar, TYPE_CHECKING
from fractions import Fraction
import time
import sys
# Json Midi Creator Libraries
import operand as o
import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_generic as og
import operand_frame as of
import operand_label as ol
import operand_chaos as ch

TypeStaff = TypeVar('TypeStaff', bound='Staff')  # TypeStaff represents any subclass of Operand


class Staff(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._tempo: ra.Tempo                       = ra.Tempo(120.0)
        self._time_signature: og.TimeSignature      = og.TimeSignature(4, 4)
        self._quantization: ra.Quantization         = ra.Quantization(1/16)
        # Key Signature is an alias of Sharps and Flats of a Scale
        self._key_signature: ou.KeySignature        = ou.KeySignature()
        self._measures: ra.Measures                   = ra.Measures(8)
        self._note_value: ra.NoteValue                 = ra.NoteValue(1/4)
        self._octave: ou.Octave                     = ou.Octave(4)
        self._velocity: ou.Velocity                 = ou.Velocity(100)
        self._controller: og.Controller             = og.Controller("Pan") \
                                                        << ou.Value( ou.Number.getDefault("Pan") )
        self._channel: ou.Channel                   = ou.Channel(1)
        self._device: od.Device                     = od.Device(["Microsoft", "FLUID", "Apple"])
        self._chaos: ch.Chaos                       = ch.SinX() * (int(time.time() * 10000) % 100)
        self._chaos << ra.Lambda( self._chaos % ra.Lambda() + int(time.time() * 10000) % 100 )   # Lambda is the SinX chaotic blueprint !!
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Staff,
        those Parameters are the ones that define a Staff as global defaults,
        they include the ones relative to the time signature like Beats per Measure
        and Neat Note Value, the Tempo, the Quantization among others.

        Examples
        --------
        >>> staff % Tempo() % float()
        120.0
        >>> staff << BeatsPerMeasure(3)
        >>> staff % BeatsPerMeasure() % float()
        3.0
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case ra.Tempo():            return self._tempo
                    case og.TimeSignature():    return self._time_signature
                    case ra.Quantization():     return self._quantization
                    case ou.KeySignature():     return self._key_signature
                    case ra.BeatsPerMeasure():  return self._time_signature % od.DataSource( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.DataSource( ra.BeatNoteValue() )
                    case ra.Measures():          return self._measures
                    case ra.NoteValue():         return self._note_value
                    case ou.Octave():           return self._octave
                    case ou.Velocity():         return self._velocity
                    case og.Controller():       return self._controller
                    case ou.Channel():          return self._channel
                    case od.Device():           return self._device
                    case ch.Chaos():            return self._chaos
                    # Calculated Values
                    case ra.NotesPerMeasure():
                        return self._time_signature % od.DataSource( ra.NotesPerMeasure() )
                    case ra.StepsPerNote():
                        return ra.StepsPerNote() << od.DataSource( 1 / (self._quantization % od.DataSource( Fraction() )) )
                    case ra.StepsPerMeasure():
                        return ra.StepsPerMeasure() \
                            << od.DataSource( self % od.DataSource( ra.StepsPerNote() ) % od.DataSource( Fraction() ) \
                                * (self % od.DataSource( ra.NotesPerMeasure() ) % od.DataSource( Fraction() )))
                    case Staff():               return self
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            # Direct Values
            case ra.Tempo():            return self._tempo.copy()
            case og.TimeSignature():    return self._time_signature.copy()
            case ra.Quantization():     return self._quantization.copy()
            case ou.KeySignature():     return self._key_signature.copy()
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                                        return self._key_signature % operand
            case ra.BeatsPerMeasure():  return self._time_signature % ra.BeatsPerMeasure()
            case ra.BeatNoteValue():    return self._time_signature % ra.BeatNoteValue()
            case ra.Measures():          return self._measures.copy()
            case ra.NoteValue():         return self._note_value.copy()
            case ou.Octave():           return self._octave.copy()
            case ou.Velocity():         return self._velocity.copy()
            case og.Controller():       return self._controller.copy()
            case ou.Number():           return self._controller % ou.Number()
            case ou.Value():            return self._controller % ou.Value()
            case ou.Channel():          return self._channel.copy()
            case od.Device():           return self._device.copy()
            case ch.Chaos():            return self._chaos.copy()
            # Calculated Values
            case ra.NotesPerMeasure():
                return self._time_signature % ra.NotesPerMeasure()
            case ra.StepsPerNote():
                return ra.StepsPerNote() << 1 / (self._quantization % Fraction())
            case ra.StepsPerMeasure():
                return ra.StepsPerMeasure() \
                    << (self % ra.StepsPerNote() % Fraction()) * (self % ra.NotesPerMeasure() % Fraction())
            case Staff():               return self.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Staff') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._tempo             == other % od.DataSource( ra.Tempo() ) \
            and self._time_signature    == other % od.DataSource( og.TimeSignature() ) \
            and self._quantization      == other % od.DataSource( ra.Quantization() ) \
            and self._key_signature     == other % od.DataSource( ou.KeySignature() ) \
            and self._measures           == other % od.DataSource( ra.Measures() ) \
            and self._note_value          == other % od.DataSource( ra.NoteValue() ) \
            and self._octave            == other % od.DataSource( ou.Octave() ) \
            and self._velocity          == other % od.DataSource( ou.Velocity() ) \
            and self._controller        == other % od.DataSource( og.Controller() ) \
            and self._channel           == other % od.DataSource( ou.Channel() ) \
            and self._device            == other % od.DataSource( od.Device() ) \
            and self._chaos             == other % od.DataSource( ch.Chaos() )
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tempo"]            = self.serialize( self._tempo )
        serialization["parameters"]["time_signature"]   = self.serialize( self._time_signature )
        serialization["parameters"]["quantization"]     = self.serialize( self._quantization )
        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
        serialization["parameters"]["measures"]         = self.serialize( self._measures )
        serialization["parameters"]["note_value"]         = self.serialize( self._note_value )
        serialization["parameters"]["octave"]           = self.serialize( self._octave )
        serialization["parameters"]["velocity"]         = self.serialize( self._velocity )
        serialization["parameters"]["controller"]       = self.serialize( self._controller )
        serialization["parameters"]["channel"]          = self.serialize( self._channel )
        serialization["parameters"]["device"]           = self.serialize( self._device )
        serialization["parameters"]["chaos"]            = self.serialize( self._chaos )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Staff':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "measures" in serialization["parameters"] and "tempo" in serialization["parameters"] and "time_signature" in serialization["parameters"] and
            "key_signature" in serialization["parameters"] and "quantization" in serialization["parameters"] and
            "note_value" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "velocity" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "device" in serialization["parameters"] and
            "chaos" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempo             = self.deserialize( serialization["parameters"]["tempo"] )
            self._time_signature    = self.deserialize( serialization["parameters"]["time_signature"] )
            self._quantization      = self.deserialize( serialization["parameters"]["quantization"] )
            self._key_signature     = self.deserialize( serialization["parameters"]["key_signature"] )
            self._measures          = self.deserialize( serialization["parameters"]["measures"] )
            self._note_value          = self.deserialize( serialization["parameters"]["note_value"] )
            self._octave            = self.deserialize( serialization["parameters"]["octave"] )
            self._velocity          = self.deserialize( serialization["parameters"]["velocity"] )
            self._controller        = self.deserialize( serialization["parameters"]["controller"] )
            self._channel           = self.deserialize( serialization["parameters"]["channel"] )
            self._device            = self.deserialize( serialization["parameters"]["device"] )
            self._chaos             = self.deserialize( serialization["parameters"]["chaos"] )
        return self
    
    def __lshift__(self, operand: o.Operand) -> 'Staff':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ra.Tempo():            self._tempo = operand % o.Operand()
                    case og.TimeSignature():    self._time_signature = operand % o.Operand()
                    case ra.Quantization():     self._quantization = operand % o.Operand()    # Note Value
                    case ou.KeySignature():     self._key_signature = operand % o.Operand()
                    case ra.BeatsPerMeasure() | ra.BeatNoteValue():
                                                self._time_signature << od.DataSource( operand % o.Operand() )
                    case ra.Measures():          self._measures = operand % o.Operand()
                    case ra.NoteValue():         self._note_value = operand % o.Operand()
                    case ou.Octave():           self._octave = operand % o.Operand()
                    case ou.Velocity():         self._velocity = operand % o.Operand()
                    case og.Controller():       self._controller = operand % o.Operand()
                    case ou.Channel():          self._channel = operand % o.Operand()
                    case od.Device():           self._device = operand % o.Operand()
                    case ch.Chaos():            self._chaos = operand % o.Operand()
            case Staff():
                super().__lshift__(operand)
                self._tempo             << operand._tempo
                self._time_signature    << operand._time_signature
                self._quantization      << operand._quantization
                self._key_signature     << operand._key_signature
                self._measures           << operand._measures
                self._note_value          << operand._note_value
                self._octave            << operand._octave
                self._velocity          << operand._velocity
                self._controller        << operand._controller
                self._channel           << operand._channel
                self._device            << operand._device
                self._chaos             << operand._chaos
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Tempo():            self._tempo << operand
            case og.TimeSignature() | ra.BeatsPerMeasure() | ra.BeatNoteValue():
                                        self._time_signature << operand
            case ra.Quantization():     self._quantization << operand # Note Value
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                                        self._key_signature << operand
            case ra.Measures():          self._measures << operand
            case ra.NoteValue():         self._note_value << operand
            case ou.Octave():           self._octave << operand
            case ou.Velocity():         self._velocity << operand
            case og.Controller() | ou.Number() | ou.Value():
                                        self._controller << operand
            case ou.Channel():          self._channel << operand
            case od.Device():           self._device << operand
            case ch.Chaos():            self._chaos << operand
            # Calculated Values
            case ra.StepsPerMeasure():
                self._quantization = ra.Quantization( (self % ra.NotesPerMeasure()) / (operand % Fraction()) )
            case ra.StepsPerNote():
                self._quantization = ra.Quantization( 1 / (operand % Fraction()) )
            case int():
                self._tempo << operand
            case float():
                self._tempo << operand
            case Fraction():
                ...
            case str():
                self._tempo << operand
                self._key_signature << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


# Instantiate the Global Staff here.
staff: Staff = Staff()
