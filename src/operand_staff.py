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
from fractions import Fraction
# Json Midi Creator Libraries
import operand as o
import operand_unit as ou
import operand_rational as ro
import operand_time as ot
import operand_data as od
import operand_generic as og
import operand_frame as of
import operand_label as ol


class Staff(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._measure: ro.Measure                   = ro.Measure(8)
        self._tempo: ro.Tempo                       = ro.Tempo(120.0)
        self._time_signature: og.TimeSignature      = og.TimeSignature(4, 4)
        # Key Signature is an alias of Sharps and Flats of a Scale
        self._key_signature: ou.KeySignature        = ou.KeySignature(0)
        self._key: ou.Key                           = ou.Key("C")
        self._tonic_key: ou.Key                     = ou.Key("C")
        self._scale: od.Scale                       = od.Scale([])  # By default, it has no scale besides the one given by the Key Signature
        self._quantization: ro.Quantization         = ro.Quantization(1/16)
        self._duration: ot.Duration                 = ot.Duration() << ro.NoteValue(1/4)
        self._octave: ou.Octave                     = ou.Octave(4)
        self._velocity: ou.Velocity                 = ou.Velocity(100)
        self._controller: og.Controller             = og.Controller("Pan") \
                                                        << ou.Value( ou.Number.getDefault("Pan") )
        self._channel: ou.Channel                   = ou.Channel(1)
        self._device: od.Device                     = od.Device(["Microsoft", "FLUID", "Apple"])
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
                    case ro.Measure():          return self._measure
                    case ro.Tempo():            return self._tempo
                    case og.TimeSignature():    return self._time_signature
                    case ou.KeySignature():     return self._key_signature
                    case ou.Key():              return self._key
                    case ro.BeatsPerMeasure():  return self._time_signature % od.DataSource( ro.BeatsPerMeasure() )
                    case ro.BeatNoteValue():    return self._time_signature % od.DataSource( ro.BeatNoteValue() )
                    case od.Scale():            return self._scale
                    case ro.Quantization():     return self._quantization
                    case ot.Duration():         return self._duration
                    case ou.Octave():           return self._octave
                    case ou.Velocity():         return self._velocity
                    case og.Controller():       return self._controller
                    case ou.Channel():          return self._channel
                    case od.Device():           return self._device
                    # Calculated Values
                    case ro.NotesPerMeasure():
                        return self._time_signature % od.DataSource( ro.NotesPerMeasure() )
                    case ro.StepsPerNote():
                        return ro.StepsPerNote() << od.DataSource( 1 / (self._quantization % od.DataSource( Fraction() )) )
                    case ro.StepsPerMeasure():
                        return ro.StepsPerMeasure() \
                            << od.DataSource( self % od.DataSource( ro.StepsPerNote() ) % od.DataSource( Fraction() ) \
                                * (self % od.DataSource( ro.NotesPerMeasure() ) % od.DataSource( Fraction() )))
                    case Staff():               return self
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            # Direct Values
            case ro.Measure():          return self._measure.copy()
            case ro.Tempo():            return self._tempo.copy()
            case og.TimeSignature():    return self._time_signature.copy()
            case ou.KeySignature():     return self._key_signature.copy()
            case ou.Key():              return self._key.copy()
            case ro.BeatsPerMeasure():  return self._time_signature % ro.BeatsPerMeasure()
            case ro.BeatNoteValue():    return self._time_signature % ro.BeatNoteValue()
            case od.Scale():
                                    if self._scale.hasScale():
                                        return self._scale.copy()
                                    else:
                                        return self._key_signature % od.Scale()
            case ro.Quantization():     return self._quantization.copy()
            case ot.Duration():         return self._duration.copy()
            case ou.Octave():           return self._octave.copy()
            case ou.Velocity():         return self._velocity.copy()
            case og.Controller():       return self._controller.copy()
            case ou.Number():           return self._controller % ou.Number()
            case ou.Value():            return self._controller % ou.Value()
            case ou.Channel():          return self._channel.copy()
            case od.Device():           return self._device.copy()
            # Calculated Values
            case ro.NotesPerMeasure():
                return self._time_signature % ro.NotesPerMeasure()
            case ro.StepsPerNote():
                return ro.StepsPerNote() << 1 / (self._quantization % Fraction())
            case ro.StepsPerMeasure():
                return ro.StepsPerMeasure() \
                    << (self % ro.StepsPerNote() % Fraction()) * (self % ro.NotesPerMeasure() % Fraction())
            case Staff():               return self.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_staff: 'Staff') -> bool:
        other_staff = self & other_staff    # Processes the tailed self operands or the Frame operand if any exists
        if other_staff.__class__ == o.Operand:
            return True
        if type(self) != type(other_staff):
            return False
        return  self._measure           == other_staff % od.DataSource( ro.Measure() ) \
            and self._tempo             == other_staff % od.DataSource( ro.Tempo() ) \
            and self._time_signature    == other_staff % od.DataSource( og.TimeSignature() ) \
            and self._key_signature     == other_staff % od.DataSource( ou.KeySignature() ) \
            and self._key               == other_staff % od.DataSource( ou.Key() ) \
            and self._scale             == other_staff % od.DataSource( od.Scale() ) \
            and self._quantization      == other_staff % od.DataSource( ro.Quantization() ) \
            and self._duration          == other_staff % od.DataSource( ot.Duration() ) \
            and self._octave            == other_staff % od.DataSource( ou.Octave() ) \
            and self._velocity          == other_staff % od.DataSource( ou.Velocity() ) \
            and self._controller        == other_staff % od.DataSource( og.Controller() ) \
            and self._channel           == other_staff % od.DataSource( ou.Channel() ) \
            and self._device            == other_staff % od.DataSource( od.Device() )
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "measures":             self._measure % od.DataSource( str() ),
                "tempo":                self._tempo % od.DataSource( str() ),
                "time_signature":       self._time_signature.getSerialization(),
                "key_signature":        self._key_signature.getSerialization(),
                "key":                  self._key % od.DataSource( int() ),
                "scale":                self._scale % od.DataSource( list() ),
                "quantization":         self._quantization % od.DataSource( str() ),
                "duration":             self._duration.getSerialization(),
                "octave":               self._octave % od.DataSource( int() ),
                "velocity":             self._velocity % od.DataSource( int() ),
                "controller":           self._controller.getSerialization(),
                "channel":              self._channel % od.DataSource( int() ),
                "device":               self._device % od.DataSource( list() )
            }
        }

    # CHAINABLE OPERATIONS

    def set_tonic_key(self):
        if self._scale % od.DataSource( list() ) == []:
            circle_fifths_position: int = self._key_signature % int()
            self._tonic_key._unit = (self._key._unit + circle_fifths_position * 7) % 12
        else:
            self._tonic_key._unit = self._key._unit
        
    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "measures" in serialization["parameters"] and "tempo" in serialization["parameters"] and "time_signature" in serialization["parameters"] and
            "key_signature" in serialization["parameters"] and "quantization" in serialization["parameters"] and
            "scale" in serialization["parameters"] and "duration" in serialization["parameters"] and "key" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "velocity" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "device" in serialization["parameters"]):

            self._measures          = ro.Measure()          << od.DataSource( serialization["parameters"]["measures"] )
            self._tempo             = ro.Tempo()            << od.DataSource( serialization["parameters"]["tempo"] )
            self._time_signature    = og.TimeSignature().loadSerialization(serialization["parameters"]["time_signature"])
            self._key_signature     = ou.KeySignature().loadSerialization(serialization["parameters"]["key_signature"])
            self._key               = ou.Key()              << od.DataSource( serialization["parameters"]["key"] )
            self._scale             = od.Scale()            << od.DataSource( serialization["parameters"]["scale"] )
            self._quantization      = ro.Quantization()     << od.DataSource( serialization["parameters"]["quantization"] )
            self._duration          = ot.Duration()         << od.DataSource( serialization["parameters"]["duration"] )
            self._octave            = ou.Octave()           << od.DataSource( serialization["parameters"]["octave"] )
            self._velocity          = ou.Velocity()         << od.DataSource( serialization["parameters"]["velocity"] )
            self._controller        = og.Controller().loadSerialization(serialization["parameters"]["controller"])
            self._channel           = ou.Channel()          << od.DataSource( serialization["parameters"]["channel"] )
            self._device            = od.Device()           << od.DataSource( serialization["parameters"]["device"] )
            self.set_tonic_key()
        return self
    
    def __lshift__(self, operand: o.Operand) -> 'Staff':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.Measure():          self._measure = operand % o.Operand()
                    case ro.Tempo():            self._tempo = operand % o.Operand()
                    case og.TimeSignature():    self._time_signature = operand % o.Operand()
                    case ou.KeySignature():
                        self._key_signature = operand % o.Operand()
                        self.set_tonic_key()
                    case ou.Key():
                        self._key._unit = operand % o.Operand() % int() % 12
                        self.set_tonic_key()
                    case ro.BeatsPerMeasure() | ro.BeatNoteValue():
                                                self._time_signature << od.DataSource( operand % o.Operand() )
                    case od.Scale():
                        self._scale = operand % o.Operand()
                        self.set_tonic_key()
                    case ro.Quantization():     self._quantization = operand % o.Operand()    # Note Value
                    case ot.Duration():         self._duration = operand % o.Operand()
                    case ou.Octave():           self._octave = operand % o.Operand()
                    case ou.Velocity():         self._velocity = operand % o.Operand()
                    case og.Controller():       self._controller = operand % o.Operand()
                    case ou.Channel():          self._channel = operand % o.Operand()
                    case od.Device():           self._device = operand % o.Operand()
            case Staff():
                self._measure           << operand._measure
                self._tempo             << operand._tempo
                self._time_signature    << operand._time_signature
                self._key_signature     << operand._key_signature
                self._key               << operand._key
                self._scale             << operand._scale
                self._quantization      << operand._quantization
                self._duration          << operand._duration
                self._octave            << operand._octave
                self._velocity          << operand._velocity
                self._controller        << operand._controller
                self._channel           << operand._channel
                self._device            << operand._device
                self.set_tonic_key()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ro.Measure():          self._measure << operand
            case ro.Tempo():            self._tempo << operand
            case og.TimeSignature() | ro.BeatsPerMeasure() | ro.BeatNoteValue():
                                        self._time_signature << operand
            case ou.KeySignature():
                                        self._key_signature << operand
                                        self.set_tonic_key()
            case ou.Key():
                                        self._key._unit = operand % int() % 12
                                        self.set_tonic_key()
            case od.Scale():
                                        self._scale << operand
                                        self.set_tonic_key()
            case ro.Quantization():     self._quantization << operand # Note Value
            case ot.Duration():         self._duration << operand
            case ou.Octave():           self._octave << operand
            case ou.Velocity():         self._velocity << operand
            case og.Controller() | ou.Number() | ou.Value():
                                        self._controller << operand
            case ou.Channel():          self._channel << operand
            case od.Device():           self._device << operand
            # Calculated Values
            case ro.StepsPerMeasure():
                self._quantization = ro.Quantization( (self % ro.NotesPerMeasure()) / (operand % Fraction()) )
            case ro.StepsPerNote():
                self._quantization = ro.Quantization( 1 / (operand % Fraction()) )
            case int():
                self._tempo << operand
            case float():
                self._tempo << operand
            case Fraction():
                ...
            case str():
                self._tempo << operand
                self._key_signature << operand
                self.set_tonic_key()
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

# Instantiate the Global Staff here.
staff: Staff = Staff()
