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
                    case od.Getter() | od.Operation():
                        return self >> operand
                    case ch.Chaos():
                        return self.shuffle(operand)
                    case list():
                        return [
                            single_datasource._data
                                for single_datasource in self._datasource_list
                        ]
                    case _:
                        return super().__mod__(operand)
            case Container():
                return self.copy()
            case od.Getter() | od.Operation():
                return self.copy() >> operand
            case ch.Chaos():
                return self.copy().shuffle(operand)
            case list():
                return [
                    self.deep_copy(single_datasource._data)
                        for single_datasource in self._datasource_list
                ]
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
                self._next_operand = self.deep_copy(operand._next_operand)
            case od.DataSource():
                match operand._data:
                    case list():
                        for single_item in operand._data:
                            self._datasource_list.append(od.DataSource( single_item ))
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._datasource_list = [
                    od.DataSource( self.deep_copy(single_operand) )
                        for single_operand in operand
                ]
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _: # Works for Frame too
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, o.Operand):
                        single_datasource._data << operand
        return self

    def empty_copy(self, *parameters) -> 'Container':
        empty_copy: Container = self.__class__()
        # COPY THE SELF OPERANDS RECURSIVELY
        if self._next_operand:
            empty_copy._next_operand = self.deep_copy(self._next_operand)
        for single_parameter in parameters:
            empty_copy << single_parameter
        return empty_copy
    
    def clear(self, *parameters) -> 'Container':
        self._datasource_list = []
        return super().clear(parameters)
    
    def sort(self, compare: o.Operand = None) -> 'Container':
        compare = ra.Position() if compare is None else compare
        self._datasource_list.sort(key=lambda x: x._data % compare)
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
    
    # Avoids the costly copy of Container self doing +=
    def __iadd__(self, operand: any) -> 'Container':
        match operand:
            case Container():
                for single_datasource in operand._datasource_list:
                    self._datasource_list.append(self.deep_copy(single_datasource))
            case _:
                if isinstance(operand, od.DataSource):
                    self._datasource_list.append(od.DataSource( self.deep_copy( operand._data ) ))
                else:
                    self._datasource_list.append(od.DataSource( self.deep_copy( operand ) ))
        return self


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

    def __isub__(self, operand: o.Operand) -> 'Container':
        match operand:
            case Container():
                # Exclude items based on equality (==) comparison
                self._datasource_list = [
                        self_datasource.copy() for self_datasource in self._datasource_list
                        if all(self_datasource != operand_datasource for operand_datasource in operand._datasource_list)
                    ]
            case o.Operand():
                self._datasource_list = [self_datasource for self_datasource in self._datasource_list if self_datasource._data != operand]
            case int(): # repeat n times the last argument if any
                if len(self._datasource_list) > 0:
                    while operand > 0 and len(self._datasource_list) > 0:
                        self._datasource_list.pop()
                        operand -= 1
        return self

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
        self_copy: Container = self.copy()
        return self_copy.__itruediv__(operand)

    def __itruediv__(self, operand: o.Operand) -> 'Container':
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
        return self

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

class Clip(Container):  # Just a container of Elements
    def __init__(self, *operands):

        super().__init__(*operands)
        self._staff: og.Staff = og.defaults._staff.copy()
        self._midi_track: ou.MidiTrack  = ou.MidiTrack()
        self._position_beats: Fraction  = Fraction(0)   # in Beats

        for single_operand in operands:
            match single_operand:
                case Clip():
                    self._midi_track        << single_operand._midi_track
                    self._position_beats    = single_operand._position_beats
                case ou.MidiTrack():
                    self._midi_track        << single_operand
                case ra.Position():
                    self._position_beats    = self._staff.convertToPosition(single_operand)._rational
        self._datasource_list = o.filter_list(self._datasource_list, lambda data_source: isinstance(data_source._data, oe.Element))


    def __getitem__(self, index: int) -> oe.Element:
        return self._datasource_list[index]._data


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


    def __mod__(self, operand: any) -> any:
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
                    case ra.Position():     return operand << self._staff.convertToPosition(ra.Beats(self._position_beats))
                    case _:                 return super().__mod__(operand)
            case og.Staff():        return self._staff.copy()
            case ou.MidiTrack():    return self._midi_track.copy()
            case ra.Length():       return self.length()
            case ra.Duration():     return self.duration()
            case ra.Position():     return operand.copy() << self._staff.convertToPosition(ra.Beats(self._position_beats))
            case ra.Duration():     return self.duration()
            case ra.Tempo() | ou.KeySignature() | og.TimeSignature() | ra.BeatsPerMeasure() | ra.BeatNoteValue() | ra.StepsPerMeasure() | ra.StepsPerNote() \
                | ra.Quantization() | og.Scale() | ra.Measures() | ou.Measure() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | int() | float() | Fraction() | str():
                                    return self._staff % operand
            case _:                 return super().__mod__(operand)

    def start(self) -> ra.Position:
        start_beats: Fraction = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                position_beats: Fraction = single_datasource._data._position_beats
                if start_beats is None or position_beats < start_beats:   # Implicit conversion
                    start_beats = position_beats
        if start_beats:
            return self._staff.convertToPosition(ra.Beats(start_beats))
        return self._staff.convertToPosition(0)

    def finish(self) -> ra.Position:
        finish_beats: Fraction = Fraction(0)
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                single_element: oe.Element = single_datasource._data
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
        for single_datasource in self._datasource_list:   # Read only (extracts the play list)
            if isinstance(single_datasource._data, oe.Element):
                if isinstance(single_datasource._data, oe.Note) and single_datasource._data._tied:
                    tied_notes.append(single_datasource._data.copy())
                else:
                    clip_elements.append(single_datasource._data)
        if len(tied_notes) > 0: # Extends the root Note to accommodate all following Notes durations
            first_tied_note: oe.Note = tied_notes[0]
            for next_tied_note_i in range(1, len(tied_notes)):
                # Must be in clip to be tied (FS - Finish to Start)!
                next_note_position: Fraction = first_tied_note._position_beats \
                    + (first_tied_note % ra.Length())._rational
                if tied_notes[next_tied_note_i]._pitch == first_tied_note._pitch \
                    and tied_notes[next_tied_note_i]._channel == first_tied_note._channel \
                    and tied_notes[next_tied_note_i]._position_beats == next_note_position:
                    first_tied_note += tied_notes[next_tied_note_i]._duration_notevalue
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
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"] and "midi_track" in serialization["parameters"] and "position" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._staff         = self.deserialize(serialization["parameters"]["staff"])
            self._midi_track    = self.deserialize(serialization["parameters"]["midi_track"])
            self._position_beats      = self.deserialize(serialization["parameters"]["position"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Clip':
        match operand:
            case Clip():
                self._midi_track        << operand._midi_track
                self._position_beats    = operand._position_beats
                # BIG BOTTLENECK HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # Profiling time of 371 ms in a total of 2006 ms (18.48%) | Called 37 times (10.017 ms per call)
                self._datasource_list   = self.deep_copy( operand._datasource_list )
                # COPY THE SELF OPERANDS RECURSIVELY
                self._next_operand  = self.deep_copy(operand._next_operand)
                self.set_staff_reference(operand._staff)

            case od.DataSource():
                match operand._data:
                    case og.Staff():        self._staff = operand._data
                    case ou.MidiTrack():    self._midi_track = operand._data
                    case ra.Position():     self._position_beats = self._staff.convertToBeats(operand._data)._rational
                    case _:
                        super().__lshift__(operand)
                        self._datasource_list = o.filter_list(self._datasource_list, lambda data_source: isinstance(data_source._data, oe.Element))
            case og.Staff():
                self._staff << operand
            case ra.Tempo() | og.TimeSignature() | ra.Quantization():
                self._staff << operand
            case ou.MidiTrack():
                self._midi_track << operand
            # Use Frame objects to bypass this parameter into elements (Setting Position)
            case ra.Position():
                self._position_beats = self._staff.convertToBeats(operand)._rational
            case ra.TimeValue() | ou.TimeUnit():
                self._position_beats = self._staff.convertToBeats(operand)._rational
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._datasource_list = [
                    od.DataSource( self.deep_copy(single_operand) )
                        for single_operand in operand
                ]
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _: # Works for Frame too
                # If it comes from Song its destiny is the Clip
                if isinstance(operand, o.Operand) and isinstance(operand.get_source_operand(), Song):
                    operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
                    self << operand
                else:
                    for single_datasource in self._datasource_list:
                        single_datasource._data << operand
        return self

    def empty_copy(self, *parameters) -> 'Clip':
        empty_copy: Clip = super().empty_copy()
        empty_copy._midi_track      << self._midi_track
        empty_copy._position_beats  = self._position_beats
        empty_copy._staff           << self._staff
        for single_parameter in parameters:
            empty_copy << single_parameter
        return empty_copy
    
    # operand is the pusher >>
    def __rrshift__(self, operand: o.Operand) -> 'Clip':
        match operand:
            case Song():
                return operand + self
            case Clip():
                if operand.len() > 0:
                    left_end_position: ra.Position = operand.finish()
                    right_start_position: ra.Position = self.start()
                    length_shift: ra.Length = self._staff.convertToLength(left_end_position - right_start_position).roundMeasures()
                    # Convert Length to Position
                    add_position: ra.Position = ra.Position(length_shift)
                    right_clip: Clip = self + add_position  # Offsets the content and it's an implicit copy
                    added_clip: Clip = operand.copy()       # Preserves the left_clip configuration
                    added_clip._datasource_list.extend(right_clip._datasource_list)
                    return added_clip
                return self.copy()
            case oe.Element():
                element_length: ra.Length = self._staff.convertToLength( operand % ra.Length() )
                # Convert Length to Position
                add_position: ra.Position = ra.Position(element_length)
                right_clip: Clip = self + add_position  # Implicit copy
                right_clip._datasource_list.insert(0, od.DataSource( operand.copy() ))
                return right_clip
            case ra.Position() | ra.TimeValue() | ra.Duration() | ou.TimeUnit():
                self._position_beats += self._staff.convertToBeats(operand)._rational
                return self
            case od.Playlist():
                return operand >> od.Playlist(self.getPlaylist(self._position_beats))
            case tuple():
                return super().__rrshift__(operand)
        return self.copy()

    def __add__(self, operand: any) -> 'Clip':
        self_copy: Clip = self.copy()
        return self_copy.__iadd__(operand)
            
    # Avoids the costly copy of Track self doing +=
    def __iadd__(self, operand: any) -> 'Clip':
        match operand:
            case Song():
                # Song at the right must be a copy
                new_song: Song = operand.copy()
                # Inserts self content at the beginning of the Song
                new_song._datasource_list.insert(0, od.DataSource( self ))
                return new_song # Operand Song replaces self Clip
            case Clip():
                operand_data_list: list[oe.Element] = operand % list()
                # Does the needed position transformation, first and replicates to its elements (it may be from other clip)
                operand_position_beats: Fraction = self._staff.transformPosition(operand % ra.Position())._rational
                if operand_position_beats > self._position_beats:
                    for single_element in operand_data_list:
                        single_element += ra.Beats(operand_position_beats - self._position_beats)
                elif operand_position_beats < self._position_beats:
                    self += ra.Beats(self._position_beats - operand_position_beats) # NO IMPLICIT COPY
                    self._position_beats = operand_position_beats
                # operand is already a copy, let's take advantage of that, Using a generator (no square brackets)
                self._datasource_list.extend(
                    od.DataSource(single_element) for single_element in operand_data_list
                )
            case oe.Element():
                return super().__iadd__(operand)
            case list():
                for single_element in operand:
                    if isinstance(single_element, oe.Element):
                        self._datasource_list.append(od.DataSource( single_element.copy() ))
            case _:
                # If it comes from Song its destiny is the Clip
                if isinstance(operand, o.Operand) and isinstance(operand.get_source_operand(), Song):
                    operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
                    self += operand
                else:
                    for single_datasource in self._datasource_list:
                        single_datasource._data += operand
        return self

    def __sub__(self, operand: any) -> 'Clip':
        self_copy: Clip = self.copy()
        return self_copy.__isub__(operand)

    def __isub__(self, operand: any) -> 'Clip':
        match operand:
            case Song():
                operand -= self # Order is irrelevant in Song
                return operand 
            case oe.Element() | Container():
                return super().__isub__(operand)
            case _:
                # If it comes from Song its destiny is the Clip
                if isinstance(operand, o.Operand) and isinstance(operand.get_source_operand(), Song):
                    operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
                    self -= operand
                else:
                    for single_datasource in self._datasource_list:
                        single_datasource._data -= operand
        return self

    # multiply with a scalar
    def __mul__(self, operand: o.Operand) -> 'Clip':
        self_copy: Clip = self.copy()
        return self_copy.__imul__(operand)
    
    # in-place multiply with a scalar
    def __imul__(self, operand: o.Operand) -> 'Clip':
        match operand:
            case int() | float():
                if isinstance(operand, int):
                    self_length: ra.Length = self.length().roundMeasures()  # Length is NOT a Position
                else:
                    self_length: ra.Length = self.length()                  # Length is NOT a Position
                    operand = int(operand)
                if operand > 1:
                    # Convert self_length to a Position
                    add_position: ra.Position = ra.Position(self_length)
                    self_copy: Clip = self.copy()
                    for _ in range(operand - 2):
                        self_copy += add_position
                        self += self_copy   # implicit copy of self_copy
                    # Uses the last self_copy for the last iteration
                    self_copy += add_position
                    self._datasource_list.extend(
                        single_data_element for single_data_element in self_copy._datasource_list
                    )
                elif operand == 0:   # Must be empty
                    self._datasource_list = []  # Just to keep the self object
            case ou.TimeUnit():
                self_repeating: int = 0
                operand_beats: Fraction = self._staff.convertToBeats(operand)._rational
                self_beats: Fraction = self.length().roundMeasures()._rational  # Beats default unit
                if self_beats > 0:
                    self_repeating = operand_beats // self_beats
                self *= self_repeating
            case ra.TimeValue():
                self_repeating: float = 0.0
                self_length: Fraction = self.length() % operand % Fraction()
                if self_length > 0:
                    operand_length: Fraction = operand._rational
                    self_repeating: float = float( operand_length / self_length )
                self *= self_repeating
            case _:
                # If it comes from Song its destiny is the Clip
                if isinstance(operand, o.Operand) and isinstance(operand.get_source_operand(), Song):
                    operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
                    self *= operand
                else:
                    for single_datasource in self._datasource_list:
                        single_datasource._data *= operand
        return self
            
    def __rmul__(self, operand: any) -> 'Clip':
        return self.__mul__(operand)
    
    def __truediv__(self, operand: o.Operand) -> 'Clip':
        self_copy: Clip = self.copy()
        return self_copy.__itruediv__(operand)

    def __itruediv__(self, operand: o.Operand) -> 'Clip':
        match operand:
            case int():
                return super().__itruediv__(operand)
            case _:
                # If it comes from Song its destiny is the Clip
                if isinstance(operand, o.Operand) and isinstance(operand.get_source_operand(), Song):
                    operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
                    self /= operand
                else:
                    for single_datasource in self._datasource_list:
                        single_datasource._data /= operand
        return self

    def __or__(self, operand: any) -> 'Clip':
        match operand:
            case Clip():
                new_clip: Clip = self.__class__()
                new_clip._datasource_list.extend(self._datasource_list)
                new_clip._datasource_list.extend(operand._datasource_list)
                new_clip._midi_track        << self._midi_track
                new_clip._position_beats    = self._position_beats
                new_clip._staff             << self._staff
                return new_clip
            case _:
                return self.filter(operand)

    def filter(self, criteria: any) -> 'Clip':
        filtered_clip: Clip = self.__class__()
        filtered_clip._datasource_list = [self_datasource for self_datasource in self._datasource_list if self_datasource._data == criteria]
        filtered_clip._midi_track       << self._midi_track
        filtered_clip._position_beats   = self._position_beats
        filtered_clip._staff            = self._staff.copy()
        return filtered_clip

    def reverse(self) -> 'Clip':
        length_beats: Fraction = ra.Length( self.finish() ).roundMeasures()._rational # Rounded up Duration to next Measure
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                single_element: oe.Element = single_datasource._data
                duration_beats: Fraction = self._staff.convertToBeats(ra.Duration(single_element._duration_notevalue))
                single_element._position_beats = length_beats - (single_element._position_beats + duration_beats)
        return super().reverse()    # Reverses the list


    def extend(self, time_value: ra.TimeValue | ra.Duration) -> 'Clip':
        extended_clip: Clip = self.copy() << od.DataSource( self._datasource_list )
        while (extended_clip >> self).length() <= time_value:
            extended_clip >>= self
        self._datasource_list = extended_clip._datasource_list
        return self

    def trim(self, length: ra.Length) -> 'Clip':
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
        for single_data in self._datasource_list:
            if isinstance(single_data._data, oe.Element) and single_data._data._stackable:
                if last_element is not None:
                    last_element << self._staff.convertToDuration(ra.Beats(single_data._data._position_beats - last_element._position_beats))
                else:
                    first_element_index = element_index
                last_element = single_data._data
            element_index += 1
        # Add a Rest in the beginning if necessary
        if first_element_index is not None:
            first_element: oe.Element = self._datasource_list[first_element_index]._data
            if first_element._position_beats != 0:  # Not the first position
                rest_duration: ra.Duration = self._staff.convertToDuration(ra.Beats(first_element._position_beats))
                self._datasource_list.insert(first_element_index, od.DataSource( oe.Rest(rest_duration) ))
        # Adjust last_element duration based on its Measure position
        if last_element is not None:    # LAST ELEMENT ONLY!
            remaining_beats: Fraction = self._staff.convertToLength(ra.Beats(last_element._position_beats)).roundMeasures()._rational - last_element._position_beats
            last_element << self._staff.convertToDuration(ra.Beats(remaining_beats))
        return self

    def stack(self) -> 'Clip':

        # Starts by sorting the self Elements list accordingly to their Tracks (all data is a Stackable Element)
        stackable_elements: list[oe.Element] = [
                single_data._data
                for single_data in self._datasource_list
                if isinstance(single_data._data, oe.Element) and single_data._data._stackable
            ]
        for index, single_element in enumerate(stackable_elements):
            if index > 0:
                duration_beats: Fraction = self._staff.convertToBeats(ra.Duration(stackable_elements[index - 1]._duration_notevalue))._rational
                single_element._position_beats = stackable_elements[index - 1]._position_beats + duration_beats  # Stacks on Element Duration
            else:   # FIRST ELEMENT!
                single_element._position_beats = Fraction(0)   # everything starts at the beginning (0)!
        
        return self
    
    def tie(self, tied: bool = True) -> 'Clip':
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Tiable):
                single_datasource._data << ou.Tied(tied)
        return self
    
    def slur(self, gate: float = 1.05) -> 'Clip':
        last_element = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Tiable):
                if last_element is not None:
                    last_element << ra.Gate(gate)
                last_element = single_datasource._data
        return self
    
    def smooth(self) -> 'Clip':
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
    
    def split(self, position: ra.Position) -> tuple['Clip', 'Clip']:
        self_left: Clip     = self.filter(of.Less(position))
        self_right: Clip    = self.filter(of.GreaterEqual(position))
        return self_left, self_right

class Song(Container):
    def __init__(self, *operands):
        super().__init__()
        for single_operand in operands:
            match single_operand:
                case Song():
                    self._datasource_list.extend(
                        data_clip.copy() for data_clip in single_operand._datasource_list
                    )
                case Clip() | od.Playlist():
                    self._datasource_list.append(od.DataSource( single_operand.copy() ))


    def __getitem__(self, key: str | int) -> Clip:
        if isinstance(key, str):
            for single_clip in self:
                if isinstance(single_clip, Clip):   # Playlists aren't selectable by name !
                    if single_clip._midi_track._name == key:
                        return single_clip
            return ol.Null()
        return self._datasource_list[key]._data

    def __mod__(self, operand: any) -> any:
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

    def __lshift__(self, operand: o.Operand) -> 'Song':
        match operand:
            case Song():
                self._datasource_list.extend(
                    data_clip.copy() for data_clip in operand._datasource_list
                )
            case Clip():
                self._datasource_list.append( od.DataSource( operand.copy() ) )
            case o.Operand():   # Only propagates Operands!
                operand.set_source_operand(self)    # Set the operand source as this Song (self)
                for single_datasource in self._datasource_list: 
                    single_datasource._data << operand
        return self

    # operand is the pusher >>
    def __rrshift__(self, operand: o.Operand) -> 'Song':
        match operand:
            case Song():
                new_song: Song = Song()
                new_song._datasource_list = [
                    data_clip.copy() for data_clip in operand._datasource_list
                ]
                new_song._datasource_list.extend(
                    data_clip.copy() for data_clip in self._datasource_list
                )
                return new_song
            case Clip():
                new_song: Song = Song()
                new_song._datasource_list = [ od.DataSource( operand.copy() ) ]
                new_song._datasource_list.extend(
                    data_clip.copy() for data_clip in self._datasource_list
                )
                return new_song
        return self.copy()

    def __add__(self, operand: any) -> 'Song':
        return self.copy().__iadd__(operand)
            
    def __iadd__(self, operand: any) -> 'Song':
        match operand:
            case Song():
                self._datasource_list.extend(
                    data_clip.copy() for data_clip in operand._datasource_list
                )
            case Clip():
                self._datasource_list.append( od.DataSource( operand.copy() ) )
            case o.Operand():   # Only propagates Operands!
                operand.set_source_operand(self)    # Set the operand source as this Song (self)
                for single_datasource in self._datasource_list: 
                    single_datasource._data += operand
        return self

    def __sub__(self, operand: any) -> 'Song':
        return self.copy().__isub__(operand)
            
    def __isub__(self, operand: any) -> 'Song':
        match operand:
            case Song():
                self._datasource_list = [
                    data_clip for data_clip in self._datasource_list if data_clip not in operand._datasource_list
                ]
            case Clip():
                self._datasource_list = [
                    data_clip for data_clip in self._datasource_list if data_clip._data != operand
                ]
            case o.Operand():   # Only propagates Operands!
                operand.set_source_operand(self)    # Set the operand source as this Song (self)
                for single_datasource in self._datasource_list: 
                    single_datasource._data -= operand
        return self

    def __mul__(self, operand: any) -> 'Song':
        return self.copy().__imul__(operand)
            
    def __imul__(self, operand: any) -> 'Song':
        match operand:
            case o.Operand():   # Only propagates Operands!
                operand.set_source_operand(self)    # Set the operand source as this Song (self)
                for single_datasource in self._datasource_list: 
                    single_datasource._data *= operand
        return self

    def __truediv__(self, operand: any) -> 'Song':
        return self.copy().__itruediv__(operand)
            
    def __itruediv__(self, operand: any) -> 'Song':
        match operand:
            case o.Operand():   # Only propagates Operands!
                operand.set_source_operand(self)    # Set the operand source as this Song (self)
                for single_datasource in self._datasource_list: 
                    single_datasource._data /= operand
        return self

