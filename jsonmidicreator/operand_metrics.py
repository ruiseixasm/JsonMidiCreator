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
# Json Midi Creator Libraries
from . import creator as c
from . import operand as o

from . import operand_label as ol
from . import operand_data as od
from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_generic as og
from . import operand_element as oe
from . import operand_container as oc
from . import operand_frame as of
from . import operand_chaos as ch
from . import operand_tamer as ot

if TYPE_CHECKING:
    from operand_element import Element
    from operand_container import Composition


class Metrics(o.Operand):
    """`Metrics`

    `Metrics` represent quantized information of multiple or single `Element` and `Composition` operands.
    """
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case int():
                return 0
            case str():
                return str(self % int())
            case _:
                return super().__mod__(operand)
            

class Vector(Metrics):
    """`Metrics -> Vector`

    A `Vector` is a multidimensional representation of a given `Element`.
    
    Parameters
    ----------
    dict({}) : The vector with the multiple dimensions concerning the `Element`.
    """
    def __init__(self, *parameters):
        self._vectordict: dict[str, int] = {}
        super().__init__(*parameters)

    def len(self) -> int:
        return len(self._vectordict)

    def get_keys(self) -> set:
        keys: set[str] = set()
        for v_key in self._vectordict.keys():
            keys.add(v_key)
        return keys

    def distance(self, keys: set = set()) -> int:
        distance_int = 0
        for v_key, v_value in self._vectordict.items():
            if len(keys) == 0 or v_key in keys:
                distance_int += abs(v_value)
        return distance_int
    
    def variations(self, keys: set = set()) -> int:
        variation_int = 0
        for v_key, v_value in self._vectordict.items():
            if len(keys) == 0 or v_key in keys:
                if v_value != 0: variation_int += 1
        return variation_int


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case dict():
                        return self._vectordict
                    case _:
                        return super().__mod__(operand)
            case dict():
                return self._vectordict.copy()
            case int():
                return self.distance()
            case ou.Distance():
                return operand << self.distance(operand._keys)
            case ou.Variations():
                return operand << self.variations(operand._keys)
            case set():
                return self.get_keys()
            case _:
                return super().__mod__(operand)
            
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["vectordict"] = self.serialize( self._vectordict )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "vectordict" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._vectordict = self.deserialize( serialization["parameters"]["vectordict"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Vector():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._vectordict = operand._vectordict.copy()
            case od.Pipe():
                match operand._data:
                    case dict():
                        self._vectordict = operand._data
                    case _:
                        super().__lshift__(operand)
            case dict():
                self._vectordict = operand.copy()
            case oe.Element():
                self._vectordict = operand.getVectordict()
            case _:
                super().__lshift__(operand)
        return self


    def __add__(self, other: 'Vector') -> Self:
        vector1 = self._vectordict
        vector2 = other._vectordict
        vector3 = {}
        for v_key, v_value1 in vector1.items():
            if v_key in vector2:
                vector3[v_key] = v_value1 + vector2[v_key]
        return Vector() << od.Pipe(vector3)

    def __sub__(self, other: 'Vector') -> Self:
        vector1 = self._vectordict
        vector2 = other._vectordict
        vector3 = {}
        for v_key, v_value1 in vector1.items():
            if v_key in vector2:
                vector3[v_key] = v_value1 - vector2[v_key]
        return Vector() << od.Pipe(vector3)

    def reset(self, *parameters) -> Self:
        self._vectordict = {}
        return super().reset(*parameters)


class Vectors(Metrics):
    """`Metrics -> Vectors`

    `Vectors` concern exclusively a `Clip`, while `Vector` concern elements.
    
    Parameters
    ----------
    list([]) : A list of `Vector` operands.
    """
    def __init__(self, *parameters):
        self._vectors: list[Vector] = []
        super().__init__(*parameters)

    def len(self) -> int:
        return len(self._vectors)

    def get_keys(self) -> set:
        keys: set[str] = set()
        for vector in self._vectors:
            keys.update(vector.get_keys())
        return keys

    def distance(self, keys: set = set()) -> int:
        distance_int = 0
        for vector in self._vectors:
            distance_int += vector.distance(keys)
        return distance_int

    def variations(self, keys: set = set()) -> int:
        variation_int = 0
        for vector in self._vectors:
            variation_int += vector.variations(keys)
        return variation_int

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():
                        return self._vectors
                    case _:
                        return super().__mod__(operand)
            case list():
                return o.Operand.deep_copy(self._vectors)
            case int():
                return self.distance()
            case ou.Distance():
                return operand << self.distance(operand._keys)
            case ou.Variations():
                return operand << self.variations(operand._keys)
            case set():
                return self.get_keys()
            case _:
                return super().__mod__(operand)
            
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["vectors"] = self.serialize( self._vectors )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "vectors" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._vectors = self.deserialize( serialization["parameters"]["vectors"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Vectors():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._vectors = o.Operand.deep_copy(operand._vectors)
            case od.Pipe():
                match operand._data:
                    case list():
                        self._vectors = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                self._vectors = o.Operand.deep_copy(operand)
            case oc.Clip():
                self._vectors = operand.getVectorslist()
            case _:
                super().__lshift__(operand)
        return self


    def __add__(self, other: 'Vectors') -> Self:
        vectors1 = self._vectors
        vectors2 = other._vectors
        vectors3: list[Vector] = []
        for vector1, vector2 in zip(vectors1, vectors2):
            vectors3.append(vector1 + vector2)
        if self.len() > other.len():
            for index in range(other.len(), self.len()):
                exceeding_vector: Vector = self._vectors[index].copy()
                exceeding_vector << {"new": +1}
                vectors3.append(exceeding_vector)
        elif self.len() < other.len():
            for index in range(self.len(), other.len()):
                missing_vector: Vector = other._vectors[index].copy()
                missing_vector << {"new": +1}
                vectors3.append(missing_vector)
        return Vectors() << od.Pipe(vectors3)

    def __sub__(self, other: 'Vectors') -> Self:
        vectors1 = self._vectors
        vectors2 = other._vectors
        vectors3: list[Vector] = []
        for vector1, vector2 in zip(vectors1, vectors2):
            vectors3.append(vector1 - vector2)
        if self.len() > other.len():
            for index in range(other.len(), self.len()):
                exceeding_vector: Vector = self._vectors[index].copy()
                exceeding_vector << {"new": +1}
                vectors3.append(exceeding_vector)
        elif self.len() < other.len():
            for index in range(self.len(), other.len()):
                missing_vector: Vector = other._vectors[index].copy()
                missing_vector << {"new": -1}
                vectors3.append(missing_vector)
        return Vectors() << od.Pipe(vectors3)

    def reset(self, *parameters) -> Self:
        self._vectors = []
        return super().reset(*parameters)


