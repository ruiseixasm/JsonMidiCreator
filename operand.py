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
from typing import Union

class Operand:
    def __mod__(self, operand: 'Operand') -> 'Operand':
        return operand

class Null(Operand):
    pass

class Staff(Operand):

    def __init__(self):
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
        return {
            "class": self.__class__.__name__,
            "measures": self._measure,
            "tempo": self._tempo,
            "beats_per_measure": self._beats_per_measure,
            "beat_note_value": self._beat_note_value,
            "quantization": self._quantization,
            "duration": self._duration,
            "key": self._key,
            "octave": self._octave,
            "velocity": self._velocity,
            "value_unit": self._value_unit,
            "channel": self._channel,
            "device_list": self._device
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measures" in serialization and "tempo" in serialization and
            "quantization" in serialization and "beats_per_measure" in serialization and "beat_note_value" in serialization and
            "duration" in serialization and "key" in serialization and
            "octave" in serialization and "velocity" in serialization and "value_unit" in serialization and
            "channel" in serialization and "device_list" in serialization):

            self._measures = serialization["measures"]
            self._tempo = serialization["tempo"]
            self._quantization = serialization["quantization"]
            self._beat_note_value = serialization["beats_per_measure"]
            self._time_signature = serialization["beat_note_value"]
            self._duration = serialization["duration"]
            self._key = serialization["key"]
            self._octave = serialization["octave"]
            self._velocity = serialization["velocity"]
            self._value_unit = serialization["value_unit"]
            self._channel = serialization["channel"]
            self._device_list = serialization["device_list"]

        return self
        
    def __lshift__(self, operand: Operand) -> 'Staff':
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


# Units have never None values and are also const, with no setters
class Unit(Operand):
    def __init__(self, unit: int = None):
        self._unit: int = unit

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case int():     return round(self._unit)
            case float():   return round(1.0 * self._unit, 9)   # rounding to 9 avoids floating-point errors
            case _:         return operand

    def __eq__(self, other_unit: 'Unit') -> bool:
        return self % int() == other_unit % int()
    
    def __lt__(self, other_unit: 'Unit') -> bool:
        return self % int() < other_unit % int()
    
    def __gt__(self, other_unit: 'Unit') -> bool:
        return self % int() > other_unit % int()
    
    def __le__(self, other_unit: 'Unit') -> bool:
        return not (self > other_unit)
    
    def __ge__(self, other_unit: 'Unit') -> bool:
        return not (self < other_unit)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "unit": self._unit
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "unit" in serialization):

            self._unit = serialization["unit"]
        return self

    def copy(self): # read only Operand doesn't have to be duplicated, it never changes
        return self

    def __add__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__(self % int() + unit % int())
            case int() | float(): return self.__class__(self % int() + unit)
    
    def __sub__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__(self % int() - unit % int())
            case int() | float(): return self.__class__(self % int() - unit)
        return self.__class__(self % int() - unit)
    
    def __mul__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__((self % int()) * (unit % int()))
            case int() | float(): return self.__class__(self % int() * unit)
    
    def __truediv__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__((self % int()) / (unit % int()))
            case int() | float(): return self.__class__(self % int() / unit)
    
class Key(Unit):

    _keys: list[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
                        "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    
    @staticmethod
    def getKey(note_key: int = 0) -> str:
        return Key._keys[note_key % 12]

    @staticmethod
    def keyStrToKeyUnit(key: str = "C") -> int:
        key_number = 0
        for key_i in range(len(Key._keys)):
            if  Key._keys[key_i].lower().find(key.strip().lower()) != -1:
                key_number += key_i % 12
                break
        return key_number

    def __init__(self, key: str = None):
        match key:
            case str():
                super().__init__(Key.keyStrToKeyUnit(key))
            case int() | float():
                super().__init__(key)
            case _:
                super().__init__( global_staff % Key(0) % int() )

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case str():     return Key.getKey(self % int())
            case _:         return super().__mod__(operand)

class Tempo(Unit):
    def __init__(self, tempo: int = None):
        super().__init__( global_staff % Tempo(0) % int() if tempo is None else tempo )

class Octave(Unit):
    def __init__(self, octave: int = None):
        super().__init__( global_staff % Octave(0) % int() if octave is None else octave )

class Velocity(Unit):
    def __init__(self, velocity: int = None):
        super().__init__( global_staff % Velocity(0) % int() if velocity is None else velocity )

class ValueUnit(Unit):
    def __init__(self, value_unit: int = None):
        super().__init__( global_staff % ValueUnit(0) % int() if value_unit is None else value_unit )

class Channel(Unit):
    def __init__(self, channel: int = None):
        super().__init__( global_staff % Channel(0) % int() if channel is None else channel )

class Scale(Unit):
    def __init__(self, scale: int = None):
        super().__init__(scale)

    scale_mames = [
        ["Chromatic", "chromatic"],
        # Diatonic Scales
        ["Major", "Maj", "Ionian"],
        ["Dorian"],
        ["Phrygian"],
        ["Lydian"],
        ["Mixolydian"],
        ["minor", "min", "Aeolian"],
        ["Locrian"],
        # Other Scales
        ["harmonic"],
        ["melodic"],
        ["octatonic_hw"],
        ["octatonic_wh"],
        ["pentatonic_maj"],
        ["pentatonic_min"],
        ["diminished"],
        ["augmented"],
        ["blues"]
    ]
    scales = [
    #       Db    Eb       Gb    Ab    Bb
    #       C#    D#       F#    G#    A#
    #    C     D     E  F     G     A     B
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        # Diatonic Scales
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        # Other Scales
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
        [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
        [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0]
    ]

class Pitch(Unit):
    def __init__(self, pitch: int = None):
        if pitch is None:
            pitch = 0
        super().__init__(pitch)

class KeyNote(Operand):

    def __init__(self):
        self._key: Key = Key()
        self._octave: Octave = Octave()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Key():     return self._key
            case Octave():  return self._octave
            case _:         return operand

    def getValue__midi_key_note(self) -> int:
        key = self._key % int()
        octave = self._octave % int()
        return 12 * (octave + 1) + key
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "key": self._key.getSerialization(),
            "octave": self._octave.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "key" in serialization and "octave" in serialization):

            self._key = Key(serialization["key"])
            self._octave = Octave(serialization["octave"])
        return self
        
    def copy(self) -> 'KeyNote':
        return KeyNote() << self._key << self._octave

    def __lshift__(self, operand: Operand) -> 'KeyNote':
        if operand.__class__ == Key:    self._measure = operand
        if operand.__class__ == Octave: self._beat = operand
        return self

    def __add__(self, unit) -> 'KeyNote':
        key: Key = self._key
        octave: Octave = self._octave
        match unit:
            case Key():
                key += unit
            case Octave():
                octave += unit
            case _:
                return self.copy()

        return KeyNote(
            key     = key.getData(),
            octave  = octave.getData()
        )
     
    def __sub__(self, unit) -> 'KeyNote':
        key: Key = self._key
        octave: Octave = self._octave
        match unit:
            case Key():
                key -= unit
            case Octave():
                octave -= unit
            case _:
                return self.copy()

        return KeyNote(
            key     = key.getData(),
            octave  = octave.getData()
        )


# Values have never None values and are also const, with no setters
class Value(Operand):

    def __init__(self, value: float = None):
        self._value: float = 0 if value is None else value

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case float():   return round(1.0 * self._value, 9)  # rounding to 9 avoids floating-point errors
            case int():     return round(self._value)
            case _:         return operand

    def __eq__(self, other_value: 'Value') -> bool:
        return self % float() == other_value % float()
    
    def __lt__(self, other_value: 'Value') -> bool:
        return self % float() < other_value % float()
    
    def __gt__(self, other_value: 'Value') -> bool:
        return self % float() > other_value % float()
    
    def __le__(self, other_value: 'Value') -> bool:
        return not (self > other_value)
    
    def __ge__(self, other_value: 'Value') -> bool:
        return not (self < other_value)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "value": self._value
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "value" in serialization):

            self._value = serialization["value"]
        return self
        
    def copy(self): # read only Operand doesn't have to be duplicated, it never changes
        return self

    def __add__(self, value: Union['Value', float, int]) -> 'Value':
        match value:
            case Value(): return self.__class__(self % float() + value % float())
            case float() | int(): return self.__class__(self % float() + value)
    
    def __sub__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value(): return self.__class__(self % float() - value % float())
            case float() | int(): return self.__class__(self % float() - value)
        return self.__class__(self % float() - value)
    
    def __mul__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value(): return self.__class__((self % float()) * (value % float()))
            case float() | int(): return self.__class__(self % float() * value)
    
    def __truediv__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value():
                if value % float() != 0:
                    return self.__class__((self % float()) / (value % float()))
            case float() | int():
                if value != 0:
                    return self.__class__(self % float() / value)
        return self.__class__()

class Quantization(Value):
    def __init__(self, quantization: float = None):
        super().__init__( global_staff % Quantization(0) % float() if quantization is None else quantization )

class BeatsPerMeasure(Value):
    def __init__(self, beats_per_measure: float = None):
        super().__init__( global_staff % BeatsPerMeasure(0) % float() if beats_per_measure is None else beats_per_measure )

class BeatNoteValue(Value):
    def __init__(self, beat_note_value: float = None):
        super().__init__( global_staff % BeatNoteValue(0) % float() if beat_note_value is None else beat_note_value )

class NotesPerMeasure(Value):
    def __init__(self, notes_per_measure: float = None):
        super().__init__( global_staff % NotesPerMeasure(0) % float() if notes_per_measure is None else notes_per_measure )

class StepsPerMeasure(Value):
    def __init__(self, steps_per_measure: float = None):
        super().__init__( global_staff % StepsPerMeasure(0) % float() if steps_per_measure is None else steps_per_measure )

class StepsPerNote(Value):
    def __init__(self, steps_per_note: float = None):
        super().__init__( global_staff % StepsPerNote(0) % float() if steps_per_note is None else steps_per_note )

class Measure(Value):

    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return Beat(1).getTime_ms() * (global_staff % BeatsPerMeasure() % float()) * self._value
     
class Beat(Value):

    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return 60.0 * 1000 / (global_staff % Tempo() % int()) * self._value
    
class NoteValue(Value):

    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return Beat(1).getTime_ms() / (global_staff % BeatNoteValue() % float()) * self._value
     
class Step(Value):

    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return NoteValue(1).getTime_ms() / (global_staff % StepsPerNote() % float()) * self._value
    
class Length(Operand):
    
    def __init__(self):
        # Default values already, no need to wrap them with Default()
        self._measure       = Measure(0)
        self._beat          = Beat(0)
        self._note_value    = NoteValue(0)
        self._step          = Step(0)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Measure():     return self._measure
            case Beat():        return self._beat
            case NoteValue():   return self._note_value
            case Step():        return self._step
            case _:             return operand

    def __eq__(self, other_length):
        return round(self.getTime_ms(), 3) == round(other_length.getTime_ms(), 3)
    
    def __lt__(self, other_length):
        return round(self.getTime_ms(), 3) < round(other_length.getTime_ms(), 3)
    
    def __gt__(self, other_length):
        return round(self.getTime_ms(), 3) > round(other_length.getTime_ms(), 3)
    
    def __le__(self, other_length):
        return not (self > other_length)
    
    def __ge__(self, other_length):
        return not (self < other_length)
    
    # Type hints as string literals to handle forward references
    def getTime_ms(self):
        return self._measure.getTime_ms() + self._beat.getTime_ms() \
                + self._note_value.getTime_ms() + self._step.getTime_ms()
        
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "measure": self._measure.getSerialization(),
            "beat": self._beat.getSerialization(),
            "note_value": self._note_value.getSerialization(),
            "step": self._step.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measure" in serialization and "beat" in serialization and
            "note_value" in serialization and "step" in serialization):

            self._measure = Measure().loadSerialization(serialization["measure"])
            self._beat = Beat().loadSerialization(serialization["beat"])
            self._note_value = NoteValue().loadSerialization(serialization["note_value"])
            self._step = Step().loadSerialization(serialization["step"])

        return self
        
    def getLength(self) -> 'Length':
        return Length() << self._measure << self._beat << self._note_value << self._step

    def copy(self) -> 'Length':
        return self.__class__() << self._measure << self._beat << self._note_value << self._step

    def __lshift__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Measure(): self._measure = operand
            case Beat(): self._beat = operand
            case NoteValue(): self._note_value = operand
            case Step(): self._step = operand
            case Length():
                self._measure = operand % Measure()
                self._beat = operand % Beat()
                self._note_value = operand % NoteValue()
                self._step = operand % Step()
            case float() | int():
                self._measure = Measure(operand)
                self._beat = Beat(operand)
                self._note_value = NoteValue(operand)
                self._step = Step(operand)
        return self

    # adding two lengths 
    def __add__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Value():
                return self.__class__() << self % operand + operand
            case Length():
                return self.__class__() \
                    << self._measure + operand % Measure() \
                    << self._beat + operand % Beat() \
                    << self._note_value + operand % NoteValue() \
                    << self._step + operand % Step()
        return self.__class__()
    
    # subtracting two lengths 
    def __sub__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Value():
                return self.__class__() << self % operand - operand
            case Length():
                return self.__class__() \
                    << self._measure - operand % Measure() \
                    << self._beat - operand % Beat() \
                    << self._note_value - operand % NoteValue() \
                    << self._step - operand % Step()
        return self.__class__()
    
    def __mul__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Value():
                return self.__class__() << self % operand * operand
            case Length():
                return self.__class__() \
                    << self._measure * (operand % Measure()) \
                    << self._beat * (operand % Beat()) \
                    << self._note_value * (operand % NoteValue()) \
                    << self._step * (operand % Step())
        return self.__class__()
    
    def __truediv__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Value():
                return self.__class__() << self % operand / operand
            case Length():
                return self.__class__() \
                    << self._measure / (operand % Measure()) \
                    << self._beat / (operand % Beat()) \
                    << self._note_value / (operand % NoteValue()) \
                    << self._step / (operand % Step())
        return self.__class__()

class Position(Length):
    def __init__(self):
        super().__init__()

class Duration(Length):
    def __init__(self):
        super().__init__()
        self << global_staff % Duration

class TimeLength(Length):
    def __init__(self):
        super().__init__()
    
class Identity(Length):
    
    def __init__(self):
        super().__init__()
        self._measure       = Measure(1)
        self._beat          = Beat(1)
        self._note_value    = NoteValue(1)
        self._step          = Step(1)
    
# Read only class
class Device(Operand):

    def __init__(self, device_list: list[str] = None):
        self._device_list: list[str] = device_list

    def __mod__(self, operand: list) -> 'Device':
        if self._device_list is not None:
            match operand:
                case list(): return self._device_list
                case _: return self
        else:
            return global_staff % self % list()

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "device_list": self._device_list
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "device_list" in serialization):

            self._device_list = serialization["device_list"]
        return self

class Yield():
    def __init__(self, value: float = 0):
        super().__init__(value)


class Default(Operand):
    def __init__(self, operand: Operand):
        self._operand: Operand = operand

    def __mod__(self, operand: Operand) -> Operand:
        return self.getOperand()
    
    def getOperand(self):
        return self._operand

class Setup(Operand):
    def __init__(self):
        self._next_operand: Union['Setup', Operand] = None

    def __mod__(self, operand: Union['Setup', Operand]) -> Operand:
        if type(self) == type(operand):
            return self
        if self._next_operand is not None:
            match operand:
                case Setup():
                    if isinstance(self._next_operand, Setup):
                        return self._next_operand % operand
                    return Null()
                case Operand():
                    match self._next_operand:
                        case Setup():
                            return self._next_operand % Operand()
                        case Operand():
                            return self._next_operand
        return Null()
    
    def __pow__(self, operand: Union['Setup', Operand]) -> 'Setup':
        match operand:
            case Setup():
                self._setup_list.append(operand)
            case Operand():
                self._next_operand = operand
        return self
    
    def __lshift__(self, operand: Operand) -> 'Setup':
        match operand:
            case None: self._next_operand = None
        return self

class Inner(Setup):
    def __init__(self):
        super().__init__()

class Selection(Setup):
    
    def __init__(self):
        self._position: Position = Position()
        self._time_length: TimeLength = TimeLength() << Beat(1)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Position():
                return self._position
            case TimeLength():
                return self._time_length
        return self

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "position": self._position.getSerialization(),
            "time_length": self._time_length.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Selection':
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "position" in serialization and "time_length" in serialization and
            "operand" in serialization):

            self._position  = Position().loadSerialization(serialization["position"])
            self._time_length    = TimeLength().loadSerialization(serialization["length"])
            class_name = serialization["class"]
        return self

    def copy(self) -> 'Selection':
        return Selection() << self._position.copy() << self._time_length.copy()

    def __lshift__(self, operand: Operand) -> 'Operand':
        match operand:
            case Position(): self._position = operand
            case TimeLength(): self._time_length = operand
            case _: super().__lshift__(operand)
        return self
    

class Range(Operand):

    def __init__(self, operand: Operand, position: Position = None, length: Length = None):
        self._operand = operand
        self._position = position
        self._length = length

class Repeat(Operand):
    
    def __init__(self, unit: Unit, repeat: int = 1):
        self._unit = unit
        self._repeat = repeat

    def step(self) -> Unit | Null:
        if self._repeat > 0:
            self._repeat -= 1
            return self._unit
        return Null()

class Increment(Operand):
    """
    The Increment class initializes with a Unit and additional arguments,
    similar to the arguments in the range() function.

    Parameters:
    unit (Unit): The unit object.
    *argv (int): Additional arguments, similar to the range() function.

    The *argv works similarly to the arguments in range():
    - If one argument is provided, it's taken as the end value.
    - If two arguments are provided, they're taken as start and end.
    - If three arguments are provided, they're taken as start, end, and step.

    Increment usage:
    operand = Increment(unit, 8)
    operand = Increment(unit, 0, 10, 2)
    """

    def __init__(self, unit: Unit, *argv: int):
        """
        Initialize the Increment with a Unit and additional arguments.

        Parameters:
        unit (Unit): The unit object.
        *argv: Additional arguments, similar to the range() function.

        The *argv works similarly to the arguments in range():
        - If one argument is provided, it's taken as the end value.
        - If two arguments are provided, they're taken as start and end.
        - If three arguments are provided, they're taken as start, end, and step.

        Increment usage:
        operand = Increment(unit, 8)
        operand = Increment(unit, 0, 10, 2)
        """

        self._unit = unit
        self._start = 0
        self._stop = 0
        self._step = 1
        if len(argv) == 1:
            self._stop = argv[0]
        elif len(argv) == 2:
            self._start = argv[0]
            self._stop = argv[1]
        elif len(argv) == 3:
            self._start = argv[0]
            self._stop = argv[1]
            self._step = argv[2]
        else:
            raise ValueError("Increment requires 1, 2, or 3 arguments for the range.")

        self._iterator = self._start

    def step(self) -> Unit | Null:
        if self._iterator < self._stop:
            self._unit += self._step
            self._iterator += 1
            return self._unit
        return Null()


class IntervalQuality(Operand):

    def __init__(self, interval_quality: str = 0):
        self._interval_quality: str = interval_quality

        # Augmented (designated as A or +)
        # Major (ma)
        # Perfect (P)
        # Minor (mi)
        # Diminished (d or o)

class Inversion(Operand):
    
    def __init__(self, inversion: int = 0):
        self._inversion: int = inversion


class Swing(Operand):

    def __init__(self, swing: float = 0):
        self._swing: float = swing


class Gate(Operand):

    def __init__(self, gate: float = 0.50):
        self._gate: float = gate

# Set the Default Staff values here
                                            # Time Signature is BeatsPerMeasure / BeatNoteValue like 4/4
global_staff << Measure(8) << Tempo(120) << BeatsPerMeasure(4) << BeatNoteValue(1/4)
global_staff << Quantization(1/16) << (Duration() << NoteValue(1/4)) << Key("C") << Octave(4) << Velocity(100)
global_staff << ValueUnit(64) << Channel(1) << Device(["FLUID", "Midi", "Port", "Synth"])
                # 64 for CC Center
                


