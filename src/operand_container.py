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
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Any
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

TypeContainer = TypeVar('TypeContainer', bound='Container')  # TypeContainer represents any subclass of Operand


class Container(o.Operand):
    def __init__(self, *operands):
        super().__init__()
        self._datasource_list: list[Type[od.DataSource]] = []
        self._datasource_iterator: int = 0
        for single_operand in operands:
            match single_operand:
                case Container():
                    self._datasource_list.extend(self.deep_copy(single_operand._datasource_list))
                case list():
                    for operand in single_operand:
                        self._datasource_list.append(od.DataSource( self.deep_copy(operand) ))
                case _:
                    self._datasource_list.append(od.DataSource( self.deep_copy(single_operand) ))
        
    def __getitem__(self, index: int) -> any:
        return self._datasource_list[index]._data

    def __iter__(self):
        return self
    
    def __next__(self):
        if self._datasource_iterator < len(self._datasource_list):
            single_datasource = self._datasource_list[self._datasource_iterator]
            self._datasource_iterator += 1
            return single_datasource._data  # It's the data that should be returned
        else:
            self._datasource_iterator = 0   # Reset to 0 when limit is reached
            raise StopIteration

    def __mod__(self, operand: any) -> any:
        """
        The % symbol is used to extract a Parameter, because a Container has
        only one type of Parameters it should be used in conjugation with list()
        to extract the Parameter list.

        Examples
        --------
        >>> sequence = Sequence(Note("A"), Note("B"))
        >>> sequence % list() >> Print()
        [<operand_element.Note object at 0x0000017B5F3FF6D0>, <operand_element.Note object at 0x0000017B5D3B36D0>]
        """
        match operand:
            case od.DataSource():
                # return self._datasource_list
                match operand._data:
                    case Container():
                        return self
                    case od.Getter() | od.Operation():
                        return self >> operand
                    case ch.Chaos():
                        return self.shuffle(operand)
                    case list():
                        return self._datasource_list
                    case _:
                        return super().__mod__(operand)
            case Container():
                return self.copy()
            case od.Getter() | od.Operation():
                return self.copy() >> operand
            case ch.Chaos():
                return self.copy().shuffle(operand)
            case list():
                operands: list[o.Operand] = []
                for single_datasource in self._datasource_list:
                    operands.append(self.deep_copy(single_datasource._data))
                return operands
            case int():
                if operand >= 0 and operand < self.len():
                    return self[operand]
                return ol.Null()
            case ou.Next():
                self._index += operand % int() - 1
                single_datasource_data: any = self._datasource_list[self._index % len(self._datasource_list)]._data
                self._index += 1
                self._index %= len(self._datasource_list)
                return single_datasource_data
            case ou.Previous():
                self._index -= operand % int()
                self._index %= len(self._datasource_list)
                single_datasource_data: any = self._datasource_list[self._index]._data
                return single_datasource_data
            case of.Frame():
                return self.filter(operand)
            case _:
                return super().__mod__(operand)

    def len(self) -> int:
        return len(self._datasource_list)

    def __eq__(self, other: 'Container') -> bool:
        if isinstance(other, Container):
            return self._datasource_list == other._datasource_list
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
        if len(self._datasource_list) > 0:
            return self._datasource_list[0]._data
        return ol.Null()

    def last(self) -> o.Operand:
        if len(self._datasource_list) > 0:
            return self._datasource_list[len(self._datasource_list) - 1]._data
        return ol.Null()

    def middle(self, nth: int) -> o.Operand:
        if isinstance(nth, int) and nth > 0 and nth <= len(self._datasource_list):
            return self._datasource_list[nth - 1]._data
        return ol.Null()

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["datasource_list"] = self.serialize(self._datasource_list)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "datasource_list" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._datasource_list = self.deserialize(serialization["parameters"]["datasource_list"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Container':
        match operand:
            case Container():
                super().__lshift__(operand)
                self._datasource_list = self.deep_copy( operand._datasource_list )
                # COPY THE SELF OPERANDS RECURSIVELY
                if self._next_operand:
                    self._next_operand = self.deep_copy(operand._next_operand)
            case od.DataSource():
                match operand._data:
                    case list():        self._datasource_list = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._datasource_list = []
                for single_operand in operand:
                    self._datasource_list.append(od.DataSource( self.deep_copy(single_operand) ))
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _: # Works for Frame too
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, o.Operand):
                        single_datasource._data << operand
        return self

    # def copy(self, *parameters) -> 'Container':
    #     container_copy: Container = self.__class__()
    #     for single_datasource in self._datasource_list:
    #         container_copy._datasource_list.append( self.deep_copy(single_datasource) )
    #     # COPY THE SELF OPERANDS RECURSIVELY
    #     if self._next_operand:
    #         container_copy._next_operand = self.deep_copy(self._next_operand)
    #     for single_parameter in parameters:
    #         container_copy << single_parameter
    #     return container_copy
    
    def clear(self, *parameters) -> 'Container':
        self._datasource_list = []
        return super().clear(parameters)
    
    def sort(self, compare: o.Operand = None) -> 'Container':
        compare = ra.Position() if compare is None else compare
        for operand_i in range(self.len() - 1):
            sorted_list = True
            for operand_j in range(self.len() - 1 - operand_i):
                if self._datasource_list[operand_j]._data % compare > self._datasource_list[operand_j + 1]._data % compare:
                    temporary_operand = self._datasource_list[operand_j]._data
                    self._datasource_list[operand_j]._data = self._datasource_list[operand_j + 1]._data
                    self._datasource_list[operand_j + 1]._data = temporary_operand
                    sorted_list = False
            if sorted_list:
                break
        return self
    
    def shuffle(self, shuffler: ch.Chaos = None) -> 'Container':
        if shuffler is None or not isinstance(shuffler, ch.Chaos):
            shuffler = ch.SinX()
        container_data: list = []
        for single_datasource in self._datasource_list:
            container_data.append(single_datasource._data)   # No need to copy
        for single_datasource in self._datasource_list:
            data_to_extract: int = shuffler * 1 % int() % len(container_data)
            single_datasource._data = container_data[data_to_extract]
            del container_data[data_to_extract]
        return self

    def reverse(self) -> 'Container':
        self_len: int = self.len()
        for operand_i in range(self_len // 2):
            tail_operand = self._datasource_list[self_len - 1 - operand_i]._data
            self._datasource_list[self_len - 1 - operand_i]._data = self._datasource_list[operand_i]._data
            self._datasource_list[operand_i]._data = tail_operand
        return self

    def filter(self, criteria: any) -> 'Container':
        new_container: Container = self.__class__()
        new_container._datasource_list = [self_datasource for self_datasource in self._datasource_list if self_datasource._data == criteria]
        return new_container

    def __add__(self, operand: o.Operand) -> 'Container':
        match operand:
            case Container():
                self_copy: Container = self.__class__()
                for single_datasource in self._datasource_list:
                    self_copy._datasource_list.append(self.deep_copy(single_datasource))
                for single_datasource in operand._datasource_list:
                    self_copy._datasource_list.append(self.deep_copy(single_datasource))
                return self_copy
            case _:
                if isinstance(operand, od.DataSource):
                    self._datasource_list.append(od.DataSource( self.deep_copy( operand._data ) ))
                    return self
                self_copy = self.copy()
                self_copy._datasource_list.append(od.DataSource( self.deep_copy( operand ) ))
                return self_copy
    
    def __radd__(self, operand: o.Operand) -> o.Operand:
        self_copy: Container = self.copy()
        self_copy._datasource_list.insert(0, od.DataSource( self.deep_copy( operand ) ))
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Container':
        self_copy: Container = self.copy()
        match operand:
            case Container():
                # Exclude items based on equality (==) comparison
                self_copy._datasource_list = [
                        self_datasource.copy() for self_datasource in self._datasource_list
                        if all(self_datasource != operand_datasource for operand_datasource in operand._datasource_list)
                    ]
            case o.Operand():
                self_copy._datasource_list = [self_datasource for self_datasource in self._datasource_list if self_datasource._data != operand]
            case int(): # repeat n times the last argument if any
                if len(self._datasource_list) > 0:
                    while operand > 0 and len(self_copy._datasource_list) > 0:
                        self_copy._datasource_list.pop()
                        operand -= 1
        return self_copy

    # multiply with a scalar 
    def __mul__(self, operand: o.Operand) -> 'Container':
        match operand:
            case Container():
                pass
            case o.Operand():
                pass
            case int(): # repeat n times the self content if any
                many_operands = self.__class__()    # with an empty list
                while operand > 0:
                    many_operands += self
                    operand -= 1
                return many_operands
        return self.copy()
    
    def __truediv__(self, operand: o.Operand) -> 'Container':
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
                        many_operands._datasource_list.append(od.DataSource(
                                self.deep_copy( self._datasource_list[cut_len - nth_item]._data )
                            ))
                        nth_item -= 1
                    return many_operands
        return self.copy()

    def __pow__(self, operand: 'o.Operand') -> 'Container':
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, o.Operand):
                single_datasource._data.__pow__(operand)
        return self

    def __or__(self, operand: any) -> 'Container':
        match operand:
            case Container():
                new_container: Container = self.__class__()
                new_container._datasource_list.extend(self._datasource_list)
                new_container._datasource_list.extend(operand._datasource_list)
                return new_container
            case _:
                return self.filter(operand)

    def __ror__(self, operand: any) -> 'Container':
        return self.__or__(operand)

class Sequence(Container):  # Just a container of Elements
    def __init__(self, *operands):

        super().__init__(*operands)
        self._midi_track: ou.MidiTrack = ou.MidiTrack()
        self._position: ra.Position = ra.Position()
        for single_operand in operands:
            match single_operand:
                case Sequence():
                    self._midi_track    << single_operand._midi_track
                    self._position      << single_operand._position
                case ou.MidiTrack():
                    self._midi_track    << single_operand
                case ra.Position():
                    self._position = single_operand.copy()
        self._datasource_list = o.filter_list(self._datasource_list, lambda data_source: isinstance(data_source._data, oe.Element))


    def __getitem__(self, index: int) -> oe.Element:
        return self._datasource_list[index]._data

    def __mod__(self, operand: any) -> any:
        """
        The % symbol is used to extract a Parameter, because a Container has
        only one type of Parameters it should be used in conjugation with list()
        to extract the Parameter list.

        Examples
        --------
        >>> sequence = Sequence(Note("A"), Note("B"))
        >>> sequence % list() >> Print()
        [<operand_element.Note object at 0x0000017B5F3FF6D0>, <operand_element.Note object at 0x0000017B5D3B36D0>]
        """
        match operand:
            case od.DataSource():
                match operand._data:
                    case ou.MidiTrack():    return self._midi_track
                    case ra.Position():     return self._position
                    case _:                 return super().__mod__(operand)
            case ou.MidiTrack():    return self._midi_track.copy()
            case ra.Length():       return self.length()
            case ra.Duration():     return self.duration()
            case ra.Position():     return self._position.copy()
            case ra.Duration():     return self.duration()
            case _:                 return super().__mod__(operand)

    def start(self) -> ra.Position:
        start: ra.Position = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                element_position: ra.Position = single_datasource._data._position
                if not start or element_position < start:   # Implicit conversion
                    start = self._position.getPosition( element_position )
        if start:
            return start
        return self._position.copy(0.0)

    def finish(self) -> ra.Position:
        finish: ra.Position = self._position.copy(0.0)
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                single_element: oe.Element = single_datasource._data
                element_finish: ra.Position = single_element._position + single_element._duration
                if element_finish > finish:    # Implicit conversion
                    finish = finish.getPosition(element_finish) # Explicit conversion
        return finish


    def length(self) -> ra.Length:
        return ra.Length( self.finish() - self.start() )

    def duration(self) -> ra.Duration:
        return self.length().getDuration()


    if TYPE_CHECKING:
        from operand_element import Element

    def get_sequence_elements(self) -> list['Element']: # Helper method
        sequence_elements: list[oe.Element] = []
        tied_notes: list[oe.Note] = []
        for single_datasource in self._datasource_list:   # Read only (extracts the play list)
            if isinstance(single_datasource._data, oe.Element):
                if isinstance(single_datasource._data, oe.Note) and single_datasource._data._tied:
                    tied_notes.append(single_datasource._data.copy())
                else:
                    sequence_elements.append(single_datasource._data)
        if len(tied_notes) > 0: # Extends the root Note to accommodate all following Notes durations
            first_tied_note: oe.Note = tied_notes[0]
            for next_tied_note_i in range(1, len(tied_notes)):
                # Must be in sequence to be tied (FS - Finish to Start)!
                next_note_position: ra.Position = first_tied_note._position + first_tied_note._duration # Duration is particularly tricky
                if tied_notes[next_tied_note_i]._pitch == first_tied_note._pitch \
                    and tied_notes[next_tied_note_i]._channel == first_tied_note._channel \
                    and tied_notes[next_tied_note_i]._position == next_note_position:
                    first_tied_note += tied_notes[next_tied_note_i]._duration # Duration is particularly tricky
                    if next_tied_note_i == len(tied_notes) - 1:   # list come to its end
                        sequence_elements.append(first_tied_note)
                else:
                    sequence_elements.append(first_tied_note)
                    first_tied_note = tied_notes[next_tied_note_i]
                    if next_tied_note_i == len(tied_notes) - 1:   # list come to its end
                        sequence_elements.append(first_tied_note)
        return sequence_elements

    def getPlaylist(self, position: ra.Position = None) -> list[dict]:

        if isinstance(position, ra.Position):
            position += self._position
        else:
            position = self._position

        play_list: list[dict] = []
        for single_element in self.get_sequence_elements():
            play_list.extend(single_element.getPlaylist(position))

        return play_list

    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list[dict]:
        midi_track: ou.MidiTrack = self._midi_track if not isinstance(midi_track, ou.MidiTrack) else midi_track
        if isinstance(position, ra.Position):
            position += self._position
        else:
            position = self._position

        midi_list: list[dict] = []
        for single_element in self.get_sequence_elements():
            midi_list.extend(single_element.getMidilist(midi_track, position))
        return midi_list

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["midi_track"]   = self.serialize(self._midi_track)
        serialization["parameters"]["position"]     = self.serialize(self._position)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "midi_track" in serialization["parameters"] and "position" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._midi_track    = self.deserialize(serialization["parameters"]["midi_track"])
            self._position      = self.deserialize(serialization["parameters"]["position"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Sequence':

        c.profiling_timer.call_timer_a()

        match operand:
            case Sequence():
                self._midi_track        << operand._midi_track
                self._position          << operand._position
                self._datasource_list   = self.deep_copy( operand._datasource_list )
                # COPY THE SELF OPERANDS RECURSIVELY
                if operand._next_operand:
                    self._next_operand  = self.deep_copy(operand._next_operand)
            case od.DataSource():
                match operand._data:
                    case ou.MidiTrack():    self._midi_track = operand._data
                    case ra.Position():     self._position = operand._data
                    case _:
                        super().__lshift__(operand)
                        self._datasource_list = o.filter_list(self._datasource_list, lambda data_source: isinstance(data_source._data, oe.Element))
            case ou.MidiTrack():
                self._midi_track << operand
            case ra.Duration(): # Works for Frame too
                for single_datasource in self._datasource_list:
                    single_datasource._data << operand
            # Use Frame objects to bypass this parameter into elements (Setting Position)
            case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                self._position << operand
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._datasource_list = []
                for single_operand in operand:
                    self._datasource_list.append(od.DataSource( self.deep_copy(single_operand) ))
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _: # Works for Frame too
                for single_datasource in self._datasource_list:
                    single_datasource._data << operand
                
        c.profiling_timer.call_timer_b()

        return self

    # def copy(self, *parameters) -> 'Sequence':

    #     sequence_copy: Sequence = Sequence()
    #     sequence_copy._midi_track   << self._midi_track
    #     sequence_copy._position     << self._position
    #     for single_datasource in self._datasource_list:
    #         sequence_copy._datasource_list.append( self.deep_copy(single_datasource) )
    #     # COPY THE SELF OPERANDS RECURSIVELY
    #     if self._next_operand:
    #         sequence_copy._next_operand = self.deep_copy(self._next_operand)
    #     for single_parameter in parameters:
    #         sequence_copy << single_parameter

    #     return sequence_copy
    
    # operand is the pusher >>
    def __rrshift__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case Sequence():
                if self._midi_track._name == operand._midi_track._name:
                    if operand.len() > 0:
                        left_end_position: ra.Position = operand.finish()
                        right_start_position: ra.Position = self.start()
                        length_shift: ra.Length = ra.Length(left_end_position - right_start_position).roundMeasures()
                        right_sequence: Sequence = self + length_shift  # Offsets the content and it's an implicit copy
                        added_sequence: Sequence = operand.copy()       # Preserves the left_sequence configuration
                        added_sequence._datasource_list.extend(right_sequence._datasource_list)
                        return added_sequence
                    return self.copy()
                return Song(operand, self)
            case oe.Element():
                return self.__radd__(operand).stack()   # Can't be removed (Analyze better why)
            case ra.Position() | ra.TimeValue() | ou.TimeUnit() | ra.Duration():
                self._position += operand
                return self
            case od.Playlist():
                return operand >> od.Playlist(self.getPlaylist(self._position))
            case tuple():
                return super().__rrshift__(operand)
        return self.copy()

    def __add__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case Song():
                return operand + self   # Order is irrelevant on Song
            case Sequence():
                if self._midi_track == operand._midi_track:

                    # Does the needed position conversion first and replicates to its elements
                    if operand._position > self._position:
                        self_copy: Sequence = self.copy()
                        operand_copy: Sequence = operand + ( operand._position - self._position )   # Implicit copy of operand
                    elif operand._position < self._position:
                        self_copy: Sequence = self + ( self._position - operand._position )         # Implicit copy of operand
                        self_copy._position = self_copy._position.getPosition(operand._position)    # Avoids changing other attributes of self_copy._position
                        operand_copy: Sequence = operand.copy()
                    else:
                        self_copy: Sequence = self.copy()
                        operand_copy: Sequence = operand.copy()
                    # operand is already a copy, let's take advantage of that
                    self_copy._datasource_list.extend(operand_copy._datasource_list)

                    return self_copy  # self_copy becomes the __add__ result as an add copy
                return Song(self, operand)
            case oe.Element():
                return super().__add__(operand)
            case _:

                self_copy: Sequence = Sequence() << self._position << self._midi_track
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, oe.Element): # Makes sure it's an Element
                        # It's already a copy, avoids extra copy by filling the list directly
                        self_copy._datasource_list.append(od.DataSource( single_datasource._data + operand ))

                return self_copy

    def __sub__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case Song():
                return operand - self   # Order is irrelevant on Song
            case Container():
                return super().__sub__(operand)
            case oe.Element():
                return super().__sub__(operand)
            case _:

                self_copy: Sequence = Sequence() << self._position << self._midi_track
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, oe.Element): # Makes sure it's an Element
                        # It's already a copy, avoids extra copy by filling the list directly
                        self_copy._datasource_list.append(od.DataSource( single_datasource._data - operand ))

                return self_copy

    # multiply with a scalar
    def __mul__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case int():

                many_operands = self.__class__()    # empty list but same track
                many_operands._midi_track   = self._midi_track  # no need for "<<" because
                many_operands._position     = self._position    # it will become 1 single sequence
                single_length: ra.Length    = self.length().roundMeasures()
                for segment in range(operand):
                    many_operands._datasource_list.extend( (self + single_length * segment)._datasource_list )

                return many_operands
            case float():

                many_operands = self.__class__()    # empty list but same track
                many_operands._midi_track   = self._midi_track  # no need for "<<" because
                many_operands._position     = self._position    # it will become 1 single sequence
                single_length: ra.Length    = self.length()
                repeat_copy: int = int(operand)
                for segment in range(repeat_copy):
                    many_operands._datasource_list.extend( (self + single_length * segment)._datasource_list )

                return many_operands
            case ou.TimeUnit():
                self_repeating: int = 0
                operand_beats: Fraction = self._position.getBeats(operand)._rational
                self_beats: Fraction = self.length().roundMeasures()._rational  # Beats default unit
                if self_beats > 0:
                    self_repeating = operand_beats // self_beats
                return self * self_repeating
            case ra.TimeValue():
                self_repeating: float = 0.0
                self_length: Fraction = (self.length() % operand)._rational
                if self_length > 0:
                    operand_length: Fraction = operand._rational
                    self_repeating: float = float( operand_length / self_length )
                return self * self_repeating
            case _:
                
                self_copy: Sequence = Sequence() << self._position << self._midi_track
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, oe.Element): # Makes sure it's an Element
                        # It's already a copy, avoids extra copy by filling the list directly
                        self_copy._datasource_list.append(od.DataSource( single_datasource._data * operand ))

                return self_copy
    
    def __rmul__(self, operand: any) -> 'Sequence':
        return self.__mul__(operand)
    
    def __truediv__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case int():
                return super().__truediv__(operand)
            case _:
                
                self_copy: Sequence = Sequence() << self._position << self._midi_track
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, oe.Element): # Makes sure it's an Element
                        # It's already a copy, avoids extra copy by filling the list directly
                        self_copy._datasource_list.append(od.DataSource( single_datasource._data / operand ))

                return self_copy

    def __or__(self, operand: any) -> 'Sequence':
        match operand:
            case Sequence():
                new_sequence: Sequence = self.__class__()
                new_sequence._datasource_list.extend(self._datasource_list)
                new_sequence._datasource_list.extend(operand._datasource_list)
                new_sequence._midi_track   << self._midi_track
                new_sequence._position     << self._position
                return new_sequence
            case _:
                return self.filter(operand)

    def filter(self, criteria: any) -> 'Sequence':
        filtered_sequence: Sequence = self.__class__()
        filtered_sequence._datasource_list = [self_datasource for self_datasource in self._datasource_list if self_datasource._data == criteria]
        filtered_sequence._midi_track   << self._midi_track
        filtered_sequence._position     << self._position
        return filtered_sequence

    def reverse(self) -> 'Sequence':
        sequence_length: ra.Length = ra.Length( self.finish() ).roundMeasures() # Rounded up Duration to next Measure
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                single_element: oe.Element = single_datasource._data
                element_position: ra.Position = single_element._position
                element_duration: ra.Duration = single_element._duration
                # Implicit Position conversion
                new_position: ra.Position = sequence_length - (element_position + element_duration)
                element_position << element_position.getSteps( new_position )
        return super().reverse()    # Reverses the list


    def extend(self, time_value: ra.TimeValue) -> 'Sequence':
        extended_sequence: Sequence = self.copy() << od.DataSource( self._datasource_list )
        while (extended_sequence >> self).length() <= time_value:
            extended_sequence >>= self
        self._datasource_list = extended_sequence._datasource_list
        return self

    def trim(self, length: ra.Length) -> 'Sequence':
        return self

    def fill(self) -> 'Sequence':
        return self


    def link(self) -> 'Sequence':
        self.sort()
        element_position: int = 0
        first_element_position: int = None
        last_element: oe.Element = None
        for single_data in self._datasource_list:
            if isinstance(single_data._data, oe.Element) and single_data._data._stackable:
                if last_element is not None:
                    last_element << (single_data._data._position - last_element._position).getDuration()
                else:
                    first_element_position = element_position
                last_element = single_data._data
            element_position += 1
        # Add a Rest in the beginning if necessary
        if first_element_position is not None:
            first_element: oe.Element = self._datasource_list[first_element_position]._data
            if first_element._position != ra.Position():
                rest_length = ra.Duration(first_element._position)
                self._datasource_list.insert(first_element_position, od.DataSource( oe.Rest(rest_length) ))
        # Adjust last_element duration based on its Measure position
        if last_element is not None:
            last_element << (ra.Position(last_element % ra.Measures() + 1) - last_element._position).getDuration()
        return self

    def stack(self) -> 'Sequence':

        # Starts by sorting the self Elements list accordingly to their Tracks (all data is a Stackable Element)
        stackable_elements: list[oe.Element] = [
                single_data._data
                for single_data in self._datasource_list
                if isinstance(single_data._data, oe.Element) and single_data._data._stackable
            ]
        for index, single_element in enumerate(stackable_elements):
            if index > 0:
                single_element._position = stackable_elements[index - 1]._position + stackable_elements[index - 1]._duration  # Stacks on Element Duration
            else:
                single_element._position = ra.Position()   # everything starts at the beginning (0)!
        
        return self
    
    def tie(self, tied: bool = True) -> 'Sequence':
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Tiable):
                single_datasource._data << ou.Tied(tied)
        return self
    
    def slur(self, gate: float = 1.05) -> 'Sequence':
        last_element = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Tiable):
                if last_element is not None:
                    last_element << ra.Gate(gate)
                last_element = single_datasource._data
        return self
    
    def smooth(self) -> 'Sequence':
        last_note = None
        smooth_range = og.Pitch(ou.Key(12 // 2), -1)  # 6 chromatic steps
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Note):    # Only Note has single Pitch
                actual_note = single_datasource._data
                if last_note is not None:
                    while actual_note._pitch > last_note._pitch:
                        actual_note._pitch -= ou.Octave(1)
                    while actual_note._pitch < last_note._pitch:
                        actual_note._pitch += ou.Octave(1)
                    if actual_note._pitch - last_note._pitch > smooth_range:
                        actual_note._pitch -= ou.Octave(1)
                last_note = actual_note
        return self
    
    def split(self, position: ra.Position) -> tuple['Sequence', 'Sequence']:
        self_left: Sequence     = self.filter(of.Less(position))
        self_right: Sequence    = self.filter(of.GreaterEqual(position))
        return self_left, self_right

class Song(Container):
    def __init__(self, *operands):
        super().__init__()
        for single_operand in operands:
            if isinstance(single_operand, (Sequence, oe.Element)):
                if isinstance(single_operand, oe.Element):
                    single_operand = Sequence(single_operand)
                else:
                    single_operand = single_operand.copy()
                for single_sequence in self:
                    if isinstance(single_sequence, Sequence):
                        if single_sequence._midi_track == single_operand._midi_track:
                            single_sequence << single_sequence.__add__(single_operand)
                            continue
                self._datasource_list.append(od.DataSource( single_operand ))
        self._datasource_list = o.filter_list(self._datasource_list, lambda data_source: isinstance(data_source._data, (Sequence, od.Playlist)))

    def __getitem__(self, key: str | int) -> Sequence:
        if isinstance(key, str):
            for single_sequence in self:
                if isinstance(single_sequence, Sequence):   # Playlists aren't selectable by name !
                    if single_sequence._midi_track._name == key:
                        return single_sequence
            return ol.Null()
        return self._datasource_list[key]._data

    def __mod__(self, operand: any) -> any:
        match operand:
            case ou.MidiTrack():
                for single_sequence in self:
                    if isinstance(single_sequence, Sequence):
                        if single_sequence._midi_track == operand:
                            return single_sequence
                return ol.Null()
            case str():             return self[operand]
            case _:                 return super().__mod__(operand)

    def getPlaylist(self, position: ra.Position = None) -> list:
        play_list: list = []
        for single_sequence in self:
            if isinstance(single_sequence, (Sequence, od.Playlist)):
                play_list.extend(single_sequence.getPlaylist(position))
        return play_list

    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        midi_list: list = []
        for single_sequence in self:
            if isinstance(single_sequence, Sequence):   # Can't get Midilist from Playlist !
                midi_list.extend(single_sequence.getMidilist(midi_track, position))
        return midi_list

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Song':
        super().__lshift__(operand)
        self._datasource_list = o.filter_list(self._datasource_list, lambda data_source: isinstance(data_source._data, (Sequence, od.Playlist)))
        return self

    # operand is the pusher >>
    def __rrshift__(self, operand: o.Operand) -> 'Song':
        if isinstance(operand, (Sequence, oe.Element)):
            if isinstance(operand, oe.Element):
                operand = Sequence(operand) # Sequence() already does the copy
            else:
                operand = operand.copy()
            for single_sequence in self:
                if isinstance(single_sequence, Sequence):
                    if single_sequence._midi_track == operand._midi_track:
                        single_sequence << single_sequence.__rrshift__(operand)
                        return self
            self._datasource_list.append(od.DataSource( operand ))
        elif isinstance(operand, of.Frame):
            o.logging.warning(f"Frames don't work on Songs!")
        return self

    def __radd__(self, operand: Sequence | oe.Element) -> 'Song':
        if isinstance(operand, (Sequence, oe.Element)):
            if isinstance(operand, oe.Element):
                operand = Sequence(operand)
            else:
                operand = operand.copy()
            for single_sequence in self:
                if isinstance(single_sequence, Sequence):
                    if single_sequence._midi_track == operand._midi_track:
                        single_sequence << single_sequence.__radd__(operand)    # Where the difference lies!
                        return self
            self._datasource_list.append(od.DataSource( operand ))
        elif isinstance(operand, of.Frame):
            o.logging.warning(f"Frames don't work on Songs!")
        return self

    def __add__(self, operand: Sequence | oe.Element) -> 'Song':
        if isinstance(operand, (Sequence, oe.Element)):
            if isinstance(operand, oe.Element):
                operand = Sequence(operand) # Makes sure it becomes a Sequence
            else:
                operand = operand.copy()
            for single_sequence in self:
                if isinstance(single_sequence, Sequence):
                    if single_sequence._midi_track == operand._midi_track:
                        single_sequence << single_sequence.__add__(operand)     # Where the difference lies!
                        return self
            self._datasource_list.append(od.DataSource( operand ))
        elif isinstance(operand, od.Playlist):  # Adds Playlist right away!
            self._datasource_list.append(od.DataSource( operand ))
        elif isinstance(operand, of.Frame):
            o.logging.warning(f"Frames don't work on Songs!")
        return self

    def __sub__(self, operand: o.Operand) -> 'Song':
        if isinstance(operand, Sequence):
            for single_sequence_i in len(self._datasource_list):
                if isinstance(self._datasource_list[single_sequence_i]._data, Sequence):
                    if self._datasource_list[single_sequence_i]._data == operand:
                        del self._datasource_list[single_sequence_i]
        elif isinstance(operand, oe.Element):
            for single_sequence_i in len(self._datasource_list):
                if isinstance(self._datasource_list[single_sequence_i]._data, Sequence):
                    if self._datasource_list[single_sequence_i]._data == Sequence(operand):
                        del self._datasource_list[single_sequence_i]
        elif isinstance(operand, of.Frame):
            o.logging.warning(f"Frames don't work on Songs!")
        return self

    # # Multiply of song shall mean the number of loops
    # def __mul__(self, operand: o.Operand) -> 'Song':
    #     self_copy: Sequence = self.copy()
    #     for single_datasource in self_copy._datasource_list:
    #         if isinstance(single_datasource._data, Sequence): # Makes sure it's an Element
    #             single_datasource._data *= operand
    #     return self_copy
    
    # def __rmul__(self, operand: any) -> 'Song':
    #     return self.__mul__(operand)
