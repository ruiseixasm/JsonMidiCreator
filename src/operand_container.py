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

    def __iter__(self):
        return self
    
    def __next__(self):
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
                if single_item is after_item:
                    append_at = index + 1   # After the item
                    break
        self._items = self._items[:append_at] + items + self._items[append_at:]
        return self

    def _delete(self, items: list) -> Self:
        if self is not self._upper_container:
            self._upper_container._delete(items)
        self._items = [
            single_item for single_item in self._items if single_item not in items
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
        # Only applicable to Clip
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
            case ou.Next():
                self._index += operand % int() - 1
                item: any = self._items[self._index % len(self._items)]
                self._index += 1
                self._index %= len(self._items)
                return item
            case ou.Previous():
                self._index -= operand % int()
                self._index %= len(self._items)
                item: any = self._items[self._index]
                return item
            case _:
                return super().__mod__(operand)

    def len(self) -> int:
        return len(self._items)

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
            case _: # Works for Frame too
                for item in self._items:
                    item << operand
        return self

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
    
    def sort(self, parameter: type = ra.Position) -> Self:
        """
        Sorts the self list based on a given type of parameter.

        Args:
            parameter (type): The type of parameter being sorted by.

        Returns:
            Container: The same self object with the items processed.
        """
        compare = parameter()
        self._items.sort(key=lambda x: x % compare)
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

    def filter(self, mask: any, shallow_copy: bool = True) -> Self:
        """
        Filters out all items that don't met the mask (equal to).

        Args:
            parameter (any): The object to be compared with (==).

        Returns:
            Container: The same self object with the items processed.
        """
        if shallow_copy:
            shallow_copy: Container = self.shallow_copy()
            shallow_copy._items = [item for item in self._items if item == mask]
            return shallow_copy
        self._items = [item for item in self._items if item == mask]
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


    def __add__(self, operand: any) -> Self:
        return self.copy().__iadd__(operand)
    
    def __sub__(self, operand: any) -> Self:
        return self.copy().__isub__(operand)
    
    def __mul__(self, operand: any) -> Self:
        return self.copy().__imul__(operand)
    
    def __truediv__(self, operand: any) -> Self:
        return self.copy().__itruediv__(operand)
    
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
                if self.len() > 0:
                    self_last_item: any = self[-1]
                    return self._append([ self.deep_copy(operand) ], self_last_item)
                return self._append([ self.deep_copy(operand) ])
        return self

    def __radd__(self, operand: any) -> Self:
        self_copy: Container = self.copy()
        self_copy._items.insert(0, self.deep_copy( operand ))
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
            case tuple():
                for single_operand in operand:
                    self *= single_operand
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
            case ch.Chaos():
                return self.shuffle(operand)
            
            case tuple():
                for single_operand in operand:
                    self /= single_operand
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
                self.filter(operand, False)
        return self

    def __ror__(self, operand: any) -> Self:
        return self.__or__(operand)



class Clip(Container):  # Just a container of Elements
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
        self._position_beats: Fraction  = Fraction(0)   # in Beats
        self._length_beats: Fraction    = Fraction(-1)  # in Beats where -1 means isn't set
        self._items: list[oe.Element] = []
        for single_operand in operands:
            self << single_operand


    def __getitem__(self, index: int) -> oe.Element:
        return self._items[index]

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
            self._staff << staff_reference
        for single_element in self:
            if isinstance(single_element, oe.Element):
                single_element.set_staff_reference(self._staff)
        return self

    def get_staff_reference(self) -> 'og.Staff':
        return self._staff

    def reset_staff_reference(self) -> Self:
        self._staff = og.defaults._staff.copy()
        for single_element in self:
            if isinstance(single_element, oe.Element):
                single_element.set_staff_reference(self._staff)
        return self

    def test_staff_reference(self) -> bool:
        clip_staff_id: int = id(self._staff)
        for single_element in self:
            if isinstance(single_element, oe.Element):
                element_staff_id: int = id( single_element._staff_reference )
                if element_staff_id != clip_staff_id:
                    return False
        return True


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
                    case ra.Position():
                        return operand._data << self._staff.convertToPosition(ra.Beats(self._position_beats))
                    case ra.Measurement():
                        return operand._data << self._staff.convertToLength(ra.Beats(self._length_beats))
                    case _:                 return super().__mod__(operand)
            case og.Staff():        return self._staff.copy()
            case ou.MidiTrack():    return self._midi_track.copy()
            case ou.TrackNumber() | od.TrackName() | str():
                return self._midi_track % operand
            case ra.Position():
                return operand.copy() << self._staff.convertToPosition(ra.Beats(self._position_beats))
            case ra.Length():
                if self._length_beats >= 0:
                    return operand.copy() << self._staff.convertToLength(ra.Beats(self._length_beats))
                return self.length()
            case ra.Duration():     return self.duration()
            case ra.StaffParameter() | ou.KeySignature() | ou.Accidentals() | ou.Major() | ou.Minor() | og.Scale() | ra.Measures() | ou.Measure() \
                | float() | Fraction():
                                    return self._staff % operand
            case _:                 return super().__mod__(operand)

    #######################################################################
    # Conversion (Simple, One-way) | Only destination Staff is considered #
    #######################################################################

    def convertToBeats(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Beats':
        return self._staff.convertToBeats(time)

    def convertToMeasures(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Measures':
        return self._staff.convertToMeasures(time)
        
    def convertToSteps(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Steps':
        return self._staff.convertToSteps(time)

    def convertToDuration(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Duration':
        return self._staff.convertToDuration(time)

    def convertToMeasure(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Measure':
        return self._staff.convertToMeasure(time)

    def convertToBeat(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Beat':
        return self._staff.convertToBeat(time)

    def convertToStep(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Step':
        return self._staff.convertToStep(time)

    def convertToLength(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Length':
        return self._staff.convertToLength(time)

    def convertToPosition(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Position':
        return self._staff.convertToPosition(time)

    ################################################################################################################
    # Transformation (Two-way, Context-Dependent) | Both Staffs are considered, the source and the destination one #
    ################################################################################################################

    def transformBeats(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Beats':
        return self._staff.transformBeats(time)

    def transformMeasures(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Measures':
        return self._staff.transformMeasures(time)

    def transformSteps(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Steps':
        return self._staff.transformSteps(time)

    def transformDuration(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Duration':
        return self._staff.transformDuration(time)

    def transformMeasure(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Measure':
        return self._staff.transformMeasure(time)

    def transformBeat(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Beat':
        return self._staff.transformBeat(time)

    def transformStep(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Step':
        return self._staff.transformStep(time)

    def transformLength(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Length':
        return self._staff.transformLength(time)

    def transformPosition(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Position':
        return self._staff.transformPosition(time)


    def first(self) -> oe.Element:
        """
        Gets the first Element accordingly to it's Position on the Staff.

        Args:
            None

        Returns:
            Element: The first Element of all Elements.
        """
        first_element: oe.Element = None
        if self.len() > 0:
            first_element = self._items[0]
            for element in self._items:
                if element % ra.Position() < first_element % ra.Position():
                    first_element = element
        return first_element

    def last(self) -> oe.Element:
        """
        Gets the last Element accordingly to it's Position on the Staff.

        Args:
            None

        Returns:
            Element: The last Element of all Elements.
        """
        last_element: oe.Element = None
        if self.len() > 0:
            last_element = self._items[0]
            for element in self._items:
                # With not < instead of just > allows the return of latter elements in the list
                if not element % ra.Position() < last_element % ra.Position():
                    last_element = element
        return last_element

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
        start_beats: Fraction = None
        for item in self._items:
            position_beats: Fraction = item._position_beats
            if start_beats is None or position_beats < start_beats:
                start_beats = position_beats
        if start_beats is not None:
            return self._staff.convertToPosition(ra.Beats(start_beats))
        return self._staff.convertToPosition(0)

    def finish(self) -> ra.Position:
        """
        Processes each element Position plus Length and returns the finish position
        as the maximum of all of them.

        Args:
            None

        Returns:
            Position: The maximum of Position + Length of all Elements.
        """
        finish_beats: Fraction = Fraction(0)
        for item in self._items:
            if isinstance(item, oe.Element):
                single_element: oe.Element = item
                element_finish: Fraction = single_element._position_beats \
                    + (single_element % ra.Length())._rational
                if element_finish > finish_beats:
                    finish_beats = element_finish
        return self._staff.convertToPosition(ra.Beats(finish_beats))


    def length(self) -> ra.Length:
        """
        Reruns the length that goes from the start to finish of all elements.

        Args:
            None

        Returns:
            Length: Equal to Clip finish() - start().
        """
        return ra.Length( self.finish() - self.start() )

    def duration(self) -> ra.Duration:
        """
        Reruns the length wrapped as Duration.

        Args:
            None

        Returns:
            Duration: Equal to length() but returning Duration.
        """
        return self.length().convertToDuration()


    if TYPE_CHECKING:
        from operand_element import Element

    def get_clip_elements(self) -> list['Element']: # Helper method
        
        # Needs to be reset because shallow_copy doesn't result in different
        # staff references for each element
        self._staff.reset_accidentals()
        self._staff.reset_tied_note()

        return [
                element for element in self.shallow_copy()._sort_position()._items 
                if isinstance(element, oe.Element)
            ]

    def getPlaylist(self, position_beats: Fraction = None, staff: og.Staff = None) -> list[dict]:

        clip_position_beats: Fraction = self._position_beats

        if isinstance(staff, og.Staff):
            clip_position_beats = staff.transformBeats(self._staff.convertToBeats(ra.Beats(clip_position_beats)))._rational

        if isinstance(position_beats, Fraction):
            clip_position_beats += position_beats

        return [
            single_playlist
                for single_element in self.get_clip_elements()
                for single_playlist in single_element.getPlaylist(clip_position_beats)
        ]

    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, staff: og.Staff = None) -> list[dict]:
        midi_track: ou.MidiTrack = self._midi_track if not isinstance(midi_track, ou.MidiTrack) else midi_track
        clip_position_beats: Fraction = self._position_beats

        if isinstance(staff, og.Staff):
            clip_position_beats = staff.transformBeats(self._staff.convertToBeats(ra.Beats(clip_position_beats)))._rational

        if isinstance(position_beats, Fraction):
            clip_position_beats += position_beats

        return [
            single_midilist
                for single_element in self.get_clip_elements()
                for single_midilist in single_element.getMidilist(midi_track, clip_position_beats)
        ]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["staff"]        = self.serialize(self._staff)
        serialization["parameters"]["midi_track"]   = self.serialize(self._midi_track)
        serialization["parameters"]["position"]     = self.serialize(self._position_beats)
        serialization["parameters"]["length"]       = self.serialize(self._length_beats)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"] and "midi_track" in serialization["parameters"]
            and "position" in serialization["parameters"] and "length" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._staff             = self.deserialize(serialization["parameters"]["staff"])
            self._midi_track        = self.deserialize(serialization["parameters"]["midi_track"])
            self._position_beats    = self.deserialize(serialization["parameters"]["position"])
            self._length_beats      = self.deserialize(serialization["parameters"]["length"])
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_mutation as om
        match operand:
            case Clip():
                self._midi_track        << operand._midi_track
                self._position_beats    = operand._position_beats
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
                    case ra.Position():     self._position_beats = self._staff.convertToBeats(operand._data)._rational
                    case ra.Length():       self._length_beats = self._staff.convertToBeats(operand._data)._rational
                    case om.Mutation():     operand._data.mutate(self)
                    case _:
                        super().__lshift__(operand)
                        self._items = o.filter_list(self._items, lambda item: isinstance(item, oe.Element))

            case ou.MidiTrack() | ou.TrackNumber() | od.TrackName():
                self._midi_track << operand
            case og.Staff() | ou.KeySignature() | og.TimeSignature() | ra.StaffParameter() | ou.Accidentals() | ou.Major() | ou.Minor():
                self._staff << operand
            # Use Frame objects to bypass this parameter into elements (Setting Position)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._items = [
                    item.copy() for item in operand if isinstance(item, oe.Element)
                ]
            case om.Mutation():
                operand.copy().mutate(self)
            
            case od.ClipParameter():
                operand._data = self & operand._data    # Processes the tailed self operands or the Frame operand if any exists
                match operand._data:
                    case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                        self._position_beats = self._staff.convertToBeats(operand._data)._rational
                    case ra.Length() | ra.Duration():
                        self._length_beats = self._staff.convertToBeats(operand._data)._rational
                    case ou.MidiTrack() | ou.TrackNumber() | od.TrackName() | str():
                        self._midi_track << operand._data
                    case og.Staff() | ou.KeySignature() | og.TimeSignature() | ra.StaffParameter() | ou.Accidentals() | ou.Major() | ou.Minor() \
                            | og.Scale() | ra.Measures() | ou.Measure() | int() | float() | Fraction():
                        self._staff << operand._data
                    case None:
                        self._length_beats = Fraction(-1)

            case tuple():
                for single_operand in operand:
                    self << single_operand

            case _: # Works for Frame too
                for item in self._items:
                    item << operand
        return self

    def empty_copy(self, *parameters) -> Self:
        empty_copy: Clip                = super().empty_copy()
        empty_copy._staff               << self._staff
        empty_copy._midi_track          << self._midi_track
        empty_copy._position_beats      = self._position_beats
        empty_copy._length_beats        = self._length_beats
        for single_parameter in parameters:
            empty_copy << single_parameter
        return empty_copy
    
    def shallow_copy(self, *parameters) -> Self:
        shallow_copy: Clip              = super().shallow_copy()
        # It's a shallow copy, so it shares the same Staff and midi track
        shallow_copy._staff             = self._staff   
        shallow_copy._midi_track        = self._midi_track
        shallow_copy._position_beats    = self._position_beats
        shallow_copy._length_beats      = self._length_beats
        for single_parameter in parameters:
            shallow_copy << single_parameter
        return shallow_copy
    
    
    # operand is the pusher >> (NO COPIES!)
    def __rrshift__(self, operand: o.T) -> Union[o.T, 'Part']:
        import operand_mutation as om
        match operand:
            case Part():
                wrapper_part: Part = Part()
                wrapper_part._items = [
                    data_clip for data_clip in operand._items
                ]
                wrapper_part._items.append( self )
                return wrapper_part
            case Clip():
                wrapper_part: Part = Part()
                wrapper_part._items = [ operand, self ]
                return wrapper_part
            case oe.Element():
                # Give space to Element
                add_position: ra.Position = \
                    self._staff.convertToPosition( operand % ra.Position() ) + self._staff.convertToPosition( operand % ra.Duration() )
                self += add_position  # No copy!
                self._items.insert(0, operand.copy().set_staff_reference(self._staff))
            case ra.Position():
                self._position_beats = self._staff.convertToBeats(operand)._rational
            case ra.Length() | ra.TimeValue() | ra.Duration() | ou.TimeUnit():
                self._position_beats += self._staff.convertToBeats(operand)._rational
            case om.Mutation():
                return operand.mutate(self)
            case od.Playlist():
                return operand >> od.Playlist(self.getPlaylist(self._position_beats))
            case _:
                return super().__rrshift__(operand)
        return operand


    # Avoids the costly copy of Track self doing +=
    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Part():
                # Song at the right must be a copy
                new_song: Part = operand.copy()
                # Inserts self content at the beginning of the Song
                new_song._items.insert(0, self)
                return new_song # Operand Song replaces self Clip
            case Clip():
                operand_elements = [
                    single_element.copy().set_staff_reference(self._staff) for single_element in operand._items
                ]
                if self.len() > 0:
                    self_last_element: oe.Element = self[-1]
                    return self._append(operand_elements, self_last_element)._sort_position()  # Shall be sorted!
                return self._append(operand_elements)._sort_position() # Shall be sorted!
            case oe.Element():
                new_element: oe.Element = operand.copy().set_staff_reference(self._staff)
                if self.len() > 0:
                    self_last_element: oe.Element = self[-1]
                    return self._append([ new_element ], self_last_element)._sort_position()  # Shall be sorted!
                return self._append([ new_element ])._sort_position()  # Shall be sorted!
            case list():
                operand_elements = [
                    single_element.copy().set_staff_reference(self._staff) for single_element in operand if isinstance(single_element, oe.Element)
                ]
                if self.len() > 0:
                    self_last_element: oe.Element = self[-1]
                    return self._append(operand_elements, self_last_element)
                return self._append(operand_elements)
                        
            case od.ClipParameter():
                operand._data = self & operand._data    # Processes the tailed self operands or the Frame operand if any exists
                match operand._data:
                    case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                        self._position_beats += self._staff.convertToBeats(operand)._rational

            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                for item in self._items:
                    item += operand
        return self._sort_position()  # Shall be sorted!

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Clip():
                return self._delete(operand._items)
            case Part():
                operand -= self # Order is irrelevant in Song
                return operand
            case oe.Element():
                return self._delete([ operand ])
            case list():
                operand_elements = [
                    single_element for single_element in operand if isinstance(single_element, oe.Element)
                ]
                return self._delete(operand_elements)
            
            case od.ClipParameter():
                operand._data = self & operand._data    # Processes the tailed self operands or the Frame operand if any exists
                match operand._data:
                    case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                        self._position_beats -= self._staff.convertToBeats(operand)._rational

            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case _:
                for item in self._items:
                    item -= operand
        return self._sort_position()  # Shall be sorted!

    # in-place multiply (NO COPY!)
    def __imul__(self, operand: any) -> Self:
        import operand_selection as os
        match operand:
            case Clip():
                right_start_position: ra.Position = operand.start()
                if self._length_beats < 0:
                    # It's the position of the element that matters and not their tailed Duration
                    last_element: oe.Element = self.last()
                    if last_element:
                        left_end_position: ra.Position = last_element % ra.Position()
                        add_position: ra.Position = left_end_position.roundMeasures() + ou.Measure(1)
                    else:
                        add_position: ra.Position = ra.Position(0)
                else:
                    left_end_position: ra.Position = self._staff.convertToPosition(ra.Beats(self._length_beats))
                    self._length_beats += (operand % ra.Length())._rational
                    add_position: ra.Position = left_end_position - right_start_position
                operand_elements = [
                    (single_data + add_position).set_staff_reference(self._staff) for single_data in operand._items
                        if isinstance(single_data, oe.Element)
                ]
                self._items.extend( single_element for single_element in operand_elements )
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
                        single_element.set_staff_reference(self._staff) for single_element in self_copy
                        if isinstance(single_element, oe.Element)
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
            case oe.Element():
                next_position: ra.Position = self.finish()
                self._items.append(
                    operand.copy().set_staff_reference(self._staff) << next_position
                )
            case od.ClipParameter():
                operand._data = self & operand._data    # Processes the tailed self operands or the Frame operand if any exists
                match operand._data:
                    case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                        self._position_beats *= self._staff.convertToBeats(operand)._rational
            case os.Selection():
                if operand != self:
                    self._items = []

            case tuple():
                for single_operand in operand:
                    self *= single_operand
            case _:
                for item in self._items:
                    item *= operand
        return self._sort_position()  # Shall be sorted!

    def __rmul__(self, operand: any) -> Self:
        return self.__mul__(operand)
    
    def __itruediv__(self, operand: any) -> Self:
        import operand_mutation as om
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
                    (single_data + add_position).set_staff_reference(self._staff) for single_data in operand._items
                        if isinstance(single_data, oe.Element)
                ]
                self._items.extend( single_element for single_element in operand_elements )

            case int():
                if operand > 1:
                    add_position: ra.Position = ra.Position(self.length())
                    self_copy: Clip = self.copy()
                    for _ in range(operand - 2):
                        self_copy += add_position
                        self += self_copy   # implicit copy of self_copy
                    # Uses the last self_copy for the last iteration
                    self_copy += add_position
                    self._items.extend(
                        single_element.set_staff_reference(self._staff) for single_element in self_copy
                        if isinstance(single_element, oe.Element)
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

            case od.ClipParameter():
                operand._data = self & operand._data    # Processes the tailed self operands or the Frame operand if any exists
                match operand._data:
                    case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                        self._position_beats /= self._staff.convertToBeats(operand)._rational

            # Returns an altered Clip with less info (truncated info)
            case od.Getter() | od.Process():
                return self >> operand

            case ch.Chaos():
                return self.shuffle(operand)
            case om.Mutation():
                return operand.copy().mutate(self)

            case tuple():
                for single_operand in operand:
                    self /= single_operand
            case _:
                for item in self._items:
                    item /= operand
        return self._sort_position()  # Shall be sorted!

    
    def sort(self, parameter: type = ra.Position) -> Self:
        """
        Sorts the self list based on a given type of parameter.

        Args:
            parameter (type): The type of parameter being sorted by.

        Returns:
            Container: The same self object with the items processed.
        """
        if parameter is not ra.Position:    # By default Clip is sorted by Position
            original_positions: list[Fraction] = [
                element._position_beats for element in self._items
            ]
            super().sort(parameter)
            for index, element in enumerate(self._items):
                element._position_beats = original_positions[index]
        return self

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
                rest_element: oe.Rest = oe.Rest().set_staff_reference(self._staff) << rest_length
                self += rest_element
        
        last_element: oe.Element = shallow_copy[shallow_copy_len - 1]
        staff_end: ra.Position = last_element.finish().convertToLength().roundMeasures().convertToPosition()
        if last_element.finish() < staff_end:
            rest_length: ra.Length = ra.Length( staff_end - last_element.finish() )
            rest_element: oe.Rest = oe.Rest().set_staff_reference(self._staff) << rest_length
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
        
        return self
    
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


class Part(Container):
    def __init__(self, *operands):
        super().__init__()
        self._items: list[Clip | od.Playlist] = []
        self._staff: og.Staff = None
        for single_operand in operands:
            self << single_operand

    def __getitem__(self, key: str | int) -> Clip:
        if isinstance(key, str):
            for single_clip in self:
                if isinstance(single_clip, Clip):   # Playlists aren't selectable by name !
                    if single_clip._midi_track._name == key:
                        return single_clip
            return ol.Null()
        return self._items[key]

    def _sort_position(self) -> Self:
        if self is not self._upper_container:
            self._upper_container._sort_position()
        self._items.sort(key=lambda x: x % ra.Position() // Fraction())
        return self


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> Self:
        if isinstance(staff_reference, og.Staff):
            self._staff = staff_reference.copy()
        elif staff_reference is None:
            self._staff = og.defaults._staff.copy()
        return self

    def get_staff_reference(self) -> og.Staff:
        return self._staff

    def reset_staff_reference(self) -> Self:
        self._staff = None
        return self

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case og.Staff():        return self._staff
            case ou.MidiTrack():
                for single_clip in self:
                    if isinstance(single_clip, Clip):
                        if single_clip._midi_track == operand:
                            return single_clip
                return ol.Null()
            case str():             return self[operand]
            case og.Staff():        return self.deep_copy(self._staff)
            case _:                 return super().__mod__(operand)

    def getPlaylist(self, position: ra.Position = None, staff: og.Staff = None) -> list:
        play_list: list = []
        if staff is None:
            staff = self._staff
        for single_clip in self:
            if isinstance(single_clip, (Clip, od.Playlist)):
                play_list.extend(single_clip.getPlaylist(position, staff))
        return play_list

    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None, staff: og.Staff = None) -> list:
        midi_list: list = []
        if staff is None:
            staff = self._staff
        for single_clip in self:
            if isinstance(single_clip, Clip):   # Can't get Midilist from Playlist !
                midi_list.extend(single_clip.getMidilist(midi_track, position, staff))
        return midi_list

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["staff"]        = self.serialize(self._staff)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._staff             = self.deserialize(serialization["parameters"]["staff"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Part():
                super().__lshift__(operand)
            case Clip():
                self._items.append( operand.copy() )
            case og.Staff() | ou.KeySignature() | og.TimeSignature() | ra.StaffParameter() | ou.Accidentals() | ou.Major() | ou.Minor():
                if isinstance(self._staff, og.Staff):
                    self._staff << operand
            case None:
                self._staff = None
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._items = [
                    self.deep_copy(item) for item in operand if isinstance(item, (Clip, od.Playlist))
                ]
                
            case od.PartParameter():
                operand._data = self & operand._data    # Processes the tailed self operands or the Frame operand if any exists
                match operand._data:
                    case og.Staff() | ou.KeySignature() | og.TimeSignature() | ra.StaffParameter() | ou.Accidentals() | ou.Major() | ou.Minor() \
                            | og.Scale() | ra.Measures() | ou.Measure() | int() | float() | Fraction():
                        if isinstance(self._staff, og.Staff):
                            self._staff << operand._data

            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                for item in self._items: 
                    item << operand
        return self

    # operand is the pusher >> (NO COPIES!) (PASSTHROUGH)
    def __rrshift__(self, operand: o.T) -> o.T:
        match operand:
            case Part():
                wrapper_song: Part = Part()
                wrapper_song._items = [
                    data_clip for data_clip in operand._items
                ]
                wrapper_song._items.extend(
                    data_clip for data_clip in self._items
                )
                return wrapper_song
            case Clip():
                wrapper_song: Part = Part()
                wrapper_song._items = [ operand ]
                wrapper_song._items.extend(
                    data_clip for data_clip in self._items
                )
                return wrapper_song
            case tuple():
                for single_operand in operand:
                    self.__rrshift__(single_operand)
            case _:
                for single_item in self:
                    if isinstance(single_item, o.Operand):
                        single_item.__rrshift__(operand)
        return operand


    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Part():
                self._items.extend(
                    data_clip.copy() for data_clip in operand._items
                )
            case Clip():
                self._items.append( operand.copy() )

            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                for item in self._items: 
                    item += operand
        return self

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Part():
                self._items = [
                    single_clip for single_clip in self._items if single_clip not in operand._items
                ]
            case Clip():
                self._items = [
                    single_clip for single_clip in self._items if single_clip != operand
                ]
                
            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case _:
                for item in self._items: 
                    item -= operand
        return self

    def __imul__(self, operand: any) -> Self:
        import operand_selection as os
        match operand:
            case tuple():
                for single_operand in operand:
                    self *= single_operand
            case _:
                for item in self._items: 
                    item *= operand
        return self

    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case tuple():
                for single_operand in operand:
                    self /= single_operand
            case _:
                for item in self._items: 
                    item /= operand
        return self

