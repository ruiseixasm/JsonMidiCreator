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
    None
    """
    def from_tail(self) -> int:
        if self._next_operand is None:
            return 1
        return self._next_operand.from_tail() + 1

    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        if self._next_operand is not None:
            rational, validation = self._next_operand.tame(rational)
            if not validation:
                return rational, False    # Breaks the chain
        if iterate:
            self.next(rational)
        return rational, True

    # CHAINABLE OPERATIONS

    def next(self, rational: Fraction) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        if isinstance(self._next_operand, Tamer):
            self._next_operand.next(rational)
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
    list([]) : A list of floats or integer that set the `Tamer` enabled range of iterations (indexes), for floats, \
    `[2.0]` to enable the Tamer at the 2nd iteration onwards or `[0.0, 2.0]` to enable the first 2 iterations, while for integers, \
    the list of integers represent the enabled indexes, like, `[0, 3, 7]` means, enabled for indexes 0, 3 and 7. \
    The default of `[]` means always enabled for any index.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    list([Tamer()]) : A list of tamers that set the `Tamer` operands in parallel.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._tamers: list[Tamer] = [Tamer()]
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational)
        if validation:
            if not self.slack(rational) and self._tamers:
                parallel_validation: bool = False
                for single_tamer in self._tamers:
                    rational, single_validation = single_tamer.tame(rational)
                    if single_validation:
                        parallel_validation = True
                if not parallel_validation:
                    return rational, False    # Breaks the chain
            if iterate:
                self.next(rational)
        return rational, validation

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
    
    def next(self, rational: Fraction) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        for single_tamer in self._tamers:
            single_tamer.next(rational)
        return super().next(rational)
        

class Validator(Tamer):
    """`Tamer -> Validator`

    A `Validator` is a read-only `Tamer` that just verifies that the submitted rational conforms.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._strictness: Fraction = Fraction(1)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def slack(self, rational: Fraction) -> bool:
        """Returns True to skip the respective tamer, meaning, gives some slack."""
        return rational * self.from_tail() % Fraction(1) > self._strictness

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ra.Strictness():       return operand._data << od.Pipe(self._strictness)
                    case Fraction():            return self._strictness
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case ra.Strictness():       return operand.copy(od.Pipe(self._strictness))
            case Fraction():            return self._strictness
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["strictness"] = self.serialize( self._strictness )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "strictness" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._strictness = self.deserialize( serialization["parameters"]["strictness"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Tamer():
                super().__lshift__(operand)
                self._strictness = operand._strictness
            case od.Pipe():
                match operand._data:
                    case ra.Strictness():
                        self._strictness = operand._data._rational
                    case Fraction():
                        self._strictness = operand._data
            case ra.Strictness():
                self._strictness = operand._rational
            case Fraction():
                self._strictness = operand
            case _:
                super().__lshift__(operand)
        return self


class Motion(Validator):
    """`Tamer -> Validator -> Motion`

    A `Motion` validates the distance between integers given by the received rational.
    It should be used together with a `Modulo` to avoid unmeet tries.

    Parameters
    ----------
    list([]) : A list of integers that set the `Tamer` enabled range of iterations (indexes), like, \
    `[2]` to enable the Tamer at the 2nd iteration or `[0, 2]` to enable the first 2 iterations. The default \
    of `[]` means always enabled.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._last_integer: int = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case int():                 return self._last_integer
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case int():                 return self._last_integer
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["last_number"] = self.serialize( self._last_integer )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "last_number" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._last_integer = self.deserialize( serialization["parameters"]["last_number"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Motion():
                super().__lshift__(operand)
                self._last_integer = operand._last_integer
            case od.Pipe():
                match operand._data:
                    case int():
                        self._last_integer = operand._data
            case int():
                self._last_integer = operand
            case _:
                super().__lshift__(operand)
        return self

    def reset(self, *parameters) -> Self:
        self._last_integer = None
        return super().reset(*parameters)
    
    def next(self, rational: Fraction) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        self._last_integer = int(rational)
        return super().next(rational)
        
class Conjunct(Motion):
    """`Tamer -> Validator -> Motion -> Conjunct`

    This `Conjunct` checks if the successive numbers have a distance less or equal to 1 to the previous one.

    Parameters
    ----------
    list([]) : A list of floats or integer that set the `Tamer` enabled range of iterations (indexes), for floats, \
    `[2.0]` to enable the Tamer at the 2nd iteration onwards or `[0.0, 2.0]` to enable the first 2 iterations, while for integers, \
    the list of integers represent the enabled indexes, like, `[0, 3, 7]` means, enabled for indexes 0, 3 and 7. \
    The default of `[]` means always enabled for any index.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational)
        if validation:
            if not self.slack(rational):
                if self._last_integer is not None \
                    and abs(int(rational) - self._last_integer) > 1:
                    return rational, False    # Breaks the chain
            if iterate:
                self.next(rational)
        return rational, validation

class Stepwise(Motion):
    """`Tamer -> Validator -> Motion -> Stepwise`

    This `Stepwise` checks if the successive numbers have a distance of 1 to the previous one.

    Parameters
    ----------
    list([]) : A list of floats or integer that set the `Tamer` enabled range of iterations (indexes), for floats, \
    `[2.0]` to enable the Tamer at the 2nd iteration onwards or `[0.0, 2.0]` to enable the first 2 iterations, while for integers, \
    the list of integers represent the enabled indexes, like, `[0, 3, 7]` means, enabled for indexes 0, 3 and 7. \
    The default of `[]` means always enabled for any index.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational)
        if validation:
            if not self.slack(rational):
                if self._last_integer is not None \
                    and abs(int(rational) - self._last_integer) != 1:
                    return rational, False    # Breaks the chain
            if iterate:
                self.next(rational)
        return rational, validation

class Skipwise(Motion):
    """`Tamer -> Validator -> Motion -> Skipwise`

    This `Skipwise` checks if the successive numbers have a distance equal to 2 relative to the previous one.

    Parameters
    ----------
    list([]) : A list of floats or integer that set the `Tamer` enabled range of iterations (indexes), for floats, \
    `[2.0]` to enable the Tamer at the 2nd iteration onwards or `[0.0, 2.0]` to enable the first 2 iterations, while for integers, \
    the list of integers represent the enabled indexes, like, `[0, 3, 7]` means, enabled for indexes 0, 3 and 7. \
    The default of `[]` means always enabled for any index.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational)
        if validation:
            if not self.slack(rational):
                if self._last_integer is not None \
                    and abs(int(rational) - self._last_integer) != 2:
                    return rational, False    # Breaks the chain
            if iterate:
                self.next(rational)
        return rational, validation

class Disjunct(Motion):
    """`Tamer -> Validator -> Motion -> Disjunct`

    This `Disjunct` checks if the successive numbers have a distance equal to 2 or greater relative to the previous one.

    Parameters
    ----------
    list([]) : A list of floats or integer that set the `Tamer` enabled range of iterations (indexes), for floats, \
    `[2.0]` to enable the Tamer at the 2nd iteration onwards or `[0.0, 2.0]` to enable the first 2 iterations, while for integers, \
    the list of integers represent the enabled indexes, like, `[0, 3, 7]` means, enabled for indexes 0, 3 and 7. \
    The default of `[]` means always enabled for any index.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational)
        if validation:
            if not self.slack(rational):
                if self._last_integer is not None \
                    and abs(int(rational) - self._last_integer) < 1:
                    return rational, False    # Breaks the chain
            if iterate:
                self.next(rational)
        return rational, validation

class Leaping(Motion):
    """`Tamer -> Validator -> Motion -> Leaping`

    This `Leaping` checks if the successive numbers have a distance equal to 3 or greater relative to the previous one.

    Parameters
    ----------
    list([]) : A list of floats or integer that set the `Tamer` enabled range of iterations (indexes), for floats, \
    `[2.0]` to enable the Tamer at the 2nd iteration onwards or `[0.0, 2.0]` to enable the first 2 iterations, while for integers, \
    the list of integers represent the enabled indexes, like, `[0, 3, 7]` means, enabled for indexes 0, 3 and 7. \
    The default of `[]` means always enabled for any index.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational)
        if validation:
            if not self.slack(rational):
                if self._last_integer is not None \
                    and abs(int(rational) - self._last_integer) < 3:
                    return rational, False    # Breaks the chain
            if iterate:
                self.next(rational)
        return rational, validation

class Ascending(Motion):
    """`Tamer -> Validator -> Motion -> Ascending`

    This `Ascending` checks if the successive rational is greater than the previous one.

    Parameters
    ----------
    list([]) : A list of floats or integer that set the `Tamer` enabled range of iterations (indexes), for floats, \
    `[2.0]` to enable the Tamer at the 2nd iteration onwards or `[0.0, 2.0]` to enable the first 2 iterations, while for integers, \
    the list of integers represent the enabled indexes, like, `[0, 3, 7]` means, enabled for indexes 0, 3 and 7. \
    The default of `[]` means always enabled for any index.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational)
        if validation:
            if not self.slack(rational):
                if self._last_integer is not None \
                    and not int(rational) > self._last_integer:
                    return rational, False    # Breaks the chain
            if iterate:
                self.next(rational)
        return rational, validation

class Descending(Motion):
    """`Tamer -> Validator -> Motion -> Descending`

    This `Descending` checks if the successive rational is less than the previous one.

    Parameters
    ----------
    list([]) : A list of floats or integer that set the `Tamer` enabled range of iterations (indexes), for floats, \
    `[2.0]` to enable the Tamer at the 2nd iteration onwards or `[0.0, 2.0]` to enable the first 2 iterations, while for integers, \
    the list of integers represent the enabled indexes, like, `[0, 3, 7]` means, enabled for indexes 0, 3 and 7. \
    The default of `[]` means always enabled for any index.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational)
        if validation:
            if not self.slack(rational):
                if self._last_integer is not None \
                    and not int(rational) < self._last_integer:
                    return rational, False    # Breaks the chain
            if iterate:
                self.next(rational)
        return rational, validation


class Manipulator(Tamer):
    """`Tamer -> Manipulator`

    A `Manipulator` is a read-write `Tamer` that instead of verifying a submitted rational manipulates
    the given rational to other Tamer operands.

    Parameters
    ----------
    None
    """
    # A `Manipulator` shall always be triggered regardless of being previously validated or not
    pass

class Limit(Manipulator):
    """`Tamer -> Manipulator -> Limit`

    A `Limit` manipulates a given value accordingly to an imposed limit.

    Parameters
    ----------
    Fraction(8) : Sets the limit value.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._limit: Fraction = Fraction(8)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case Fraction():            return self._limit
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case Fraction():            return self._limit
            case int():                 return int(self._limit)
            case float():               return float(self._limit)
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["limit"] = self.serialize( self._limit )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "limit" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._limit = self.deserialize( serialization["parameters"]["limit"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
                self._limit = operand._limit
            case od.Pipe():
                match operand._data:
                    case Fraction():                self._limit = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case int() | float() | Fraction():
                self._limit = ra.Result(operand)._rational
        return self

class Modulo(Limit):
    """`Tamer -> Manipulator -> Limit -> Modulo`

    This `Modulo` does the module by a given value.

    Parameters
    ----------
    Fraction(8) : Sets the limit value.
    """
    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational, iterate)
        rational %= self._limit
        return rational, validation
    
class Maximum(Limit):
    """`Tamer -> Manipulator -> Limit -> Maximum`

    This `Maximum` limits a given Result to a maximum, equal or below it.

    Parameters
    ----------
    Fraction(127) : Sets the limit value.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._limit: Fraction = Fraction(127)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational, iterate)
        rational = min(self._limit, rational)
        return rational, validation

class Minimum(Limit):
    """`Tamer -> Manipulator -> Limit -> Minimum`

    This `Minimum` limits a given Result to a minimum, equal or above it.

    Parameters
    ----------
    Fraction(0) : Sets the limit value.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._limit: Fraction = Fraction(0)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, rational: Fraction, iterate: bool = False) -> tuple[Fraction, bool]:
        rational, validation = super().tame(rational, iterate)
        rational = max(self._limit, rational)
        return rational, validation
    
