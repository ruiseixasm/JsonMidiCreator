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

    Tamer, contrarily to Randomness, is repeatable and has order in it.
    This class allows trough parametrization the unpredictable return of data
    and processing of other `Operand` in a repeatable way.

    Parameters
    ----------
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Tamer can be reset to.
    """
    def __init__(self, *parameters):
        super().__init__()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def number_to_int(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> int:
        match number:
            case ou.Unit() | ra.Rational():
                return number % int()
            case int() | float() | Fraction():
                return int(number)
        return 0

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ra.Xn():               return self._xn
                    case ra.X0():               return self._x0
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case Tamer():               return self.copy()
            case ra.Xn():               return self._xn.copy()
            case ra.X0():               return self._x0.copy()
            case int() | float():
                self.__imul__(operand)  # Numbers trigger iterations
                return self._xn % operand
            case list():
                list_out: list = []
                for number in operand:
                    list_out.append(self % number)  # Implicit iterations
                return list_out
            case _:                     return super().__mod__(operand)

    def __str__(self) -> str:
        return f'{self._index + 1}: {self._xn % float()}'
    
    def __eq__(self, other: 'Tamer') -> bool:
        if other.__class__ == o.Operand:
            return True
        if type(self) == type(other):
            return self._xn == other._xn    # Only the actual result matters, NOT the x0
        if isinstance(other, od.Conditional):
            return other == self
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["xn"] = self.serialize( self._xn )
        serialization["parameters"]["x0"] = self.serialize( self._x0 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "xn" in serialization["parameters"] and "x0" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._xn = self.deserialize( serialization["parameters"]["xn"] )
            self._x0 = self.deserialize( serialization["parameters"]["x0"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Tamer():
                super().__lshift__(operand)
                self._xn            << operand._xn
                self._x0            << operand._x0
            case od.Pipe():
                match operand._data:
                    case ra.Xn():                   self._xn = operand._data
                    case ra.X0():                   self._x0 = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Xn():                   self._xn << operand
            case ra.X0():                   self._x0 << operand
            case int() | float():
                self.__imul__(operand)  # Numbers trigger iterations
                self._xn << operand
                self._x0 << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def iterate(self, times: int = 0) -> Self:
        self._initiated = True
        for _ in range(times):
            # INSERT CODE HERE
            self._index += 1    # keeps track of each iteration
        return self

    def __imul__(self, number: Union[int, float, Fraction, ou.Unit, ra.Rational]) -> Self:
        number ^= self # Extracts the Frame operand first
        total_iterations = self.number_to_int(number)
        if total_iterations > 0:
            if isinstance(self._next_operand, Tamer):
                # iterations are only done on tailed Tamer operands
                self << self._next_operand.iterate(total_iterations)
            return self.iterate(total_iterations)
        return self
    
    # self is the pusher
    def __rshift__(self, operand: any) -> Self:
        return self.__irshift__(operand)    # Does no Copy !!

    # Pass trough method that always results in a Tamer (Self)
    def __irshift__(self, operand: any) -> Self:
        return self.__imul__(operand)
    
    def __pow__(self, operand: o.Operand) -> Self:
        match operand:
            case Tamer():       self._next_operand = operand
            case _:             self._next_operand = None
        return self

    def reset(self, *parameters) -> Self:
        super().reset(*parameters)
        self._xn << self._x0
        return self

class Validator(Tamer):
    """`Tamer -> Validator`

    Increments the Xn by each step and its return is the remainder of the given cycle.

    Parameters
    ----------
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Tamer can be reset to.
    Cycle(12) : The cyclic value on which the `Xn` modulus % operation is made.
    Steps(1) : The increase amount for each iteration.
    """
    pass
            

class Manipulator(Tamer):
    """`Tamer -> Manipulator`

    Manipulator works much alike the moving word in a screen saver.
    So, it is a two dimensional data generator, with a Xn and a Yn.
    The `Manipulator() % int()` and `Manipulator() % float()` returns the hypotenuse.

    Parameters
    ----------
    Width(16) : Horizontal size of the "screen".
    Height(9) : Vertical size of the "screen".
    dX(0.555) : The incremental value for the horizontal position.
    dY(0.555) : The incremental value for the vertical position.
    Xn(Width(16) / 2), int, float : The resultant horizontal value of each iteration.
    Yn(Height(9) / 2) : The resultant vertical value of each iteration.
    """
    pass
