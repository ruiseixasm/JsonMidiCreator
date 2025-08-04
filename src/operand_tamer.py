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

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._next_operand: Tamer = None
        self._enabled_indexes: list[int] = []
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def enabled(self) -> bool:
        """Returns True if current index is within enabled range."""
        indexes_len: int = len(self._enabled_indexes)
        match indexes_len:
            case 1:
                return self._index >= self._enabled_indexes[0]
            case 2:
                return self._index < self._enabled_indexes[1] \
                   and self._index >= self._enabled_indexes[0]
        return True

    def tame(self, number: Fraction, from_chaos: bool = False) -> tuple[Fraction, bool]:
        if self._next_operand is not None:
            number, validation = self._next_operand.tame(number)
            if not validation:
                return number, False    # Breaks the chain
        return number, True

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["enabled_indexes"] = self.serialize( self._enabled_indexes )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "enabled_indexes" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._enabled_indexes = self.deserialize( serialization["parameters"]["enabled_indexes"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Tamer():
                super().__lshift__(operand)
                self._enabled_indexes = operand._enabled_indexes.copy()
            case od.Pipe():
                match operand._data:
                    case list():
                        self._enabled_indexes = operand._data
            case list():
                self._enabled_indexes = operand.copy()
            case _:
                super().__lshift__(operand)
        return self

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

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    pass

class Motion(Validator):
    """`Tamer -> Validator -> Motion`

    A `Motion` validates the distance between integers given by the received number.
    It should be used together with a `Modulo` to avoid unmeet tries.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._last_number: int = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

class Melodic(Motion):
    """`Tamer -> Validator -> Motion -> Melodic`

    This `Melodic` checks if the successive numbers have a distance less or equal to 1 to the previous one.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    def tame(self, number: Fraction, from_chaos: bool = False) -> tuple[Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            if self.enabled():
                if self._last_number is None:
                    self._last_number = int(number)
                else:
                    if abs(int(number) - self._last_number) > 1:
                        return number, False    # Breaks the chain
                    else:
                        self._last_number = int(number)
            if from_chaos:
                self.index_increment()
        return number, validation

class Stepwise(Motion):
    """`Tamer -> Validator -> Motion -> Stepwise`

    This `Stepwise` checks if the successive numbers have a distance of 1 to the previous one.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    def tame(self, number: Fraction, from_chaos: bool = False) -> tuple[Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            if self.enabled():
                if self._last_number is None:
                    self._last_number = int(number)
                else:
                    if abs(int(number) - self._last_number) != 1:
                        return number, False    # Breaks the chain
                    else:
                        self._last_number = int(number)
            if from_chaos:
                self.index_increment()
        return number, validation

class Skipwise(Motion):
    """`Tamer -> Validator -> Motion -> Skipwise`

    This `Skipwise` checks if the successive numbers have a distance equal to 2 relative to the previous one.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    def tame(self, number: Fraction, from_chaos: bool = False) -> tuple[Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            if self.enabled():
                if self._last_number is None:
                    self._last_number = int(number)
                else:
                    if abs(int(number) - self._last_number) != 2:
                        return number, False    # Breaks the chain
                    else:
                        self._last_number = int(number)
            if from_chaos:
                self.index_increment()
        return number, validation

class Disjunct(Motion):
    """`Tamer -> Validator -> Motion -> Disjunct`

    This `Disjunct` checks if the successive numbers have a distance equal to 2 or greater relative to the previous one.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    def tame(self, number: Fraction, from_chaos: bool = False) -> tuple[Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            if self.enabled():
                if self._last_number is None:
                    self._last_number = int(number)
                else:
                    if abs(int(number) - self._last_number) < 2:
                        return number, False    # Breaks the chain
                    else:
                        self._last_number = int(number)
            if from_chaos:
                self.index_increment()
        return number, validation

class Leaping(Motion):
    """`Tamer -> Validator -> Motion -> Leaping`

    This `Leaping` checks if the successive numbers have a distance equal to 3 or greater relative to the previous one.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    def tame(self, number: Fraction, from_chaos: bool = False) -> tuple[Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            if self.enabled():
                if self._last_number is None:
                    self._last_number = int(number)
                else:
                    if abs(int(number) - self._last_number) < 3:
                        return number, False    # Breaks the chain
                    else:
                        self._last_number = int(number)
            if from_chaos:
                self.index_increment()
        return number, validation


class Manipulator(Tamer):
    """`Tamer -> Manipulator`

    A `Manipulator` is a read-write `Tamer` that instead of verifying a submitted number manipulates
    the given number to other Tamer operands.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    pass

class Modulo(Manipulator):
    """`Tamer -> Validator -> Modulo`

    This `Modulo` does the module by a given value.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._module: Fraction = Fraction(8)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, number: Fraction, from_chaos: bool = False) -> tuple[Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            if self.enabled():
                number %= self._module
            if from_chaos:
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
