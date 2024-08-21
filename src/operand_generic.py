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
import operand_frame as of
import operand_label as ol


class Generic(Operand):
    pass

class KeyScale(Generic):
    def __init__(self, key: int | str = None):
        self._key: ou.Key = ou.Key(key)
        self._scale: ou.Scale = ou.Scale()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case ou.Key():          return self._key
            case ou.Scale():        return self._scale
            case ol.Null() | None:  return ol.Null()
            case _:                 return self

    def getSharps(self, key: ou.Key = None) -> int:
        ...

    def getFlats(self, key: ou.Key = None) -> int:
        ...

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "key": self._key % int(),
            "scale_type": self._scale % int()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeyScale':
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "key" in serialization and "scale_type" in serialization):

            self._key = ou.Key(serialization["key"])
            self._scale = ou.Scale(serialization["scale_type"])
        return self
        
    def copy(self) -> 'KeyScale':
        return KeyScale() << self._key.copy() << self._scale.copy()

    def __lshift__(self, operand: Operand) -> 'KeyScale':
        match operand:
            case of.Frame():        self << (operand & self)
            case KeyScale():
                self._key = operand % ou.Key()
                self._scale = operand % ou.Scale()
            case ou.Key():          self._key = operand
            case ou.Scale():        self._scale = operand
        return self

    def __add__(self, operand) -> 'KeyScale':
        key_int: int = self._key % int()
        scale_type_int: int = self._scale % int()
        match operand:
            case of.Frame():
                return self + (operand & self)
            case int():
                key_int += operand % 12
                scale_type_int += operand // 12
            case ou.Key():
                key_int += operand % int() % 12
                scale_type_int += operand % int() // 12
            case ou.Scale():
                scale_type_int += operand % int()
            case KeyScale():
                key_int += operand % ou.Key() % int() % 12
                scale_type_int += (operand % ou.Scale() \
                               + ((KeyScale() << self % ou.Key() << ou.Scale(0)) + operand % ou.Key()) % ou.Scale()) % int()
            case _: return self.copy()
        return KeyScale() << ou.Key(key_int) << ou.Scale(scale_type_int)
     
    def __sub__(self, operand) -> 'KeyScale':
        key_int: int = self._key % int()
        scale_type_int: int = self._scale % int()
        match operand:
            case of.Frame():
                return self - (operand & self)
            case int():
                key_int -= operand % 12
                scale_type_int -= operand // 12
            case ou.Key():
                key_int -= operand % int() % 12
                scale_type_int -= operand % int() // 12
            case ou.Scale():
                scale_type_int -= operand % int()
            case KeyScale():
                key_int -= operand % ou.Key() % int() % 12
                scale_type_int -= (operand % ou.Scale() \
                               + ((KeyScale() << self % ou.Key() << ou.Scale(0)) + operand % ou.Key()) % ou.Scale()) % int()
            case _:
                return self.copy()
        return KeyScale() << ou.Key(key_int) << ou.Scale(scale_type_int)

class TimeSignature(Generic):
    ...

class KeyNote(Generic):
    def __init__(self, key: int | str = None):
        self._key: ou.Key = ou.Key(key)
        self._octave: ou.Octave = ou.Octave()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case ou.Key():          return self._key
            case ou.Octave():       return self._octave
            case ol.Null() | None:  return ol.Null()
            case _:                 return self

    def __eq__(self, other: 'KeyNote') -> bool:
        if self % ou.Octave() == other % ou.Octave() and self % ou.Key() == other % ou.Key():
            return True
        return False
    
    def __lt__(self, other: 'KeyNote') -> bool:
        if self % ou.Octave() < other % ou.Octave():    return True
        if self % ou.Octave() > other % ou.Octave():    return False
        if self % ou.Key() < other % ou.Key():          return True
        return False
    
    def __gt__(self, other: 'KeyNote') -> bool:
        if self % ou.Octave() > other % ou.Octave():    return True
        if self % ou.Octave() < other % ou.Octave():    return False
        if self % ou.Key() > other % ou.Key():          return True
        return False
    
    def __le__(self, other: 'KeyNote') -> bool:
        return not (self > other)
    
    def __ge__(self, other: 'KeyNote') -> bool:
        return not (self < other)
    
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
        return KeyNote() << self._key.copy() << self._octave.copy()

    def __lshift__(self, operand: Operand) -> 'KeyNote':
        match operand:
            case of.Frame():        self << (operand & self)
            case KeyNote():
                self._key = operand % ou.Key()
                self._octave = operand % ou.Octave()
            case ou.Key():          self._key = operand
            case ou.Octave():       self._octave = operand
        return self

    def __add__(self, operand) -> 'KeyNote':
        key_int: int = self._key % int()
        octave_int: int = self._octave % int()
        match operand:
            case of.Frame():
                return self + (operand & self)
            case int():
                key_int += operand
                octave_int += key_int // 12
            case ou.Key():
                key_int += operand % int()
                octave_int += key_int // 12
            case ou.Octave():
                octave_int += operand % int()
            case KeyNote():
                key_int += operand % ou.Key() % int()
                octave_int += operand % ou.Octave() % int() + key_int // 12
            case _: return self.copy()
        return KeyNote() << ou.Key(key_int) << ou.Octave(octave_int)
     
    def __sub__(self, operand) -> 'KeyNote':
        key_int: int = self._key % int()
        octave_int: int = self._octave % int()
        match operand:
            case of.Frame():
                return self - (operand & self)
            case int():
                key_int -= operand
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case ou.Key():
                key_int -= operand % int()
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case ou.Octave():
                octave_int -= operand % int()
            case KeyNote():
                key_int -= operand % ou.Key() % int()
                octave_int -= operand % ou.Octave() % int() - max(-1 * key_int + 11, 0) // 12
            case _: return self.copy()
        return KeyNote() << ou.Key(key_int) << ou.Octave(octave_int)

class Controller(Generic):
    def __init__(self, number: int | str = None):
        self._control_number: ou.ControlNumber  = ou.ControlNumber( number )
        self._control_value: ou.ControlValue    = ou.ControlValue( ou.ControlNumber.getDefault(self._control_number % int()) )

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():            return self % (operand % Operand())
            case ou.ControlNumber():    return self._control_number
            case ou.ControlValue():     return self._control_value
            case ol.Null() | None:      return ol.Null()
            case _:                     return self

    def getMidi__cc_value(self) -> int:
        return self._control_value.getMidi__control_value()
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "control_number": self._control_number % int(),
            "control_value": self._control_value % int()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "control_number" in serialization and "control_value" in serialization):

            self._control_number = ou.ControlNumber(serialization["control_number"])
            self._control_value = ou.ControlValue(serialization["control_value"])
        return self
        
    def copy(self) -> 'Controller':
        return Controller() << self._control_number.copy() << self._control_value.copy()

    def __lshift__(self, operand: Operand) -> 'Controller':
        match operand:
            case of.Frame():            self << (operand & self)
            case Controller():
                self._control_number = operand % ou.ControlNumber()
                self._control_value = operand % ou.ControlValue()
            case ou.ControlNumber():    self._control_number = operand
            case ou.ControlValue():     self._control_value = operand
        return self

    def __add__(self, operand) -> 'Controller':
        control_value_int: int = self._control_value % int()
        match operand:
            case of.Frame():
                return self + (operand & self)
            case int():
                control_value_int += operand
            case ou.ControlValue():
                control_value_int += operand % int()
            case Controller():
                control_value_int += operand % ou.ControlValue() % int()
            case _:
                return self.copy()
        return Controller() << ou.ControlNumber(self._control_number) << ou.ControlValue(control_value_int)
    
    def __sub__(self, operand) -> 'Controller':
        control_value_int: int = self._control_value % int()
        match operand:
            case of.Frame():
                return self - (operand & self)
            case int():
                control_value_int -= operand
            case ou.ControlValue():
                control_value_int -= operand % int()
            case Controller():
                control_value_int -= operand % ou.ControlValue() % int()
            case _:
                return self.copy()
        return Controller() << ou.ControlNumber(self._control_number) << ou.ControlValue(control_value_int)

class Yield(Generic):
    def __init__(self, value: float = 0):
        super().__init__(value)

class Default(Generic):
    def __init__(self, operand: Operand):
        self._operand: Operand = operand

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():                return self % (operand % Operand())
            case self._operand.__class__(): return self._operand
            case ol.Null() | None:          return ol.Null()
            case _:                         return self

class IntervalQuality(Generic):
    def __init__(self, interval_quality: str = 0):
        self._interval_quality: str = interval_quality

        # Augmented (designated as A or +)
        # Major (ma)
        # Perfect (P)
        # Minor (mi)
        # Diminished (d or o)
