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
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_frame as of
import operand_label as ol

if TYPE_CHECKING:
    from operand_container import Container

# Works as a traditional C list (chained)
class Frame(o.Operand):
    """`Frame`

    Frame is used in conjugation with a `Composition` container to apply, frame, specific parameters.
    Frames are chained with other Frames with the `**` operator.

    Parameters
    ----------
    Any(None) : Frame doesn't have any self parameters.
    """
    def __init__(self, *parameters):
        import operand_container as oc
        super().__init__()
        # These parameters replace the homologous Operand's ones
        self._next_operand: any = o.Operand()
        self._multi_data: dict  = {}
        self._inside_container: oc.Container = None
        self._root_frame: bool = True
        self._index_iterator: Type = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter
        
    # It has to include self, contrary to the Operand __next__ that excludes the self!!
    def __iter__(self):
        self._current_node: any = self    # Reset to the start node on new iteration
        return self
    
    # It has to skip NON Frame Operand, contrary to the Operand __next__ that includes all operands!!
    def __next__(self):
        if self._current_node is None: raise StopIteration
        previous_node = self._current_node
        match self._current_node:
            case Frame():   self._current_node = self._current_node._next_operand
            case _:         self._current_node = None
        return previous_node

    def _increment_index(self, type: Type) -> Self:
        if self._index_iterator is None or self._index_iterator == type:
            self._index += 1
            self._index_iterator = type
        return self

    def _set_inside_container(self, container: 'Container') -> Self:
        # Needs to propagate the settings to the next Frames
        if isinstance(self._next_operand, Frame):
            self._next_operand._set_inside_container(container)
        self._inside_container = container
        # For each container, index needs to be reset
        self._index = 0
        return self

    def __pow__(self, operand: any) -> 'Frame':
        if isinstance(operand, o.Operand):
            operand._set = False
            if isinstance(operand, Frame):
                operand._root_frame = False
        self._next_operand = operand
        return self

    def __mod__(self, operand: o.T) -> o.T:
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
            case self.__class__():
                return self.copy()
            case od.DataSource():
                match operand._data:
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
    
    def __eq__(self, other: 'Frame') -> bool:
        if type(self) == type(other):
            return self._multi_data == other._multi_data
        if isinstance(other, od.Conditional):
            return other == self
            # self_operand_list: list = []
            # for single_operand in self:
            #     self_operand_list.append(single_operand)
            # other: list = []
            # for single_operand in other:
            #     other.append(single_operand)
            # return self_operand_list == other  # PRONE TO INFINITE RECURSION !!
        return False
    
    def getSerialization(self) -> dict:
        # serialization = {'class': "some", "parameters": {}}
        serialization = super().getSerialization()
        serialization["parameters"]["multi_data"] = self.serialize(self._multi_data)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "multi_data" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._multi_data = self.deserialize(serialization["parameters"]["multi_data"])
        return self
    
    def __lshift__(self, operand: any) -> Self:
        if isinstance(operand, Frame):
            self._multi_data = self.deep_copy(operand._multi_data)
            self._initiated = operand._initiated
            self._index = operand._index
            self._set = False   # by default a new copy of data unsets the Operand
            # COPY THE SELF OPERANDS RECURSIVELY
            if type(operand._next_operand) is not o.Operand:
                self._next_operand = self.deep_copy(operand._next_operand)
        return self

    # def __rrshift__(self, operand: o.T) -> o.T:
    #     return operand ^ self   # operand is the subject

    def __imul__(self, operand) -> Self:
        match operand:
            case int():
                for _ in range(operand):
                    ol.Null() << self
        return self


    def __xor__(self, input: Any) -> Any:
        return self.__ixor__(input)
    
    def __ixor__(self, input: Any) -> o.Operand:
        return o.Operand()
    
    def __rxor__(self, input: Any) -> Any:
        return self.__ixor__(input)
    

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
    
    def reset(self, *parameters) -> 'Frame':
        super().reset()
        self.deep_reset(self._multi_data)
        return self << parameters
    
    def clear(self, *parameters) -> 'Frame':
        super().clear()
        self.deep_clear(self._multi_data)
        return self << parameters
    
# 1. FRAME FILTERS (INDEPENDENT OF OPERAND DATA) Operand isn't the Subject

class FrameFilter(Frame):
    def __init__(self):
        super().__init__()

    def __ixor__(self, input: o.T) -> o.T:
        super().__init__()
        for operand in input:
            if self == operand:
                return self._next_operand.__and__(input)
        return ol.Null()
        
    def __eq__(self, other: o.Operand) -> bool:
        return self.__class__ == other.__class__

class Canvas(FrameFilter):
    def __init__(self):
        super().__init__()

    def __ixor__(self, input: o.T) -> o.T:
        return self % o.Operand()

class Blank(FrameFilter):
    def __init__(self):
        super().__init__()

    def __ixor__(self, input: o.T) -> o.T:
        return ol.Null()

class Inner(FrameFilter):
    def __init__(self):
        super().__init__()
    
class Outer(FrameFilter):
    def __init__(self):
        super().__init__()

# 2. SUBJECT FILTERS (DEPENDENT ON SUBJECT'S OPERAND DATA)

class Left(Frame):  # LEFT TO RIGHT
    def __init__(self, operand: any = None):
        super().__init__()
        self._multi_data['operand'] = 0 if operand is None else operand   # NO COPY !!

    def __ixor__(self, input: any) -> any:
                
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand = self_operand.__ixor__(input)
        if isinstance(self_operand, tuple):
            self_operand_tuple: tuple = ()
            for single_operand in self_operand:
                if single_operand.__class__ == o.Operand:
                    single_operand = input
                    if isinstance(single_operand, o.Operand):
                        single_operand._set = True
                elif isinstance(single_operand, o.Operand) and not single_operand._set:
                    self_operand_tuple += (single_operand << input,)
                    single_operand._set = True
                else:
                    self_operand_tuple += (input,)
                    if isinstance(input, o.Operand):
                        input._set = True
            self_operand = self_operand_tuple
        elif self_operand.__class__ == o.Operand:
            self_operand = input
            if isinstance(self_operand, o.Operand):
                self_operand._set = True
        elif isinstance(self_operand, o.Operand) and not self_operand._set:
            self_operand = self_operand.copy() << input   # Has to use a copy of the frame operand
            self_operand._set = True
            
        return self_operand


class Input(Left):
    def __ixor__(self, input: o.T) -> o.T:
        import operand_container as oc
        import operand_chaos as ch
        self._increment_index(Input)
        if isinstance(self._multi_data['operand'], oc.Container):
            if self._multi_data['operand'].len() > 0:
                item = self._multi_data['operand'][(self._index - 1) % self._multi_data['operand'].len()]
                return super().__ixor__(item)
            return super().__ixor__(ol.Null())
        if isinstance(self._multi_data['operand'], ch.Chaos):
            actual_chaos: ch.Chaos = self._multi_data['operand'] * 0    # Makes a copy without iterating
            self._multi_data['operand'] *= 1    # In order to not result in a copy of Chaos
            return super().__ixor__(actual_chaos)
        return super().__ixor__(self._multi_data['operand'])


class PushTo(Left):
    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input >> self._multi_data['operand'])

class PushOut(Left):
    def __ixor__(self, input: o.T) -> o.T:
        input >> self._multi_data['operand']
        return super().__ixor__(input)

class Choice(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __ixor__(self, input: o.T) -> o.T:
        if len(self._multi_data['operand']) > 0:
            choice: int = 0
            match input:
                case int() | float() | Fraction():
                    choice = int(input)
                case o.Operand():
                    choice_candidate = input % int()
                    if isinstance(choice_candidate, int):
                        choice = choice_candidate
            choice %= len(self._multi_data['operand'])
            return super().__ixor__(self._multi_data['operand'][choice])
        return super().__ixor__(ol.Null())

class Pick(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._multi_data['pick'] = list(self._multi_data['operand'])

    def __ixor__(self, input: o.T) -> o.T:
        if len(self._multi_data['operand']) > 0:
            if len(self._multi_data['pick']) == 0:
                self._multi_data['pick'] = list(self._multi_data['operand'])
            choice: int = 0
            match input:
                case int() | float() | Fraction():
                    choice = int(input)
                case o.Operand():
                    choice_candidate = input % int()
                    if isinstance(choice_candidate, int):
                        choice = choice_candidate
            choice %= len(self._multi_data['pick'])
            return super().__ixor__(self._multi_data['pick'].pop(choice))
        return super().__ixor__(ol.Null())

class Until(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._count_down: list = []
        for single_parameter in self._multi_data['operand']:
            if not isinstance(single_parameter, int):
                single_parameter = -1
            self._count_down.append(single_parameter)
        self._multi_data['operand'] = tuple(self._count_down)  # tuples are read only

    def __ixor__(self, input: o.T) -> o.T:
        pick_choices: any = ol.Null()
        if len(self._multi_data['operand']) > 0:
            picker: int = 0
            match input:
                case int() | float() | Fraction():
                    picker = int(input)
                case o.Operand():
                    picker_candidate = input % int()
                    if isinstance(picker_candidate, int):
                        picker = picker_candidate
            picker %= len(self._multi_data['operand'])
            if self._count_down[picker] > 0:
                self._count_down[picker] -= 1
            closest_picker: int = picker
            closest_place: int  = self._count_down[picker]
            for index, value in enumerate(self._multi_data['operand']):
                if self._count_down[index] < closest_place and value >= 0:
                    closest_picker = index
                    closest_place = self._count_down[index]
            pick_choices = closest_picker
            self._count_down[pick_choices] += self._multi_data['operand'][pick_choices] # adds position debt
            # Trim base, move closer (avoids astronomical distances)
            for index, _ in enumerate(self._multi_data['operand']):
                self._count_down[index] -= max(0, closest_place - 1)
        return super().__ixor__(pick_choices)

class Frequency(Left):
    def __init__(self, *parameters):
        frequency_list: list = []
        common_pi: int = 1
        common_sigma: int = 0
        top_frequency: int = 1
        for single_frequency in parameters:
            if isinstance(single_frequency, int) and single_frequency > 0:
                frequency_list.append(single_frequency)
                common_pi *= single_frequency
                common_sigma += single_frequency
                top_frequency = max(top_frequency, single_frequency)
            else:
                frequency_list.append(0)
        common_denominator: int = round(common_pi * common_sigma / top_frequency)

        until_list: list = []
        for single_frequency in frequency_list:
            if single_frequency > 0:
                until_list.append(
                    round(common_denominator / single_frequency)
                )
            else:
                until_list.append(-1)
        super().__init__(Until(*until_list))

    def __ixor__(self, input: o.T) -> o.T:
        return self._multi_data['operand'].__iand__(input)

class Formula(Left):
    def __init__(self, operation: Callable[[Tuple[Any, ...]], Any] = None):
        super().__init__(operation)

    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(self._multi_data['operand'](input))
    
class Iterate(Left):
    """`Frame -> Left -> Iterate`

    Iterate() returns a series of values by the set input amount, where this
    input defines the type of values too. Intended to be used with Clips.
    The first values is always zero or equivalent, so you may combine
    the present operand with Add().

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like, operand_like
        The default value is 1, but you may set a float like 2.5.
    
    Examples
    --------
    Gets the Staff Steps per Measure:
    >>> notes = Note() * 4
    >>> notes << Iterate()**Add(1)**Degree()
    >>> notes[0] % Pitch() % int() >> Print()
    1
    >>> notes[3] % Pitch() % int() >> Print()
    4
    """
    def __init__(self, start: any = 0, step: any = 1):
        iterator: dict = {
            "start":    start,
            "current":  start,
            "step":     step
        }
        if iterator['step'] is None:
            iterator['step'] = 1
        if iterator['current'] is None:
            iterator['current'] = iterator['step'] * 0
        elif type(iterator['current']) is not type(iterator['step']) \
            and isinstance(iterator['step'], o.Operand):
                iterator['current'] = iterator['step'].copy() << iterator['current']
        super().__init__(iterator)

    def __ixor__(self, input: o.T) -> o.T:
        import operand_chaos as ch
        self._increment_index(Iterate)
        if isinstance(input, ch.Chaos):
            if self._multi_data['operand']['current'] == self._multi_data['operand']['start']:
                input *= self._multi_data['operand']['start']
            self_operand = super().__ixor__( input )
            input *= self._multi_data['operand']['step']
        else:
            self_operand = super().__ixor__(
                self.deep_copy(self._multi_data['operand']['current'])
            )
        # iterates whenever called
        self._multi_data['operand']['current'] += self._multi_data['operand']['step']
        return self_operand

class Drag(Left):
    def __init__(self, *parameters):
        self._first_parameter = None
        super().__init__(parameters)

    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(input, o.Operand):
            if self._first_parameter is None:
                self._first_parameter = input
                for single_parameter in self._multi_data['operand']:
                    self._first_parameter %= single_parameter
            return super().__ixor__(self._first_parameter)
        return super().__ixor__(input)

class Loop(Left):
    def __init__(self, *parameters):

        processed_params = []
        for param in parameters:
            if isinstance(param, (range, list, tuple)):
                processed_params.extend(param)
            else:
                processed_params.append(param)
        super().__init__(tuple(processed_params))

    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Loop)
        operand_len: int = len(self._multi_data['operand'])
        if operand_len > 0:    # In case it its own parameters to iterate trough
            input = self._multi_data['operand'][(self._index - 1) % operand_len]
            return super().__ixor__(input)
        return ol.Null()

class Foreach(Loop):
    def __ixor__(self, input: o.T) -> o.T:
        operand_len: int = len(self._multi_data['operand'])
        if self._index < operand_len:   # Does only a single loop!
            return super().__ixor__(input)
        return ol.Null()

class Transition(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._multi_data['step'] = 1
        self._multi_data['last_subject'] = ol.Null()

    # NEEDS TO BE REVIEWED AND TESTED
    def __ixor__(self, input: o.T) -> o.T:
        import operand_container as oc
        import operand_chaos as ch
        if len(self._multi_data['operand']) > 0:
            input = self._multi_data['operand'][self._index]
            if not self._multi_data['last_subject'] == input:
                if isinstance(input, (oc.Container, ch.Chaos)):
                    next_data = input % od.Next()
                    input = next_data._data # Iterates to next subject
                self._index += self._multi_data['step']
                self._index %= len(self._multi_data['operand'])
                self._multi_data['last_subject'] = input
        else:
            input = ol.Null()
        return super().__ixor__(input)

    def reset(self, *parameters) -> 'Frame':
        super().reset()
        self._multi_data['last_subject'] = ol.Null()
        return self << parameters
    
class Repeat(Left):
    def __init__(self, times: int = 1):
        super().__init__(times)

    def __ixor__(self, input: o.T) -> o.T:
        import operand_container as oc
        new_container: oc.Container = oc.Container()
        for _ in range(self._multi_data['operand']):
            datasource_data = super().__ixor__(input)
            if isinstance(datasource_data, o.Operand):
                datasource_data = datasource_data.copy()
            new_container += datasource_data
        return new_container

class Selector(Left):
    pass

class All(Selector):
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input)

class First(Selector):
    def __ixor__(self, input: o.T) -> o.T:
        import operand_container as oc
        if isinstance(self._inside_container, oc.Container):
            first_item = self._inside_container.first()
            if input is first_item:    # Selected first call to pass
                if isinstance(self._next_operand, Frame):
                    return self._next_operand.__xor__(input)
                return self._next_operand
        return ol.Null()

class Last(Selector):
    def __ixor__(self, input: o.T) -> o.T:
        import operand_container as oc
        if isinstance(self._inside_container, oc.Container):
            last_item = self._inside_container.last()
            if input is last_item:    # Selected first call to pass
                if isinstance(self._next_operand, Frame):
                    return self._next_operand.__xor__(input)
                return self._next_operand
        return ol.Null()

class Odd(Selector):
    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Odd)
        if self._index % 2 == 1:    # Selected to pass
            if isinstance(self._next_operand, Frame):
                return self._next_operand.__xor__(input)
            return self._next_operand
        else:
            return ol.Null()

class Even(Selector):
    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Even)
        if self._index % 2 == 0:
            if isinstance(self._next_operand, Frame):
                return self._next_operand.__xor__(input)
            return self._next_operand
        else:
            return ol.Null()

class Every(Selector):
    def __init__(self, nths: int = 4):
        super().__init__()
        self._multi_data['nths'] = nths

    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Every)
        if self._multi_data['nths'] > 0 and self._index % self._multi_data['nths'] == 0:
            if isinstance(self._next_operand, Frame):
                return self._next_operand.__xor__(input)
            return self._next_operand
        else:
            return ol.Null()

class Nth(Selector):
    def __init__(self, *parameters):
        super().__init__()
        self._multi_data['parameters'] = parameters

    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Nth)
        if self._index in self._multi_data['parameters']:
            if isinstance(self._next_operand, Frame):
                return self._next_operand.__xor__(input)
            return self._next_operand
        else:
            return ol.Null()

class OperandType(Selector):
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __ixor__(self, input: o.T) -> o.T:
        for operand_class in self._multi_data['operand']:
            if isinstance(input, operand_class):
                return super().__ixor__(input)
        return super().__ixor__(ol.Null())

class Equal(Selector):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._multi_data['previous'] = []

    def __ixor__(self, input: o.T) -> o.T:
        self._multi_data['previous'].insert(0, input)
        for condition in self._multi_data['operand']:
            if isinstance(condition, od.Previous):
                previous_i: int = condition._data
                if previous_i < len(self._multi_data['previous']):
                    condition = self._multi_data['previous'][previous_i]
                else:
                    continue
            if input == condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand = self_operand.__ixor__(input)
                return self_operand
        return ol.Null()

    def reset(self, *parameters) -> 'Frame':
        super().reset()
        self._multi_data['previous'] = []
        return self << parameters
    
class NotEqual(Selector):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._multi_data['previous'] = []

    def __ixor__(self, input: o.T) -> o.T:
        self._multi_data['previous'].insert(0, input)
        for condition in self._multi_data['operand']:
            if isinstance(condition, od.Previous):
                previous_i: int = condition._data
                if previous_i < len(self._multi_data['previous']):
                    condition = self._multi_data['previous'][previous_i]
                else:
                    continue
            if not input == condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand = self_operand.__ixor__(input)
                return self_operand
        return ol.Null()

    def reset(self, *parameters) -> 'Frame':
        super().reset()
        self._multi_data['previous'] = []
        return self << parameters
    
class Greater(Selector):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._multi_data['previous'] = []

    def __ixor__(self, input: o.T) -> o.T:
        self._multi_data['previous'].insert(0, input)
        for condition in self._multi_data['operand']:
            if isinstance(condition, od.Previous):
                previous_i: int = condition._data
                if previous_i < len(self._multi_data['previous']):
                    condition = self._multi_data['previous'][previous_i]
                else:
                    continue
            if input > condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand = self_operand.__ixor__(input)
                return self_operand
        return ol.Null()

    def reset(self, *parameters) -> 'Frame':
        super().reset()
        self._multi_data['previous'] = []
        return self << parameters
    
class Less(Selector):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._multi_data['previous'] = []

    def __ixor__(self, input: o.T) -> o.T:
        self._multi_data['previous'].insert(0, input)
        for condition in self._multi_data['operand']:
            if isinstance(condition, od.Previous):
                previous_i: int = condition._data
                if previous_i < len(self._multi_data['previous']):
                    condition = self._multi_data['previous'][previous_i]
                else:
                    continue
            if input < condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand = self_operand.__ixor__(input)
                return self_operand
        return ol.Null()

    def reset(self, *parameters) -> 'Frame':
        super().reset()
        self._multi_data['previous'] = []
        return self << parameters
    
class GreaterEqual(Selector):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._multi_data['previous'] = []

    def __ixor__(self, input: o.T) -> o.T:
        self._multi_data['previous'].insert(0, input)
        for condition in self._multi_data['operand']:
            if isinstance(condition, od.Previous):
                previous_i: int = condition._data
                if previous_i < len(self._multi_data['previous']):
                    condition = self._multi_data['previous'][previous_i]
                else:
                    continue
            if input >= condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand = self_operand.__ixor__(input)
                return self_operand
        return ol.Null()

    def reset(self, *parameters) -> 'Frame':
        super().reset()
        self._multi_data['previous'] = []
        return self << parameters
    
class LessEqual(Selector):
    def __init__(self, *parameters):
        super().__init__(parameters)
        self._multi_data['previous'] = []

    def __ixor__(self, input: o.T) -> o.T:
        self._multi_data['previous'].insert(0, input)
        for condition in self._multi_data['operand']:
            if isinstance(condition, od.Previous):
                previous_i: int = condition._data
                if previous_i < len(self._multi_data['previous']):
                    condition = self._multi_data['previous'][previous_i]
                else:
                    continue
            if input <= condition:    # global "or" condition, only one needs to be verified as True
                self_operand = self._next_operand
                if isinstance(self_operand, Frame):
                    self_operand = self_operand.__ixor__(input)
                return self_operand
        return ol.Null()

    def reset(self, *parameters) -> 'LessEqual':
        super().reset()
        self._multi_data['previous'] = []
        return self << parameters
    
class Get(Left):
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(input, o.Operand):
            parameter = input
            for single_parameter in self._multi_data['operand']:
                parameter %= single_parameter
            return super().__ixor__(parameter)
        return super().__ixor__(input)
        
class Set(Left):
    def __init__(self, operand: o.Operand = None):
        super().__init__(operand)

    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(input, o.Operand):
            return super().__ixor__(input << self._multi_data['operand'])
        return super().__ixor__(input)
        
class Push(Left):
    def __init__(self, operand: o.Operand = None):
        super().__init__(operand)

    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(input, o.Operand):
            return super().__ixor__(self._multi_data['operand'] >> input)
        return super().__ixor__(input)

class Add(Left):
    def __init__(self, operand: any = 1):
        super().__init__(operand)

    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input + self._multi_data['operand'])

class Subtract(Left):
    def __init__(self, operand: any = 1):
        super().__init__(operand)

    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input - self._multi_data['operand'])

class Multiply(Left):
    def __init__(self, operand: any = 1):
        super().__init__(operand)

    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input * self._multi_data['operand'])

class Divide(Left):
    def __init__(self, operand: any = 1):
        super().__init__(operand)

    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input / self._multi_data['operand'])

# 3. OPERAND FILTERS (PROCESSES THE OPERAND DATA WITHOUT WRITING/ALTERING THE SOURCE OPERAND)

class Right(Frame):
    def __init__(self, operand: any = None):
        super().__init__()
        self._multi_data['operand'] = 0 if operand is None else operand   # NO COPY !!

class WrapR(Right):
    def __init__(self, wrapper: o.Operand = None):
        super().__init__(wrapper)

    def __ixor__(self, input: o.T) -> o.T:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand = self_operand.__ixor__(input)
        match self_operand:
            case o.Operand():
                match self._multi_data['operand']:
                    case o.Operand():   wrapped_operand = self._multi_data['operand'].copy() << self_operand
                    case None:          wrapped_operand = ol.Null()
                    case _:             wrapped_operand = self._multi_data['operand']
            case _:
                match self._multi_data['operand']:
                    case o.Operand():   wrapped_operand = self._multi_data['operand'].copy() << self_operand
                    case None:          wrapped_operand = ol.Null()
                    case _:             wrapped_operand = self._multi_data['operand']
        if isinstance(wrapped_operand, o.Operand):
            if isinstance(self_operand, o.Operand):
                wrapped_operand._set = self_operand._set
            else:
                wrapped_operand._set = True
        return wrapped_operand

class GetR(Right):
    def __init__(self, operand: o.Operand = None):
        super().__init__(operand)

    def __ixor__(self, input: o.T) -> o.T:
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand = self_operand.__ixor__(input)
        extracted_data = self_operand
        if isinstance(self_operand, o.Operand):
            extracted_data = self_operand % self._multi_data['operand']
            extracted_data._set = self_operand._set # Set status has to be kept
        return extracted_data

# 4. OPERAND EDITORS (ALTERS THE SOURCE OPERAND DATA)

class OperandEditor(Frame):
    def __init__(self):
        super().__init__()
