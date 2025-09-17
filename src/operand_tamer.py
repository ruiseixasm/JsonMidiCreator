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

    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        if self._next_operand is not None:
            numeral, validated = self._next_operand.tame(numeral)
            if not validated:
                return numeral, False    # Breaks the chain
            if validated and iterate:
                self.next(numeral)
        elif iterate:
            self.next(numeral)
        return numeral, True

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case _:                     return super().__mod__(operand)
            case of.Frame():
                return self % operand
            case Tamer():
                return operand.copy(self)
            case _:
                return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def next(self, numeral: o.TypeNumeral) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        if isinstance(self._next_operand, Tamer):
            self._next_operand.next(numeral)
        self._index += 1
        return self
        
    def __pow__(self, operand: 'o.Operand') -> Self:
        match operand:
            case Tamer():       self._next_operand = operand
            case _:             super().__pow__(operand)
        return self

    # Operand ^= Tamer is taken care above
    def __rxor__(self, operand: o.T) -> o.T:
        return operand

    def reset(self, *parameters) -> Self:
        self._initiated     = False
        self._set           = False
        self._index         = 0
        # RESET THE SELF OPERANDS RECURSIVELY
        if isinstance(self._next_operand, o.Operand):
            self._next_operand.reset()
        return self << parameters


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

    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral) and self._tamers:
                parallel_validation: bool = False
                for single_tamer in self._tamers:
                    numeral, single_validation = single_tamer.tame(numeral)
                    if single_validation:
                        parallel_validation = True
                if not parallel_validation:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():
                        if all(isinstance(item, Tamer) for item in operand._data):
                            return self._tamers
                        else:   # Not for me
                            return super().__mod__(operand)
                    case _:                     return super().__mod__(operand)
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
    
    def next(self, numeral: o.TypeNumeral) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        for single_tamer in self._tamers:
            single_tamer.next(numeral)
        return super().next(numeral)
        

class Validator(Tamer):
    """`Tamer -> Validator`

    A `Validator` is a read-only `Tamer` that just verifies that the submitted numeral conforms.

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

    def slack(self, numeral: o.TypeNumeral) -> bool:
        """Returns True to skip the respective tamer, meaning, gives some slack."""
        return numeral * self.from_tail() % Fraction(1) > self._strictness

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Strictness():       return operand._data << od.Pipe(self._strictness)
                    case Fraction():            return self._strictness
                    case _:                     return super().__mod__(operand)
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
            case Validator():
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

class Check(Validator):
    """`Tamer -> Validator -> Check`

    A `Check` manipulates a given value accordingly to an imposed limit.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    Fraction(8) : Sets the limit value.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._checker: Callable = lambda: True
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral) and not self._checker(numeral):
                return numeral, False  # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                if isinstance(operand._data, Callable):
                    return self._checker
                else:
                    return super().__mod__(operand)
            case _:
                if isinstance(operand, Callable):
                    return self._checker
                else:
                    return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
                self._checker = operand._checker
            case od.Pipe():
                if isinstance(operand._data, Callable):
                    self._checker = operand._data
                else:
                    super().__lshift__(operand)
            case _:
                if isinstance(operand, Callable):
                    self._checker = operand
                else:
                    super().__lshift__(operand)
        return self


class Boundary(Validator):
    """`Tamer -> Validator -> Boundary`

    A `Boundary` verifies a given value accordingly to an imposed limit.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    Fraction(8) : Sets the limit value.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._boundary: Fraction = Fraction(8)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case Fraction():            return self._boundary
                    case _:                     return super().__mod__(operand)
            case Fraction():            return self._boundary
            case int():                 return int(self._boundary)
            case float():               return float(self._boundary)
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["boundary"] = self.serialize( self._boundary )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "boundary" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._boundary = self.deserialize( serialization["parameters"]["boundary"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
                self._boundary = operand._boundary
            case od.Pipe():
                match operand._data:
                    case Fraction():                self._boundary = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case int() | float() | Fraction():
                self._boundary = ra.Result(operand)._rational
        return self


class Maximum(Boundary):
    """`Tamer -> Validator -> Boundary -> Maximum`

    This `Maximum` limits a given Result to a maximum, equal or below it.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    Fraction(127) : Sets the boundary value.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._boundary: Fraction = Fraction(127)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if numeral > self._boundary:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

class Minimum(Boundary):
    """`Tamer -> Validator -> Boundary -> Minimum`

    This `Minimum` limits a given Result to a minimum, equal or above it.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    Fraction(0) : Sets the boundary value.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._boundary: Fraction = Fraction(0)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if numeral < self._boundary:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated
    
class Prior(Validator):
    """`Tamer -> Validator -> Prior`

    A `Prior` tamer keeps the previous Rational validated.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._prior_numeral: o.TypeNumeral = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["prior"] = self.serialize( self._prior_numeral )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "prior" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._prior_numeral = self.deserialize( serialization["parameters"]["prior"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
                self._prior_numeral = operand._prior_numeral
            case _:
                super().__lshift__(operand)
        return self

    def reset(self, *parameters) -> Self:
        self._prior_numeral = None
        return super().reset(*parameters)
    
    def next(self, numeral: o.TypeNumeral) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        self._prior_numeral = numeral
        return super().next(numeral)

class Different(Prior):
    """`Tamer -> Validator -> Prior -> Different`

    A `Different` tamer validates if the new `Rational` is different form the prior one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral) and self._prior_numeral is not None and numeral == self._prior_numeral:
                return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated
    
class Same(Prior):
    """`Tamer -> Validator -> Prior -> Same`

    A `Same` tamer validates if the new `Rational` is equal to the prior one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral) and self._prior_numeral is not None and numeral != self._prior_numeral:
                return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated
    
class Increasing(Prior):
    """`Tamer -> Validator -> Prior -> Increasing`

    A `Increasing` tamer validates if the new `Rational` is greater than the prior one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral) and self._prior_numeral is not None and numeral <= self._prior_numeral:
                return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated
    
class Decreasing(Prior):
    """`Tamer -> Validator -> Prior -> Decreasing`

    A `Decreasing` tamer validates if the new `Rational` is less than the prior one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral) and self._prior_numeral is not None and numeral >= self._prior_numeral:
                return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated


class Motion(Validator):
    """`Tamer -> Validator -> Motion`

    A `Motion` validates the distance between integers given by the received numeral.
    It should be used together with a `Modulo` to avoid unmeet tries.

    Parameters
    ----------
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
            case od.Pipe():
                match operand._data:
                    case int():                 return self._last_integer
                    case _:                     return super().__mod__(operand)
            case int():                 return self._last_integer
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["last_integer"] = self.serialize( self._last_integer )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "last_integer" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._last_integer = self.deserialize( serialization["parameters"]["last_integer"] )
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
    
    def next(self, numeral: o.TypeNumeral) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        self._last_integer = int(numeral)
        return super().next(numeral)
        

class Pattern(Motion):
    """`Tamer -> Validator -> Motion -> Pattern`

    A `Pattern` validates the given Motion accordingly to a pattern where 1 means up, -1 means down and 0 repeat.

    Parameters
    ----------
    list([]), Clip() : A `list` of integers where the positivity or negativity of the integer is used as the motion pattern.
    int(0) : An integer sets an absolute limit where the cumulative numeral can't go above or below. The default is 0, \
        meaning it has no limit.
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._pattern: list[int] = []
        self._limit: int = 0
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if self._last_integer is not None:
                if not self.slack(numeral):
                    expected_motion: int = self._pattern[self._index % len(self._pattern)]
                    if expected_motion > 0:
                        if not int(numeral) > 0:
                            return numeral, False   # Breaks the chain
                    elif expected_motion < 0:
                        if not int(numeral) < 0:
                            return numeral, False   # Breaks the chain
                    elif not int(numeral) == 0: # Value 0 means repeat previous
                        return numeral, False       # Breaks the chain
            # Has to be 0, first pattern number must not change
            elif not int(numeral) == 0: # Value 0 means repeat previous
                return numeral, False   # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated
    
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():                return self._pattern
                    case int():                 return self._limit
                    case _:                     return super().__mod__(operand)
            case list():                return self._pattern.copy()
            case int():                 return self._limit
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pattern"]  = self.serialize( self._pattern )
        serialization["parameters"]["limit"]    = self.serialize( self._pattern )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pattern" in serialization["parameters"] and "limit" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pattern   = self.deserialize( serialization["parameters"]["pattern"] )
            self._limit     = self.deserialize( serialization["parameters"]["limit"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Pattern():
                super().__lshift__(operand)
                self._pattern   = operand._pattern.copy()
                self._limit     = operand._limit
            case od.Pipe():
                match operand._data:
                    case list():
                        self._pattern = operand._data
                    case int():
                        self._limit = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                self._pattern = [
                    number if isinstance(number, int) else 0 for number in operand
                ]
            case int():
                self._limit = operand
            case _:
                super().__lshift__(operand)
        return self

    def next(self, numeral: o.TypeNumeral) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        if self._last_integer is None:
            cumulative_number: int = 0
        else:
            cumulative_number: int = self._last_integer + int(numeral)
        super().next(numeral)   # Updates all indexes
        self._last_integer = cumulative_number
        return self
        

class Conjunct(Motion):
    """`Tamer -> Validator -> Motion -> Conjunct`

    This `Conjunct` checks if the successive numbers have a distance less or equal to 1 to the previous one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if self._last_integer is not None \
                    and abs(int(numeral) - self._last_integer) > 1:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

class Stepwise(Motion):
    """`Tamer -> Validator -> Motion -> Stepwise`

    This `Stepwise` checks if the successive numbers have a distance of 1 to the previous one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if self._last_integer is not None \
                    and abs(int(numeral) - self._last_integer) != 1:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

class Skipwise(Motion):
    """`Tamer -> Validator -> Motion -> Skipwise`

    This `Skipwise` checks if the successive numbers have a distance equal to 2 relative to the previous one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if self._last_integer is not None \
                    and abs(int(numeral) - self._last_integer) != 2:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

class Disjunct(Motion):
    """`Tamer -> Validator -> Motion -> Disjunct`

    This `Disjunct` checks if the successive numbers have a distance equal to 2 or greater relative to the previous one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if self._last_integer is not None \
                    and abs(int(numeral) - self._last_integer) < 1:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

class Leaping(Motion):
    """`Tamer -> Validator -> Motion -> Leaping`

    This `Leaping` checks if the successive numbers have a distance equal to 3 or greater relative to the previous one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if self._last_integer is not None \
                    and abs(int(numeral) - self._last_integer) < 3:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

class Ascending(Motion):
    """`Tamer -> Validator -> Motion -> Ascending`

    This `Ascending` checks if the successive numeral is greater than the previous one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if self._last_integer is not None \
                    and not int(numeral) > self._last_integer:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated

class Descending(Motion):
    """`Tamer -> Validator -> Motion -> Descending`

    This `Descending` checks if the successive numeral is less than the previous one.

    Parameters
    ----------
    Strictness(1), Fraction() : A `Fraction` between 0 and 1 where 1 means always applicable and less that 1 \
    represents the probability of being applicable based on the received `Rational`. The inverse of a slack.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        if validated:
            if not self.slack(numeral):
                if self._last_integer is not None \
                    and not int(numeral) < self._last_integer:
                    return numeral, False    # Breaks the chain
            if iterate:
                self.next(numeral)
        return numeral, validated


class Manipulator(Tamer):
    """`Tamer -> Manipulator`

    A `Manipulator` is a read-write `Tamer` that instead of verifying a submitted numeral manipulates
    the given numeral to other Tamer operands.

    Parameters
    ----------
    Fraction(8) : Sets the respective numeral.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._numeral: o.TypeNumeral = Fraction(8)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case Fraction():            return self._numeral
                    case _:                     return super().__mod__(operand)
            case Fraction():            return self._numeral
            case int():                 return int(self._numeral)
            case float():               return float(self._numeral)
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["numeral"] = self.serialize( self._numeral )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "numeral" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._numeral = self.deserialize( serialization["parameters"]["numeral"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
                self._numeral = operand._numeral
            case od.Pipe():
                match operand._data:
                    case Fraction():                self._numeral = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case _: # o.TypeNumeral
                if isinstance(operand, (int, float, Fraction, o.Operand)):
                    self._numeral = operand
        return self

class Modulo(Manipulator):
    """`Tamer -> Manipulator -> Modulo`

    This `Modulo` does the module by a given value.

    Parameters
    ----------
    Fraction(8), int, float : Sets the respective `Modulus`.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral, iterate)
        # A `Manipulator` shall always be triggered regardless of being previously validated or not
        self_numeral: Fraction = self._numeral
        if isinstance(self._numeral, o.Operand):
            self_numeral = self._numeral % Fraction()
        if isinstance(numeral, o.Operand):
            numeral << numeral % Fraction() % self_numeral
        else:
            numeral %= self_numeral
        return numeral, validated
    

class Increase(Manipulator):
    """`Tamer -> Manipulator -> Increase`

    `Increase` adds a given amount to the given `Rational`.

    Parameters
    ----------
    Fraction(8), int, float : Sets the respective increasing amount.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral, iterate)
        # A `Manipulator` shall always be triggered regardless of being previously validated or not
        numeral += self._numeral
        return numeral, validated
    

class Decrease(Manipulator):
    """`Tamer -> Manipulator -> Decrease`

    `Decrease` subtracts a given amount to the given `Rational`.

    Parameters
    ----------
    Fraction(8), int, float : Sets the respective decrement amount.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral, iterate)
        # A `Manipulator` shall always be triggered regardless of being previously validated or not
        numeral -= self._numeral
        return numeral, validated


class Repeat(Manipulator):
    """`Tamer -> Manipulator -> Repeat`

    `Repeat` returns the previous `Rational` numeral resulting in its repetition.

    Parameters
    ----------
    None
    """
    def __init__(self, *parameters):
        super().__init__()
        self._numeral: o.TypeNumeral | None = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral)
        # A `Manipulator` shall always be triggered regardless of being previously validated or not
        if self._numeral is not None:
            numeral = self._numeral
        if iterate: # Has to be after the fact
            self.next(numeral)
        return numeral, validated
    
    # CHAINABLE OPERATIONS

    def reset(self, *parameters) -> Self:
        self._numeral = None
        return super().reset(*parameters)
    
    def next(self, numeral: o.TypeNumeral) -> Self:
        """Only called by the first link of the chain if all links are validated"""
        self._numeral = numeral
        return super().next(numeral)


class Wrap(Manipulator):
    """`Tamer -> Manipulator -> Wrap`

    `Wrap` wraps the `Numeral` into a different class than `Fraction`.

    Parameters
    ----------
    Any() : Sets the type of object to wrap the numeral.
    """
    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral, iterate)
        # A `Manipulator` shall always be triggered regardless of being previously validated or not
        numeral = self._numeral.__class__(numeral)
        return numeral, validated
    

class Switch(Manipulator):
    """`Tamer -> Manipulator -> Switch`

    A `Switch` returns 0 or 1 depending of Numeral being below the threshold or not.

    Parameters
    ----------
    Fraction(1), int, float : Sets the respective switch threshold.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._numeral: o.TypeNumeral = 1
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, numeral: o.TypeNumeral, iterate: bool = False) -> tuple[o.TypeNumeral, bool]:
        numeral, validated = super().tame(numeral, iterate)
        # A `Manipulator` shall always be triggered regardless of being previously validated or not
        numeral = Fraction(0) if numeral < self._numeral else Fraction(1)
        return numeral, validated

