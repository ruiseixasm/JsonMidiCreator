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
# Json Midi Creator Libraries
from operand import Operand
import operand_unit as ou
import operand_value as ov
import operand_length as ol
import operand_data as od

class Staff(Operand):
    def __init__(self):
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._measure: ov.Measure                      = None
        self._tempo: ou.Tempo                          = None
        # Time Signature is BeatsPerMeasure / BeatNoteValue like 4/4
        self._beats_per_measure: ov.BeatsPerMeasure    = None
        self._beat_note_value: ov.BeatNoteValue        = None
        self._quantization: ov.Quantization            = None
        self._duration: ol.Duration                    = None
        self._key: ou.Key                              = None
        self._octave: ou.Octave                        = None
        self._velocity: ou.Velocity                    = None
        self._value_unit: ou.ValueUnit                 = None
        self._channel: ou.Channel                      = None
        self._device: od.Device                        = None

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            # Direct Values
            case ov.Measure():         return self._measure
            case ou.Tempo():           return self._tempo
            case ov.BeatsPerMeasure(): return self._beats_per_measure
            case ov.BeatNoteValue():   return self._beat_note_value
            case ov.Quantization():    return self._quantization
            case ol.Duration():        return self._duration
            case ou.Key():             return self._key
            case ou.Octave():          return self._octave
            case ou.Velocity():        return self._velocity
            case ou.ValueUnit():       return self._value_unit
            case ou.Channel():         return self._channel
            case od.Device():          return self._device
            # Calculated Values
            case ov.NotesPerMeasure():
                return ov.NotesPerMeasure((self % ov.BeatsPerMeasure() % float()) * (self % ov.BeatNoteValue() % float()))
            case ov.StepsPerMeasure():
                return ov.StepsPerMeasure((self % ov.StepsPerNote() % float()) * (self % ov.NotesPerMeasure() % float()))
            case ov.StepsPerNote():
                return ov.StepsPerNote(1 / (self._quantization % float()))
        return operand

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "measures": self._measure % float(),
            "tempo": self._tempo % int(),
            "beats_per_measure": self._beats_per_measure % float(),
            "beat_note_value": self._beat_note_value % float(),
            "quantization": self._quantization % float(),
            "duration": self._duration.getSerialization(),
            "key": self._key % int(),
            "octave": self._octave % int(),
            "velocity": self._velocity % int(),
            "value_unit": self._value_unit % int(),
            "channel": self._channel % int(),
            "device": self._device % list()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measures" in serialization and "tempo" in serialization and
            "quantization" in serialization and "beats_per_measure" in serialization and "beat_note_value" in serialization and
            "duration" in serialization and "key" in serialization and
            "octave" in serialization and "velocity" in serialization and "value_unit" in serialization and
            "channel" in serialization and "device" in serialization):

            self._measures = ov.Measure(serialization["measures"])
            self._tempo = ou.Tempo(serialization["tempo"])
            self._beats_per_measure = ov.BeatsPerMeasure(serialization["beats_per_measure"])
            self._beat_note_value = ov.BeatNoteValue(serialization["beat_note_value"])
            self._quantization = ov.Quantization(serialization["quantization"])
            self._duration = ol.Duration(serialization["duration"])
            self._key = ou.Key(serialization["key"])
            self._octave = ou.Octave(serialization["octave"])
            self._velocity = ou.Velocity(serialization["velocity"])
            self._value_unit = ou.ValueUnit(serialization["value_unit"])
            self._channel = ou.Channel(serialization["channel"])
            self._device = od.Device(serialization["device"])
        return self
        
    def __lshift__(self, operand: Operand) -> 'Staff':
        match operand:
            case ov.Measure():         self._measure = operand
            case ou.Tempo():           self._tempo = operand
            case ov.BeatsPerMeasure(): self._beats_per_measure = operand
            case ov.BeatNoteValue():   self._beat_note_value = operand
            case ov.Quantization():    self._quantization = operand
            case ol.Duration():        self._duration = operand
            case ou.Key():             self._key = operand
            case ou.Octave():          self._octave = operand
            case ou.Velocity():        self._velocity = operand
            case ou.ValueUnit():       self._value_unit = operand
            case ou.Channel():         self._channel = operand
            case od.Device():          self._device = operand
        return self

global_staff: Staff = Staff()