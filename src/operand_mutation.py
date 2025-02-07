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
from types import FunctionType
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
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
        self._chaos: ch.Chaos           = ch.SinX()
        self._parameter: type           = ra.Position
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def mutate(self, clip: oc.Clip) -> oc.Clip:
        return clip.shuffle(self._chaos, self._parameter)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case oc.Clip():         return operand._data.shuffle(self._chaos, self._parameter)
                    case ch.Chaos():        return self._chaos
                    case type():            return self._parameter
                    case _:                 return super().__mod__(operand)
            case oc.Clip():         return operand.copy().shuffle(self._chaos, self._parameter)
            case ch.Chaos():        return self._chaos.copy()
            case type():            return self._parameter
            case ra.Index():        return ra.Index(self._index)
            case ou.Next():         return self * operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, Mutation):
            return self._chaos == other._chaos and self._parameter == other._parameter
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["chaos"]            = self.serialize(self._chaos)
        serialization["parameters"]["parameter"]        = self._parameter.__name__
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "chaos" in serialization["parameters"] and "parameter" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._chaos             = self.deserialize(serialization["parameters"]["chaos"])
            parameter: type = o.find_class_by_name( o.Operand, serialization["parameters"]["parameter"] )
            if parameter:
                self._parameter     = parameter
            else:
                self._parameter     = ra.Position
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Mutation():
                super().__lshift__(operand)
                self._chaos         << operand._chaos
                self._parameter     = operand._parameter
            case od.DataSource():
                match operand._data:
                    case ch.Chaos():                self._chaos = operand._data
                    case type():                    self._parameter = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ch.Chaos():        self._chaos << operand
            case type():            self._parameter = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self
    
    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> Self:
        total_iterations = self.convert_to_int(number)
        if total_iterations > 0:
            self._initiated = True
            for _ in range(total_iterations):
                self._chaos * 1
                self._index += 1    # keeps track of each iteration
        return self

    def reset(self, *parameters) -> Self:
        super().reset(*parameters)
        self._chaos.reset()
        return self

class Translocation(Mutation):
    def __init__(self, *parameters):
        super().__init__()
        self._filter: od.Filter         = od.Filter(of.All())
        self._parameters: od.Parameters = od.Parameters(ra.Position())
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case od.Filter():       return self._filter
                    case od.Parameters():   return self._parameters
                    case _:                 return super().__mod__(operand)
            case od.Filter():       return self._filter.copy()
            case od.Parameters():   return self._parameters.copy()
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["filter"]       = self.serialize(self._filter)
        serialization["parameters"]["parameters"]   = self.serialize(self._parameters)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "filter" in serialization["parameters"] and "parameters" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._filter            = self.deserialize(serialization["parameters"]["filter"])
            self._parameters        = self.deserialize(serialization["parameters"]["parameters"])
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Translocation():
                super().__lshift__(operand)
                self._filter        << operand._filter
                self._parameters    << operand._parameters
            case od.DataSource():
                match operand._data:
                    case od.Filter():               self._filter = operand._data
                    case od.Parameters():           self._parameters = operand._data
                    case _:                         super().__lshift__(operand)
            case od.Filter():               self._filter << operand
            case od.Parameters():           self._parameters << operand
            case _:                         super().__lshift__(operand)
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> Self:
        total_iterations = self.convert_to_int(number)
        if total_iterations > 0:
            self._initiated = True
            source_result: oc.Clip  = self._result._data | self._filter._data   # Applies the filter
            jumbled_result: oc.Clip = source_result.copy()
            for _ in range(total_iterations):
                jumbled_result.shuffle(self._chaos) # a single shuffle
                for single_parameter in self._parameters._data: # A tuple of parameters
                    source_result << of.Foreach(jumbled_result)**of.Get(single_parameter)
                self._index += 1    # keeps track of each iteration
        return self

    def reset(self, *parameters) -> Self:
        super().reset(*parameters)
        self._filter.reset()
        return self

class TranslocateRhythm(Translocation):
    def __init__(self, *parameters):
        super().__init__()
        self._parameters        = od.Parameters(ra.NoteValue())
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        super().__lshift__(operand)
        self._parameters        = od.Parameters(ra.NoteValue())  # Can't change targeted parameter
        return self

class TranslocatePitch(Translocation):
    def __init__(self, *parameters):
        super().__init__()
        self._parameters        = od.Parameters(og.Pitch())
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        super().__lshift__(operand)
        self._parameters        = od.Parameters(og.Pitch())     # Can't change targeted parameter
        return self

class Crossover(Mutation):
    def __init__(self, *parameters):
        super().__init__()
        self._clips: od.Clips           = od.Clips()
        self._filter: od.Filter         = od.Filter(of.All())
        self._parameters: od.Parameters = od.Parameters(oe.Note())
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case od.Clips():        return self._clips
                    case od.Filter():       return self._filter
                    case od.Parameters():   return self._parameters
                    case _:                 return super().__mod__(operand)
            case od.Clips():        return self._clips.copy()
            case od.Filter():       return self._filter.copy()
            case od.Parameters():   return self._parameters.copy()
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["clips"]        = self.serialize(self._clips)
        serialization["parameters"]["filter"]       = self.serialize(self._filter)
        serialization["parameters"]["parameters"]   = self.serialize(self._parameters)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "clips" in serialization["parameters"] and "filter" in serialization["parameters"] and "parameters" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._clips             = self.deserialize(serialization["parameters"]["clips"])
            self._filter            = self.deserialize(serialization["parameters"]["filter"])
            self._parameters        = self.deserialize(serialization["parameters"]["parameters"])
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Crossover():
                super().__lshift__(operand)
                self._clips         << operand._clips
                self._filter        << operand._filter
                self._parameters    << operand._parameters
            case od.DataSource():
                match operand._data:
                    case od.Clips():                self._clips = operand._data
                    case od.Filter():               self._filter = operand._data
                    case od.Parameters():           self._parameters = operand._data
                    case _:                         super().__lshift__(operand)
            case od.Clips():                self._clips << operand
            case od.Filter():               self._filter << operand
            case od.Parameters():           self._parameters << operand
            case _:                         super().__lshift__(operand)
        return self

    def __mul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> Self:
        total_iterations = self.convert_to_int(number)
        if total_iterations > 0:
            self._initiated = True
            result_clip: oc.Clip  = (self._result % od.DataSource()) % (self._filter % od.DataSource())
            source_len: int = result_clip.len()
            for _ in range(total_iterations):
                source_parameters: list[any] = []
                for _ in range(source_len):
                    for single_clip in self._clips._data:
                        if isinstance(single_clip, oc.Clip):
                            source_parameters.append(single_clip % ou.Next()) # moves the index one step forward
                    source_parameter = source_parameters[self._chaos * 1 % int() % len(source_parameters)]
                    destination_parameter = result_clip % ou.Next()
                    destination_parameter << source_parameter
                self._index += 1    # keeps track of each iteration
        return self

    def reset(self, *parameters) -> Self:
        super().reset()
        self._clips.reset()
        self._filter.reset()
        return self << parameters
