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
import math
# Json Midi Creator Libraries
import creator as c
from operand import Operand
import operand_time as ot
import operand_value as ov
import operand_label as ol
import operand_frame as of


class Operator(Operand):
    """
    An Operator processes an Operand with an Integer input and an Operand output.

    Parameters
    ----------
    first : Operand_like
        A Operand to be regulated
    """
    def __init__(self, operand: Operand = None):
        self._operand: Operand = ol.Null() if operand is None else operand

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case ol.Null() | None:  return ol.Null()
            case Operand():         return self._operand
            case _:                 return self

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "operand": self._operand.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "operand" in serialization):

            operand_class = serialization["operand"]["class"]
            self._operand = globals()[operand_class]().loadSerialization(serialization["operand"])
        return self

    def copy(self) -> 'Operator':
        return self.__class__(self._operand)

    def __lshift__(self, operand: Operand) -> 'Operator':
        match operand:
            case of.Frame():        self << (operand & self)
            case Operand():         self._operand = operand
            case _:                 self._operand << operand
        return self

    def __add__(self, operand: Operand) -> 'Operand':
        match operand:
            case of.Frame():        return self + (operand & self)
            case _:                 return self.copy() << self._operand + operand
    
    def __sub__(self, operand: Operand) -> 'Operand':
        match operand:
            case of.Frame():        return self - (operand & self)
            case _:                 return self.copy() << self._operand - operand
    
    def __mul__(self, operand: Operand) -> 'Operand':
        match operand:
            case of.Frame():        return self * (operand & self)
            case _:                 return self.copy() << self._operand * operand
    
    def __truediv__(self, operand: Operand) -> 'Operand':
        match operand:
            case of.Frame():        return self / (operand & self)
            case _:                 return self.copy() << self._operand / operand

class Oscillator(Operator):
    """
    This Operator has a function returns the given Operand regulated accordingly to the Oscillator parameters.

    Parameters
    ----------
    first : Operand_like
        A Operand to be regulated
    """
    def __init__(self, operand: Operand = None):
        super().__init__(operand)
        self._position: ot.Position     = ot.Position()
        self._length: ot.Length         = ot.Length()
        self._amplitude: ov.Amplitude   = ov.Amplitude()
        self._offset: ov.Offset         = ov.Offset()
        
    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ot.Position():         return self._position
            case ot.Length():           return self._length
            case ov.Amplitude():        return self._amplitude
            case ov.Offset():           return self._offset
            case self._operand.__class__():
                print(math.sin(math.radians(30)))
            case _:                     return super().__mod__(operand)

    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["position"] = self._position.getSerialization()
        element_serialization["length"] = self._length.getSerialization()
        element_serialization["amplitude"] = self._amplitude % float()
        element_serialization["offset"] = self._offset % float()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Oscillator':
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "position" in serialization and "length" in serialization and
            "amplitude" in serialization and "offset" in serialization):

            super().loadSerialization(serialization)
            self._position = ot.Position().loadSerialization(serialization["position"])
            self._length = ot.Length().loadSerialization(serialization["length"])
            self._amplitude = ov.Amplitude(serialization["amplitude"])
            self._offset = ov.Offset(serialization["offset"])
        return self
      
    def copy(self) -> 'Oscillator':
        return super().copy() << self._position.copy() << self._length.copy() << self._amplitude.copy() << self._offset.copy()

    def __lshift__(self, operand: Operand) -> 'Oscillator':
        match operand:
            case Oscillator():
                super().__lshift__(operand)
                self._position      = operand % ot.Position()
                self._length        = operand % ot.Length()
                self._amplitude     = operand % ov.Amplitude()
                self._offset        = operand % ov.Offset()
            case ot.Position():     self._position = operand
            case ot.Length():       self._length = operand
            case ov.Amplitude():    self._amplitude = operand
            case ov.Offset():       self._offset = operand
            case _: super().__lshift__(operand)
        return self

class Line(Operator):
    ...
