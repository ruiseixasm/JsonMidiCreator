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
        return 12 * (octave + 1) + key
    
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

    def __add__(self, unit) -> 'KeyNote':
        key: ou.Key = self._key
        octave: ou.Octave = self._octave
        match unit:
            case ou.Key():
                key += unit
            case ou.Octave():
                octave += unit
            case _:
                return self.copy()

        return KeyNote(
            key     = key.getData(),
            octave  = octave.getData()
        )
     
    def __sub__(self, unit) -> 'KeyNote':
        key: ou.Key = self._key
        octave: ou.Octave = self._octave
        match unit:
            case ou.Key():
                key -= unit
            case ou.Octave():
                octave -= unit
            case _:
                return self.copy()

        return KeyNote(
            key     = key.getData(),
            octave  = octave.getData()
        )

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
