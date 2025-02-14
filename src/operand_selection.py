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


class Selection(o.Operand):
    """`Selection`

    Selection allows the choice of given clips than have been mutated many times accordingly
    to a group of criteria.

    Parameters
    ----------
    first : any_like
        Any type of parameter can be used to set Selection.
    """
    # clip is the input >> (NO COPIES!) (PASSTHROUGH)
    def select(self, clip: o.T) -> o.T:
        if isinstance(clip, oc.Clip) and self != clip:
            clip._items = []
        return clip

    def __rrshift__(self, clip: o.T) -> o.T:
        return self.select(clip)


class IsNot(Selection):
    def __init__(self, *parameters):
        self._selection: Selection = None
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case Selection():       return self._selection
                    case _:                 return super().__mod__(operand)
            case Selection():       return self._selection
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, IsNot):
            return self._selection == other._selection
        if isinstance(other, oc.Clip):
            if isinstance(self._selection, Selection):
                return self._selection != other
            return True # IsNot None
        return not super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["selection"]          = self.serialize(self._selection)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "selection" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._selection           = self.deserialize(serialization["parameters"]["selection"])
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case IsNot():
                super().__lshift__(operand)
                self._selection     = self.deep_copy(operand._selection)   # Avoids None Type error
            case od.DataSource():
                match operand._data:
                    case Selection():           self._selection = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Selection():       self._selection = self.deep_copy(operand)   # Avoids None Type error
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


from typing import Dict, Iterable

class Mono(Selection):

    @staticmethod
    def is_overlapping(event: Dict[str, ra.Position], events: Iterable[ Dict[str, ra.Position] ]) -> bool:
        for single_event in events:
            if event["start"] < single_event["finish"] and event["finish"] > single_event["start"]:
                return True
        return False
    
    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, oc.Clip):
            events_filo: list[ Dict[str, ra.Position] ] = []
            for element in other:
                if isinstance(element, oe.Element):
                    event: Dict[str, ra.Position] = {
                        "start": element.start(),
                        "finish": element.finish()
                    }
                    if self.is_overlapping(event, events_filo):
                        return False
                    events_filo.insert(0, event)    # Faster with insert than append (FILO) (STACK)
            return True
        return super().__eq__(other)
    

class Condition(Selection):
    def __init__(self, *parameters):
        super().__init__()
        self._and: od.And               = od.And()
        self._or: od.Or                 = od.Or()
        and_parameters: list = [ 
            single_parameter for single_parameter in parameters \
            if not isinstance(single_parameter, (od.And, od.Or))
        ]
        if len(and_parameters) > 0:
            self._and = od.And( *tuple(and_parameters) )
        else:
            for single_operand in parameters:
                self << single_operand

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case od.And():          return self._and
                    case od.Or():           return self._or
                    case _:                 return super().__mod__(operand)
            case od.And():          return self.deep_copy(self._and)
            case od.Or():           return self._or.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, Condition):
            return self._and == other._and and self._or == other._or
        if isinstance(other, oc.Clip):
            return self._and == other and self._or == other
        return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["and"]          = self.serialize(self._and)
        serialization["parameters"]["or"]           = self.serialize(self._or)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "and" in serialization["parameters"] and "or" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._and           = self.deserialize(serialization["parameters"]["and"])
            self._or            = self.deserialize(serialization["parameters"]["or"])
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Condition():
                super().__lshift__(operand)
                self._and           << operand._and
                self._or            << operand._or
            case od.DataSource():
                match operand._data:
                    case od.And():              self._and = operand._data
                    case od.Or():               self._or = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case od.And():          self._and << operand
            case od.Or():           self._or << operand
            case tuple():
                and_parameters: list = [ 
                    single_parameter for single_parameter in operand \
                    if not isinstance(single_parameter, (od.And, od.Or))
                ]
                if len(and_parameters) > 0:
                    self._and = od.And( *tuple(and_parameters) )
                else:
                    for single_operand in operand:
                        self << single_operand
        return self


class Comparison(Selection):
    def __init__(self, *parameters):
        self._parameter: type = ra.Length
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case type():            return self._parameter
                    case _:                 return super().__mod__(operand)
            case type():            return self._parameter
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, Comparison):
            return self._parameter == other._parameter
        return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["parameter"]        = self._parameter.__name__
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "parameter" in serialization["parameters"]):

            super().loadSerialization(serialization)
            parameter: type = o.find_class_by_name( o.Operand, serialization["parameters"]["parameter"] )
            if parameter:
                self._parameter     = parameter
            else:
                self._parameter     = ra.Length
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Comparison():
                super().__lshift__(operand)
                self._parameter = operand._parameter
            case od.DataSource():
                match operand._data:
                    case type():                    self._parameter = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case type():            self._parameter = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self
    
class Matching(Comparison):

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, oc.Clip):
            parameter_instantiation = self._parameter()
            for element_index in range(other.len() - 1):
                if other[element_index] % parameter_instantiation != other[element_index + 1] % parameter_instantiation:
                    return False
            return True
        return super().__eq__(other)

class Ascending(Comparison):

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, oc.Clip):
            parameter_instantiation = self._parameter()
            for element_index in range(other.len() - 1):
                if other[element_index] % parameter_instantiation > other[element_index + 1] % parameter_instantiation:
                    return False
            return True
        return super().__eq__(other)
    
class Descending(Comparison):

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, oc.Clip):
            parameter_instantiation = self._parameter()
            for element_index in range(other.len() - 1):
                if other[element_index] % parameter_instantiation < other[element_index + 1] % parameter_instantiation:
                    return False
            return True
        return super().__eq__(other)

class Pattern(Comparison):
    def __init__(self, *parameters):
        self._pattern: list = []
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case list():            return self._pattern
                    case _:                 return super().__mod__(operand)
            case list():            return self._pattern
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, oc.Clip):
            if len(self._parameter) > 0:
                parameter_instantiation = self._parameter()
                for element_index in range(other.len() - 1):
                    if other[element_index + 1] % parameter_instantiation - other[element_index] % parameter_instantiation \
                        != self._pattern[element_index % len(self._parameter)]:
                        return False
            return True
        return super().__eq__(other)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pattern"]    = self.serialize(self._pattern)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pattern" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pattern     = self.deserialize(serialization["parameters"]["pattern"])
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pattern():
                super().__lshift__(operand)
                self._pattern = operand._pattern
            case od.DataSource():
                match operand._data:
                    case list():                    self._pattern = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():            self._pattern = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

class UpDown(Pattern):
    
    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, oc.Clip):
            if len(self._parameter) > 0:
                parameter_instantiation = self._parameter()
                for element_index in range(other.len() - 1):
                    if self._pattern[element_index % len(self._parameter)] > 0:
                        if not other[element_index + 1] % parameter_instantiation > other[element_index] % parameter_instantiation:
                            return False
                    elif self._pattern[element_index % len(self._parameter)] < 0:
                        if not other[element_index + 1] % parameter_instantiation < other[element_index] % parameter_instantiation:
                            return False
                    else:
                        if other[element_index + 1] % parameter_instantiation != other[element_index] % parameter_instantiation:
                            return False
            return True
        return super().__eq__(other)


class Threshold(Selection):
    def __init__(self, *parameters):
        self._threshold: int = 5
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case int():            return self._threshold
                    case _:                 return super().__mod__(operand)
            case int():            return self._threshold
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["threshold"]    = self.serialize(self._threshold)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "threshold" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._threshold     = self.deserialize(serialization["parameters"]["threshold"])
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Threshold():
                super().__lshift__(operand)
                self._threshold = operand._threshold
            case od.DataSource():
                match operand._data:
                    case int():                    self._threshold = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case int():            self._threshold = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

class First(Threshold):

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if self._threshold > 0:
            if isinstance(other, oc.Clip) and other.len() > 0:
                self._threshold -= 1
            return True
        return super().__eq__(other)

class After(Threshold):

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if self._threshold > 0 and isinstance(other, oc.Clip):
            if other.len() > 0:
                self._threshold -= 1
            return False
        return super().__eq__(other)
    
class Most(Threshold):
    def __init__(self, *parameters):
        super().__init__()
        self._threshold = 16
        for single_operand in parameters:
            self << single_operand

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, oc.Clip) and other.len() > self._threshold:
            return False
        return super().__eq__(other)
    
class Least(Threshold):
    def __init__(self, *parameters):
        super().__init__()
        self._threshold = 4
        for single_operand in parameters:
            self << single_operand

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, oc.Clip) and other.len() < self._threshold:
            return False
        return super().__eq__(other)

