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
    Frames are chained with other Frames with the `**` operator. A `Frame` is a read-only class!

    Parameters
    ----------
    None : Frame doesn't have any self parameters.
    """
    def __init__(self, *parameters):
        import operand_container as oc
        super().__init__()
        # These parameters replace the homologous Operand's ones
        self._next_operand: any         = o.Operand()
        self._parameters: tuple         = parameters
        self._named_parameters: dict    = {}
        self._inside_container: oc.Container = None
        self._root_frame: bool = True
        self._index_iterator: Type = None
        
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
            case od.Pipe():
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
            return self._parameters == other._parameters and self._named_parameters == other._named_parameters
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
        serialization["parameters"]["multi_data"] = self.serialize(self._named_parameters)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "multi_data" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._named_parameters = self.deserialize(serialization["parameters"]["multi_data"])
        return self
    
    def __lshift__(self, operand: any) -> Self:
        # Frame class IS a Read-only class
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
        self.deep_reset(self._named_parameters)
        return self << parameters
    
    def clear(self, *parameters) -> 'Frame':
        # Frame class IS a Read-only class
        return self
    

class Left(Frame):  # LEFT TO RIGHT
    """`Frame -> Left`

    The `Left` frames are processed from left to right in the framing chain made with the `**` operator.

    Parameters
    ----------
    Any(None) : Data used in the framing process.
    """
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
            if isinstance(self_operand, o.Operand): # Strict operand, the default (validated as true)
                self_operand._set = True
        elif isinstance(self_operand, o.Operand) and not self_operand._set:
            self_operand = self_operand.copy(input) # Has to use a copy of the frame operand
            self_operand._set = True
        elif isinstance(self_operand, (int, float, Fraction)):
            if isinstance(input, (int, float, Fraction)):
                self_operand = type(self_operand)(input)
            elif isinstance(input, o.Operand):
                self_operand = input % self_operand
            
        return self_operand


class Input(Left):
    """`Frame -> Left -> Input`

    By default a `Frame` uses the data being passed trough it as input, \
        with this `Frame` it's possible to inject a different `Operand` as input.

    Parameters
    ----------
    Any(None) : The `Operand` to be used as input.
    """
    def __init__(self, input: any = None):
        super().__init__()
        self._named_parameters['input'] = input

    def __ixor__(self, input: o.T) -> o.T:
        import operand_container as oc
        import operand_chaos as ch
        self._increment_index(Input)
        if isinstance(self._named_parameters['input'], oc.Container):
            if self._named_parameters['input'].len() > 0:
                item = self._named_parameters['input'][(self._index - 1) % self._named_parameters['input'].len()]
                return super().__ixor__(item)
            return super().__ixor__(ol.Null())
        if isinstance(self._named_parameters['input'], ch.Chaos):
            actual_chaos: ch.Chaos = self._named_parameters['input'] * 0    # Makes a copy without iterating
            self._named_parameters['input'] *= 1    # In order to not result in a copy of Chaos
            return super().__ixor__(actual_chaos)
        return super().__ixor__(self._named_parameters['input'])


class Previous(Left):
    """`Frame -> Left -> Previous`

    Represents the previous processed `Element`, returns `Null()` for the first one.

    Parameters
    ----------
    Any(None) : Any type of data.
    """
    def __init__(self, previous: any = None):
        super().__init__()
        self._named_parameters['previous'] = previous

    def __ixor__(self, input: o.T) -> o.T:
        if self._named_parameters['previous'] is None:
            self._named_parameters['previous'] = input
            return ol.Null()
        parameter: Any = super().__ixor__(self._named_parameters['previous'])
        self._named_parameters['previous'] = input
        return parameter


class PassThrough(Left):
    """`Frame -> Left -> PassThrough`

    Allows to pass the input trough an `Operand` with `>>` before sending it to the next `Frame`.

    Parameters
    ----------
    Operand(None) : The `Operand` to be used as pass through.
    """
    def __init__(self, operand: o.Operand = ol.Null()):
        super().__init__()
        self._named_parameters['operand'] = operand

    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(self._named_parameters['operand'], o.Operand):
            return super().__ixor__(input >> self._named_parameters['operand'])
        return super().__ixor__(input)

class SendTo(Left):
    """`Frame -> Left -> SendTo`

    Allows to send the input to an `Operand` with `>>` before sending it to the next `Frame`.
    The difference with `PassThrough` is that the original input is still the one sent to the next `Frame`.

    Parameters
    ----------
    Operand(None) : The `Operand` to send to, like a `Print` for instance.
    """
    def __init__(self, operand: o.Operand = ol.Null()):
        super().__init__()
        self._named_parameters['operand'] = operand

    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(self._named_parameters['operand'], o.Operand):
            input >> self._named_parameters['operand']
        return super().__ixor__(input)

class Choice(Left):
    """`Frame -> Left -> Choice`

    A `Choice` is a group of items that can be chosen from based on the input as the chooser.

    Parameters
    ----------
    Any(None) : Multiple items to be chosen.
    """
    def __ixor__(self, input: o.T) -> o.T:
        if len(self._parameters) > 0:
            choice: int = 0
            match input:
                case int() | float() | Fraction():
                    choice = int(input)
                case o.Operand():
                    choice_candidate = input % int()
                    if isinstance(choice_candidate, int):
                        choice = choice_candidate
            choice %= len(self._parameters)
            return super().__ixor__(self._parameters[choice])
        return super().__ixor__(ol.Null())

class Pick(Left):
    """`Frame -> Left -> Pick`

    A `Pick` is a group of items that can be picketed from based on the input as the picker.
    The difference with `Choice` is that each picked item becomes unavailable until all items are picked.

    Parameters
    ----------
    Any(None) : Multiple items to be picketed.
    """
    def __init__(self, *parameters):
        super().__init__(*parameters)
        self._named_parameters['pick'] = list(self._parameters)

    def __ixor__(self, input: o.T) -> o.T:
        if len(self._parameters) > 0:
            if len(self._named_parameters['pick']) == 0:
                self._named_parameters['pick'] = list(self._parameters)
            choice: int = 0
            match input:
                case int() | float() | Fraction():
                    choice = int(input)
                case o.Operand():
                    choice_candidate = input % int()
                    if isinstance(choice_candidate, int):
                        choice = choice_candidate
            choice %= len(self._named_parameters['pick'])
            return super().__ixor__(self._named_parameters['pick'].pop(choice))
        return super().__ixor__(ol.Null())

class CountDown(Left):
    """`Frame -> Left -> CountDown`

    A `CountDown` is a group of count down numbers that work as selectors when they reach 0.
    In `CountDown(5, 1, 5)**Choice(O3, O4, O5)` the value `O4` will be chosen in the next call.

    Parameters
    ----------
    int(None) : Integers to be used as starting count downs.
    """
    def __init__(self, *parameters):
        super().__init__(*parameters)
        self._count_down: list = []
        for single_parameter in self._parameters:
            if not isinstance(single_parameter, int):
                single_parameter = -1
            self._count_down.append(single_parameter)
        self._named_parameters['count_down'] = tuple(self._count_down)  # tuple will be used as data reset

    def __ixor__(self, input: o.T) -> o.T:
        pick_choices: any = ol.Null()
        if len(self._named_parameters['count_down']) > 0:
            picker: int = 0
            match input:
                case int() | float() | Fraction():
                    picker = int(input)
                case o.Operand():
                    picker_candidate = input % int()
                    if isinstance(picker_candidate, int):
                        picker = picker_candidate
            picker %= len(self._named_parameters['count_down'])
            if self._count_down[picker] > 0:
                self._count_down[picker] -= 1
            closest_picker: int = picker
            closest_place: int  = self._count_down[picker]
            for index, value in enumerate(self._named_parameters['count_down']):
                if self._count_down[index] < closest_place and value >= 0:
                    closest_picker = index
                    closest_place = self._count_down[index]
            pick_choices = closest_picker
            self._count_down[pick_choices] += self._named_parameters['count_down'][pick_choices] # adds position debt
            # Trim base, move closer (avoids astronomical distances)
            for index, _ in enumerate(self._named_parameters['count_down']):
                self._count_down[index] -= max(0, closest_place - 1)
        return super().__ixor__(pick_choices)

class Frequency(CountDown):
    """`Frame -> Left -> CountDown -> Frequency`

    A `Frequency` sets a count down based on the intended frequency for each placed item.
    In `Frequency(1, 4, 2, 1)**Choice(eight, quarter, dotted_eight, dotted_quarter)` the `quarter` notes will be chosen \
        four times as much as `eight` ones.

    Parameters
    ----------
    int(None) : Integers to be used as choosing frequency.
    """
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
        super().__init__(*until_list)   # Saves a CountDown as self._multi_data['operand']

class Formula(Left):
    """`Frame -> Left -> Formula`

    A `Formula` processes the input data with the given function and passes its result to the next `Frame`.

    Parameters
    ----------
    Callable(None) : A function to be used to process the input like `Formula(lambda n: (n * 5 + 4) % 3)`.
    """
    def __init__(self, operation: Callable[[Tuple[Any, ...]], Any] = None):
        super().__init__()
        self._named_parameters['operand'] = operation

    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(self._named_parameters['operand'](input))
    
class Iterate(Left):
    """`Frame -> Left -> Iterate`

    An `Iterate` returns a series of values much alike the Python `range` method, where this
    input defines the type of values too. Intended to be used with Clips.

    Args:
        start (int): Starting iteration value.
        step (int): Increment amount for each iteration.
    
    Examples
    --------
    Gets the Staff Steps per Measure:
    >>> notes = Note() * 4
    >>> notes << Iterate(2)**Degree()
    >>> notes[0] % Pitch() % int() >> Print()
    2
    >>> notes[3] % Pitch() % int() >> Print()
    5
    """
    def __init__(self, start: int = 0, step: int = 1):
        super().__init__()
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
        self._named_parameters['iterator'] = iterator

    def __ixor__(self, input: o.T) -> o.T:
        import operand_chaos as ch
        self._increment_index(Iterate)
        if isinstance(input, ch.Chaos):
            if self._named_parameters['iterator']['current'] == self._named_parameters['iterator']['start']:
                input *= self._named_parameters['iterator']['start']
            self_operand = super().__ixor__( input )
            input *= self._named_parameters['iterator']['step']
        else:
            self_operand = super().__ixor__(
                self.deep_copy(self._named_parameters['iterator']['current'])
            )
        # iterates whenever called
        self._named_parameters['iterator']['current'] += self._named_parameters['iterator']['step']
        return self_operand

class Drag(Left):
    """`Frame -> Left -> Drag`

    A `Drag` works similarly the a drag in Excel\xa9, where the first inputted `Operand`'s extracted item is the one bring dragged.
    In `Nth(6, 7, 8)**Drag(Degree())` the `Degree()` of the first `Operand` is propagated to the next ones.

    Parameters
    ----------
    Any(None) : The item to be get and to drag along.
    """
    def __init__(self, *parameters):
        super().__init__(*parameters)
        self._first_parameter = None

    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(input, o.Operand):
            if self._first_parameter is None:
                self._first_parameter = input
                for single_parameter in self._parameters:
                    self._first_parameter %= single_parameter
            return super().__ixor__(self._first_parameter)
        return super().__ixor__(input)


class Mux(Left):
    """`Frame -> Left -> Mux`

    A `Mux` does a multiplexing of multiple elements into single ones, allowing this way a more versatile way of flow.

    Parameters
    ----------
    Any(None) : A set of integers by which the elements will be multiplexed by.
    """
    def __init__(self, *parameters):
        self._last_parameter: Any = None
        validated_parameters: list[int] = []
        for param in parameters:
            if isinstance(param, int):
                validated_parameters.append(param)
        self._full_range: int = sum(validated_parameters)
        super().__init__(*validated_parameters)

    def __ixor__(self, input: o.T) -> o.T:
        final_remainder: int = 0
        tamed_index: int = self._index % self._full_range
        for multiplex in self._parameters:
            if tamed_index // multiplex == 0:
                final_remainder = tamed_index % multiplex
                break
            tamed_index -= multiplex
        if final_remainder == 0:
            self._last_parameter = super().__ixor__(input)
        self._increment_index(Mux)
        return self._last_parameter


class Foreach(Left):
    """`Frame -> Left -> Foreach`

    A `Foreach` cycles through a set of items and returns to the first one whenever reaches the end of it.

    Parameters
    ----------
    Any(None) : The set of items to loop through.
    """
    def __init__(self, *parameters):
        validated_parameters: list = []
        for param in parameters:
            if isinstance(param, (range, list, tuple)):
                validated_parameters.extend(param)
            else:
                validated_parameters.append(param)
        super().__init__(*validated_parameters)

    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Foreach)
        operand_len: int = len(self._parameters)
        if operand_len > 0:    # In case it its own parameters to iterate trough
            input = self._parameters[(self._index - 1) % operand_len]
            return super().__ixor__(input)
        return ol.Null()

class Cycle(Foreach):
    """`Frame -> Left -> Foreach -> Cycle`

    A `Cycle` is a Foreach that cycles through a set of items but doesn't return to the first one when it reaches the end of it.

    Parameters
    ----------
    Any(None) : The set of items to loop through only once.
    """
    def __ixor__(self, input: o.T) -> o.T:
        operand_len: int = len(self._parameters)
        if self._index < operand_len:   # Does only a single loop!
            return super().__ixor__(input)
        return ol.Null()


class InputFilter(Left):
    """`Frame -> Left -> InputFilter`

    An `InputFilter` only passes the input to the next `Frame` if its criteria is met.

    Parameters
    ----------
    None : `InputFilter` doesn't have parameters to be set.
    """
    pass

class All(InputFilter):
    """`Frame -> Left -> InputFilter -> All`

    An `All` lets any input to pass to the next `Frame`.

    Parameters
    ----------
    None : `All` doesn't have parameters to be set.
    """
    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input)

class First(InputFilter):
    """`Frame -> Left -> InputFilter -> First`

    A `First` only lets the first `Element` in a `Clip` to pass to the next `Frame`.

    Parameters
    ----------
    None : `First` doesn't have parameters to be set.
    """
    def __ixor__(self, input: o.T) -> o.T:
        import operand_container as oc
        if isinstance(self._inside_container, oc.Container):
            first_item = self._inside_container.first()
            if input is first_item:    # Selected first call to pass
                if isinstance(self._next_operand, Frame):
                    return self._next_operand.__xor__(input)
                return self._next_operand
        return ol.Null()

class Last(InputFilter):
    """`Frame -> Left -> InputFilter -> Last`

    A `Last` only lets the last `Element` in a `Clip` to pass to the next `Frame`.

    Parameters
    ----------
    None : `Last` doesn't have parameters to be set.
    """
    def __ixor__(self, input: o.T) -> o.T:
        import operand_container as oc
        if isinstance(self._inside_container, oc.Container):
            last_item = self._inside_container.last()
            if input is last_item:    # Selected first call to pass
                if isinstance(self._next_operand, Frame):
                    return self._next_operand.__xor__(input)
                return self._next_operand
        return ol.Null()

class Odd(InputFilter):
    """`Frame -> Left -> InputFilter -> Odd`

    An `Odd` only lets odd nth inputs to be passed to the next `Frame`.

    Parameters
    ----------
    None : `Odd` doesn't have parameters to be set.
    """
    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Odd)
        if self._index % 2 == 1:    # Selected to pass
            if isinstance(self._next_operand, Frame):
                return self._next_operand.__xor__(input)
            return self._next_operand
        else:
            return ol.Null()

class Even(InputFilter):
    """`Frame -> Left -> InputFilter -> Even`

    An `Even` only lets even nth inputs to be passed to the next `Frame`.

    Parameters
    ----------
    None : `Even` doesn't have parameters to be set.
    """
    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Even)
        if self._index % 2 == 0:
            if isinstance(self._next_operand, Frame):
                return self._next_operand.__xor__(input)
            return self._next_operand
        else:
            return ol.Null()

class Every(InputFilter):
    """`Frame -> Left -> InputFilter -> Every`

    An `Every` only lets every other nth inputs to be passed to the next `Frame`.

    Args:
        nth (int): The nth input, as in every other 2nd or 4th.
    """
    def __init__(self, nth: int = 4):
        super().__init__()
        self._named_parameters['nths'] = nth

    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Every)
        if self._named_parameters['nths'] > 0 and self._index % self._named_parameters['nths'] == 0:
            if isinstance(self._next_operand, Frame):
                return self._next_operand.__xor__(input)
            return self._next_operand
        else:
            return ol.Null()

class Nth(InputFilter):
    """`Frame -> Left -> InputFilter -> Nth`

    A `Nth` only lets the nth inputs to be passed to the next `Frame`.
    In `Nth(1, 6)**Duration(1/1)` sets the 1st and 6th `Clip` elements to 1 as note value.

    Parameters
    ----------
    int(None) : The set of nths to pass to the next `Frame`.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._named_parameters['parameters'] = parameters

    def __ixor__(self, input: o.T) -> o.T:
        self._increment_index(Nth)
        if self._index in self._named_parameters['parameters']:
            if isinstance(self._next_operand, Frame):
                return self._next_operand.__xor__(input)
            return self._next_operand
        else:
            return ol.Null()

class InputType(InputFilter):
    """`Frame -> Left -> InputFilter -> InputType`

    An `InputType` only lets specified types of inputs to be passed to the next `Frame`.

    Parameters
    ----------
    type(None) : A single or multiple types can be set as accepted ones.
    """
    def __ixor__(self, input: o.T) -> o.T:
        for operand_class in self._parameters:
            if isinstance(input, operand_class):
                return super().__ixor__(input)
        return super().__ixor__(ol.Null())


class BasicComparison(InputFilter):
    """`Frame -> Left -> InputFilter -> BasicComparison`

    A `BasicComparison` checks if the input meets a basic comparison condition before being passed to the next `Frame`.

    Parameters
    ----------
    Any(None) : One or more conditions where **all** need to be met.
    """
    def __init__(self, *parameters):
        super().__init__(*parameters)
        self._named_parameters['previous'] = []

    def __ixor__(self, input: o.T) -> o.T:
        for condition in self._parameters:
            if not self._compare(input, condition): # Where the comparison is made
                return ol.Null()
        self_operand = self._next_operand
        if isinstance(self_operand, Frame):
            self_operand = self_operand.__ixor__(input)
        return self_operand

    @staticmethod
    def _compare(input: Any, condition: Any) -> bool:
        return True

    def reset(self, *parameters) -> Self:
        super().reset()
        self._named_parameters['previous'] = []
        return self << parameters

class Equal(BasicComparison):
    """`Frame -> Left -> InputFilter -> BasicComparison -> Equal`

    An `Equal` checks if the input is equal to **all** the conditions before being passed to the next `Frame`.

    Parameters
    ----------
    Any(None) : One or more conditions where **all** need to be met as equal (`==`).
    """
    @staticmethod
    def _compare(input: Any, condition: Any) -> bool:
        return input == condition

class NotEqual(BasicComparison):
    """`Frame -> Left -> InputFilter -> BasicComparison -> NotEqual`

    A `NotEqual` checks if the input is NOT equal to **all** the conditions before being passed to the next `Frame`.

    Parameters
    ----------
    Any(None) : One or more conditions where **all** need to be met as NOT equal (`not ==`).
    """
    @staticmethod
    def _compare(input: Any, condition: Any) -> bool:
        return not input == condition

class Greater(BasicComparison):
    """`Frame -> Left -> InputFilter -> BasicComparison -> Greater`

    A `Greater` checks if the input is greater to **all** the conditions before being passed to the next `Frame`.

    Parameters
    ----------
    Any(None) : One or more conditions where **all** need to be met as greater (`>`).
    """
    @staticmethod
    def _compare(input: Any, condition: Any) -> bool:
        return input > condition

class Less(BasicComparison):
    """`Frame -> Left -> InputFilter -> BasicComparison -> Less`

    A `Less` checks if the input is less to **all** the conditions before being passed to the next `Frame`.

    Parameters
    ----------
    Any(None) : One or more conditions where **all** need to be met as less (`<`).
    """
    @staticmethod
    def _compare(input: Any, condition: Any) -> bool:
        return input < condition

class GreaterOrEqual(BasicComparison):
    """`Frame -> Left -> InputFilter -> BasicComparison -> GreaterOrEqual`

    A `GreaterOrEqual` checks if the input is greater or equal to **all** the conditions before being passed to the next `Frame`.

    Parameters
    ----------
    Any(None) : One or more conditions where **all** need to be met as greater or equal (`>=`).
    """
    @staticmethod
    def _compare(input: Any, condition: Any) -> bool:
        return input >= condition

class LessOrEqual(BasicComparison):
    """`Frame -> Left -> InputFilter -> BasicComparison -> LessOrEqual`

    A `LessOrEqual` checks if the input is less or equal to **all** the conditions before being passed to the next `Frame`.

    Parameters
    ----------
    Any(None) : One or more conditions where **all** need to be met as less or equal (`<=`).
    """
    @staticmethod
    def _compare(input: Any, condition: Any) -> bool:
        return input <= condition


class Get(Left):
    """`Frame -> Left -> Get`

    A `Get` does an `input % item` and passes it to the next `Frame`.

    Parameters
    ----------
    Any(None) : An item to get from the input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(input, o.Operand):
            parameter = input
            for single_parameter in self._parameters:
                parameter %= single_parameter
            return super().__ixor__(parameter)
        return super().__ixor__(input)

class DeepCopy(Left):
    """`Frame -> Left -> DeepCopy`

    A `DeepCopy` makes a deep copy of the input and passes it to the next `Frame`.

    Parameters
    ----------
    None : This `Frame` has no parameters.
    """
    def __ixor__(self, input: o.T) -> o.T:
        input_duplication = self.deep_copy(input)
        return super().__ixor__(input_duplication)

class Inject(Left):
    """`Frame -> Left -> Inject`

    An `Inject` sets the input with extra parameters before passing it to the next `Frame`.

    Parameters
    ----------
    None : This `Frame` has no parameters.
    """
    pass

class Set(Inject):
    """`Frame -> Left -> Inject -> Set`

    A `Set` does a `<<` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    Any(None) : A series of parameters to be injected into the input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(input, o.Operand):
            for single_parameter in self._parameters:
                input << single_parameter
        return super().__ixor__(input)
        
class Push(Inject):
    """`Frame -> Left -> Inject -> Push`

    A `Push` does a `>>` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    Any(None) : A series of parameters to be push into the input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        if isinstance(input, o.Operand):
            for single_parameter in self._parameters:
                single_parameter >> input
        return super().__ixor__(input)


class BasicOperation(Left):
    """`Frame -> Left -> BasicOperation`

    A `BasicOperation` does a basic operation like `+` or `/` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    None : This `Frame` has no parameters.
    """
    def __init__(self, parameter: any = 1):
        super().__init__()
        self._named_parameters['parameter'] = parameter

class Add(BasicOperation):
    """`Frame -> Left -> BasicOperation -> Add`

    An `Add` does a basic `+` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    int(1) : A parameter to do an `+` on input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input + self._named_parameters['parameter'])

class Subtract(BasicOperation):
    """`Frame -> Left -> BasicOperation -> Subtract`

    A `Subtract` does a basic `-` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    int(1) : A parameter to do an `-` on input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input - self._named_parameters['parameter'])

class Multiply(BasicOperation):
    """`Frame -> Left -> BasicOperation -> Multiply`

    A `Multiply` does a basic `*` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    int(1) : A parameter to do an `*` on input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input * self._named_parameters['parameter'])

class Divide(BasicOperation):
    """`Frame -> Left -> BasicOperation -> Divide`

    A `Divide` does a basic `/` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    int(1) : A parameter to do an `/` on input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        return super().__ixor__(input / self._named_parameters['parameter'])


class Right(Frame):  # RIGHT TO LEFT
    """`Frame -> Right`

    The `Right` frames are processed from right to left in the framing chain made with the `**` operator.

    Parameters
    ----------
    Any(None) : Data used in the framing process.
    """
    def __ixor__(self, input: o.T) -> o.T:
        right_input = self._next_operand
        if isinstance(right_input, Frame):
            # ByPasses a Right frame
            right_input = right_input.__ixor__(input)
        if isinstance(right_input, o.Operand) and not right_input._set:
            right_input = right_input.copy(input) # Has to use a copy of the frame operand
            right_input._set = True
        return right_input

class WrapR(Right):
    """`Frame -> Right -> WrapR`

    A `WrapR` wraps the right side input with an `Operand` set as parameter before returning it.

    Parameters
    ----------
    Operand(None) : `Operand` to wrap the right side input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        wrapped_right_input = super().__ixor__(input)
        for single_wrapper in self._parameters:
            if isinstance(single_wrapper, o.Operand):
                wrapped_right_input = single_wrapper.copy(wrapped_right_input)
                wrapped_right_input._set = True
        return wrapped_right_input

class GetR(Right):
    """`Frame -> Right -> GetR`

    A `GetR` extracts the right side input parameter with `%` before returning it.

    Parameters
    ----------
    Any(None) : Item to extract from the right side input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        extracted_data = super().__ixor__(input)
        for single_parameter in self._parameters:
            if isinstance(extracted_data, o.Operand):
                extracted_data %= single_parameter
        if isinstance(extracted_data, o.Operand):
            extracted_data._set = extracted_data._set # Set status has to be kept
        return extracted_data

class BasicOperationR(Right):
    """`Frame -> Right -> BasicOperationR`

    A `BasicOperationR` does a basic operation like `+` or `/` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    None : This `Frame` has no parameters.
    """
    def __init__(self, parameter: any = 1):
        super().__init__()
        self._named_parameters['parameter'] = parameter

class AddR(BasicOperationR):
    """`Frame -> Right -> BasicOperationR -> AddR`

    An `AddR` does a basic `+` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    int(1) : A parameter to do an `+` on input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        extracted_data = super().__ixor__(input)
        if isinstance(extracted_data, list):
            for index, _ in enumerate(extracted_data):
                extracted_data[index] += self._named_parameters['parameter']
        else:
            extracted_data += self._named_parameters['parameter']
        if isinstance(extracted_data, o.Operand):
            extracted_data._set = extracted_data._set # Set status has to be kept
        return extracted_data

class SubtractR(BasicOperationR):
    """`Frame -> Right -> BasicOperationR -> SubtractR`

    A `SubtractR` does a basic `-` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    int(1) : A parameter to do an `-` on input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        extracted_data = super().__ixor__(input)
        if isinstance(extracted_data, list):
            for index, _ in enumerate(extracted_data):
                extracted_data[index] -= self._named_parameters['parameter']
        else:
            extracted_data -= self._named_parameters['parameter']
        if isinstance(extracted_data, o.Operand):
            extracted_data._set = extracted_data._set # Set status has to be kept
        return extracted_data

class MultiplyR(BasicOperationR):
    """`Frame -> Right -> BasicOperationR -> MultiplyR`

    A `MultiplyR` does a basic `*` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    int(1) : A parameter to do an `*` on input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        extracted_data = super().__ixor__(input)
        if isinstance(extracted_data, list):
            for index, _ in enumerate(extracted_data):
                extracted_data[index] *= self._named_parameters['parameter']
        else:
            extracted_data *= self._named_parameters['parameter']
        if isinstance(extracted_data, o.Operand):
            extracted_data._set = extracted_data._set # Set status has to be kept
        return extracted_data

class DivideR(BasicOperationR):
    """`Frame -> Right -> BasicOperationR -> DivideR`

    A `DivideR` does a basic `/` on the input before passing it to the next `Frame`.

    Parameters
    ----------
    int(1) : A parameter to do an `/` on input.
    """
    def __ixor__(self, input: o.T) -> o.T:
        extracted_data = super().__ixor__(input)
        if isinstance(extracted_data, list):
            for index, _ in enumerate(extracted_data):
                extracted_data[index] /= self._named_parameters['parameter']
        else:
            extracted_data /= self._named_parameters['parameter']
        if isinstance(extracted_data, o.Operand):
            extracted_data._set = extracted_data._set # Set status has to be kept
        return extracted_data

