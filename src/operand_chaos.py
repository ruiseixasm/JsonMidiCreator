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
import operand_tamer as ot


class Chaos(o.Operand):
    """`Chaos`

    Chaos, contrarily to Randomness, is repeatable and has order in it.
    This class allows trough parametrization the unpredictable return of data
    and processing of other `Operand` in a repeatable way.

    Parameters
    ----------
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._tamer: ot.Tamer           = None
        self._max_iterations: int       = 1000
        self._xn: ra.Xn                 = ra.Xn()
        self._x0: ra.X0                 = ra.X0(self._xn)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def number_to_int(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> int:
        match number:
            case ou.Unit() | ra.Rational():
                return number % int()
            case int() | float() | Fraction():
                return int(number)
        return 0

    def tame(self, number: Fraction) -> bool:
        if self._tamer is not None:
            return self._tamer.tame(number, True)[1]
        return True

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ot.Tamer():            return self._tamer
                    case ra.Xn():               return self._xn
                    case ra.X0():               return self._x0
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case Chaos():               return self.copy()
            case ot.Tamer():            return self.deep_copy(self._tamer)
            case ra.Xn():               return self._xn.copy()
            case ra.X0():               return self._x0.copy()
            case int() | float() | Fraction():
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
    
    def __eq__(self, other: 'Chaos') -> bool:
        if other.__class__ == o.Operand:
            return True
        if type(self) == type(other):
            return self._xn == other._xn    # Only the actual result matters, NOT the x0
        if isinstance(other, od.Conditional):
            return other == self
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tamer"] = self.serialize( self._tamer )
        serialization["parameters"]["xn"] = self.serialize( self._xn )
        serialization["parameters"]["x0"] = self.serialize( self._x0 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tamer" in serialization["parameters"] and "xn" in serialization["parameters"] and "x0" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tamer = self.deserialize( serialization["parameters"]["tamer"] )
            self._xn = self.deserialize( serialization["parameters"]["xn"] )
            self._x0 = self.deserialize( serialization["parameters"]["x0"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Chaos():
                super().__lshift__(operand)
                self._tamer         = self.deep_copy(operand._tamer)
                self._xn            << operand._xn
                self._x0            << operand._x0
            case od.Pipe():
                match operand._data:
                    case ot.Tamer():                self._tamer = operand._data
                    case ra.Xn():                   self._xn = operand._data
                    case ra.X0():                   self._x0 = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ot.Tamer():                self._tamer = operand.copy()
            case None:                      self._tamer = None
            case ra.Xn():                   self._xn << operand
            case ra.X0():                   self._x0 << operand
            case int() | float() | Fraction():
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
            tamed: bool = False
            count_down: int = self._max_iterations
            while not tamed and count_down > 0:
                if isinstance(self._next_operand, Chaos):
                    # iterations are only done on tailed Chaos operands
                    self << self._next_operand.iterate(total_iterations)
                self.iterate(total_iterations)
                tamed = self.tame(self % Fraction())
                count_down -= 1
        return self
    
    # self is the pusher
    def __rshift__(self, operand: any) -> Self:
        return self.__irshift__(operand)    # Does no Copy !!

    # Pass trough method that always results in a Chaos (Self)
    def __irshift__(self, operand: any) -> Self:
        return self.__imul__(operand)
    
    def __pow__(self, operand: o.Operand) -> Self:
        match operand:
            case Chaos():       self._next_operand = operand
            case _:             self._next_operand = None
        return self

    def reset(self, *parameters) -> Self:
        super().reset(*parameters)
        self._xn << self._x0
        return self

class Modulus(Chaos):
    """`Chaos -> Modulus`

    Increments the Xn by each step and its return is the remainder of the given cycle.

    Parameters
    ----------
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    Cycle(12) : The cyclic value on which the `Xn` modulus % operation is made.
    Steps(1) : The increase amount for each iteration.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._period: Fraction  = ra.Period(12)._rational
        self._steps: Fraction   = ra.Steps(1)._rational
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Period():           return operand._data << self._period
                    case ra.Steps():            return operand._data << self._steps
                    case _:                     return super().__mod__(operand)
            case ra.Period():           return ra.Period(self._period)
            case ra.Steps():            return ra.Steps(self._period)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: Any) -> bool:
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._period == other._period and self._steps == other._steps
            case _:
                return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["period"]   = self.serialize( self._period )
        serialization["parameters"]["steps"]    = self.serialize( self._steps )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "period" in serialization["parameters"] and "steps" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._period    = self.deserialize( serialization["parameters"]["period"] )
            self._steps     = self.deserialize( serialization["parameters"]["steps"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Modulus():
                super().__lshift__(operand)
                self._period     = operand._period
                self._steps     = operand._steps
            case od.Pipe():
                match operand._data:
                    case ra.Period():           self._period = operand._data._rational
                    case ra.Steps():            self._steps = operand._data._rational
                    case _:                     super().__lshift__(operand)
            case ra.Period():      self._period = operand._rational
            case ra.Steps():       self._steps = operand._rational
            case _:
                super().__lshift__(operand)
        # Makes sure xn isn't out of the cycle
        self._xn << (self._xn % float()) % float(self._period)
        return self

    def iterate(self, times: int = 0) -> Self:
        self._initiated = True
        for _ in range(times):
            self._xn += self._steps
            self._xn << (self._xn % float()) % float(self._period)
            self._index += 1    # keeps track of each iteration
        return self


class Flipper(Modulus):
    """`Chaos -> Modulus -> Flipper`

    The Xn alternates like left and right, where left is 0 and right is 1.
    It works just like a Modulus with the difference of returning only 0 or 1,
    where a given split defines what belongs to left and what to right.

    Parameters
    ----------
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    Cycle(2) : The cyclic value on which the `Xn` modulus % operation is made.
    Steps(1) : The increase amount for each iteration.
    Split(1) : This sets the value below which is considered a "left" flip.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._period             = ra.Period(2)._rational
        self._split: Fraction   = ra.Split(1)._rational
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Split():            return self._split
                    case _:                     return super().__mod__(operand)
            case ra.Split():            return self._split.copy()
            case Fraction():
                self.__imul__(operand)  # Numbers trigger iterations
                return Fraction(0) if super().__mod__(Fraction()) < self._split else Fraction(1)
            case int():
                self.__imul__(operand)  # Numbers trigger iterations
                return 0 if super().__mod__(int()) < int(self._split) else 1
            case float():
                self.__imul__(operand)  # Numbers trigger iterations
                return 0.0 if super().__mod__(float()) < float(self._split) else 1.0
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: Any) -> bool:
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._split == other._split
            case _:
                return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["split"] = self.serialize( self._split )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "split" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._split = self.deserialize( serialization["parameters"]["split"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Flipper():
                super().__lshift__(operand)
                self._split = operand._split
            case od.Pipe():
                match operand._data:
                    case ra.Split():                self._split = operand._data._rational
                    case _:                         super().__lshift__(operand)
            case ra.Split():                self._split = operand._rational
            case _:
                super().__lshift__(operand)
        return self

class Counter(Modulus):
    """`Chaos -> Modulus -> Counter`

    The Xn represents the total number of completed cycles.
    Contrary to modulus, the counter returns the amount of completed cycles.

    Parameters
    ----------
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    Cycle(12) : The cyclic value on which the `Xn` modulus % operation is made.
    Steps(1) : The increase amount for each iteration.
    """
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case Fraction():
                self.__imul__(operand)  # Numbers trigger iterations
                return super().__mod__(Fraction()) // self._period
            case int():
                self.__imul__(operand)  # Numbers trigger iterations
                return super().__mod__(int()) // int(self._period)
            case float():
                self.__imul__(operand)  # Numbers trigger iterations
                return super().__mod__(float()) // float(self._period)
            case _:
                return super().__mod__(operand)


class Bouncer(Chaos):
    """`Chaos -> Bouncer`

    Bouncer works much alike the moving word in a screen saver.
    So, it is a two dimensional data generator, with a Xn and a Yn.
    The `Bouncer() % int()` and `Bouncer() % float()` returns the hypotenuse.

    Parameters
    ----------
    Width(16) : Horizontal size of the "screen".
    Height(9) : Vertical size of the "screen".
    dX(0.555) : The incremental value for the horizontal position.
    dY(0.555) : The incremental value for the vertical position.
    Xn(Width(16) / 2), int, float : The resultant horizontal value of each iteration.
    Yn(Height(9) / 2) : The resultant vertical value of each iteration.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._width: ra.Width   = ra.Width(16)
        self._height: ra.Height = ra.Height(9)
        self._dx: ra.dX         = ra.dX(0.555)
        self._dy: ra.dY         = ra.dY(0.555)
        self._xn                = ra.Xn(self._width / 2 % Fraction())
        self._x0                = ra.X0(self._xn)
        self._yn: ra.Yn         = ra.Yn(self._height / 2 % Fraction())
        self._y0: ra.Y0         = ra.Y0(self._yn)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Width():            return self._width
                    case ra.Height():           return self._height
                    case ra.dX():               return self._dx
                    case ra.dY():               return self._dy
                    case ra.Xn():               return self._xn
                    case ra.X0():               return self._x0
                    case ra.Yn():               return self._yn
                    case ra.Y0():               return self._y0
                    case _:                     return super().__mod__(operand)
            case ra.Width():            return self._width.copy()
            case ra.Height():           return self._height.copy()
            case ra.dX():               return self._dx.copy()
            case ra.dY():               return self._dy.copy()
            case ra.Xn():               return self._xn.copy()
            case ra.X0():               return self._x0.copy()
            case ra.Yn():               return self._yn.copy()
            case ra.Y0():               return self._y0.copy()
            case int() | float() | Fraction():
                self.__imul__(operand)  # Numbers trigger iterations
                hypotenuse = math.hypot(self._xn % float(), self._yn % float())
                if isinstance(operand, int):
                    return int(hypotenuse)
                if isinstance(operand, Fraction):
                    return Fraction(hypotenuse)
                return hypotenuse
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Bouncer') -> bool:
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._xn == other._xn and self._yn == other._yn
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["width"]    = self.serialize( self._width )
        serialization["parameters"]["height"]   = self.serialize( self._height )
        serialization["parameters"]["dx"]       = self.serialize( self._dx )
        serialization["parameters"]["dy"]       = self.serialize( self._dy )
        serialization["parameters"]["xn"]       = self.serialize( self._xn )
        serialization["parameters"]["x0"]       = self.serialize( self._x0 )
        serialization["parameters"]["yn"]       = self.serialize( self._yn )
        serialization["parameters"]["y0"]       = self.serialize( self._y0 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "width" in serialization["parameters"] and "height" in serialization["parameters"] and "dx" in serialization["parameters"] and
            "dy" in serialization["parameters"] and "xn" in serialization["parameters"] and "x0" in serialization["parameters"] and 
            "yn" in serialization["parameters"] and "y0" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._width     = self.deserialize( serialization["parameters"]["width"] )
            self._height    = self.deserialize( serialization["parameters"]["height"] )
            self._dx        = self.deserialize( serialization["parameters"]["dx"] )
            self._dy        = self.deserialize( serialization["parameters"]["dy"] )
            self._xn        = self.deserialize( serialization["parameters"]["xn"] )
            self._x0        = self.deserialize( serialization["parameters"]["x0"] )
            self._yn        = self.deserialize( serialization["parameters"]["yn"] )
            self._y0        = self.deserialize( serialization["parameters"]["y0"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Bouncer():
                super().__lshift__(operand)
                self._width     << operand._width
                self._height    << operand._height
                self._dx        << operand._dx
                self._dy        << operand._dy
                self._xn        << operand._xn
                self._x0        << operand._x0
                self._yn        << operand._yn
                self._y0        << operand._y0
            case od.Pipe():
                match operand._data:
                    case ra.Width():    self._width = operand._data
                    case ra.Height():   self._height = operand._data
                    case ra.dX():       self._dx = operand._data
                    case ra.dY():       self._dy = operand._data
                    case ra.Xn():       self._xn = operand._data
                    case ra.X0():       self._x0 = operand._data
                    case ra.Yn():       self._yn = operand._data
                    case ra.Y0():       self._y0 = operand._data
                    case _:             super().__lshift__(operand)
            case ra.Width():    self._width << operand
            case ra.Height():   self._height << operand
            case ra.dX():       self._dx << operand
            case ra.dY():       self._dy << operand
            case ra.Xn():       self._xn << operand
            case ra.X0():       self._x0 << operand
            case ra.Yn():       self._yn << operand
            case ra.Y0():       self._y0 << operand
            case _: super().__lshift__(operand)
        # Final needed modulation
        self._xn << (self._xn % float()) % (self._width % float())
        self._yn << (self._yn % float()) % (self._height % float())
        return self

    def iterate(self, times: int = 0) -> Self:
        self._initiated = True
        for _ in range(times):
            for direction_data in [(self._xn, self._dx, self._width), (self._yn, self._dy, self._height)]:
                new_position = direction_data[0] + direction_data[1]
                if new_position < 0:
                    direction_data[1] << direction_data[1] * -1 # flips direction
                    new_position = new_position * -1 % direction_data[2]
                elif new_position >= direction_data[2]:
                    direction_data[1] << direction_data[1] * -1 # flips direction
                    new_position = direction_data[2] - new_position % direction_data[2]
                direction_data[0] << new_position
            self._index += 1    # keeps track of each iteration
        return self

    def __str__(self) -> str:
        return f'{self._index + 1}: {self % tuple()}'
    
    def reset(self, *parameters) -> Self:
        super().reset(*parameters)
        self._xn    << self._x0
        self._yn    << self._y0
        return self

class SinX(Chaos):
    """`Chaos -> SinX`

    Represents a more traditional chaotic formulation with the use of the Sin function.

    Parameters
    ----------
    Xn(2), int, float : The resultant value of each iteration.
    X0(Xn(2)) : The starting value of all iterations possible to reset to.
    Lambda(77.238537) : Sets the lambda constant of the formula `Xn + Lambda * Sin(Xn)`.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._xn                        << 2
        self._x0                        << self._xn
        self._lambda: ra.Lambda         = ra.Lambda(77.238537) # Can't be an integer in order to be truly chaotic !!
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Lambda():           return self._lambda
                    case _:                     return super().__mod__(operand)
            case ra.Lambda():           return self._lambda.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'SinX') -> bool:
        if other.__class__ == o.Operand:
            return True
        if super().__eq__(other):
            return  self._lambda == other % od.Pipe( ra.Lambda() )
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["lambda"] = self.serialize( self._lambda )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "lambda" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._lambda = self.deserialize( serialization["parameters"]["lambda"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case SinX():
                super().__lshift__(operand)
                self._lambda            << operand._lambda
            case od.Pipe():
                match operand._data:
                    case ra.Lambda():               self._lambda = operand._data
                    case _:                         super().__lshift__(operand)
            case ra.Lambda():               self._lambda << operand
            case ra.Xn():                   self._xn << operand
            case ra.X0():                   self._x0 << operand
            case int() | float():
                                            self._xn << operand
                                            self._x0 << operand
            case _: super().__lshift__(operand)
        return self

    def iterate(self, times: int = 0) -> Self:
        self._initiated = True
        for _ in range(times):
            self._xn << self._xn % float() + self._lambda % float() * math.sin(self._xn % float())
            self._index += 1    # keeps track of each iteration
        return self


