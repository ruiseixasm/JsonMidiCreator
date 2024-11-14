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
import operand_rational as ra
import operand_time as ot
import operand_data as od
import operand_label as ol
import operand_generic as og
import operand_element as oe
import operand_frame as of
import operand_container as oc
import operand_chaos as ch


class Jumbler(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        self._operand: o.Operand        = oe.Note() * 4
        self._frame: of.Frame           = of.Foreach(ch.Modulus(ra.Amplitude(23), ra.Step(101)))**of.Pick(1, 2, 3, 4, 5, 6, 7)**ou.Degree()
        self._reporter: od.Reporter     = od.Reporter(
                of.Get(ra.Index(), int())**of.Add(1)**of.PushTo(ol.Print()), 
                of.Get(o.Operand())**of.PushTo(ol.Play()),
                of.Subject(oe.Rest())**of.PushTo(ol.Play())
            )
        # self._operator: Callable[[o.Operand, of.Frame], o.Operand] \
        #                                 = lambda operand, frame: operand << frame
        self._operator: str             = "<<"
        self._result: od.Result         = od.Result(self._operand.copy())
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Reporter():     return self._reporter
                    case of.Frame():        return self._frame
                    case o.Operand():       return self._operand
                    case str():             return self._operator
                    case od.Result():       return self._result
                    case _:                 return ol.Null()
            case Jumbler():         return self.copy()
            case od.Reporter():     return self._reporter.copy()
            case of.Frame():        return self._frame.copy()
            case ra.Index():        return ra.Index(self._index)
            case o.Operand():       return self._operand.copy()
            # case FunctionType() if op.__name__ == "<lambda>":
            #                         return self._operator
            # case FunctionType():    return self._operator
            case str():             return self._operator
            case od.Result():       return self._result._data
            case ou.Next():         return self * operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: 'Jumbler') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._result == other._result
    
    def getSerialization(self) -> dict:
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "operand":          self._operand.getSerialization(),
                "frame":            self._frame.getSerialization(),
                "reporter":         self._reporter.getSerialization(),
                "operator":         self._operator
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Jumbler':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "operand" in serialization["parameters"] and "frame" in serialization["parameters"] and "reporter" in serialization["parameters"] and
            "operator" in serialization["parameters"]):

            self._operand           = o.Operand().loadSerialization(serialization["parameters"]["operand"])
            self._frame             = o.Operand().loadSerialization(serialization["parameters"]["frame"])
            self._reporter          = od.Reporter().loadSerialization(serialization["parameters"]["reporter"])
            self._operator          = serialization["parameters"]["operator"]
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Jumbler':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Reporter():             self._reporter = operand % o.Operand()
                    case of.Frame():                self._frame = operand % o.Operand()
                    case o.Operand():               self._operand = operand % o.Operand()
                    case str():                     self._operator = operand % o.Operand()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Jumbler():
                        self._operand       = operand._operand.copy()
                        self._frame         = operand._frame.copy()
                        self._reporter      << operand._reporter
            case od.Reporter():             self._reporter << operand
            case of.Frame():                self._frame = operand.copy()
            case o.Operand():               self._operand = operand.copy()
            # case FunctionType() if f.__name__ == "<lambda>":
            #                                 self._operator = operand
            # case FunctionType():            self._operator = operand
            case str():                     self._operator = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Jumbler':
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        iterations: int = 1
        match number:
            case ou.Unit() | ra.Rational():
                iterations = number % int()
            case int() | float() | Fraction():
                iterations = int(number)
        if not self._initiated:
            self._initiated = True
        if iterations > 0:
            for _ in range(iterations):
                operand: o.Operand  = self._operand
                frame: of.Frame     = self._frame
                match self._operator:
                    case "^":   result: o.Operand = operand ^ frame
                    case ">>":  result: o.Operand = operand >> frame
                    case "+":   result: o.Operand = operand + frame
                    case "-":   result: o.Operand = operand - frame
                    case "*":   result: o.Operand = operand * frame
                    case "%":   result: o.Operand = operand % frame
                    case "/":   result: o.Operand = operand / frame
                    case "//":  result: o.Operand = operand // frame
                    case _:     result: o.Operand = operand << frame
                self._result = od.Result(result)
                if isinstance(self._reporter._data, tuple):
                    for single_reporter in self._reporter._data:
                        self >> single_reporter
                else:
                    self >> self._reporter._data
                self._index += 1    # keeps track of each iteration
        return self

    def reset(self, *parameters) -> 'Jumbler':
        super().reset(parameters)
        self._operand.reset()
        self._frame.reset()
        self._reporter._data.reset()
        self._result = od.Result(self._operand.copy())
        return self
    
class JumbleRhythm(Jumbler):
    def __init__(self, *parameters):
        super().__init__()
        self._filter: od.Filter   = od.Filter(of.All())
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Filter():       return self._filter
                    case _:                 return ol.Null()
            case od.Filter():       return self._filter.copy()
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["filter"] = self._filter.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Jumbler':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "filter" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._operand           = od.Filter().loadSerialization(serialization["parameters"]["filter"])
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Jumbler':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Filter():               self._filter = operand % o.Operand()
            case JumbleRhythm():
                super().__lshift__(operand)
                self._filter << operand._filter
            case od.Filter():               self._filter << operand
            case od.Reporter():
                super().__lshift__(operand)
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Jumbler':
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        iterations: int = 1
        match number:
            case ou.Unit() | ra.Rational():
                iterations = number % int()
            case int() | float() | Fraction():
                iterations = int(number)
        if not self._initiated:
            self._initiated = True
        if iterations > 0:
            filtered_operand = self._operand % self._filter
            for _ in range(iterations):
                ...
                self._operand >> ol.Link(True)
                self._index += 1    # keeps track of each iteration
        return self

    def reset(self, *parameters) -> 'Jumbler':
        super().reset(parameters)
        self._filter.reset()
        return self
