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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from operand_staff import global_staff
# Json Midi Creator Libraries
from operand import *
from operand_unit import *
from operand_value import *
from operand_length import *


class Null(Operand):
    pass

class KeyNote(Operand):
    def __init__(self):
        self._key: Key = Key()
        self._octave: Octave = Octave()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Key():     return self._key
            case Octave():  return self._octave
            case _:         return operand

    def getMidi__key_note(self) -> int:
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
  
# Read only class
class Device(Operand):
    def __init__(self, device_list: list[str] = None):
        from operand_staff import global_staff
        self._device_list: list[str] = []
        self._device_list = global_staff % self % list() if device_list is None else device_list

    def __mod__(self, operand: list) -> 'Device':
        match operand:
            case list(): return self._device_list
            case _: return self

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

class Yield(Operand):
    def __init__(self, value: float = 0):
        super().__init__(value)

class Default(Operand):
    def __init__(self, operand: Operand):
        self._operand: Operand = operand

    def __mod__(self, operand: Operand) -> Operand:
        return self.getOperand()
    
    def getOperand(self):
        return self._operand

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

