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


class Mutation(o.Operand):
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
        self._result: od.Result         = od.Result(self._sequence)
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
            case Mutation():         return self.copy()
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

    def __eq__(self, other: 'Mutation') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._result == other._result
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["sequence"]         = self.serialize(self._sequence)
        serialization["parameters"]["frame"]            = self.serialize(self._frame)
        serialization["parameters"]["reporters_tuple"]  = self.serialize(self._reporters)
        serialization["parameters"]["operator"]         = self.serialize(self._operator)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Mutation':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "sequence" in serialization["parameters"] and "frame" in serialization["parameters"] and "reporters_tuple" in serialization["parameters"] and
            "operator" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._sequence          = self.deserialize(serialization["parameters"]["sequence"])
            self._frame             = self.deserialize(serialization["parameters"]["frame"])
            self._reporters         = self.deserialize(serialization["parameters"]["reporters_tuple"])
            self._operator          = self.deserialize(serialization["parameters"]["operator"])
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Mutation':
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
            case Mutation():
                        super().__lshift__(operand)
                        self._sequence      = operand._sequence.copy()
                        self._result        = operand._result.copy()
                        self._frame         = operand._frame.copy()
                        self._reporters     = operand._reporters.copy()
                        self._operator      = operand._operator # The string str()
            case od.Reporters():            self._reporters << operand
            case of.Frame():                self._frame = operand.copy()
            case oc.Sequence():
                                            self._sequence  = operand.copy()
                                            self._result    << self._sequence
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

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Mutation':
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

    def report(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Mutation':
        if not isinstance(number, (int, ou.Unit)):  # Report only when floats are used
            print(f'{type(self).__name__} {self._index + 1}', end = " ")
            if isinstance(self._reporters._data, tuple):
                for single_reporters in self._reporters._data:
                    self._result._data >> single_reporters
            else:
                self._result._data >> self._reporters._data
            print()
        return self

    def reset(self, *parameters) -> 'Mutation':
        super().reset(*parameters)
        self._sequence.reset()
        self._frame.reset()
        self._reporters._data.reset()
        self._result << self._sequence
        return self

class Translocation(Mutation):
    def __init__(self, *parameters):
        super().__init__()
        self._chaos: ch.Chaos           = ch.SinX()
        self._filter: ol.Filter         = ol.Filter(of.All())
        self._parameters: od.Parameters = od.Parameters(ot.Position(), ra.NoteValue())
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ch.Chaos():        return self._chaos
                    case ol.Filter():       return self._filter
                    case od.Parameters():   return self._parameters
                    case _:                 return super().__mod__(operand)
            case ch.Chaos():        return self._chaos.copy()
            case ol.Filter():       return self._filter.copy()
            case od.Parameters():   return self._parameters.copy()
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["chaos"]        = self.serialize(self._chaos)
        serialization["parameters"]["filter"]       = self.serialize(self._filter)
        serialization["parameters"]["parameters"]   = self.serialize(self._parameters)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Translocation':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "chaos" in serialization["parameters"] and "filter" in serialization["parameters"] and "parameters" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._chaos             = self.deserialize(serialization["parameters"]["chaos"])
            self._filter            = self.deserialize(serialization["parameters"]["filter"])
            self._parameters        = self.deserialize(serialization["parameters"]["parameters"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Translocation':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ch.Chaos():                self._chaos = operand % o.Operand()
                    case ol.Filter():               self._filter = operand % o.Operand()
                    case od.Parameters():           self._parameters = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Translocation():
                super().__lshift__(operand)
                self._chaos         << operand._chaos
                self._filter        << operand._filter
                self._parameters    << operand._parameters
            case ch.Chaos():                self._chaos << operand
            case ol.Filter():               self._filter << operand
            case od.Parameters():           self._parameters << operand
            case _:                         super().__lshift__(operand)
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Translocation':
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

    def reset(self, *parameters) -> 'Translocation':
        super().reset(*parameters)
        self._chaos.reset()
        self._filter.reset()
        return self

class TranslocateRhythm(Translocation):
    def __init__(self, *parameters):
        super().__init__()
        self._parameters        = od.Parameters(ot.Position())
        if len(parameters) > 0:
            self << parameters

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'TranslocateRhythm':
        super().__lshift__(operand)
        self._parameters        = od.Parameters(ot.Position())
        return self

class TranslocatePitch(Translocation):
    def __init__(self, *parameters):
        super().__init__()
        self._parameters        = od.Parameters(og.Pitch())
        if len(parameters) > 0:
            self << parameters

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'TranslocateRhythm':
        super().__lshift__(operand)
        self._parameters        = od.Parameters(og.Pitch())
        return self

class Crossover(Mutation):
    def __init__(self, *parameters):
        super().__init__()
        self._sequences: od.Sequences   = od.Sequences()
        self._chaos: ch.Chaos           = ch.SinX()
        self._filter: ol.Filter         = ol.Filter(of.All())
        self._parameters: od.Parameters = od.Parameters(oe.Note())
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Sequences():    return self._sequences
                    case ch.Chaos():        return self._chaos
                    case ol.Filter():       return self._filter
                    case od.Parameters():   return self._parameters
                    case _:                 return super().__mod__(operand)
            case od.Sequences():    return self._sequences.copy()
            case ch.Chaos():        return self._chaos.copy()
            case ol.Filter():       return self._filter.copy()
            case od.Parameters():   return self._parameters.copy()
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["sequences"]    = self.serialize(self._sequences)
        serialization["parameters"]["chaos"]        = self.serialize(self._chaos)
        serialization["parameters"]["filter"]       = self.serialize(self._filter)
        serialization["parameters"]["parameters"]   = self.serialize(self._parameters)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Crossover':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "sequences" in serialization["parameters"] and "chaos" in serialization["parameters"] and "filter" in serialization["parameters"] and "parameters" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._sequences         = self.deserialize(serialization["parameters"]["sequences"])
            self._chaos             = self.deserialize(serialization["parameters"]["chaos"])
            self._filter            = self.deserialize(serialization["parameters"]["filter"])
            self._parameters        = self.deserialize(serialization["parameters"]["parameters"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Crossover':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Sequences():            self._sequences = operand % o.Operand()
                    case ch.Chaos():                self._chaos = operand % o.Operand()
                    case ol.Filter():               self._filter = operand % o.Operand()
                    case od.Parameters():           self._parameters = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Crossover():
                super().__lshift__(operand)
                self._sequences     << operand._sequences
                self._chaos         << operand._chaos
                self._filter        << operand._filter
                self._parameters    << operand._parameters
            case od.Sequences():            self._sequences << operand
            case ch.Chaos():                self._chaos << operand
            case ol.Filter():               self._filter << operand
            case od.Parameters():           self._parameters << operand
            case _:                         super().__lshift__(operand)
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> 'Crossover':
        muted_iterations, total_iterations = self.muted_and_total_iterations(number)
        if total_iterations > 0:
            self._initiated = True
            result_sequence: oc.Sequence  = (self._result % od.DataSource()) % (self._filter % od.DataSource())
            source_len: int = result_sequence.len()
            for actual_iteration in range(1, total_iterations + 1):
                source_parameters: list[any] = []
                for _ in range(source_len):
                    for single_sequence in self._sequences._data:
                        if isinstance(single_sequence, oc.Sequence):
                            source_parameters.append(single_sequence % ou.Next()) # moves the index one step forward
                    source_parameter = source_parameters[self._chaos * 1 % int() % len(source_parameters)]
                    destination_parameter = result_sequence % ou.Next()
                    destination_parameter << source_parameter
                self._result % od.DataSource() >> ol.Link(True)
                if actual_iteration % muted_iterations == 0:
                    self.report(number)
                self._index += 1    # keeps track of each iteration
        return self

    def reset(self, *parameters) -> 'Crossover':
        super().reset()
        self._sequences.reset()
        self._chaos.reset()
        self._filter.reset()
        return self << parameters
