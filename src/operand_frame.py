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
from typing import Union, Callable, Tuple, Any
from fractions import Fraction
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
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
        if isinstance(operand, o.Operand):
            operand._set = False
        self._next_operand = operand
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Frame,
        those Parameters are the ones present in the Frame tail of operands,
        namely a Frame or an Operand at the end of the tail made of Operand nodes.

        Examples
        --------
        >>> frame = Wrap(Position())**Increment(2)**Step()
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
    
    def getSerialization(self) -> dict:
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
    
    def __rrshift__(self, operand: any) -> any:
        return operand & self   # operand is the subject

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
    
    def copy(self, *parameters) -> 'Frame':
        match self._left_parameter:
            case o.Operand():
                self_copy: Frame = self.__class__( self._left_parameter.copy() ) << parameters
            case _:
                self_copy: Frame = self.__class__( self._left_parameter ) << parameters
        # COPY THE SELF OPERANDS RECURSIVELY
        if type(self._next_operand) is not o.Operand:
            match self._next_operand:
                case o.Operand():
                    self_copy._next_operand = self._next_operand.copy()
                case _:
                    self_copy._next_operand = self._next_operand
        return self_copy

    def reset(self, *parameters) -> 'Frame':
        # RESET THE SELF OPERANDS RECURSIVELY
        if type(self._next_operand) is not o.Operand and isinstance(self._next_operand, o.Operand):
            self._next_operand.reset()
        self._initiated     = False
        self._set           = False
        self._index         = 0
        return self << parameters
    
    def clear(self, *parameters) -> 'Frame':
        self._next_operand = o.Operand()
        return self.reset() << self.__class__() << parameters
    
# 1. FRAME FILTERS (INDEPENDENT OF OPERAND DATA) Operand isn't the Subject

class FrameFilter(Frame):
    def __init__(self):
        super().__init__()

    def __and__(self, subject: o.Operand) -> o.Operand:
        super().__init__()
        for operand in subject:
            if self == operand:
                return self._next_operand & subject
        return ol.Null()
        
    def __eq__(self, other: o.Operand) -> bool:
        return self.__class__ == other.__class__

class Canvas(FrameFilter):
    def __init__(self):
        super().__init__()

    def __and__(self, subject: o.Operand) -> o.Operand:
        return self % o.Operand()

class Blank(FrameFilter):
    def __init__(self):
        super().__init__()

    def __and__(self, subject: o.Operand) -> o.Operand:
        return ol.Null()

class Inner(FrameFilter):
    def __init__(self):
        super().__init__()
    
class Outer(FrameFilter):
    def __init__(self):
        super().__init__()

class Odd(FrameFilter):
    def __init__(self):
        super().__init__()
        self._call: int = 0

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._call += 1
        if self._call % 2 == 1:
            return self._next_operand & subject
        else:
            return ol.Null()

class Even(FrameFilter):
    def __init__(self):
        super().__init__()
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
        super().__init__()
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
        super().__init__()
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

class Left(Frame):  # LEFT TO RIGHT
    def __init__(self, left_parameter: any = None):
        super().__init__()
        self._left_parameter = 0 if left_parameter is None else left_parameter

    def __and__(self, subject: any) -> any:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        if isinstance(self_operand, tuple):
            self_operand_tuple: tuple = ()
            for single_operand in self_operand:
                if single_operand.__class__ == o.Operand:
                    single_operand = subject
                    if isinstance(single_operand, o.Operand):
                        single_operand._set = True
                elif isinstance(single_operand, o.Operand) and not single_operand._set:
                    self_operand_tuple += (single_operand << subject,)
                    single_operand._set = True
                else:
                    self_operand_tuple += (subject,)
                    if isinstance(subject, o.Operand):
                        subject._set = True
            self_operand = self_operand_tuple
        elif self_operand.__class__ == o.Operand:
            self_operand = subject
            if isinstance(self_operand, o.Operand):
                self_operand._set = True
        elif isinstance(self_operand, o.Operand) and not self_operand._set:
            self_operand = self_operand.copy() << subject   # Has to use a copy of the frame operand
            self_operand._set = True
        return self_operand
    
    def copy(self, *parameters) -> 'Frame':
        self_copy = super().copy(parameters)
        match self._left_parameter:
            case o.Operand():
                self_copy._left_parameter = self._left_parameter.copy()
            case _:
                self_copy._left_parameter = self._left_parameter
        return self_copy
    
    def clear(self, *parameters) -> 'Frame':
        self._left_parameter = 0
        return super().clear(parameters)
    
class Subject(Left):
    def __init__(self, subject):
        super().__init__(subject)

    def __and__(self, subject: o.Operand) -> o.Operand:
        return super().__and__(self._left_parameter)

class PushTo(Left):
    def __init__(self, operand: o.Operand):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        return super().__and__(subject >> self._left_parameter)

class PushOut(Left):
    def __init__(self, operand: o.Operand):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        subject >> self._left_parameter
        return super().__and__(subject)

class Pick(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __and__(self, subject: o.Operand) -> o.Operand:
        if len(self._left_parameter) > 0:
            picker: int = 0
            match subject:
                case int() | float() | Fraction():
                    picker = int(subject)
                case o.Operand():
                    picker_candidate = subject % int()
                    if isinstance(picker_candidate, int):
                        picker = picker_candidate
            picker %= len(self._left_parameter)
            return super().__and__(self._left_parameter[picker])
        return super().__and__(ol.Null())

class Formula(Left):
    def __init__(self, operation: Callable[[Tuple[Any, ...]], Any]):
        super().__init__(operation)

    def __and__(self, subject: o.Operand) -> o.Operand:
        return super().__and__(self._left_parameter(subject))
    
class Iterate(Left):
    def __init__(self, step = None):
        super().__init__(1 if step is None else step)

    def __and__(self, subject: o.Operand) -> o.Operand:
        self_operand = super().__and__(self._index)
        self._index += self._left_parameter    # iterates whenever called
        return self_operand
    
class Foreach(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._len: int      = len(parameters)
        self._step: int     = 1

    def __and__(self, subject: o.Operand) -> o.Operand:
        import operand_container as oc
        import operand_chaos as ocr
        if self._len > 0:
            subject = self._left_parameter[self._index]
            if isinstance(subject, (oc.Container, ocr.Chaos)):
                subject %= ou.Next()    # Iterates to next subject
            self._index += self._step
            self._index %= self._len
        else:
            subject = ol.Null()
        return super().__and__(subject)

    def clear(self, *parameters) -> 'Foreach':
        super().clear(parameters)
        self._left_parameter = ()
        self._len = 0
        self._step = 1
        return self
    
class Transition(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._len: int      = len(parameters)
        self._step: int     = 1
        self._last_subject  = ol.Null()

    def __and__(self, subject: o.Operand) -> o.Operand:
        import operand_container as oc
        import operand_chaos as ocr
        if self._len > 0:
            subject = self._left_parameter[self._index]
            if not self._last_subject == subject:
                if isinstance(subject, (oc.Container, ocr.Chaos)):
                    subject %= ou.Next()    # Iterates to next subject
                self._index += self._step
                self._index %= self._len
                self._last_subject = subject
        else:
            subject = ol.Null()
        return super().__and__(subject)

    def clear(self, *parameters) -> 'Transition':
        super().clear(parameters)
        self._left_parameter = ()
        self._len = 0
        self._step = 1
        self._last_subject  = ol.Null()
        return self
    
class Repeat(Left):
    def __init__(self, times: int = 1):
        super().__init__(times)

    def __and__(self, subject: o.Operand) -> o.Operand:
        import operand_container as oc
        new_container: oc.Container = oc.Container()
        for _ in range(self._left_parameter):
            datasource_data = super().__and__(subject)
            if isinstance(datasource_data, o.Operand):
                datasource_data = datasource_data.copy()
            new_container += datasource_data
        return new_container

class Type(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __and__(self, subject: o.Operand) -> o.Operand:
        for condition in self._left_parameter:
            if type(subject) == type(condition):
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand &= subject
                return self_operand
        return ol.Null()

class Equal(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._previous: list = []

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._previous.insert(0, subject)
        for condition in self._left_parameter:
            if isinstance(condition, ou.Previous):
                previous_i: int = condition % int()
                if previous_i < len(self._previous):
                    condition = self._previous[previous_i]
                else:
                    continue
            if subject == condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand &= subject
                return self_operand
        return ol.Null()

class NotEqual(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._previous: list = []

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._previous.insert(0, subject)
        for condition in self._left_parameter:
            if isinstance(condition, ou.Previous):
                previous_i: int = condition % int()
                if previous_i < len(self._previous):
                    condition = self._previous[previous_i]
                else:
                    continue
            if not subject == condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand &= subject
                return self_operand
        return ol.Null()

class Greater(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._previous: list = []

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._previous.insert(0, subject)
        for condition in self._left_parameter:
            if isinstance(condition, ou.Previous):
                previous_i: int = condition % int()
                if previous_i < len(self._previous):
                    condition = self._previous[previous_i]
                else:
                    continue
            if subject > condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand &= subject
                return self_operand
        return ol.Null()

class Less(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._previous: list = []

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._previous.insert(0, subject)
        for condition in self._left_parameter:
            if isinstance(condition, ou.Previous):
                previous_i: int = condition % int()
                if previous_i < len(self._previous):
                    condition = self._previous[previous_i]
                else:
                    continue
            if subject < condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand &= subject
                return self_operand
        return ol.Null()

class GreaterEqual(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._previous: list = []

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._previous.insert(0, subject)
        for condition in self._left_parameter:
            if isinstance(condition, ou.Previous):
                previous_i: int = condition % int()
                if previous_i < len(self._previous):
                    condition = self._previous[previous_i]
                else:
                    continue
            if subject >= condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand &= subject
                return self_operand
        return ol.Null()

class LessEqual(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._previous: list = []

    def __and__(self, subject: o.Operand) -> o.Operand:
        self._previous.insert(0, subject)
        for condition in self._left_parameter:
            if isinstance(condition, ou.Previous):
                previous_i: int = condition % int()
                if previous_i < len(self._previous):
                    condition = self._previous[previous_i]
                else:
                    continue
            if subject <= condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand &= subject
                return self_operand
        return ol.Null()

class Get(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __and__(self, subject: o.Operand) -> o.Operand:
        if isinstance(subject, o.Operand):
            parameter = subject
            for single_parameter in self._left_parameter:
                parameter %= single_parameter
            return super().__and__(parameter)
        return super().__and__(subject)
        
class Set(Left):
    def __init__(self, operand: o.Operand = None):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        if isinstance(subject, o.Operand):
            return super().__and__(subject << self._left_parameter)
        return super().__and__(subject)
    
        # self_operand = self._next_operand
        # if isinstance(self_operand, Frame):
        #     match subject:
        #         case o.Operand():   self_operand &= subject << self_operand
        #         case _:             self_operand &= subject
        # if self_operand.__class__ == o.Operand:
        #     match subject:
        #         case o.Operand():   self_operand = subject << self_operand
        #         case _:             self_operand = subject
        #     self_operand._set = True
        # return self_operand
        
class Push(Left):
    def __init__(self, operand: o.Operand = None):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            match subject:
                case o.Operand():   self_operand &= self_operand >> subject
                case _:             self_operand &= subject
        if self_operand.__class__ == o.Operand:
            match subject:
                case o.Operand():   self_operand = self_operand >> subject
                case _:             self_operand = subject
        return self_operand

class Add(Left):
    def __init__(self, operand: any = 1):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        return super().__and__(subject + self._left_parameter)

class Subtract(Left):
    def __init__(self, operand: any = 1):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        return super().__and__(subject - self._left_parameter)

class Multiply(Left):
    def __init__(self, operand: any = 1):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        return super().__and__(subject * self._left_parameter)

class Divide(Left):
    def __init__(self, operand: any = 1):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        return super().__and__(subject / self._left_parameter)

# 3. OPERAND FILTERS (PROCESSES THE OPERAND DATA WITHOUT WRITING/ALTERING THE SOURCE OPERAND)

class Right(Frame):
    def __init__(self, right_parameter: any = None):
        super().__init__()
        self._right_parameter = 0 if right_parameter is None else right_parameter

class Increment(Right):
    def __init__(self, step = None):
        super().__init__(0)
        self._step: float = 1 if step is None else step

    def __and__(self, subject: o.Operand) -> o.Operand:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        match self_operand:
            case ol.Null():
                self._right_parameter += self._step    # iterates whenever called
                return self_operand
            case tuple():
                for single_operand in self_operand:
                    if isinstance(single_operand, o.Operand):
                        single_operand << single_operand + self._right_parameter
                        single_operand._set = True
                incremented_operand = self_operand
            case _:
                if self_operand.__class__ == o.Operand:
                    incremented_operand = self._right_parameter
                elif isinstance(self_operand, o.Operand):
                    incremented_operand = self_operand + self._right_parameter
                else:
                    incremented_operand = self._right_parameter
        self._right_parameter += self._step
        if isinstance(incremented_operand, o.Operand):
            if isinstance(self_operand, o.Operand):
                incremented_operand._set = self_operand._set
            else:
                incremented_operand._set = True
        return incremented_operand

class Wrap(Right):
    def __init__(self, wrapper: o.Operand = None):
        super().__init__(wrapper)

    def __and__(self, subject: o.Operand) -> o.Operand:
        import operand_operator as oo
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        match self_operand:
            case o.Operand():
                match self._right_parameter:
                    case oo.Operator(): wrapped_operand = self._right_parameter | self_operand.copy()
                    case o.Operand():   wrapped_operand = self._right_parameter.copy() << self_operand
                    case None:          wrapped_operand = ol.Null()
                    case _:             wrapped_operand = self._right_parameter
            case _:
                match self._right_parameter:
                    case oo.Operator(): wrapped_operand = self._right_parameter | self_operand
                    case o.Operand():   wrapped_operand = self._right_parameter.copy() << self_operand
                    case None:          wrapped_operand = ol.Null()
                    case _:             wrapped_operand = self._right_parameter
        if isinstance(wrapped_operand, o.Operand):
            if isinstance(self_operand, o.Operand):
                wrapped_operand._set = self_operand._set
            else:
                wrapped_operand._set = True
        return wrapped_operand

class Extract(Right):
    def __init__(self, operand: o.Operand = None):
        super().__init__(operand)

    def __and__(self, subject: o.Operand) -> o.Operand:
        import operand_operator as oo
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand &= subject
        extracted_data = self_operand % self._right_parameter
        extracted_data._set = self_operand._set # Set status has to be kept
        return extracted_data

# 4. OPERAND EDITORS (ALTERS THE SOURCE OPERAND DATA)

class OperandEditor(Frame):
    def __init__(self):
        super().__init__()
