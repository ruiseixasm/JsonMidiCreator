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

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case list():                return self._enabled_indexes
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case list():                return self._enabled_indexes.copy()
            case _:                     return super().__mod__(operand)

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

    def next(self, number: Fraction) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        if self._next_operand is not None:
            self._next_operand.next(number)
        self._index += 1
        return self
        
    def __pow__(self, tamer: 'Tamer') -> Self:
        match tamer:
            case Tamer():       self._next_operand = tamer
            case _:             self._next_operand = None
        return self

class Parallel(Tamer):
    """`Tamer -> Parallel`

    Because `Tamer` operands work in series, a `Parallel` operand is able to place them \
        in parallel, meaning, they are processed in a `or` fashion.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    list([Tamer()]) : A list of tamers that set the `Tamer` operands in parallel.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._tamers: list[Tamer] = [Tamer()]
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
        number, validation = super().tame(number)
        if validation:
            if self.enabled() and self._tamers:
                parallel_validation: bool = False
                for single_tamer in self._tamers:
                    number, single_validation = single_tamer.tame(number)
                    if single_validation:
                        parallel_validation = True
                if not parallel_validation:
                    return number, False    # Breaks the chain
            if from_chaos:
                self.next(number)
        return number, validation

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case list():
                        if all(isinstance(item, Tamer) for item in operand._data):
                            return self._tamers
                        else:   # Not for me
                            return super().__mod__(operand)
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case list():
                if all(isinstance(item, Tamer) for item in operand):
                    return self.deep_copy(self._tamers)
                else:   # Not for me
                    return super().__mod__(operand)
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tamers"] = self.serialize( self._tamers )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tamers" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tamers = self.deserialize( serialization["parameters"]["tamers"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Tamer():
                super().__lshift__(operand)
                self._tamers = self.deep_copy(operand._tamers)
            case od.Pipe():
                match operand._data:
                    case list():
                        if all(isinstance(item, Tamer) for item in operand._data):
                            self._tamers = operand._data
                        else:   # Not for me
                            super().__lshift__(operand)
            case list():
                if all(isinstance(item, Tamer) for item in operand):
                    self._tamers = self.deep_copy(operand)
                else:   # Not for me
                    super().__lshift__(operand)
            case _:
                super().__lshift__(operand)
        return self

    def reset(self, *parameters) -> Self:
        for single_tamer in self._tamers:
            single_tamer.reset()
        return super().reset(*parameters)
    
    def next(self, number: Fraction) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        for single_tamer in self._tamers:
            single_tamer.next(number)
        return super().next(number)
        

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

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case int():                 return self._last_number
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case int():                 return self._last_number
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["last_number"] = self.serialize( self._last_number )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "last_number" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._last_number = self.deserialize( serialization["parameters"]["last_number"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Motion():
                super().__lshift__(operand)
                self._last_number = operand._last_number
            case od.Pipe():
                match operand._data:
                    case int():
                        self._last_number = operand._data
            case int():
                self._last_number = operand
            case _:
                super().__lshift__(operand)
        return self

    def reset(self, *parameters) -> Self:
        self._last_number = None
        return super().reset(*parameters)
    
    def next(self, number: Fraction) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        self._last_number = int(number)
        return super().next(number)
        
class Conjunct(Motion):
    """`Tamer -> Validator -> Motion -> Conjunct`

    This `Conjunct` checks if the successive numbers have a distance less or equal to 1 to the previous one.

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
                if self._last_number is not None \
                    and abs(int(number) - self._last_number) > 1:
                    return number, False    # Breaks the chain
            if from_chaos:
                self.next(number)
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
                if self._last_number is not None \
                    and abs(int(number) - self._last_number) != 1:
                    return number, False    # Breaks the chain
            if from_chaos:
                self.next(number)
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
                if self._last_number is not None \
                    and abs(int(number) - self._last_number) != 2:
                    return number, False    # Breaks the chain
            if from_chaos:
                self.next(number)
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
                if self._last_number is not None \
                    and abs(int(number) - self._last_number) < 1:
                    return number, False    # Breaks the chain
            if from_chaos:
                self.next(number)
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
                if self._last_number is not None \
                    and abs(int(number) - self._last_number) < 3:
                    return number, False    # Breaks the chain
            if from_chaos:
                self.next(number)
        return number, validation

class Ascending(Motion):
    """`Tamer -> Validator -> Motion -> Ascending`

    This `Ascending` checks if the successive number is greater than the previous one.

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
                if self._last_number is not None \
                    and not int(number) > self._last_number:
                    return number, False    # Breaks the chain
            if from_chaos:
                self.next(number)
        return number, validation

class Descending(Motion):
    """`Tamer -> Validator -> Motion -> Descending`

    This `Descending` checks if the successive number is less than the previous one.

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
                if self._last_number is not None \
                    and not int(number) < self._last_number:
                    return number, False    # Breaks the chain
            if from_chaos:
                self.next(number)
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
                self.next(number)
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
            case int():                 return int(self._module)
            case float():               return float(self._module)
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
            case int() | float():           self._module = Fraction(operand)
        return self
