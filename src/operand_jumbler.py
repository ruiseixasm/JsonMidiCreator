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
        self._sequence: oc.Sequence     = oe.Note() * 4
        self._frame: of.Frame           = of.Foreach(ch.Modulus(ra.Amplitude(23), ra.Step(78)))**of.Pick(1, 2, 3, 4, 5, 6, 7)**ou.Degree()
        self._reporters: od.Reporters   = od.Reporters(
                of.PushTo(ol.Play()),
                of.Subject(oe.Rest())**of.PushTo(ol.Play()) # Finally plays a single Rest
            )
        # self._operator: Callable[[oc.Sequence, of.Frame], oc.Sequence] \
        #                                 = lambda sequence, frame: sequence << frame
        self._operator: str             = "<<"
        self._result: od.Result         = od.Result(self._sequence.copy())
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Reporters():    return self._reporters
                    case of.Frame():        return self._frame
                    case oc.Sequence():     return self._sequence
                    case str():             return self._operator
                    case od.Result():       return self._result
                    case _:                 return ol.Null()
            case Jumbler():         return self.copy()
            case od.Reporters():    return self._reporters.copy()
            case of.Frame():        return self._frame.copy()
            case ra.Index():        return ra.Index(self._index)
            case oc.Sequence():     return self._result._data.copy()
            # case FunctionType() if op.__name__ == "<lambda>":
            #                         return self._operator
            # case FunctionType():    return self._operator
            case str():             return self._operator
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
                "sequence":         self._sequence.getSerialization(),
                "frame":            self._frame.getSerialization(),
                "reporter":         self._reporters.getSerialization(),
                "operator":         self._operator
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Jumbler':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "sequence" in serialization["parameters"] and "frame" in serialization["parameters"] and "reporter" in serialization["parameters"] and
            "operator" in serialization["parameters"]):

            self._sequence          = o.Operand().loadSerialization(serialization["parameters"]["sequence"])
            self._frame             = o.Operand().loadSerialization(serialization["parameters"]["frame"])
            self._reporters         = od.Reporters().loadSerialization(serialization["parameters"]["reporter"])
            self._operator          = serialization["parameters"]["operator"]
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Jumbler':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Reporters():            self._reporters = operand % o.Operand()
                    case of.Frame():                self._frame = operand % o.Operand()
                    case oc.Sequence():             self._sequence = operand % o.Operand()
                    case str():                     self._operator = operand % o.Operand()
                    case od.Result():               self._result = operand % o.Operand()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Jumbler():
                        self._sequence      = operand._result._data.copy()
                        self._frame         = operand._frame.copy()
                        self._reporters     << operand._reporters
                        self._operator      = operand._operator # The string str()
                        self._result        = operand._result.copy()
            case od.Reporters():            self._reporters << operand
            case of.Frame():                self._frame = operand.copy()
            case oc.Sequence():
                                            self._sequence << operand
                                            self._result << od.DataSource( self._sequence.copy() )
            # case FunctionType() if f.__name__ == "<lambda>":
            #                                 self._operator = operand
            # case FunctionType():            self._operator = operand
            case str():                     self._operator = operand
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

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Jumbler':
        muted_iterations, total_iterations = self.muted_and_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            for actual_iteration in range(1, total_iterations + 1):
                match self._operator:
                    case "^":   self._result._data ^ self._frame
                    case ">>":  self._result._data >> self._frame
                    case "+":   self._result._data + self._frame
                    case "-":   self._result._data - self._frame
                    case "*":   self._result._data * self._frame
                    case "%":   self._result._data % self._frame
                    case "/":   self._result._data / self._frame
                    case "//":  self._result._data // self._frame
                    case _:     self._result._data << self._frame
                if actual_iteration % muted_iterations == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self

    def report(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Jumbler':
        if not isinstance(number, (int, ou.Unit)):  # Report only when floats are used
            print(f'{type(self).__name__} {self._index + 1}', end = " ")
            if isinstance(self._reporters._data, tuple):
                for single_reporters in self._reporters._data:
                    self._result._data >> single_reporters
            else:
                self._result._data >> self._reporters._data
            print()
        return self

    def reset(self, *parameters) -> 'Jumbler':
        super().reset(*parameters)
        self._sequence.reset()
        self._frame.reset()
        self._reporters._data.reset()
        self._result << od.DataSource( self._sequence.copy() )
        return self
    
class JumbleParameters(Jumbler):
    def __init__(self, *parameters):
        super().__init__()
        self._chaos: ch.Chaos           = ch.SinX()
        self._filter: od.Filter         = od.Filter(of.All())
        self._parameters: od.Parameters = od.Parameters(ot.Position(), ra.NoteValue())
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ch.Chaos():        return self._chaos
                    case od.Filter():       return self._filter
                    case od.Parameters():   return self._parameters
                    case _:                 return super().__mod__(operand)
            case ch.Chaos():        return self._chaos.copy()
            case od.Filter():       return self._filter.copy()
            case od.Parameters():   return self._parameters.copy()
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["chaos"]        = self._chaos.getSerialization()
        element_serialization["parameters"]["filter"]       = self._filter.getSerialization()
        element_serialization["parameters"]["parameters"]   = self._parameters.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'JumbleParameters':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "chaos" in serialization["parameters"] and "filter" in serialization["parameters"] and "parameters" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._chaos             = ch.Chaos().loadSerialization(serialization["parameters"]["chaos"])
            self._filter            = od.Filter().loadSerialization(serialization["parameters"]["filter"])
            self._parameters        = od.Parameters().loadSerialization(serialization["parameters"]["parameters"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'JumbleParameters':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ch.Chaos():                self._chaos = operand % o.Operand()
                    case od.Filter():               self._filter = operand % o.Operand()
                    case od.Parameters():           self._parameters = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case JumbleParameters():
                super().__lshift__(operand)
                self._chaos         << operand._chaos
                self._filter        << operand._filter
                self._parameters    << operand._parameters
            case ch.Chaos():                self._chaos << operand
            case od.Filter():               self._filter << operand
            case _:                         super().__lshift__(operand)
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'JumbleParameters':
        muted_iterations, total_iterations = self.muted_and_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            source_result: oc.Sequence  = (self._result % od.DataSource()) % (self._filter % od.DataSource())
            jumbled_result: oc.Sequence = source_result.copy()
            for actual_iteration in range(1, total_iterations + 1):
                jumbled_result.shuffle(self._chaos) # a single shuffle
                for single_parameter in self._parameters._data:
                    source_result << of.Foreach(jumbled_result)**of.Get(single_parameter)
                self._result % od.DataSource() >> ol.Link(True)
                if actual_iteration % muted_iterations == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self

    def reset(self, *parameters) -> 'JumbleParameters':
        super().reset(*parameters)
        self._chaos.reset()
        self._filter.reset()
        return self

class JumbleRhythm(JumbleParameters):
    def __init__(self, *parameters):
        super().__init__()
        self._parameters        = od.Parameters(ot.Position())
        if len(parameters) > 0:
            self << parameters

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'JumbleRhythm':
        super().__lshift__(operand)
        self._parameters        = od.Parameters(ot.Position())
        return self

class JumblePitch(JumbleParameters):
    def __init__(self, *parameters):
        super().__init__()
        self._parameters        = od.Parameters(og.Pitch())
        if len(parameters) > 0:
            self << parameters

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'JumbleRhythm':
        super().__lshift__(operand)
        self._parameters        = od.Parameters(og.Pitch())
        return self
