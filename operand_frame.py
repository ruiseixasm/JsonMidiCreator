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

import operand_value as ou
import operand_value as ov
import operand_length as ol
import operand_tag as ot


# Works as a traditional C list (chained)
class Frame(Operand):
    def __init__(self):
        self._next_operand: Optional[Operand] = ot.Null()
        
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
        for single_operand in self:
            match operand:
                case Frame():
                    match single_operand:
                        case operand:   return single_operand
                case _:
                    match single_operand:
                        case Frame():   continue
                        case operand:   return single_operand
        return ot.Null()
    
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
   
    def __pow__(self, operand: Operand) -> 'Frame':
        self._next_operand = operand
        return self
    
    def __rpow__(self, operand: Operand) -> 'Frame':
        return self**operand
    
    def __lshift__(self, operand: Operand) -> 'Frame':
        match operand:
            case None: self._next_operand = None
        return self

    def __and__(self, subject: 'Operand') -> Operand:
        match subject:
            case Frame():   # Both must be Frame() operands
                for self_frame in self: # Full conditions to be verified one by one (and)!
                    match self_frame:
                        case Canvas():  return self % Operand()
                        case Blank():   return ot.Null()
                        case FrameFrame():      # Only Frames are conditional
                            frame_frame_null = True
                            for subject_frame in subject:
                                if not isinstance(subject_frame, FrameFrame): continue
                                if (self_frame | subject_frame).__class__ != ot.Null:
                                    frame_frame_null = False
                                    break
                            if frame_frame_null: return ot.Null()
                        case OperandFrame():    # Only Frames are conditional (OperandFrame is it for single Operand)
                            for single_subject_operand in subject:    # Gets the single Subject Operand, last one
                                if isinstance(single_subject_operand, Frame): continue
                                if (self_frame | single_subject_operand).__class__ == ot.Null:
                                    return ot.Null()
                        case Frame():   continue
                        case _:         return self_frame   # In case it's an Operand (last in the chain)
            case _: return self.__rand__(subject)

    # Only self is a Frame() operand, operand is not a Frame, just an Operand, for sure
    def __rand__(self, subject: 'Operand') -> 'Operand':
        for self_frame in self: # Full conditions to be verified one by one (and)!
            match self_frame:
                case Canvas():  return self % Operand()
                case Blank():   return ot.Null()
                case OperandFrame():    # Only Frames are conditional
                    if (self_frame | subject).__class__ == ot.Null:
                        return ot.Null()
                case FrameFrame():  # If it's a simple Operand the existence of FrameFrame means False!
                    return ot.Null()
                case Frame():   continue
                case _:         return self_frame
        return subject

class FrameFrame(Frame):
    def __or__(self, subject: Operand) -> Operand:
        match subject:
            case FrameFrame():  return ot.Null()
            case _:             return subject

class OperandFrame(Frame):
    def __or__(self, subject: Operand) -> Operand:
        match subject:
            case Frame():       return subject
            case _:             return ot.Null()

class Canvas(FrameFrame):
    pass

class Blank(FrameFrame):
    pass

class Inner(FrameFrame):
    def __or__(self, subject: Operand) -> Operand:
        match subject:
            case Inner():   return subject
            case _:         return super().__or__(subject)

class Outer(FrameFrame):
    def __or__(self, subject: Operand) -> Operand:
        match subject:
            case Outer():   return subject
            case _:         return super().__or__(subject)

class Selection(OperandFrame):
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
            case ol.Position(): self._position = operand
            case ol.TimeLength(): self._time_length = operand
            case _: super().__lshift__(operand)
        return self

class Range(OperandFrame):
    def __init__(self, operand: Operand, position: ol.Position = None, length: ol.Length = None):
        self._operand = operand
        self._position = position
        self._length = length

    def __or__(self, operand: 'Operand') -> bool:
        return True


class Repeat(OperandFrame):
    def __init__(self, unit, repeat: int = 1):
        self._unit = unit
        self._repeat = repeat

    def step(self) -> Operand:
        if self._repeat > 0:
            self._repeat -= 1
            return self._unit
        return ot.Null()

    def __or__(self, operand: 'Operand') -> Operand:
        return ot.Null()

class Increment(OperandFrame):
    """
    The Increment class initializes with a Unit and additional arguments,
    similar to the arguments in the range() function.

    Parameters:
    unit (Unit): The unit object.
    *argv (int): Additional arguments, similar to the range() function.

    The *argv works similarly to the arguments in range():
    - If one argument is provided, it's taken as the end value.
    - If two arguments are provided, they're taken as start and end.
    - If three arguments are provided, they're taken as start, end, and step.

    Increment usage:
    operand = Increment(unit, 8)
    operand = Increment(unit, 0, 10, 2)
    """
    def __init__(self, unit, *argv: int):
        """
        Initialize the Increment with a Unit and additional arguments.

        Parameters:
        unit (Unit): The unit object.
        *argv: Additional arguments, similar to the range() function.

        The *argv works similarly to the arguments in range():
        - If one argument is provided, it's taken as the end value.
        - If two arguments are provided, they're taken as start and end.
        - If three arguments are provided, they're taken as start, end, and step.

        Increment usage:
        operand = Increment(unit, 8)
        operand = Increment(unit, 0, 10, 2)
        """

        self._unit = unit
        self._start = 0
        self._stop = 0
        self._step = 1
        if len(argv) == 1:
            self._stop = argv[0]
        elif len(argv) == 2:
            self._start = argv[0]
            self._stop = argv[1]
        elif len(argv) == 3:
            self._start = argv[0]
            self._stop = argv[1]
            self._step = argv[2]
        else:
            raise ValueError("Increment requires 1, 2, or 3 arguments for the range.")

        self._iterator = self._start

    def step(self) -> Operand:
        if self._iterator < self._stop:
            self._unit += self._step
            self._iterator += 1
            return self._unit
        return ot.Null()

    def __or__(self, operand: 'Operand') -> bool:
        return ot.Null()
