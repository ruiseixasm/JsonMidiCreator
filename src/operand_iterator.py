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
from typing import Union, TYPE_CHECKING, Callable
from fractions import Fraction
import json
import enum
import math
from types import FunctionType
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
        self._subject: o.Operand        = ol.Null()
        self._frame: of.Frame           = of.Frame()
        self._reporter: od.Reporter     = od.Reporter(of.PushTo(ol.Play()))
        # self._operator: Callable[[o.Operand, of.Frame], o.Operand] \
        #                                 = lambda subject, frame: subject << frame
        self._operator: str             = "<<"
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Reporter():     return self._reporter
                    case of.Frame():        return self._frame
                    case o.Operand():       return self._subject
                    case str():             return self._operator
                    case _:                 return ol.Null()
            case Iterator():        return self.copy()
            case od.Reporter():     return self._reporter.copy()
            case of.Frame():        return self._frame.copy()
            case o.Operand():       return self._subject.copy()
            # case FunctionType() if op.__name__ == "<lambda>":
            #                         return self._operator
            # case FunctionType():    return self._operator
            case str():             return self._operator
            case ou.Next():         return self * operand
            case _:                 return super().__mod__(operand)

    # def __eq__(self, other: 'Iterator') -> bool:
    #     other = self & other    # Processes the tailed self operands or the Frame operand if any exists
    #     if other.__class__ == o.Operand:
    #         return True
    #     if type(self) != type(other):
    #         return False
    #     return  self._x == other._x and self._y == other._y
    
    def getSerialization(self) -> dict:
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "subject":          self._subject.getSerialization(),
                "frame":            self._frame.getSerialization(),
                "reporter":         self._reporter.getSerialization(),
                "operator":         self._operator
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Iterator':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "subject" in serialization["parameters"] and "frame" in serialization["parameters"] and "reporter" in serialization["parameters"] and
            "operator" in serialization["parameters"]):

            self._subject           = o.Operand().loadSerialization(serialization["parameters"]["subject"])
            self._frame             = of.Frame().loadSerialization(serialization["parameters"]["frame"])
            self._reporter          = od.Reporter().loadSerialization(serialization["parameters"]["reporter"])
            self._operator          = serialization["parameters"]["operator"]
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Iterator':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Reporter():             self._reporter = operand % o.Operand()
                    case of.Frame():                self._frame = operand % o.Operand()
                    case o.Operand():               self._subject = operand % o.Operand()
                    case str():                     self._operator = operand % o.Operand()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Iterator():
                        self._subject       = operand._subject.copy()
                        self._frame         = operand._frame.copy()
                        self._reporter      << operand._reporter
            case od.Reporter():             self._reporter << operand
            case of.Frame():                self._frame = operand.copy()
            case o.Operand():               self._subject = operand.copy()
            # case FunctionType() if f.__name__ == "<lambda>":
            #                                 self._operator = operand
            # case FunctionType():            self._operator = operand
            case str():                     self._operator = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ro.Rational) -> 'Iterator':
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        iterations: int = 1
        match number:
            case ou.Unit() | ro.Rational():
                iterations = number % int()
            case int() | float() | Fraction():
                iterations = int(number)
        if not self._initiated:
            self._initiated = True
        if iterations > 0:
            for _ in range(iterations):
                # result: o.Operand = self._operator(self._subject, self._frame)
                match self._operator:
                    case "^":   result: o.Operand = self._subject ^ self._frame
                    case ">>":  result: o.Operand = self._subject >> self._frame
                    case "+":   result: o.Operand = self._subject + self._frame
                    case "-":   result: o.Operand = self._subject - self._frame
                    case "*":   result: o.Operand = self._subject * self._frame
                    case "%":   result: o.Operand = self._subject % self._frame
                    case "/":   result: o.Operand = self._subject / self._frame
                    case "//":  result: o.Operand = self._subject // self._frame
                    case _:     result: o.Operand = self._subject << self._frame
                result >> self._reporter._data
        return self
