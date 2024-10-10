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
from fractions import Fraction
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ro
import operand_data as od
import operand_time as ot
import operand_frame as of
import operand_label as ol


# Works as a traditional C list (chained)
class Frame(o.Operand):
    def __init__(self):
        super().__init__()
        self._next_operand: o.Operand = o.Operand()
        
    # It has to include self, contrary to the Operand __next__ that excludes the self!!
    def __iter__(self):
        self._current_node: o.Operand = self    # Reset to the start node on new iteration
        return self
    
    # It has to skip NON Frame Operand, contrary to the Operand __next__ that includes all operands!!
    def __next__(self):
        if self._current_node is None: raise StopIteration
        previous_node = self._current_node
        match self._current_node:
            case Frame():   self._current_node = self._current_node._next_operand
            case _:         self._current_node = None
        return previous_node

    def __pow__(self, operand: any) -> 'Frame':
        self._next_operand = operand
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Frame,
        those Parameters are the ones present in the Frame tail of operands,
        namely a Frame or an Operand at the end of the tail made of Operand nodes.

        Examples
        --------
        >>> frame = Wrapper(Position())**Increment(2)**Step()
        >>> frame % Step() >> Print(0)
        {'class': 'Step', 'parameters': {'value': 0.0}}
        >>> Null() + frame + frame
        >>> frame % Step() >> Print(0)
        {'class': 'Step', 'parameters': {'value': 4.0}}
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Frame():
                        for single_operand in self:
                            if isinstance(single_operand, operand.__class__): # checks if it's the same Frame
                                return single_operand   # It's a Frame
                    case ol.Null() | None:      return ol.Null()
                    case _:
                        for single_operand in self:
                            match single_operand:
                                case Frame():   continue
                                case _:         return single_operand
            case Frame():
                for single_operand in self:
                    if isinstance(single_operand, operand.__class__): # checks if it's the same Frame
                        return single_operand.copy()    # It's a Frame
            case _:
                for single_operand in self:
                    match single_operand:
                        case Frame():           continue
                        case o.Operand():       return single_operand.copy()
                        case _:                 return single_operand
        return super().__mod__(operand)
    
    def __eq__(self, other_frame: 'Frame') -> bool:
        if type(self) == type(other_frame):
            self_operand_list: list = []
            for single_operand in self:
                self_operand_list.append(single_operand)
            other_operand_list: list = []
            for single_operand in other_frame:
                other_operand_list.append(single_operand)
            return self_operand_list == other_operand_list
        return False
    
    def getSerialization(self):
        next_operand = None
        if isinstance(self._next_operand, o.Operand):
            next_operand = self._next_operand.getSerialization()
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "next_operand": next_operand
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "next_operand" in serialization["parameters"]):

            self._next_operand = o.Operand().loadSerialization(serialization["parameters"]["next_operand"])
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
    
# 1. FRAME FILTERS (INDEPENDENT OF OPERAND DATA)

class FrameFilter(Frame):
    def __and__(self, subject: o.Operand) -> o.Operand:
        super().__init__()
        for operand in subject:
            if self == operand:
                return self._next_operand & subject
        return ol.Null()
        
    def __eq__(self, other: o.Operand) -> bool:
        return self.__class__ == other.__class__

class Canvas(FrameFilter):
    def __and__(self, subject: o.Operand) -> o.Operand:
        return self % o.Operand()

class Blank(FrameFilter):
    def __and__(self, subject: o.Operand) -> o.Operand:
        return ol.Null()

class Inner(FrameFilter):
    pass
    
class Outer(FrameFilter):
    pass

class Odd(FrameFilter):
    def __init__(self):
        self._call: int = 0

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._call += 1
        if self._call % 2 == 1:
            return self._next_operand & subject
        else:
            return ol.Null()

class Even(FrameFilter):
    def __init__(self):
        self._call: int = 0
        
    def __and__(self, subject: o.Operand) -> o.Operand:
        self._call += 1
        if self._call % 2 == 0:
            if isinstance(self._next_operand, Frame):
                return self._next_operand & subject
            return self._next_operand
        else:
            return ol.Null()

class Nths(FrameFilter):
    def __init__(self, nths: int = 4):
        self._call: int = 0
        self._nths: int = nths

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._call += 1
        if self._call % self._nths == 0:
            if isinstance(self._next_operand, Frame):
                return self._next_operand & subject
            return self._next_operand
        else:
            return ol.Null()

class Nth(FrameFilter):
    def __init__(self, *parameters):
        self._call: int = 0
        self._nth: tuple = parameters

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._call += 1
        if self._call in self._nth:
            if isinstance(self._next_operand, Frame):
                return self._next_operand & subject
            return self._next_operand
        else:
            return ol.Null()

# 2. SUBJECT FILTERS (DEPENDENT ON SUBJECT'S OPERAND DATA)

class SubjectFilter(Frame):
    def __init__(self, filter_operand: o.Operand):
        super().__init__()
        self._filter_operand: any = filter_operand

    def copy(self) -> 'SubjectFilter':
        match self._filter_operand:
            case o.Operand():
                return self.__class__( self._filter_operand.copy() )
            case _:
                return self.__class__( self._filter_operand )
    
class Equal(SubjectFilter):
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __and__(self, subject: o.Operand) -> o.Operand:
        for condition in self._filter_operand:
            if subject == condition:
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand &= subject
                return self_operand
        return ol.Null()

class NotEqual(SubjectFilter):
    def __init__(self, filter_operand: o.Operand):
        super().__init__(filter_operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        if subject != self._filter_operand:
            self_operand = self._next_operand
            if isinstance(self_operand, Frame):
                self_operand &= subject
            return self_operand
        return ol.Null()

class Greater(SubjectFilter):
    def __init__(self, filter_operand: o.Operand):
        super().__init__(filter_operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        if subject > self._filter_operand:
            self_operand = self._next_operand
            if isinstance(self_operand, Frame):
                self_operand &= subject
            return self_operand
        return ol.Null()

class Lower(SubjectFilter):
    def __init__(self, filter_operand: o.Operand):
        super().__init__(filter_operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        if subject < self._filter_operand:
            self_operand = self._next_operand
            if isinstance(self_operand, Frame):
                self_operand &= subject
            return self_operand
        return ol.Null()

class GreaterEqual(SubjectFilter):
    def __init__(self, filter_operand: o.Operand):
        super().__init__(filter_operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        if subject % self._filter_operand >= self._filter_operand:
            self_operand = self._next_operand
            if isinstance(self_operand, Frame):
                self_operand &= subject
            return self_operand
        return ol.Null()

class LowerEqual(SubjectFilter):
    def __init__(self, filter_operand: o.Operand):
        super().__init__(filter_operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        if subject % od.DataSource( self._filter_operand ) <= self._filter_operand:
            self_operand = self._next_operand
            if isinstance(self_operand, Frame):
                self_operand &= subject
            return self_operand
        return ol.Null()

# 3. OPERAND FILTERS (PROCESSES THE OPERAND DATA WITHOUT WRITING/ALTERING THE SOURCE OPERAND)

class OperandFilter(Frame):
    def __init__(self):
        super().__init__()
        self._data = 0

class Subject(OperandFilter):
    def __and__(self, subject: o.Operand) -> o.Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        if isinstance(self_operand, ol.Null):
            return self_operand
        return subject

class Iterate(OperandFilter):
    def __init__(self, step = None):
        super().__init__()
        self._step: int = 1 if step is None else step
        self._data = self._step * 0 # Sets the _data variable type

    def __and__(self, subject: o.Operand) -> o.Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        if self_operand is not None:
            stepped_operand = self_operand + self._data
            self._data += self._step
            return stepped_operand
        return ol.Null()
    
class Wrapper(OperandFilter):
    def __init__(self, operand: o.Operand = None):
        super().__init__()
        self._data = operand    # data is the targeted operand

    def __and__(self, subject: o.Operand) -> o.Operand:
        import operand_operator as oo
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        match self_operand:
            case o.Operand():
                match self._data:
                    case oo.Operator(): return self._data | self_operand.copy()
                    case o.Operand():   return self._data.copy() << self_operand
                    case None:          return ol.Null()
                    case _:             return self._data
            case _:
                match self._data:
                    case oo.Operator(): return self._data | self_operand
                    case o.Operand():   return self._data.copy() << self_operand
                    case None:          return ol.Null()
                    case _:             return self._data

class Extractor(OperandFilter):
    def __init__(self, operand: o.Operand = None):
        super().__init__()
        self._data = operand    # data is the targeted operand

    def __and__(self, subject: o.Operand) -> o.Operand:
        import operand_operator as oo
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        return self_operand % self._data

# 4. OPERAND EDITORS (ALTERS THE SOURCE OPERAND DATA)

class OperandEditor(Frame):
    def __init__(self):
        super().__init__()

class Increment(OperandEditor):
    def __init__(self, step: float = None):
        super().__init__()
        self._step: float = 1 if step is None else step

    def __and__(self, subject: o.Operand) -> o.Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        match self_operand:
            case o.Operand():
                last_self_operand = self_operand.copy()
            case _:
                last_self_operand = self_operand
        if self_operand is not None:
            self_operand << self_operand + self._step
            return last_self_operand
        return ol.Null()

