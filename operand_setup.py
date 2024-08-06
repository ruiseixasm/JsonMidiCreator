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
import enum
# Json Midi Creator Libraries
from creator import *
from operand import Operand

import operand_value as ov
import operand_length as ol
import operand_generic as og


class Setup(Operand):
    def __init__(self):
        self._next_operand: Operand = None

    def __mod__(self, operand: Operand) -> Operand:
        if type(self) == type(operand):
            return self
        if self._next_operand is not None:
            match operand:
                case Setup():
                    if isinstance(self._next_operand, Setup):
                        return self._next_operand % operand
                    return og.Null()
                case Operand():
                    match self._next_operand:
                        case Setup():
                            return self._next_operand % Operand()
                        case Operand():
                            return self._next_operand
        return og.Null()
    
    def __pow__(self, operand: Operand) -> 'Setup':
        match operand:
            case Setup():
                self._setup_list.append(operand)
            case Operand():
                self._next_operand = operand
        return self
    
    def __lshift__(self, operand: Operand) -> 'Setup':
        match operand:
            case None: self._next_operand = None
        return self

class Inner(Setup):
    def __init__(self):
        super().__init__()

class Selection(Setup):
    def __init__(self):
        self._position: ol.Position = ol.Position()
        self._time_length: ol.TimeLength = ol.TimeLength() << ov.Beat(1)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ol.Position():
                return self._position
            case ol.TimeLength():
                return self._time_length
        return self

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "position": self._position.getSerialization(),
            "time_length": self._time_length.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Selection':
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "position" in serialization and "time_length" in serialization and
            "operand" in serialization):

            self._position  = ol.Position().loadSerialization(serialization["position"])
            self._time_length    = ol.TimeLength().loadSerialization(serialization["length"])
            class_name = serialization["class"]
        return self

    def copy(self) -> 'Selection':
        return Selection() << self._position.copy() << self._time_length.copy()

    def __lshift__(self, operand: Operand) -> 'Operand':
        match operand:
            case ol.Position(): self._position = operand
            case ol.TimeLength(): self._time_length = operand
            case _: super().__lshift__(operand)
        return self
    

class Range(Setup):
    def __init__(self, operand: Operand, position: ol.Position = None, length: ol.Length = None):
        self._operand = operand
        self._position = position
        self._length = length
