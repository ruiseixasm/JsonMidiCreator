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
        self._xn: ra.Xn                 = ra.Xn()
        self._x0: ra.X0                 = ra.X0(self._xn)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ra.Xn():               return self._xn
                    case ra.X0():               return self._x0
                    case int() | float():       return self._xn % operand._data
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case Chaos():               return self.copy()
            case ra.Xn():               return self._xn.copy()
            case ra.X0():               return self._x0.copy()
            case int() | float():       return self._xn % operand
            case list():
                list_out: list = []
                for number in operand:
                    if isinstance(number, (int, float, Fraction)):
                        self.__imul__(int(number))
                    if isinstance(number, (ou.Unit, ra.Rational)):
                        self.__imul__(number % int())
                    list_out.append(self._xn % operand)
                return list_out
            case _:                     return super().__mod__(operand)

    def __str__(self) -> str:
        return f'{self._index + 1}: {self._xn % float()}'
    
    def __eq__(self, other: 'Chaos') -> bool:
        if other.__class__ == o.Operand:
            return True
        if type(self) == type(other):
            return  self._xn == other._xn \
                and self._x0 == other._x0
        if isinstance(other, od.Conditional):
            return other == self
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["xn"] = self.serialize( self._xn )
        serialization["parameters"]["x0"] = self.serialize( self._x0 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Chaos':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "xn" in serialization["parameters"] and "x0" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._xn    = self.deserialize( serialization["parameters"]["xn"] )
            self._x0    = self.deserialize( serialization["parameters"]["x0"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Chaos():
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
                                            self._xn << operand
                                            self._x0 << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def reportable_per_total_iterations(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> tuple:
        iterations = 1
        match number:
            case ou.Unit() | ra.Rational():
                iterations = number % float()
            case int() | float() | Fraction():
                iterations = float(number)
        fractional_part, integer_part = math.modf(iterations)  # Separate fractional and integer parts
        reportable_iteration: int = round(fractional_part * 10**2)  # It has to be round given the float point error
        total_iterations: int = round(integer_part)                 # It has to be round given the float point error
        return reportable_iteration, total_iterations

    def __imul__(self, number: Union[int, float, Fraction, ou.Unit, ra.Rational]) -> Self:
        number = self._tail_imul(number)    # Processes the tailed self operands or the Frame operand if any exists
        # This results in just int numbers
        reportable_iteration, total_iterations = self.reportable_per_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(total_iterations):
                if reportable_iteration > 0 and actual_iteration % reportable_iteration == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
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

    def _tail_imul(self, number: o.T) -> o.T:
        number ^= self # Extracts the Frame operand first
        if self._next_operand:
            # iteration is only done on tailed chaos operands and never on self
            self << self._next_operand.__imul__(number) # __imul__ already includes __or__
        return number   # Has to keep compatibility with Operand __or__ method

    def report(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Chaos':
        if not isinstance(number, (int, ou.Unit)):  # Report only when floats are used
            print(f'{type(self).__name__} {self}')
        return self

    def reset(self, *parameters) -> 'Chaos':
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
        self._cycle: Fraction   = ra.Period(12)._rational
        self._steps: Fraction   = ra.Steps(1)._rational
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Period():            return operand._data << self._cycle
                    case ra.Steps():            return operand._data << self._steps
                    case _:                     return super().__mod__(operand)
            case ra.Period():            return ra.Period(self._cycle)
            case ra.Steps():            return ra.Steps(self._cycle)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: Any) -> bool:
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._cycle == other._cycle and self._steps == other._steps
            case _:
                return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["cycle"]    = self.serialize( self._cycle )
        serialization["parameters"]["steps"]    = self.serialize( self._steps )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Modulus':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "cycle" in serialization["parameters"] and "steps" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._cycle = self.deserialize( serialization["parameters"]["cycle"] )
            self._steps = self.deserialize( serialization["parameters"]["steps"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Modulus():
                super().__lshift__(operand)
                self._cycle     = operand._cycle
                self._steps     = operand._steps
            case od.Pipe():
                match operand._data:
                    case ra.Period():            self._cycle = operand._data._rational
                    case ra.Steps():            self._steps = operand._data._rational
                    case _:                     super().__lshift__(operand)
            case ra.Period():       self._cycle = operand._rational
            case ra.Steps():       self._steps = operand._rational
            case _:
                super().__lshift__(operand)
        # Makes sure xn isn't out of the cycle
        self._xn << (self._xn % float()) % float(self._cycle)
        return self

    def __imul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Modulus':
        number = self._tail_imul(number)    # Processes the tailed self operands or the Frame operand if any exists
        reportable_iteration, total_iterations = self.reportable_per_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(total_iterations):
                self._xn += self._steps
                self._xn << (self._xn % float()) % float(self._cycle)
                if reportable_iteration > 0 and actual_iteration % reportable_iteration == 0:
                    self.report(number)
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
        self._cycle             = ra.Period(2)._rational
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
            case int():                 return 0 if super().__mod__(int()) < int(self._split) else 1
            case float():               return 0.0 if super().__mod__(float()) < float(self._split) else 1.0
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

    def loadSerialization(self, serialization: dict):
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
                                        # These are math operations, NOT extractions with //
            case int():                 return super().__mod__(int()) // int(self._cycle)
            case float():               return super().__mod__(float()) // float(self._cycle)
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
        self._width: ra.Width           = ra.Width(16)
        self._height: ra.Height         = ra.Height(9)
        self._dx: ra.dX                 = ra.dX(0.555)
        self._dy: ra.dY                 = ra.dY(0.555)
        self._xn: ra.Xn                 = ra.Xn(self._width / 2 % Fraction())
        self._yn: ra.Yn                 = ra.Yn(self._height / 2 % Fraction())
        self._set_xy: tuple             = (self._xn.copy(), self._yn.copy())
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
                    case ra.Yn():               return self._yn
                    case int() | float():
                        self_tuple = self % od.Pipe( tuple() )
                        hypotenuse = math.hypot(self_tuple[0], self_tuple[1])
                        if isinstance(operand, int):
                            return int(hypotenuse)
                        return hypotenuse
                    case tuple():
                        self_x_float = self._xn % float()
                        self_y_float = self._yn % float()
                        return (self_x_float, self_y_float)
                    case _:                     return super().__mod__(operand)
            case ra.Width():            return self._width.copy()
            case ra.Height():           return self._height.copy()
            case ra.dX():               return self._dx.copy()
            case ra.dY():               return self._dy.copy()
            case ra.Xn():               return self._xn.copy()
            case ra.Yn():               return self._yn.copy()
            case int() | float() | tuple():
                                        return self % od.Pipe( operand )
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Bouncer') -> bool:
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._xn == other._xn and self._yn == other._yn
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["width"]        = self.serialize( self._width )
        serialization["parameters"]["height"]       = self.serialize( self._height )
        serialization["parameters"]["dx"]           = self.serialize( self._dx )
        serialization["parameters"]["dy"]           = self.serialize( self._dy )
        serialization["parameters"]["xn"]           = self.serialize( self._xn )
        serialization["parameters"]["yn"]           = self.serialize( self._yn )
        serialization["parameters"]["set_xy"]       = self.serialize( self._set_xy )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Modulus':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "width" in serialization["parameters"] and "height" in serialization["parameters"] and "dx" in serialization["parameters"] and
            "dy" in serialization["parameters"] and "xn" in serialization["parameters"] and "yn" in serialization["parameters"] and
            "set_xy" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._width             = self.deserialize( serialization["parameters"]["width"] )
            self._height            = self.deserialize( serialization["parameters"]["height"] )
            self._dx                = self.deserialize( serialization["parameters"]["dx"] )
            self._dy                = self.deserialize( serialization["parameters"]["dy"] )
            self._xn                = self.deserialize( serialization["parameters"]["xn"] )
            self._yn                = self.deserialize( serialization["parameters"]["yn"] )
            self._set_xy            = tuple(self.deserialize( serialization["parameters"]["set_xy"] ))
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand ^= self    # Processes the Frame operand if any exists
        match operand:
            case Bouncer():
                super().__lshift__(operand)
                self._width         << operand._width
                self._height        << operand._height
                self._dx            << operand._dx
                self._dy            << operand._dy
                self._xn            << operand._xn
                self._yn            << operand._yn
                set_x               = operand._set_xy[0].copy()
                set_y               = operand._set_xy[1].copy()
                self._set_xy        = (set_x, set_y)
            case od.Pipe():
                match operand._data:
                    case ra.Width():                self._width = operand._data
                    case ra.Height():               self._height = operand._data
                    case ra.dX():                   self._dx = operand._data
                    case ra.dY():                   self._dy = operand._data
                    case ra.Xn():                   self._xn = operand._data
                    case ra.Yn():                   self._yn = operand._data
                    case _:                         super().__lshift__(operand)
            case ra.Width():                self._width << operand
            case ra.Height():               self._height << operand
            case ra.dX():                   self._dx << operand
            case ra.dY():                   self._dy << operand
            case ra.Xn():                   self._xn << operand
            case ra.Yn():                   self._yn << operand
            case _: super().__lshift__(operand)
        self._xn << (self._xn % float()) % (self._width % float())
        self._yn << (self._yn % float()) % (self._height % float())
        return self

    def __imul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Bouncer':
        number = self._tail_imul(number)    # Processes the tailed self operands or the Frame operand if any exists
        reportable_iteration, total_iterations = self.reportable_per_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(total_iterations):
                for direction_data in [(self._xn, self._dx, self._width), (self._yn, self._dy, self._height)]:
                    new_position = direction_data[0] + direction_data[1]
                    if new_position < 0:
                        direction_data[1] << direction_data[1] * -1 # flips direction
                        new_position = new_position * -1 % direction_data[2]
                    elif new_position >= direction_data[2]:
                        direction_data[1] << direction_data[1] * -1 # flips direction
                        new_position = direction_data[2] - new_position % direction_data[2]
                    direction_data[0] << new_position
                if reportable_iteration > 0 and actual_iteration % reportable_iteration == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self

    def __str__(self) -> str:
        return f'{self._index + 1}: {self % tuple()}'
    
    def reset(self, *parameters) -> 'Bouncer':
        super().reset(*parameters)
        self._xn        << self._set_xy[0]
        self._yn        << self._set_xy[1]
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
        serialization["parameters"]["lambda"]   = self.serialize( self._lambda )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Modulus':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "lambda" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._lambda            = self.deserialize( serialization["parameters"]["lambda"] )
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

    def __imul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'SinX':
        number = self._tail_imul(number)    # Processes the tailed self operands or the Frame operand if any exists
        reportable_iteration, total_iterations = self.reportable_per_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(total_iterations):
                self._xn << self._xn % float() + self._lambda % float() * math.sin(self._xn % float())
                if reportable_iteration > 0 and actual_iteration % reportable_iteration == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self


