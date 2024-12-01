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
from typing import Union, TYPE_CHECKING
from fractions import Fraction
import json
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
import operand_time as ot
import operand_data as od
import operand_label as ol
import operand_generic as og
import operand_element as oe
import operand_frame as of
import operand_chaos as ch


class Container(o.Operand):
    def __init__(self, *operands):
        super().__init__()
        self._datasource_list: list[od.DataSource] = []
        self._datasource_iterator: int = 0
        for single_operand in operands:
            match single_operand:
                case Container():
                    self._datasource_list.extend(single_operand.copy() % od.DataSource())
                case list():
                    for operand in single_operand:
                        if isinstance(operand, o.Operand):
                            self._datasource_list.append(od.DataSource( operand.copy() ))
                        else:
                            self._datasource_list.append(od.DataSource( operand ))
                case o.Operand():
                    self._datasource_list.append(od.DataSource( single_operand.copy() ))
                case _:
                    self._datasource_list.append(od.DataSource( single_operand ))
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._datasource_iterator < len(self._datasource_list):
            single_datasource = self._datasource_list[self._datasource_iterator]
            self._datasource_iterator += 1
            return single_datasource._data  # It's the data that should be returned
        else:
            self._datasource_iterator = 0  # Reset to 0 when limit is reached
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
            case od.DataSource():   return self._datasource_list
            case Container():       return self.copy()
            case od.Getter():       return operand.get(self)
            case od.Process():      return self >> operand
            case list():
                operands: list[o.Operand] = []
                for single_datasource in self._datasource_list:
                    operands.append(self.deep_copy(single_datasource._data))
                return operands
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
        if type(self) == type(other):
            return self._datasource_list == other % od.DataSource()
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
        if nth > 0:
            index = nth - 1
            if len(self._datasource_list) > index:
                return self._datasource_list[index]._data
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
            case od.DataSource():
                match operand % o.Operand():
                    case list():        self._datasource_list = operand % o.Operand()
            case Container():
                super().__lshift__(operand)
                last_datasource: int = min(self.len(), operand.len())
                for datasource_i in range(last_datasource):
                    if isinstance(self._datasource_list[datasource_i]._data, o.Operand):
                        self._datasource_list[datasource_i]._data << operand._datasource_list[datasource_i]._data
                    else:
                        self._datasource_list[datasource_i]._data = operand._datasource_list[datasource_i]._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._datasource_list = []
                for single_operand in operand:
                    match single_operand:
                        case o.Operand():
                            self._datasource_list.append(od.DataSource( single_operand.copy() ))
                        case _:
                            self._datasource_list.append(od.DataSource( single_operand ))
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _: # Works for Frame too
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, o.Operand):
                        single_datasource._data << operand
        return self

    def copy(self, *parameters) -> 'Container':
        container_copy: Container = self.__class__()
        for single_datasource in self._datasource_list:
            container_copy._datasource_list.append( single_datasource.copy() )
        # COPY THE SELF OPERANDS RECURSIVELY
        if self._next_operand is not None:
            container_copy._next_operand = self._next_operand.copy()
        return container_copy << parameters
    
    def clear(self, *parameters) -> 'Container':
        self._datasource_list = []
        return super().clear(parameters)
    
    def sort(self, compare: o.Operand = None) -> 'Container':
        compare = ot.Position() if compare is None else compare
        for operand_i in range(self.len() - 1):
            sorted_list = True
            for operand_j in range(self.len() - 1 - operand_i):
                if self._datasource_list[operand_j]._data % compare > self._datasource_list[operand_j + 1]._data % compare:
                    temporary_operand = self._datasource_list[operand_j]._data
                    self._datasource_list[operand_j]._data = self._datasource_list[operand_j + 1]._data
                    self._datasource_list[operand_j + 1]._data = temporary_operand
                    sorted_list = False
            if sorted_list: break
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
        for operand_i in range(self.len() // 2):
            tail_operand = self._datasource_list[self.len() - 1 - operand_i]._data
            self._datasource_list[self.len() - 1 - operand_i]._data = self._datasource_list[operand_i]._data
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
                    self_copy._datasource_list.append(single_datasource.copy())
                for single_datasource in operand._datasource_list:
                    self_copy._datasource_list.append(single_datasource.copy())
                return self_copy
            case o.Operand():
                self_copy = self.copy()
                self_copy._datasource_list.append(od.DataSource( operand.copy() ))
                return self_copy
            case int() | ou.Integer(): # repeat n times the last argument if any
                self_copy: Container = self.copy()
                if len(self._datasource_list) > 0:
                    last_datasource = self._datasource_list[len(self._datasource_list) - 1]
                    while operand > 0:
                        self_copy._datasource_list.append(last_datasource.copy())
                        operand -= 1
                return self_copy
            case ol.Null(): return ol.Null()
            case _: return self.copy()
    
    def __radd__(self, operand: o.Operand) -> o.Operand:
        self_copy: Container = self.copy()
        match operand:
            case o.Operand():
                self_copy._datasource_list.insert(0, od.DataSource( operand.copy() ))
            case int(): # repeat n times the first argument if any
                if len(self._datasource_list) > 0:
                    first_datasource = self._datasource_list[0]
                    while operand > 0:
                        self_copy._datasource_list.insert(0, first_datasource.copy())
                        operand -= 1
            case ol.Null(): return ol.Null()
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Container':
        self_copy: Container = self.copy()
        match operand:
            case Container():
                # Exclude items based on equality (==) comparison
                self_copy._datasource_list = [
                        self_datasource.copy() for self_datasource in self._datasource_list
                        if all(self_datasource != operand_datasource for operand_datasource in operand)
                    ]
            case o.Operand():
                self_copy._datasource_list = [self_datasource for self_datasource in self._datasource_list if self_datasource._data != operand]
            case int(): # repeat n times the last argument if any
                if len(self._datasource_list) > 0:
                    while operand > 0 and len(self_copy._datasource_list) > 0:
                        self_copy._datasource_list.pop()
                        operand -= 1
            case ol.Null(): return ol.Null()
        return self_copy

    # multiply with a scalar 
    def __mul__(self, operand: o.Operand) -> 'Container':
        self_copy: Container = self.copy()
        match operand:
            case Container():
                ...
            case o.Operand():
                ...
            case int(): # repeat n times the last argument if any
                many_operands = self.__class__()    # with an empty list
                while operand > 0:
                    many_operands += self
                    operand -= 1
                return many_operands
            case ol.Null(): return ol.Null()
        return self_copy
    
    def __truediv__(self, operand: o.Operand) -> 'Container':
        self_copy: Container = self.copy()
        match operand:
            case Container():
                ...
            case o.Operand():
                ...
            case int(): # remove n last arguments if any
                if operand > 0:
                    elements_to_be_removed = round(1 - self_copy.len() / operand)
                    while elements_to_be_removed > 0:
                        self_copy._datasource_list.pop()
                        elements_to_be_removed -= 1
            case ol.Null(): return ol.Null()
        return self_copy

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
        self._track: og.Track       = og.Track()
        self._position: ot.Position = ot.Position(0)
        for single_operand in operands:
            match single_operand:
                case Sequence():
                    self._track << single_operand._track
                    self._position << single_operand._position
                case og.Track():
                    self._track = single_operand.copy()
                case ot.Position():
                    self._position = single_operand.copy()

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
                match operand % o.Operand():
                    case og.Track():        return self._track
                    case ou.Channel():      return self._track % od.DataSource( ou.Channel() )
                    case od.Device():       return self._track % od.DataSource( od.Device() )
                    case ot.Position():     return self._position
                    case _:                 return super().__mod__(operand)
            case og.Track():        return self._track.copy()
            case ou.Channel():      return self._track % ou.Channel()
            case od.Device():       return self._track % od.Device()
            case ot.Position():     return self._position.copy()
            case ot.Duration():       return self.duration()
                # total_length = ot.Duration()
                # for single_datasource in self._datasource_list:
                #     if isinstance(single_datasource._data, oe.Element):
                #         total_length += single_datasource._data % od.DataSource( ot.Duration() )
                # return total_length
            case _:                 return super().__mod__(operand)

    def duration(self) -> ot.Duration:
        total_length: ot.Duration = ot.Duration(0)
        if self.len() > 0:
            # Starts by sorting the self Elements list accordingly to their Tracks (all data is a Stackable Element)
            elements: list[oe.Element] = [
                    single_data._data
                    for single_data in self._datasource_list
                    if isinstance(single_data._data, oe.Element)
                ]
            position_min: ot.Position = elements[0]._position
            position_max: ot.Position = elements[0]._position
            for single_element in elements:
                if single_element._position < position_min:
                    position_min = single_element._position
                elif single_element._position > position_max:
                    position_max = single_element._position
            total_length << position_max - position_min
            # total_length << total_length % ra.Measure() + 1 # Rounded up Duration to Measures
        return total_length

    def start(self) -> ot.Position:
        if self.len() > 0:
            start_position: ot.Position = self._datasource_list[0]._data % ot.Position()
            for single_datasource in self._datasource_list:
                if single_datasource._data % ot.Position() < start_position:
                    start_position = single_datasource._data % ot.Position()
            return start_position.copy()
        return ot.Position(0)

    def end(self) -> ot.Position:
        if self.len() > 0:
            end_position: ot.Position = self._datasource_list[0]._data % ot.Position() + self._datasource_list[0]._data % ot.Duration()
            for single_datasource in self._datasource_list:
                if single_datasource._data % ot.Position() + single_datasource._data % ot.Duration() > end_position:
                    end_position = single_datasource._data % ot.Position() + single_datasource._data % ot.Duration()
            return end_position # already a copy (+)
        return ot.Position(0)
    
    if TYPE_CHECKING:
        from operand_element import Element

    def get_sequence_elements(self) -> list['Element']:
        sequence_elements: list[oe.Element] = []
        tied_notes: list[oe.Note] = []
        for single_datasource in self._datasource_list:   # Read only (extracts the play list)
            if isinstance(single_datasource._data, oe.Element):
                if isinstance(single_datasource._data, oe.Note) and single_datasource._data._tied:
                    tied_notes.append(single_datasource._data.copy())
                else:
                    sequence_elements.append(single_datasource._data)
        if len(tied_notes) > 0:
            tied_notes = sorted(tied_notes, key=lambda x: (id(x._track._track_data)))
            first_tied_note: oe.Note = tied_notes[0]
            for next_tied_note_i in range(1, len(tied_notes)):
                # Must be in sequence to be tied (FS - Finish to Start)!
                next_note_position: ot.Position = first_tied_note._position + first_tied_note._duration # Duration is particularly tricky
                if tied_notes[next_tied_note_i]._pitch == first_tied_note._pitch \
                    and tied_notes[next_tied_note_i]._track == first_tied_note._track \
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

    def getPlaylist(self, track: og.Track = None, position: ot.Position = None) -> list:
        track: og.Track = self._track if not isinstance(track, og.Track) else track
        position: ot.Position = self._position + (ot.Position(0) if not isinstance(position, ot.Position) else position)
        play_list = []
        for single_element in self.get_sequence_elements():
            play_list.extend(single_element.getPlaylist(track, position))
        return play_list

    def getMidilist(self, track: og.Track = None, position: ot.Position = None) -> list:
        track: og.Track = self._track if not isinstance(track, og.Track) else track
        position: ot.Position = self._position + (ot.Position(0) if not isinstance(position, ot.Position) else position)
        midi_list = []
        for single_element in self.get_sequence_elements():
            midi_list.extend(single_element.getMidilist(track, position))
        return midi_list

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["track"]    = self.serialize(self._track)
        serialization["parameters"]["position"] = self.serialize(self._position)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "track" in serialization["parameters"] and "position" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._track     = self.deserialize(serialization["parameters"]["track"])
            self._position  = self.deserialize(serialization["parameters"]["position"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Track():        self._track = operand % o.Operand()
                    case ou.Channel() | od.Device():
                                            self._track << od.DataSource( operand % o.Operand() )
                    case ot.Position():     self._position = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case Sequence():
                super().__lshift__(operand)
                self._datasource_list = []
                for single_element in operand:
                    if isinstance(single_element, oe.Element):
                        self._datasource_list.append(od.DataSource( single_element.copy() ))
                self._track << operand._track
                self._position << operand._position
            case og.Track() | ou.Channel() | od.Device():
                self._track << operand
            case ot.Position():
                self._position << operand
            case ot.Duration() | ra.NoteValue() | float() | Fraction():
                super().__lshift__(operand)
                self.stack()
            case ot.Position() | ra.TimeUnit():
                super().__lshift__(operand)
                self.link() # Maybe completely unnecessary
            case _: super().__lshift__(operand)
        return self

    def copy(self, *parameters) -> 'Sequence':
        sequence_copy: Sequence = super().copy(*parameters)
        sequence_copy._track << self._track
        sequence_copy._position << self._position
        return sequence_copy
    
    def reverse(self) -> 'Sequence':
        super().reverse()
        self.first() << self.last() % ot.Position()
        return self.stack()

    def link(self, and_join: bool = False) -> 'Sequence':
        self.sort()
        element_position: int = 0
        first_element_position: int = None
        last_element: oe.Element = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                if last_element is not None:
                    last_element << ot.Duration(single_datasource._data._position - last_element._position)
                else:
                    first_element_position = element_position
                last_element = single_datasource._data
            element_position += 1
        # Add a Rest in the beginning if necessary
        if first_element_position is not None:
            first_element: oe.Element = self._datasource_list[first_element_position]._data
            if first_element._position != ot.Position(0):
                rest_length = ot.Duration(first_element._position)
                self._datasource_list.insert(first_element_position, od.DataSource( oe.Rest(rest_length) ))
        # Adjust last_element duration based on its Measure position
        if last_element is not None:
            last_element << ot.Duration(ot.Position(last_element % ra.Measure() + 1) - last_element._position)
        if and_join:
            self << of.Get(ot.Duration())**ot.Duration()
        return self

    def join(self) -> 'Sequence':
        return self << of.Get(ot.Duration())**ot.Duration()

    def stack(self) -> 'Sequence':
        # Starts by sorting the self Elements list accordingly to their Tracks (all data is a Stackable Element)
        stackable_elements: list[oe.Stackable] = [
                single_data._data
                for single_data in self._datasource_list
                if isinstance(single_data._data, oe.Stackable)
            ]
        for single_element_i in range(len(stackable_elements)):
            single_element: oe.Stackable = stackable_elements[single_element_i]
            if single_element_i > 0:
                single_element._position = stackable_elements[single_element_i - 1]._position + stackable_elements[single_element_i - 1]._duration  # Stacks on Element Duration
            else:
                single_element._position = ot.Position(0)   # everything starts at the beginning (0)!
        return self
    
    def tie(self, tied: bool = True) -> 'Sequence':
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Note):
                single_datasource._data << ou.Tied(tied)
        return self
    
    def slur(self, gate: float = 1.05) -> 'Sequence':
        last_element = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Note):
                if last_element is not None:
                    last_element << ra.Gate(gate)
                last_element = single_datasource._data
        return self
    
    def smooth(self) -> 'Sequence':
        last_note = None
        smooth_range = og.Pitch(ou.Key(12 // 2), -1)  # 6 chromatic steps
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Note):
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

    # operand is the pusher >>
    def __rrshift__(self, operand: o.Operand) -> 'Sequence':
        self_copy: Sequence = self.copy()
        match operand:
            case ot.Duration() | ra.NoteValue():
                if self_copy.len() > 0:
                    self_copy._datasource_list[0]._data << self_copy._datasource_list[0]._data % ot.Position() + operand
            case ot.Position() | ra.TimeUnit():
                if self_copy.len() > 0:
                    self_copy._datasource_list[0]._data << operand
            case oe.Element():
                return self.__radd__(operand).stack()
            case Sequence():
                if self._track == operand._track:
                    operand_copy: Sequence = operand.copy()
                    last_position: ot.Position = operand_copy.sort().last() % od.DataSource( ot.Position() )
                    new_self_position: ot.Position = last_position % ra.Measure() + 1
                    self << of.Get(ot.Position())**of.Add(new_self_position) # WITHOUT OPERAND.COPY IT FAILS TEST 3.6
                    # return operand + (self + end_position)    # FAILS TEST 3.5
                    return (operand + self) # WITHOUT STACK IT FAILS TEST 3.5
                    # return (operand + self).stack()
                return Song(operand, self)
            case od.Playlist():
                return operand >> od.Playlist(self.getPlaylist(self._track, self._position))
            case tuple():
                return super().__rrshift__(operand)
        return self_copy.stack()

    def __add__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case Song():
                return operand + self   # Order is irrelevant on Song
            case Sequence():
                if self % og.Track() == operand % og.Track():
                    return Sequence(self, operand)
                return Song(self, operand)
            case Container():
                self_copy: Sequence = self.__class__()
                for single_datasource in self._datasource_list:
                    self_copy._datasource_list.append(single_datasource.copy())
                for single_datasource in operand._datasource_list:
                    if isinstance(operand, Sequence) or isinstance(single_datasource._data, oe.Element):
                        self_copy._datasource_list.append(single_datasource.copy())
                return self_copy
            case oe.Element():
                self._datasource_list.append(od.DataSource( operand.copy() ))
                return self
            case o.Operand() | int() | float() | Fraction():
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, oe.Element): # Makes sure it's an Element
                        single_datasource._data += operand
                return self
        return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case Container() | oe.Element():
                return super().__sub__(operand)
            case o.Operand() | int() | float() | Fraction():
                for single_datasource in self._datasource_list:
                    single_datasource._data << single_datasource._data - operand
                return self
        return super().__sub__(operand)

    # multiply with a scalar 
    def __mul__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case Sequence() | oe.Element():
                ...
            case o.Operand():
                for single_datasource in self._datasource_list:
                    single_datasource._data << single_datasource._data * operand
                return self
            case int():
                many_operands = self.__class__()    # empty list
                while operand > 0:
                    many_operands >>= self.copy()
                    operand -= 1
                return many_operands
        return super().__mul__(operand)
    
    def __rmul__(self, operand: any) -> 'Sequence':
        return self.__mul__(operand)
    
    def __truediv__(self, operand: o.Operand) -> 'Sequence':
        match operand:
            case Sequence() | oe.Element():
                ...
            case o.Operand():
                for single_datasource in self._datasource_list:
                    single_datasource._data << single_datasource._data / operand
                return self
            case int(): # Splits the total Duration by the integer
                start_position = self.start()
                sequence_length: ot.Duration = self.end() - start_position
                new_end_position: ot.Position = start_position + sequence_length / operand
                trimmed_self = self | of.Less(new_end_position)**o.Operand()
                return trimmed_self.copy()
        return super().__truediv__(operand)
    
    def __floordiv__(self, duration: ot.Duration) -> 'Sequence':
        if isinstance(duration, ra.TimeUnit):
            duration = ot.Duration() << duration
        match duration:
            case ot.Duration():
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, oe.Stackable):
                        single_datasource._data << duration
        return self.stack()

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
                        if single_sequence._track == single_operand._track:
                            single_sequence << single_sequence.__add__(single_operand)
                            continue
                self._datasource_list.append(od.DataSource( single_operand ))

    def __mod__(self, operand: any) -> any:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Track():
                        for sequence in self:
                            if isinstance(sequence, Sequence):
                                if sequence._track == operand % o.Operand():
                                    return sequence
                        return ol.Null()
                    case str():
                        return self % od.DataSource( og.Track(operand % o.Operand()) )
                    case _:                 return super().__mod__(operand)
            case og.Track():
                for sequence in self:
                    if isinstance(sequence, Sequence):
                        if sequence._track == operand:
                            return sequence.copy()
                return ol.Null()
            case str():
                return self % og.Track(operand)
            case _:                 return super().__mod__(operand)

    def getPlaylist(self, track: og.Track = None, position: ot.Position = None) -> list:
        play_list: list = []
        for single_sequence in self:
            if isinstance(single_sequence, Sequence):
                play_list.extend(single_sequence.getPlaylist(track, position))
        return play_list

    def getMidilist(self, track: og.Track = None, position: ot.Position = None) -> list:
        midi_list: list = []
        for single_sequence in self:
            if isinstance(single_sequence, Sequence):
                midi_list.extend(single_sequence.getMidilist(track, position))
        return midi_list

    def getSerialization(self) -> dict:
        import operand_staff as os
        serialization = super().getSerialization()
        serialization["parameters"]["staff"] = self.serialize(os.staff)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Song':
        import operand_staff as os
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"]):

            old_staff: os.Staff = os.staff
            if o.logging.getLogger().getEffectiveLevel() <= o.logging.DEBUG:
                old_staff = os.staff.copy()
            super().loadSerialization(serialization)
            # Can't be made equal (=), or else, all other references lose their staff!
            os.staff << self.deserialize(serialization["parameters"]["staff"])
            if o.logging.getLogger().getEffectiveLevel() <= o.logging.DEBUG and not os.staff == old_staff:
                o.logging.info(f"Deserialized staff is not identical to the original one!")
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
                    if single_sequence._track == operand._track:
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
                    if single_sequence._track == operand._track:
                        single_sequence << single_sequence.__radd__(operand)
                        return self
            self._datasource_list.append(od.DataSource( operand ))
        elif isinstance(operand, of.Frame):
            o.logging.warning(f"Frames don't work on Songs!")
        return self

    def __add__(self, operand: Sequence | oe.Element) -> 'Song':
        if isinstance(operand, (Sequence, oe.Element)):
            if isinstance(operand, oe.Element):
                operand = Sequence(operand)
            else:
                operand = operand.copy()
            for single_sequence in self:
                if isinstance(single_sequence, Sequence):
                    if single_sequence._track == operand._track:
                        single_sequence << single_sequence.__add__(operand)
                        return self
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
