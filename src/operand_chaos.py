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
from typing import Union, TypeVar, TYPE_CHECKING
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
import operand_label as ol
import operand_generic as og
import operand_frame as of

TypeChaos = TypeVar('TypeChaos', bound='Chaos')  # TypeChaos represents any subclass of Operand


class Chaos(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        self._xn: ra.Xn                 = ra.Xn()
        self._x0: ra.X0                 = ra.X0(self._xn)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case ra.Xn():               return self._xn
                    case ra.X0():               return self._x0
                    case int() | float():       return self._xn % (operand._data)
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % (operand._data)
            case Chaos():               return self.copy()
            case ra.Xn():               return self._xn.copy()
            case ra.X0():               return self._x0.copy()
            case int() | float():       return self._xn % operand
            case ou.Next():             return self * operand
            case _:                     return super().__mod__(operand)

    def __str__(self) -> str:
        return f'{self._index + 1}: {self._xn % float()}'
    
    def __eq__(self, other: 'Chaos') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) == type(other):
            return  self._xn == other._xn \
                and self._x0 == other._x0
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
        
    def __lshift__(self, operand: any) -> TypeChaos:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Chaos():
                super().__lshift__(operand)
                self._xn            << operand._xn
                self._x0            << operand._x0
            case od.DataSource():
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

    def muted_and_total_iterations(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> tuple:
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        iterations = 1
        match number:
            case ou.Unit() | ra.Rational():
                iterations = number % float()
            case int() | float() | Fraction():
                iterations = float(number)
        fractional_part, integer_part = math.modf(iterations)  # Separate fractional and integer parts
        muted_iterations: int = round(abs(fractional_part) * (10 ** 2) + 1)
        total_iterations: int = round(integer_part * muted_iterations)
        return muted_iterations, total_iterations

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Chaos':
        muted_iterations, total_iterations = self.muted_and_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(1, total_iterations + 1):
                if actual_iteration % muted_iterations == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self
    
    def report(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Chaos':
        if not isinstance(number, (int, ou.Unit)):  # Report only when floats are used
            print(f'{type(self).__name__} {self}')
        return self

    def reset(self, *parameters) -> 'Chaos':
        super().reset(*parameters)
        self._xn << self._x0
        return self

class Modulus(Chaos):
    def __init__(self, *parameters):
        super().__init__()
        self._amplitude: ra.Amplitude   = ra.Amplitude(12)
        self._steps: ra.Steps             = ra.Steps(1)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case ra.Amplitude():        return self._amplitude
                    case ra.Steps():             return self._steps
                    case _:                     return super().__mod__(operand)
            case ra.Amplitude():        return self._amplitude.copy()
            case ra.Steps():             return self._steps.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Chaos') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if super().__eq__(other):
            return  self._amplitude == other % od.DataSource( ra.Amplitude() ) \
                and self._steps == other % od.DataSource( ra.Steps() )
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["amplitude"]    = self.serialize( self._amplitude )
        serialization["parameters"]["steps"]         = self.serialize( self._steps )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Modulus':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "amplitude" in serialization["parameters"] and "steps" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._amplitude         = self.deserialize( serialization["parameters"]["amplitude"] )
            self._steps              = self.deserialize( serialization["parameters"]["steps"] )
        return self
        
    def __lshift__(self, operand: any) -> TypeChaos:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Modulus():
                super().__lshift__(operand)
                self._amplitude     << operand._amplitude
                self._steps         << operand._steps
            case od.DataSource():
                match operand._data:
                    case ra.Amplitude():            self._amplitude = operand._data
                    case ra.Steps():                 self._steps = operand._data
                    case _:                         super().__lshift__(operand)
            case ra.Amplitude():            self._amplitude << operand
            case ra.Steps():                self._steps << operand
            case _: super().__lshift__(operand)
        self._xn << (self._xn % float()) % (self._amplitude % float())
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Modulus':
        muted_iterations, total_iterations = self.muted_and_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(1, total_iterations + 1):
                self._xn += self._steps
                self._xn << (self._xn % float()) % (self._amplitude % float())
                if actual_iteration % muted_iterations == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self

class Flipper(Modulus):
    def __init__(self, *parameters):
        super().__init__()
        self._amplitude                 << 2
        self._split: ra.Split           = ra.Split(1)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case ra.Split():            return self._split
                    case int() | float():
                        self_index = super().__mod__(od.DataSource( operand._data ))
                        if isinstance(operand._data, int):
                            return 0 if self_index < self._split % int() else 1
                        return 0.0 if self_index < self._split % float() else 1.0
                    case _:                     return super().__mod__(operand)
            case ra.Split():            return self._split.copy()
            case int():                 return 0 if super().__mod__(int()) < self._split % int() else 1
            case float():               return 0.0 if super().__mod__(float()) < self._split % float() else 1.0
            case int() | float():       return self % od.DataSource( operand )
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Flipper') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if super().__eq__(other):
            return  self._split == other % od.DataSource( ra.Split() )
        return False
    
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
      
    def __lshift__(self, operand: any) -> TypeChaos:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Flipper():
                super().__lshift__(operand)
                self._split         << operand._split
            case od.DataSource():
                match operand._data:
                    case ra.Split():                self._split = operand._data
                    case _:                         super().__lshift__(operand)
            case ra.Split():                self._split << operand
            case _: super().__lshift__(operand)
        return self

class Bouncer(Chaos):
    def __init__(self, *parameters):
        super().__init__()
        self._width: ra.Width           = ra.Width(16)
        self._height: ra.Height         = ra.Height(9)
        self._dx: ra.dX                 = ra.dX(0.555)
        self._dy: ra.dY                 = ra.dY(0.555)
        self._x: ra.X                   = ra.X(self._width / 2 % Fraction())
        self._y: ra.Y                   = ra.Y(self._height / 2 % Fraction())
        self._set_xy: tuple             = (self._x.copy(), self._y.copy())
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case ra.Width():            return self._width
                    case ra.Height():           return self._height
                    case ra.dX():               return self._dx
                    case ra.dY():               return self._dy
                    case ra.X():                return self._x
                    case ra.Y():                return self._y
                    case int() | float():
                        self_tuple = self % od.DataSource( tuple() )
                        hypotenuse = math.hypot(self_tuple[0], self_tuple[1])
                        if isinstance(operand, int):
                            return int(hypotenuse)
                        return hypotenuse
                    case tuple():
                        self_x_float = self._x % float()
                        self_y_float = self._y % float()
                        return (self_x_float, self_y_float)
                    case _:                     return super().__mod__(operand)
            case ra.Width():            return self._width.copy()
            case ra.Height():           return self._height.copy()
            case ra.dX():               return self._dx.copy()
            case ra.dY():               return self._dy.copy()
            case ra.X():                return self._x.copy()
            case ra.Y():                return self._y.copy()
            case int() | float() | tuple():
                                        return self % od.DataSource( operand )
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Bouncer') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._x == other._x and self._y == other._y
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["width"]        = self.serialize( self._width )
        serialization["parameters"]["height"]       = self.serialize( self._height )
        serialization["parameters"]["dx"]           = self.serialize( self._dx )
        serialization["parameters"]["dy"]           = self.serialize( self._dy )
        serialization["parameters"]["x"]            = self.serialize( self._x )
        serialization["parameters"]["y"]            = self.serialize( self._y )
        serialization["parameters"]["set_xy"]       = self.serialize( self._set_xy )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Modulus':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "width" in serialization["parameters"] and "height" in serialization["parameters"] and "dx" in serialization["parameters"] and
            "dy" in serialization["parameters"] and "x" in serialization["parameters"] and "y" in serialization["parameters"] and
            "set_xy" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._width             = self.deserialize( serialization["parameters"]["width"] )
            self._height            = self.deserialize( serialization["parameters"]["height"] )
            self._dx                = self.deserialize( serialization["parameters"]["dx"] )
            self._dy                = self.deserialize( serialization["parameters"]["dy"] )
            self._x                 = self.deserialize( serialization["parameters"]["x"] )
            self._y                 = self.deserialize( serialization["parameters"]["y"] )
            self._set_xy            = tuple(self.deserialize( serialization["parameters"]["set_xy"] ))
        return self
        
    def __lshift__(self, operand: any) -> TypeChaos:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Bouncer():
                super().__lshift__(operand)
                self._width         << operand._width
                self._height        << operand._height
                self._dx            << operand._dx
                self._dy            << operand._dy
                self._x             << operand._x
                self._y             << operand._y
                set_x               = operand._set_xy[0].copy()
                set_y               = operand._set_xy[1].copy()
                self._set_xy        = (set_x, set_y)
            case od.DataSource():
                match operand._data:
                    case ra.Width():                self._width = operand._data
                    case ra.Height():               self._height = operand._data
                    case ra.dX():                   self._dx = operand._data
                    case ra.dY():                   self._dy = operand._data
                    case ra.X():                    self._x = operand._data
                    case ra.Y():                    self._y = operand._data
                    case _:                         super().__lshift__(operand)
            case ra.Width():                self._width << operand
            case ra.Height():               self._height << operand
            case ra.dX():                   self._dx << operand
            case ra.dY():                   self._dy << operand
            case ra.X():                    self._x << operand
            case ra.Y():                    self._y << operand
            case _: super().__lshift__(operand)
        self._x << (self._x % float()) % (self._width % float())
        self._y << (self._y % float()) % (self._height % float())
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Bouncer':
        muted_iterations, total_iterations = self.muted_and_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(1, total_iterations + 1):
                for direction_data in [(self._x, self._dx, self._width), (self._y, self._dy, self._height)]:
                    new_position = direction_data[0] + direction_data[1]
                    if new_position < 0:
                        direction_data[1] << direction_data[1] * -1 # flips direction
                        new_position = new_position * -1 % direction_data[2]
                    elif new_position >= direction_data[2]:
                        direction_data[1] << direction_data[1] * -1 # flips direction
                        new_position = direction_data[2] - new_position % direction_data[2]
                    direction_data[0] << new_position
                if actual_iteration % muted_iterations == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self

    def __str__(self) -> str:
        return f'{self._index + 1}: {self % tuple()}'
    
    def reset(self, *parameters) -> 'Bouncer':
        super().reset(*parameters)
        self._x         << self._set_xy[0]
        self._y         << self._set_xy[1]
        return self

class SinX(Chaos):
    def __init__(self, *parameters):
        super().__init__()
        self._xn                        << 2
        self._x0                        << self._xn
        self._lambda: ra.Lambda         = ra.Lambda(77.238537) # Can't be an integer in order to be truly chaotic !!
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case ra.Lambda():           return self._lambda
                    case _:                     return super().__mod__(operand)
            case ra.Lambda():           return self._lambda.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'SinX') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if super().__eq__(other):
            return  self._lambda == other % od.DataSource( ra.Lambda() )
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
        
    def __lshift__(self, operand: any) -> TypeChaos:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case SinX():
                super().__lshift__(operand)
                self._lambda            << operand._lambda
            case od.DataSource():
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

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'SinX':
        muted_iterations, total_iterations = self.muted_and_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(1, total_iterations + 1):
                self._xn << self._xn % float() + self._lambda % float() * math.sin(self._xn % float())
                if actual_iteration % muted_iterations == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self
