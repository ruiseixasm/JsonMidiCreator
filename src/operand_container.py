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
import math
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
    from matplotlib.backend_bases import MouseEvent
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
    """`Container`

    Container represents an `Operand` that contains multiple items, the typical case
    is the `Clip` with multiple `Element` items in it.

    Parameters
    ----------
    list([]) : Any type of parameter can be used to be added as item.
    int : Returns the len of the list.
    """
    def __init__(self, *operands):
        super().__init__()
        self._items: list = []
        self._items_iterator: int = 0
        self._base_container: Self = self
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
        if self is not self._base_container:
            self._base_container._insert(items, before_item)
        insert_at: int = 0                  # By default works as insert
        if before_item is not None:
            for index, single_item in enumerate(self._items):
                # if single_item == before_item:
                if single_item is before_item:
                    insert_at = index       # Before the item
                    break
        existing_ids: set[int] = {id(existing_item) for existing_item in self._items}
        inexistent_items: list = [inexistent_item for inexistent_item in items if id(inexistent_item) not in existing_ids]
        self._items = self._items[:insert_at] + inexistent_items + self._items[insert_at:]
        return self

    def _append(self, items: list, after_item: any = None) -> Self:
        if self.is_a_mask():
            self._base_container._append(items, after_item)
        append_at: int = len(self._items)   # By default works as append
        if after_item is not None:
            for index, single_item in enumerate(self._items):
                if single_item is after_item:
                    append_at = index + 1   # After the item
                    break
        existing_ids: set[int] = {id(existing_item) for existing_item in self._items}
        inexistent_items: list = [inexistent_item for inexistent_item in items if id(inexistent_item) not in existing_ids]
        self._items = self._items[:append_at] + inexistent_items + self._items[append_at:]
        return self

    def _delete(self, items: list = None, by_id: bool = False) -> Self:
        if self is not self._base_container:
            self._base_container._delete(items)
        if items is None:
            self._items.clear()
            self._base_container._items.clear()
        else:
            if by_id:
                # removes by id instead
                self._items = [
                    single_item for single_item in self._items
                    if not any(single_item is item for item in items)
                ]
            else:
                # Uses "==" instead of id
                self._items = [
                    single_item for single_item in self._items
                    if single_item not in items
                ]
        return self

    def _delete_by_ids(self, item_ids: set | None = None):
        if isinstance(item_ids, set):
            if item_ids:
                self._base_container._items = [
                    base_item for base_item in self._base_container._items
                    if id(base_item) not in item_ids
                ]
                self._items = [
                    mask_item for mask_item in self._items
                    if id(mask_item) not in item_ids
                ]
        else:
            self._base_container._items.clear()
            self._items.clear()
        return self


    def _replace(self, old_item: Any = None, new_item: Any = None) -> Self:
        if self is not self._base_container:
            self._base_container._replace(old_item, new_item)
        for index, item in enumerate(self._items):
            if old_item is item:
                self._items[index] = new_item
        return self

    def _swap(self, left_item: Any = None, right_item: Any = None) -> Self:
        if self is not self._base_container:
            self._base_container._swap(left_item, right_item)
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


    def _sort_items(self) -> Self:
        # This works with a list method sort
        self._base_container._items.sort()  # Operands implement __lt__ and __gt__
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
            case od.Pipe():
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
                if operand: # Non empty list
                    parameters: list = []
                    for single_item in self._items:
                        item_parameter: any = single_item
                        for single_parameter in operand:
                            item_parameter = item_parameter % single_parameter
                        parameters.append( item_parameter )
                    return parameters
                return [
                    self.deep_copy(item) for item in self._items
                ]
            case int():
                return self.len()
            case bool():
                return not self.is_a_mask()
            case _:
                return super().__mod__(operand)

    def len(self) -> int:
        """
        Returns the total number of items.def erase

        Args:
            None

        Returns:
            int: Returns the equivalent to the len(self._items).
        """
        return len(self._items)

    def first(self) -> Any:
        """
        Gets the first Item accordingly to it's Position on the TimeSignature.

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
        Gets the last Item accordingly to it's Position on the TimeSignature.

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
        match other:
            case Container():
                return self._items == other._items
            case od.Conditional():
                return other == self
            case of.Frame():
                for single_item in self._items:
                    if not single_item == other:
                        return False
                return True
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
        if isinstance(other, of.Frame):
            for single_clip in self._items:
                if not single_clip < other:
                    return False
            return True
        return self % other < other

    def __gt__(self, other: any) -> bool:
        if isinstance(other, of.Frame):
            for single_clip in self._items:
                if not single_clip > other:
                    return False
            return True
        return self % other > other

    def getPlaylist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        return []

    def getMidilist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        return []

    def getSerialization(self) -> dict:
        """
        Returns the serialization in a form of a dictionary of `Container` parameters.

        Args:
            None

        Returns:
            dict: A dictionary with multiple the `Container` configuration.
        """
        serialization = super().getSerialization()

        serialization["parameters"]["items"] = self.serialize(self._base_container._items)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        """
        Sets all `Container` parameters based on a dictionary input previously generated by `getSerialization`.

        Args:
            serialization: A dictionary with all the `Container` parameters.

        Returns:
            Container: The self Container object with the respective set parameters.
        """
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "items" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._items = self.deserialize(serialization["parameters"]["items"])
            self._base_container = self # Not a mask anymore if one
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Container():
                super().__lshift__(operand)

                if not (self.is_a_mask() or operand.is_a_mask()):
                    self._items = self.deep_copy(operand._items)

                elif self.is_a_mask() and operand.is_a_mask():
                    self_base: Container = self._base_container
                    operand_base: Container = operand._base_container
                    self_base._items = self.deep_copy(operand_base._items)
                    unmasked_ids: set[int] = {id(unmasked_item) for unmasked_item in operand._items}
                    self._items = [
                        self_base._items[index] for index, root_item in enumerate(operand_base._items)
                        if id(root_item) in unmasked_ids
                    ]

                elif self.is_a_mask():
                    self._base_container = self # Not a mask anymore
                    self._items = self.deep_copy(operand._items)

                else:   # operand.is_a_mask(), so, self shall become a mask too
                    self_base: Container = self.empty_copy()
                    self._base_container = self_base
                    operand_base: Container = operand._base_container
                    self_base._items = self.deep_copy(operand_base._items)
                    unmasked_ids: set[int] = {id(unmasked_item) for unmasked_item in operand._items}
                    self._items = [
                        self_base._items[index] for index, root_item in enumerate(operand_base._items)
                        if id(root_item) in unmasked_ids
                    ]

            case od.Pipe():
                match operand._data:
                    case list():
                        # Remove previous Elements from the Container stack
                        self._delete(self._items, True) # deletes by id, safer
                        # Finally adds the decomposed elements to the Container stack
                        self._append( operand._data )
                        # for item in operand._data:
                        #     self._append([ item ])
            case od.Serialization():
                self._base_container.loadSerialization( operand.getSerialization() )
            case list():
                # Remove previous Elements from the Container stack
                self._delete(self._items, True) # deletes by id, safer
                # Finally adds the decomposed elements to the Container stack
                self._append([
                    self.deep_copy(item) for item in operand
                ])
            case dict():
                for index, item in operand.items():
                    if isinstance(index, int) and index >= 0 and index < len(self._items):
                        self._items[index] = self.deep_copy(item)
                        
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
        match operand:
            case Container():
                return self + operand   # Implicit copy of self
            case og.Process():
                return operand.__rrshift__(self)
            case ch.Chaos():
                return self.copy().shuffle(operand)
        if not isinstance(operand, tuple):
            return self.mask(operand)
        return super().__irshift__(operand)

    # Pass trough method that always results in a Container (Self)
    def __irshift__(self, operand) -> Self:
        match operand:
            case Container():
                self += operand
                return self
            case og.Process():
                return operand.__irrshift__(self)
            case ch.Chaos():
                return self.shuffle(operand)
        if not isinstance(operand, tuple):
            return self.mask(operand)
        return super().__irshift__(operand)


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
                        self._delete([ self._items.pop() ], True)
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
                        new_items: list = [
                            self.deep_copy( data ) for data in items_copy
                        ]
                        self._append(new_items)  # Propagates upwards in the stack
                        # self._items.extend(
                        #     self.deep_copy( data ) for data in items_copy
                        # )
                        operand -= 1
                    self._append(items_copy)  # Propagates upwards in the stack
                    # self._items.extend( items_copy )
                elif operand == 0:
                    self._delete(self._base_container._items, True)
            case ch.Chaos():
                return self.shuffle(operand.copy())
            case tuple():
                for single_operand in operand:
                    self.__imul__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__imul__(operand)
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
                    cut_len: int = self.len() % od.Pipe( operand )
                    nth_item: int = cut_len
                    while nth_item > 0:
                        many_operands._items.append(
                                self.deep_copy( self._items[cut_len - nth_item] )
                            )
                        nth_item -= 1
                    return many_operands

            case tuple():
                for single_operand in operand:
                    self.__itruediv__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__itruediv__(operand)
        return self


    def empty_copy(self, *parameters) -> Self:
        """
        Returns a Container with all the same parameters but the list that is empty.

        Args:
            *parameters: Any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Container: Returns the copy of self but with an empty list of items.
        """
        empty_base: Container = self._base_container.__class__()
        for single_parameter in parameters: # Parameters should be set on the base container
            empty_base << single_parameter
        if self.is_a_mask():
            empty_mask: Container = self.__class__()
            empty_mask._base_container = empty_base
            return empty_mask
        return empty_base

    # A shallow copy isn't the same as a mask!
    def shallow_copy(self, *parameters) -> Self:
        """
        Returns a Container with all the same parameters copied, but the list that
        is just a reference of the same list of the original container.

        Args:
            *parameters: Any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Container: Returns the copy of self but with a list of the same items of the original one.
        """
        shallow_copy: Container = self.empty_copy()
        # This copy of a list is a shallow copy, not a deep copy
        shallow_copy._items = self._items.copy()
        for single_parameter in parameters: # Parameters should be set on the base container
            shallow_copy._base_container << single_parameter
        if shallow_copy.is_a_mask():
            shallow_copy._base_container._items = self._base_container._items.copy()
        return shallow_copy
    

    def process(self, input: any = None) -> Self:
        return self >> input

    def clear(self, *parameters) -> Self:
        self._delete(self._items, True)
        return super().clear(parameters)
    
    def erase(self, *parameters) -> Self:
        """
        Erases all the given items in the present container and propagates the deletion
        of the same items for the containers above.

        Args:
            *parameters: After deletion, any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Clip: Returns an empty self but with all the rest parameters untouched except the ones
            changed by the imputed Args.
        """
        self._delete(self._items, True)
        for single_parameter in parameters:
            self << single_parameter
        return self

    def is_a_mask(self) -> bool:
        return self._base_container is not self
    
    def upper(self, level: int = None) -> Self:
        """
        Returns self or the upper container if existent up to the last one if no argument is given, or,
        up to the one above the level given.

        Args:
            level: The level at which the upper container is returned.

        Returns:
            Clip: Returns the upper container if existent or self otherwise.
        """
        if self._base_container is self:
            return self
        if isinstance(level, int):
            if level > 0:
                level -= 1
            else:
                return self
        return self._base_container.upper(level)

    def sort(self, parameter: type = ra.Position, reverse: bool = False) -> Self:
        """
        Sorts the self list based on a given type of parameter.

        Args:
            parameter (type): The type of parameter being sorted by.

        Returns:
            Container: The same self object with the items processed.
        """
        compare = parameter()
        sorted_items: list = self._items.copy().sort(
            key=lambda x: x % compare
        )
        self << od.Pipe( sorted_items )
        if reverse:
            self._items.reverse()
        return self

    def shuffle(self, chaos: ch.Chaos = None, parameter: type = ra.Position) -> Self:
        """
        Reaffects the given parameter type in a chaotic manner.

        Args:
            chaos (Chaos): An Chaos object to be used as sorter.
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
        return self._sort_items()

    def swap(self, left: Union[o.Operand, list, int] = 0, right: Union[o.Operand, list, int] = 1, what: type = ra.Position) -> Self:
        """
        This method swaps a given parameter type between two operands.

        Args:
            left (any): The first item or `Segment` data.
            right (any): The second item or `Segment` data.
            what (type): The parameter type that will be swapped between both left and right.

        Returns:
            Container: The same self object with the operands processed.
        """
        import operand_generic as og
        if what == og.Segment:
            left_segment: og.Segment = og.Segment(left)
            right_segment: og.Segment = og.Segment(right)
            if left_segment.len() == right_segment.len():
                left_mask: Clip = self.mask(left_segment)
                right_mask: Clip = self.mask(right_segment)
                left_mask << right_segment
                right_mask << left_segment
        else:
            if self.len() > 0 and isinstance(what, type):
                if isinstance(left, int):
                    left = self[left]
                if isinstance(right, int):
                    right = self[right]
                if isinstance(left, o.Operand) and isinstance(right, o.Operand):
                    parameter_instance = what()
                    left_parameter: any = left % parameter_instance
                    left << right % parameter_instance
                    right << left_parameter
        return self._sort_items()

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
            self._swap(self._items[operand_i], self._items[self_len - 1 - operand_i])
            # tail_operand = self._items[self_len - 1 - operand_i]
            # self._items[self_len - 1 - operand_i] = self._items[operand_i]
            # self._items[operand_i] = tail_operand
        return self._sort_items()
    
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
        return self._sort_items()

    def rotate(self, left: int = 1, parameter: type = ra.Position) -> Self:
        """
        Rotates a given parameter by a given left amount, by other words,
        does a displacement for each Element in the Container list of
        a chosen parameter by the given left amount. Counterclockwise.

        Args:
            left (int): The left amount of the list index, displacement.
            parameter (type): The type of parameter being displaced, rotated.

        Returns:
            Container: The self object with the chosen parameter displaced.
        """
        parameter_instance = parameter()
        if isinstance(parameter_instance, od.Pipe):
            items: list = []
            for _ in len(self._items):
                item_index: int = left % len(self._items)
                items.append(self._items[item_index])   # No need to copy
                left += 1
            # Remove previous Elements from the Container stack
            self._delete(self._items, True) # deletes by id, safer
            # Finally adds the decomposed elements to the Container stack
            self._append(items)
        else:
            parameters: list = []
            for operand in self:
                if isinstance(operand, o.Operand):
                    parameters.append( operand % parameter_instance )
                else:
                    parameters.append( ol.Null() )
            for operand in self:
                if isinstance(operand, o.Operand):
                    operand << parameters[ left % len(parameters) ]
                left += 1
        return self._sort_items()


    def mask(self, *conditions) -> Self:
        """
        Masks the items that meet the conditions (equal to). No implicit copies.

        Conditions
        ----------
        Any : Conditions that need to be matched in an And fashion.

        Returns:
            Container Mask: A different object with a shallow copy of the original
            `Container` items now selected as a `Mask`.
        """
        new_mask: Container = self._base_container.shallow_copy()
        # This shallow copy is a mask, so it chains upper containers
        new_mask._base_container = self._base_container
        for single_condition in conditions:
            if isinstance(single_condition, Container):
                new_mask._items = [
                    base_item for base_item in self._base_container._items
                    if any(base_item == cond_item for cond_item in single_condition._base_container._items)
                ]
            else:
                new_mask._items = [
                    base_item for base_item in self._base_container._items
                    if base_item == single_condition
                ]
        return new_mask

    def base(self) -> Self:
        """
        Returns the base `Container` of a mask or self if already the base `Container`.

        Args:
            None

        Returns:
            Container: The same self object with the items processed.
        """
        return self._base_container


    def filter(self, *conditions) -> Self:
        """
        A `Filter` works exactly like a `Mask` with the difference of keeping just \
            the matching items and deleting everything else.

        Conditions
        ----------
        Any : Conditions that need to be matched in an `And` alike fashion.

        Returns:
            Container: The same self object with the items processed.
        """
        deletable_item_ids: set = set()
        # And type of conditions, not meeting any means excluded
        for single_condition in conditions:
            if isinstance(single_condition, Container):
                deletable_item_ids.update(
                    id(item) for item in self._base_container._items
                    if not any(item == cond_item for cond_item in single_condition._base_container._items)
                )
            else:
                deletable_item_ids.update(
                    id(item) for item in self._base_container._items
                    if not item == single_condition
                )
        return self._delete_by_ids(deletable_item_ids)


    def operate(self, operand: Any = None, operator: str = "<<") -> Self:
        """
        Allows the setting of a specific operator as operation with a str as operator symbol.

        Args:
            operand (Any): `Operand` that is the source of the operation.
            operator (str): The operator `op` that becomes processed as `self op operand`.

        Returns:
            Container: The same self object after the given processed operation.
        """
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
                self >>= operand
            case "<<=":
                self <<= operand
            case "^":
                self ^ operand
        return self

    def transform(self, operand_type: type = 'oe.Note') -> Self:
        """
        Transforms each item by wrapping it with the new operand type given.

        Args:
            operand_type (type): The type of `Operand` by which each item will be transformed into.

        Returns:
            Container: The same self object after the given processed items.
        """
        for item in self._items:
            self._replace(item, operand_type(item))
        return self



class Devices(Container):
    """`Container -> Devices`

    Represents a list of Devices to be passed to the clip track, these devices
    aren't supposed to be all connected but just the first one in the list able
    to be so end up being connected.

    Parameters
    ----------
    list([]) : A list of Devices names, str, are intended to be considered Items.
    str : A device name to be added to the beginning of the Devices list.
    int : Returns the len of the list.
    """
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
    """`Container -> Devices -> ClockedDevices`

    Represents a list of Devices passed to the clip staff, all these devices are intended
    to be connected as destiny of the generated Clock messages by the JsonMidiPlayer.

    Parameters
    ----------
    list([]) : A list of Devices names, str, are intended to be considered Items.
    str : A device name to be added to the beginning of the Devices list.
    int : Returns the len of the list.
    """
    pass



class Composition(Container):
    """`Container -> Composition`

    A Composition is no more than the immediate super class of `Clip`, `Part` and `Song`.

    Parameters
    ----------
    list([]) : A list of Items accordingly to the accepted type by the sub class.
    int : Returns the len of the list.
    """
    def __init__(self, *operands):
        super().__init__()
        self._base_container: Composition = self
        # Song sets the TimeSignature, this is just a reference
        self._time_signature: og.TimeSignature  = og.settings._time_signature
        self._length_beats: Fraction            = None


    def _get_time_signature(self) -> 'og.TimeSignature':
        return og.settings._time_signature


    def _first_element(self) -> 'oe.Element':
        """
        Gets the first Element accordingly to it's Position on the TimeSignature.

        Args:
            None

        Returns:
            Element: The first Element of all Elements.
        """
        return super().first()

    def _last_element(self) -> 'oe.Element':
        """
        Gets the last Element accordingly to it's Position on the TimeSignature.

        Args:
            None

        Returns:
            Element: The last Element of all Elements.
        """
        return super().last()

    def _last_element_position(self) -> 'ra.Position':
        """
        Gets the last Element position.

        Args:
            None

        Returns:
            Position: The Position fo the last Element.
        """
        last_element: oe.Element = self._last_element()
        if last_element is not None:
            return last_element % ra.Position()
        return None


    def checksum(self) -> str:
        return "0000" # 4 hexadecimal chars sized 16^4 = 65_536

    def composition_filename(self, title: str = "composition") -> str:
        # Process title separately (replace whitespace with underscores)
        processed_title = str(title).replace(" ", "_").replace("\t", "_").replace("\n", "_").replace("__", "_")
        composition_designations: list[str] = [
            processed_title,
            type(self).__name__,
            self.checksum()
        ]
        # 1. Filter empty strings and convert all parts to lowercase
        filtered_strings = [
            designation.strip().lower() 
            for designation in composition_designations 
            if designation
        ]
        # 2. Join with single underscore (no leading/trailing/double underscores)
        return "_".join(filtered_strings)


    def masked_element(self, element: oe.Element) -> bool:
        return False

    # Ignores the self Length
    def start(self) -> 'ra.Position':
        """
        Gets the starting position of all its Elements.
        This is the same as the minimum Position of all `Element` positions.

        Args:
            None

        Returns:
            Position: The minimum Position of all Elements.
        """
        return None


    # Ignores the self Length
    def finish(self) -> 'ra.Position':
        """
        Processes each element Position plus Length and returns the finish position
        as the maximum of all of them.

        Args:
            None

        Returns:
            Position: The maximum of Position + Length of all Elements.
        """
        return None


    def length(self) -> 'ra.Length':
        """
        Returns the rounded `Length` to `Measures` that goes from 0 to position of the last `Element`.

        Args:
            None

        Returns:
            Length: Equal to last `Element` position converted to `Length` and rounded by `Measures`.
        """
        last_position: ra.Position = self._last_element_position()
        if last_position is not None:
            return ra.Length( last_position.roundMeasures() ) + ra.Measures(1)
        return ra.Length(self)
    
    
    def duration(self) -> 'ra.Duration':
        """
        Returns the `Duration` that goes from 0 to the `finish` of all elements.

        Args:
            None

        Returns:
            Duration: Equal to `Clip.finish()` converted to `Duration`.
        """
        self_finish: ra.Position = self.finish()
        if self_finish is not None:
            return ra.Duration(self.finish())
        return ra.Duration(self)
    
    def net_duration(self) -> 'ra.Duration':
        """
        Returns the `Duration` that goes from `start` to the `finish` of all elements.

        Args:
            None

        Returns:
            Duration: Equal to `Clip.finish() - Clip.start()` converted to `Duration`.
        """
        self_start: ra.Position = self.start()
        self_finish: ra.Position = self.finish()
        if self_start is not None and self_finish is not None:
            return ra.Duration(self.finish() - self.start())
        return ra.Duration(self)
    

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Length():
                        if self._length_beats is not None:
                            return operand._data << ra.Length(self, self._length_beats)
                        return None
                    case _:                 return super().__mod__(operand)
            # By definition Clips are always at Position 0
            case ra.Position():
                return operand.copy( ra.Position(self, 0) )
            case ra.Length():
                if self._length_beats is not None:
                    return operand.copy( ra.Length(self, self._length_beats) )
                return operand.copy( self.length() )
            case ra.Duration():
                return self.duration()
            case og.TimeSignature():
                return self._time_signature % operand
            case _:
                return super().__mod__(operand)


    def get_unmasked_element_ids(self) -> set[int]:
        return set()

    def get_masked_element_ids(self) -> set[int]:
        return set()


    def getPlotlist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        """
        Returns the plotlist for a given Position.

        Args:
            position: The reference Position where the `Composition` starts at.

        Returns:
            list[dict]: A list with multiple Plot configuration dictionaries.
        """
        return []


    def getSerialization(self) -> dict:
        """
        Returns the serialization in a form of a dictionary of `Clip` parameters.

        Args:
            None

        Returns:
            dict: A dictionary with multiple the `Clip` configuration.
        """
        serialization = super().getSerialization()

        serialization["parameters"]["length"] = self.serialize(self._length_beats)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        """
        Sets all `Clip` parameters based on a dictionary input previously generated by `getSerialization`.

        Args:
            serialization: A dictionary with all the `Clip` parameters.

        Returns:
            Clip: The self Clip object with the respective set parameters.
        """
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "length" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._length_beats = self.deserialize(serialization["parameters"]["length"])
        return self


    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Composition():
                super().__lshift__(operand)
                self._length_beats = operand._length_beats

            case od.Pipe():
                match operand._data:
                    case ra.Length():
                        self._length_beats = operand._data._rational
                        if self._length_beats < 0:
                            self._length_beats = None
                    case None:              self._length_beats = None
                    case _:                 super().__lshift__(operand)

            case ra.Length():
                self._base_container._length_beats = operand._rational
                if self._base_container._length_beats < 0:
                    self._base_container._length_beats = None
            case None:
                self._base_container._length_beats = None

            case _:
                super().__lshift__(operand)

        return self


    def __floordiv__(self, operand: any) -> Self:
        return self.copy().__ifloordiv__(operand)
    
    def __ifloordiv__(self, operand: any) -> Self:
        return self
    

    def loop(self, position = 0, length = 4) -> Self:
        """
        Creates a loop from the Composition from the given `Position` with a given `Length`.

        Args:
            position (Position): The given `Position` where the loop starts at.
            length (Length): The `Length` of the loop.

        Returns:
            Composition: A copy of the self object with the items processed.
        """
        return self.empty_copy()


    def drop(self, *measures) -> Self:
        """
        Drops from the `Composition` all `Measure`'s given by the numbers as parameters.

        Parameters
        ----------
        int(), list(), tuple(), set() : Accepts a sequence of integers as the Measures to be dropped.

        Returns:
            Container: The same self object with the items removed if any.
        """
        return self

    def crop(self, *measures) -> Self:
        """
        Crops from the `Composition` all `Measure`'s given by the numbers as parameters.

        Parameters
        ----------
        int(), list(), tuple(), set() : Accepts a sequence of integers as the Measures to be cropped.

        Returns:
            Container: The same self object with the items removed if any.
        """
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
        """
        The method that does the heavy work of plotting
        """
        self._ax.clear()

        # Chart title (TITLE)
        self._ax.set_title(f"{self._title + " - " if self._title != "" else ""}"
                           f"{"Mask - " if self._iterations[self._iteration].is_a_mask() else ""}"
                           f"Iteration {self._iteration} of {len(self._iterations) - 1 if len(self._iterations) > 1 else 0
        }")


        # Horizontal X-Axis, Time related (COMMON)

        clip_tempo: float = float(plotlist[0]["tempo"])
        # # 1. Disable autoscaling and force limits
        # self._ax.set_autoscalex_on(False)
        # current_min, current_max = self._ax.get_xlim()
        # self._ax.set_xlim(current_min, current_max * 1.03)
        self._ax.margins(x=0)  # Ensures NO extra padding is added on the x-axis

        beats_per_measure: Fraction = self._time_signature % og.TimeSignature() % ra.BeatsPerMeasure() % Fraction()
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        steps_per_measure: Fraction = beats_per_measure / quantization_beats

        # By default it's 1 Measure long
        last_position: Fraction = beats_per_measure
        last_position_measures: Fraction = last_position / beats_per_measure
        last_position_measure: int = int(last_position / beats_per_measure)
        if last_position_measure != last_position_measures:
            last_position_measure += 1


        # Vertical Y-Axis, Pitch/Value related (SPECIFIC)
        plot_channels: list[dict] = [ channel_dict["channels"] for channel_dict in plotlist if "channels" in channel_dict ]

        note_channels: list[int] = []
        automation_channels: list[int] = []

        for element_channel in plot_channels:
            for note_channel in element_channel["note"]:
                if note_channel not in note_channels:
                    note_channels.append(note_channel)
            for automation_channel in element_channel["automation"]:
                if automation_channel not in automation_channels:
                    automation_channels.append(automation_channel)

                    
        # Plot Notes
        if note_channels or not automation_channels:

            if self._by_channel:
                self._ax.set_ylabel("Channels")

                # Where the corner Coordinates are defined
                self._ax.format_coord = lambda x, y: (
                    f"Time = {int(x / clip_tempo * 60 // 60)}'"
                    f"{int(x / clip_tempo * 60 % 60)}''"
                    f"{int(x / clip_tempo * 60_000 % 1000)}ms, "
                    f"Measure = {int(x / beats_per_measure)}, "
                    f"Beat = {int(x % beats_per_measure)}, "
                    f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                    f"Channel = {int(y + 1)}"
                )

                note_plotlist: list[dict] = [ element_dict["note"] for element_dict in plotlist if "note" in element_dict ]

                if note_plotlist:

                    # Updates X-Axis data
                    last_position = max(note["position_off"] for note in note_plotlist)
                    last_position_measures = last_position / beats_per_measure
                    last_position_measure = int(last_position_measures) # Trims extra length
                    if last_position_measure != last_position_measures: # Includes the trimmed length
                        last_position_measure += 1  # Adds only if the end doesn't coincide

                    # CHANNELS VERTICAL AXIS

                    # Shade black keys
                    for channel in range(16):
                        if channel % 2 == 1:
                            self._ax.axhspan(channel - 0.5, channel + 0.5, color='lightgray', alpha=0.5)

                    # Plot notes
                    for channel in note_channels:
                        channel_color = Clip._channel_colors[channel - 1]
                        channel_plotlist = [
                            channel_note for channel_note in note_plotlist
                            if channel_note["channel"] == channel
                        ]

                        for note in channel_plotlist:
                            if type(note["self"]) is oe.Rest:
                                # Available hatch patterns: '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'
                                self._ax.barh(y = note["channel"] - 1, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                        height=0.20, color=channel_color, hatch='//', edgecolor='gray', linewidth=1, linestyle='dotted', alpha = 1)
                            else:
                                bar_hatch: str = ''
                                line_style: str = 'solid'
                                if isinstance(note["self"], oe.KeyScale):
                                    line_style = 'dashed'
                                elif isinstance(note["self"], oe.Retrigger):
                                    line_style = 'dotted'
                                edge_color: str = 'black'
                                color_alpha: float = round(0.3 + 0.7 * (note["velocity"] / 127), 2)
                                if note["velocity"] > 127:
                                    edge_color = 'red'
                                    color_alpha = 1.0
                                elif note["velocity"] < 0:
                                    edge_color = 'blue'
                                    color_alpha = 1.0

                                if note["masked"]:
                                    color_alpha = 0.2
                                
                                self._ax.barh(y = note["channel"] - 1, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                        height=0.5, color=channel_color, hatch=bar_hatch, edgecolor=edge_color, linewidth=1, linestyle=line_style, alpha = color_alpha)

                                if "middle_pitch" in note:
                                    self._ax.hlines(y=note["channel"] - 1, xmin=float(note["position_on"]), xmax=float(note["position_off"]), 
                                                    color='black', linewidth=0.5, alpha = color_alpha)
                
                    # Set MIDI channel ticks with Middle C in bold
                    self._ax.set_yticks(range(16))
                    y_labels = [
                        channel + 1 for channel in range(16)
                    ]
                    self._ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')
                    self._ax.set_ylim(0 - 0.5, 15 + 0.5)  # Ensure all channels fit


            else:

                self._ax.set_ylabel("Chromatic Keys")
                # Where the corner Coordinates are defined
                self._ax.format_coord = lambda x, y: (
                    f"Time = {int(x / clip_tempo * 60 // 60)}'"
                    f"{int(x / clip_tempo * 60 % 60)}''"
                    f"{int(x / clip_tempo * 60_000 % 1000)}ms, "
                    f"Measure = {int(x / beats_per_measure)}, "
                    f"Beat = {int(x % beats_per_measure)}, "
                    f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                    f"Pitch = {int(y + 0.5)}"
                )

                note_plotlist: list[dict] = [ element_dict["note"] for element_dict in plotlist if "note" in element_dict ]

                if note_plotlist:

                    # Updates X-Axis data
                    last_position = max(note["position_off"] for note in note_plotlist)
                    last_position_measures = last_position / beats_per_measure
                    last_position_measure = int(last_position_measures) # Trims extra length
                    if last_position_measure != last_position_measures: # Includes the trimmed length
                        last_position_measure += 1  # Adds only if the end doesn't coincide

                    # PITCHES VERTICAL AXIS

                    # Get pitch range
                    min_pitch: int = min(note["pitch"] for note in note_plotlist) // 12 * 12
                    max_pitch: int = max(note["pitch"] for note in note_plotlist) // 12 * 12 + 12

                    pitch_range: int = max_pitch - min_pitch
                    if pitch_range // 12 < 4:   # less than 4 octaves
                        middle_c_reference: int = 60    # middle C pitch
                        extra_octaves_range: int = 4 - pitch_range // 12
                        for _ in range(extra_octaves_range):
                            raised_top: int = max_pitch + 12
                            lowered_bottom: int = min_pitch - 12
                            if abs(raised_top - middle_c_reference) < abs(lowered_bottom - middle_c_reference):
                                max_pitch += 12
                            else:
                                min_pitch -= 12


                    # Shade black keys
                    for channel in range(min_pitch, max_pitch + 1):
                        if o.is_black_key(channel):
                            self._ax.axhspan(channel - 0.5, channel + 0.5, color='lightgray', alpha=0.5)

                    # Plot notes
                    for channel in note_channels:
                        channel_color = Clip._channel_colors[channel - 1]
                        channel_plotlist = [
                            channel_note for channel_note in note_plotlist
                            if channel_note["channel"] == channel
                        ]

                        for note in channel_plotlist:
                            if type(note["self"]) is oe.Rest:
                                # Available hatch patterns: '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'
                                self._ax.barh(y = note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                        height=0.20, color=channel_color, hatch='//', edgecolor='gray', linewidth=1, linestyle='dotted', alpha = 1)
                            else:
                                bar_hatch: str = ''
                                line_style: str = 'solid'
                                if isinstance(note["self"], oe.KeyScale):
                                    line_style = 'dashed'
                                elif isinstance(note["self"], oe.Retrigger):
                                    line_style = 'dotted'
                                edge_color: str = 'black'
                                color_alpha: float = round(0.3 + 0.7 * (note["velocity"] / 127), 2)
                                if note["velocity"] > 127:
                                    edge_color = 'red'
                                    color_alpha = 1.0
                                elif note["velocity"] < 0:
                                    edge_color = 'blue'
                                    color_alpha = 1.0
                                
                                if note["masked"]:
                                    color_alpha = 0.2
                                
                                self._ax.barh(y = note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                        height=0.5, color=channel_color, hatch=bar_hatch, edgecolor=edge_color, linewidth=1, linestyle=line_style, alpha = color_alpha)

                                if "middle_pitch" in note:
                                    self._ax.hlines(y=note["middle_pitch"], xmin=float(note["position_on"]), xmax=float(note["position_off"]), 
                                                    color='black', linewidth=0.5, alpha = color_alpha)
                

                    # Where the VERTICAL axis is defined - Chromatic Keys
                    chromatic_keys: list[str] = ["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"]
                    # Set MIDI note ticks with Middle C in bold
                    self._ax.set_yticks(range(min_pitch, max_pitch + 1))
                    y_labels = [
                        chromatic_keys[pitch % 12] + (str(pitch // 12 - 1) if pitch % 12 == 0 else "")
                        for pitch in range(min_pitch, max_pitch + 1)
                    ]  # Bold Middle C
                    self._ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')
                    self._ax.set_ylim(min_pitch - 0.5, max_pitch + 0.5)  # Ensure all notes fit

        
        # Plot Automations
        else:

            self._ax.set_ylabel("Automation Values (MSB)")
            # Where the corner Coordinates are defined
            self._ax.format_coord = lambda x, y: (
                f"Time = {int(x / clip_tempo * 60 // 60)}'"
                f"{int(x / clip_tempo * 60 % 60)}''"
                f"{int(x / clip_tempo * 60_000 % 1000)}ms, "
                f"Measure = {int(x / beats_per_measure)}, "
                f"Beat = {int(x % beats_per_measure)}, "
                f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                f"Value = {int(y + 0.5)}"
            )

            automation_plotlist: list[dict] = [ element_dict["automation"] for element_dict in plotlist if "automation" in element_dict ]

            if automation_plotlist:

                # Updates X-Axis data
                last_position = max(automation["position"] for automation in automation_plotlist)
                last_position_measures = last_position / beats_per_measure
                last_position_measure = int(last_position_measures)
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
                        
                        if automation["masked"]:
                            color_alpha = 0.2
                        else:
                            color_alpha = 1.0
                                
                        # Actual data points
                        self._ax.plot(x, y, marker='o', linestyle='None', color=channel_color,
                                    markeredgecolor='black', markeredgewidth=1, markersize=8, alpha = color_alpha)

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
        four_measures_multiple: int = max(4, (last_position_measure - 1) // 4 * 4 + 4)
        step_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), float(quantization_beats))
        beat_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), 1)
        measure_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), float(beats_per_measure))
    
        for measure_pos in measure_positions:
            self._ax.axvline(measure_pos, color='black', linestyle='-', alpha=1.0, linewidth=0.7)   # Measure lines
        for beat_pos in beat_positions:
            self._ax.axvline(beat_pos, color='gray', linestyle='-', alpha=0.5, linewidth=0.5)       # Beat lines
        for grid_pos in step_positions:
            self._ax.axvline(grid_pos, color='gray', linestyle='dotted', alpha=0.25, linewidth=0.5) # Step subdivisions

        # Set x-axis labels in 'Measure.Beat' format
        measure_labels = [
            f"{int(pos // float(beats_per_measure))}" for pos in measure_positions
        ]
        
        self._ax.set_xlabel(
            f"Measures played at {round(clip_tempo, 1)}bpm for "
            f"{int(last_position / clip_tempo * 60 // 60)}'"
            f"{int(last_position / clip_tempo * 60 % 60)}''"
            f"{int(last_position / clip_tempo * 60_000 % 1000)}ms"
        )

        self._ax.set_xticks(measure_positions)  # Only show measure & beat labels
        if four_measures_multiple > 100:
            self._ax.set_xticklabels(measure_labels, fontsize=6, rotation=45)
        else:
            self._ax.set_xticklabels(measure_labels, rotation=0)
        self._fig.canvas.draw_idle()

        return None


    def _run_play(self, even = None) -> Self:
        import threading
        iteration_clip: Clip = self._iterations[self._iteration]
        threading.Thread(target=og.Play.play, args=(iteration_clip,)).start()
        # iteration_clip >> og.Play()
        return self

    def _run_first(self, even = None) -> Self:
        if self._iteration > 0:
            self._iteration = 0
            plotlist: list[dict] = self._plot_lists[self._iteration]
            self._plot_elements(plotlist)
            self._enable_button(self._next_button)
            if self._iteration == 0:
                self._disable_button(self._previous_button)
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

    def _run_last(self, even = None) -> Self:
        if self._iteration < len(self._plot_lists) - 1:
            self._iteration = len(self._plot_lists) - 1
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
            iteration_clip: Clip = self._iterations[-1]
            new_clip: Clip = self._n_function(iteration_clip.copy())
            if isinstance(new_clip, Clip):
                self._iteration = len(self._iterations)
                plotlist: list[dict] = new_clip.getPlotlist()
                self._iterations.append(new_clip)
                self._plot_lists.append(plotlist)
                self._plot_elements(plotlist)
            # Updates the iteration_clip data and plot just in case
            self._update_iteration(iteration, iteration_clip.getPlotlist())
            self._enable_button(self._previous_button)
            self._disable_button(self._next_button)
        return self

    def _run_composition(self, even = None) -> Self:
        import threading
        if callable(self._c_function):
            iteration_clip: Clip = self._iterations[self._iteration]
            composition: Composition = self._c_function(iteration_clip)
            if isinstance(composition, Composition):
                threading.Thread(target=og.Play.play, args=(composition,)).start()
                # composition >> og.Play()
            # Updates the iteration_clip data and plot just in case
            self._update_iteration(self._iteration, iteration_clip.getPlotlist())
        return self

    def _plot_filename(self, composition: 'Composition') -> str:
        # Process title separately (replace whitespace with underscores)
        processed_title = str(self._title).replace(" ", "_").replace("\t", "_").replace("\n", "_").replace("__", "_")
        composition_designations: list[str] = [
            processed_title,
            type(composition).__name__,
            f"{self._iteration}",
            f"{len(self._iterations) - 1}",
            composition.checksum()
        ]
        # 1. Filter empty strings and convert all parts to lowercase
        filtered_strings = [
            designation.strip().lower() 
            for designation in composition_designations 
            if designation
        ]
        # 2. Join with single underscore (no leading/trailing/double underscores)
        return "_".join(filtered_strings)

    def _run_save(self, even = None) -> Self:
        composition = self._iterations[self._iteration]
        file_name: str = self._plot_filename(composition) + "_save.json"
        composition >> og.Save(file_name)
        return self

    def _run_export(self, even = None) -> Self:
        composition = self._iterations[self._iteration]
        file_name: str = self._plot_filename(composition) + "_export.json"
        composition >> og.Export(file_name)
        return self

    def _run_render(self, even = None) -> Self:
        composition = self._iterations[self._iteration]
        file_name: str = self._plot_filename(composition) + "_render.mid"
        composition >> og.Render(file_name)
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

    def _on_move(self, event: MouseEvent) -> Self:
        if event.inaxes == self._ax:
            print(f"x = {event.xdata}, y = {event.ydata}")
        return self

    def _on_key(self, event: MouseEvent) -> Self:
        match event.key:
            case 'p':
                self._run_play(event)
            case 'c':
                self._run_composition(event)
            case 'S':
                self._run_save(event)
            case 'E':
                self._run_export(event)
            case 'R':
                self._run_render(event)
            case 'n':
                self._run_new(event)
            case ',':
                self._run_previous(event)
            case '.':
                self._run_next(event)
            case 'm':
                self._run_first(event)
            case '/' | "-" | ";":
                self._run_last(event)
        return self


    def plot(self, by_channel: bool = False, block: bool = True, pause: float = 0, iterations: int = 0,
            n_button: Optional[Callable[['Composition'], 'Composition']] = None,
            c_button: Optional[Callable[['Composition'], 'Composition']] = None, title: str = "") -> Self:
        """
        Plots the `Note`s in a `Composition`, if it has no Notes it plots the existing `Automation` instead.

        Args:
            by_channel: Allows the visualization in a Drum Machine alike instead of by Pitch.
            block (bool): Suspends the program until the chart is closed.
            pause (float): Sets a time in seconds before the chart is closed automatically.
            iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
                this is dependent on a n_button being given.
            n_button (Callable): A function that takes a Composition to be used to generate a new iteration.
            c_button (Callable): A function intended to play the plotted clip among other compositions.
            title (str): A title to give to the chart in order to identify it.

        Returns:
            Composition: Returns the presently plotted composition.
        """
        self._iterations: list[Composition] = [ type(self)(self) ]   # Works with a forced copy (Read Only)
        self._plot_lists: list[list] = [ self.getPlotlist() ]
        self._by_channel: bool = by_channel
        self._iteration: int = 0
        self._n_function = n_button
        self._c_function = c_button
        self._title: str = title

        if callable(self._n_function) and isinstance(iterations, int) and iterations > 0:
            for i in range(iterations):
                previous_composition: Composition = self._iterations[i]
                new_composition: Composition = self._n_function(previous_composition.copy())
                new_plotlist: list[dict] = new_composition.getPlotlist()
                self._iterations.append(new_composition)
                self._plot_lists.append(new_plotlist)
                self._iteration += 1

        # Enable interactive mode (doesn't block the execution)
        plt.ion()

        self._fig, self._ax = plt.subplots(figsize=(12, 6))
        # self._fig.canvas.mpl_connect("motion_notify_event", lambda event: self._on_move(event))
        self._fig.canvas.mpl_connect('key_press_event', lambda event: self._on_key(event))

        self._plot_elements(self._plot_lists[self._iteration])

        # Where the padding is set
        plt.tight_layout()
        plt.subplots_adjust(right=0.975)  # 2.5% right padding
        # Avoids too thick hatch lines
        plt.rcParams['hatch.linewidth'] = 0.10

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

        # Buttons are vertically spaced by 0.060

        # Save Button Widget
        ax_button = plt.axes([0.979, 0.528, 0.015, 0.05])
        export_button = Button(ax_button, 'S', color='white', hovercolor='grey')
        export_button.on_clicked(self._run_export)

        # Execution Button Widget
        ax_button = plt.axes([0.979, 0.468, 0.015, 0.05])
        export_button = Button(ax_button, 'E', color='white', hovercolor='grey')
        export_button.on_clicked(self._run_save)

        # Render Button Widget
        ax_button = plt.axes([0.979, 0.408, 0.015, 0.05])
        export_button = Button(ax_button, 'R', color='white', hovercolor='grey')
        export_button.on_clicked(self._run_render)

        # Previous Button Widget
        if self._iteration == 0:
            self._disable_button(self._previous_button)
        # Next Button Widget
        self._disable_button(self._next_button)

        if not callable(self._n_function):
            # New Button Widget
            self._disable_button(new_button)

        if not callable(self._c_function):
            # Composition Button Widget
            self._disable_button(composition_button)

        if block and pause == 0:
            plt.show(block=True)
        elif pause > 0:
            plt.draw()
            plt.pause(pause)
        else:
            plt.show(block=False)

        return self._iterations[self._iteration]


    def call(self, iterations: int = 1, n_button: Optional[Callable[['Composition'], 'Composition']] = None) -> Self:
            """
            `Call` a given callable function passed as `n_button`. This is to be used instead of `Plot` whenever \
                a given iteration was already chosen bypassing this way the process of plotting.

            Args:
                iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
                    this is dependent on a n_button being given.
                n_button (Callable): A function that takes a Composition to be used to generate a new iteration.

            Returns:
                Composition: Returns the presently plotted composition.
            """
            iterated_composition: Composition = type(self)(self)
            if callable(n_button) and isinstance(iterations, int) and iterations > 0:
                for _ in range(iterations):
                    iterated_composition = n_button(iterated_composition)
            return iterated_composition



TypeClip = TypeVar('TypeClip', bound='Clip')    # TypeClip represents any subclass of Operand


class Clip(Composition):  # Just a container of Elements
    """`Container -> Composition -> Clip`

    This type of `Container` aggregates only `Element` items. This is the only class
    that can be Plotted.

    Parameters
    ----------
    list([]) : A list of `Element` type items.
    int : Returns the len of the list.
    TimeSignature(settings) : A staff on which `TimeValue` units are based and `Element` items placed.
    MidiTrack("Track 1") : Where the track name and respective Devices are set.
    Length : Returns the length of all combined elements.
    """
    def __init__(self, *operands):
        super().__init__()
        self._base_container: Clip = self
        self._time_signature: og.TimeSignature           = og.settings._time_signature.copy()
        self._midi_track: ou.MidiTrack  = ou.MidiTrack()
        self._items: list[oe.Element]   = []
        for single_operand in operands:
            self << single_operand

    def _get_time_signature(self) -> 'og.TimeSignature':
        return self._time_signature

    def _index_from_frame(self, frame: of.Frame) -> int:
        """
        Read Only method
        """
        frame._set_inside_container(self)
        for index, single_element in enumerate(self._items):
            if single_element == frame:
                return index
        return None

    def _index_from_element(self, element: oe.Element) -> int:
        """
        Read Only method
        """
        for index, single_element in enumerate(self._items):
            if single_element is element:
                return index
        return None

    def __getitem__(self, index: int | of.Frame) -> 'oe.Element':
        """
        Read Only method
        """
        if isinstance(index, of.Frame):
            element_index: int = self._index_from_frame(index)
            if element_index is not None:
                return self._items[element_index]
            return ol.Null()
        return super().__getitem__(index)
    
    def __setitem__(self, index: int | of.Frame, value: oe.Element) -> Self:
        """
        Read and Write method
        """
        if isinstance(value, oe.Element):
            target_element: oe.Element = self[index]
            if isinstance(target_element, oe.Element) and value is not target_element:
                self._replace(target_element, value)    # Makes sure it propagates
        return self
    
    def __next__(self) -> 'oe.Element':
        return super().__next__()


    def _replace(self, old_item: Any = None, new_item: Any = None) -> Self:
        if isinstance(new_item, oe.Element):
            return super()._replace(old_item, new_item)
        return self

        
    def _set_owner_clip(self, owner_clip: 'Clip' = None) -> Self:
        """
        Allows the setting of a distinct `Clip` in the contained Elements for a transition process
        with a shallow `Clip`.
        """
        if owner_clip is None:
            for single_element in self._base_container._items:
                single_element._set_owner_clip(self._base_container)
        elif isinstance(owner_clip, Clip):
            self._base_container._time_signature << owner_clip._base_container._time_signature    # Does a parameters copy
            for single_element in self._base_container._items:
                single_element._set_owner_clip(owner_clip._base_container)
        return self


    def _convert_time_signature_reference(self, staff_reference: 'og.TimeSignature') -> Self:
        if isinstance(staff_reference, og.TimeSignature):
            for single_element in self:
                single_element._convert_time_signature(self._time_signature)
            if self._length_beats is not None:
                self._length_beats = ra.Length(staff_reference, self % od.Pipe( ra.Length() ))._rational
            self._time_signature << staff_reference  # Does a copy
        return self


    def _test_owner_clip(self) -> bool:
        for single_element in self._items:
            if single_element._owner_clip is not self._base_container:
                return False
        return True


    def checksum(self) -> str:
        """4-char hex checksum (16-bit) for a Clip, combining Element checksums."""
        master: int = len(self._base_container._items)
        for single_element in self._base_container._items:
            master ^= int(single_element.checksum(), 16)   # XOR 16-bit
        return f"{master & 0xFFFF:04x}" # 4 hexadecimal chars sized 16^4 = 65_536


    def masked_element(self, element: oe.Element) -> bool:
        if self.is_a_mask():
            for single_element in self._items:
                if single_element is element:
                    return False
            return True
        return False

    # Ignores the self Length
    def start(self) -> 'ra.Position':
        """
        Gets the starting position of all its Elements.
        This is the same as the minimum Position of all `Element` positions.

        Args:
            None

        Returns:
            Position: The minimum Position of all Elements.
        """
        if self.len() > 0:
            start_beats: Fraction = Fraction(0)
            first_element: oe.Element = self._first_element()
            if first_element:
                start_beats = first_element._position_beats
            return ra.Position(self, start_beats)
        return None


    # Ignores the self Length
    def finish(self) -> 'ra.Position':
        """
        Processes each element Position plus Length and returns the finish position
        as the maximum of all of them.

        Args:
            None

        Returns:
            Position: The maximum of Position + Length of all Elements.
        """
        if self.len() > 0:
            finish_beats: Fraction = Fraction(0)
            for item in self._items:
                if isinstance(item, oe.Element):
                    single_element: oe.Element = item
                    element_finish: Fraction = single_element._position_beats \
                        + (single_element % ra.Length())._rational
                    if element_finish > finish_beats:
                        finish_beats = element_finish
            return ra.Position(self, finish_beats)
        return None


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
            case od.Pipe():
                match operand._data:
                    case og.TimeSignature():        return self._base_container._time_signature
                    case ou.MidiTrack():            return self._base_container._midi_track
                    case ClipGet():
                        clip_get: ClipGet = operand._data
                        for single_element in self._items:
                            element_parameter: any = single_element
                            for get_operand in clip_get._get:
                                element_parameter //= get_operand
                            clip_get._items.append(element_parameter)
                        return clip_get
                    case _:                 return super().__mod__(operand)
            case og.TimeSignature():        return self._time_signature.copy()
            case ou.MidiTrack():    return self._base_container._midi_track.copy()
            case ou.TrackNumber() | od.TrackName() | Devices() | str():
                return self._base_container._midi_track % operand
            case og.TimeSignature() | og.TimeSignature():
                return self._base_container._time_signature % operand
            case Part():            return Part(self._base_container._time_signature, self._base_container)
            case Song():            return Song(self._base_container._time_signature, self._base_container)
            case ClipGet():
                clip_get: ClipGet = operand.copy()
                for single_element in self._items:
                    element_parameter: any = single_element.copy()
                    for get_operand in clip_get._get:
                        element_parameter %= get_operand
                    clip_get._items.append(element_parameter)
                return clip_get
            case _:
                return super().__mod__(operand)


    def get_unmasked_element_ids(self) -> set[int]:
        return {id(unmasked_item) for unmasked_item in self._items}

    def get_masked_element_ids(self) -> set[int]:
        if self.is_a_mask():
            unmasked_ids: set[int] = self.get_unmasked_element_ids()
            return {
                id(masked_item) for masked_item in self._base_container._items
                if id(masked_item) not in unmasked_ids
            }
        return set()


    def getPlotlist(self, position_beats: Fraction = Fraction(0), masked_element_ids: set[int] | None = None) -> list[dict]:
        """
        Returns the plotlist for a given Position.

        Args:
            position: The reference Position where the `Clip` starts at.

        Returns:
            list[dict]: A list with multiple Plot configuration dictionaries.
        """
        og.settings.reset()

        self_plotlist: list[dict] = []
        channels: dict[str, set[int]] = {
            "note":         set(),
            "automation":   set()
        }

        if masked_element_ids is None:
            masked_element_ids = set()
            
        masked_element_ids.update(self.get_masked_element_ids())

        self_plotlist.extend(
            single_playlist
                for single_element in self._base_container._items
                    for single_playlist in single_element.getPlotlist(
                        self._base_container._midi_track, position_beats, channels, masked_element_ids
                    )
        )
        # sorted(set) returns the sorted list from set
        # list_none = list(set).sort() doesn't return anything but None !
        self_plotlist.insert(0,
            {
                "channels": {
                    "note":         sorted(channels["note"]),
                    "automation":   sorted(channels["automation"])
                },
                "tempo": og.settings._tempo
            }
        )
        return self_plotlist


    def getPlaylist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        """
        Returns the playlist for a given Position.

        Args:
            position: The reference Position where the Clip starts at.

        Returns:
            list[dict]: A list with multiple Play configuration dictionaries.
        """
        og.settings.reset()

        self_playlist: list[dict] = [
            {
                "devices": self._base_container._midi_track._devices
            }
        ]
    
        for single_element in self._base_container._items:
            self_playlist.extend(
                single_element.getPlaylist(self._base_container._midi_track, position_beats, False)
            )
        return self_playlist


    def getMidilist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        """
        Returns the midilist for a given Position.

        Args:
            position: The reference Position where the Clip starts at.

        Returns:
            list[dict]: A list with multiple Midi file configuration dictionaries.
        """
        og.settings.reset()

        return [
            single_midilist
                for single_element in self._items
                for single_midilist in single_element.getMidilist(self._midi_track, position_beats)
        ]

    def getSerialization(self) -> dict:
        """
        Returns the serialization in a form of a dictionary of `Clip` parameters.

        Args:
            None

        Returns:
            dict: A dictionary with multiple the `Clip` configuration.
        """
        serialization = super().getSerialization()

        serialization["parameters"]["staff"]        = self.serialize(self._time_signature)
        serialization["parameters"]["midi_track"]   = self.serialize(self._midi_track)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        """
        Sets all `Clip` parameters based on a dictionary input previously generated by `getSerialization`.

        Args:
            serialization: A dictionary with all the `Clip` parameters.

        Returns:
            Clip: The self Clip object with the respective set parameters.
        """
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"] and "midi_track" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._time_signature             = self.deserialize(serialization["parameters"]["staff"])
            self._midi_track        = self.deserialize(serialization["parameters"]["midi_track"])
            self._set_owner_clip()
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Clip():
                super().__lshift__(operand)
                self._base_container._time_signature    << operand._base_container._time_signature
                self._base_container._midi_track        << operand._base_container._midi_track
                self._base_container._set_owner_clip()

            case od.Pipe():
                match operand._data:
                    case og.TimeSignature():        self._base_container._time_signature = operand._data
                    case ou.MidiTrack():            self._base_container._midi_track = operand._data

                    # All possible TimeSignature parameters enter here
                    case og.TimeSignature() | og.TimeSignature():
                        self._base_container._time_signature << operand._data

                    case list():
                        if all(isinstance(item, oe.Element) for item in operand):
                            # Remove previous Elements from the Container stack
                            self._delete(self._items, True) # deletes by id, safer
                            # Finally adds the decomposed elements to the Container stack
                            self._append( operand._data )
                            self._set_owner_clip()
                        else:   # Not for me
                            for item in self._items:
                                item <<= operand

                    case ClipGet():
                        clip_get: ClipGet = operand._data
                        if self.len() == clip_get.len() and len(clip_get._get) > 0:
                            for element_i in range(self.len()):
                                element_parameter: any = clip_get._items[element_i]
                                clip_get_get_len: int = len(clip_get._get)
                                # -1 because the last get parameter is the one existent in the list, last one type
                                for get_operand_j in range(clip_get_get_len - 1):
                                    clip_get._get[clip_get_get_len - 2 - get_operand_j] <<= element_parameter
                                    element_parameter = clip_get._get[clip_get_get_len - 2 - get_operand_j]
                                self._items[element_i] <<= element_parameter

                    case _:
                        super().__lshift__(operand)

            case ra.Length():
                self._base_container._length_beats = operand._rational
                if self._base_container._length_beats < 0:
                    self._base_container._length_beats = None
            case None:
                self._base_container._length_beats = None

            case ou.MidiTrack() | ou.TrackNumber() | od.TrackName() | Devices() | od.Device():
                self._base_container._midi_track << operand
            case og.TimeSignature() | og.TimeSignature():
                self._base_container._time_signature << operand  # TimeSignature has no clock!
            # Use Frame objects to bypass this parameter into elements (Setting Position)
            case od.Serialization():
                self._base_container.loadSerialization( operand.getSerialization() )

            case oe.Element():
                self += operand

            case list():
                if all(isinstance(item, oe.Element) for item in operand):
                    # Remove previous Elements from the Container stack
                    self._delete(self._items, True) # deletes by id, safer
                    # Finally adds the decomposed elements to the Container stack
                    self._append( self.deep_copy(operand) )
                    self._set_owner_clip()
                else:   # Not for me
                    for item in self._items:
                        item << operand
            case dict():
                if all(isinstance(item, oe.Element) for item in operand.values()):
                    for index, item in operand.items():
                        if isinstance(index, int) and index >= 0 and index < len(self._items):
                            self._items[index] = item.copy()
                else:   # Not for me
                    for item in self._items:
                        item << operand

            case tuple():
                for single_operand in operand:
                    self << single_operand

            case Composition():
                self._base_container._time_signature << operand._base_container._time_signature

            case ClipGet():
                clip_get: ClipGet = operand
                if self.len() == clip_get.len() and len(clip_get._get) > 0:
                    for element_i in range(self.len()):
                        element_parameter: any = clip_get._items[element_i]
                        clip_get_get_len: int = len(clip_get._get)
                        # -1 because the last get parameter is the one existent in the list, last one type
                        for get_operand_j in range(clip_get_get_len - 1):
                            clip_get._get[clip_get_get_len - 2 - get_operand_j] << element_parameter
                            element_parameter = clip_get._get[clip_get_get_len - 2 - get_operand_j]
                        self._items[element_i] << element_parameter
            
            case _: # Works for Frame too
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item << operand
        return self._sort_items()

    def __rshift__(self, operand: any) -> Self:
        match operand:
            case oe.Element():
                if self.is_a_mask():
                    return self.__irshift__(operand)
                return self.copy().__irshift__(operand)
        return super().__rshift__(operand)
    
    def __irshift__(self, operand) -> Self:
        match operand:
            case oe.Element():  # Element wapping (wrap)
                for single_element in self._items:
                    self._replace(single_element, operand.copy()._set_owner_clip(self) << single_element)
                return self
            case list():
                total_wrappers: int = len(operand)
                if total_wrappers > 0:
                    for index, single_element in enumerate(self._items):
                        wrapper: oe.Element = operand[index % total_wrappers]
                        single_element.__irshift__(wrapper)
                return self
        return super().__irshift__(operand)


    # Avoids the costly copy of Track self doing +=
    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Clip():
                self += operand._base_container._items

            case oe.Element():
                new_element: oe.Element = operand.copy()._set_owner_clip(self)
                if self.len() > 0:
                    self_last_element: oe.Element = self[-1]
                    return self._append([ new_element ], self_last_element)._sort_items()  # Shall be sorted!
                return self._append([ new_element ])._sort_items()  # Shall be sorted!
            
            case list():
                operand_elements = [
                    single_element.copy()._set_owner_clip(self)
                    for single_element in operand if isinstance(single_element, oe.Element)
                ]
                self._append(operand_elements)

            case og.TimeSignature() | og.TimeSignature():
                self._time_signature += operand

            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item += operand
        return self._sort_items()  # Shall be sorted!

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Clip():
                return self._base_container._delete(operand._items)
            case oe.Element():
                return self._delete([ operand ])
            case list():
                return self._delete(operand)
            
            case og.TimeSignature() | og.TimeSignature():
                self._time_signature -= operand

            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item -= operand
        return self._sort_items()  # Shall be sorted!

    # in-place multiply (NO COPY!)
    def __imul__(self, operand: any) -> Self:
        match operand:
            case Clip():
                operand_copy: Clip = operand.copy()._set_owner_clip(self)
                operand_base: Clip = operand_copy._base_container
                operand_position: ra.Position = operand_base.start()

                if operand_position is not None:

                    self_base: Clip = self._base_container
                    self_length: ra.Length = self_base % ra.Length()
                    operand_position = operand_position.roundMeasures()
                    position_offset: ra.Position = operand_position - self_length
                    operand_base -= position_offset   # Does a position offset
                    
                    self_base._append(operand_base._items) # Propagates upwards in the stack
                    if self_base._length_beats is not None:
                        self_base._length_beats += (operand_copy % ra.Length())._rational
                    if self.is_a_mask() and operand_copy.is_a_mask():
                        self._append(operand_copy._items)

            case oe.Element():
                self.__imul__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Clip = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__imul__(single_shallow_copy)
                elif operand == 0:
                    self._delete(self._base_container._items, True)
                    

            case ra.TimeValue() | ra.TimeUnit():
                self_repeating: int = 0
                operand_beats: Fraction = ra.Beats(self, operand)._rational
                self_length: ra.Length = self % ra.Length()
                self_beats: Fraction = self_length.roundMeasures()._rational  # Beats default unit
                if self_beats > 0:
                    self_repeating = operand_beats // self_beats
                self.__imul__(self_repeating)

            case list():
                segments_list: list[og.Segment] = [
                    og.Segment(self._base_container, single_segment) for single_segment in operand
                ]
                base_elements: list[oe.Element] = []
                mask_elements: list[oe.Element] = []
                for target_measure, source_segment in enumerate(segments_list):
                    # Preserves masked elements by id in base and mask containers
                    self_segment: Clip = self.copy().filter(source_segment)
                    self_segment._base_container << ra.Measure(target_measure)   # Stacked by measure *
                    base_elements.extend(self_segment._base_container._items)
                    mask_elements.extend(self_segment._items)
                self._delete()
                self._base_container._items = base_elements
                self._items = mask_elements
                self._set_owner_clip()

            case tuple():
                for single_operand in operand:
                    self.__imul__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__imul__(operand)
        return self._sort_items()  # Shall be sorted!

    def __rmul__(self, operand: any) -> Self:
        return self.__mul__(operand)
    
    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case Clip():
                operand: Clip = operand._base_container
                left_end_position: ra.Position = self.finish()
                if left_end_position is None:
                    left_end_position = ra.Position(self)
                if self._length_beats is not None:
                    self._length_beats += (operand % ra.Length())._rational
                right_start_position: ra.Position = operand.start()
                if right_start_position is not None:
                    length_shift: ra.Length = ra.Length(left_end_position - right_start_position)
                    position_shift: Fraction = length_shift._rational
                    # Elements to be added and propagated upwards on the stack
                    operand_elements: list[oe.Element] = []
                    for single_element in operand._items:
                        element_copy: oe.Element = single_element.copy()._set_owner_clip(self)
                        operand_elements.append(element_copy)
                        element_copy._position_beats += position_shift
                    self._append(operand_elements)  # Propagates upwards in the stack

            case oe.Element():
                self.__itruediv__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Clip = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__itruediv__(single_shallow_copy)
                elif operand == 0:
                    self._delete(self._base_container._items, True)

            case ra.TimeUnit():
                self_repeating: int = 0
                self_duration: Fraction = self % ra.Duration() % Fraction() # Kept in Beats
                if self_duration > 0:
                    operand_duration: Fraction = operand % ra.Beats(self) % Fraction()  # Converted to Beats
                    self_repeating = int( operand_duration / self_duration )
                self.__itruediv__(self_repeating)

            case list():
                segments_list: list[og.Segment] = [
                    og.Segment(self._base_container, single_segment) for single_segment in operand
                ]
                clip_segments: Clip = Clip()
                for single_segment in segments_list:
                    clip_segments /= self.copy().filter(single_segment) # Stacked notes /
                self._delete()
                self /= clip_segments
                self._set_owner_clip()

            case tuple():
                for single_operand in operand:
                    self.__itruediv__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__itruediv__(operand)
        return self._sort_items()  # Shall be sorted!

    def __ifloordiv__(self, operand: any) -> Self:
        match operand:
            case Clip():
                operand = operand._base_container
                # Equivalent to +=
                self += operand

            case oe.Element():
                self.__ifloordiv__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Clip = self.shallow_copy()
                    for _ in range(operand - 1):
                        self += single_shallow_copy
                elif operand == 0:   # Must be empty
                    self._delete(self._base_container._items, True)
            # Divides the `Duration` by the given `Length` amount as denominator
            case ra.Length() | ra.Duration():
                total_segments: int = operand % int()   # Extracts the original imputed integer
                if total_segments > 1:
                    new_elements: list[oe.Element] = []
                    for first_element in self._items:
                        first_element._duration_beats /= total_segments
                        first_element_duration: Fraction = first_element._duration_beats
                        for next_element_i in range(1, total_segments):
                            next_element: oe.Element = first_element.copy() # already with the right duration
                            next_element._position_beats += first_element_duration * next_element_i
                            new_elements.append(next_element)
                    self._append(new_elements)
            # Divides the `Duration` by sections with the given `Duration` (note value)
            case ra.NoteValue() | ra.TimeValue():
                new_elements: list[oe.Element] = []
                for first_element in self._items:
                    group_length: Fraction = first_element._duration_beats
                    segment_duration: Fraction = ra.Duration(self, operand)._rational
                    if segment_duration < group_length:
                        group_start: Fraction = first_element._position_beats
                        group_finish: Fraction = group_start + first_element._duration_beats
                        first_element._duration_beats = segment_duration
                        next_split: Fraction = group_start + segment_duration
                        while group_finish > next_split:
                            next_element: oe.Element = first_element.copy()
                            new_elements.append(next_element)
                            next_element._position_beats = next_split  # Just positions the `Element`
                            next_split += segment_duration
                            if next_split > group_finish:
                                next_element._duration_beats -= next_split - group_finish # Trims the extra `Duration`
                                break
                self._append(new_elements)
            
            case ra.Position() | ra.TimeUnit():
                new_elements: list[oe.Element] = []
                for left_element in self._items:
                    left_start: Fraction = left_element._position_beats
                    split_position: Fraction = ra.Position(self, left_start, operand)._rational
                    if split_position > left_start:
                        right_finish: Fraction = left_start + left_element._duration_beats
                        if split_position < right_finish:
                            left_duration: Fraction = split_position - left_start
                            right_duration: Fraction = right_finish - split_position
                            left_element._duration_beats = left_duration
                            right_element: oe.Element = left_element.copy()
                            new_elements.append(right_element)
                            right_element._position_beats = split_position
                            right_element._duration_beats = right_duration
                self._append(new_elements)

            case list():
                segments_list: list[og.Segment] = [
                    og.Segment(self._base_container, single_segment) for single_segment in operand
                ]
                base_elements: list[oe.Element] = []
                mask_elements: list[oe.Element] = []
                for _, source_segment in enumerate(segments_list):
                    # Preserves masked elements by id in base and mask containers
                    self_segment: Clip = self.copy().filter(source_segment)
                    self_segment._base_container << ra.Measure(0)   # Side by Side
                    base_elements.extend(self_segment._base_container._items)
                    mask_elements.extend(self_segment._items)
                self._delete()
                self._base_container._items = base_elements
                self._items = mask_elements
                self._set_owner_clip()

            case tuple():
                for single_operand in operand:
                    self.__ifloordiv__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__ifloordiv__(operand)
        return self._sort_items()  # Shall be sorted!


    def empty_copy(self, *parameters) -> Self:
        """
        Returns a Clip with all the same parameters but the list that is empty.

        Args:
            *parameters: Any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Clip: Returns the copy of self but with an empty list of items.
        """
        empty_copy: Clip                = super().empty_copy()
        empty_base: Clip                = empty_copy._base_container
        self_base: Clip                 = self._base_container
        empty_base._time_signature      << self_base._time_signature
        empty_base._midi_track          << self_base._midi_track
        empty_base._length_beats        = self_base._length_beats
        for single_parameter in parameters: # Parameters should be set on the base container
            empty_base << single_parameter
        return empty_copy
    
    def shallow_copy(self, *parameters) -> Self:
        """
        Returns a Clip with all the same parameters copied, but the list that
        is just a reference of the same list of the original Clip.

        Args:
            *parameters: Any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Clip: Returns the copy of self but with a list of the same items of the original one.
        """
        shallow_copy: Clip              = super().shallow_copy()
        # It's a shallow copy, so it shares the same TimeSignature and midi track
        shallow_copy._base_container._time_signature    = self._base_container._time_signature   
        shallow_copy._base_container._midi_track        = self._base_container._midi_track
        shallow_copy._base_container._length_beats      = self._base_container._length_beats
        for single_parameter in parameters: # Parameters should be set on the base container
            shallow_copy._base_container << single_parameter
        return shallow_copy


    def swap(self, left_operand: o.Operand, right_operand: o.Operand, parameter_type: type = ra.Position) -> Self:
        """
        This method swaps a given parameter type between two operands.

        Args:
            left_item (any): The first item called the left item.
            right_item (any): The second item called the right item.
            parameter (type): The parameters that will be switched between both operands.

        Returns:
            Container: The same self object with the operands processed.
        """
        if self.len() > 0 and isinstance(parameter_type, type):
            if isinstance(left_operand, of.Frame):
                left_operand = self[left_operand]
            if isinstance(right_operand, of.Frame):
                right_operand = self[right_operand]
            return super().swap(left_operand, right_operand, parameter_type)
        return self


    def drop(self, *measures) -> Self:
        """
        Drops from the `Composition` all `Measure`'s given by the numbers as parameters.

        Parameters
        ----------
        int(), list(), tuple(), set() : Accepts a sequence of integers as the Measures to be dropped.

        Returns:
            Clip: The same self object with the items removed if any.
        """
        finish_position: ra.Position = self.finish()
        if finish_position is not None:

            measures_list: list[int] = []
            for single_measure in measures:
                if isinstance(single_measure, (list, tuple, set)):
                    for measure in single_measure:
                        if isinstance(measure, (int, float, Fraction)):
                            measures_list.append(int(measure))
                elif isinstance(single_measure, (int, float, Fraction)):
                    measures_list.append(int(measure))
            
            end_measure: int = finish_position % ra.Measure() % int()
            # Pre processing of the measures_list, to start dropping from the end
            measures_list = [
                validated_measure for validated_measure in sorted(set(measures_list), reverse=True)
                if validated_measure <= end_measure
            ]

            for single_measure in measures_list:
                # removes all Elements at the Measure
                elements_to_remove: list[oe.Element] = [
                    measure_element for measure_element in self._items
                    if measure_element == ra.Measure(single_measure)
                ]
                self._delete(elements_to_remove, True)
                # offsets the right side of it to occupy the dropped measure
                for single_element in self._items:
                    if single_element > ra.Measure(single_measure):
                        single_measure -= ra.Measure(1)

        return self

    def crop(self, *measures) -> Self:
        """
        Crops from the `Composition` all `Measure`'s given by the numbers as parameters.

        Parameters
        ----------
        int(), list(), tuple(), set() : Accepts a sequence of integers as the Measures to be cropped.

        Returns:
            Clip: The same self object with the items removed if any.
        """
        finish_position: ra.Position = self.finish()
        if finish_position is not None:

            measures_list: list[int] = []
            for single_measure in measures:
                if isinstance(single_measure, (list, tuple, set)):
                    for measure in single_measure:
                        if isinstance(measure, (int, float, Fraction)):
                            measures_list.append(int(measure))
                elif isinstance(single_measure, (int, float, Fraction)):
                    measures_list.append(int(measure))
            
            end_measure: int = finish_position % ra.Measure() % int()
            
            all_measures = range(end_measure + 1)
            drop_measures: list[int] = [
                single_measure for single_measure in all_measures
                if single_measure not in measures_list
            ]
            return self.drop(drop_measures)
        return self


    def purge(self) -> Self:
        """
        With time a `Clip` may accumulate redundant Elements, this method removes all those elements.

        Args:
            None.

        Returns:
            Clip: The same self object with the items processed.
        """
        unique_items: list[oe.Element] = []
        remove_items: list[oe.Element] = []
        for single_element in self._items:
            for unique_element in unique_items:
                if single_element == unique_element:
                    remove_items.append(single_element)
                    break
            unique_items.append(single_element)
        return self._delete(remove_items, True)

    
    def sort(self, parameter: type = ra.Position, reverse: bool = False) -> Self:
        """
        Sorts the self list based on a given type of parameter.

        Args:
            parameter (type): The type of parameter being sorted by.

        Returns:
            Clip: The same self object with the items processed.
        """
        original_positions: list[Fraction] = [
            element._position_beats for element in self._items
        ]
        super().sort(parameter, reverse)
        for index, element in enumerate(self._items):
            element._position_beats = original_positions[index]
        return self
    
    def stepper(self, pattern: str = "1... 1... 1... 1...", note: Any = None) -> Self:
        """
        Sets the steps in a Drum Machine for a given `Note`.

        Args:
            pattern (str): A string where the 1s in it set where the triggered steps are.
            note (Any): A note or any respective parameter that sets each note.

        Returns:
            Clip: A clip with the notes placed at the triggered steps.
        """
        if isinstance(pattern, str):

            # Fraction sets the Duration in Steps
            element_note: oe.Note = \
                oe.Note()._set_owner_clip(self) \
                << Fraction(1) << note

            pattern = [1 if char == '1' else 0 for char in pattern if char != ' ' and char != '-']

            if isinstance(pattern, list):

                position_steps: ra.Steps = ra.Steps(0)
                for single_step in pattern:
                    if single_step == 1:
                        self += element_note << position_steps
                    position_steps += 1

            return self._sort_items()

        return self


    def automate(self, values: list[int] = [100, 70, 30, 100],
                 pattern: str = "1... 1... 1... 1...", automation: Any = "Pan", interpolate: bool = True) -> Self:
        """
        Distributes the values given by the Steps pattern in a way very like the stepper Drum Machine fashion.

        Args:
            values (list[int]): The automation values at the triggered steps.
            pattern (str): A string where the 1s in it are where the triggered midi messages are.
            automation (Any): The type of automation wanted, like, Aftertouch, PitchBend or ControlChange,
            the last one being the default.
            interpolate (bool): Does an interpolation per `Step` between the multiple triggered steps.

        Returns:
            Clip: A clip with the triggers placed at the respective steps.
        """
        if isinstance(pattern, str):

            # ControlChange, PitchBend adn Aftertouch Elements have already 1 Step of Duration
            if isinstance(automation, oe.Aftertouch):
                automate_element: oe.Element = \
                    oe.Aftertouch()._set_owner_clip(self) \
                    << automation
                # Ensure values is a non-empty list with only integers ≥ 0
                if not (isinstance(values, list) and values and all(isinstance(v, int) for v in values)):
                    values = [30, 70, 50, 0]
            elif isinstance(automation, oe.PitchBend) or automation is None:  # Pitch Bend, special case
                automate_element: oe.Element = \
                    oe.PitchBend()._set_owner_clip(self) \
                    << automation
                # Ensure values is a non-empty list with only integers ≥ 0
                if not (isinstance(values, list) and values and all(isinstance(v, int) for v in values)):
                    values = [-20*64, -70*64, -50*64, 0*64]
            else:
                automate_element: oe.Element = \
                    oe.ControlChange()._set_owner_clip(self) \
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

            return self._sort_items()
        
        return self


    def interpolate(self) -> Self:
        """
        Interpolates the multiple values of a given `Automation` element by `Channel`.

        Args:
            None.

        Returns:
            Clip: A clip with added automated elements placed at intermediary steps.
        """
        automation_clip: Clip = self.mask(of.InputType(oe.Automation))
        plotlist: list[dict] = automation_clip.getPlotlist()
        channels: list[int] = plotlist[0]["channels"]["automation"]

        for channel in channels:

            channel_automation: Clip = automation_clip.mask(ou.Channel(channel))

            if channel_automation.len() > 1:

                element_template: oe.Element = channel_automation[0].copy()
                
                # Find indices of known values
                known_indices = [
                    element % ra.Position() % ra.Steps() % int() for element in channel_automation._items
                ]

                total_messages: int = known_indices[-1] - known_indices[0] + 1
                pattern_values = [ None ] * total_messages

                element_index: int = 0
                for index in range(total_messages):
                    if index in known_indices:
                        # Extracts int as what is being automated
                        pattern_values[index] = channel_automation[element_index] % int()
                        element_index += 1

                # Calls a static method
                automation = self._interpolate_list(known_indices, pattern_values)

                position_steps: ra.Steps = ra.Steps(0)
                for index, value in enumerate(automation):
                    if index not in known_indices:   # None adds no Element
                        channel_automation += element_template << value << position_steps
                    position_steps += 1

        return self._sort_items()

    @staticmethod
    def _interpolate_list(known_indices, pattern_values) -> list:

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


    def oscillate(self, amplitude: int = 63, wavelength: float = 1/1, offset: int = 0, phase: int = 0,
                  parameter: type = None) -> Self:
        """
        Applies for each item element the value at the given position given by the oscillator function at
        that same position.

        Args:
            amplitude (int): Amplitude of the wave.
            wavelength (float): The length of the wave in note value.
            offset (int): Sets the horizontal axis of the wave.
            phase (int): Sets the starting degree of the wave.
            parameter (type): The parameter used as the one being automated by the wave.

        Returns:
            Clip: A clip with each element having the wave value set on it.
        """
        for single_element in self._items:
            
            element_position: ra.Position = single_element % ra.Position()
            wavelength_duration: Fraction = ra.Duration(wavelength)._rational
            wavelength_position: Fraction = element_position % ra.Duration() % Fraction()
            wavelength_ratio: Fraction = wavelength_position / wavelength_duration
            # The default unit of measurement of Position and Length is in Measures !!
            wave_phase: float = float(wavelength_ratio * 360 + phase)   # degrees
            # int * float results in a float
            # Fraction * float results in a float
            # Fraction * Fraction results in a Fraction
            value: int = int(amplitude * math.sin(math.radians(wave_phase)))
            value += offset
            if parameter is not None:
                single_element << parameter(value)
            else:
                single_element << value            

        return self
    

    def reverse(self, ignore_empty_measures: bool = True) -> Self:
        """
        Switches the sequence of the clip concerning the elements `Position`.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        if ignore_empty_measures:
            first_measure_position_beats: Fraction = self.start().roundMeasures()._rational
        else:
            first_measure_position_beats: Fraction = Fraction(0)
        self_finish: ra.Position = self.finish()
        if self_finish is None:
            self_finish = ra.Position(self)
        clip_length_beats: Fraction = ra.Length( self_finish ).roundMeasures()._rational # Rounded up Duration to next Measure
        for single_element in self._items:
            element_position_beats: Fraction = single_element._position_beats
            element_length_beats: Fraction = single_element % ra.Length() % od.Pipe( Fraction() )
            # Only changes Positions
            single_element._position_beats = first_measure_position_beats + clip_length_beats - (element_position_beats + element_length_beats)
        return super().reverse()    # Reverses the list

    def flip(self) -> Self:
        """
        `flip` works like `reverse` but it's agnostic about the Measure keeping the elements positional range.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        position_duration_beats: list[dict[str, Fraction]] = []
        for index, single_element in enumerate(self._items):
            position_duration_dict: dict[str, Fraction] = {
                "duration": single_element._duration_beats
            }
            if index == 0:
                position_duration_dict["position"] = single_element._position_beats
            else:
                position_duration_dict["position"] = \
                    position_duration_beats[0]["position"] + position_duration_beats[0]["duration"]
            position_duration_beats.insert(0, position_duration_dict)   # last one at position 0

        for index, single_element in enumerate(self._items):
            single_element._position_beats = position_duration_beats[index]["position"]
            single_element._duration_beats = position_duration_beats[index]["duration"]
            
        return self._sort_items()    # Sorting here is only needed because it may be a mask!


    def mirror(self) -> Self:
        """
        Mirror is similar to reverse but instead of reversing the elements position it reverses the
        Note's respective Pitch, like vertically mirrored.

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

        if higher_pitch is not None:

            top_pitch: int = higher_pitch.pitch_int()
            bottom_pitch: int = lower_pitch.pitch_int()

            for item in self._items:
                if isinstance(item, oe.Note):
                    element_pitch: og.Pitch = item._pitch
                    note_pitch: int = element_pitch.pitch_int()
                    new_pitch: int = top_pitch - (note_pitch - bottom_pitch)
                    element_pitch << new_pitch
                
        return self

    def invert(self) -> Self:
        """
        `invert` is similar to 'mirror' but based in a center defined by the first note on which all notes are vertically mirrored.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        center_pitch: int = None
        
        for item in self._items:
            if isinstance(item, oe.Note):
                center_pitch = item._pitch.pitch_int()
                break

        for item in self._items:
            if isinstance(item, oe.Note):
                note_pitch: int = item._pitch.pitch_int()
                if note_pitch != center_pitch:
                    item._pitch << 2 * center_pitch - note_pitch
                
        return self


    def snap(self, up: bool = False) -> Self:
        """
        For `Note` and derived, it snaps the given `Pitch` to the one of the key signature.

        Args:
            up (bool): By default it snaps to the closest bellow pitch, but if set as True, \
                it will snap to the closest above pitch instead.

        Returns:
            Clip: The same self object with the items processed.
        """
        for single_note in self:
            if isinstance(single_note, oe.Note):
                single_note._pitch.snap(up)
        return self


    def extend(self, length: ra.Length = None) -> Self:
        """
        Extends (stretches) the given clip along a given length.

        Args:
            length(2.0) : The length along which the clip will be extended (stretched).

        Returns:
            Clip: The same self object with the items processed.
        """
        if length is None:
            length = ra.Length(2.0)
        original_self: Clip = self.shallow_copy()
        original_self_duration: ra.Duration = self % ra.Duration()
        while self % ra.Duration() + original_self_duration <= length:
            self.__itruediv__(original_self)
        return self


    def trim(self, length: ra.Length = None) -> Self:
        """
        Trims the given clip at a given length.

        Args:
            length(1.0) : The length of the clip that will be trimmed.

        Returns:
            Clip: The same self object with the items processed.
        """
        if length is None:
            length = ra.Length(1.0)
        if isinstance(length, ra.Length):
            self._items = [
                element for element in self._items
                if element % ra.Position() < length
            ]
            for index, element in enumerate(self._items):
                if element % ra.Position() + element % ra.Length() > length:
                    new_length: ra.Length = length - element % ra.Position()
                    element << new_length
            if self._length_beats is not None:
                self._length_beats = min(self._length_beats, length._rational)
        return self
    
    def cut(self, start: ra.Position = None, finish: ra.Position = None) -> Self:
        """
        Cuts (removes) the section of the clip from the start to the finish positions.

        Args:
            start (Position): Starting position of the section to be cut.
            finish (Position): Finish position of the section to be cut.

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
            start (Position): Starting position of the section to be selected.
            finish (Position): Finish position of the section to be selected.

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


    def loop(self, position = 0, length = 4) -> Self:
        """
        Creates a loop from the Composition from the given `Position` with a given `Length`.

        Args:
            position (Position): The given `Position` where the loop starts at.
            length (Length): The `Length` of the loop.

        Returns:
            Clip: A copy of the self object with the items processed.
        """
        punch_in: ra.Position = ra.Position(self, Fraction(0))              # Inclusive
        punch_out: ra.Position = punch_in + ra.Position(self, Fraction(4))  # Exclusive

        if isinstance(position, (int, float, Fraction, ra.Position)):
            punch_in = ra.Position(self, position)
        if isinstance(length, (int, float, Fraction, ra.Length)):
            punch_out = punch_in + ra.Beats(length)
        
        included_elements: list[oe.Element] = [
            inside_element for inside_element in self._items
            if punch_in <= inside_element % od.Pipe( ra.Position() ) < punch_out
        ]

        self._delete(self._items, True)
        self._append(included_elements)

        self._length_beats = ra.Length(punch_out - punch_in)._rational
        self -= punch_in   # Moves to the start of the Clip being looped/trimmed

        return self._sort_items()


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
            shallow_copy: Clip = self.shallow_copy()._sort_items()
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
        shallow_copy: Clip = self.shallow_copy()._sort_items()
        shallow_copy_len: int = shallow_copy.len()
        for index in range(shallow_copy_len):
            current_element: oe.Element = shallow_copy._items[index]
            next_element: oe.Element = shallow_copy._items[index + 1]
            if current_element.finish() < next_element.start():
                rest_length: ra.Length = ra.Length( next_element.start() - current_element.finish() )
                rest_element: oe.Rest = \
                    oe.Rest()._set_owner_clip(self) \
                    << rest_length
                self += rest_element
        
        last_element: oe.Element = shallow_copy[shallow_copy_len - 1]
        staff_end: ra.Position = (last_element.finish() % ra.Length()).roundMeasures() % ra.Position()
        if last_element.finish() < staff_end:
            rest_length: ra.Length = ra.Length( staff_end - last_element.finish() )
            rest_element: oe.Rest = \
                oe.Rest()._set_owner_clip(self) \
                << rest_length
            self += rest_element

        return self

    def fit(self, length: ra.Length = None) -> Self:
        """
        Fits the entire clip in a given length.

        Args:
            length (Length): A length in which the clip must fit.

        Returns:
            Clip: The same self object with the items processed.
        """
        if isinstance(length, (ra.Position, ra.TimeValue, ra.Duration, ra.TimeUnit)):
            fitting_finish: ra.Position = ra.Position(self, length)
        else:
            fitting_finish: ra.Position = ra.Position(ra.Measure(self, 1))
        actual_finish: ra.Position = self.finish()
        if actual_finish is None:
            actual_finish = ra.Position(self)
        length_ratio: Fraction = fitting_finish._rational / actual_finish._rational
        self.__imul__(ra.Position(self, float(length_ratio)))   # Adjust positions
        self.__imul__(ra.Duration(self, float(length_ratio)))   # Adjust durations
        return self

    def link(self, ignore_empty_measures: bool = True) -> Self:
        """
        Adjusts the duration/length of each element to connect to the start of the next element.
        For the last element in the clip, this is extended up to the end of the measure.

        Args:
            ignore_empty_measures (bool): Ignores first empty Measures if `True`.

        Returns:
            Clip: The same self object with the items processed.
        """
        if self.len() > 0:
            for index, element in enumerate(self._items):
                if index > 0:
                    previous_element: oe.Element = self[index - 1]
                    previous_element << \
                        ra.Beats(self, element._position_beats - previous_element._position_beats) % ra.Duration()
            # Add a Rest in the beginning if necessary
            first_element: oe.Element = self._first_element()
            last_element: oe.Element = self._last_element()
            starting_position_beats: Fraction = Fraction(0)
            if ignore_empty_measures:
                starting_position_beats = (first_element % od.Pipe( ra.Position() )).roundMeasures()._rational
            if first_element._position_beats != starting_position_beats:  # Not at the starting position
                rest_duration: ra.Duration = ra.Beats(self, first_element._position_beats) % ra.Duration()
                self._items.insert(0, oe.Rest(rest_duration))
            # Adjust last_element duration based on its Measure position
            if last_element is not None:    # LAST ELEMENT ONLY!
                remaining_beats: Fraction = \
                    ra.Length(self, last_element._position_beats).roundMeasures()._rational - last_element._position_beats
                if remaining_beats == 0:    # Means it's on the next Measure alone, thus, it's a one Measure note
                    last_element << ra.Measures(self, 1) % ra.Duration()
                else:
                    last_element << ra.Beats(self, remaining_beats) % ra.Duration()
        return self._sort_items()


    def stack(self, ignore_empty_measures: bool = True) -> Self:
        """
        Moves each Element to start at the finish position of the previous one.
        If it's the first element then its position becomes 0 or the staring of the first non empty `Measure`.

        Args:
            ignore_empty_measures (bool): Ignores first empty Measures if `True`.

        Returns:
            Clip: The same self object with the items processed.
        """
        for index, single_element in enumerate(self._items):
            if index > 0:   # Not the first element
                duration_beats: Fraction = self._items[index - 1]._duration_beats
                single_element._position_beats = self._items[index - 1]._position_beats + duration_beats  # Stacks on Element Duration
            else:           # THE FIRST ELEMENT!
                if ignore_empty_measures:
                    root_position: ra.Position = (single_element % ra.Position()).roundMeasures()
                    single_element._position_beats = root_position._rational
                else:
                    single_element._position_beats = Fraction(0)   # everything starts at the beginning (0)!
        
        return self._sort_items()    # May be needed due to upper clips
    
    def quantize(self, amount: float = 1.0) -> Self:
        """
        Quantizes a `Clip` by a given amount from 0.0 to 1.0.

        Args:
            amount (float): The amount of quantization to apply from 0.0 to 1.0.

        Returns:
            Clip: The same self object with the items processed.
        """
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        amount_rational: Fraction = ra.Amount(amount) % Fraction()
        for single_element in self._items:
            element_position: Fraction = single_element._position_beats
            unquantized_amount: Fraction = element_position % quantization_beats
            quantization_limit: int = round(unquantized_amount / quantization_beats)
            position_offset: Fraction = (quantization_limit * quantization_beats - unquantized_amount) * amount_rational
            single_element._position_beats += position_offset
        return self
    

    def decompose(self) -> Self:
        """
        Transform each element in its component elements if it's a composed element,
        like a chord that is composed of multiple notes, so, it becomes those multiple notes instead.

        Args:
            None

        Returns:
            Clip: Equally sounding Clip but with its elements reduced to their components.
        """
        decomposed_elements: list[oe.Element] = []
        for single_element in self._items:
            component_elements: list[oe.Element] = single_element.get_component_elements()
            for single_component in component_elements:
                decomposed_elements.append(single_component)
        # Remove previous Elements from the Container stack
        self._delete(self._items, True) # deletes by id, safer
        # Finally adds the decomposed elements to the Container stack
        self._append(decomposed_elements)
        return self._sort_items()

    def arpeggiate(self, parameters: any = None) -> Self:
        """
        Distributes each element accordingly to the configured arpeggio by the parameters given.

        Args:
            parameters: Parameters that will be passed to the `Arpeggio` operand.

        Returns:
            Clip: Clip with its elements distributed in an arpeggiated manner.
        """
        arpeggio = og.Arpeggio(parameters)
        arpeggio.arpeggiate_source(self._items, self.start(), ra.Length( self.net_duration() ))
        return self


    def tie(self, decompose: bool = True) -> Self:
        """
        Extends the `Note` elements as tied when applicable.
        Works only on Notes, and NOT on its derived elements, as `Chord`,
        do `Decompose` if needed to transform a `Chord` into Notes.

        Args:
            decompose (bool): If `True`, decomposes elements derived from `Note` first.

        Returns:
            Clip: The same self object with the items processed.
        """
        if decompose:
            self.decompose()
        all_notes: list[oe.Note] = [
            single_note for single_note in self._items if type(single_note) is oe.Note
        ]
        removed_notes: list[oe.Note] = []
        extended_notes: dict[int, oe.Note] = {}
        for note in all_notes:
            channel_pitch: int = note._channel << 8 | note._pitch.pitch_int()
            if channel_pitch in extended_notes:
                extended_note: oe.Note = extended_notes[channel_pitch]
                extended_note_position: Fraction = extended_note._position_beats
                extended_note_length: Fraction = extended_note % od.Pipe( ra.Length() ) % od.Pipe( Fraction() )   # In Beats
                extended_note_position_off: Fraction = extended_note_position + extended_note_length
                
                if note._position_beats == extended_note_position_off:
                    note_length: Fraction = note % od.Pipe( ra.Length() ) % od.Pipe( Fraction() )   # In Beats
                    extended_length: Fraction = extended_note_length + note_length
                    # Extends the original note duration and marks note for removal
                    extended_note << ra.Length(self, extended_length)
                    removed_notes.append(note)
                else:
                    # Becomes the new original note
                    extended_notes[channel_pitch] = note
            else:
                extended_notes[channel_pitch] = note
        self._delete(removed_notes)
        return self
    
    def join(self, decompose: bool = True) -> Self:
        """
        Joins all same type notes with the same `Pitch` as a single `Note`, from left to right.

        Args:
            decompose (bool): If `True`, decomposes elements derived from `Note` first.

        Returns:
            Clip: The same self object with its notes joined by pitch and type.
        """
        if decompose:
            self.decompose()
        all_notes: list[oe.Note] = [
            single_note for single_note in self._items if type(single_note) is oe.Note
        ]
        removed_notes: list[oe.Note] = []
        extended_notes: dict[int, oe.Note] = {}
        for note in all_notes:
            channel_pitch: int = note._channel << 8 | note._pitch.pitch_int()
            if channel_pitch in extended_notes:
                extended_note: oe.Note = extended_notes[channel_pitch]
                extended_note_position: Fraction = extended_note._position_beats
                finish_note_position: Fraction = note.finish()._rational
                if finish_note_position > extended_note_position:
                    extended_note_length: Fraction = finish_note_position - extended_note_position
                    extended_note << ra.Length(self, extended_note_length)  # Fraction represents Beats (direct)
                removed_notes.append(note)
            else:
                extended_notes[channel_pitch] = note
        self._delete(removed_notes)
        return self


    def slur(self, gate: float = 1.05) -> Self:
        """
        Changes the note `Gate` in order to crate a small overlap.

        Args:
            gate (float): Can be given a different gate from 1.05, de default.

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
        Adjusts the `Note` octave to have the closest pitch to the previous one.

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


    def split(self, position: ra.Position) -> tuple['Clip', 'Clip']:
        """
        Splits the given clip in two at the given position.

        Args:
            position (ra.Position): Position at which the clip will be split in two

        Returns:
            Clip: The same self object with the items processed.
        """
        self_left: Clip     = self.copy().filter(of.Less(position))
        self_right: Clip    = self.copy().filter(of.GreaterOrEqual(position))
        return self_left, self_right
    

class Part(Composition):
    """`Container -> Composition -> Part`

    This type of `Container` aggregates `Clip` items as also `Playlist` ones. This type
    of `Composition` has a `Position` working similarly to `Element` operands.

    Parameters
    ----------
    list([]) : A list of `Clip` and `Playlist` type items.
    int : Returns the len of the list.
    Position(0) : It is possible to place a Part on a staff `Position`.
    Length : Returns the length of all combined clips.
    """
    def __init__(self, *operands):
        self._position_beats: Fraction  = Fraction(0)   # in Beats
        super().__init__()
        self._base_container: Part = self
        self._time_signature = og.settings._time_signature
        self._items: list[Clip] = []
        self._name: str = "Part"

        # Song sets the TimeSignature, this is just a reference
        self._owner_song: Song      = None

        for single_operand in operands:
            self << single_operand


    def _convert_time_signature_reference(self, staff_reference: 'og.TimeSignature') -> Self:
        if isinstance(staff_reference, og.TimeSignature):
            self._position_beats = ra.Position(staff_reference, self % od.Pipe( ra.Position() ))._rational
            if self._length_beats is not None:
                self._length_beats = ra.Length(staff_reference, self % od.Pipe( ra.Length() ))._rational
            self._time_signature = staff_reference  # Does an assignment
        return self


    def _set_owner_song(self, owner_song: 'Song') -> Self:
        if isinstance(owner_song, Song):
            self._owner_song = owner_song
        return self

    def _get_time_signature(self) -> 'og.TimeSignature':
        if self._owner_song is None:
            return og.settings._time_signature
        return self._owner_song._time_signature


    def __getitem__(self, key: str | int) -> 'Clip':
        if isinstance(key, str):
            for single_item in self._items:
                if single_item._midi_track._name == key:
                    return single_item
            return ol.Null()
        return self._items[key]

    def __next__(self) -> 'Clip':
        return super().__next__()
    
    def _sort_items(self) -> Self:
        # Clips aren't sortable
        return self


    def checksum(self) -> str:
        """4-char hex checksum (16-bit) for a Part, combining Clip checksums."""
        master: int = len(self._base_container._items)
        for single_clip in self._base_container._items:
            master ^= int(single_clip.checksum(), 16)   # XOR 16-bit
        return f"{master & 0xFFFF:04x}" # 4 hexadecimal chars sized 16^4 = 65_536


    def masked_element(self, element: oe.Element) -> bool:
        if self.is_a_mask():
            for single_clip in self._items:
                for single_element in single_clip._items:
                    if single_element is element:
                        return False
            return True
        return False

    def len(self, just_clips: bool = False) -> int:
        """
        Returns the total number of items.

        Args:
            just_clips: Excludes the `Playlist` items if True.

        Returns:
            int: Returns the equivalent to the len(self._items).
        """
        if just_clips:
            total_clips: int = 0
            for single_item in self._items:
                if isinstance(single_item, Clip):
                    total_clips += 1
            return total_clips

        return super().len()


    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Part():
                if self._owner_song is other._owner_song:   # Most of the cases. Optimization!
                    return super().__eq__(other) \
                        and self._position_beats == other._position_beats
                return super().__eq__(other) \
                    and self % ra.Position() == other % ra.Position()
            case of.Frame():
                for single_clip in self._items:
                    if not single_clip == other:
                        return False
                return True
            case _:
                if other.__class__ == o.Operand:
                    return True
                if type(other) == ol.Null:
                    return False    # Makes sure ol.Null ends up processed as False
                return self % other == other

    def __lt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Part():
                if self._owner_song is other._owner_song:   # Most of the cases. Optimization!
                    return self._position_beats < other._position_beats
                return self % ra.Position() < other % ra.Position()
            case of.Frame():
                for single_clip in self._items:
                    if not single_clip < other:
                        return False
                return True
            case _:
                return self % other < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Part():
                if self._owner_song is other._owner_song:   # Most of the cases. Optimization!
                    return self._position_beats > other._position_beats
                return self % ra.Position() > other % ra.Position()
            case of.Frame():
                for single_clip in self._items:
                    if not single_clip > other:
                        return False
                return True
            case _:
                return self % other > other
    

    def start(self) -> ra.Position:
        """
        Gets the starting position of all its Clips.
        This is the same as the minimum `Position` of all `Clip` positions.
        This position is Part reference_time_signature based position.

        Args:
            None

        Returns:
            Position: The minimum `Position` of all Clips.
        """
        clips_list: list[Clip] = [
            clip for clip in self._items if isinstance(clip, Clip)
        ]

        start_position: ra.Position = None
        for clip in clips_list:
            clip_start: ra.Position = clip.start()
            if clip_start is not None:
                if start_position is not None:
                    if clip_start < start_position:
                        start_position = clip_start
                else:
                    start_position = clip_start
        return start_position


    def finish(self) -> ra.Position:
        """
        Processes each clip `Position` plus Length and returns the finish position
        as the maximum of all of them. This position is `Part` reference_time_signature based `Position`.

        Args:
            None

        Returns:
            Position: The maximum of `Position` + Length of all Clips.
        """
        clips_list: list[Clip] = [
            clip for clip in self._items if isinstance(clip, Clip)
        ]

        finish_position: ra.Position = None
        for clip in clips_list:
            clip_finish: ra.Position = clip.finish()
            if clip_finish is not None:
                if finish_position is not None:
                    if clip_finish > finish_position:
                        finish_position = clip_finish
                else:
                    finish_position = clip_finish
        return finish_position


    def _last_element(self) -> 'oe.Element':
        """
        Returns the `Element` with the last `Position` in the given `Part`.

        Args:
            None

        Returns:
            Element: The last `Element` of all elements in each `Clip`.
        """
        clips_list: list[Clip] = [
            clip for clip in self._items if isinstance(clip, Clip)
        ]

        part_last: oe.Element = None
        if len(clips_list) > 0:
            for clip in clips_list:
                clip_last: oe.Element = clip._last_element()
                if clip_last:
                    if part_last:
                        # Implicit conversion
                        if clip_last > part_last:
                            part_last = clip_last
                    else:
                        part_last = clip_last
        return part_last


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Position():
                        return operand._data << ra.Position(self._base_container, self._base_container._position_beats)
                    case str():
                        return self._name
                    case _:                 return super().__mod__(operand)
            case ra.Position():
                return operand.copy( ra.Position(self._base_container, self._base_container._position_beats) )
            case str():
                return self._base_container._name
            case od.Names():
                all_names: list[str] = []
                for single_item in self._items:
                    if isinstance(single_item, Clip):
                        all_names.append(single_item._midi_track._name)
                    else:
                        all_names.append(single_item._track_name)
                return od.Names(*tuple(all_names))
            case Song():
                return Song(self)
            case _:
                return super().__mod__(operand)


    def get_unmasked_element_ids(self) -> set[int]:
        unmasked_element_ids: set[int] = set()
        for unmasked_clip in self._items:
            unmasked_element_ids.update( unmasked_clip.get_unmasked_element_ids() )
        return unmasked_element_ids

    def get_masked_element_ids(self) -> set[int]:
        masked_element_ids: set[int] = set()
        if self.is_a_mask():
            unmasked_ids: set[int] = self.get_unmasked_element_ids()
            for masked_clip in self._base_container._items:
                masked_element_ids.update({
                    id(masked_item) for masked_item in masked_clip._items
                    if id(masked_item) not in unmasked_ids
                })
        return masked_element_ids


    def getPlotlist(self, masked_element_ids: set[int] | None = None) -> list[dict]:
        """
        Returns the plotlist for a given Position.

        Returns:
            list[dict]: A list with multiple Plot configuration dictionaries.
        """
        plot_list: list = []
        
        if masked_element_ids is None:
            masked_element_ids = set()
            
        masked_element_ids.update(self.get_masked_element_ids())

        for single_clip in self._base_container._items:
            clip_plotlist: list[dict] = single_clip.getPlotlist(self._position_beats, masked_element_ids)
            plot_list.extend( clip_plotlist )
        return plot_list


    def getPlaylist(self) -> list[dict]:
        """
        Returns the playlist for a given Position.

        Args:
            None

        Returns:
            list[dict]: A list with multiple Play configuration dictionaries.
        """
        play_list: list = []
        for single_clip in self._base_container._items:
            play_list.extend(single_clip.getPlaylist(self._base_container._position_beats))
        return play_list

    def getMidilist(self) -> list[dict]:
        """
        Returns the midilist for a given Position.

        Args:
            None

        Returns:
            list[dict]: A list with multiple Midi file configuration dictionaries.
        """
        midi_list: list = []
        for single_clip in self:
            if isinstance(single_clip, Clip):   # Can't get Midilist from Playlist !
                midi_list.extend(single_clip.getMidilist(self._position_beats))
        return midi_list

    def getSerialization(self) -> dict:
        """
        Returns the serialization in a form of a dictionary of `Part` parameters.

        Args:
            None

        Returns:
            dict: A dictionary with multiple the `Part` configuration.
        """
        serialization = super().getSerialization()

        serialization["parameters"]["position"] = self.serialize(self._position_beats)
        serialization["parameters"]["name"]     = self.serialize(self._name)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        """
        Sets all `Part` parameters based on a dictionary input previously generated by `getSerialization`.

        Args:
            serialization: A dictionary with all the `Part` parameters.

        Returns:
            Part: The self Part object with the respective set parameters.
        """
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "name" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position_beats    = self.deserialize(serialization["parameters"]["position"])
            self._name              = self.deserialize(serialization["parameters"]["name"])
        return self

    def __lshift__(self, operand: any) -> Self:
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Part():
                super().__lshift__(operand)
                # No conversion is done, beat values are directly copied (Same for Element)
                self._base_container._position_beats    = operand._base_container._position_beats
                self._base_container._name              = operand._base_container._name
                # Because a Part is also defined by the Owner Song, this also needs to be copied!
                if self._owner_song is None:   # << and copy operation doesn't override ownership
                    self._owner_song    = operand._owner_song
                
            case od.Pipe():
                match operand._data:
                    case ra.Position():     self._base_container._position_beats = operand._data._rational
                    case str():             self._base_container._name = operand._data
                    case list():
                        if all(isinstance(item, Clip) for item in operand._data):
                            self._items = [item for item in operand._data]
                        else:   # Not for me
                            for item in self._items:
                                item << operand._data
                    case _:
                        super().__lshift__(operand)

            case ra.Position() | ra.TimeValue() | ra.TimeUnit():
                self._base_container._position_beats = operand % ra.Position(self) % Fraction()

            case Clip():
                self.__iadd__(operand)

            case oe.Element():
                self += operand

            case od.Serialization():
                self._base_container.loadSerialization( operand.getSerialization() )
            case list():
                if all(isinstance(item, Clip) for item in operand):
                    self._items = [item.copy() for item in operand]
                else:   # Not for me
                    for item in self._items:
                        item << operand
            case dict():
                if all(isinstance(item, Clip) for item in operand.values()):
                    for index, item in operand.items():
                        if isinstance(index, int) and index >= 0 and index < len(self._items):
                            self._items[index] = item.copy()
                else:   # Not for me
                    for item in self._items:
                        item << operand

            case str():
                self._base_container._name = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item << operand
        return self._sort_items()


    def __iadd__(self, operand: any) -> Self:
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Part():
                for single_clip in operand:
                    self += single_clip

            case Clip():
                self._append([ Clip(operand) ])

            case oe.Element():
                self += Clip(operand)

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
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Part():
                return self._delete(operand._items)
            case Clip():
                return self._delete([ operand ])
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
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Part():
                # Part(operand) works as copy on Masks while operand.copy() doesn't !!
                right_part: Part = Part(operand)

                left_length: ra.Length = self % ra.Length()
                right_position: ra.Position = right_part % od.Pipe( ra.Position() )
                position_offset: ra.Position = right_position - left_length

                for single_clip in right_part:
                    single_clip -= position_offset

                self._append(right_part._items)  # Propagates upwards in the stack
                
                if self._length_beats is not None:
                    self._length_beats += (right_part % ra.Length())._rational

            case Clip():
                self.__imul__(Part(operand))

            case oe.Element():
                self.__imul__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Part = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__imul__(single_shallow_copy)
                elif operand == 0:
                    self._delete(self._base_container._items, True)

            case tuple():
                for single_operand in operand:
                    self.__imul__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__imul__(operand)
        return self

    def __itruediv__(self, operand: any) -> Self:
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Part():
                # This conversion doesn't touch on the Clips
                right_part: Part = Part(operand)

                left_length: ra.Length = self % ra.Duration() % ra.Length()
                position_offset: ra.Position = ra.Position(left_length.roundMeasures())

                # right part Position is lost, so, there is the need of reposition the Clips based on the self Part
                for single_clip in right_part:
                    single_clip += position_offset

                self._append(right_part._items)  # Propagates upwards in the stack
                
                if self._length_beats is not None:
                    self._length_beats += (right_part % ra.Duration() % ra.Length())._rational

            case Clip():
                self.__itruediv__(Part(operand))

            case oe.Element():
                self.__itruediv__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Part = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__itruediv__(single_shallow_copy)
                elif operand == 0:
                    self._delete(self._base_container._items, True)
                    
            case tuple():
                for single_operand in operand:
                    self.__itruediv__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__itruediv__(operand)
        return self

    def __ifloordiv__(self, operand: any) -> Self:
        match operand:
            case Part():
                self += operand

            case Clip():
                self.__ifloordiv__(Part(operand))

            case oe.Element():
                self.__ifloordiv__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Part = self.shallow_copy()
                    for _ in range(operand - 1):
                        self += single_shallow_copy
                elif operand == 0:
                    self._delete(self._base_container._items, True)

            case tuple():
                for single_operand in operand:
                    self.__ifloordiv__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__ifloordiv__(operand)
        return self._sort_items()  # Shall be sorted!


    def loop(self, position = 0, length = 4) -> Self:
        """
        Creates a loop from the Composition from the given `Position` with a given `Length`.

        Args:
            position (Position): The given `Position` where the loop starts at.
            length (Length): The `Length` of the loop.

        Returns:
            Part: A copy of the self object with the items processed.
        """
        punch_in: ra.Position = ra.Position(self, Fraction(0))  # Inclusive
        punch_length: ra.Length = ra.Length(self, Fraction(4))  # Exclusive

        if isinstance(position, (int, float, Fraction, ra.Position)):
            punch_in = ra.Position(self, position)
        if isinstance(length, (int, float, Fraction, ra.Length)):
            punch_length = ra.Length(self, length)

        clip_punch_in: ra.Position = punch_in - ra.Beats(self._position_beats)

        # No Clip is removed, only elements are removed
        for single_clip in self._items:
            single_clip.loop(clip_punch_in, punch_length)

        if self._position_beats < punch_in._rational:
            self._position_beats = Fraction(0) # Positions all parts at the start
        else:
            self._position_beats -= punch_in._rational
        self._length_beats = punch_length._rational

        return self._sort_items()


class Song(Composition):
    """`Container -> Composition -> Song`

    This type of `Container` aggregates only `Part` items. This type
    of `Composition` has a `TimeSignature` working similarly to `Clip` operands, where
    `Clip` contains `Element` items while `Song` contains `Part` ones.

    Parameters
    ----------
    list([]) : A list of `Part` type items.
    int : Returns the len of the list.
    TimeSignature(settings) : It keeps its own staff on which their `Part` items are placed.
    Length : Returns the length of all combined parts.
    """
    def __init__(self, *operands):
        super().__init__()
        self._base_container: Song = self
        self._time_signature = og.settings._time_signature.copy()
        self._items: list[Part] = []
        for single_operand in operands:
            self << single_operand

    def _get_time_signature(self) -> 'og.TimeSignature':
        return self._time_signature


    def __getitem__(self, key: int) -> 'Part':
        if isinstance(key, str):
            for single_part in self._items:
                if single_part._name == key:
                    return single_part
            return ol.Null()
        return self._items[key]

    def __next__(self) -> 'Part':
        return super().__next__()
    

    def _set_owner_song(self, owner_song: 'Song' = None) -> Self:
        """
        Allows the setting of a distinct `Song` in the contained Elements for a transition process
        with a shallow `Song`.
        """
        if owner_song is None:
            for single_part in self._base_container._items:
                single_part._set_owner_song(self._base_container)
        elif isinstance(owner_song, Song):
            self._base_container._time_signature << owner_song._base_container._time_signature    # Does a parameters copy
            for single_part in self._base_container._items:
                single_part._set_owner_song(owner_song._base_container)
        return self


    def _convert_time_signature_reference(self, staff_reference: 'og.TimeSignature') -> Self:
        if isinstance(staff_reference, og.TimeSignature):
            for single_part in self:
                single_part._convert_time_signature_reference(self._time_signature)
            if self._length_beats is not None:
                self._length_beats = ra.Length(staff_reference, self % od.Pipe( ra.Length() ))._rational
            self._time_signature << staff_reference  # Does a copy
        return self


    def _test_owner_song(self) -> bool:
        for single_part in self:
            if single_part._owner_song is not self:
                return False
        return True


    def checksum(self) -> str:
        """4-char hex checksum (16-bit) for a Song, combining Part checksums."""
        master: int = len(self._base_container._items)
        for single_part in self._base_container._items:
            master ^= int(single_part.checksum(), 16)   # XOR 16-bit
        return f"{master & 0xFFFF:04x}" # 4 hexadecimal chars sized 16^4 = 65_536


    def masked_element(self, element: oe.Element) -> bool:
        if self.is_a_mask():
            for single_part in self._items:
                for single_clip in single_part._items:
                    for single_element in single_clip._items:
                        if single_element is element:
                            return False
            return True
        return False

    def start(self) -> ra.Position:
        """
        Gets the starting position of all its Parts.
        This is the same as the minimum `Position` of all `Part` positions, which ones,
        share the same common Song TimeSignature reference.

        Args:
            None

        Returns:
            Position: The minimum `Position` of all Parts.
        """
        start_position: ra.Position = None

        for single_part in self._items:
            # Already includes the Song TimeSignature conversion
            part_start: ra.Position = single_part.start()
            if part_start is not None:
                absolute_start: ra.Position = single_part % ra.Position() + part_start
                if start_position is not None:
                    if absolute_start < start_position:
                        start_position = absolute_start
                else:
                    start_position = absolute_start
        return start_position


    def finish(self) -> ra.Position:
        """
        Gets the finishing position of all its Parts.
        This is the same as the maximum `Position` of all `Part` positions, which ones,
        share the same common Song TimeSignature reference.

        Args:
            None

        Returns:
            Position: The maximum `Position` of all Parts.
        """
        finish_position: ra.Position = None

        for single_part in self._items:
            # Already includes the Song TimeSignature conversion
            part_finish: ra.Position = single_part.finish()
            if part_finish is not None:
                absolute_finish: ra.Position = single_part % ra.Position() + part_finish
                if finish_position is not None:
                    if absolute_finish > finish_position:
                        finish_position = absolute_finish
                else:
                    finish_position = absolute_finish
        return finish_position


    def _last_position_and_element(self) -> tuple:
        last_elements_list: list[tuple[ra.Position, Clip]] = []
        for single_part in self._items:
            part_last_element: oe.Element = single_part._last_element()
            if part_last_element is not None:
                # NEEDS TO TAKE INTO CONSIDERATION THE PART POSITION TOO
                last_elements_list.append(
                    ( single_part % ra.Position() + part_last_element % ra.Position(), part_last_element )
                )
        # In this case a dictionary works like a list of pairs where [0] is the key
        last_elements_list.sort(key=lambda pair: pair[0])
        if len(last_elements_list) > 0:
            return last_elements_list[-1]
        return None

    def _last_element(self) -> 'oe.Element':
        """
        Returns the `Element` with the last `Position` in the given `Part`.

        Args:
            None

        Returns:
            Element: The last `Element` of all elements in each `Clip`.
        """
        last_position_element: tuple = self._last_position_and_element()
        if last_position_element is not None:
            return last_position_element[1]
        return None

    def _last_element_position(self) -> ra.Position:
        """
        Returns the `Position` of tha last `Element`.

        Args:
            None

        Returns:
            Position: The `Position` of the last `Element` of all elements in each `Part`.
        """
        last_position_element: tuple = self._last_position_and_element()
        if last_position_element is not None:
            # NEEDS TO TAKE INTO CONSIDERATION THE PART POSITION TOO, SO DON'T REMOVE THIS METHOD
            return last_position_element[0]
        return None


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case og.TimeSignature():        return self._base_container._time_signature
                    case _:                         return super().__mod__(operand)
            case og.TimeSignature():        return self._base_container._time_signature.copy()
            case og.TimeSignature() | og.TimeSignature():
                return self._base_container._time_signature % operand
            case od.Names():
                all_names: list[str] = []
                for single_part in self._items:
                    all_names.append(single_part._name)
                return od.Names(*tuple(all_names))
            case _:
                return super().__mod__(operand)


    def get_unmasked_element_ids(self) -> set[int]:
        unmasked_element_ids: set[int] = set()
        for unmasked_part in self._items:
            unmasked_element_ids.update( unmasked_part.get_unmasked_element_ids() )
        return unmasked_element_ids

    def get_masked_element_ids(self) -> set[int]:
        masked_element_ids: set[int] = set()
        if self.is_a_mask():
            unmasked_ids: set[int] = self.get_unmasked_element_ids()
            for masked_part in self._base_container._items:
                for masked_clip in masked_part._base_container._items:
                    masked_element_ids.update({
                        id(masked_item) for masked_item in masked_clip._items
                        if id(masked_item) not in unmasked_ids
                    })
        return masked_element_ids


    def getPlotlist(self) -> list[dict]:
        """
        Returns the plotlist for a given Position.

        Returns:
            list[dict]: A list with multiple Plot configuration dictionaries.
        """
        plot_list: list = []
        masked_element_ids: set[int] = self.get_masked_element_ids()
        
        for single_part in self._base_container._items:
            part_plotlist: list[dict] = single_part.getPlotlist(masked_element_ids)
            # Part uses the Song staff as Elements use the Clip staff, so, no need for conversions
            plot_list.extend( part_plotlist )

        return plot_list


    def getPlaylist(self) -> list[dict]:
        """
        Returns the playlist for a given Position.

        Args:
            None

        Returns:
            list[dict]: A list with multiple Play configuration dictionaries.
        """
        play_list: list = []
        for single_part in self._base_container._items:
            play_list.extend(single_part.getPlaylist())
        return play_list

    def getMidilist(self) -> list[dict]:
        """
        Returns the midilist for a given Position.

        Args:
            None

        Returns:
            list[dict]: A list with multiple Midi file configuration dictionaries.
        """
        midi_list: list = []
        for single_part in self:
            midi_list.extend(single_part.getMidilist())
        return midi_list

    def getSerialization(self) -> dict:
        """
        Returns the serialization in a form of a dictionary of `Song` parameters.

        Args:
            None

        Returns:
            dict: A dictionary with multiple the `Song` configuration.
        """
        serialization = super().getSerialization()

        serialization["parameters"]["staff"] = self.serialize(self._time_signature)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        """
        Sets all `Song` parameters based on a dictionary input previously generated by `getSerialization`.

        Args:
            serialization: A dictionary with all the `Song` parameters.

        Returns:
            Song: The self Song object with the respective set parameters.
        """
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._time_signature = self.deserialize(serialization["parameters"]["staff"])
            self._set_owner_song()
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Song():
                super().__lshift__(operand)
                self._base_container._time_signature << operand._base_container._time_signature
                self._base_container._set_owner_song()

            case od.Pipe():
                match operand._data:
                    case og.TimeSignature():
                        self._base_container._time_signature = operand._data
                    case list():
                        if all(isinstance(item, Part) for item in operand._data):
                            self._items = [item for item in operand._data]
                            self._set_owner_song()
                        else:   # Not for me
                            for item in self._items:
                                item << operand._data
                    case _:
                        super().__lshift__(operand)

            case Part() | Clip() | oe.Element():
                self += operand

            case od.Serialization():
                self._base_container.loadSerialization( operand.getSerialization() )
            case og.TimeSignature() | og.TimeSignature():
                self._base_container._time_signature << operand
            case list():
                if all(isinstance(item, Part) for item in operand):
                    self._items = [item.copy() for item in operand]
                    self._set_owner_song()
                else:   # Not for me
                    for item in self._items:
                        item << operand
            case dict():
                if all(isinstance(item, Part) for item in operand.values()):
                    for index, item in operand.items():
                        if isinstance(index, int) and index >= 0 and index < len(self._items):
                            self._items[index] = item.copy()
                else:   # Not for me
                    for item in self._items:
                        item << operand

            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for single_part in self._items:
                    single_part << operand

        return self._sort_items()


    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Song():
                for single_part in operand:
                    self += single_part

            case Part():
                self._append([ Part(operand)._set_owner_song(self) ])._sort_items()

            case Clip():
                self += Part(operand)

            case oe.Element():
                self += Clip(operand)

            case list():
                for item in operand:
                    if isinstance(item, Part):
                        self._append([ item.copy()._set_owner_song(self) ])
                self._sort_items()
            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item += operand
                self._sort_items()
        return self


    # FROM PART TO BE ADAPTED
    def __isub__(self, operand: any) -> Self:
        match operand:
            case Song():
                return self._delete(operand._items)
            case Part():
                return self._delete([ operand ])
            case Clip():
                clip_part: Part = Part(operand)
                self -= clip_part
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
        return self._sort_items()


    def __imul__(self, operand: any) -> Self:
        match operand:
            case Song():
                right_song: Song = Song(operand)._set_owner_song(self)

                left_length: ra.Length = self % ra.Length()
                position_offset: ra.Position = ra.Position(left_length)

                for single_part in right_song:
                    single_part += position_offset

                self._append(right_song._items)
                
                if self._length_beats is not None:
                    self._length_beats += (right_song % ra.Length())._rational

            case Part():
                self.__imul__(Song(operand))

            case Clip():
                self.__imul__(Part(operand))

            case oe.Element():
                self.__imul__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Song = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__imul__(single_shallow_copy)
                elif operand == 0:
                    self._delete(self._base_container._items, True)
                
            case tuple():
                for single_operand in operand:
                    self.__imul__(single_operand)

            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__imul__(operand)
        return self._sort_items()


    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case Song():
                right_song: Song = Song(operand)._set_owner_song(self)

                left_length: ra.Length = self % ra.Duration() % ra.Length()
                position_offset: ra.Position = ra.Position(left_length.roundMeasures())

                for single_part in right_song:
                    single_part += position_offset

                self._append(right_song._items)  # Propagates upwards in the stack
                
                if self._length_beats is not None:
                    self._length_beats += (right_song % ra.Duration() % ra.Length())._rational

            case Part():
                self.__itruediv__(Song(operand))

            case Clip():
                self.__itruediv__(Part(operand))

            case oe.Element():
                self.__itruediv__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Part = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__itruediv__(single_shallow_copy)
                elif operand == 0:
                    self._delete(self._base_container._items, True)
                    
            case tuple():
                for single_operand in operand:
                    self.__itruediv__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__itruediv__(operand)
        return self._sort_items()

    def __ifloordiv__(self, operand: any) -> Self:
        match operand:
            case Song():
                self += operand

            case Part():
                self.__ifloordiv__(Song(operand))

            case Clip():
                self.__ifloordiv__(Part(operand))

            case oe.Element():
                self.__ifloordiv__(Clip(operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Song = self.shallow_copy()
                    for _ in range(operand - 1):
                        self += single_shallow_copy
                elif operand == 0:
                    self._delete(self._base_container._items, True)

            case tuple():
                for single_operand in operand:
                    self.__ifloordiv__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item.__ifloordiv__(operand)
        return self._sort_items()  # Shall be sorted!


    def loop(self, position = 0, length = 4) -> Self:
        """
        Creates a loop from the Composition from the given `Position` with a given `Length`.

        Args:
            position (Position): The given `Position` where the loop starts at.
            length (Length): The `Length` of the loop.

        Returns:
            Song: A copy of the self object with the items processed.
        """
        punch_length: ra.Length = ra.Length(self, Fraction(4))  # Exclusive
        if isinstance(length, (int, float, Fraction, ra.Length)):
            punch_length = ra.Length(self, length)

        # No Part is removed, only elements are removed
        for part_loop in self._items:
            part_loop.loop(position, punch_length)

        self._length_beats = punch_length._rational

        return self._sort_items()



class ClipGet(Container):
    """`ClipGet`

    ClipGet allows the extraction of multiple elements from a `Clip`.

    Parameters
    ----------
    tuple() : The sequence of parameters to be extracted in sequence.
    """
    def __init__(self, *operands):
        super().__init__()
        self._get: tuple = operands
        

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
            case od.Pipe():
                match operand._data:
                    case tuple():
                        return self._get
                    case _:
                        return super().__mod__(operand)
            case tuple():
                return self._get
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        """
        Returns the serialization in a form of a dictionary of `Container` parameters.

        Args:
            None

        Returns:
            dict: A dictionary with multiple the `Container` configuration.
        """
        serialization = super().getSerialization()

        serialization["parameters"]["get"] = self.serialize(self._get)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        """
        Sets all `Container` parameters based on a dictionary input previously generated by `getSerialization`.

        Args:
            serialization: A dictionary with all the `Container` parameters.

        Returns:
            Container: The self Container object with the respective set parameters.
        """
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "get" in serialization["parameters"]):

            super().loadSerialization(serialization)
            get_list: list = self.deserialize(serialization["parameters"]["get"])
            self._get: tuple = tuple(get_list)
        return self
    

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case ClipGet():
                super().__lshift__(operand)
                self._get = operand._get
            case od.Pipe():
                match operand._data:
                    case tuple():
                        self._get = operand
                    case _:
                        super().__lshift__(operand)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                # Remove previous Elements from the Container stack
                self._delete(self._items, True) # deletes by id, safer
                # Finally adds the decomposed elements to the Container stack
                self._append([
                    self.deep_copy(item) for item in operand
                ])
            case dict():
                for index, item in operand.items():
                    if isinstance(index, int) and index >= 0 and index < len(self._items):
                        self._items[index] = self.deep_copy(item)

            case tuple():
                self._get = operand
            case _: # Works for Frame too
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item in self._items:
                    item << operand
        return self


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
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item_i in range(self.len()):
                    self._items[item_i] += operand
        return self


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
                        self._delete([ self._items.pop() ], True)
                        operand -= 1
            case of.Frame():
                operand._set_inside_container(self)
                for item in self._items:
                    item -= operand
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item_i in range(self.len()):
                    self._items[item_i] -= operand
        return self


    # multiply with a scalar 
    def __imul__(self, operand: any) -> Self:
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
                        new_items: list = [
                            self.deep_copy( data ) for data in items_copy
                        ]
                        self._append(new_items)  # Propagates upwards in the stack
                        # self._items.extend(
                        #     self.deep_copy( data ) for data in items_copy
                        # )
                        operand -= 1
                    self._append(items_copy)  # Propagates upwards in the stack
                    # self._items.extend( items_copy )
                elif operand == 0:
                    self._delete(self._base_container._items, True)
            case ch.Chaos():
                return self.shuffle(operand.copy())
            case tuple():
                for single_operand in operand:
                    self.__imul__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item_i in range(self.len()):
                    self._items[item_i].__imul__(operand)
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
                    cut_len: int = self.len() % od.Pipe( operand )
                    nth_item: int = cut_len
                    while nth_item > 0:
                        many_operands._items.append(
                                self.deep_copy( self._items[cut_len - nth_item] )
                            )
                        nth_item -= 1
                    return many_operands

            case tuple():
                for single_operand in operand:
                    self.__itruediv__(single_operand)
            case _:
                if isinstance(operand, of.Frame):
                    operand._set_inside_container(self)
                for item_i in range(self.len()):
                    self._items[item_i].__itruediv__(operand)
        return self


