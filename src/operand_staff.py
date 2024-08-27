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
import operand_value as ov
import operand_time as ot
import operand_data as od
import operand_generic as og
import operand_frame as of
import operand_label as ol


class Staff(o.Operand):
    def __init__(self):
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._measure: ov.Measure                   = ov.Measure(8)
        self._tempo: ov.Tempo                       = ov.Tempo(120.0)
        # Time Signature is BeatsPerMeasure / BeatNoteValue like 4/4
        self._beats_per_measure: ov.BeatsPerMeasure = ov.BeatsPerMeasure(4)
        self._beat_note_value: ov.BeatNoteValue     = ov.BeatNoteValue(1/4)
        # Key Signature is an alias of Sharps and Flats of a Scale
        self._scale: ou.Scale                       = ou.Scale("Major")
        self._quantization: ov.Quantization         = ov.Quantization(1/16)
        self._duration: ot.Duration                 = ot.Duration() << ov.NoteValue(1/4)
        self._key: ou.Key                           = ou.Key("C")
        self._octave: ou.Octave                     = ou.Octave(4)
        self._velocity: ou.Velocity                 = ou.Velocity(100)
        self._controller: og.Controller             = og.Controller("Pan") << ou.ControlValue( ou.ControlNumber.getDefault("Pan") )
        self._channel: ou.Channel                   = ou.Channel(1)
        self._device: od.Device                     = od.Device(["Microsoft", "FLUID", "Apple"])

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ov.Measure():          return self._measure
                    case ov.Tempo():            return self._tempo
                    case ov.BeatsPerMeasure():  return self._beats_per_measure
                    case ov.BeatNoteValue():    return self._beat_note_value
                    case ou.Scale():            return self._scale
                    case ov.Quantization():     return self._quantization
                    case ot.Duration():         return self._duration
                    case ou.Key():              return self._key
                    case ou.Octave():           return self._octave
                    case ou.Velocity():         return self._velocity
                    case og.Controller():       return self._controller
                    case ou.Channel():          return self._channel
                    case od.Device():           return self._device
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            # Direct Values
            case ov.Measure():          return self._measure.copy()
            case ov.Tempo():            return self._tempo.copy()
            case ov.BeatsPerMeasure():  return self._beats_per_measure.copy()
            case ov.BeatNoteValue():    return self._beat_note_value.copy()
            case ou.Scale():            return self._scale.copy()
            case ov.Quantization():     return self._quantization.copy()
            case ot.Duration():         return self._duration.copy()
            case ou.Key():              return self._key.copy()
            case ou.Octave():           return self._octave.copy()
            case ou.Velocity():         return self._velocity.copy()
            case og.Controller():       return self._controller.copy()
            case ou.ControlNumber():    return self._controller % ou.ControlNumber()
            case ou.ControlValue():     return self._controller % ou.ControlValue()
            case ou.Channel():          return self._channel.copy()
            case od.Device():           return self._device.copy()
            # Calculated Values
            case ov.NotesPerMeasure():
                return ov.NotesPerMeasure((self % ov.BeatsPerMeasure() % Fraction()) * (self % ov.BeatNoteValue() % Fraction()))
            case ov.StepsPerMeasure():
                return ov.StepsPerMeasure((self % ov.StepsPerNote() % Fraction()) * (self % ov.NotesPerMeasure() % Fraction()))
            case ov.StepsPerNote():
                return ov.StepsPerNote(1 / (self._quantization % Fraction()))
            case ol.Null() | None:      return ol.Null()
            case _:                     return self.copy()

    def __eq__(self, other_staff: 'Staff') -> bool:
        if type(self) != type(other_staff):
            return False
        return  self._measure == other_staff % od.DataSource( ov.Measure() ) \
            and self._tempo == other_staff % od.DataSource( ov.Tempo() ) \
            and self._beats_per_measure == other_staff % od.DataSource( ov.BeatsPerMeasure() ) \
            and self._beat_note_value == other_staff % od.DataSource( ov.BeatNoteValue() ) \
            and self._scale == other_staff % od.DataSource( ou.Scale() ) \
            and self._quantization == other_staff % od.DataSource( ov.Quantization() ) \
            and self._duration == other_staff % od.DataSource( ot.Duration() ) \
            and self._key == other_staff % od.DataSource( ou.Key() ) \
            and self._octave == other_staff % od.DataSource( ou.Octave() ) \
            and self._velocity == other_staff % od.DataSource( ou.Velocity() ) \
            and self._controller == other_staff % od.DataSource( og.Controller() ) \
            and self._channel == other_staff % od.DataSource( ou.Channel() ) \
            and self._device == other_staff % od.DataSource( od.Device() )
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "measures": self._measure % float(),
                "tempo": self._tempo % int(),
                "beats_per_measure": self._beats_per_measure % float(),
                "beat_note_value": self._beat_note_value % float(),
                "scale": self._scale.getSerialization(),
                "quantization": self._quantization % float(),
                "duration": self._duration.getSerialization(),
                "key": self._key % int(),
                "octave": self._octave % int(),
                "velocity": self._velocity % int(),
                "controller": self._controller.getSerialization(),
                "channel": self._channel % int(),
                "device": self._device % list()
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "measures" in serialization["parameters"] and "tempo" in serialization["parameters"] and
            "quantization" in serialization["parameters"] and "beats_per_measure" in serialization["parameters"] and "beat_note_value" in serialization["parameters"] and
            "scale" in serialization["parameters"] and "duration" in serialization["parameters"] and "key" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "velocity" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "device" in serialization["parameters"]):

            self._measures = ov.Measure(serialization["parameters"]["measures"])
            self._tempo = ov.Tempo(serialization["parameters"]["tempo"])
            self._beats_per_measure = ov.BeatsPerMeasure(serialization["parameters"]["beats_per_measure"])
            self._beat_note_value = ov.BeatNoteValue(serialization["parameters"]["beat_note_value"])
            self._scale = ou.Scale().loadSerialization(serialization["parameters"]["scale"])
            self._quantization = ov.Quantization(serialization["parameters"]["quantization"])
            self._duration = ot.Duration(serialization["parameters"]["duration"])
            self._key = ou.Key(serialization["parameters"]["key"])
            self._octave = ou.Octave(serialization["parameters"]["octave"])
            self._velocity = ou.Velocity(serialization["parameters"]["velocity"])
            self._controller = og.Controller().loadSerialization(serialization["parameters"]["controller"])
            self._channel = ou.Channel(serialization["parameters"]["channel"])
            self._device = od.Device(serialization["parameters"]["device"])
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Staff':
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ov.Measure():          self._measure = operand % o.Operand()
                    case ov.Tempo():            self._tempo = operand % o.Operand()
                    case ov.BeatsPerMeasure():  self._beats_per_measure = operand % o.Operand()
                    case ov.BeatNoteValue():    self._beat_note_value = operand % o.Operand()
                    case ou.Scale():            self._scale = operand % o.Operand()
                    case ov.Quantization():     self._quantization = operand % o.Operand()    # Note Value
                    case ot.Duration():         self._duration = operand % o.Operand()
                    case ou.Key():              self._key = operand % o.Operand()
                    case ou.Octave():           self._octave = operand % o.Operand()
                    case ou.Velocity():         self._velocity = operand % o.Operand()
                    case og.Controller():       self._controller = operand % o.Operand()
                    case ou.ControlNumber():    self._controller << operand % o.Operand()
                    case ou.ControlValue():     self._controller << operand % o.Operand()
                    case ou.Channel():          self._channel = operand % o.Operand()
                    case od.Device():           self._device = operand % o.Operand()
            case Staff():
                self._measure           = operand % od.DataSource( ov.Measure() )
                self._tempo             = operand % od.DataSource( ov.Tempo() )
                self._beats_per_measure = operand % od.DataSource( ov.BeatsPerMeasure() )
                self._beat_note_value   = operand % od.DataSource( ov.BeatNoteValue() )
                self._scale             = operand % od.DataSource( ou.Scale() )
                self._quantization      = operand % od.DataSource( ov.Quantization() ) # Note Value
                self._duration          = operand % od.DataSource( ot.Duration() )
                self._key               = operand % od.DataSource( ou.Key() )
                self._octave            = operand % od.DataSource( ou.Octave() )
                self._velocity          = operand % od.DataSource( ou.Velocity() )
                self._controller        = operand % od.DataSource( og.Controller() )
                self._channel           = operand % od.DataSource( ou.Channel() )
                self._device            = operand % od.DataSource( od.Device() )
            case of.Frame():            self << (operand & self)
            case od.Load():
                self.loadSerialization(operand % od.DataSource())
            case ov.Measure():          self._measure = operand.copy()
            case ov.Tempo():            self._tempo = operand.copy()
            case ov.BeatsPerMeasure():  self._beats_per_measure = operand.copy()
            case ov.BeatNoteValue():    self._beat_note_value = operand.copy()
            case ou.Scale():            self._scale = operand.copy()
            case ov.Quantization():     self._quantization = operand.copy() # Note Value
            case ot.Duration():         self._duration = operand.copy()
            case ou.Key():              self._key = operand.copy()
            case ou.Octave():           self._octave = operand.copy()
            case ou.Velocity():         self._velocity = operand.copy()
            case og.Controller():       self._controller = operand.copy()
            case ou.ControlNumber():    self._controller << operand
            case ou.ControlValue():     self._controller << operand
            case ou.Channel():          self._channel = operand.copy()
            case od.Device():           self._device = operand.copy()
            # Calculated Values
            case ov.NotesPerMeasure():
                self._beat_note_value = ov.BeatNoteValue( (operand % Fraction()) / (self % ov.BeatsPerMeasure()) )
            case ov.StepsPerMeasure():
                self._quantization = ov.Quantization( (self % ov.NotesPerMeasure()) / (operand % Fraction()) )
            case ov.StepsPerNote():
                self._quantization = ov.Quantization( 1 / (operand % Fraction()) )
        return self

# Set the Default Staff values here.
global_staff: Staff = Staff()
