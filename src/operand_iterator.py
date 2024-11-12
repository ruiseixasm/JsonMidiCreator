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
from typing import Union
from fractions import Fraction
import json
import enum
from typing import TYPE_CHECKING
import math
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ro
import operand_time as ot
import operand_data as od
import operand_label as ol
import operand_generic as og
import operand_frame as of
import operand_container as oc
import operand_chaotic_randomizer as ocr


class Iterator(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Iterator():
                                    return self.copy()
            case ou.Next():         return self * operand
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Iterator':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ro.Rational) -> 'Looper':
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        return self

class Looper(Iterator):
    def __init__(self, *parameters):
        super().__init__()
        self._width: ro.Width           = ro.Width(16)
        self._height: ro.Height         = ro.Height(9)
        self._dx: ro.dX                 = ro.dX(0.555)
        self._dy: ro.dY                 = ro.dY(0.555)
        self._x: ro.X                   = ro.X(8.0)
        self._y: ro.Y                   = ro.Y(4.5)
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.Width():            return self._width
                    case ro.Height():           return self._height
                    case ro.dX():               return self._dx
                    case ro.dY():               return self._dy
                    case ro.X():                return self._x
                    case ro.Y():                return self._y
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
            case ro.Width():            return self._width.copy()
            case ro.Height():           return self._height.copy()
            case ro.dX():               return self._dx.copy()
            case ro.dY():               return self._dy.copy()
            case ro.X():
                self_x = self._x.copy()
                # self * 1    # Iterate one time
                return self_x
            case ro.Y():
                self_y = self._y.copy()
                # self * 1    # Iterate one time
                return self_y
            case int() | float():
                hypotenuse = self % od.DataSource( operand )
                # self * 1    # Iterate one time
                return hypotenuse
            case tuple():
                self_tuple = self % od.DataSource( tuple() )
                # self * 1    # Iterate one time
                return self_tuple
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Looper') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._x == other._x and self._y == other._y
    
    def getSerialization(self) -> dict:
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "width":        self._width % float(),
                "height":       self._height % float(),
                "dx":           self._dx % float(),
                "dy":           self._dy % float(),
                "x":            self._x % float(),
                "y":            self._y % float()
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Looper':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "width" in serialization["parameters"] and "height" in serialization["parameters"] and "dx" in serialization["parameters"] and
            "dy" in serialization["parameters"] and "x" in serialization["parameters"] and "y" in serialization["parameters"]):

            self._width             << serialization["parameters"]["width"]
            self._height            << serialization["parameters"]["height"]
            self._dx                << serialization["parameters"]["dx"]
            self._dy                << serialization["parameters"]["dy"]
            self._x                 << serialization["parameters"]["x"]
            self._y                 << serialization["parameters"]["y"]
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Looper':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.Width():                self._width = operand % o.Operand()
                    case ro.Height():               self._height = operand % o.Operand()
                    case ro.dX():                   self._dx = operand % o.Operand()
                    case ro.dY():                   self._dy = operand % o.Operand()
                    case ro.X():                    self._x = operand % o.Operand()
                    case ro.Y():                    self._y = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Looper():
                        self._width         << operand._width
                        self._height        << operand._height
                        self._dx            << operand._dx
                        self._dy            << operand._dy
                        self._x             << operand._x
                        self._y             << operand._y
            case ro.Width():                self._width << operand
            case ro.Height():               self._height << operand
            case ro.dX():                   self._dx << operand
            case ro.dY():                   self._dy << operand
            case ro.X():                    self._x << operand
            case ro.Y():                    self._y << operand
            case _: super().__lshift__(operand)
        self._x << (self._x % float()) % (self._width % float())
        self._y << (self._y % float()) % (self._height % float())
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ro.Rational) -> 'Looper':
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        iterations: int = 1
        match number:
            case ou.Unit() | ro.Rational():
                iterations = number % int()
            case int() | float() | Fraction():
                iterations = int(number)
        if not self._initiated:
            self._initiated = True
            iterations -= 1
        if iterations > 0:
            for _ in range(iterations):
                for direction_data in [(self._x, self._dx, self._width), (self._y, self._dy, self._height)]:
                    new_position = direction_data[0] + direction_data[1]
                    if new_position < 0:
                        direction_data[1] << direction_data[1] * -1 # flips direction
                        new_position = new_position * -1 % direction_data[2]
                    elif new_position >= direction_data[2]:
                        direction_data[1] << direction_data[1] * -1 # flips direction
                        new_position = direction_data[2] - new_position % direction_data[2]
                    direction_data[0] << new_position
        return self

