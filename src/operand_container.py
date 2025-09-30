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
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseEvent
    from matplotlib.widgets import Button
    import matplotlib.patheffects as patheffects
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
        self._mask_items: list = []
        self._masked: bool = False
        self._items_iterator: int = 0
        for single_operand in operands:
            self << single_operand

    def _replicate_to_mask(self) -> Self:
        mask_ids: set[int] = set()
        for mask_item in self._mask_items:
            mask_ids.add(id(mask_item))
        self._mask_items.clear()
        for item in self._items:
            if id(item) in mask_ids:
                self._mask_items.append(item)
        return self


    def _unmasked_items(self) -> list:
        if self._masked:
            return self._mask_items
        return self._items


    def __getitem__(self, index: int) -> any:
        if self._masked:
            return self._mask_items[index]
        return self._items[index]
    
    def __setitem__(self, index: int, value) -> Self:
        if self._masked:
            self._mask_items[index] = value
        else:
            self._items[index] = value
        return self._sort_items()   # Changing a given item should trigger the sorting of the Container
    

    def __iter__(self) -> Self:
        return self
    
    # To be used directly in for loops
    def __next__(self) -> any:
        items_to_iterate: list = self._items
        if self._masked:
            items_to_iterate = self._mask_items
        if self._items_iterator < len(items_to_iterate):
            item = items_to_iterate[self._items_iterator]
            self._items_iterator += 1
            return item  # It's the data that should be returned
        else:
            self._items_iterator = 0   # Reset to 0 when limit is reached
            raise StopIteration


    def _insert(self, items: list) -> Self:
        # Avoids redundant items/objects
        existing_ids: set[int] = {id(existing_item) for existing_item in self._items}
        new_items: list = [new_item for new_item in items if id(new_item) not in existing_ids]
        self._items = new_items + self._items
        if self._masked:
            self._mask_items = new_items + self._mask_items
        return self

    def _extend(self, items: list) -> Self:
        # Avoids redundant items/objects
        existing_ids: set[int] = {id(existing_item) for existing_item in self._items}
        new_items: list = [new_item for new_item in items if id(new_item) not in existing_ids]
        self._items.extend(new_items)
        if self._masked:
            self._mask_items.extend(new_items)
        return self


    def _append(self, item: any) -> Self:
        return self._extend([ item ])

    
    def _delete(self, items: list = None, by_id: bool = False) -> Self:
        if items is None:
            self._items.clear()
            self._mask_items.clear()
        else:
            if by_id:
                # removes by id instead
                self._items = [
                    single_item for single_item in self._items
                    if not any(single_item is item for item in items)
                ]
                self._mask_items = [
                    single_item for single_item in self._mask_items
                    if not any(single_item is item for item in items)
                ]
            else:
                # Uses "==" instead of id
                self._items = [
                    single_item for single_item in self._items
                    if single_item not in items
                ]
                self._mask_items = [
                    single_item for single_item in self._mask_items
                    if single_item not in items
                ]
        return self

    
    def _delete_by_ids(self, item_ids: set | None = None):
        if isinstance(item_ids, set):
            if item_ids:
                self._items = [
                    base_item for base_item in self._items
                    if id(base_item) not in item_ids
                ]
                self._mask_items = [
                    mask_item for mask_item in self._mask_items
                    if id(mask_item) not in item_ids
                ]
        else:
            self._items.clear()
            self._mask_items.clear()
        return self


    def _replace(self, old_item: Any = None, new_item: Any = None) -> Self:
        for index, item in enumerate(self._items):
            if old_item is item:
                self._items[index] = new_item
                break   # There is no repeated items
        for index, item in enumerate(self._mask_items):
            if old_item is item:
                self._mask_items[index] = new_item
                break   # There is no repeated items
        return self


    def _swap(self, left_item: Any = None, right_item: Any = None) -> Self:
        first_index: int = None
        for index, item in enumerate(self._items):
            if item is left_item or item is right_item:
                if first_index is None:
                    first_index = index
                else:
                    temp_item: Any = self._items[first_index]
                    self._items[first_index] = self._items[index]
                    self._items[index] = temp_item
                    break
        for index, item in enumerate(self._mask_items):
            if item is left_item or item is right_item:
                if first_index is None:
                    first_index = index
                else:
                    temp_item: Any = self._mask_items[first_index]
                    self._mask_items[first_index] = self._mask_items[index]
                    self._mask_items[index] = temp_item
                    break
        return self


    def _sort_items(self) -> Self:
        # This works with a list method sort (Operands implement __lt__ and __gt__)
        self._items.sort()
        self._mask_items.sort() # Faster this way
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
            case od.Pipe():
                match operand._data:
                    case list():
                        return [
                            item for item in self._unmasked_items()
                        ]
                    case _:
                        return super().__mod__(operand)
            case list():
                if operand: # Non empty list
                    parameters: list = []
                    for single_item in self._unmasked_items():
                        if isinstance(single_item, o.Operand):
                            operand_parameter: any = single_item
                            for single_parameter in operand:
                                operand_parameter %= single_parameter
                            parameters.append( operand_parameter )
                        else:
                            parameters.append( ol.Null() )
                    return parameters
                return [
                    self.deep_copy(item) for item in self._unmasked_items()
                ]
            case int():
                return self.len()
            case bool():
                return self._masked
            case Container():
                return operand.copy(self)
            
            case of.Frame():    # Only applicable to Operand items
                operand._set_inside_container(self)
                parameters: list = []
                for single_element in self._unmasked_items():
                    if isinstance(single_element, o.Operand):
                        operand_parameter: o.Operand = single_element
                        parameter_getter: list = operand ^ single_element
                        if isinstance(parameter_getter, list):
                            if parameter_getter:    # Non empty list
                                for single_parameter in parameter_getter:
                                    operand_parameter %= single_parameter
                                parameters.append( operand_parameter )
                            else:
                                parameters.append( single_element.copy() )
                return parameters

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
        return len(self._unmasked_items())

    def first(self) -> Any:
        """
        Gets the first Item accordingly to it's Position on the TimeSignature.

        Args:
            None

        Returns:
            Item: The first Item of all Items.
        """
        first_item: Any = None
        if self._unmasked_items():
            first_item = self._unmasked_items()[0]
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
        if self._unmasked_items():
            last_item = self._unmasked_items()[-1]
        return last_item

    def __eq__(self, other: any) -> bool:
        match other:
            case Container():
                return self._items == other._items
            case od.Conditional():
                return other == self
            case of.Frame():
                other._set_inside_container(self)
                for single_item in self._unmasked_items():
                    other_item = other.frame(single_item)
                    if not single_item == other_item:
                        return False
                return True
        if not isinstance(other, ol.Null):
            if other.__class__ == o.Operand:
                return True
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
            other._set_inside_container(self)
            for single_item in self._items:
                other_item = other.frame(single_item)
                if not single_item < other_item:
                    return False
            return True
        return self % other < other

    def __gt__(self, other: any) -> bool:
        if isinstance(other, of.Frame):
            other._set_inside_container(self)
            for single_item in self._items:
                other_item = other.frame(single_item)
                if not single_item > other_item:
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

        serialization["parameters"]["items"]        = self.serialize(self._items)
        serialization["parameters"]["mask_items"]   = self.serialize(self._mask_items)
        serialization["parameters"]["masked"]       = self.serialize(self._masked)
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
            "items" in serialization["parameters"] and "mask_items" in serialization["parameters"] and "masked" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._items = self.deserialize(serialization["parameters"]["items"])
            self._mask_items = self.deserialize(serialization["parameters"]["mask_items"])
            self._masked = self.deserialize(serialization["parameters"]["masked"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Container():
                super().__lshift__(operand)

                self._items = self.deep_copy(operand._items)
                self._mask_items.clear()
                if operand._mask_items:
                    operand_mask_items: list = operand._mask_items.copy()
                    for base_index, base_item in enumerate(operand._items):
                        for mask_item in operand_mask_items:
                            if mask_item is base_item:
                                self._mask_items.append(self._items[base_index])
                                operand_mask_items.pop(0)   # Removes the first item
                                break
                self._masked = operand._masked

            case od.Pipe():
                match operand._data:
                    case list():
                        # Remove previous Elements from the Container stack
                        self._delete() # deletes all
                        # Finally adds the decomposed elements to the Container stack
                        self._extend(operand._data)
                    case bool():
                        self._masked = operand._data

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                # Remove previous Elements from the Container stack
                self._delete() # deletes all
                # Finally adds the decomposed elements to the Container stack
                self._extend( [self.deep_copy(item) for item in operand] )
            case dict():
                for index, item in operand.items():
                    if isinstance(index, int) and index >= 0 and index < len(self._unmasked_items()):
                        self._unmasked_items()[index] = self.deep_copy(item)
            case bool():
                self._masked = operand
            case og.Mask():
                mask_parameters: tuple = operand._parameters
                self.mask(*mask_parameters)
            case og.Unmask():
                self.unmask()
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case of.Frame():
                operand._set_inside_container(self)
                for single_item in self._unmasked_items():
                    single_item << operand.frame(single_item)
            case _:
                for single_item in self._unmasked_items():
                    single_item << operand
        return self

    # Pass trough method that always results in a Container (Self)
    def __rshift__(self, operand) -> Self:
        match operand:
            case Container():
                return self + operand   # Implicit copy of self
            case og.ReadOnly():
                return operand.__rrshift__(self)
            case od.Inline():
                return self.__irshift__(operand)
            case _:
                return self.copy().__irshift__(operand)

    # Pass trough method that always results in a Container (Self)
    def __irshift__(self, operand) -> Self:
        match operand:
            case Container():
                self += operand
                return self
            case og.Process():
                return operand.__irrshift__(self)
            case od.Inline():
                return od.Inline(self)
            case ch.Chaos():
                return self.shuffle(operand)
            
            case tuple():
                return super().__irshift__(operand)
            case of.Frame():
                operand._set_inside_container(self)
                unmasked_items: list = self._unmasked_items()
                for index, single_item in enumerate(unmasked_items):
                    unmasked_items[index] >>= operand.frame(single_item)
                return self
            case _:
                return self.mask(operand)


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
                return self._extend(operand_items)
            case list():
                operand_items = [
                    self.deep_copy(single_item) for single_item in operand
                ]
                return self._extend(operand_items)
            
            case tuple():
                for single_operand in operand:
                    self += single_operand
            case of.Frame():
                operand._set_inside_container(self)
                for single_item in self._unmasked_items():
                    single_item += operand.frame(single_item)
            case _:
                for single_item in self._unmasked_items():
                    single_item += operand
        return self

    def __radd__(self, operand: any) -> Self:
        self_copy: Container = self.copy()
        self_copy._insert([ self.deep_copy( operand ) ])
        return self_copy

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Container():
                return self._delete(operand._items)
            case int(): # repeat n times the last argument if any
                if len(self._unmasked_items()) > 0:
                    while operand > 0 and len(self._unmasked_items()) > 0:
                        self._delete([ self._unmasked_items().pop() ], True)
                        operand -= 1
            case list():
                return self._delete(operand)
            
            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case of.Frame():
                operand._set_inside_container(self)
                for single_item in self._unmasked_items():
                    single_item -= operand.frame(single_item)
            case _:
                for single_item in self._unmasked_items():
                    single_item -= operand
        return self

    # multiply with a scalar
    def __imul__(self, operand: any) -> Self:
        match operand:
            case Container():
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
                        self._extend(new_items)  # Propagates upwards in the stack
                        operand -= 1
                    self._extend(items_copy)  # Propagates upwards in the stack
                elif operand == 0:
                    self._delete()
            case ch.Chaos():
                return self.shuffle(operand.copy())
            
            case tuple():
                for single_operand in operand:
                    self.__imul__(single_operand)
            case of.Frame():
                operand._set_inside_container(self)
                for single_item in self._unmasked_items():
                    single_item *= operand.frame(single_item)
            case _:
                for item in self._unmasked_items():
                    item.__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case Container():
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
            case of.Frame():
                operand._set_inside_container(self)
                for single_item in self._unmasked_items():
                    single_item /= operand.frame(single_item)
            case _:
                for item in self._unmasked_items():
                    item.__itruediv__(operand)
        return self

    def __ifloordiv__(self, operand: any) -> Self:
        match operand:
            case Container():
                pass

            case tuple():
                for single_operand in operand:
                    self.__ifloordiv__(single_operand)
            case of.Frame():
                operand._set_inside_container(self)
                for single_item in self._unmasked_items():
                    single_item //= operand.frame(single_item)
            case _:
                for item in self._unmasked_items():
                    item.__ifloordiv__(operand)
        return self


    def empty_copy(self, *parameters) -> Self:
        """
        Returns a Container with all the same parameters but the list that is empty.

        Args:
            *parameters: Any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Container: Returns the copy of self but with an empty list of items.
        """
        new_container: Container = self.__class__()
        new_container._masked = self._masked
        return new_container << parameters


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
        shallow_copy._items = self._items.copy()
        shallow_copy._mask_items = self._mask_items.copy()
        return shallow_copy << parameters
    

    def proxy(self) -> Self:
        """
        Creates and returns a shallow copy of the left side `>>` Container.

        Parameters
        ----------
        Any(None) : The Parameters to be set on the shallow copied `Container`.

        Returns:
            Container: Returns a shallow copy of the left side `>>` operand.
        """
        return self.shallow_copy()


    def process(self, input: any = None) -> Self:
        return self >> input

    def clear(self, *parameters) -> Self:
        """
        Clears all the given items in the present container and propagates the deletion
        of the same items for the containers above.

        Args:
            *parameters: After deletion, any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Container: Returns an empty self but with all the rest parameters untouched except the ones
            changed by the imputed Args.
        """
        self._delete(self._unmasked_items(), True)
        return super().clear(parameters)
    
    def erase(self, *parameters) -> Self:
        """
        Erases all the given items in the present container and propagates the deletion
        of the same items for the containers above.

        Args:
            *parameters: After deletion, any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Container: Returns an empty self but with all the rest parameters untouched except the ones
            changed by the imputed Args.
        """
        self._delete(self._unmasked_items(), True)
        for single_parameter in parameters:
            self << single_parameter
        return self


    def is_masked(self) -> bool:
        return self._masked
    

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
            data_index: int = chaos % 1 % len(parameters)
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
                left_mask: Clip = self.shallow_copy().mask(left_segment)
                right_mask: Clip = self.shallow_copy().mask(right_segment)
                left_mask << right_segment
                right_mask << left_segment
        else:
            if self._unmasked_items() and isinstance(what, type):
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
            self._swap(self._unmasked_items()[operand_i], self._unmasked_items()[self_len - 1 - operand_i])
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

    def rotate(self, right: int = 1, parameter: type = ra.Position) -> Self:
        """
        Rotates a given parameter by a given right amount, by other words,
        does a displacement for each Element in the Container list of
        a chosen parameter by the given right amount. Clockwise.

        Args:
            right (int): The right amount of the list index, displacement.
            parameter (type): The type of parameter being displaced, rotated.

        Returns:
            Container: The self object with the chosen parameter displaced.
        """
        parameter_instance = parameter()
        if isinstance(parameter_instance, od.Pipe):
            items: list = []
            for _ in len(self._items):
                item_index: int = right % len(self._items)
                items.append(self._items[item_index])   # No need to copy
                right += 1
            # Remove previous Elements from the Container stack
            self._delete(self._items, True) # deletes by id, safer
            # Finally adds the decomposed elements to the Container stack
            self._extend(items)
        else:
            parameters: list = []
            for operand in self._unmasked_items():
                if isinstance(operand, o.Operand):
                    parameters.append( operand % parameter_instance )
                else:
                    parameters.append( ol.Null() )
            for operand in self._unmasked_items():
                if isinstance(operand, o.Operand):
                    operand << parameters[ right % len(parameters) ]
                right += 1
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
        self._masked = False    # Has to apply to the entire content
        if conditions:
            excluded_item_ids: set = set()
            # And type of conditions, not meeting any means excluded
            for single_condition in conditions:
                match single_condition:
                    case Container():
                        excluded_item_ids.update(
                            id(single_item) for single_item in self._items
                            if not any(single_item == cond_item for cond_item in single_condition)
                        )
                    case of.Frame():
                        single_condition._set_inside_container(self)
                        for single_item in self._items:
                            if not single_item == single_condition.frame(single_item):
                                excluded_item_ids.add(id(single_item))
                    case _:
                        excluded_item_ids.update(
                            id(single_item) for single_item in self._items
                            if not single_item == single_condition
                        )
            self._mask_items = [
                unmasked_item for unmasked_item in self._items
                if id(unmasked_item) not in excluded_item_ids
            ]
        self._masked = True
        return self

    def unmask(self) -> Self:
        self._masked = False
        return self
    
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
        excluded_item_ids: set = set()
        if conditions:
            # And type of conditions, not meeting any means excluded
            for single_condition in conditions:
                match single_condition:
                    case Container():
                        excluded_item_ids.update(
                            id(single_item) for single_item in self._items
                            if not any(single_item == cond_item for cond_item in single_condition)
                        )
                    case of.Frame():
                        single_condition._set_inside_container(self)
                        for single_item in self._items:
                            if not single_item == single_condition.frame(single_item):
                                excluded_item_ids.add(id(single_item))
                    case _:
                        excluded_item_ids.update(
                            id(single_item) for single_item in self._items
                            if not single_item == single_condition
                        )
        return self._delete_by_ids(excluded_item_ids)


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

    Represents a list of Devices passed to the clip `Track`, all these devices are intended
    to be connected as destiny of the generated Clock messages by the JsonMidiPlayer.

    Parameters
    ----------
    list([]) : A list of Devices names, str, are intended to be considered Items.
    str : A device name to be added to the beginning of the Devices list.
    int : Returns the len of the list.
    """
    pass


#####################################################################################################
###########################################  COMPOSITION  ###########################################
#####################################################################################################

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
        # Song sets the TimeSignature, this is just a reference
        self._time_signature: og.TimeSignature  = og.settings._time_signature
        self._length_beats: Fraction            = None


    def _get_time_signature(self) -> 'og.TimeSignature':
        return og.settings._time_signature


    def _has_elements(self) -> bool:
        return False

    def _total_elements(self) -> int:
        return 0

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

    def composition_filename(self) -> str:
        # Process title separately (replace whitespace with underscores)
        title: str = self % str()
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

    def last_position(self) -> 'ra.Position':
        return self._last_element_position()


    def length(self) -> 'ra.Length':
        """
        Returns the rounded `Length` to `Measures` that goes from 0 to position of the last `Element`.

        Args:
            None

        Returns:
            Length: Equal to last `Element` position converted to `Length` and rounded by `Measures`.
        """
        if self._has_elements():
            last_position: ra.Position = self._last_element_position()
            position_length: ra.Length = ra.Length( last_position.roundMeasures() ) + ra.Measures(1)
            finish_length: ra.Length = ra.Length( self.finish().roundMeasures() )
            if finish_length > position_length:
                return finish_length
            return position_length
        return ra.Length(self, 0)
    
    
    def duration(self) -> 'ra.Duration':
        """
        Returns the `Duration` that goes from 0 to the `finish` of all elements.

        Args:
            None

        Returns:
            Duration: Equal to `Clip.finish()` converted to `Duration`.
        """
        if self._has_elements():
            return ra.Duration(self.finish())
        return ra.Duration(self, 0)
    
    def net_duration(self) -> 'ra.Duration':
        """
        Returns the `Duration` that goes from `start` to the `finish` of all elements.

        Args:
            None

        Returns:
            Duration: Equal to `Clip.finish() - Clip.start()` converted to `Duration`.
        """
        if self._has_elements():
            return ra.Duration(self.finish() - self.start())
        return ra.Duration(self, 0)
    
    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case Composition():
                return self._time_signature == other._time_signature \
                    and super().__eq__(other)
            case _:
                return super().__eq__(other)

    def all_elements(self) -> list[oe.Element]:
        return []

    def at_position_elements(self, position: 'ra.Position') -> list[oe.Element]:
        return []


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
            case bool():
                return self._masked
            case int():
                if self._items:
                    last_element_position: ra.Position = self._last_element_position()
                    measures_length: ra.Length = ra.Length(last_element_position)
                    return measures_length % ra.Measure() % int()
                return 0
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
                self._length_beats = operand._rational
                if self._length_beats < 0:
                    self._length_beats = None
            case None:
                self._length_beats = None

            case _:
                super().__lshift__(operand)
        return self


    def fit(self, tie_splits: bool = True) -> Self:
        """
        Fits all the `Element` items into the respective Measure doing an optional tie if a `Note`.

        Args:
            tie_splits (bool): Does a tie of all splitted Notes.

        Returns:
            Composition: The same self object with the items processed.
        """
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
        "#4CAF50",  # Green (starting point)    01
        "#2196F3",  # Blue                      02
        "#FF5722",  # Orange                    03
        "#9C27B0",  # Purple                    04
        "#FFEB3B",  # Bright Yellow             05
        "#FF9800",  # Amber                     06
        "#E91E63",  # Pink                      07
        "#00BCD4",  # Cyan                      08
        "#8BC34A",  # Light Green               09
        "#FFC107",  # Gold                      10
        "#4A5ED3",  # Indigo                    11
        "#FF5252",  # Light Red                 12
        "#2B184D",  # Deep Purple               13
        "#CDDC39",  # Lime                      14
        "#03A9F4",  # Light Blue                15
        "#FF4081",  # Hot Pink                  16
    ]

    _white_key_heigh: float = 1.0
    _black_key_heigh: float = 1.0
    _b3_key_heigh: float = 1.0
    _c4_key_heigh: float = 1.0
    _octave_heigh: float = 7 * _white_key_heigh + 5 * _black_key_heigh
    _white_above_black_heigh: float = _white_key_heigh - _black_key_heigh
    _previous_black_keys: tuple[int] = (0, 0, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5)

    @staticmethod
    def _pitch_to_y(pitch: float) -> float:
        y: float = 0.0
        pitch_int: int = int(pitch)
        octaves: int = pitch_int // 12
        y += octaves * Composition._octave_heigh
        if pitch_int > 59:
            y += Composition._b3_key_heigh - Composition._white_key_heigh
            if pitch_int > 60:
                y += Composition._c4_key_heigh - Composition._white_key_heigh
        pitch_octave: int = pitch_int % 12
        y += pitch_octave * Composition._white_key_heigh
        y -= Composition._previous_black_keys[pitch_octave] * Composition._white_above_black_heigh
        key_float: float = pitch - pitch_int
        key_heigh: float = Composition._white_key_heigh
        if pitch_int == 59:
            key_heigh = Composition._b3_key_heigh
        elif pitch_int == 60:
            key_heigh = Composition._c4_key_heigh
        elif o.is_black_key(pitch_int):
            key_heigh = Composition._black_key_heigh
        y += key_heigh * key_float
        return y

    @staticmethod
    def _y_to_pitch(y: float) -> float:
        pitch: float = 0.0
    
        return pitch


    def _plot_elements(self, plotlist: list[dict], time_signature: 'og.TimeSignature'):
        """
        The method that does the heavy work of plotting
        """
        self._ax.clear()

        # Chart title (TITLE)
        self._ax.set_title(f"{self._title + " - " if self._title != "" else ""}"
                           f"{self._iterations[self._iteration].__class__.__name__} - "
                           f"{"Mask - " if self._iterations[self._iteration].is_masked() else ""}"
                           f"Iteration {self._iteration} of {len(self._iterations) - 1 if len(self._iterations) > 1 else 0
        }")

        # Horizontal X-Axis, Time related (COMMON)

        composition_tempo: float = float(plotlist[0]["tempo"])
        # # 1. Disable autoscaling and force limits
        # self._ax.set_autoscalex_on(False)
        # current_min, current_max = self._ax.get_xlim()
        # self._ax.set_xlim(current_min, current_max * 1.03)
        self._ax.margins(x=0)  # Ensures NO extra padding is added on the x-axis

        beats_per_measure: Fraction = time_signature % ra.BeatsPerMeasure() % Fraction()
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

            # As Channels
            if self._by_channel:
                self._ax.set_ylabel("Channels")

                # Set MIDI channel ticks with Middle C in bold
                self._ax.set_yticks(range(17))  # Needs to accommodate all labels, so, it's 17
                self._ax.tick_params(axis='y', which='both', length=0)
                y_labels = ['R'] + [
                    channel_0 + 1 for channel_0 in range(16)
                ]
                self._ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')
                self._ax.set_ylim(0 - 0.5, 16 + 0.5)  # Ensure all channels fit

                # Where the corner Coordinates are defined
                self._ax.format_coord = lambda x, y: (
                    f"Time = {int(x / composition_tempo * 60 // 60)}'"
                    f"{int(x / composition_tempo * 60 % 60)}''"
                    f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
                    f"Measure = {int(x / beats_per_measure)}, "
                    f"Beat = {int(x % beats_per_measure)}, "
                    f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                    f"Channel = {round(y)}"
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

                    # Shade Odd Channels (1 based)
                    for channel_0 in range(16):
                        if channel_0 % 2 == 1:
                            self._ax.axhspan(channel_0 - 0.5, channel_0 + 0.5, color='lightgray', alpha=0.5)

                    # Plot notes
                    for channel_0 in note_channels:
                        channel_color = Clip._channel_colors[channel_0]
                        channel_plotlist = [
                            channel_note for channel_note in note_plotlist
                            if channel_note["channel"] == channel_0
                        ]

                        for note in channel_plotlist:
                            if type(note["self"]) is oe.Rest:
                                # Available hatch patterns: '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'
                                color_alpha: float = 1.0
                                if note["masked"]:
                                    color_alpha = 0.2
                                self._ax.barh(y = 0.0, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]),
                                    height=0.30, color='none', hatch='', edgecolor='black', linewidth=1.0, linestyle='solid', alpha = color_alpha)
                            else:
                                bar_hatch: str = ''
                                line_style: str = 'solid'
                                if isinstance(note["self"], oe.KeyScale):
                                    line_style = 'dashed'
                                elif isinstance(note["self"], oe.Retrigger):
                                    line_style = 'dotted'
                                edge_color: str = 'black'
                                if not note["enabled"]:
                                    edge_color = 'white'

                                color_alpha: float = round(0.3 + 0.7 * (note["velocity"] / 127), 2)

                                if note["velocity"] > 127:
                                    edge_color = 'red'
                                    color_alpha = 1.0
                                elif note["velocity"] < 0:
                                    edge_color = 'blue'
                                    color_alpha = 1.0

                                if note["masked"]:
                                    color_alpha = 0.2
                                    
                                if note["tied"]:
                                    self._ax.barh(y = note["channel"] + 1, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                            height=0.3 - 0.1, color='none', hatch='|', edgecolor=channel_color, linewidth=0, linestyle='solid', alpha=color_alpha)
                                    self._ax.barh(y = note["channel"] + 1, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                            height=0.3, color='none', hatch=bar_hatch, edgecolor=edge_color, linewidth=1.0, linestyle=line_style, alpha=color_alpha)

                                else:
                                    self._ax.barh(y = note["channel"] + 1, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                            height=0.3, color=channel_color, hatch=bar_hatch, edgecolor=edge_color, linewidth=1.0, linestyle=line_style, alpha=color_alpha)

                                if "middle_pitch" in note:
                                    self._ax.hlines(y=note["channel"] + 1, xmin=float(note["position_on"]), xmax=float(note["position_off"]), 
                                                    color='black', linewidth=0.5, alpha=color_alpha)
                
                
            # As Chromatic keys
            else:

                self._ax.set_ylabel("Chromatic Keys")
                # Where the corner Coordinates are defined
                self._ax.format_coord = lambda x, y: (
                    f"Time = {int(x / composition_tempo * 60 // 60)}'"
                    f"{int(x / composition_tempo * 60 % 60)}''"
                    f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
                    f"Measure = {int(x / beats_per_measure)}, "
                    f"Beat = {int(x % beats_per_measure)}, "
                    f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                    f"Pitch = {int(y + 0.5)}"
                )

                # Solid line at y = 60 the Middle C
                self._ax.axhline(y=60 - 0.5, color='gray', linestyle='-', linewidth=1.0)

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
                    min_pitch: int = int(min(note["pitch"] for note in note_plotlist) // 12 * 12)
                    max_pitch: int = int(max(note["pitch"] for note in note_plotlist) // 12 * 12 + 12)

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

                    # Set MIDI note ticks with Middle C in bold
                    self._ax.set_yticks(range(min_pitch, max_pitch + 1))
                    self._ax.tick_params(axis='y', which='both', length=0)

                    # # Only show tick marks for octaves (pitch % 12 == 0)
                    # for tick in self._ax.yaxis.get_major_ticks():
                    #     if tick.get_loc() % 12 != 0:  # If not an octave
                    #         tick.tick1line.set_visible(False)  # Hide left tick
                    #         tick.tick2line.set_visible(False)  # Hide right tick

                    # Where the VERTICAL axis is defined - Chromatic Keys
                    chromatic_keys: list[str] = ["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"]
                    
                    y_labels = [
                        chromatic_keys[pitch % 12] + (str(pitch // 12 - 1) if pitch % 12 == 0 else "")
                        for pitch in range(min_pitch, max_pitch + 1)
                    ]  # Bold Middle C
                    self._ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')

                    # Adjust alignment and shift
                    for label in self._ax.get_yticklabels():
                        label.set_horizontalalignment("right")  # right-align text
                        label.set_x(-0.005)                     # shift a bit left (tweak as needed)

                    self._ax.set_ylim(min_pitch - 0.5, max_pitch + 0.5)  # Ensure all notes fit

                    # Shade and shorten black keys and enlarge B3 and C4 keys
                    for pitch in range(min_pitch, max_pitch + 1):
                        if o.is_black_key(pitch):   # Make it less taller, 0.6 instead of 1.0
                            self._ax.axhspan(pitch - 0.3, pitch + 0.3, color='lightgray', alpha=0.5)

                    # Plot notes per Channel
                    for channel_0 in note_channels:
                        printed_channel_number: bool = False
                        channel_color = Clip._channel_colors[channel_0]
                        channel_plotlist = [
                            channel_note for channel_note in note_plotlist
                            if channel_note["channel"] == channel_0
                        ]
                        staff_modes: dict[int, int] = {}
                        staff_tonic_keys: dict[int, int] = {}
                        staff_sharps_or_flats: dict[int, list[int]] = {}
                        last_mode_measure: int = -1
                        last_tonic_key_measure: int = -1
                        last_sharps_or_flats_measure: int = -1

                        for note in channel_plotlist:
                            if type(note["self"]) is oe.Rest:
                                # Available hatch patterns: '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'
                                color_alpha: float = 1.0
                                if note["masked"]:
                                    color_alpha = 0.2
                                self._ax.barh(y = note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]),
                                    height=0.40, color='none', hatch='', edgecolor='black', linewidth=1.0, linestyle='solid', alpha = color_alpha)
                            else:
                                if o.is_black_key(round(note["pitch"])):
                                    bar_height: float = 0.25
                                else:
                                    bar_height: float = 0.40
                                bar_hatch: str = ''
                                line_style: str = 'solid'
                                if isinstance(note["self"], oe.KeyScale):
                                    line_style = 'dashed'
                                elif isinstance(note["self"], oe.Retrigger):
                                    line_style = 'dotted'
                                edge_color: str = 'black'
                                if not note["enabled"]:
                                    edge_color = 'white'

                                color_alpha: float = round(0.3 + 0.7 * (note["velocity"] / 127), 2)
                                if note["velocity"] > 127:
                                    edge_color = 'red'
                                    color_alpha = 1.0
                                elif note["velocity"] < 0:
                                    edge_color = 'blue'
                                    color_alpha = 1.0
                                
                                if note["masked"]:
                                    color_alpha = 0.2

                                if note["tied"]:
                                    self._ax.barh(y = note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                            height=bar_height - 0.1, color='none', hatch='|', edgecolor=channel_color, linewidth=0, linestyle='solid', alpha=color_alpha)
                                    self._ax.barh(y = note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                            height=bar_height, color='none', hatch=bar_hatch, edgecolor=edge_color, linewidth=1.0, linestyle=line_style, alpha=color_alpha)

                                else:
                                    self._ax.barh(y=note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                            height=bar_height, color=channel_color, hatch=bar_hatch, edgecolor=edge_color, linewidth=1.0, linestyle=line_style, alpha=color_alpha)

                                if "middle_pitch" in note:
                                    self._ax.hlines(y=note["middle_pitch"], xmin=float(note["position_on"]), xmax=float(note["position_off"]), 
                                                    color='black', linewidth=0.5, alpha=color_alpha)

                                # note Measures to keep track of
                                note_measure: int = int(note["position_on"] // beats_per_measure)
                                flag_update_key_signature: bool = False

                                if note_measure not in staff_modes:
                                    mode: int = note["mode"]
                                    if last_mode_measure < 0 or staff_modes[last_mode_measure] != mode:
                                        staff_modes[note_measure] = mode
                                        base_pitch: int = max_pitch - 12
                                        mode_marker: str = 'Major'
                                        match note['mode']:
                                            case 0:
                                                pass
                                            case 5:
                                                mode_marker = 'minor'
                                            case 1:
                                                mode_marker = 'Dorian'
                                            case 2:
                                                mode_marker = 'Phrygian'
                                            case 3:
                                                mode_marker = 'Lydian'
                                            case 4:
                                                mode_marker = 'Mixolydian'
                                            case 6:
                                                mode_marker = 'Locrian'
                                        self._ax.text(float(note_measure * beats_per_measure) + 0.05, base_pitch + 12, mode_marker, ha='left', va='center', fontsize=6, color='black')
                                        flag_update_key_signature = True
                                        last_mode_measure = note_measure
                                else:
                                    last_mode_measure = note_measure

                                if note_measure not in staff_tonic_keys:
                                    tonic_key: int = note["tonic_key"]
                                    if last_tonic_key_measure < 0 or staff_tonic_keys[last_tonic_key_measure] != tonic_key:
                                        staff_tonic_keys[note_measure] = tonic_key
                                        base_pitch: int = max_pitch - 12
                                        self._ax.text(float(note_measure * beats_per_measure) + 0.05, base_pitch + tonic_key, 'T', ha='left', va='center', fontsize=5, color='black')
                                        flag_update_key_signature = True
                                        last_tonic_key_measure = note_measure
                                else:
                                    last_tonic_key_measure = note_measure

                                if note_measure not in staff_sharps_or_flats:
                                    if flag_update_key_signature:
                                        diatonic_mode_0: int = staff_modes[last_mode_measure]
                                        diatonic_scale: list[int] = og.Scale.get_diatonic_scale(diatonic_mode_0 + 1)
                                        tonic_key: int = staff_tonic_keys[last_tonic_key_measure]
                                        scale_accidentals: list[int] = og.Scale.sharps_or_flats_picker(tonic_key, diatonic_scale)
                                        if last_sharps_or_flats_measure < 0 or staff_sharps_or_flats[last_sharps_or_flats_measure] != scale_accidentals:
                                            staff_sharps_or_flats[note_measure] = scale_accidentals
                                            
                                            for accidental_key, accidental in enumerate(scale_accidentals):
                                                chromatic_pitch: int = base_pitch
                                                if accidental > 0:
                                                    accidental_key += 1
                                                    chromatic_pitch += accidental_key % 12
                                                    self._ax.text(float(note_measure * beats_per_measure) - 0.05, chromatic_pitch, '♯', ha='right', va='center', fontsize=10, fontweight='bold', color='black')
                                                elif accidental < 0:
                                                    accidental_key -= 1
                                                    chromatic_pitch += accidental_key % 12
                                                    self._ax.text(float(note_measure * beats_per_measure) - 0.05, chromatic_pitch, '♭', ha='right', va='center', fontsize=10, fontweight='bold', color='black')

                                            last_sharps_or_flats_measure = note_measure
                                else:
                                    last_sharps_or_flats_measure = note_measure


                                # Where the bar accidentals are plotted
                                if note["accidentals"]:
                                    symbol: str = ''
                                    if note["accidentals"] > 0: # Sharped
                                        symbol = '♯' * note["accidentals"]
                                    else:                       # Flattened
                                        symbol = '♭' * (note["accidentals"] * -1)
                                    y_pos: int = note["pitch"]
                                    x_pos = float(note["position_on"]) - 0.1
                                    self._ax.text(x_pos, y_pos, symbol, ha='center', va='center', fontsize=14, fontweight='bold',
                                        color='black',  # Outline color
                                        path_effects=[patheffects.withStroke(linewidth=1.4, foreground=channel_color)],
                                        alpha=color_alpha)

                                if not printed_channel_number:
                                    y_pos: int = note["pitch"] + 0.2
                                    x_pos = (float(note["position_on"]) + float(note["position_off"])) / 2
                                    self._ax.text(x_pos, y_pos, channel_0 + 1, ha='center', va='bottom', fontsize=6,
                                        color='black',  # Outline color
                                        path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                                        alpha=color_alpha)
                                    printed_channel_number = True
                                        

        # Plot Automations
        else:

            self._ax.set_ylabel("Automation Values (MSB)")
            # Where the corner Coordinates are defined
            self._ax.format_coord = lambda x, y: (
                f"Time = {int(x / composition_tempo * 60 // 60)}'"
                f"{int(x / composition_tempo * 60 % 60)}''"
                f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
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
                for channel_0 in automation_channels:
                    printed_channel_number: bool = False
                    channel_color = Clip._channel_colors[channel_0]
                    channel_plotlist = [
                        channel_automation for channel_automation in automation_plotlist
                        if channel_automation["channel"] == channel_0
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

                        edge_color: str = 'black'
                        if not automation["enabled"]:
                            edge_color = 'white'
                                
                        # Actual data points
                        self._ax.plot(x, y, marker='o', linestyle='None', color=channel_color,
                                    markeredgecolor=edge_color, markeredgewidth=1, markersize=8, alpha = color_alpha)

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

                        if not printed_channel_number:
                            y_pos: int = automation["value"] + 2
                            x_pos = automation["position"]
                            self._ax.text(x_pos, y_pos, channel_0 + 1, ha='center', va='bottom', fontsize=6,
                                color='black',  # Outline color
                                path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                                alpha=color_alpha)
                            printed_channel_number = True
                                        

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
            f"Measures played at {round(composition_tempo, 1)}bpm for "
            f"{int(last_position / composition_tempo * 60 // 60)}'"
            f"{int(last_position / composition_tempo * 60 % 60)}''"
            f"{int(last_position / composition_tempo * 60_000 % 1000)}ms"
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
        iteration_self: Composition = self._iterations[self._iteration]
        threading.Thread(target=og.Play.play, args=(iteration_self,)).start()
        return self

    def _run_first(self, even = None) -> Self:
        if self._iteration > 0:
            self._iteration = 0
            plotlist: list[dict] = self._plot_lists[self._iteration]
            self._plot_elements(plotlist, self._iterations[self._iteration]._time_signature)
            self._enable_button(self._next_button)
            if self._iteration == 0:
                self._disable_button(self._previous_button)
        return self

    def _run_previous(self, even = None) -> Self:
        if self._iteration > 0:
            self._iteration -= 1
            plotlist: list[dict] = self._plot_lists[self._iteration]
            self._plot_elements(plotlist, self._iterations[self._iteration]._time_signature)
            self._enable_button(self._next_button)
            if self._iteration == 0:
                self._disable_button(self._previous_button)
        return self

    def _run_next(self, even = None) -> Self:
        if self._iteration < len(self._plot_lists) - 1:
            self._iteration += 1
            plotlist: list[dict] = self._plot_lists[self._iteration]
            self._plot_elements(plotlist, self._iterations[self._iteration]._time_signature)
            self._enable_button(self._previous_button)
            if self._iteration == len(self._plot_lists) - 1:
                self._disable_button(self._next_button)
        return self

    def _run_last(self, even = None) -> Self:
        if self._iteration < len(self._plot_lists) - 1:
            self._iteration = len(self._plot_lists) - 1
            plotlist: list[dict] = self._plot_lists[self._iteration]
            self._plot_elements(plotlist, self._iterations[self._iteration]._time_signature)
            self._enable_button(self._previous_button)
            if self._iteration == len(self._plot_lists) - 1:
                self._disable_button(self._next_button)
        return self

    def _update_iteration(self, iteration: int, plotlist: list[dict]) -> Self:
        self._plot_lists[iteration] = plotlist
        if iteration == self._iteration:
            self._plot_elements(plotlist, self._iterations[iteration]._time_signature)
        return self

    def _run_new(self, even = None) -> Self:
        if callable(self._n_function):
            # Keeps iterating the root/seed composition
            new_iteration: Composition = self._n_function(self.copy())
            if isinstance(new_iteration, Composition):
                self._iteration = len(self._iterations)
                plotlist: list[dict] = new_iteration.getPlotlist()
                self._iterations.append(new_iteration)
                self._plot_lists.append(plotlist)
                self._plot_elements(plotlist, new_iteration._time_signature)
                self._enable_button(self._previous_button)
                self._disable_button(self._next_button)
        return self

    def _run_composition(self, even = None) -> Self:
        import threading
        if isinstance(self._composition, Composition):
            iteration_self: Composition = self._iterations[self._iteration]
            threading.Thread(target=og.Play.play, args=(self._composition + iteration_self,)).start()
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
    
    def _onclick(self, event: MouseEvent) -> Self:
        import threading
        if event.button == 3 and event.xdata is not None and event.ydata is not None:   # 1=left, 2=middle, 3=right
            composition = self._iterations[self._iteration]
            at_position_elements: list[oe.Element] = composition.at_position_elements(ra.Position(ra.Beats(event.xdata)))
            at_position_notes: list[oe.Note] = [
                single_note.copy() for single_note in at_position_elements
                if isinstance(single_note, oe.Note)
            ]
            if at_position_notes:
                if self._by_channel:
                    if 0 <= round(event.ydata - 1) < 16:
                        # Sort by Position in reverse instead
                        at_position_notes.sort(key=lambda note:note._position_beats * -1)
                        at_position_notes = [ at_position_notes[0] ]    # Just a single note is played
                        at_position_notes[0]._channel_0 = round(event.ydata - 1)
                        at_position_notes[0]._position_beats = Fraction(0)
                    else:
                        return self
                else:
                    # Sort by Pitch instead
                    at_position_notes.sort(key=lambda note:note._pitch.pitch_int())
                    minimum_position: Fraction = None
                    plotting_pitch: int = int(event.ydata + 0.5)
                    for single_note in at_position_notes:
                        if minimum_position is None:
                            minimum_position = single_note._position_beats
                            root_pitch: int = single_note._pitch.pitch_int()
                            single_note._pitch << plotting_pitch
                            plotting_pitch -= root_pitch
                        else:
                            if single_note._position_beats < minimum_position:
                                minimum_position = single_note._position_beats
                            single_note._pitch += plotting_pitch
                    for single_note in at_position_notes:
                        single_note._position_beats -= minimum_position
                    
                threading.Thread(target=og.Play.play, args=(Clip( od.Pipe(at_position_notes) ),)).start()
        return self


    def plot(self, by_channel: bool = False, block: bool = True, pause: float = 0, iterations: int = 0,
            n_button: Optional[Callable[['Composition'], 'Composition']] = None,
            composition: Optional['Composition'] = None, title: str | None = None) -> Self:
        """
        Plots the `Note`s in a `Composition`, if it has no Notes it plots the existing `Automation` instead.

        Args:
            by_channel: Allows the visualization in a Drum Machine alike instead of by Pitch.
            block (bool): Suspends the program until the chart is closed.
            pause (float): Sets a time in seconds before the chart is closed automatically.
            iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
                this is dependent on a n_button being given.
            n_button (Callable): A function that takes a Composition to be used to generate a new iteration.
            composition (Composition): A composition to be played together with the plotted one.
            title (str): A title to give to the chart in order to identify it.

        Returns:
            Composition: Returns the presently plotted composition.
        """
        self._iterations: list[Composition] = [ self.copy() ]   # Works with a forced copy (Read Only)
        self._plot_lists: list[list] = [ self.getPlotlist() ]
        self._by_channel: bool = by_channel
        self._iteration: int = 0
        self._n_function = n_button
        self._composition = composition
        if not isinstance(title, str):
            self._title: str = self % str()
        else:
            self._title: str = title

        if callable(self._n_function) and isinstance(iterations, int) and iterations > 0:
            for _ in range(iterations):
                new_composition: Composition = self._n_function(self.copy())
                new_plotlist: list[dict] = new_composition.getPlotlist()
                self._iterations.append(new_composition)
                self._plot_lists.append(new_plotlist)
                self._iteration += 1

        # Enable interactive mode (doesn't block the execution)
        plt.ion()

        # Where the window title is set too
        self._fig, self._ax = plt.subplots(num=self._title, figsize=(12, 6))
        # Replace handler
        try:
            # self._fig.canvas.mpl_disconnect(self._fig.canvas.manager.key_press_handler_id)
            # mpl.rcParams['keymap.back'].remove('left')
            # mpl.rcParams['keymap.forward'].remove('right')

            # Get the current keymap
            current_keymap: list = plt.rcParams['keymap.all_axes']
            # Remove the 'p' key binding
            current_keymap.remove('p')
            current_keymap.remove('s')
            # Update the rcParams
            plt.rcParams['keymap.all_axes'] = current_keymap
        except Exception as e:
            print(f"Unable to disable default keys!")
        self._fig.canvas.mpl_connect('key_press_event', lambda event: self._on_key(event))
        self._fig.canvas.mpl_connect('button_press_event', lambda event: self._onclick(event))

        # Where the plotting is done
        self._plot_elements(self._plot_lists[self._iteration], self._iterations[self._iteration]._time_signature)

        # Where the padding is set
        plt.tight_layout()

        plt.subplots_adjust(right=0.975)  # 2.5% right padding
        # Avoids too thick hatch lines
        plt.rcParams['hatch.linewidth'] = 3.00  # Where the HATCH thickness is set

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
        save_button = Button(ax_button, 'S', color='white', hovercolor='grey')
        save_button.on_clicked(self._run_save)

        # Execution Button Widget
        ax_button = plt.axes([0.979, 0.468, 0.015, 0.05])
        export_button = Button(ax_button, 'E', color='white', hovercolor='grey')
        export_button.on_clicked(self._run_export)

        # Render Button Widget
        ax_button = plt.axes([0.979, 0.408, 0.015, 0.05])
        render_button = Button(ax_button, 'R', color='white', hovercolor='grey')
        render_button.on_clicked(self._run_render)

        # Previous Button Widget
        if self._iteration == 0:
            self._disable_button(self._previous_button)
        # Next Button Widget
        self._disable_button(self._next_button)

        if not callable(self._n_function):
            # New Button Widget
            self._disable_button(new_button)

        if not isinstance(self._composition, Composition):
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
            iterated_composition: Composition = self.copy()
            if callable(n_button) and isinstance(iterations, int) and iterations > 0:
                for _ in range(iterations):
                    iterated_composition = n_button(self.copy())
            return iterated_composition



#####################################################################################################
##############################################  CLIP  ###############################################
#####################################################################################################


TypeClip = TypeVar('TypeClip', bound='Clip')    # TypeClip represents any subclass of Operand


class Clip(Composition):  # Just a container of Elements
    """`Container -> Composition -> Clip`

    This type of `Container` aggregates only `Element` items. This is the only class
    that can be Plotted.

    Parameters
    ----------
    list([]) : A list of `Element` type items.
    int : Returns the len of the list.
    TimeSignature(settings) : A Time Signature on which `TimeValue` units are based and `Element` items placed.
    MidiTrack("Track 1") : Where the track name and respective Devices are set.
    None, Length : Returns the length of all combined elements.
    """
    def __init__(self, *operands):
        super().__init__()
        self._time_signature: og.TimeSignature  = og.settings._time_signature.copy()
        self._midi_track: ou.MidiTrack  = ou.MidiTrack()
        self._items: list[oe.Element]   = []
        self._mask_items: list[oe.Element] = []
        for single_operand in operands:
            self << single_operand

    def _get_time_signature(self) -> 'og.TimeSignature':
        return self._time_signature

    def _index_from_frame(self, frame: of.Frame) -> int:
        """
        Read Only method
        """
        frame._set_inside_container(self)
        for index, single_element in enumerate(self._unmasked_items()):
            if single_element == frame.frame(single_element):
                return index
        return None

    def _index_from_element(self, element: oe.Element) -> int:
        """
        Read Only method
        """
        for index, single_element in enumerate(self._unmasked_items()):
            if single_element is element:
                return index
        return None

    def _unmasked_items(self) -> list['oe.Element']:
        if self._masked:
            return self._mask_items
        return self._items

    def __getitem__(self, index: int | of.Frame) -> 'oe.Element':
        """
        Read Only method
        """
        if isinstance(index, of.Frame):
            element_index: int = self._index_from_frame(index)
            if element_index is not None:
                return self._unmasked_items()[element_index]
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
                value._set_owner_clip(self) # Makes sure `value` is owned by the Clip
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
            for single_element in self._items:
                single_element._set_owner_clip(self)
        elif isinstance(owner_clip, Clip):
            self._time_signature << owner_clip._time_signature    # Does a parameters copy
            for single_element in self._items:
                single_element._set_owner_clip(owner_clip)
        return self


    def _convert_time_signature_reference(self, time_signature: 'og.TimeSignature') -> Self:
        if isinstance(time_signature, og.TimeSignature):
            for single_element in self:
                single_element._convert_time_signature(self._time_signature)
            if self._length_beats is not None:
                self._length_beats = ra.Length(time_signature, self % od.Pipe( ra.Length() ))._rational
            self._time_signature << time_signature  # Does a copy
        return self


    def _test_owner_clip(self) -> bool:
        for single_element in self._items:
            if single_element._owner_clip is not self:
                return False
        return True


    def _has_elements(self) -> bool:
        if self._items:
            return True
        return False

    def _total_elements(self) -> int:
        return len(self._items)


    def checksum(self) -> str:
        """4-char hex checksum (16-bit) for a Clip, combining Element checksums."""
        master: int = len(self._items)
        for single_element in self._items:
            master += int(single_element.checksum(), 16)   # XOR 16-bit
        return f"{master & 0xFFFF:04x}" # 4 hexadecimal chars sized 16^4 = 65_536


    def masked_element(self, element: oe.Element) -> bool:
        if self.is_masked():
            for single_element in self._mask_items:
                if element is single_element:
                    return False
            return True
        return False


    # Ignores the self Length
    def start(self) -> 'ra.Position':
        """
        Gets the starting position of all its BASE Elements.
        This is the same as the minimum Position of all `Element` positions.

        Args:
            None

        Returns:
            Position: The minimum Position of all Elements.
        """
        if self._has_elements():
            start_beats: Fraction = Fraction(0)
            first_element: oe.Element = self._first_element()
            if first_element is not None:
                start_beats = first_element._position_beats
            return ra.Position(self, start_beats)
        return None

    # Ignores the self Length
    def finish(self) -> 'ra.Position':
        """
        Processes each element Position plus Length and returns the finish position
        as the maximum of all BASE them.

        Args:
            None

        Returns:
            Position: The maximum of Position + Length of all Elements.
        """
        if self._has_elements():
            finish_beats: Fraction = Fraction(0)
            for item in self._items:
                if isinstance(item, oe.Element):
                    single_element: oe.Element = item
                    element_finish: Fraction = \
                        single_element._position_beats + single_element._duration_beats
                    if element_finish > finish_beats:
                        finish_beats = element_finish
            return ra.Position(self, finish_beats)
        return None

    def last_position(self) -> 'ra.Position':
        return self._last_element_position()


    def all_elements(self) -> list[oe.Element]:
        return self._items

    def at_position_elements(self, position: 'ra.Position') -> list[oe.Element]:
        position_beats: Fraction = position._rational
        return [
            single_element for single_element in self.all_elements()
            if single_element._position_beats <= position_beats < single_element._position_beats + single_element._duration_beats
        ] 


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
                    case og.TimeSignature():        return self._time_signature
                    case ou.MidiTrack():            return self._midi_track
                    case _:                 return super().__mod__(operand)
            case og.TimeSignature():        return self._time_signature.copy()
            case ou.MidiTrack():    return self._midi_track.copy()
            case ou.TrackNumber() | od.TrackName() | Devices() | str():
                return self._midi_track % operand
            case og.TimeSignature():
                return self._time_signature.copy()

            case Part():            return Part(self._time_signature, self)
            case Song():            return Song(self._time_signature, self)

            case _:
                return super().__mod__(operand)


    def get_unmasked_element_ids(self) -> set[int]:
        return {id(unmasked_item) for unmasked_item in self._unmasked_items()}

    def get_masked_element_ids(self) -> set[int]:
        if self.is_masked():
            unmasked_ids: set[int] = self.get_unmasked_element_ids()
            return {
                id(masked_item) for masked_item in self._items
                if id(masked_item) not in unmasked_ids
            }
        return set()


    def getPlotlist(self, position_beats: Fraction = None, masked_element_ids: set[int] | None = None) -> list[dict]:
        """
        Returns the plotlist for a given Position.

        Args:
            position: The reference Position where the `Clip` starts at.

        Returns:
            list[dict]: A list with multiple Plot configuration dictionaries.
        """
        if not isinstance(position_beats, Fraction):
            position_beats = Fraction(0, 1)
            og.settings.reset_notes_on()

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
                for single_element in self._items
                    for single_playlist in single_element.getPlotlist(
                        self._midi_track, position_beats, channels, masked_element_ids
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


    def getPlaylist(self, position_beats: Fraction = None) -> list[dict]:
        """
        Returns the playlist for a given Position.

        Args:
            position: The reference Position where the Clip starts at.

        Returns:
            list[dict]: A list with multiple Play configuration dictionaries.
        """
        if not isinstance(position_beats, Fraction):
            position_beats = Fraction(0, 1)
            og.settings.reset_notes_on()
        og.settings.reset_notes_off()

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


    def getMidilist(self, position_beats: Fraction = None) -> list[dict]:
        """
        Returns the midilist for a given Position.

        Args:
            position: The reference Position where the Clip starts at.

        Returns:
            list[dict]: A list with multiple Midi file configuration dictionaries.
        """
        if not isinstance(position_beats, Fraction):
            position_beats = Fraction(0, 1)
            og.settings.reset_notes_on()
        og.settings.reset_notes_off()

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

        serialization["parameters"]["time_signature"]   = self.serialize(self._time_signature)
        serialization["parameters"]["midi_track"]       = self.serialize(self._midi_track)
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
            "time_signature" in serialization["parameters"] and "midi_track" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._time_signature    << self.deserialize(serialization["parameters"]["time_signature"])
            self._midi_track        << self.deserialize(serialization["parameters"]["midi_track"])
            self._set_owner_clip()
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Clip():
                super().__lshift__(operand)
                self._time_signature    << operand._time_signature
                self._midi_track        << operand._midi_track
                self._set_owner_clip()

            case od.Pipe():
                match operand._data:
                    case ou.MidiTrack():
                        self._midi_track = operand._data

                    case og.TimeSignature():
                        self._time_signature = operand._data

                    case list():
                        if all(isinstance(item, oe.Element) for item in operand._data):
                            # Remove previous Elements from the Container stack
                            self._delete(self._unmasked_items(), True) # deletes by id, safer
                            # Finally adds the decomposed elements to the Container stack
                            self._extend(operand._data)
                            self._set_owner_clip()
                        elif all(isinstance(item, og.Locus) for item in operand._data):
                            for single_element, locus in zip(self, operand._data):
                                single_element << locus
                        else:   # Not for me
                            for item in self._unmasked_items():
                                item <<= operand._data

                    case _:
                        super().__lshift__(operand)

            case ra.Length():
                self._length_beats = operand._rational
                if self._length_beats < 0:
                    self._length_beats = None
            case None:
                self._length_beats = None

            case ou.MidiTrack() | ou.TrackNumber() | od.TrackName() | Devices() | od.Device():
                self._midi_track << operand
            case og.TimeSignature():
                self._time_signature << operand  # TimeSignature has no clock!
            # Use Frame objects to bypass this parameter into elements (Setting Position)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )

            case oe.Element():
                self += operand

            case list():
                if all(isinstance(item, oe.Element) for item in operand):
                    # Remove previous Elements from the Container stack
                    self._delete(self._unmasked_items(), True) # deletes by id, safer
                    # Finally adds the decomposed elements to the Container stack
                    self._extend(self.deep_copy(operand))
                    self._set_owner_clip()
                elif all(isinstance(item, og.Locus) for item in operand):
                    for single_element, locus in zip(self, operand):
                        single_element << locus
                else:   # Not for me
                    for item in self._unmasked_items():
                        item << operand
            case dict():
                if all(isinstance(item, oe.Element) for item in operand.values()):
                    for index, item in operand.items():
                        if isinstance(index, int) and index >= 0 and index < len(self._unmasked_items()):
                            self._unmasked_items()[index] = item.copy()
                else:   # Not for me
                    for item in self._unmasked_items():
                        item << operand

            case bool():
                self._masked = operand

            case tuple():
                for single_operand in operand:
                    self << single_operand

            case Composition():
                self._time_signature << operand._time_signature

            case _:
                super().__lshift__(operand)
        return self._sort_items()

    # Works as a Clip transformer
    def __irshift__(self, operand) -> Self:
        match operand:
            case oe.Element():  # Element wapping (wrap)
                for single_element in self._unmasked_items():
                    self._replace(single_element, operand.copy()._set_owner_clip(self) << single_element)
                return self
            
            case list():
                kept_elements: list[oe.Element] = [
                    self[index] for index in operand    # No need to copy
                ]
                return self._delete(self._unmasked_items(), True)._extend(kept_elements)._sort_items()
            
            case str():
                elements_place: list[int] = o.string_to_list(operand)
                kept_elements: list[oe.Element] = []
                for index, placed in enumerate(elements_place):
                    if placed:
                        kept_elements.append(self[index])    # No need to copy
                return self._delete(self._unmasked_items(), True)._extend(kept_elements)._sort_items()
            
        return super().__irshift__(operand)


    # Avoids the costly copy of Track self doing +=
    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Clip():
                operand_copy: Clip = operand.copy()._set_owner_clip(self)
                # Clip preserves the entirety of the operand Clip as is, unmasked
                self._items.extend(operand_copy._items)
                self._mask_items.extend(operand_copy._mask_items)

            case oe.Element():
                new_element: oe.Element = operand.copy()._set_owner_clip(self)
                return self._append(new_element)._sort_items()  # Shall be sorted!
            
            case list():
                if all(isinstance(item, oe.Element) for item in operand):
                    new_elements: list[oe.Element] = [
                        single_element.copy()._set_owner_clip(self)
                        for single_element in operand if isinstance(single_element, oe.Element)
                    ]
                else: # Duplicate and add by index
                    new_elements: list[oe.Element] = [
                        self[index].copy() for index in operand
                    ]
                self._extend(new_elements)
                
            case og.TimeSignature():
                self._time_signature += operand

            case _:
                super().__iadd__(operand)
        return self._sort_items()  # Shall be sorted!

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Clip():
                return self._delete(operand._unmasked_items())
            case oe.Element():
                return self._delete([ operand ])
            case list():
                if all(isinstance(item, oe.Element) for item in operand):
                    return self._delete(operand)
                else: # Remove by index
                    elements_to_delete: list[oe.Element] = [
                        self[index] for index in operand
                    ]
                    return self._delete(elements_to_delete, True)
            
            case str():
                elements_place: list[int] = o.string_to_list(operand)
                elements_to_delete: list[oe.Element] = []
                for index, placed in enumerate(elements_place):
                    if placed:
                        elements_to_delete.append(self[index])    # Shouldn't be copied
                return self._delete(elements_to_delete, True)
            
            case og.TimeSignature():
                self._time_signature -= operand

            case _:
                super().__isub__(operand)
        return self._sort_items()  # Shall be sorted!

    # in-place multiply (NO COPY!)
    def __imul__(self, operand: any) -> Self:
        match operand:
            case Clip():
                # Multiply with `Clip` is applicable to the totality of the self and other Clip and NOT just its the mask
                self_masked: bool = self._masked
                self._masked = False

                operand_copy: Clip = operand.copy()._set_owner_clip(self)   # To be dropped
                operand_copy._masked = False

                operand_position: ra.Position = operand_copy.start()
                if operand_position is not None:

                    self_length: ra.Length = self % ra.Length()
                    operand_position = operand_position.roundMeasures()
                    position_offset: ra.Position = operand_position - self_length
                    operand_copy -= position_offset   # Does a position offset
                    
                    self._items.extend(operand_copy._items)
                    self._mask_items.extend(operand_copy._mask_items)
                    if self._length_beats is not None:
                        self._length_beats += (operand_copy % ra.Length())._rational

                self._masked = self_masked

            case oe.Element():
                self.__imul__(Clip(operand._time_signature, operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Clip = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__imul__(single_shallow_copy)
                elif operand == 0:
                    self._delete()

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
                    og.Segment(self._time_signature, single_segment) for single_segment in operand
                ]
                base_elements: list[oe.Element] = []
                mask_elements: list[oe.Element] = []
                for target_measure, source_segment in enumerate(segments_list):
                    self_segment: Clip = self.copy().filter(source_segment)._set_owner_clip(self)
                    self_segment << ra.Measure(target_measure)   # Stacked by measure *
                    base_elements.extend(self_segment._items)
                    mask_elements.extend(self_segment._mask_items)
                self._items = base_elements
                self._mask_items = mask_elements

            case _:
                super().__imul__(operand)
        return self._sort_items()  # Shall be sorted!

    def __rmul__(self, operand: any) -> Self:
        return self.__mul__(operand)
    
    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case Clip():
                # Only the operand unmasked items are considered
                operand_elements: list[oe.Element] = [
                    element.copy()._set_owner_clip(self) for element in operand
                ]

                if operand_elements:

                    # Division with `Clip` is applicable to the totality of the self Clip and NOT just its the mask
                    self_masked: bool = self._masked
                    self._masked = False

                    left_finish_position: ra.Position = self.finish()
                    if left_finish_position is None:
                        left_finish_position = ra.Position(self)
                    if self._length_beats is not None:
                        self._length_beats += (operand % ra.Length())._rational
                        
                    # operand_elements already sorted by position
                    left_finish_position_beats: Fraction = left_finish_position._rational
                    right_start_position_beats: Fraction = operand_elements[0]._position_beats
                    position_shift: Fraction = left_finish_position_beats - right_start_position_beats
                    for new_element in operand_elements:
                        new_element._position_beats += position_shift
                    self._masked = self_masked
                    self._extend(operand_elements)
                
            case oe.Element():
                self.__itruediv__(Clip(operand._time_signature, operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Clip = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__itruediv__(single_shallow_copy)
                elif operand == 0:
                    self._delete()

            case ra.TimeUnit():
                self_repeating: int = 0
                self_duration: Fraction = self % ra.Duration() % Fraction() # Kept in Beats
                if self_duration > 0:
                    operand_duration: Fraction = operand % ra.Beats(self) % Fraction()  # Converted to Beats
                    self_repeating = int( operand_duration / self_duration )
                self.__itruediv__(self_repeating)

            case list():
                segments_list: list[og.Segment] = [
                    og.Segment(self, single_segment) for single_segment in operand
                ]
                clip_segments: Clip = Clip()
                for single_segment in segments_list:
                    clip_segments /= self.copy().filter(single_segment) # Stacked notes /
                self._delete()
                self /= clip_segments
                self._set_owner_clip()

            case _:
                super().__itruediv__(operand)
        return self._sort_items()  # Shall be sorted!

    def __ifloordiv__(self, operand: any) -> Self:
        match operand:
            case Clip():
                # Preserves the Structure (Locus), Wraps the content (Element)
                for existent_element, new_element in zip(self, operand):
                    element_locus: og.Locus = existent_element % og.Locus()
                    self._replace(existent_element, new_element.copy(element_locus)._set_owner_clip(self))

            case oe.Element():
                # Preserves the Structure (Locus), Wraps the content (Element)
                for existent_element in self:
                    element_locus: og.Locus = existent_element % og.Locus()
                    self._replace(existent_element, operand.copy(element_locus)._set_owner_clip(self))

            case int():
                if operand > 1:
                    single_shallow_copy: Clip = self.shallow_copy()
                    for _ in range(operand - 1):
                        self += single_shallow_copy
                elif operand == 0:   # Must be empty
                    self._delete()
            # Divides the `Duration` by the given `Length` amount as denominator
            case ra.Length() | ra.Duration():
                total_segments: int = operand % int()   # Extracts the original imputed integer
                if total_segments > 1:
                    new_elements: list[oe.Element] = []
                    for first_element in self._unmasked_items():
                        first_element._duration_beats /= total_segments
                        first_element_duration: Fraction = first_element._duration_beats
                        for next_element_i in range(1, total_segments):
                            next_element: oe.Element = first_element.copy() # already with the right duration
                            next_element._position_beats += first_element_duration * next_element_i
                            new_elements.append(next_element)
                    self._extend(new_elements)
            # Divides the `Duration` by sections with the given `TimeValue` (ex.: note value)
            case ra.Duration() | ra.TimeValue():    # Single point split if Duration
                new_elements: list[oe.Element] = []
                for first_element in self._unmasked_items():
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
                self._extend(new_elements)
            
            case ra.Position() | ra.TimeUnit(): # Single point split if Position
                new_elements: list[oe.Element] = []
                for existent_element in self._unmasked_items():
                    existent_start: Fraction = existent_element._position_beats
                    operand_position = ra.Position(self._time_signature, existent_start)
                    # It has to be `<<=` because position must be set at the exactly given TimeUnit regardless its position in the Measure !!
                    operand_position <<= operand
                    split_position: Fraction = operand_position._rational
                    if split_position > existent_start: # Can't split the start
                        existent_finish: Fraction = existent_start + existent_element._duration_beats
                        if split_position < existent_finish:    # Can't split the finish
                            left_duration: Fraction = split_position - existent_start
                            right_duration: Fraction = existent_finish - split_position
                            existent_element._duration_beats = left_duration
                            new_element: oe.Element = existent_element.copy()
                            new_elements.append(new_element)
                            new_element._position_beats = split_position
                            new_element._duration_beats = right_duration
                self._extend(new_elements)

            case list():
                
                if all(isinstance(item, oe.Element) for item in operand):
                    # Preserves the Structure (Locus), Wraps the content (Element)
                    self_base: Clip = self
                    for existent_element, new_element in zip(self_base, operand):
                        element_locus: og.Locus = existent_element % og.Locus()
                        self._replace(existent_element, new_element.copy(element_locus)._set_owner_clip(self_base))

                else:
                    segments_list: list[og.Segment] = [
                        og.Segment(self, single_segment) for single_segment in operand
                    ]
                    base_elements: list[oe.Element] = []
                    mask_elements: list[oe.Element] = []
                    for _, source_segment in enumerate(segments_list):
                        # Preserves masked elements by id in base and mask containers
                        segment_clip: Clip = self.copy().filter(source_segment)
                        segment_clip << ra.Measure(0)   # Side by Side
                        base_elements.extend(segment_clip._items)
                        mask_elements.extend(segment_clip._items)
                    self._delete()
                    self._extend(mask_elements)
                    self._items = base_elements
                    self._set_owner_clip()

            case _:
                super().__ifloordiv__(operand)
        return self._sort_items()  # Shall be sorted!


    def empty_copy(self, *parameters) -> Self:
        """
        Returns a Clip with all the same parameters but the list that is empty.

        Args:
            *parameters: Any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Clip: Returns the copy of self but with an empty list of items.
        """
        new_clip: Clip              = super().empty_copy()
        new_clip._time_signature    << self._time_signature
        new_clip._midi_track        << self._midi_track
        new_clip._length_beats      = self._length_beats
        return new_clip << parameters


    def shallow_copy(self, *parameters) -> Self:
        """
        Returns a Clip with all the same parameters copied, but the list that
        is just a reference of the same list of the original Clip.

        Args:
            *parameters: Any given parameter will be operated with `<<` in the sequence given.

        Returns:
            Clip: Returns the copy of self but with a list of the same items of the original one.
        """
        new_clip: Clip              = super().shallow_copy()
        # It's a shallow copy, so it shares the same TimeSignature and midi track
        new_clip._time_signature    << self._time_signature   
        new_clip._midi_track        << self._midi_track
        new_clip._length_beats      = self._length_beats
        return new_clip << parameters


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
        if self._unmasked_items() and isinstance(parameter_type, type):
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
                    measure_element for measure_element in self._unmasked_items()
                    if measure_element == ra.Measure(single_measure)
                ]
                self._delete(elements_to_remove, True)
                # offsets the right side of it to occupy the dropped measure
                for single_element in self._unmasked_items():
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
            element._position_beats for element in self._unmasked_items()
        ]
        super().sort(parameter, reverse)
        for index, element in enumerate(self._unmasked_items()):
            element._position_beats = original_positions[index]
        return self
    
    def stepper(self, pattern: str = "1... 1... 1... 1...", element: 'oe.Element' = None) -> Self:
        """
        Sets the steps in a Drum Machine for a given `Element`. The default element is `Note()` for None.

        Args:
            pattern (str): A string where the 1s in it set where the triggered steps are.
            element (Element): A element or any respective parameter that sets each element.

        Returns:
            Clip: A clip with the elements placed at the triggered steps.
        """
        if isinstance(pattern, str):

            # Fraction sets the Duration in Steps
            element_element: oe.Note = \
                oe.Note()._set_owner_clip(self) \
                << Fraction(1) << element

            steps_place = o.string_to_list(pattern)

            position_steps: ra.Steps = ra.Steps(0)
            for single_step in steps_place:
                if single_step == 1:
                    self += element_element << position_steps
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
        automation_channels: list[int] = plotlist[0]["channels"]["automation"]

        for channel_0 in automation_channels:

            channel_automation: Clip = automation_clip.mask(ou.Channel(channel_0 + 1))

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
        for single_element in self._unmasked_items():
            
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
        for single_element in self._unmasked_items():
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
        for index, single_element in enumerate(self._unmasked_items()):
            position_duration_dict: dict[str, Fraction] = {
                "duration": single_element._duration_beats
            }
            if index == 0:
                position_duration_dict["position"] = single_element._position_beats
            else:
                position_duration_dict["position"] = \
                    position_duration_beats[0]["position"] + position_duration_beats[0]["duration"]
            position_duration_beats.insert(0, position_duration_dict)   # last one at position 0

        for index, single_element in enumerate(self._unmasked_items()):
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
        
        for item in self._unmasked_items():
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

            for item in self._unmasked_items():
                if isinstance(item, oe.Note):
                    element_pitch: og.Pitch = item._pitch
                    note_pitch: int = element_pitch.pitch_int()
                    new_pitch: int = top_pitch - (note_pitch - bottom_pitch)
                    element_pitch << new_pitch
                
        return self

    def invert(self, by_degree: bool = True) -> Self:
        """
        `invert` is similar to `mirror` but based in a center defined by the first note on which all notes are vertically mirrored.

        Args:
            by_degree (bool): If `True` an inversion by Degree accordingly to the Key Signature, similar to the typical Staff, if False, \
                does a chromatic inversion by pitch like in a piano roll. The default is `True`.

        Returns:
            Clip: The same self object with the items processed.
        """
        if by_degree:
            center_degree_0: ou.Degree = None
            
            for note in self._unmasked_items():
                if isinstance(note, oe.Note):
                    center_degree_0 = note._pitch.absolute_degree_0()
                    break

            for note in self._unmasked_items():
                if isinstance(note, oe.Note):
                    note_degree_0: ou.Degree = note._pitch.absolute_degree_0()
                    degree_distance: ou.Degree = note_degree_0 - center_degree_0
                    # Removes twice, safer than removing 2x
                    note._pitch -= degree_distance  # Recenter position
                    note._pitch -= degree_distance  # Moves in opposite direction

        else:
            center_pitch: int = None
            
            for note in self._unmasked_items():
                if isinstance(note, oe.Note):
                    center_pitch = note._pitch.pitch_int()
                    break

            for note in self._unmasked_items():
                if isinstance(note, oe.Note):
                    note_pitch: int = note._pitch.pitch_int()
                    if note_pitch != center_pitch:
                        note._pitch << 2 * center_pitch - note_pitch
                
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
        self._extend(included_elements)

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


    def fit(self, tie_splitted_notes: bool = True) -> Self:
        """
        Fits all the `Element` items into the respective Measure doing an optional tie if a `Note`.

        Args:
            tie_splitted_notes (bool): Does a tie of all splitted Notes.

        Returns:
            Clip: The same self object with the items processed.
        """
        new_elements: list[oe.Element] = []
        for single_element in self._items:
            rightest_element: oe.Element = single_element
            while rightest_element.start().roundMeasures() + ra.Measure(1) < rightest_element.finish():
                if tie_splitted_notes and isinstance(rightest_element, oe.Note):
                    rightest_element._tied = True
                right_element: oe.Element = rightest_element.copy()
                new_elements.append(right_element)
                measure_end: ra.Position = rightest_element.start().roundMeasures() + ra.Measure(1)
                rightest_element._duration_beats = measure_end._rational - rightest_element._position_beats
                right_element._position_beats = measure_end._rational
                right_element._duration_beats -= rightest_element._duration_beats
                rightest_element = right_element
        return self._extend(new_elements)._sort_items()


    def link(self, ignore_empty_measures: bool = True) -> Self:
        """
        Adjusts the duration/length of each element to connect to the start of the next element.
        For the last element in the clip, this is extended up to the end of the measure.

        Args:
            ignore_empty_measures (bool): Ignores first empty Measures if `True`.

        Returns:
            Clip: The same self object with the items processed.
        """
        if self._items:
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
    
    def quantize(self, amount: float = 1.0, quantize_duration: bool = False) -> Self:
        """
        Quantizes a `Clip` by a given amount from 0.0 to 1.0.

        Args:
            amount (float): The amount of quantization to apply from 0.0 to 1.0.
            quantize_duration (bool): Includes the quantization of the `Duration` too.

        Returns:
            Clip: The same self object with the items processed.
        """
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        amount_rational: Fraction = ra.Amount(amount) % Fraction()
        for single_element in self._unmasked_items():
            # Position On
            element_position_on: Fraction = single_element._position_beats
            unquantized_amount: Fraction = element_position_on % quantization_beats
            quantization_limit: int = round(unquantized_amount / quantization_beats)
            position_on_offset: Fraction = (quantization_limit * quantization_beats - unquantized_amount) * amount_rational
            single_element._position_beats += position_on_offset
            # Position Off
            if quantize_duration:
                element_position_off: Fraction = single_element._position_beats + single_element._duration_beats
                unquantized_amount = element_position_off % quantization_beats
                quantization_limit = round(unquantized_amount / quantization_beats)
                position_off_offset: Fraction = (quantization_limit * quantization_beats - unquantized_amount) * amount_rational
                single_element._duration_beats += position_off_offset
                if single_element._duration_beats == 0:
                    single_element._duration_beats += quantization_beats
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
        for single_element in self._unmasked_items():
            component_elements: list[oe.Element] = single_element.get_component_elements()
            for single_component in component_elements:
                decomposed_elements.append(single_component)
        # Remove previous Elements from the Container stack
        self._delete(self._unmasked_items(), True) # deletes by id, safer
        # Finally adds the decomposed elements to the Container stack
        self._extend(decomposed_elements)
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
        arpeggio.arpeggiate_source(self._unmasked_items(), self.start(), ra.Length( self.net_duration() ))
        return self


    def tie(self) -> Self:
        """
        Adjusts the pitch of successive notes to the previous one and sets all Notes as tied.

        Args:
            None

        Returns:
            Clip: The same self object with the items processed.
        """
        # Only notes can be tied
        tied_notes: list[oe.Note] = [
            single_note << ou.Tied(True)
            for single_note in self._unmasked_items() if isinstance(single_note, oe.Note)
        ]
        notes_position_off: dict[Fraction, og.Pitch] = {
            single_note._position_beats + single_note._duration_beats: single_note._pitch   # Has to be a pitch reference
            for single_note in tied_notes
        }
        for single_note in tied_notes:
            if single_note._position_beats in notes_position_off:
                single_note << notes_position_off[single_note._position_beats]
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
            single_note for single_note in self._unmasked_items() if type(single_note) is oe.Note
        ]
        removed_notes: list[oe.Note] = []
        extended_notes: dict[int, oe.Note] = {}
        for note in all_notes:
            channel_pitch: int = note._channel_0 << 8 | note._pitch.pitch_int()
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
        for item in self._unmasked_items():
            if isinstance(item, oe.Note):
                if last_element is not None:
                    last_element << ra.Gate(gate)
                last_element = item
        return self
    
    def smooth(self, algorithm_type: int = 1) -> Self:
        """
        Adjusts each `Note` octave to have the closest pitch to the first, previous one or both.

        Args:
            algorithm_type (int): Sets the type of algorithm to be used accordingly to the next table:

                +------+---------------------------------------------------------------------------+
                | Type | Description                                                               |
                +------+---------------------------------------------------------------------------+
                | 1    | Considers both pitch distances, from the first note and the previous one. |
                | 2    | Considers only the previous note pitch distance.                          |
                | 3    | Considers only the first note pitch distance.                             |
                +------+---------------------------------------------------------------------------+

        Returns:
            Clip: The same self object with the items processed.
        """
        first_pitch: int | None = None
        previous_pitch: int | None = None
        for note in self._unmasked_items():
            if isinstance(note, oe.Note):    # Only Notes have Pitch
                note_pitch: int = note._pitch.pitch_int()
                if first_pitch is None:
                    previous_pitch = first_pitch = note_pitch
                else:
                    delta_pitch: int = note_pitch
                    if algorithm_type == 3:
                        delta_pitch -= first_pitch
                    else:
                        delta_pitch -= previous_pitch
                    octave_offset: int = delta_pitch // 12
                    remaining_delta: int = delta_pitch % 12
                    if remaining_delta > 6:
                        octave_offset += 1
                    elif remaining_delta < -6:
                        octave_offset -= 1
                    if algorithm_type == 1:
                        expected_pitch: int = note_pitch - octave_offset * 12
                        alternative_pitch: int = expected_pitch
                        if first_pitch > expected_pitch:
                            alternative_pitch += 12
                        else:
                            alternative_pitch -= 12
                        delta_expected_pitch: int = abs(expected_pitch - first_pitch) + abs(expected_pitch - previous_pitch)
                        delta_alternative_pitch: int = abs(alternative_pitch - first_pitch) + abs(alternative_pitch - previous_pitch)
                        if delta_alternative_pitch < delta_expected_pitch:
                            octave_offset -= (alternative_pitch - expected_pitch) // 12
                    note -= ou.Octave(octave_offset)
                    previous_pitch = note_pitch - octave_offset * 12
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



#####################################################################################################
##############################################  PART  ###############################################
#####################################################################################################


class Part(Composition):
    """`Container -> Composition -> Part`

    This type of `Container` aggregates `Clip` items. This type of `Composition` has \
        a `Position` working similarly to `Element` operands.
    A `Part` works similarly like an `Element`, meaning that adding two parts will result \
        in a `Song` as adding two elements result in a `Clip`.

    Parameters
    ----------
    list([]) : A list of `Clip` and `Playlist` type items.
    int : Returns the len of the list.
    Position(0) : It is possible to place a Part on a staff `Position`.
    None, Length : Returns the length of all combined elements.
    """
    def __init__(self, *operands):
        self._position_beats: Fraction  = Fraction(0)   # in Beats
        super().__init__()
        self._time_signature = og.settings._time_signature
        self._items: list[Clip] = []
        self._mask_items: list[Clip] = []
        self._name: str = "Part"

        # Song sets the TimeSignature, this is just a reference
        self._owner_song: Song      = None

        for single_operand in operands:
            self << single_operand


    def _convert_time_signature_reference(self, time_signature: 'og.TimeSignature') -> Self:
        if isinstance(time_signature, og.TimeSignature):
            self._position_beats = ra.Position(time_signature, self % od.Pipe( ra.Position() ))._rational
            if self._length_beats is not None:
                self._length_beats = ra.Length(time_signature, self % od.Pipe( ra.Length() ))._rational
            self._time_signature = time_signature  # Does an assignment
        return self


    def _set_owner_song(self, owner_song: 'Song') -> Self:
        if isinstance(owner_song, Song):
            self._owner_song = owner_song
        return self

    def _get_time_signature(self) -> 'og.TimeSignature':
        if self._owner_song is None:
            return og.settings._time_signature
        return self._owner_song._time_signature


    def _unmasked_items(self) -> list['Clip']:
        if self._masked:
            return self._mask_items
        return self._items


    def __getitem__(self, key: str | int) -> 'Clip':
        if isinstance(key, str):
            for single_item in self._unmasked_items():
                if single_item._midi_track._name == key:
                    return single_item
            return ol.Null()
        return self._unmasked_items()[key]

    def __next__(self) -> 'Clip':
        return super().__next__()
    
    def _sort_items(self) -> Self:
        # Clips aren't sortable
        return self


    def _has_elements(self) -> bool:
        for single_clip in self._items:
            if single_clip._has_elements():
                return True
        return False

    def _total_elements(self) -> int:
        total_elements: int = 0
        for single_clip in self._items:
            total_elements += single_clip._total_elements()
        return total_elements

    def _last_element(self) -> 'oe.Element':
        """
        Returns the `Element` with the last `Position` in the given `Part`.

        Args:
            None

        Returns:
            Element: The last `Element` of all elements in each `Clip`.
        """
        clips_list: list[Clip] = [
            clip for clip in self._unmasked_items() if isinstance(clip, Clip)
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


    def checksum(self) -> str:
        """4-char hex checksum (16-bit) for a Part, combining Clip checksums."""
        master: int = len(self._items)
        for single_clip in self._items:
            master += int(single_clip.checksum(), 16)   # XOR 16-bit
        return f"{master & 0xFFFF:04x}" # 4 hexadecimal chars sized 16^4 = 65_536


    def masked_element(self, element: oe.Element) -> bool:
        if self.is_masked():
            for single_clip in self._unmasked_items():
                for single_element in single_clip._unmasked_items():
                    if single_element is element:
                        return False
            return True
        return False


    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case Part():
                return super().__eq__(other) and self._position_beats == other._position_beats
            case of.Frame():
                for single_clip in self._items:
                    if not single_clip == other:
                        return False
                return True
            case _:
                return super().__eq__(other)

    def __lt__(self, other: 'o.Operand') -> bool:
        match other:
            case Part():
                return self._position_beats < other._position_beats
            case of.Frame():
                for single_clip in self._items:
                    if not single_clip < other:
                        return False
                return True
            case _:
                return self % other < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        match other:
            case Part():
                return self._position_beats > other._position_beats
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

    def last_position(self) -> 'ra.Position':
        position: ra.Position = None
        for clip in self._items:
            clip_position: ra.Position = clip.last_position()
            if clip_position is not None:
                if position is None:
                    position = clip_position
                elif clip_position > position:
                    position = clip_position
        return position


    def all_elements(self) -> list[oe.Element]:
        elements: list[oe.Element] = []
        for single_clip in self._items:
            elements.extend(single_clip.all_elements())
        return elements

    def at_position_elements(self, position: 'ra.Position') -> list[oe.Element]:
        position_beats: Fraction = position._rational - self._position_beats
        if position_beats < 0:
            return []
        return [
            single_element for single_element in self.all_elements()
            if single_element._position_beats <= position_beats < single_element._position_beats + single_element._duration_beats
        ] 


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Position():
                        return operand._data << ra.Position(self, self._position_beats)
                    case str():
                        return self._name
                    case _:
                        return super().__mod__(operand)
            case ra.Position() | ra.TimeValue() | ra.TimeUnit():
                return operand.copy( ra.Position(self._time_signature, self._position_beats) )
            case od.TrackName():
                return operand << self._name
            case str():
                return self._name
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
        for unmasked_clip in self._unmasked_items():
            unmasked_element_ids.update( unmasked_clip.get_unmasked_element_ids() )
        return unmasked_element_ids

    def get_masked_element_ids(self) -> set[int]:
        masked_element_ids: set[int] = set()
        if self.is_masked():
            unmasked_ids: set[int] = self.get_unmasked_element_ids()
            for masked_clip in self._items:
                masked_element_ids.update({
                    id(masked_item) for masked_item in masked_clip._items
                    if id(masked_item) not in unmasked_ids
                })
        return masked_element_ids


    def getPlotlist(self, masked_element_ids: set[int] | None = None, from_song: bool = False) -> list[dict]:
        """
        Returns the plotlist for a given Position.

        Returns:
            list[dict]: A list with multiple Plot configuration dictionaries.
        """
        if not from_song:
            og.settings.reset_notes_on()
        plot_list: list = []
        
        if masked_element_ids is None:
            masked_element_ids = set()
            
        masked_element_ids.update(self.get_masked_element_ids())

        for single_clip in self._items:
            clip_plotlist: list[dict] = single_clip.getPlotlist(self._position_beats, masked_element_ids)
            plot_list.extend( clip_plotlist )
        return plot_list


    def getPlaylist(self, from_song: bool = False) -> list[dict]:
        """
        Returns the playlist for a given Position.

        Args:
            None

        Returns:
            list[dict]: A list with multiple Play configuration dictionaries.
        """
        if not from_song:
            og.settings.reset_notes_on()
        play_list: list = []
        for single_clip in self._items:
            play_list.extend(single_clip.getPlaylist(self._position_beats))
        return play_list

    def getMidilist(self, from_song: bool = False) -> list[dict]:
        """
        Returns the midilist for a given Position.

        Args:
            None

        Returns:
            list[dict]: A list with multiple Midi file configuration dictionaries.
        """
        if not from_song:
            og.settings.reset_notes_on()
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
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Part():
                super().__lshift__(operand)
                # No conversion is done, beat values are directly copied (Same for Element)
                self._position_beats    = operand._position_beats
                self._name              = operand._name
                # Because a Part is also defined by the Owner Song, this also needs to be copied!
                if self._owner_song is None:   # << and copy operation doesn't override ownership
                    self._owner_song    = operand._owner_song
                
            case od.Pipe():
                match operand._data:
                    case ra.Position():
                        self._position_beats = operand._data._rational
                    case str():
                        self._name = operand._data
                    case list():
                        if all(isinstance(item, Clip) for item in operand._data):
                            self._items = [item for item in operand._data]
                        else:   # Not for me
                            for item in self._unmasked_items():
                                item << operand._data
                    case _:
                        super().__lshift__(operand)

            case ra.Position() | ra.TimeValue() | ra.TimeUnit():
                self._position_beats = operand % ra.Position(self) % Fraction()

            case Clip():
                self.__iadd__(operand)

            case oe.Element():
                self += operand

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                if all(isinstance(item, Clip) for item in operand):
                    self._items = [item.copy() for item in operand]
                else:   # Not for me
                    for item in self._unmasked_items():
                        item << operand
            case dict():
                if all(isinstance(item, Clip) for item in operand.values()):
                    for index, item in operand.items():
                        if isinstance(index, int) and index >= 0 and index < len(self._unmasked_items()):
                            self._unmasked_items()[index] = item.copy()
                else:   # Not for me
                    for item in self._unmasked_items():
                        item << operand

            case od.TrackName():
                self._name = operand % str()
            case str():
                self._name = operand

            case _:
                super().__lshift__(operand)
        return self._sort_items()


    def __iadd__(self, operand: any) -> Union['Song', 'Part']:
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Part():
                return Song(self, operand)

            case Clip():
                self._append(operand.copy())

            case oe.Element():
                self._append(Clip(operand._time_signature, operand))

            case ra.Position() | ra.TimeValue() | ra.TimeUnit():
                self << self % ra.Position() + operand
            case list():
                self._extend(self.deep_copy(operand))
            case _:
                super().__iadd__(operand)
        return self._sort_items()  # Shall be sorted!

    def __isub__(self, operand: any) -> Self:
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Clip():
                return self._delete([ operand ])
            case ra.Position() | ra.TimeValue() | ra.TimeUnit():
                self << self % ra.Position() - operand
            case _:
                super().__isub__(operand)
        return self._sort_items()  # Shall be sorted!

    def __imul__(self, operand: any) -> Self:
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Part():
                last_position: ra.Position = self.last_position()
                if last_position is not None:
                    finish_position: ra.Position = self.finish()
                    if finish_position % ra.Measure() >= last_position % ra.Measure() + 1:
                        last_position = ra.Position(finish_position % ra.Measure())
                    finish_length: ra.Length = ra.Length(last_position).roundMeasures()
                    return Song(self._time_signature, self, operand.copy(ra.Position(finish_length)))
                else:
                    return Song(self._time_signature, self, operand)  # Implicit copy

            case Clip():
                last_position: ra.Position = self.last_position()
                if last_position is not None:
                    finish_position: ra.Position = self.finish()
                    if finish_position % ra.Measure() >= last_position % ra.Measure() + 1:
                        last_position = ra.Position(finish_position % ra.Measure())
                    finish_length: ra.Length = ra.Length(last_position).roundMeasures()
                    self._append(operand + ra.Position(finish_length))  # Implicit copy
                else:
                    self._append(operand.copy())    # Explicit copy

            case oe.Element():
                last_position: ra.Position = self.last_position()
                if last_position is not None:
                    finish_position: ra.Position = self.finish()
                    if finish_position % ra.Measure() >= last_position % ra.Measure() + 1:
                        last_position = ra.Position(finish_position % ra.Measure())
                    finish_length: ra.Length = ra.Length(last_position).roundMeasures()
                    self._append(Clip(operand._time_signature, operand + ra.Position(finish_length)))   # Implicit copy
                else:
                    self._append(Clip(operand._time_signature, operand))

            case int():
                new_parts: list[Part] = []
                if operand > 0:
                    last_position: ra.Position = self.last_position()
                    if last_position is not None:
                        finish_position: ra.Position = self.finish()
                        if finish_position % ra.Measure() >= last_position % ra.Measure() + 1:
                            last_position = ra.Position(finish_position % ra.Measure())
                        single_length: ra.Length = ra.Length(last_position).roundMeasures()
                        next_position: ra.Position = self % ra.Position()
                        for _ in range(operand):
                            self_copy: Part = self.copy(next_position)
                            new_parts.append(self_copy)
                            next_position += single_length
                return Song(self._get_time_signature(), od.Pipe(new_parts))._set_owner_song()._sort_items()

            case _:
                super().__imul__(operand)
        return self._sort_items()  # Shall be sorted!

    def __itruediv__(self, operand: any) -> Self:
        # A `Part` is Homologous to an Element, and thus, it processes Frames too
        # Do `Frame**(Frame,)` to do a Frame of a frame, by wrapping a frame in a tuple
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Part():
                finish_position: ra.Position = self.finish()
                if finish_position is not None:
                    return Song(self._time_signature, self, operand.copy(finish_position))
                else:
                    return Song(self._time_signature, self, operand)  # Implicit copy

            case Clip():
                finish_position: ra.Position = self.finish()
                repositioned_clip: Clip = operand + finish_position # Implicit copy
                self._append(repositioned_clip) # No implicit copy

            case oe.Element():
                finish_position: ra.Position = self.finish()
                repositioned_clip: Clip = Clip(operand._time_signature, operand) + finish_position # Implicit copy
                self._append(repositioned_clip) # No implicit copy

            case int():
                if operand > 1:
                    single_shallow_copy: Part = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__itruediv__(single_shallow_copy)
                elif operand == 0:
                    self._delete()
                    
            case _:
                super().__itruediv__(operand)
        return self._sort_items()  # Shall be sorted!

    def __ifloordiv__(self, operand: any) -> Self:
        match operand:
            case Part():
                start_position: ra.Position = self.start()
                if start_position is not None:
                    return Song(self._time_signature, self, operand.copy(start_position))
                else:
                    return Song(self._time_signature, self, operand)  # Implicit copy

            case Clip():
                self._append(operand.copy())

            case oe.Element():
                self._append(Clip(operand._time_signature, operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Part = self.shallow_copy()
                    for _ in range(operand - 1):
                        self += single_shallow_copy
                elif operand == 0:
                    self._delete()

            case _:
                super().__ifloordiv__(operand)
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
        for single_clip in self._unmasked_items():
            single_clip.loop(clip_punch_in, punch_length)

        if self._position_beats < punch_in._rational:
            self._position_beats = Fraction(0) # Positions all parts at the start
        else:
            self._position_beats -= punch_in._rational
        self._length_beats = punch_length._rational

        return self._sort_items()



#####################################################################################################
##############################################  SONG  ###############################################
#####################################################################################################

class Song(Composition):
    """`Container -> Composition -> Song`

    This type of `Container` aggregates only `Part` items. This type
    of `Composition` has a `TimeSignature` working similarly to `Clip` operands, where
    `Clip` contains `Element` items while `Song` contains `Part` ones.

    Parameters
    ----------
    list([]) : A list of `Part` type items.
    int : Returns the len of the list.
    TimeSignature(settings) : It keeps its own Time Signature on which their `Part` items are placed.
    None, Length : Returns the length of all combined elements.
    """
    def __init__(self, *operands):
        super().__init__()
        self._time_signature = og.settings._time_signature.copy()
        self._items: list[Part] = []
        self._mask_items: list[Part] = []
        self._name: str = "Song"
        for single_operand in operands:
            self << single_operand

    def _get_time_signature(self) -> 'og.TimeSignature':
        return self._time_signature


    def _unmasked_items(self) -> list['Part']:
        if self._masked:
            return self._mask_items
        return self._items


    def __getitem__(self, key: int) -> 'Part':
        if isinstance(key, str):
            for single_part in self._unmasked_items():
                if single_part._name == key:
                    return single_part
            return ol.Null()
        return self._unmasked_items()[key]

    def __next__(self) -> 'Part':
        return super().__next__()
    

    def _set_owner_song(self, owner_song: 'Song' = None) -> Self:
        """
        Allows the setting of a distinct `Song` in the contained Elements for a transition process
        with a shallow `Song`.
        """
        if owner_song is None:
            for single_part in self._items:
                single_part._set_owner_song(self)
        elif isinstance(owner_song, Song):
            self._time_signature << owner_song._time_signature    # Does a parameters copy
            for single_part in self._items:
                single_part._set_owner_song(owner_song)
        return self


    def _convert_time_signature_reference(self, time_signature: 'og.TimeSignature') -> Self:
        if isinstance(time_signature, og.TimeSignature):
            for single_part in self:
                single_part._convert_time_signature_reference(self._time_signature)
            if self._length_beats is not None:
                self._length_beats = ra.Length(time_signature, self % od.Pipe( ra.Length() ))._rational
            self._time_signature << time_signature  # Does a copy
        return self


    def _test_owner_song(self) -> bool:
        for single_part in self:
            if single_part._owner_song is not self:
                return False
        return True


    def _has_elements(self) -> bool:
        for single_part in self._items:
            if single_part._has_elements():
                return True
        return False

    def _total_elements(self) -> int:
        total_elements: int = 0
        for single_part in self._items:
            total_elements += single_part._total_elements()
        return total_elements

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


    def checksum(self) -> str:
        """4-char hex checksum (16-bit) for a Song, combining Part checksums."""
        master: int = len(self._items)
        for single_part in self._items:
            master += int(single_part.checksum(), 16)   # XOR 16-bit
        return f"{master & 0xFFFF:04x}" # 4 hexadecimal chars sized 16^4 = 65_536


    def masked_element(self, element: oe.Element) -> bool:
        if self.is_masked():
            for single_part in self._unmasked_items():
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

    def last_position(self) -> 'ra.Position':
        position: ra.Position = None
        for part in self._items:
            part_position: ra.Position = part.last_position()
            if part_position is not None:
                if position is None:
                    position = part_position
                elif part_position > position:
                    position = part_position
        return position


    def all_elements(self) -> list[oe.Element]:
        elements: list[oe.Element] = []
        for single_part in self._items:
            elements.extend(single_part.all_elements())
        return elements

    def at_position_elements(self, position: 'ra.Position') -> list[oe.Element]:
        elements: list[oe.Element] = []
        for single_part in self._items:
            elements.extend( single_part.at_position_elements(position) )
        return elements


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case og.TimeSignature():        return self._time_signature
                    case str():                     return self._name
                    case _:                         return super().__mod__(operand)
            case og.TimeSignature():
                return self._time_signature.copy()
            case od.TrackName():
                return operand << self._name
            case str():
                return self._name
            case od.Names():
                all_names: list[str] = []
                for single_part in self._unmasked_items():
                    all_names.append(single_part._name)
                return od.Names(*tuple(all_names))
            case _:
                return super().__mod__(operand)


    def get_unmasked_element_ids(self) -> set[int]:
        unmasked_element_ids: set[int] = set()
        for unmasked_part in self._unmasked_items():   # Here self._items is unmasked
            unmasked_element_ids.update( unmasked_part.get_unmasked_element_ids() )
        return unmasked_element_ids

    def get_masked_element_ids(self) -> set[int]:
        masked_element_ids: set[int] = set()
        if self.is_masked():
            unmasked_ids: set[int] = self.get_unmasked_element_ids()
            for masked_part in self._items:
                for masked_clip in masked_part._items:
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
        og.settings.reset_notes_on()
        plot_list: list = []
        masked_element_ids: set[int] = self.get_masked_element_ids()
        
        for single_part in self._items:
            part_plotlist: list[dict] = single_part.getPlotlist(masked_element_ids, True)
            # Part uses the Song Time Signature as Elements use the Clip Time Signature, so, no need for conversions
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
        og.settings.reset_notes_on()
        play_list: list = []
        for single_part in self._items:
            play_list.extend(single_part.getPlaylist(True))
        return play_list

    def getMidilist(self) -> list[dict]:
        """
        Returns the midilist for a given Position.

        Args:
            None

        Returns:
            list[dict]: A list with multiple Midi file configuration dictionaries.
        """
        og.settings.reset_notes_on()
        midi_list: list = []
        for single_part in self:
            midi_list.extend(single_part.getMidilist(True))
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

        serialization["parameters"]["time_signature"] = self.serialize(self._time_signature)
        serialization["parameters"]["name"] = self.serialize(self._name)
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
            "time_signature" in serialization["parameters"] and "name" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._time_signature << self.deserialize(serialization["parameters"]["time_signature"])
            self._name = self.deserialize(serialization["parameters"]["name"])
            self._set_owner_song()
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Song():
                super().__lshift__(operand)
                self._time_signature << operand._time_signature
                self._name = operand._name
                self._set_owner_song()

            case od.Pipe():
                match operand._data:
                    case og.TimeSignature():
                        self._time_signature = operand._data
                    case list():
                        if all(isinstance(item, Part) for item in operand._data):
                            self._items = [item for item in operand._data]
                            self._set_owner_song()
                        else:   # Not for me
                            for item in self._unmasked_items():
                                item << operand._data
                    case str():
                        self._name = operand._data
                    case _:
                        super().__lshift__(operand)

            case Part() | Clip() | oe.Element():
                self += operand

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case og.TimeSignature():
                self._time_signature << operand
            case list():
                if all(isinstance(item, Part) for item in operand):
                    self._items = [item.copy() for item in operand]
                    self._set_owner_song()
                else:   # Not for me
                    for item in self._unmasked_items():
                        item << operand
            case dict():
                if all(isinstance(item, Part) for item in operand.values()):
                    for index, item in operand.items():
                        if isinstance(index, int) and index >= 0 and index < len(self._unmasked_items()):
                            self._unmasked_items()[index] = item.copy()
                else:   # Not for me
                    for item in self._unmasked_items():
                        item << operand

            case od.TrackName():
                self._name = operand % str()
            case str():
                self._name = operand

            case _:
                super().__lshift__(operand)
        return self._sort_items()


    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Song():
                for single_part in operand:
                    self += single_part

            case Part():
                self._append(Part(operand)._set_owner_song(self))._sort_items()

            case Clip():
                self += Part(operand)

            case oe.Element():
                self += Clip(operand._time_signature, operand)

            case list():
                for item in operand:
                    if isinstance(item, Part):
                        self._append(item.copy()._set_owner_song(self))
            case _:
                super().__iadd__(operand)
        return self._sort_items()  # Shall be sorted!


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
            case _:
                super().__isub__(operand)
        return self._sort_items()


    def __imul__(self, operand: any) -> Self:
        match operand:
            case Song():
                right_song: Song = Song(operand)._set_owner_song(self)

                left_length: ra.Length = self % ra.Length()
                position_offset: ra.Position = ra.Position(left_length)

                for single_part in right_song:
                    single_part += position_offset

                self._extend(right_song._items)
                
                if self._length_beats is not None:
                    self._length_beats += (right_song % ra.Length())._rational

            case Part():
                self.__imul__(Song(operand))

            case Clip():
                self.__imul__(Part(operand))

            case oe.Element():
                self.__imul__(Clip(operand._time_signature, operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Song = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__imul__(single_shallow_copy)
                elif operand == 0:
                    self._delete()
                
            case _:
                super().__imul__(operand)
        return self._sort_items()


    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case Song():
                right_song: Song = Song(operand)._set_owner_song(self)

                left_length: ra.Length = self % ra.Duration() % ra.Length()
                position_offset: ra.Position = ra.Position(left_length.roundMeasures())

                for single_part in right_song:
                    single_part += position_offset

                self._extend(right_song._items)  # Propagates upwards in the stack
                
                if self._length_beats is not None:
                    self._length_beats += (right_song % ra.Duration() % ra.Length())._rational

            case Part():
                self.__itruediv__(Song(operand))

            case Clip():
                self.__itruediv__(Part(operand))

            case oe.Element():
                self.__itruediv__(Clip(operand._time_signature, operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Part = self.shallow_copy()
                    for _ in range(operand - 1):
                        self.__itruediv__(single_shallow_copy)
                elif operand == 0:
                    self._delete()
                    
            case _:
                super().__itruediv__(operand)
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
                self.__ifloordiv__(Clip(operand._time_signature, operand))

            case int():
                if operand > 1:
                    single_shallow_copy: Song = self.shallow_copy()
                    for _ in range(operand - 1):
                        self += single_shallow_copy
                elif operand == 0:
                    self._delete()

            case _:
                super().__ifloordiv__(operand)
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
        for part_loop in self._unmasked_items():
            part_loop.loop(position, punch_length)

        self._length_beats = punch_length._rational

        return self._sort_items()


