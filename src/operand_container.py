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
from typing import Self, cast

from fractions import Fraction
import json
import enum
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
import operand_chaos as ch

# Define ANSI escape codes for colors
RED = "\033[91m"
RESET = "\033[0m"
        
try:
    # pip install matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Button
except ImportError:
    print(f"{RED}Error: The 'matplotlib.pyplot' library is not installed.{RESET}")
    print("Please install it by running 'pip install matplotlib'.")
try:
    # pip install numpy
    import numpy as np
except ImportError:
    print(f"{RED}Error: The 'numpy' library is not installed.{RESET}")
    print("Please install it by running 'pip install numpy'.")
        

class Container(o.Operand):
    def __init__(self, *operands):
        super().__init__()
        self._items: list = []
        self._items_iterator: int = 0
        self._upper_container: Container = self
        for single_operand in operands:
            self << single_operand
        
    def __getitem__(self, index: int) -> any:
        return self._items[index]
    
    def __setitem__(self, index, value) -> Self:
        self._items[index] = value
        return self

    def __iter__(self) -> Self:
        return self
    
    def __next__(self) -> any:
        if self._items_iterator < len(self._items):
            item = self._items[self._items_iterator]
            self._items_iterator += 1
            return item  # It's the data that should be returned
        else:
            self._items_iterator = 0   # Reset to 0 when limit is reached
            raise StopIteration

    def _insert(self, items: list, before_item: any = None) -> Self:
        if self is not self._upper_container:
            self._upper_container._insert(items, before_item)
        insert_at: int = 0                  # By default works as insert
        if before_item is not None:
            for index, single_item in enumerate(self._items):
                # if single_item == before_item:
                if single_item is before_item:
                    insert_at = index       # Before the item
                    break
        self._items = self._items[:insert_at] + items + self._items[insert_at:]
        return self

    def _append(self, items: list, after_item: any = None) -> Self:
        if self is not self._upper_container:
            self._upper_container._append(items, after_item)
        append_at: int = len(self._items)   # By default works as append
        if after_item is not None:
            for index, single_item in enumerate(self._items):
                # if single_item == after_item:
                if single_item is after_item:
                    append_at = index + 1   # After the item
                    break
        self._items = self._items[:append_at] + items + self._items[append_at:]
        return self

    def _delete(self, items: list) -> Self:
        if self is not self._upper_container:
            self._upper_container._delete(items)
        self._items = [
            single_item for single_item in self._items
            if single_item not in items
        ]
        return self

    def _replace(self, old_item: Any = None, new_item: Any = None) -> Self:
        if self is not self._upper_container:
            self._upper_container._replace(old_item, new_item)
        for index, item in enumerate(self._items):
            if old_item is item:
                self._items[index] = new_item
        return self

    def _swap(self, left_item: Any = None, right_item: Any = None) -> Self:
        if self is not self._upper_container:
            self._upper_container._swap(left_item, right_item)
        left_index: int = None
        for index, item in enumerate(self._items):
            if left_item is item:
                left_index = index
        right_index: int = None
        for index, item in enumerate(self._items):
            if right_item is item:
                right_index = index
        if left_index and right_index:
            temp_item: Any = self._items[right_index]
            self._items[right_index] = self._items[left_index]
            self._items[left_index] = temp_item
        return self

    def _sort_position(self) -> Self:
        # Container sort position does nothing
        # Only applicable to Clip and Song
        return self


    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, because a Container has
        only one type of Parameters it should be used in conjugation with list()
        to extract the Parameter list.

        Examples
        --------
        >>> clip = Track(Note("A"), Note("B"))
        >>> clip % list() >> Print()
        [<operand_element.Note object at 0x0000017B5F3FF6D0>, <operand_element.Note object at 0x0000017B5D3B36D0>]
        """
        match operand:
            case self.__class__():
                return self.copy()
            case od.DataSource():
                match operand._data:
                    case Container():
                        return self
                    case list():
                        return [
                            item for item in self._items
                        ]
                    case _:
                        return super().__mod__(operand)
            case Container():
                return self.copy()
            case list():
                return [
                    self.deep_copy(item) for item in self._items
                ]
            case int():
                return self.len()
            case od.Next():
                self._index += operand % int() - 1
                item: any = self._items[self._index % len(self._items)]
                self._index += 1
                self._index %= len(self._items)
                return od.Next(item)
            case od.Previous():
                self._index -= operand % int()
                self._index %= len(self._items)
                item: any = self._items[self._index]
                return od.Previous(item)
            case _:
                return super().__mod__(operand)

    def len(self) -> int:
        return len(self._items)

    def first(self) -> Any:
        """
        Gets the first Item accordingly to it's Position on the Staff.

        Args:
            None

        Returns:
            Item: The first Item of all Items.
        """
        first_item: Any = None
        if self.len() > 0:
            first_item = self._items[0]
        return first_item

    def last(self) -> Any:
        """
        Gets the last Item accordingly to it's Position on the Staff.

        Args:
            None

        Returns:
            Item: The last Item of all Items.
        """
        last_item: Any = None
        if self.len() > 0:
            last_item = self._items[-1]
        return last_item

    def __eq__(self, other: any) -> bool:
        import operand_selection as os
        match other:
            case Container():
                return self._items == other._items
            case os.Selection():
                return other == self
            case od.Conditional():
                return other == self
        if not isinstance(other, ol.Null):
            return self % other == other
        # When comparing lists containing objects in Python using the == operator,
        # Python will call the __eq__ method on the objects if it is defined,
        # rather than comparing their references directly.
        # If the __eq__ method is not defined for the objects, then the default behavior
        # (which usually involves comparing object identities, like references,
        # using the is operator) will be used.
        return False

    def __lt__(self, other: any) -> bool:
        return self % other < other

    def __gt__(self, other: any) -> bool:
        return self % other > other

    def getPlaylist(self, position: ra.Position = None) -> list[dict]:
        return []

    def getMidilist(self, position: ra.Position = None) -> list[dict]:
        return []

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["items"] = self.serialize(self._items)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "items" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._items = self.deserialize(serialization["parameters"]["items"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Container():
                super().__lshift__(operand)
                self._items = self.deep_copy( operand._items )
                # COPY THE SELF OPERANDS RECURSIVELY
                self._next_operand = self.deep_copy(operand._next_operand)
            case od.DataSource():
                match operand._data:
                    case list():
                        for item in operand._data:
                            self._items.append( item )
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._items = [
                    self.deep_copy(item) for item in operand
                ]
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case of.Frame():
                operand._set_inside_container(self)
                for item in self._items:
                    item << operand
            case _:
                self += operand
        return self

    # Pass trough method that always results in a Container (Self)
    def __rshift__(self, operand) -> Self:
        import operand_mutation as om
        match operand:
            case Container():
                self += operand
                return self
            case om.Mutation():
                return operand.mutate(self)
            case od.Playlist():
                operand.__rrshift__(self)
                return self
            case od.Process():
                return operand.__rrshift__(self)
            case ch.Chaos():
                return self.shuffle(operand)
        return super().__rshift__(operand)

    # Pass trough operation as last resort
    def __rrshift__(self, operand: o.T) -> o.T:
        self << operand # Left shifts remaining parameter (Pass Through)
        return operand

    # Avoids the costly copy of Container self doing +=
    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Container():
                operand_items = [
                    self.deep_copy(single_item) for single_item in operand._items
                ]
                if self.len() > 0:
                    self_last_item: any = self[-1]
                    return self._append(operand_items, self_last_item)
                return self._append(operand_items)
            case list():
                operand_items = [
                    self.deep_copy(single_item) for single_item in operand
                ]
                if len(operand_items) > 0:
                    self_last_item: any = self[-1]
                    return self._append(operand_items, self_last_item)
                return self._append(operand_items)
            case tuple():
                for single_operand in operand:
                    self += single_operand
            case of.Frame():
                operand._set_inside_container(self)
                for item in self._items:
                    item += operand
            case _:
                if self.len() > 0:
                    self_last_item: any = self[-1]
                    return self._append([ self.deep_copy(operand) ], self_last_item)
                return self._append([ self.deep_copy(operand) ])
        return self

    def __radd__(self, operand: any) -> Self:
        self_copy: Container = self.copy()
        self_copy._insert([ self.deep_copy( operand ) ])
        return self_copy

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Container():
                return self._delete(operand._items)
            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case int(): # repeat n times the last argument if any
                if len(self._items) > 0:
                    while operand > 0 and len(self._items) > 0:
                        self._items.pop()
                        operand -= 1
            case of.Frame():
                operand._set_inside_container(self)
                for item in self._items:
                    item -= operand
            case _:
                return self._delete([ operand ])
        return self

    # multiply with a scalar 
    def __imul__(self, operand: any) -> Self:
        import operand_selection as os
        match operand:
            case Container():
                pass
            case o.Operand():
                pass
            case int(): # repeat n times the self content if any
                if operand > 1:
                    items_copy: list = [
                        self.deep_copy( data ) for data in self._items
                    ]
                    while operand > 2:
                        self._items.extend(
                            self.deep_copy( data ) for data in items_copy
                        )
                        operand -= 1
                    self._items.extend( items_copy )
                elif operand == 0:
                    self._items = []
            case os.Selection():
                if operand != self:
                    self._items = []
            case ch.Chaos():
                return self.shuffle(operand.copy())
            case tuple():
                for single_operand in operand:
                    self *= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item *= operand
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case Container():
                pass
            case o.Operand():
                pass
            case int(): # split n times the self content if any
                if operand > 0:
                    many_operands = self.__class__()    # with an empty list
                    cut_len: int = self.len() // operand
                    nth_item: int = cut_len
                    while nth_item > 0:
                        many_operands._items.append(
                                self.deep_copy( self._items[cut_len - nth_item] )
                            )
                        nth_item -= 1
                    return many_operands

            # Returns an altered Container with less info (truncated info)
            case od.Getter() | od.Process():
                return self >> operand
            
            case tuple():
                for single_operand in operand:
                    self /= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item /= operand
        return self


    def __pow__(self, operand: any) -> Self:
        for item in self._items:
            if isinstance(item, o.Operand):
                item.__pow__(operand)
        return self


    def __or__(self, operand: any) -> Self:
        return self.shallow_copy().__ior__(operand)

    def __ior__(self, operand: any) -> Self:
        import operand_mutation as om
        match operand:
            case Container():
                self._items.extend( item for item in operand )
            case od.Getter() | od.Process():
                self >>= operand
            case ch.Chaos():
                self.shuffle(operand)
            case om.Mutation():
                operand.mutate(self)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                self.filter(operand, False)
        return self

    def __ror__(self, operand: any) -> Self:
        return self.__or__(operand)


    def empty_copy(self, *parameters) -> Self:
        empty_copy: Container = self.__class__()
        # COPY THE SELF OPERANDS RECURSIVELY
        if self._next_operand:
            empty_copy._next_operand = self.deep_copy(self._next_operand)
        for single_parameter in parameters:
            empty_copy << single_parameter
        return empty_copy

    def shallow_copy(self, *parameters) -> Self:
        shallow_copy: Container = self.empty_copy()
        # This copy of a list is a shallow copy, chains upper containers
        shallow_copy._upper_container = self
        # This copy of a list is a shallow copy, not a deep copy
        shallow_copy._items = self._items.copy()
        for single_parameter in parameters:
            shallow_copy << single_parameter
        return shallow_copy
    

    def process(self, input: any = None) -> Self:
        return self >> input

    def clear(self, *parameters) -> Self:
        self._items = []
        return super().clear(parameters)
    
    def erase(self, *parameters) -> Self:
        self._delete(self._items)
        for single_parameter in parameters:
            self << single_parameter
        return self
    
    def upper(self, level: int = None) -> Self:
        if self._upper_container is self:
            return self
        if isinstance(level, int):
            if level > 0:
                level -= 1
            else:
                return self
        return self._upper_container.upper(level)

    def sort(self, parameter: type = ra.Position, reverse: bool = False) -> Self:
        """
        Sorts the self list based on a given type of parameter.

        Args:
            parameter (type): The type of parameter being sorted by.

        Returns:
            Container: The same self object with the items processed.
        """
        compare = parameter()
        self._items.sort(key=lambda x: x % compare)
        if reverse:
            self._items.reverse()
        return self

    def shuffle(self, chaos: ch.Chaos = None, parameter: type = ra.Position) -> Self:
        """
        Reaffects the given parameter type in a chaotic manner.

        Args:
            chaos (ch.Chaos): An Chaos object to be used as sorter.
            parameter (type): The type of parameter being swapped around the items.

        Returns:
            Container: The same self object with the items processed.
        """
        if chaos is None or not isinstance(chaos, ch.Chaos):
            chaos = ch.SinX()
        parameters: list = []
        parameter_instance = parameter()
        for item in self._items:
            parameters.append(item % parameter_instance)   # No need to copy
        for item in self._items:
            data_index: int = chaos * 1 % int() % len(parameters)
            item << parameters[data_index]
            del parameters[data_index] # Like picking up colored balls, pop out
        return self._sort_position()

    def swap(self, probability: ra.Probability = None, chaos: ch.Chaos = None, parameter: type = ra.Position) -> Self:
        """
        Reaffects the given parameter type in a chaotic manner accordingly to a probability.

        Args:
            probability (ra.Probability): A given probability of swapping.
            chaos (ch.Chaos): An Chaos object to be used as sorter.
            parameter (type): The type of parameter being swapped around the items.

        Returns:
            Container: The same self object with the items processed.
        """
        if self.len() > 0:
            if probability is None or not isinstance(probability, ra.Probability):
                probability = ra.Probability(1/self.len()**2)
            if chaos is None or not isinstance(chaos, ch.Chaos):
                chaos = ch.SinX()
            
            parameter_instance = parameter()
            for element_i in range(self.len()):
                for element_j in range(self.len()):
                    
                    if chaos * 1 % int() \
                        % probability._rational.denominator < probability._rational.numerator:   # Make the swap

                        if isinstance(parameter_instance, od.DataSource):

                            temp_element: oe.Element = self[element_i]
                            self[element_i] = self[element_j]
                            self[element_j] = temp_element

                        else:

                            temp_parameter: any = self[element_i] % parameter_instance
                            self[element_i] << self[element_j] % parameter_instance
                            self[element_j] << temp_parameter

        return self._sort_position()

    def reverse(self) -> Self:
        """
        Reverses the self list of items.

        Args:
            None

        Returns:
            Container: The same self object with the items processed.
        """
        self_len: int = self.len()
        for operand_i in range(self_len // 2):
            tail_operand = self._items[self_len - 1 - operand_i]
            self._items[self_len - 1 - operand_i] = self._items[operand_i]
            self._items[operand_i] = tail_operand
        return self._sort_position()
    
    def recur(self, recursion: Callable = lambda d: d/2, parameter: type = ra.Duration) -> Self:
        """
        Calls the function on the successive items in a Xn+1 = Xn fashion (recursive),
        where n is the previous element and n+1 the next one.

        Args:
            recursion (Callable): recursive function.
            parameter (type): The type of parameter being processed by the recursive function.

        Returns:
            Container: The same self object with the items processed.
        """
        for item_i in range(1, self.len()):
            self._items[item_i] << recursion(self._items[item_i - 1] % parameter())
        return self._sort_position()

    def rotate(self, offset: int = 1, parameter: type = ra.Position) -> Self:
        """
        Rotates a given parameter by a given offset, by other words,
        does a displacement for each Element in the Container list of
        a chosen parameter by the offset amount.

        Args:
            a (int): The offset amount of the list index, displacement.
            b (type): The type of parameter being displaced, rotated.

        Returns:
            Container: The self object with the chosen parameter displaced.
        """
        parameters: list = []
        parameter_instance = parameter()
        if isinstance(parameter_instance, od.DataSource):
            for _ in len(self._items):
                data_index: int = offset % len(self._items)
                parameters.append(self._items[data_index])   # No need to copy
                offset += 1
            self._items = parameters
        else:
            for operand in self:
                if isinstance(operand, o.Operand):
                    parameters.append( operand % parameter_instance )
                else:
                    parameters.append( ol.Null() )
            for operand in self:
                if isinstance(operand, o.Operand):
                    operand << parameters[ offset % len(parameters) ]
                offset += 1
        return self._sort_position()

    def filter(self, condition: any, shallow_copy: bool = True) -> Self:
        """
        Filters out all items that don't met the condition (equal to).

        Args:
            parameter (any): The object to be compared with (==).

        Returns:
            Container: The same self object with the items processed.
        """
        if shallow_copy:
            shallow_copy: Container = self.shallow_copy()
            shallow_copy._items = [item for item in self._items if item == condition]
            return shallow_copy
        self._items = [item for item in self._items if item == condition]
        return self

    def dropper(self, probability: float | Fraction = 1/16, chaos: ch.Chaos = None) -> Self:
        if not isinstance(chaos, ch.Chaos):
            chaos = ch.SinX()

        probability = ra.Probability(probability)._rational
        for single_item in self._items:
            if chaos * 1 % int() % probability.denominator < probability.numerator:
                self._delete([ single_item ])

        return self
    
    def operate(self, operand: any = None, operator: str = "<<") -> Self:
        operator = operator.strip()
        match operator:
            case "<<":
                self << operand
            case "+":
                self += operand
            case "-":
                self -= operand
            case "*":
                self *= operand
            case "/":
                self /= operand
            case "|":
                self |= operand
            case "<<=":
                self <<= operand
            case "^":
                self ^ operand
        return self

    def transform(self, operand_type: type = oe.Note) -> Self:
        for item in self._items:
            self._replace(item, operand_type(item))
        return self



class Devices(Container):
    
    def __iadd__(self, operand: any) -> Self:
        match operand:
            case od.Device():
                if isinstance(operand._data, str):
                    self._insert([ operand._data ]) # Places at the beginning
                return self
        return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        match operand:
            case od.Device():
                return self._delete([ operand._data ])
        return super().__isub__(operand)

class ClockedDevices(Devices):
    pass


class Composition(Container):

    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> Self:
        return self

    def get_staff_reference(self) -> 'og.Staff':
        return og.defaults._staff

    def reset_staff_reference(self) -> Self:
        return self

    def test_staff_reference(self) -> bool:
        return True



TypeClip = TypeVar('TypeClip', bound='Clip')    # TypeClip represents any subclass of Operand


class Clip(Composition):  # Just a container of Elements
    """
    This type of Operand aggregates Elements having itself a Position
    that propagates to them.

    Parameters
    ----------
    first : list_like, operand_like
        To set it with a group of Elements wrap them in a list to pass them
    """
    def __init__(self, *operands):
        super().__init__()
        self._staff: og.Staff = og.defaults._staff.copy()
        self._midi_track: ou.MidiTrack  = ou.MidiTrack()
        self._length_beats: Fraction    = Fraction(-1)  # in Beats where -1 means isn't set
        self._items: list[oe.Element] = []
        for single_operand in operands:
            self << single_operand


    def __getitem__(self, index: int) -> oe.Element:
        return super().__getitem__(index)
    
    def __next__(self) -> oe.Element:
        return super().__next__()


    def _replace(self, old_item: Any = None, new_item: Any = None) -> Self:
        if isinstance(new_item, oe.Element):
            return super()._replace(old_item, new_item)
        return self

    def _sort_position(self) -> Self:
        if self is not self._upper_container:
            self._upper_container._sort_position()
        self._items.sort(key=lambda x: x._position_beats)
        return self


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> Self:
        if isinstance(staff_reference, og.Staff):
            self._staff << staff_reference  # Does a copy
        for single_element in self:
            if isinstance(single_element, oe.Element):
                single_element.set_staff_reference(self._staff)
                single_element.set_clip_reference(self)
        return self

    def get_staff_reference(self) -> 'og.Staff':
        return self._staff

    def reset_staff_reference(self) -> Self:
        self._staff = og.defaults._staff.copy()
        for single_element in self:
            if isinstance(single_element, oe.Element):
                single_element.set_staff_reference(self._staff)
                single_element.set_clip_reference(self)
        return self

    def test_staff_reference(self) -> bool:
        for single_element in self:
            if isinstance(single_element, oe.Element) and not (
                single_element._staff_reference is self._staff and
                single_element._clip_reference is not None
            ):
                return False
        return True


    def first(self) -> oe.Element:
        """
        Gets the first Element accordingly to it's Position on the Staff.

        Args:
            None

        Returns:
            Element: The first Element of all Elements.
        """
        return super().first()

    def last(self) -> oe.Element:
        """
        Gets the last Element accordingly to it's Position on the Staff.

        Args:
            None

        Returns:
            Element: The last Element of all Elements.
        """
        return super().last()

    def last_position(self) -> ra.Position:
        last_element: oe.Element = self.last()

        if last_element:
            return last_element % ra.Position()
        
        return None

    def start(self) -> ra.Position:
        """
        Gets the starting position of all its Elements.
        This is the same as the minimum Position of all
        Element positions.

        Args:
            None

        Returns:
            Position: The minimum Position of all Elements.
        """
        start_position: ra.Position = None
        if self._length_beats < 0:
            if self.len() > 0:
                start_beats: Fraction = Fraction(0)
                first_element: oe.Element = self.first()
                if first_element:
                    start_beats = first_element._position_beats
                start_position = self._staff.convertToPosition(ra.Beats(start_beats))
        else:
            start_position = self._staff.convertToPosition(0)
        return start_position

    def finish(self) -> ra.Position:
        """
        Processes each element Position plus Length and returns the finish position
        as the maximum of all of them.

        Args:
            None

        Returns:
            Position: The maximum of Position + Length of all Elements.
        """
        finish_position: ra.Position = None

        if self._length_beats < 0:
            if self.len() > 0:
                finish_beats: Fraction = Fraction(0)
                for item in self._items:
                    if isinstance(item, oe.Element):
                        single_element: oe.Element = item
                        element_finish: Fraction = single_element._position_beats \
                            + (single_element % ra.Length())._rational
                        if element_finish > finish_beats:
                            finish_beats = element_finish
                finish_position = self._staff.convertToPosition(ra.Beats(finish_beats))
        else:
            finish_position = self._staff.convertToPosition(ra.Beats(self._length_beats))
        return finish_position


    def length(self) -> ra.Length:
        """
        Reruns the length that goes from the start to finish of all elements.

        Args:
            None

        Returns:
            Length: Equal to Clip finish() - start().
        """
        start = self.start()
        finish = self.finish()
        if start and finish:
            return (finish - start).convertToLength()
        return self._staff.convertToLength(0)

    def duration(self) -> ra.Duration:
        """
        Reruns the length wrapped as Duration.

        Args:
            None

        Returns:
            Duration: Equal to length() but returning Duration.
        """
        return self.length().convertToDuration()


    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, because a Container has
        only one type of Parameters it should be used in conjugation with list()
        to extract the Parameter list.

        Examples
        --------
        >>> clip = Track(Note("A"), Note("B"))
        >>> clip % list() >> Print()
        [<operand_element.Note object at 0x0000017B5F3FF6D0>, <operand_element.Note object at 0x0000017B5D3B36D0>]
        """
        match operand:
            case od.DataSource():
                match operand._data:
                    case og.Staff():        return self._staff
                    case ou.MidiTrack():    return self._midi_track
                    case ra.Measurement():
                        return operand._data << self._staff.convertToLength(ra.Beats(self._length_beats))
                    case _:                 return super().__mod__(operand)
            case og.Staff():        return self._staff.copy()
            case ou.MidiTrack():    return self._midi_track.copy()
            case ou.TrackNumber() | od.TrackName() | Devices() | str():
                return self._midi_track % operand
            case ra.Length():       return self.length()
            case ra.Duration():     return self.duration()
            case ra.StaffParameter() | ou.KeySignature() | ou.Accidentals() | ou.Major() | ou.Minor() | og.Scale() | ra.Measures() | ou.Measure() \
                | float() | Fraction():
                return self._staff % operand
            case _:
                return super().__mod__(operand)

    def get_position_beats(self, position: ra.Position = None) -> Fraction:

        # Needs to be reset because shallow_copy doesn't result in different
        # staff references for each element
        self._staff.reset_accidentals()
        self._staff.reset_tied_note()
        self._staff.reset_stacked_notes()

        position_beats: Fraction = Fraction(0)

        if isinstance(position, ra.Position):
            position_beats += self._staff.transformPosition(position)._rational

        return position_beats


    def getPlotlist(self, position: ra.Position = None) -> list[dict]:

        position_beats: Fraction = self.get_position_beats(position)

        self_plotlist: list[dict] = []
        channels: dict[str, set[int]] = {
            "note":         set(),
            "automation":   set()
        }
    
        self_plotlist.extend(
            single_playlist
                for single_element in self._items
                for single_playlist in single_element.getPlotlist(self._midi_track, position_beats, channels)
        )
        # sorted(set) returns the sorted list from set
        # list_none = list(set).sort() doesn't return anything but None !
        self_plotlist.insert(0,
            {
                "channels": {
                    "note":         sorted(channels["note"]),
                    "automation":   sorted(channels["automation"])
                },
                "tempo": self._staff._tempo
            }
        )

        return self_plotlist


    def getPlaylist(self, position: ra.Position = None) -> list[dict]:

        position_beats: Fraction = self.get_position_beats(position)

        self_playlist: list[dict] = [
            {
                "devices": self._midi_track._devices
            }
        ]
    
        for single_element in self._items:
            self_playlist.extend(
                single_element.getPlaylist(self._midi_track, position_beats, False)
            )

        return self_playlist


    def getMidilist(self, position: ra.Position = None) -> list[dict]:

        position_beats: Fraction = self.get_position_beats(position)

        return [
            single_midilist
                for single_element in self._items
                for single_midilist in single_element.getMidilist(self._midi_track, position_beats)
        ]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["staff"]        = self.serialize(self._staff)
        serialization["parameters"]["midi_track"]   = self.serialize(self._midi_track)
        serialization["parameters"]["length"]       = self.serialize(self._length_beats)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"] and "midi_track" in serialization["parameters"] and
            "length" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._staff             = self.deserialize(serialization["parameters"]["staff"])
            self._midi_track        = self.deserialize(serialization["parameters"]["midi_track"])
            self._length_beats      = self.deserialize(serialization["parameters"]["length"])
            self.set_staff_reference()
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_mutation as om
        match operand:
            case Clip():
                self._midi_track        << operand._midi_track
                self._length_beats      = operand._length_beats
                # BIG BOTTLENECK HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # Profiling time of 371 ms in a total of 2006 ms (18.48%) | Called 37 times (10.017 ms per call)
                self._items   = self.deep_copy( operand._items )
                # COPY THE SELF OPERANDS RECURSIVELY
                self._next_operand  = self.deep_copy(operand._next_operand)
                self.set_staff_reference(operand._staff)

            case od.DataSource():
                match operand._data:
                    case og.Staff():        self._staff = operand._data
                    case ou.MidiTrack():    self._midi_track = operand._data
                    case ra.Length():       self._length_beats = self._staff.convertToBeats(operand._data)._rational
                    case om.Mutation():     operand._data.mutate(self)
                    case _:                 super().__lshift__(operand)

            case ou.MidiTrack() | ou.TrackNumber() | od.TrackName() | Devices() | od.Device():
                self._midi_track << operand
            case og.Staff() | ou.KeySignature() | og.TimeSignature() | ra.StaffParameter() | ou.Accidentals() | ou.Major() | ou.Minor():
                self._staff << operand  # Staff has no clock!
            # Use Frame objects to bypass this parameter into elements (Setting Position)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )

            case oe.Element():
                if self.len() > 0:  # Avoids infinite recursion
                    self /= operand # Stacks elements directly
                else:
                    self += operand

            case list():
                self._items = [
                    item.copy() for item in operand if isinstance(item, oe.Element)
                ]
            case om.Mutation():
                operand.copy().mutate(self)
            
            case od.ClipParameter() | od.Parameters():

                if isinstance(operand, od.Parameters):
                    for single_parameter in operand._data:
                        self << od.ClipParameter(single_parameter)
                else:

                    operand._data = self & operand._data    # Processes the tailed self operands or the Frame operand if any exists
                    match operand._data:
                        case ra.Length() | ra.Duration():
                            self._length_beats = self._staff.convertToBeats(operand._data)._rational
                        case ou.MidiTrack() | ou.TrackNumber() | od.TrackName() | str():
                            self._midi_track << operand._data
                        case None:
                            self._length_beats = Fraction(-1)
                        case Clip():
                            self._staff << operand._data._staff
                        case _:
                            self._staff << operand._data

            case tuple():
                for single_operand in operand:
                    self << single_operand

            case Composition():
                self.set_staff_reference(operand.get_staff_reference())

            case _: # Works for Frame too
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item << operand
        return self

    # Pass trough method that always results in a Clip (Self)
    def __rshift__(self, operand) -> Self:
        import operand_mutation as om
        match operand:
            case Clip() | oe.Element():
                # Quantized Stacking by Measures
                self *= operand
                return self
            case om.Mutation():
                return operand.mutate(self)
            case od.Playlist():
                operand.__rrshift__(self)
                return self
            case od.Process():
                return operand.__rrshift__(self)
            case om.Mutation():
                return operand.mutate(self)

        return super().__rshift__(operand)


    # Avoids the costly copy of Track self doing +=
    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Clip():
                operand_elements = [
                    single_element.copy().set_staff_reference(self._staff).set_clip_reference(self)
                    for single_element in operand._items
                ]
                if self.len() > 0:
                    self_last_element: oe.Element = self[-1]
                    return self._append(operand_elements, self_last_element)._sort_position()  # Shall be sorted!
                return self._append(operand_elements)._sort_position() # Shall be sorted!
            case oe.Element():
                new_element: oe.Element = operand.copy().set_staff_reference(self._staff).set_clip_reference(self)
                if self.len() > 0:
                    self_last_element: oe.Element = self[-1]
                    return self._append([ new_element ], self_last_element)._sort_position()  # Shall be sorted!
                return self._append([ new_element ])._sort_position()  # Shall be sorted!
            case list():
                operand_elements = [
                    single_element.copy().set_staff_reference(self._staff).set_clip_reference(self)
                    for single_element in operand if isinstance(single_element, oe.Element)
                ]
                if self.len() > 0:
                    self_last_element: oe.Element = self[-1]
                    return self._append(operand_elements, self_last_element)
                return self._append(operand_elements)

            case ou.KeySignature() | og.TimeSignature() | ra.StaffParameter() | ou.Accidentals() | ou.Major() | ou.Minor():
                self._staff += operand
            case od.Parameters():
                for single_parameter in operand._data:
                    self += od.ClipParameter(single_parameter)

            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item += operand
        return self._sort_position()  # Shall be sorted!

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Clip():
                return self._delete(operand._items)
            case oe.Element():
                return self._delete([ operand ])
            case list():
                return self._delete(operand)
            
            case ou.KeySignature() | og.TimeSignature() | ra.StaffParameter() | ou.Accidentals() | ou.Major() | ou.Minor():
                self._staff -= operand
            case od.Parameters():
                for single_parameter in operand._data:
                    self -= od.ClipParameter(single_parameter)

            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item -= operand
        return self._sort_position()  # Shall be sorted!

    # in-place multiply (NO COPY!)
    def __imul__(self, operand: any) -> Self:
        import operand_mutation as om
        import operand_selection as os
        match operand:
            case Clip():
                right_start_position: ra.Position = operand.start()
                if self._length_beats < 0:
                    # It's the position of the element that matters and not their tailed Duration
                    last_position: oe.Position = self.last_position()
                    if last_position:
                        add_position: ra.Position = last_position.roundMeasures() + ou.Measure(1)
                    else:
                        add_position: ra.Position = ra.Position(0)
                else:
                    left_end_position: ra.Position = self._staff.convertToPosition(ra.Beats(self._length_beats))
                    self._length_beats += (operand % ra.Length())._rational
                    add_position: ra.Position = left_end_position - right_start_position
                operand_elements = [
                    (single_data + add_position).set_staff_reference(self._staff).set_clip_reference(self)
                    for single_data in operand._items if isinstance(single_data, oe.Element)
                ]
                self._items.extend( single_element for single_element in operand_elements )
                
            case oe.Element():
                self *= Clip(operand)

            case int():
                if operand > 1:
                    if self._length_beats >= 0:
                        add_position: ra.Position = self._staff.convertToPosition(ra.Beats(self._length_beats))
                        self._length_beats *= operand
                    else:
                        # It's the position of the element that matters and not their tailed Duration
                        last_element: oe.Element = self.last()
                        if last_element:
                            left_end_position: ra.Position = last_element % ra.Position()
                            add_position: ra.Position = left_end_position.roundMeasures() + ou.Measure(1)
                        else:
                            add_position: ra.Position = self._staff.convertToPosition(ra.Beats(0))
                    self_copy: Clip = self.copy()
                    for _ in range(operand - 2):
                        self_copy += add_position
                        self += self_copy   # implicit copy of self_copy
                    # Uses the last self_copy for the last iteration
                    self_copy += add_position
                    self._items.extend(
                        single_element.set_staff_reference(self._staff).set_clip_reference(self)
                        for single_element in self_copy if isinstance(single_element, oe.Element)
                    )
                elif operand == 0:   # Must be empty
                    self._items = []  # Just to keep the self object
            case ou.TimeUnit():
                self_repeating: int = 0
                operand_beats: Fraction = self._staff.convertToBeats(operand)._rational
                self_length: ra.Length = self % ra.Length()
                self_beats: Fraction = self_length.roundMeasures()._rational  # Beats default unit
                if self_beats > 0:
                    self_repeating = operand_beats // self_beats
                self *= self_repeating
            case od.Parameters():
                for single_parameter in operand._data:
                    self *= od.ClipParameter(single_parameter)

            case om.Mutation():
                return operand.copy().mutate(self)

            case os.Selection():
                if operand != self:
                    self._items = []

            case tuple():
                for single_operand in operand:
                    self *= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item *= operand
        return self._sort_position()  # Shall be sorted!

    def __rmul__(self, operand: any) -> Self:
        return self.__mul__(operand)
    
    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case Clip():
                if self._length_beats < 0:
                    left_end_position: ra.Position = self.finish()
                else:
                    left_end_position: ra.Position = self._staff.convertToPosition(ra.Beats(self._length_beats))    # Doesn't round, immediate stacking
                    self._length_beats += (operand % ra.Length())._rational
                right_start_position: ra.Position = operand.start()
                length_shift: ra.Length = ra.Length(left_end_position - right_start_position)
                # Convert Length to Position
                add_position: ra.Position = ra.Position(length_shift)
                operand_elements = [
                    (single_data + add_position).set_staff_reference(self._staff).set_clip_reference(self)
                    for single_data in operand._items if isinstance(single_data, oe.Element)
                ]
                self._items.extend( single_element for single_element in operand_elements )

            case oe.Element():
                self /= Clip(operand)

            case int():
                if operand > 1:
                    add_position: ra.Position = ra.Position(0)
                    finish: ra.Position = self.finish()
                    if finish:
                        add_position = finish
                    self_copy: Clip = self.copy()
                    for _ in range(operand - 2):
                        self_copy += add_position
                        self += self_copy   # implicit copy of self_copy
                    # Uses the last self_copy for the last iteration
                    self_copy += add_position
                    self._items.extend(
                        single_element.set_staff_reference(self._staff).set_clip_reference(self)
                        for single_element in self_copy if isinstance(single_element, oe.Element)
                    )
                    if self._length_beats >= 0:
                        finish_position_beats: Fraction = self.finish()._rational
                        if finish_position_beats > self._length_beats:
                            self._length_beats = finish_position_beats
                elif operand == 0:   # Must be empty
                    self._items = []  # Just to keep the self object
            
            case ou.TimeUnit():
                self_repeating: int = 0
                self_length: ra.Length = self % ra.Length()
                length_value: Fraction = self_length % operand % Fraction()
                if length_value > 0:
                    operand_value: int = operand._unit
                    self_repeating = int( operand_value / length_value )
                self /= self_repeating

            case od.Parameters():
                for single_parameter in operand._data:
                    self /= od.ClipParameter(single_parameter)

            case tuple():
                for single_operand in operand:
                    self /= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item /= operand
        return self._sort_position()  # Shall be sorted!

    def empty_copy(self, *parameters) -> Self:
        empty_copy: Clip                = super().empty_copy()
        empty_copy._staff               << self._staff
        empty_copy._midi_track          << self._midi_track
        empty_copy._length_beats        = self._length_beats
        for single_parameter in parameters:
            empty_copy << single_parameter
        return empty_copy
    
    def shallow_copy(self, *parameters) -> Self:
        shallow_copy: Clip              = super().shallow_copy()
        # It's a shallow copy, so it shares the same Staff and midi track
        shallow_copy._staff             = self._staff   
        shallow_copy._midi_track        = self._midi_track
        shallow_copy._length_beats      = self._length_beats
        for single_parameter in parameters:
            shallow_copy << single_parameter
        return shallow_copy

    
    def sort(self, parameter: type = ra.Position, reverse: bool = False) -> Self:
        """
        Sorts the self list based on a given type of parameter.

        Args:
            parameter (type): The type of parameter being sorted by.

        Returns:
            Container: The same self object with the items processed.
        """
        original_positions: list[Fraction] = [
            element._position_beats for element in self._items
        ]
        super().sort(parameter, reverse)
        for index, element in enumerate(self._items):
            element._position_beats = original_positions[index]
        return self
    
    def stepper(self, pattern: str = "1... 1... 1... 1...", note: Any = None) -> Self:

        if isinstance(pattern, str):

            # Fraction sets the Duration in Steps
            element_note: oe.Note = \
                oe.Note().set_staff_reference(self._staff).set_clip_reference(self) \
                << Fraction(1) << note

            pattern = [1 if char == '1' else 0 for char in pattern if char != ' ' and char != '-']

            if isinstance(pattern, list):

                position_steps: ra.Steps = ra.Steps(0)
                for single_step in pattern:
                    if single_step == 1:
                        self += element_note << position_steps
                    position_steps += 1

            return self._sort_position()

        return self


    def automate(self, values: list[int] = [100, 70, 30, 100],
                 pattern: str = "1... 1... 1... 1...", automation: Any = "Pan", interpolate: bool = True) -> Self:

        if isinstance(pattern, str):

            # ControlChange, PitchBend adn Aftertouch Elements have already 1 Step of Duration
            if isinstance(automation, oe.Aftertouch):
                automate_element: oe.Element = \
                    oe.Aftertouch().set_staff_reference(self._staff).set_clip_reference(self) \
                    << automation
                # Ensure values is a non-empty list with only integers ≥ 0
                if not (isinstance(values, list) and values and all(isinstance(v, int) for v in values)):
                    values = [30, 70, 50, 0]
            elif isinstance(automation, oe.PitchBend) or automation is None:  # Pitch Bend, special case
                automate_element: oe.Element = \
                    oe.PitchBend().set_staff_reference(self._staff).set_clip_reference(self) \
                    << automation
                # Ensure values is a non-empty list with only integers ≥ 0
                if not (isinstance(values, list) and values and all(isinstance(v, int) for v in values)):
                    values = [-20*64, -70*64, -50*64, 0*64]
            else:
                automate_element: oe.Element = \
                    oe.ControlChange().set_staff_reference(self._staff).set_clip_reference(self) \
                    << automation
                # Ensure values is a non-empty list with only integers ≥ 0
                if not (isinstance(values, list) and values and all(isinstance(v, int) and v >= 0 for v in values)):
                    values = [80, 50, 30, 100]
                
            pattern_values = []
            value_index = 0  # Keep track of which value to use
            for char in pattern.replace(" ", "").replace("-", ""):
                if char == "1":
                    pattern_values.append(values[value_index])
                    value_index = (value_index + 1) % len(values)  # Cycle through values
                else:
                    pattern_values.append(None)  # Empty slots
            
            automation = pattern_values[:] # makes a copy of pattern_values

            if interpolate:

                # Find indices of known values
                known_indices = [i for i, val in enumerate(pattern_values) if val is not None]
                
                if not known_indices:
                    raise ValueError("List must contain at least one integer.")
                else:
                    automation = self._interpolate_list(known_indices, pattern_values)

            position_steps: ra.Steps = ra.Steps(0)
            for value in automation:
                if value is not None:   # None adds no Element
                    self += automate_element << value << position_steps
                position_steps += 1

            return self._sort_position()
        
        return self


    def interpolate(self) -> Self:

        # It's a shallow copy of self, so, adding elements to it also adds elements to self!
        clip_automations: Clip = self.filter(of.OperandType(oe.Automation))
        plotlist: list[dict] = clip_automations.getPlotlist()
        channels: list[int] = plotlist[0]["channels"]["automation"]

        for channel in channels:

            channel_automation: Clip = clip_automations.filter(ou.Channel(channel))

            if channel_automation.len() > 1:

                element_template: oe.Element = channel_automation[0].copy()
                
                # Find indices of known values
                known_indices = [
                    (element % ra.Position()).convertToSteps() % int() for element in channel_automation._items
                ]

                total_messages: int = known_indices[-1] - known_indices[0] + 1
                pattern_values = [ None ] * total_messages

                element_index: int = 0
                for index in range(total_messages):
                    if index in known_indices:
                        pattern_values[index] = channel_automation[element_index] % int()
                        element_index += 1

                automation = self._interpolate_list(known_indices, pattern_values)

                position_steps: ra.Steps = ra.Steps(0)
                for index, value in enumerate(automation):
                    if index not in known_indices:   # None adds no Element
                        channel_automation += element_template << value << position_steps
                    position_steps += 1

        return self._sort_position()


    def _interpolate_list(self, known_indices, pattern_values) -> list:

        automation = pattern_values[:] # makes a copy of pattern_values
            
        for i in range(len(pattern_values)):
            if automation[i] is None:
                    # Find closest known values before and after
                left_idx = max([idx for idx in known_indices if idx < i], default=None)
                right_idx = min([idx for idx in known_indices if idx > i], default=None)
                    
                if left_idx is None:
                    automation[i] = automation[right_idx]   # Use the right value if no left
                elif right_idx is None:
                    automation[i] = automation[left_idx]    # Use the left value if no right
                else:
                        # Linear interpolation
                    left_val = automation[left_idx]
                    right_val = automation[right_idx]
                    step = (right_val - left_val) / (right_idx - left_idx)
                    automation[i] = int(left_val + step * (i - left_idx))

        return automation
    
    
    def reverse(self, non_empty_measures_only: bool = True) -> Self:
        """
        Reverses the sequence of the clip concerning the elements position, like horizontally mirrored.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        if non_empty_measures_only:
            first_measure_position_beats: Fraction = self.start().roundMeasures()._rational
        else:
            first_measure_position_beats: Fraction = Fraction(0)
        clip_length_beats: Fraction = ra.Length( self.finish() ).roundMeasures()._rational # Rounded up Duration to next Measure
        for single_element in self._items:
            element_position_beats: Fraction = single_element._position_beats
            element_length_beats: Fraction = single_element % ra.Length() // Fraction()
            # Only changes Positions
            single_element._position_beats = first_measure_position_beats + clip_length_beats - (element_position_beats + element_length_beats)
        return super().reverse()    # Reverses the list

    def flip(self) -> Self:
        """
        Flip is similar to reverse but instead of the elements position it reverses the
        Note and similar Pitch, like vertically mirrored.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        higher_pitch: og.Pitch = None
        lower_pitch: og.Pitch = None
        
        for item in self._items:
            if isinstance(item, oe.Note):
                element_pitch: og.Pitch = item._pitch
                if higher_pitch is None:
                    higher_pitch = element_pitch
                    lower_pitch = element_pitch
                elif element_pitch > higher_pitch:
                    higher_pitch = element_pitch
                elif element_pitch < lower_pitch:
                    lower_pitch = element_pitch

        top_pitch: float = higher_pitch % float()
        bottom_pitch: float = lower_pitch % float()

        for item in self._items:
            if isinstance(item, oe.Note):
                element_pitch: og.Pitch = item._pitch
                note_pitch: float = element_pitch % float()
                new_pitch: float = top_pitch - (note_pitch - bottom_pitch)
                element_pitch << new_pitch
                
        return self

    def snap(self, up: bool = False) -> Self:
        """
        For Note and similar, it snaps the given Pitch to the one of the key signature.

        Args:
            up (bool): By default it snaps to the closest bellow pitch, but if set
            as True, it will snap to the closest above pitch instead

        Returns:
            Clip: The same self object with the items processed.
        """
        for single_note in self:
            if isinstance(single_note, oe.Note):
                single_note._pitch.snap(up)
        return self

    def extend(self, length: ra.Length = ra.Length(2.0)) -> Self:
        """
        Extends (drags) the given clip along a given length.

        Args:
            length (ra.Length): The length along with the clip will be extended (dragged)

        Returns:
            Clip: The same self object with the items processed.
        """
        original_self: Clip = self.shallow_copy()
        while self / original_self <= length:
            self /= original_self
        return self

    def trim(self, length: ra.Length = ra.Length(1.0)) -> Self:
        """
        Trims the given clip at a given length.

        Args:
            length (ra.Length): The length along with the clip will be trimmed

        Returns:
            Clip: The same self object with the items processed.
        """
        if isinstance(length, ra.Length):
            self._items = [
                element for element in self._items
                if element % ra.Position() < length
            ]
            for index, element in enumerate(self._items):
                if element % ra.Position() + element % ra.Length() > length:
                    new_length: ra.Length = length - element % ra.Position()
                    element << new_length
            if self._length_beats >= 0:
                self._length_beats = min(self._length_beats, self._staff.convertToBeats(length)._rational)
        return self
    
    def cut(self, start: ra.Position = None, finish: ra.Position = None) -> Self:
        """
        Cuts (removes) the section of the clip from the start to the finish positions.

        Args:
            start (ra.Position): Starting position of the section to be cut
            finish (ra.Position): Finish position of the section to be cut

        Returns:
            Clip: The same self object with the items processed.
        """
        if start is None:
            start = ra.Position(0)
        if finish is None:
            finish = start + ra.Measures(1)
        if finish > start:
            self._items = [
                element for element in self._items
                if element < start or element >= finish
            ]
            move_left: ra.Position = finish - start
            for index, element in enumerate(self._items):
                if element > start:
                    element -= move_left
        return self

    def select(self, start: ra.Position = None, finish: ra.Position = None) -> Self:
        """
        Selects the section of the clip that will be preserved.

        Args:
            start (ra.Position): Starting position of the section to be selected
            finish (ra.Position): Finish position of the section to be selected

        Returns:
            Clip: The same self object with the items processed.
        """
        shallow_copy: Clip = self.shallow_copy()
        if start is None:
            start = ra.Position(0)
        if finish is None:
            finish = start + ra.Measures(1)
        if finish > start:
            shallow_copy._items = [
                element for element in shallow_copy._items
                if element >= start and element < finish
            ]
            for index, element in enumerate(shallow_copy._items):
                element -= start
        return shallow_copy

    def monofy(self) -> Self:
        """
        Cuts out any part of an element Duration that overlaps with the next element.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        if self.len() > 1:
            # Starts by sorting by Position
            shallow_copy: Clip = self.shallow_copy()._sort_position()
            for index in range(shallow_copy.len()):
                current_element: oe.Element = shallow_copy._items[index]
                next_element: oe.Element = shallow_copy._items[index + 1]
                if current_element.finish() > next_element.start():
                    new_length: ra.Length = ra.Length( next_element.start() - current_element.start() )
                    current_element << new_length
        return self

    def fill(self) -> Self:
        """
        Adds up Rests to empty spaces (lengths) in a staff for each Measure.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        shallow_copy: Clip = self.shallow_copy()._sort_position()
        shallow_copy_len: int = shallow_copy.len()
        for index in range(shallow_copy_len):
            current_element: oe.Element = shallow_copy._items[index]
            next_element: oe.Element = shallow_copy._items[index + 1]
            if current_element.finish() < next_element.start():
                rest_length: ra.Length = ra.Length( next_element.start() - current_element.finish() )
                rest_element: oe.Rest = \
                    oe.Rest().set_staff_reference(self._staff).set_clip_reference(self) \
                    << rest_length
                self += rest_element
        
        last_element: oe.Element = shallow_copy[shallow_copy_len - 1]
        staff_end: ra.Position = last_element.finish().convertToLength().roundMeasures().convertToPosition()
        if last_element.finish() < staff_end:
            rest_length: ra.Length = ra.Length( staff_end - last_element.finish() )
            rest_element: oe.Rest = \
                oe.Rest().set_staff_reference(self._staff).set_clip_reference(self) \
                << rest_length
            self += rest_element

        return self

    def fit(self, length: ra.Length = None) -> Self:
        """
        Fits the entire clip in a given length.

        Args:
            length (ra.Length): A length in which the clip must fit

        Returns:
            Clip: The same self object with the items processed.
        """
        if isinstance(length, (ra.Position, ra.TimeValue, ra.Duration, ou.TimeUnit)):
            fitting_finish: ra.Position = self._staff.convertToPosition(length)
        else:
            fitting_finish: ra.Position = self._staff.convertToPosition(ou.Measure(1))
        actual_finish: ra.Position = self.finish()
        length_ratio: Fraction = fitting_finish._rational / actual_finish._rational
        self *= ra.Position(length_ratio)   # Adjust positions
        self *= ra.Duration(length_ratio)   # Adjust durations
        return self

    def link(self, non_empty_measures_only: bool = True) -> Self:
        """
        Adjusts the duration/length of each element to connect to the start of the next.
        For the last element in the clip, this is extended up to the end of the measure.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        if self.len() > 0:
            for index, element in enumerate(self._items):
                if index > 0:
                    previous_element: oe.Element = self[index - 1]
                    previous_element << self._staff.convertToDuration(
                        ra.Beats(element._position_beats - previous_element._position_beats)
                    )
            # Add a Rest in the beginning if necessary
            first_element: oe.Element = self.first()
            last_element: oe.Element = self.last()
            starting_position_beats: Fraction = Fraction(0)
            if non_empty_measures_only:
                starting_position_beats = (first_element // ra.Position()).roundMeasures()._rational
            if first_element._position_beats != starting_position_beats:  # Not at the starting position
                rest_duration: ra.Duration = self._staff.convertToDuration(ra.Beats(first_element._position_beats))
                self._items.insert(0, oe.Rest(rest_duration))
            # Adjust last_element duration based on its Measure position
            if last_element is not None:    # LAST ELEMENT ONLY!
                remaining_beats: Fraction = \
                    self._staff.convertToLength(ra.Beats(last_element._position_beats)).roundMeasures()._rational \
                        - last_element._position_beats
                if remaining_beats == 0:    # Means it's on the next Measure alone, thus, it's a one Measure note
                    last_element << self._staff.convertToDuration(ra.Measures(1))
                else:
                    last_element << self._staff.convertToDuration(ra.Beats(remaining_beats))
        return self._sort_position()


    def stack(self, non_empty_measures_only: bool = True) -> Self:
        """
        For stackable elements, moves each one to start at the finish position
        of the previous one. If it's the first element then it's position becomes 0.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        for index, single_element in enumerate(self._items):
            if index > 0:   # Not the first element
                duration_beats: Fraction = self._staff.convertToBeats(ra.Duration(self._items[index - 1]._duration_notevalue))._rational
                single_element._position_beats = self._items[index - 1]._position_beats + duration_beats  # Stacks on Element Duration
            else:           # THE FIRST ELEMENT!
                if non_empty_measures_only:
                    root_position: ra.Position = (single_element // ra.Position()).roundMeasures()
                    single_element._position_beats = root_position._rational
                else:
                    single_element._position_beats = Fraction(0)   # everything starts at the beginning (0)!
        
        return self._sort_position()    # May be needed due to upper clips
    
    def decompose(self) -> Self:
        decomposed_elements: list[oe.Element] = []
        for single_element in self._items:
            component_elements: list[oe.Element] = single_element.get_component_elements()
            for single_component in component_elements:
                decomposed_elements.append(single_component)
        self._items = decomposed_elements
        return self

    def arpeggiate(self, parameters: any = None) -> Self:
        arpeggio = og.Arpeggio(parameters)
        arpeggio.arpeggiate_source(self._items, self.start(), self.length())
        return self

    def tie(self, tied: bool = True) -> Self:
        """
        Sets the Note or similar elements as tied or not tied.

        Args:
            tied (bool): True for tied and False for not tied

        Returns:
            Clip: The same self object with the items processed.
        """
        for item in self._items:
            if isinstance(item, oe.Note):
                item << ou.Tied(tied)
        return self
    
    def slur(self, gate: float = 1.05) -> Self:
        """
        Changes the element duration in order to crate a small overlap.

        Args:
            gate (float): Can be given a different value from 1.05, de default

        Returns:
            Clip: The same self object with the items processed.
        """
        last_element = None
        for item in self._items:
            if isinstance(item, oe.Note):
                if last_element is not None:
                    last_element << ra.Gate(gate)
                last_element = item
        return self
    
    def smooth(self) -> Self:
        """
        Changes the Note or similar octave to become the closest pitch to the previous one.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        last_note = None
        smooth_range = og.Pitch(ou.Key(12 // 2), -1)  # 6 chromatic steps
        for item in self._items:
            if isinstance(item, oe.Note):    # Only Note has single Pitch
                actual_note = item
                if last_note is not None:
                    while actual_note._pitch > last_note._pitch:
                        actual_note._pitch -= ou.Octave(1)
                    while actual_note._pitch < last_note._pitch:
                        actual_note._pitch += ou.Octave(1)
                    if actual_note._pitch - last_note._pitch > smooth_range:
                        actual_note._pitch -= ou.Octave(1)
                last_note = actual_note
        return self


    _channel_colors = [
        "#4CAF50",  # Green (starting point)
        "#2196F3",  # Blue
        "#FF5722",  # Orange
        "#9C27B0",  # Purple
        "#FFEB3B",  # Bright Yellow
        "#FF9800",  # Amber
        "#E91E63",  # Pink
        "#00BCD4",  # Cyan
        "#8BC34A",  # Light Green
        "#FFC107",  # Gold
        "#3F51B5",  # Indigo
        "#FF5252",  # Light Red
        "#673AB7",  # Deep Purple
        "#CDDC39",  # Lime
        "#03A9F4",  # Light Blue
        "#FF4081",  # Hot Pink
    ]

    def _plot_elements(self, plotlist: list[dict]):

        self._ax.clear()

        self._ax.set_title(f"Iteration {self._iteration} of {
            len(self._clip_iterations) - 1 if len(self._clip_iterations) > 1 else 0
        }")


        # Horizontal X-Axis, Time related (COMMON)

        clip_tempo: float = float(plotlist[0]["tempo"])
        self._ax.set_xlabel(f"Time (Measures.Beats.Steps) at {round(clip_tempo, 1)} bpm")
        self._ax.margins(x=0)  # Ensures NO extra padding is added on the x-axis

        beats_per_measure: Fraction = self._staff % og.TimeSignature() % ra.BeatsPerMeasure() % Fraction()
        quantization: Fraction = self._staff % ra.Quantization() % Fraction()
        quantization_beats: Fraction = ra.Duration(self, quantization).convertToLength() // Fraction()
        steps_per_measure: Fraction = beats_per_measure / quantization_beats

        # By default it's 1 Measure long
        last_position: Fraction = beats_per_measure
        last_position_measures: Fraction = last_position / beats_per_measure
        last_position_measure: int = int(last_position / beats_per_measure)
        if last_position_measure != last_position_measures:
            last_position_measure += 1


        # Vertical Y-Axis, Pitch/Value related (SPECIFIC)

        note_channels: list[int] = plotlist[0]["channels"]["note"]
        automation_channels: list[int] = plotlist[0]["channels"]["automation"]

        # Plot Notes
        if note_channels or not automation_channels:

            self._ax.set_ylabel("Chromatic Keys")
            self._ax.format_coord = \
                lambda x, y: f"Seconds = {round(x / clip_tempo * 60, 3)}, Beat = {int(x)}, Pitch = {int(y + 0.5)}"

            note_plotlist: list[dict] = [ element_dict["note"] for element_dict in plotlist if "note" in element_dict ]

            # Updates X-Axis data
            last_position = max(note["position_off"] for note in note_plotlist)
            last_position_measures = last_position / beats_per_measure
            last_position_measure = int(last_position / beats_per_measure)
            if last_position_measure != last_position_measures:
                last_position_measure += 1

            # Get pitch range
            min_pitch: int = min(note["pitch"] for note in note_plotlist) // 12 * 12
            max_pitch: int = max(note["pitch"] for note in note_plotlist) // 12 * 12 + 12

            # Shade black keys
            for pitch in range(min_pitch, max_pitch + 1):
                if o.is_black_key(pitch):
                    self._ax.axhspan(pitch - 0.5, pitch + 0.5, color='lightgray', alpha=0.5)

            # Plot notes
            for channel in note_channels:
                channel_color = Clip._channel_colors[channel - 1]
                channel_plotlist = [
                    channel_note for channel_note in note_plotlist
                    if channel_note["channel"] == channel
                ]

                for note in channel_plotlist:
                    self._ax.barh(y = note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                            height=0.5, color=channel_color, edgecolor='black', linewidth=3, alpha = (note["velocity"] / 127))
        

            chromatic_keys: list[str] = ["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"]
            # Set MIDI note ticks with Middle C in bold
            self._ax.set_yticks(range(min_pitch, max_pitch + 1))
            y_labels = [
                chromatic_keys[p % 12] + (str(p // 12 - 1) if p % 12 == 0 else "")
                for p in range(min_pitch, max_pitch + 1)
            ]  # Bold Middle C
            self._ax.set_yticklabels(y_labels, fontsize=10, fontweight='bold' if 60 in range(min_pitch, max_pitch + 1) else 'normal')

            self._ax.set_ylim(min_pitch - 0.5, max_pitch + 0.5)  # Ensure all notes fit

        
        # Plot Automations
        else:

            self._ax.set_ylabel("Automation Values (MSB)")
            self._ax.format_coord = \
                lambda x, y: f"Seconds = {round(x / clip_tempo * 60, 3)}, Beat = {int(x)}, Value = {int(y + 0.5)}"

            automation_plotlist: list[dict] = [ element_dict["automation"] for element_dict in plotlist if "automation" in element_dict ]

            # Updates X-Axis data
            last_position = max(automation["position"] for automation in automation_plotlist)
            last_position_measures = last_position / beats_per_measure
            last_position_measure = int(last_position / beats_per_measure)
            if last_position_measure != last_position_measures:
                last_position_measure += 1

            # Axis limits
            self._ax.set_ylim(-1, 128)
            # Ticks
            self._ax.set_yticks(range(0, 129, 8))

            # Dashed horizontal lines at multiples of 16 (except 64)
            for i in range(0, 129, 16):
                if i != 64:
                    self._ax.axhline(y=i, color='gray', linestyle='--', linewidth=1)
            # Dashed line at y = 127
            self._ax.axhline(y=127, color='gray', linestyle='--', linewidth=1)
            # Solid line at y = 64
            self._ax.axhline(y=64, color='gray', linestyle='-', linewidth=1.5)

            # Plot automations
            for channel in automation_channels:
                channel_color = Clip._channel_colors[channel - 1]
                channel_plotlist = [
                    channel_automation for channel_automation in automation_plotlist
                    if channel_automation["channel"] == channel
                ]

                if channel_plotlist:

                    channel_plotlist.sort(key=lambda a: a['position'])

                    # Plotting point lists
                    x: list[float]  = []
                    y: list[int]    = []
                    for automation in channel_plotlist:
                        x.append( float(automation["position"]) )
                        y.append( automation["value"] )

                    # Stepped line connecting the points
                    self._ax.plot(x, y, linestyle='-', drawstyle='steps-post', color=channel_color, linewidth=0.5)
                    # Actual data points
                    self._ax.plot(x, y, marker='o', linestyle='None', color=channel_color,
                                  markeredgecolor='black', markeredgewidth=1, markersize=8)

                    # Add the tailed line up to the end of the chart
                    x = [
                        float(channel_plotlist[-1]["position"]),
                        float(last_position_measure * beats_per_measure)
                    ]
                    y = [
                        channel_plotlist[-1]["value"],
                        channel_plotlist[-1]["value"]
                    ]
                    # Stepped line connecting the points
                    self._ax.plot(x, y, linestyle='-', drawstyle='steps-post', color=channel_color, linewidth=0.5)
                    # Actual data points
                    self._ax.plot(x, y, marker='None', linestyle='None', color=channel_color, markersize=6)


        # Draw vertical grid lines based on beats and measures
        one_extra_subdivision: float = quantization_beats
        step_positions = np.arange(0.0, float(last_position_measure * beats_per_measure + one_extra_subdivision), float(quantization_beats))
        beat_positions = np.arange(0.0, float(last_position_measure * beats_per_measure + one_extra_subdivision), 1)
        measure_positions = np.arange(0.0, float(last_position_measure * beats_per_measure + one_extra_subdivision), float(beats_per_measure))
    
        for measure_pos in measure_positions:
            self._ax.axvline(measure_pos, color='black', linestyle='-', alpha=1.0, linewidth=0.7)  # Measure lines
        for beat_pos in beat_positions:
            self._ax.axvline(beat_pos, color='gray', linestyle='-', alpha=0.5)  # Measure lines
        for grid_pos in step_positions:
            self._ax.axvline(grid_pos, color='gray', linestyle='dotted', alpha=0.5)  # Beat subdivisions

        # Set x-axis labels in 'Measure.Beat' format
        beat_labels = [
            f"{int(pos // float(beats_per_measure))}.{int(pos % float(beats_per_measure))}.{int(pos / quantization_beats % float(steps_per_measure))}"
            for pos in beat_positions
        ]
        
        self._ax.set_xticks(beat_positions)  # Only show measure & beat labels
        self._ax.set_xticklabels(beat_labels, rotation=45)
        self._fig.canvas.draw_idle()

        return None


    def _run_play(self, even = None, channel: int = None) -> Self:
        import threading
        last_clip: Clip = self._clip_iterations[self._iteration]
        if isinstance(channel, int) and channel > 0:
            # Filter already results in a shallow copy
            threading.Thread(target=od.Play.play, args=(
                last_clip.filter(ou.Channel(channel)),
            )).start()
            # last_clip.filter(ou.Channel(channel)) >> od.Play()
        else:
            threading.Thread(target=od.Play.play, args=(last_clip,)).start()
            # last_clip >> od.Play()
        return self

    def _run_previous(self, even = None) -> Self:
        if self._iteration > 0:
            self._iteration -= 1
            plotlist: list[dict] = self._plot_lists[self._iteration]
            self._plot_elements(plotlist)
            self._enable_button(self._next_button)
            if self._iteration == 0:
                self._disable_button(self._previous_button)
        return self

    def _run_next(self, even = None) -> Self:
        if self._iteration < len(self._plot_lists) - 1:
            self._iteration += 1
            plotlist: list[dict] = self._plot_lists[self._iteration]
            self._plot_elements(plotlist)
            self._enable_button(self._previous_button)
            if self._iteration == len(self._plot_lists) - 1:
                self._disable_button(self._next_button)
        return self

    def _update_iteration(self, iteration: int, plotlist: list[dict]) -> Self:
        self._plot_lists[iteration] = plotlist
        if iteration == self._iteration:
            self._plot_elements(plotlist)
        return self

    def _run_new(self, even = None) -> Self:
        if callable(self._n_function):
            iteration: int = self._iteration
            last_clip: Clip = self._clip_iterations[-1]
            new_clip: Clip = self._n_function(last_clip.copy())
            if isinstance(new_clip, Clip):
                self._iteration = len(self._clip_iterations)
                plotlist: list[dict] = new_clip.getPlotlist()
                self._clip_iterations.append(new_clip)
                self._plot_lists.append(plotlist)
                self._plot_elements(plotlist)
            # Updates the last_clip data and plot just in case
            self._update_iteration(iteration, last_clip.getPlotlist())
            self._enable_button(self._previous_button)
            self._disable_button(self._next_button)
        return self

    def _run_composition(self, even = None) -> Self:
        import threading
        if callable(self._c_function):
            last_clip: Clip = self._clip_iterations[self._iteration]
            composition: Composition = self._c_function(last_clip)
            if isinstance(composition, Composition):
                threading.Thread(target=od.Play.play, args=(composition,)).start()
                # composition >> od.Play()
            # Updates the last_clip data and plot just in case
            self._update_iteration(self._iteration, last_clip.getPlotlist())
        return self

    def _run_execute(self, even = None) -> Self:
        if callable(self._e_function):
            last_clip: Clip = self._clip_iterations[self._iteration]
            self._e_function(last_clip)
            # Updates the last_clip data and plot just in case
            self._update_iteration(self._iteration, last_clip.getPlotlist())
        return self

    @staticmethod
    def _disable_button(button: Button) -> Button:
        # Set disabled style
        button.label.set_color('lightgray')         # Light text
        button.ax.set_facecolor('none')             # No fill color
        button.hovercolor = 'none'
        for spine in button.ax.spines.values():
            spine.set_color('lightgray')
        return button

    @staticmethod
    def _enable_button(button: Button) -> Button:
        # Set enabled style
        button.ax.set_facecolor('white')
        button.hovercolor = 'gray'
        button.label.set_color('black')
        for spine in button.ax.spines.values():
            spine.set_color('black')
        return button

    def _on_move(self, event):
        if event.inaxes == self._ax:
            print(f"x = {event.xdata}, y = {event.ydata}")


    def plot(self, block: bool = True, pause: float = 0, iterations: int = 0,
            n_button: Optional[Callable[['Clip'], 'Clip']] = None,
            c_button: Optional[Callable[['Clip'], Composition]] = None,
            e_button: Optional[Callable[['Clip'], Any]] = None):


        self._clip_iterations: list[Clip] = [ self.copy() ]
        self._plot_lists: list[list] = [ self.getPlotlist() ]
        self._iteration: int = 0
        self._n_function = n_button
        self._c_function = c_button
        self._e_function = e_button

        if callable(self._n_function) \
                and isinstance(iterations, int) and iterations > 0:
            for _ in range(iterations):
                last_clip: Clip = self._clip_iterations[-1]
                new_clip: Clip = self._n_function(last_clip.copy())
                plotlist: list[dict] = new_clip.getPlotlist()
                self._clip_iterations.append(new_clip)
                self._plot_lists.append(plotlist)

        # Enable interactive mode (doesn't block the execution)
        plt.ion()

        self._fig, self._ax = plt.subplots(figsize=(12, 6))
        # self._fig.canvas.mpl_connect("motion_notify_event", lambda event: self._on_move(event))

        self._plot_elements(self._plot_lists[0])

        plt.tight_layout()

        # Play Button Widget
        ax_button = plt.axes([0.979, 0.888, 0.015, 0.05])
        play_button = Button(ax_button, 'P', color='white', hovercolor='grey')
        play_button.on_clicked(self._run_play)

        # Previous Button Widget
        ax_button = plt.axes([0.979, 0.828, 0.015, 0.05])
        self._previous_button = Button(ax_button, '<', color='white', hovercolor='grey')
        self._previous_button.on_clicked(self._run_previous)

        # Next Button Widget
        ax_button = plt.axes([0.979, 0.768, 0.015, 0.05])
        self._next_button = Button(ax_button, '>', color='white', hovercolor='grey')
        self._next_button.on_clicked(self._run_next)

        # New Button Widget
        ax_button = plt.axes([0.979, 0.708, 0.015, 0.05])
        new_button = Button(ax_button, 'N', color='white', hovercolor='grey')
        new_button.on_clicked(self._run_new)

        # Composition Button Widget
        ax_button = plt.axes([0.979, 0.648, 0.015, 0.05])
        composition_button = Button(ax_button, 'C', color='white', hovercolor='grey')
        composition_button.on_clicked(self._run_composition)

        # Execution Button Widget
        ax_button = plt.axes([0.979, 0.528, 0.015, 0.05])
        execute_button = Button(ax_button, 'E', color='white', hovercolor='grey')
        execute_button.on_clicked(self._run_execute)

        # Previous Button Widget
        self._disable_button(self._previous_button)
        if len(self._clip_iterations) == 1:
            # Next Button Widget
            self._disable_button(self._next_button)

        if not callable(self._n_function):
            # New Button Widget
            self._disable_button(new_button)

        if not callable(self._c_function):
            # Composition Button Widget
            self._disable_button(composition_button)

        if not callable(self._e_function):
            # Composition Button Widget
            self._disable_button(execute_button)


        if block and pause == 0:
            plt.show(block=True)
        elif pause > 0:
            plt.draw()
            plt.pause(pause)
        else:
            plt.show(block=False)


        # plt.show(block=False)
        # # Keep script alive while plots are open
        # while plt.get_fignums():  # Check if any figure is open
        #     plt.pause(0.1)  # Pause to allow GUI event processing

        return self._clip_iterations[self._iteration]


    def split(self, position: ra.Position) -> tuple['Clip', 'Clip']:
        """
        Splits the given clip in two at the given position.

        Args:
            position (ra.Position): Position at which the clip will be split in two

        Returns:
            Clip: The same self object with the items processed.
        """
        self_left: Clip     = self.filter(of.Less(position))
        self_right: Clip    = self.filter(of.GreaterEqual(position))
        return self_left, self_right
    

class Part(Composition):
    # Part it's like a classic Pattern
    def __init__(self, *operands):
        self._position_beats: Fraction  = Fraction(0)   # in Beats
        super().__init__()
        self._items: list[Clip | od.Playlist] = []

        # Song sets the Staff, this is just a reference
        self._staff_reference: og.Staff = og.defaults._staff
        self._song_reference: Song      = None

        for single_operand in operands:
            self << single_operand


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> Self:
        if isinstance(staff_reference, og.Staff):
            self._staff_reference = staff_reference
        return self

    def get_staff_reference(self) -> 'og.Staff':
        return self._staff_reference

    def reset_staff_reference(self) -> Self:
        self._staff_reference = og.defaults._staff
        return self

    def set_song_reference(self, song_reference: 'Song' = None) -> Self:
        if isinstance(song_reference, Song):
            self._song_reference = song_reference
        return self

    def get_song_reference(self) -> 'Song':
        return self._song_reference

    def reset_song_reference(self) -> Self:
        self._song_reference = None
        return self


    def __getitem__(self, key: str | int) -> Clip | od.Playlist:
        if isinstance(key, str):
            for single_item in self._items:
                if isinstance(single_item, Clip):
                    if single_item._midi_track._name == key:
                        return single_item
                else:
                    if single_item._track_name == key:
                        return single_item
            return ol.Null()
        return self._items[key]

    def __next__(self) -> Clip | od.Playlist:
        return super().__next__()
    

    def len(self, just_clips: bool = False) -> int:

        if just_clips:
            total_clips: int = 0
            for single_item in self._items:
                if isinstance(single_item, Clip):
                    total_clips += 1
            return total_clips

        return super().len()


    def finish(self) -> ra.Position:
        """
        Processes each element Position plus Length and returns the finish position
        as the maximum of all of them.

        Args:
            None

        Returns:
            Position: The maximum of Position + Length of all Elements.
        """
        finish_position: ra.Position = None

        clips_list: list[Clip] = [
            clip for clip in self._items if isinstance(clip, Clip)
        ]

        if len(clips_list) > 0:

            for clip in clips_list:

                clip_finish: ra.Position = clip.finish()
                if clip_finish:
                    if finish_position:
                        if clip_finish > finish_position:
                            finish_position = clip_finish
                    else:
                        finish_position = clip_finish

        return finish_position

    def last(self) -> oe.Element:

        part_last: oe.Element = None

        clips_list: list[Clip] = [
            clip for clip in self._items if isinstance(clip, Clip)
        ]

        if len(clips_list) > 0:

            for clip in clips_list:

                clip_last: oe.Element = clip.last()
                if clip_last:
                    if part_last:
                        if clip_last > part_last:
                            part_last = clip_last
                    else:
                        part_last = clip_last

        return part_last

    def last_position(self) -> ra.Position:
        last_element: oe.Element = self.last()

        if last_element:
            return last_element % ra.Position()
        
        return None


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case ra.Position():
                        return operand._data << self._staff_reference.convertToPosition(ra.Beats(self._position_beats))
                    case _:                 return super().__mod__(operand)
            case ra.Position():
                return self._staff_reference.convertToPosition(ra.Beats(self._position_beats))
            case _:
                return super().__mod__(operand)


    def getPlaylist(self) -> list:
        play_list: list = []
        for single_clip in self:
            if isinstance(single_clip, (Clip, od.Playlist)):
                part_position: ra.Position = self // ra.Position()
                play_list.extend(single_clip.getPlaylist(part_position))
        return play_list

    def getMidilist(self) -> list:
        midi_list: list = []
        for single_clip in self:
            if isinstance(single_clip, Clip):   # Can't get Midilist from Playlist !
                part_position: ra.Position = self // ra.Position()
                midi_list.extend(single_clip.getMidilist(part_position))
        return midi_list

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["position"] = self.serialize(self._position_beats)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position_beats = self.deserialize(serialization["parameters"]["position"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Part():
                super().__lshift__(operand)
                self._position_beats    = operand._position_beats
                self._staff_reference             << operand._staff_reference
                
            case od.DataSource():
                match operand._data:
                    case ra.Position():     self._position_beats = self._staff_reference.convertToBeats(operand._data)._rational
                    case _:                 super().__lshift__(operand)

            case ra.Position() | ra.TimeValue():
                self._position_beats = self._staff_reference.convertToBeats(operand)._rational
            case Clip() | oe.Element():
                self += operand
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._items = [
                    self.deep_copy(item) for item in operand if isinstance(item, (Clip, od.Playlist))
                ]
                self._sort_position()
            case tuple():
                for single_operand in operand:
                    self << single_operand

            case Composition():
                self.set_staff_reference(operand.get_staff_reference())

            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item << operand
        return self


    # Pass trough method that always results in a Part (Self)
    def __rshift__(self, operand) -> Self:
        match operand:
            case Part() | Clip() | oe.Element() | od.Playlist():
                self *= operand
                return self
        return super().__rshift__(operand)


    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Part():
                self._append(self.deep_copy(operand._items))
            case Clip() | od.Playlist():
                self._append([ operand.copy() ])
            case oe.Element():
                element_clip: Clip = Clip(operand)
                self._append([ element_clip ])
            case ra.Position() | ra.TimeValue():
                self << self % ra.Position() + operand
            case list():
                self._append(self.deep_copy(operand))
            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item += operand
        return self

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Part():
                return self._delete(operand._items)
            case Clip() | od.Playlist():
                return self._delete(operand)
            case ra.Position() | ra.TimeValue():
                self << self % ra.Position() - operand
            case list():
                return self._delete(operand)
            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item -= operand
        return self

    def __imul__(self, operand: any) -> Self:
        match operand:
            case Part():
                operand_copy: Part = operand.copy()
                add_measure: ou.Measure = ou.Measure(0)
                # It's the position of the element that matters and not their tailed Duration
                last_position: ra.Position = self.last_position()
                if last_position:
                    add_measure = ou.Measure(1) + last_position.roundMeasures()
                # Clips have no Position, so, it's implicit position is always 0
                for clip_or_playlist in operand_copy._items:
                    clip_or_playlist += add_measure
                    self._append([ clip_or_playlist ])
            case Clip() | od.Playlist():
                add_measure: ou.Measure = ou.Measure(0)
                # It's the position of the element that matters and not their tailed Duration
                last_position: ra.Position = self.last_position()
                if last_position:
                    add_measure = ou.Measure(1) + last_position.roundMeasures()
                # Clips have no Position, so, it's implicit position is always 0
                self._append([ operand + add_measure ])
            case oe.Element():
                operand_copy: Part = operand.copy()
                add_measure: ou.Measure = ou.Measure(0)
                # It's the position of the element that matters and not their tailed Duration
                last_position: ra.Position = self.last_position()
                if last_position:
                    add_measure = ou.Measure(1) + last_position.roundMeasures()
                # Clips have no Position, so, it's implicit position is always 0
                clip_operand: Clip = Clip(operand)
                clip_operand += add_measure
                self._append([ clip_operand ])
            case tuple():
                for single_operand in operand:
                    self *= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item *= operand
        return self

    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case tuple():
                for single_operand in operand:
                    self /= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item /= operand
        return self


class Song(Composition):
    def __init__(self, *operands):
        self._staff: og.Staff = og.defaults._staff.copy()
        super().__init__()
        self._items: list[Part] = []
        for single_operand in operands:
            self << single_operand


    def __getitem__(self, key: int) -> Part:
        return self._items[key]

    def __next__(self) -> Part:
        return super().__next__()
    

    def _sort_position(self) -> Self:
        if self is not self._upper_container:
            self._upper_container._sort_position()
        self._items.sort(key=lambda x: x._position_beats)
        return self


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> Self:
        if isinstance(staff_reference, og.Staff):
            self._staff << staff_reference  # Does a copy
        for single_part in self._items:
            single_part.set_staff_reference(self._staff)
            single_part.set_song_reference(self)
        return self

    def get_staff_reference(self) -> 'og.Staff':
        return self._staff

    def reset_staff_reference(self) -> Self:
        self._staff = og.defaults._staff.copy()
        for single_part in self._items:
            single_part.set_staff_reference(self._staff)
        return self

    def test_staff_reference(self) -> bool:
        for single_part in self._items:
            if single_part._staff_reference is not self._staff:
                return False
        return True


    def finish(self) -> ra.Position:

        finish_position: ra.Position = None

        if self.len() > 0:

            for part in self._items:

                part_finish: ra.Position = part.finish()
                if part_finish:
                    if finish_position:
                        if part_finish > finish_position:
                            finish_position = part_finish
                    else:
                        finish_position = part_finish

        return finish_position


    def last_position(self) -> ra.Position:

        last_part: Part = self.last()
        if last_part:
            last_part_element: oe.Element = last_part.last()
            if last_part_element:
                return last_part % ra.Position() + last_part_element % ra.Position()
        
        return None


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case og.Staff():        return self._staff
                    case _:                 return super().__mod__(operand)
            case og.Staff():        return self._staff.copy()
            case ra.StaffParameter() | ou.KeySignature() | ou.Accidentals() | ou.Major() | ou.Minor() | og.Scale() | ra.Measures() | ou.Measure() \
                | float() | Fraction():
                return self._staff % operand
            case _:
                return super().__mod__(operand)


    def getPlaylist(self) -> list:
        play_list: list = []
        for single_part in self:
            play_list.extend(single_part.getPlaylist())
        return play_list

    def getMidilist(self) -> list:
        midi_list: list = []
        for single_part in self:
            midi_list.extend(single_part.getMidilist())
        return midi_list

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["staff"] = self.serialize(self._staff)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._staff = self.deserialize(serialization["parameters"]["staff"])
            self.set_staff_reference()
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Song():
                super().__lshift__(operand)
                self.set_staff_reference(operand.get_staff_reference())

            case od.DataSource():
                match operand._data:
                    case og.Staff():        self._staff = operand._data
                    case _:                 super().__lshift__(operand)

            case Part() | Clip() | oe.Element():
                self += operand
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case og.Staff() | ou.KeySignature() | og.TimeSignature() | ra.StaffParameter() | ou.Accidentals() | ou.Major() | ou.Minor():
                self._staff << operand
            case list():
                self._items = [
                    self.deep_copy(item) for item in operand if isinstance(item, Part)
                ]
                self._sort_position()
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for single_part in self._items:
                    single_part << operand
        return self


    # Pass trough method that always results in a Song (Self)
    def __rshift__(self, operand) -> Self:
        match operand:
            case Song() | Part() | Clip() | oe.Element() | od.Playlist():
                self *= operand # Stacks by Measure
                return self
        return super().__rshift__(operand)


    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Song():
                for single_part in operand._items:
                    self._append([ single_part.copy().set_staff_reference(self._staff) ])
                self._sort_position()
            case Part():
                self._append([ operand.copy().set_staff_reference(self._staff) ])._sort_position()
            case Clip() | od.Playlist():
                clip_part: Part = Part(operand).set_staff_reference(self._staff)
                self._append([ clip_part ])._sort_position()
            case oe.Element():
                element_clip: Clip = Clip(operand) << self._staff
                clip_part: Part = Part(element_clip).set_staff_reference(self._staff)
                self._append([ clip_part ])._sort_position()
            case list():
                for item in operand:
                    if isinstance(item, Part):
                        self._append([ item.copy().set_staff_reference(self._staff) ])
                self._sort_position()
            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item += operand
        return self


    def __imul__(self, operand: any) -> Self:
        match operand:
            case Song():
                if operand.len() > 0:
                    operand_first_position: ra.Position = operand[0] % ra.Position()
                    self_last_position: ra.Position = self.last_position()
                    if self_last_position:
                        position_offset: ra.Position = \
                            self_last_position.roundMeasures() + ou.Measure(1) - operand_first_position
                        # Beats are the common unit of measurement across multiple Time Signatures !!
                        for single_part in operand._items:
                            new_part: Part = single_part.copy().set_staff_reference(self._staff)
                            new_part += position_offset
                            self._append([ new_part ])
                    else:
                        for single_part in operand._items:
                            new_part: Part = single_part.copy().set_staff_reference(self._staff)
                            new_part -= operand_first_position
                            self._append([ new_part ])
                self._sort_position()
            case Part():
                if operand.len() > 0:
                    self_last_position: ra.Position = self.last_position()
                    next_position: ra.Position = self_last_position.roundMeasures() + ou.Measure(1)
                    new_part: Part = operand.copy().set_staff_reference(self._staff) << next_position
                    self._append([ new_part ])._sort_position()
            case Clip() | od.Playlist():
                clip_part: Part = Part(operand)
                self *= clip_part
            case oe.Element():
                element_part: Part = Part( Clip(operand) << self._staff )
                self *= element_part
                
            case tuple():
                for single_operand in operand:
                    self *= single_operand

            case Composition():
                self.set_staff_reference(operand.get_staff_reference())

            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item *= operand
        return self

    def stack(self, non_empty_measures_only: bool = True) -> Self:
        for index, single_part in enumerate(self._items):
            if index > 0:   # Not following Parts
                previous_part: Part = self._items[index - 1]
                next_position: ra.Position = previous_part.last_position()
                if next_position:
                    next_position = next_position.roundMeasures() + ou.Measure(1)
                else:
                    next_position = ra.Position(0)
                single_part << next_position
            else:           # THE FIRST PART!
                single_part._position_beats = Fraction(0)   # everything starts at the beginning (0)!
        
        return self._sort_position()    # May be needed due to upper clips
    
