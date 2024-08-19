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
from typing import Optional
import enum
# Json Midi Creator Libraries
import creator as c
from operand import Operand

import operand_numeric as on
import operand_value as ou
import operand_value as ov
import operand_length as ol
import operand_frame as of
import operand_tag as ot


# Works as a traditional C list (chained)
class Frame(Operand):
    def __init__(self):
        self._next_operand: Optional[Operand] = ot.Dummy()
        
    def __iter__(self):
        self._current_node: Optional[Operand] = self    # Reset to the start node on new iteration
        return self
    
    def __next__(self):
        if isinstance(self._current_node, ot.Null): raise StopIteration
        previous_node = self._current_node
        match self._current_node:
            case Frame():   self._current_node = self._current_node._next_operand
            case _:         self._current_node = ot.Null()
        return previous_node

    def len(self) -> int:
        list_size = 0
        for _ in self:
            list_size += 1
        return list_size

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Frame():
                for single_operand in self:
                    if isinstance(single_operand, operand.__class__):
                        return single_operand
            case ot.Null() | None:      return ot.Null()
            case _:
                for single_operand in self:
                    match single_operand:
                        case Frame():   continue
                        case operand:   return single_operand
        return self
    
    def __eq__(self, frame: 'Frame') -> bool:
        return isinstance(self, frame.__class__)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "next_operand": self._next_operand.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "next_operand" in serialization):

            self._next_operand = Operand().loadSerialization(serialization)
        return self
    
    def pop(self, frame: 'Frame') -> 'Frame':
        previous_frame: 'Frame' = self
        for single_frame in self:
            if isinstance(single_frame, Frame) and single_frame == frame:
                if single_frame == self:
                    self = self._next_operand
                    previous_frame = self
                else:
                    previous_frame._next_operand = single_frame._next_operand
                    previous_frame = single_frame
        return self      
   
    def __pow__(self, operand: Operand) -> 'Frame':
        match operand:
            case Operand(): self._next_operand = operand
            case _:         self._next_operand = ot.Dummy()
        return self

# FRAME FILTERS (INDEPENDENT OF OPERAND DATA)

class FrameFilter(Frame):
    def __and__(self, subject: Operand) -> Operand:
        for operand in subject:
            if self == operand:
                return self._next_operand & subject
        return ot.Null()
        
    def __eq__(self, other: Operand) -> bool:
        return self.__class__ == other.__class__

class Canvas(FrameFilter):
    def __and__(self, subject: Operand) -> Operand:
        return self % Operand()

class Blank(FrameFilter):
    def __and__(self, subject: Operand) -> Operand:
        return ot.Null()

class Inner(FrameFilter):
    pass
    
class Outer(FrameFilter):
    pass

class Odd(FrameFilter):
    def __init__(self):
        self._call: int = 0

    def __and__(self, subject: Operand) -> Operand:
        self._call += 1
        if self._call % 2 == 1:
            return self._next_operand & subject
        else:
            return ot.Null()

class Even(FrameFilter):
    def __init__(self):
        self._call: int = 0
        
    def __and__(self, subject: Operand) -> Operand:
        self._call += 1
        if self._call % 2 == 0:
            return self._next_operand & subject
        else:
            return ot.Null()

class Nths(FrameFilter):
    def __init__(self, nths: int = 4):
        self._call: int = 0
        self._nths: int = nths

    def __and__(self, subject: Operand) -> Operand:
        self._call += 1
        if self._call % self._nths == 0:
            return self._next_operand & subject
        else:
            return ot.Null()

class Nth(FrameFilter):
    def __init__(self, nth: int = 4):
        self._call: int = 0
        self._nth: int = nth

    def __and__(self, subject: Operand) -> Operand:
        self._call += 1
        if self._call == self._nth:
            return self._next_operand & subject
        else:
            return ot.Null()

# SUBJECT FILTERS (DEPENDENT ON SUBJECT'S OPERAND DATA)

class SubjectFilter(Frame):
    ...

class Equal(SubjectFilter):
    def __init__(self, operand: Operand):
        super().__init__()
        self._operand: Operand = operand

    def __and__(self, subject: Operand) -> Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        if self_operand == self._operand:
            return self_operand
        return ot.Null()

class Greater(SubjectFilter):
    def __init__(self, operand: Operand):
        super().__init__()
        self._operand: Operand = operand

    def __and__(self, subject: Operand) -> Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        if self_operand == self._operand:
            return self_operand
        return ot.Null()

class Lower(SubjectFilter):
    def __init__(self, operand: Operand):
        super().__init__()
        self._operand: Operand = operand

    def __and__(self, subject: Operand) -> Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        if self_operand == self._operand:
            return self_operand
        return ot.Null()

# OPERAND FILTERS (PROCESSES THE OPERAND DATA WITHOUT WRITING/ALTERING THE SOURCE OPERAND)

class OperandFilter(Frame):
    def __init__(self):
        self._value: float = 0

class Iterate(OperandFilter):
    def __init__(self, step: float = None):
        super().__init__()
        self._step: float = 1 if step is None else step

    def __and__(self, subject: Operand) -> Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        stepped_operand = self_operand + self._value
        self._value += self._step
        return stepped_operand

class Selection(OperandFilter):
    def __init__(self):
        self._position: ol.Position = ol.Position()
        self._time_length: ol.TimeLength = ol.TimeLength() << ov.Beat(1)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ol.Position():     return self._position
            case ol.TimeLength():   return self._time_length
            case _:                 return super().__mod__(operand)

    def __or__(self, operand: 'Operand') -> bool:
        return True

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
            case of.Frame():        self << (operand & self)
            case Selection():
                self._position = operand % ol.Position()
                self._time_length = operand % ol.TimeLength()
            case ol.Position():     self._position = operand
            case ol.TimeLength():   self._time_length = operand
        return self

class Range(OperandFilter):
    def __init__(self, operand: Operand, position: ol.Position = None, length: ol.Length = None):
        self._operand = operand
        self._position = position
        self._length = length

    def __or__(self, operand: 'Operand') -> bool:
        return True

class Repeat(OperandFilter):
    def __init__(self, unit, repeat: int = 1):
        self._value = unit
        self._repeat = repeat

    def step(self) -> Operand:
        if self._repeat > 0:
            self._repeat -= 1
            return self._value
        return ot.Null()

    def __or__(self, operand: 'Operand') -> Operand:
        return ot.Null()

# OPERAND EDITORS (ALTERS THE SOURCE OPERAND DATA)

class OperandEditor(Frame):
    def __init__(self):
        self._value: float = 0

class Increment(OperandEditor):
    def __init__(self, step: float = None):
        super().__init__()
        self._step: float = 1 if step is None else step

    def __and__(self, subject: Operand) -> Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        self_operand << self_operand + self._value
        self._value = self._step
        return self_operand

