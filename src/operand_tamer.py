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
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Tuple, Optional, Any, Generic
from typing import Self

from fractions import Fraction
import json
import enum
import math
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_frame as of


class Tamer(o.Operand):
    """`Tamer`

    Because `Chaos` returns numbers that fit no specific criteria, `Tamer` makes sure a criteria is
    met with validation or manipulation dependant of the tamer.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._next_operand: Tamer = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, number: Fraction) -> tuple[Fraction, bool]:
        if self._next_operand is not None:
            number, validation = self._next_operand.tame(number)
            if not validation:
                return number, False    # Breaks the chain
        return number, True

    # CHAINABLE OPERATIONS

    def index_increment(self) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        if self._next_operand is not None:
            self._next_operand.index_increment()
        self._index += 1
        return self
        
    def __pow__(self, tamer: 'Tamer') -> Self:
        match tamer:
            case Tamer():       self._next_operand = tamer
            case _:             self._next_operand = None
        return self


class Validator(Tamer):
    """`Tamer -> Validator`

    A `Validator` is a read-only `Tamer` that just verifies that the submitted number conforms.
    """
    pass

class Stepwise(Validator):
    """`Tamer -> Validator -> Stepwise`

    This `Stepwise` checks if the successive numbers have a distance less or equal to 0 to the previous one.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._last_number: int = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, number: Fraction) -> tuple[Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            if self._last_number is None:
                self._last_number = int(number)
            else:
                if abs(int(number) - self._last_number) > 1:
                    return number, False    # Breaks the chain
                else:
                    self._last_number = int(number)
            self.index_increment()
        return number, validation


class Manipulator(Tamer):
    """`Tamer -> Manipulator`

    A `Manipulator` is a read-write `Tamer` that instead of verifying a submitted number manipulates
    the given number to other Tamer operands.
    """
    pass

class Modulo(Manipulator):
    """`Tamer -> Validator -> Modulo`

    This `Modulo` does the module by a given value.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._module: Fraction = Fraction(8)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, number: Fraction) -> tuple[Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            number %= self._module
            self.index_increment()
        return number, validation

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case Fraction():            return self._module
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case Fraction():            return self._module
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Modulo():
                super().__lshift__(operand)
                self._module        = operand._module
            case od.Pipe():
                match operand._data:
                    case Fraction():                self._module = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Fraction():                self._module = operand
        return self
