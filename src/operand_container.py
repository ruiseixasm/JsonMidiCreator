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
                # return self._datasource_list
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
                if operand >= 0 and operand < self.len():
                    return self[operand]
                return ol.Null()
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

    def __eq__(self, other: 'Container') -> bool:
        if isinstance(other, Container):
            return self._items == other._items
        if not isinstance(other, ol.Null):
            return self % other == other
        # if type(self) == type(other):
        #     return self._datasource_list == other % od.DataSource( list() )
            # When comparing lists containing objects in Python using the == operator,
            # Python will call the __eq__ method on the objects if it is defined,
            # rather than comparing their references directly.
            # If the __eq__ method is not defined for the objects, then the default behavior
            # (which usually involves comparing object identities, like references,
            # using the is operator) will be used.
        return False
    
    def first(self) -> o.Operand:
        if len(self._items) > 0:
            return self._items[0]
        return ol.Null()

    def last(self) -> o.Operand:
        if len(self._items) > 0:
            return self._items[len(self._items) - 1]
        return ol.Null()

    def middle(self, nth: int) -> o.Operand:
        if isinstance(nth, int) and nth > 0 and nth <= len(self._items):
            return self._items[nth - 1]
        return ol.Null()

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
        shallow_copy._items = [
            item for item in self
        ]
        for single_parameter in parameters:
            shallow_copy << single_parameter
        return shallow_copy
    
    def clear(self, *parameters) -> Self:
        self._items = []
        return super().clear(parameters)
    
    def sort(self, compare: o.Operand = None) -> Self:
        compare = ra.Position() if compare is None else compare
        self._items.sort(key=lambda x: x % compare)
        return self

    def shuffle(self, shuffler: ch.Chaos = None, parameter: type = ra.Position) -> Self:
        if shuffler is None or not isinstance(shuffler, ch.Chaos):
            shuffler = ch.SinX()
        parameters: list = []
        parameter_instance = parameter()
        if isinstance(parameter_instance, od.DataSource):
            for _ in range(len(self._items)):
                data_index: int = shuffler * 1 % int() % len(self._items)
                parameters.append(self._items[data_index])   # No need to copy
                del self._items[data_index] # Like picking up colored balls, pop out
            self._items = parameters
        else:
            for item in self._items:
                parameters.append(item % parameter_instance)   # No need to copy
            for item in self._items:
                data_index: int = shuffler * 1 % int() % len(parameters)
                item << parameters[data_index]
                del parameters[data_index] # Like picking up colored balls, pop out
        return self

    def reverse(self) -> Self:
        self_len: int = self.len()
        for operand_i in range(self_len // 2):
            tail_operand = self._items[self_len - 1 - operand_i]
            self._items[self_len - 1 - operand_i] = self._items[operand_i]
            self._items[operand_i] = tail_operand
        return self
    
    def rotate(self, offset: int = 1, parameter: type = ra.Duration) -> Self:
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
        return self

    def filter(self, criteria: any) -> Self:
        self._items = [item for item in self._items if item == criteria]
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
                for item in operand._items:
                    self._items.append(self.deep_copy(item))

            case list():
                for item in operand:
                    self._items.append( self.deep_copy( item ) )
            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                self._items.append(self.deep_copy( operand ))
        return self

    def __radd__(self, operand: any) -> Self:
        self_copy: Container = self.copy()
        self_copy._items.insert(0, self.deep_copy( operand ))
        return self_copy

    def __isub__(self, operand: any) -> Self:
        match operand:
            case Container():
                # Exclude items based on equality (==) comparison
                self._items = [
                        self_datasource.copy() for self_datasource in self._items
                        if all(self_datasource != operand_datasource for operand_datasource in operand._items)
                    ]
            case o.Operand():
                self._items = [self_datasource for self_datasource in self._items if self_datasource != operand]

            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case int(): # repeat n times the last argument if any
                if len(self._items) > 0:
                    while operand > 0 and len(self._items) > 0:
                        self._items.pop()
                        operand -= 1
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
                        self._items.extend(
                            self.deep_copy( data ) for data in items_copy
                        )
                        operand -= 1
                    self._items.extend( items_copy )
                elif operand == 0:
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
            case od.Getter() | od.Operation():
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
            case od.Getter() | od.Operation():
                self >>= operand
            case ch.Chaos():
                self.shuffle(operand)
            case om.Mutation():
                operand.mutate(self)
            case _:
                self.filter(operand)
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
        self._staff: og.Staff = og.defaults._staff.copy()
        self._midi_track: ou.MidiTrack  = ou.MidiTrack()
        self._position_beats: Fraction  = Fraction(0)   # in Beats
        self._length_beats: Fraction    = Fraction(-1)  # in Beats where -1 means isn't set
        super().__init__(*operands)


    def __getitem__(self, index: int) -> oe.Element:
        return self._items[index]


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> 'Clip':
        if isinstance(staff_reference, og.Staff):
            self._staff << staff_reference
        for single_element in self:
            if isinstance(single_element, oe.Element):
                single_element.set_staff_reference(self._staff)
        return self

    def get_staff_reference(self) -> 'og.Staff':
        return self._staff

    def reset_staff_reference(self) -> 'Clip':
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
                | int() | float() | Fraction():
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
            if isinstance(item, oe.Element):
                position_beats: Fraction = item._position_beats
                if start_beats is None or position_beats < start_beats:   # Implicit conversion
                    start_beats = position_beats
        if start_beats:
            return self._staff.convertToPosition(ra.Beats(start_beats))
        return self._staff.convertToPosition(0)

    def finish(self) -> ra.Position:
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
        return ra.Length( self.finish() - self.start() )

    def duration(self) -> ra.Duration:
        return self.length().convertToDuration()


    if TYPE_CHECKING:
        from operand_element import Element

    def get_clip_elements(self) -> list['Element']: # Helper method
        clip_elements: list[oe.Element] = []
        tied_notes: list[oe.Note] = []
        for item in self._items:   # Read only (extracts the play list)
            if isinstance(item, oe.Element):
                if isinstance(item, oe.Note) and item._tied:
                    tied_notes.append(item.copy())
                else:
                    clip_elements.append(item)
        if len(tied_notes) > 0: # Extends the root Note to accommodate all following Notes durations
            first_tied_note: oe.Note = tied_notes[0]
            for next_tied_note_i in range(1, len(tied_notes)):
                # Must be in clip to be tied (FS - Finish to Start)!
                next_note_position: Fraction = first_tied_note._position_beats \
                    + first_tied_note % ra.Length() // Fraction()
                if tied_notes[next_tied_note_i]._pitch == first_tied_note._pitch \
                    and tied_notes[next_tied_note_i]._channel == first_tied_note._channel \
                    and tied_notes[next_tied_note_i]._position_beats == next_note_position:

                    first_tied_note._duration_notevalue += tied_notes[next_tied_note_i]._duration_notevalue
                    if next_tied_note_i == len(tied_notes) - 1:   # list come to its end
                        clip_elements.append(first_tied_note)
                else:
                    clip_elements.append(first_tied_note)
                    first_tied_note = tied_notes[next_tied_note_i]
                    if next_tied_note_i == len(tied_notes) - 1:   # list come to its end
                        clip_elements.append(first_tied_note)
        return clip_elements

    def getPlaylist(self, position_beats: Fraction = None) -> list[dict]:

        if isinstance(position_beats, Fraction):
            position_beats += self._position_beats
        else:
            position_beats = self._position_beats

        return [
            single_playlist
                for single_element in self.get_clip_elements()
                for single_playlist in single_element.getPlaylist(position_beats)
        ]

    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list[dict]:
        midi_track: ou.MidiTrack = self._midi_track if not isinstance(midi_track, ou.MidiTrack) else midi_track
        if isinstance(position_beats, Fraction):
            position_beats += self._position_beats
        else:
            position_beats = self._position_beats

        return [
            single_midilist
                for single_element in self.get_clip_elements()
                for single_midilist in single_element.getMidilist(midi_track, position_beats)
        ]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["staff"]        = self.serialize(self._staff)
        serialization["parameters"]["midi_track"]   = self.serialize(self._midi_track)
        serialization["parameters"]["position"]     = self.serialize(self._position_beats)
        serialization["parameters"]["length"]       = self.serialize(self._length_beats)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
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
                    self.deep_copy(item) for item in operand if isinstance(item, oe.Element)
                ]
            case tuple():
                for single_operand in operand:
                    self << single_operand
                    
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
        shallow_copy._staff             << self._staff
        shallow_copy._midi_track        << self._midi_track
        shallow_copy._position_beats    = self._position_beats
        shallow_copy._length_beats      = self._length_beats
        for single_parameter in parameters:
            shallow_copy << single_parameter
        return shallow_copy
    
    # operand is the pusher >> (NO COPIES!)
    def __rrshift__(self, operand: any) -> 'Clip':
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
                element_length: ra.Length = self._staff.convertToLength( operand % ra.Length() )
                # Convert Length to Position
                add_position: ra.Position = ra.Position(element_length)
                self += add_position  # No copy!
                self._items.insert(0, operand.set_staff_reference(self._staff))
            case ra.Position():
                self._position_beats = self._staff.convertToBeats(operand)._rational
            case ra.Length() | ra.TimeValue() | ra.Duration() | ou.TimeUnit():
                self._position_beats += self._staff.convertToBeats(operand)._rational
            case od.Playlist():
                return operand >> od.Playlist(self.getPlaylist(self._position_beats))
            case tuple():
                return super().__rrshift__(operand)
        return self


    # Avoids the costly copy of Track self doing +=
    def __iadd__(self, operand: any) -> 'Clip':
        match operand:
            case Part():
                # Song at the right must be a copy
                new_song: Part = operand.copy()
                # Inserts self content at the beginning of the Song
                new_song._items.insert(0, self)
                return new_song # Operand Song replaces self Clip
            case Clip():
                operand_elements = [
                    single_data.copy().set_staff_reference(self._staff) for single_data in operand._items
                        if isinstance(single_data, oe.Element)
                ]
                if operand._position_beats > self._position_beats:
                    for single_element in operand_elements:
                        single_element += ra.Beats(operand._position_beats - self._position_beats)
                elif operand._position_beats < self._position_beats:
                    self += ra.Beats(self._position_beats - operand._position_beats) # NO IMPLICIT COPY
                    self._position_beats = operand._position_beats
                self._items.extend( single_element for single_element in operand_elements )
            case oe.Element():
                return super().__iadd__(operand).set_staff_reference()
            case list():
                for item in operand:
                    if isinstance(item, oe.Element):
                        self._items.append( item.copy() )
                        
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
        return self

    def __isub__(self, operand: any) -> 'Clip':
        match operand:
            case Part():
                operand -= self # Order is irrelevant in Song
                return operand 
            case oe.Element() | Container():
                return super().__isub__(operand)
            
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
        return self

    # in-place multiply (NO COPY!)
    def __imul__(self, operand: any) -> Self:
        match operand:
            case Clip():
                if self._length_beats < 0:
                    left_end_position: ra.Position = self.finish()
                else:
                    left_end_position: ra.Position = self._staff.convertToPosition(ra.Beats(self._length_beats))
                    self._length_beats += (operand % ra.Length())._rational
                right_start_position: ra.Position = operand.start()
                length_shift: ra.Length = ra.Length(left_end_position - right_start_position).roundMeasures()
                # Convert Length to Position
                add_position: ra.Position = ra.Position(length_shift)
                operand_elements = [
                    (single_data + add_position).set_staff_reference(self._staff) for single_data in operand._items
                        if isinstance(single_data, oe.Element)
                ]
                self._items.extend( single_element for single_element in operand_elements )
            case int() | float():
                if self._length_beats >= 0:
                    add_position: ra.Position = self._staff.convertToPosition(ra.Beats(self._length_beats))
                    operand = int(operand)
                    self._length_beats *= operand
                elif isinstance(operand, int):
                    add_position: ra.Position = ra.Position((self % ra.Length()).roundMeasures())
                else:
                    add_position: ra.Position = ra.Position(self.length())
                    operand = int(operand)
                if operand > 1:
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
            case ra.TimeValue():
                self_repeating: float = 0.0
                self_length: ra.Length = self % ra.Length()
                length_value: Fraction = self_length % operand % Fraction()
                if length_value > 0:
                    operand_value: Fraction = operand._rational
                    self_repeating: float = float( operand_value / length_value )
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

            case tuple():
                for single_operand in operand:
                    self *= single_operand
            case _:
                for item in self._items:
                    item *= operand
        return self

    def __rmul__(self, operand: any) -> 'Clip':
        return self.__mul__(operand)
    
    def __itruediv__(self, operand: any) -> 'Clip':
        import operand_mutation as om
        match operand:
            case int():
                return super().__itruediv__(operand)
            
            case od.ClipParameter():
                operand._data = self & operand._data    # Processes the tailed self operands or the Frame operand if any exists
                match operand._data:
                    case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                        self._position_beats /= self._staff.convertToBeats(operand)._rational

            # Returns an altered Clip with less info (truncated info)
            case od.Getter() | od.Operation():
                return self >> operand

            case ch.Chaos():
                return self.shuffle(operand)
            case om.Mutation():
                return operand.mutate(self)

            case tuple():
                for single_operand in operand:
                    self /= single_operand
            case _:
                for item in self._items:
                    item /= operand
        return self

    def reverse(self) -> 'Clip':
        length_beats: Fraction = ra.Length( self.finish() ).roundMeasures()._rational # Rounded up Duration to next Measure
        for item in self._items:
            if isinstance(item, oe.Element):
                single_element: oe.Element = item
                duration_beats: Fraction = single_element % ra.Length() // Fraction()
                # Only changes Positions
                single_element._position_beats = length_beats - (single_element._position_beats + duration_beats)
        return super().reverse()    # Reverses the list

    def flip(self) -> 'Clip':
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

    def snap(self, up: bool = False) -> 'Clip':
        for single_note in self:
            if isinstance(single_note, oe.Note):
                single_note._pitch.snap(up)
        return self

    def extend(self, time_value: ra.TimeValue | ra.Duration) -> 'Clip':
        extended_clip: Clip = self.copy() << od.DataSource( self._items )
        while (extended_clip >> self).length() <= time_value:
            extended_clip >>= self
        self._items = extended_clip._items
        return self

    def trim(self, length: ra.Length = ra.Length(1.0)) -> 'Clip':
        if isinstance(length, ra.Length):
            length_beats: Fraction = length._rational
        else:
            length_beats: Fraction = self._staff.convertToBeats(ra.Measures(1))._rational
        self._items = [
            item for item in self._items
            if isinstance(item, oe.Element) and item._position_beats < length_beats
        ]
        if self._length_beats >= 0:
            self._length_beats = min(self._length_beats, length_beats)
        return self

    def fill(self) -> 'Clip':
        return self

    def fit(self, time: Union['ra.Position', 'ra.TimeValue', 'ra.Duration', 'ou.TimeUnit'] = None) -> 'Clip':
        if isinstance(time, (ra.Position, ra.TimeValue, ra.Duration, ou.TimeUnit)):
            fitting_finish: ra.Position = self._staff.convertToPosition(time)
        else:
            fitting_finish: ra.Position = self._staff.convertToPosition(ou.Measure(1))
        actual_finish: ra.Position = self.finish()
        length_ratio: Fraction = fitting_finish._rational / actual_finish._rational
        self *= ra.Position(length_ratio)   # Adjust positions
        self *= ra.Duration(length_ratio)   # Adjust durations
        return self

    def link(self) -> 'Clip':
        self.sort()
        element_index: int = 0
        first_element_index: int = None
        last_element: oe.Element = None
        for single_data in self._items:
            if isinstance(single_data, oe.Element) and single_data._stackable:
                if last_element is not None:
                    last_element << self._staff.convertToDuration(ra.Beats(single_data._position_beats - last_element._position_beats))
                else:
                    first_element_index = element_index
                last_element = single_data
            element_index += 1
        # Add a Rest in the beginning if necessary
        if first_element_index is not None:
            first_element: oe.Element = self._items[first_element_index]
            if first_element._position_beats != 0:  # Not the first position
                rest_duration: ra.Duration = self._staff.convertToDuration(ra.Beats(first_element._position_beats))
                self._items.insert(first_element_index, oe.Rest(rest_duration))
        # Adjust last_element duration based on its Measure position
        if last_element is not None:    # LAST ELEMENT ONLY!
            remaining_beats: Fraction = self._staff.convertToLength(ra.Beats(last_element._position_beats)).roundMeasures()._rational - last_element._position_beats
            last_element << self._staff.convertToDuration(ra.Beats(remaining_beats))
        return self

    def stack(self) -> 'Clip':

        # Starts by sorting the self Elements list accordingly to their Tracks (all data is a Stackable Element)
        stackable_elements: list[oe.Element] = [
                single_data
                for single_data in self._items
                if isinstance(single_data, oe.Element) and single_data._stackable
            ]
        for index, single_element in enumerate(stackable_elements):
            if index > 0:
                duration_beats: Fraction = self._staff.convertToBeats(ra.Duration(stackable_elements[index - 1]._duration_notevalue))._rational
                single_element._position_beats = stackable_elements[index - 1]._position_beats + duration_beats  # Stacks on Element Duration
            else:   # FIRST ELEMENT!
                single_element._position_beats = Fraction(0)   # everything starts at the beginning (0)!
        
        return self
    
    def tie(self, tied: bool = True) -> 'Clip':
        for item in self._items:
            if isinstance(item, oe.Note):
                item << ou.Tied(tied)
        return self
    
    def slur(self, gate: float = 1.05) -> 'Clip':
        last_element = None
        for item in self._items:
            if isinstance(item, oe.Note):
                if last_element is not None:
                    last_element << ra.Gate(gate)
                last_element = item
        return self
    
    def smooth(self) -> 'Clip':
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
        self_left: Clip     = self.filter(of.Less(position))
        self_right: Clip    = self.filter(of.GreaterEqual(position))
        return self_left, self_right



class Part(Container):

    def __getitem__(self, key: str | int) -> Clip:
        if isinstance(key, str):
            for single_clip in self:
                if isinstance(single_clip, Clip):   # Playlists aren't selectable by name !
                    if single_clip._midi_track._name == key:
                        return single_clip
            return ol.Null()
        return self._items[key]

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case ou.MidiTrack():
                for single_clip in self:
                    if isinstance(single_clip, Clip):
                        if single_clip._midi_track == operand:
                            return single_clip
                return ol.Null()
            case str():             return self[operand]
            case _:                 return super().__mod__(operand)

    def getPlaylist(self, position: ra.Position = None) -> list:
        play_list: list = []
        for single_clip in self:
            if isinstance(single_clip, (Clip, od.Playlist)):
                play_list.extend(single_clip.getPlaylist(position))
        return play_list

    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        midi_list: list = []
        for single_clip in self:
            if isinstance(single_clip, Clip):   # Can't get Midilist from Playlist !
                midi_list.extend(single_clip.getMidilist(midi_track, position))
        return midi_list

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Part():
                super().__lshift__(operand)
            case Clip():
                self._items.append( operand.copy() )
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._items = [
                    self.deep_copy(item) for item in operand if isinstance(item, (Clip, od.Playlist))
                ]
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                for item in self._items: 
                    item << operand
        return self

    # operand is the pusher >> (NO COPIES!)
    def __rrshift__(self, operand: any) -> 'Part':
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
        return self


    def __iadd__(self, operand: any) -> 'Part':
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

    def __isub__(self, operand: any) -> 'Part':
        match operand:
            case Part():
                self._items = [
                    data_clip for data_clip in self._items if data_clip not in operand._items
                ]
            case Clip():
                self._items = [
                    data_clip for data_clip in self._items if data_clip != operand
                ]
                
            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case _:
                for item in self._items: 
                    item -= operand
        return self

    def __imul__(self, operand: any) -> 'Part':
        match operand:
            case tuple():
                for single_operand in operand:
                    self *= single_operand
            case _:
                for item in self._items: 
                    item *= operand
        return self

    def __itruediv__(self, operand: any) -> 'Part':
        match operand:
            case tuple():
                for single_operand in operand:
                    self /= single_operand
            case _:
                for item in self._items: 
                    item /= operand
        return self

