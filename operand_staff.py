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
from operand import *

class Staff(Operand):
    def __init__(self):
        from operand_unit import Tempo
        from operand_unit import Key
        from operand_unit import Octave
        from operand_unit import Velocity
        from operand_unit import ValueUnit
        from operand_unit import Channel
        from operand_value import Measure
        from operand_value import BeatsPerMeasure
        from operand_value import BeatNoteValue
        from operand_value import Quantization
        from operand_generic import Device
        from operand_length import Duration
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._measure: Measure                      = None
        self._tempo: Tempo                          = None
        # Time Signature is BeatsPerMeasure / BeatNoteValue like 4/4
        self._beats_per_measure: BeatsPerMeasure    = None
        self._beat_note_value: BeatNoteValue        = None
        self._quantization: Quantization            = None
        self._duration: Duration                    = None
        self._key: Key                              = None
        self._octave: Octave                        = None
        self._velocity: Velocity                    = None
        self._value_unit: ValueUnit                 = None
        self._channel: Channel                      = None
        self._device: Device                        = None

    def __mod__(self, operand: Operand) -> Operand:
        from operand_unit import Tempo
        from operand_unit import Key
        from operand_unit import Octave
        from operand_unit import Velocity
        from operand_unit import ValueUnit
        from operand_unit import Channel
        from operand_value import Measure
        from operand_value import BeatsPerMeasure
        from operand_value import BeatNoteValue
        from operand_value import Quantization
        from operand_value import NotesPerMeasure
        from operand_value import StepsPerMeasure
        from operand_value import StepsPerNote
        from operand_generic import Device
        from operand_length import Duration
        match operand:
            # Direct Values
            case Measure():         return self._measure
            case Tempo():           return self._tempo
            case BeatsPerMeasure(): return self._beats_per_measure
            case BeatNoteValue():   return self._beat_note_value
            case Quantization():    return self._quantization
            case Duration():        return self._duration
            case Key():             return self._key
            case Octave():          return self._octave
            case Velocity():        return self._velocity
            case ValueUnit():       return self._value_unit
            case Channel():         return self._channel
            case Device():          return self._device
            # Calculated Values
            case NotesPerMeasure(): return NotesPerMeasure((self % BeatsPerMeasure() % float()) * (self % BeatNoteValue() % float()))
            case StepsPerMeasure(): return StepsPerMeasure((self % StepsPerNote() % float()) * (self % NotesPerMeasure() % float()))
            case StepsPerNote():    return StepsPerNote(1 / (self._quantization % float()))
        return operand

    def getSerialization(self):
        from operand_unit import Tempo
        from operand_unit import Key
        from operand_unit import Octave
        from operand_unit import Velocity
        from operand_unit import ValueUnit
        from operand_unit import Channel
        from operand_value import Measure
        from operand_value import BeatsPerMeasure
        from operand_value import BeatNoteValue
        from operand_value import Quantization
        from operand_generic import Device
        from operand_length import Duration
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
        from operand_unit import Tempo
        from operand_unit import Key
        from operand_unit import Octave
        from operand_unit import Velocity
        from operand_unit import ValueUnit
        from operand_unit import Channel
        from operand_value import Measure
        from operand_value import BeatsPerMeasure
        from operand_value import BeatNoteValue
        from operand_value import Quantization
        from operand_generic import Device
        from operand_length import Duration
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measures" in serialization and "tempo" in serialization and
            "quantization" in serialization and "beats_per_measure" in serialization and "beat_note_value" in serialization and
            "duration" in serialization and "key" in serialization and
            "octave" in serialization and "velocity" in serialization and "value_unit" in serialization and
            "channel" in serialization and "device" in serialization):

            self._measures = Measure(serialization["measures"])
            self._tempo = Tempo(serialization["tempo"])
            self._beats_per_measure = BeatsPerMeasure(serialization["beats_per_measure"])
            self._beat_note_value = BeatNoteValue(serialization["beat_note_value"])
            self._quantization = Quantization(serialization["quantization"])
            self._duration = Duration(serialization["duration"])
            self._key = Key(serialization["key"])
            self._octave = Octave(serialization["octave"])
            self._velocity = Velocity(serialization["velocity"])
            self._value_unit = ValueUnit(serialization["value_unit"])
            self._channel = Channel(serialization["channel"])
            self._device = Device(serialization["device"])
        return self
        
    def __lshift__(self, operand: Operand) -> 'Staff':
        from operand_unit import Tempo
        from operand_unit import Key
        from operand_unit import Octave
        from operand_unit import Velocity
        from operand_unit import ValueUnit
        from operand_unit import Channel
        from operand_value import Measure
        from operand_value import BeatsPerMeasure
        from operand_value import BeatNoteValue
        from operand_value import Quantization
        from operand_generic import Device
        from operand_length import Duration
        match operand:
            case Measure():         self._measure = operand
            case Tempo():           self._tempo = operand
            case BeatsPerMeasure(): self._beats_per_measure = operand
            case BeatNoteValue():   self._beat_note_value = operand
            case Quantization():    self._quantization = operand
            case Duration():        self._duration = operand
            case Key():             self._key = operand
            case Octave():          self._octave = operand
            case Velocity():        self._velocity = operand
            case ValueUnit():       self._value_unit = operand
            case Channel():         self._channel = operand
            case Device():          self._device = operand
        return self

global_staff: Staff = Staff()
