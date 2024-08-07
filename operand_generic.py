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
import enum
# Json Midi Creator Libraries
import creator as c
from operand import Operand

import operand_unit as ou


class Generic(Operand):
    pass

class KeyNote(Generic):
    def __init__(self):
        self._key: ou.Key = ou.Key()
        self._octave: ou.Octave = ou.Octave()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ou.Key():     return self._key
            case ou.Octave():  return self._octave
            case _:         return operand

    def getMidi__key_note(self) -> int:
        key = self._key % int()
        octave = self._octave % int()
        return max(min(12 * (octave + 1) + key, 127), 0)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "key": self._key % int(),
            "octave": self._octave % int()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "key" in serialization and "octave" in serialization):

            self._key = ou.Key(serialization["key"])
            self._octave = ou.Octave(serialization["octave"])
        return self
        
    def copy(self) -> 'KeyNote':
        return KeyNote() << self._key << self._octave

    def __lshift__(self, operand: Operand) -> 'KeyNote':
        match operand:
            case ou.Key(): self._key = operand
            case ou.Octave(): self._octave = operand
        return self

    def __add__(self, operand) -> 'KeyNote':
        key_int: int = self._key % int()
        octave_int: int = self._octave % int()
        match operand:
            case ou.Key():
                key_int += operand % int() % 12
                octave_int += operand % int() // 12
            case ou.Octave():
                octave_int += operand % int()
            case KeyNote():
                key_int += operand % ou.Key() % int() % 12
                octave_int += (operand % ou.Octave() \
                               + ((KeyNote() << self % ou.Key() << ou.Octave(0)) + operand % ou.Key()) % ou.Octave()) % int()
            case _:
                return self.copy()
        return KeyNote() << ou.Key(key_int) << ou.Octave(octave_int)
     
    def __sub__(self, operand) -> 'KeyNote':
        key_int: int = self._key % int()
        octave_int: int = self._octave % int()
        match operand:
            case ou.Key():
                key_int -= operand % int() % 12
                octave_int -= operand % int() // 12
            case ou.Octave():
                octave_int -= operand % int()
            case KeyNote():
                key_int -= operand % ou.Key() % int() % 12
                octave_int -= (operand % ou.Octave() \
                               + ((KeyNote() << self % ou.Key() << ou.Octave(0)) + operand % ou.Key()) % ou.Octave()) % int()
            case _:
                return self.copy()
        return KeyNote() << ou.Key(key_int) << ou.Octave(octave_int)

class Controller(Generic):
    def __init__(self):
        self._midi_cc: ou.MidiCC        = ou.MidiCC()
        self._midi_value: ou.MidiValue  = ou.MidiValue( ou.MidiCC.getDefault(self._midi_cc % int()) )

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ou.MidiCC():       return self._midi_cc
            case ou.MidiValue():    return self._midi_value
            case _:                 return operand

    def getMidi__cc_value(self) -> int:
        return self._midi_value.getMidi__midi_value()
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "midi_cc": self._midi_cc % int(),
            "midi_value": self._midi_value % int()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "midi_cc" in serialization and "midi_value" in serialization):

            self._midi_cc = ou.MidiCC(serialization["midi_cc"])
            self._midi_value = ou.MidiValue(serialization["midi_value"])
        return self
        
    def copy(self) -> 'Controller':
        return Controller() << self._midi_cc << self._midi_value

    def __lshift__(self, operand: Operand) -> 'Controller':
        match operand:
            case ou.MidiCC(): self._midi_cc = operand
            case ou.MidiValue(): self._midi_value = operand
        return self

    def __add__(self, operand) -> 'Controller':
        midi_value_int: int = self._midi_value % int()
        match operand:
            case int():
                midi_value_int += operand
            case ou.MidiValue():
                midi_value_int += operand % int()
            case Controller():
                midi_value_int += operand % ou.MidiValue() % int()
            case _:
                return self.copy()
        return Controller() << ou.MidiCC(self._midi_cc) << ou.MidiValue(midi_value_int)
    
    def __sub__(self, operand) -> 'Controller':
        midi_value_int: int = self._midi_value % int()
        match operand:
            case int():
                midi_value_int -= operand
            case ou.MidiValue():
                midi_value_int -= operand % int()
            case Controller():
                midi_value_int -= operand % ou.MidiValue() % int()
            case _:
                return self.copy()
        return Controller() << ou.MidiCC(self._midi_cc) << ou.MidiValue(midi_value_int)

class Yield(Generic):
    def __init__(self, value: float = 0):
        super().__init__(value)

class Default(Generic):
    def __init__(self, operand: Operand):
        self._operand: Operand = operand

    def __mod__(self, operand: Operand) -> Operand:
        return self.getOperand()
    
    def getOperand(self):
        return self._operand


class IntervalQuality(Generic):
    def __init__(self, interval_quality: str = 0):
        self._interval_quality: str = interval_quality

        # Augmented (designated as A or +)
        # Major (ma)
        # Perfect (P)
        # Minor (mi)
        # Diminished (d or o)
