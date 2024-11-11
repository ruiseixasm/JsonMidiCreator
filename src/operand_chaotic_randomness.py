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


class ChaoticRandomness(o.Operand):
    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'ChaoticRandomness':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

class Modulus(ChaoticRandomness):
    def __init__(self, *parameters):
        super().__init__()
        self._amplitude: ro.Amplitude   = ro.Amplitude(12)
        self._step: ro.Step             = ro.Step(1)
        self._index: ro.Index           = ro.Index(0)
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.Amplitude():        return self._amplitude
                    case ro.Step():             return self._step
                    case ro.Index():            return self._index
                    case _:                     return super().__mod__(operand)
            case Modulus():             return self.copy()
            case ro.Amplitude():        return self._amplitude.copy()
            case ro.Step():             return self._step.copy()
            case ro.Index():            return self._index.copy()
            case int() | float():
                self_index = self._index % operand
                self * 1    # Iterate one time
                return self_index
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Modulus') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._index           == other._index
    
    def getSerialization(self) -> dict:
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "amplitude":    self._amplitude % float(),
                "step":         self._step % float(),
                "index":        self._index % float()
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Modulus':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "amplitude" in serialization["parameters"] and "step" in serialization["parameters"] and "index" in serialization["parameters"]):

            self._amplitude         << serialization["parameters"]["amplitude"]
            self._step              << serialization["parameters"]["step"]
            self._index             << serialization["parameters"]["index"]
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Modulus':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.Amplitude():            self._amplitude = operand % o.Operand()
                    case ro.Step():                 self._step = operand % o.Operand()
                    case ro.Index():                self._index = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Modulus():
                        self._amplitude     << operand._amplitude
                        self._step          << operand._step
                        self._index         << operand._index
            case ro.Amplitude():            self._amplitude << operand
            case ro.Step():                 self._step << operand
            case ro.Index():
                self._index << operand
                if self._index >= self._amplitude:
                    self._index << (self._index % int()) % (self._amplitude % int())
            case int() | float():
                self._index << operand
                if self._index >= self._amplitude:
                    self._index << (self._index % int()) % (self._amplitude % int())
            case _: super().__lshift__(operand)
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ro.Rational) -> 'Modulus':
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        iterations: int = 1
        match number:
            case ou.Unit() | ro.Rational():
                iterations = number % int()
            case int() | float() | Fraction():
                iterations = round(number)
        if iterations > 0:
            for _ in range(iterations):
                self._index += self._step
                self._index << (self._index % int()) % (self._amplitude % int())
        return self

class Flipper(Modulus):
    def __init__(self, *parameters):
        super().__init__()
        self._amplitude: ro.Amplitude   = ro.Amplitude(2)
        self._step: ro.Step             = ro.Step(1)
        self._index: ro.Index           = ro.Index(0)
        self._split: ro.Split           = ro.Split(1)
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.Split():            return self._split
                    case _:                     return super().__mod__(operand)
            case Flipper():             return self.copy()
            case ro.Split():            return self._split.copy()
            case int():                 return -1 if super().__mod__(int()) < self._split % int() else +1
            case float():               return -1.0 if super().__mod__(float()) < self._split % float() else +1.0
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Modulus') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self % int()        == other % int()
    
    def getSerialization(self) -> dict:
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["split"]    = self._split % od.DataSource( float() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "split" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._split = ro.Split()    << od.DataSource( serialization["parameters"]["split"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Modulus':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.Split():                self._split = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Flipper():
                        super().__lshift__(operand)
                        self._split         << operand._split
            case ro.Split():                self._split << operand
            case _: super().__lshift__(operand)
        return self

class Bouncer(ChaoticRandomness):
    ...
