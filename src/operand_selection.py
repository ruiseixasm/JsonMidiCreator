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
    pass


class Condition(Selection):
    def __init__(self, *parameters):
        self._and: od.And               = od.And()
        self._or: od.Or                 = od.Or()
        super().__init__(*parameters)

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
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, Selection):
            return self._and == other._and and self._or == other._or
        return self._and == other and self._or == other
    
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
            case Selection():
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
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, Comparison):
            return self._parameter == other._parameter
        return False
    
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


class Threshold(Selection):
    pass

# class First(Threshold):
#     pass