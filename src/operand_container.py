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
from typing import Union
from fractions import Fraction
import json
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ro
import operand_time as ot
import operand_data as od
import operand_label as ol
import operand_generic as og
import operand_frame as of


class Container(o.Operand):
    def __init__(self, *operands):
        super().__init__()
        self._datasource_list: list[od.DataSource] = []
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
        self._datasource_iterator = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._datasource_iterator < len(self._datasource_list):
            single_datasource = self._datasource_list[self._datasource_iterator]
            self._datasource_iterator += 1
            return single_datasource
        else:
            self._datasource_iterator = 0  # Reset to 0 when limit is reached
            raise StopIteration

    def __mod__(self, operand: list) -> list:
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
            case ol.Getter():       return operand.get(self)
            case list():
                operands: list[o.Operand] = []
                for single_datasource in self._datasource_list:
                    match single_datasource._data:
                        case o.Operand():
                            operands.append(single_datasource._data.copy())
                        case _:
                            operands.append(single_datasource._data)
                return operands
            case _:
                return self.filter(operand)   # NEEDS AN ALTERNATIVE WITH SAME PRIORITY (NEW FILTER CLASS ???)

    def len(self) -> int:
        return len(self._datasource_list)

    def __eq__(self, other_container: 'Container') -> bool:
        if type(self) == type(other_container):
            return self._datasource_list == other_container % od.DataSource()
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
 
    def getSerialization(self):
        operands_serialization = []
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, o.Operand):
                operands_serialization.append(single_datasource._data.getSerialization())
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "operands": operands_serialization
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        import operand_element as oe
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "operands" in serialization["parameters"]):

            self._datasource_list = []
            operands_serialization = serialization["parameters"]["operands"]
            for single_operand_serialization in operands_serialization:
                if "class" in single_operand_serialization:
                    new_operand = self.getOperand(single_operand_serialization["class"])
                    if new_operand: self._datasource_list.append(od.DataSource( new_operand.loadSerialization(single_operand_serialization) ))
        return self
       
    def copy(self) -> 'Container':
        container_copy: Container = self.__class__()
        for single_datasource in self._datasource_list:
            container_copy._datasource_list.append( single_datasource.copy() )
        return container_copy
    
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

    def __lshift__(self, operand: o.Operand) -> 'Container':
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case list():        self._datasource_list = operand % o.Operand()
            case Container():
                last_datasource: int = min(self.len(), operand.len())
                for datasource_i in range(last_datasource):
                    if isinstance(self._datasource_list[datasource_i]._data, o.Operand):
                        self._datasource_list[datasource_i]._data << operand._datasource_list[datasource_i]._data
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
            case _: # Works for Frame too
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, o.Operand):
                        single_datasource._data << operand
        return self

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

    def __mod__(self, operand: list) -> list:
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
            case od.DataSource():   return super().__mod__(operand)
            case ot.Length():
                import operand_element as oe
                total_length = ot.Length()
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, oe.Element):
                        total_length += single_datasource._data % od.DataSource( ot.Length() )
                return total_length
            case _:                 return super().__mod__(operand)

    def start(self) -> ot.Position:
        if self.len() > 0:
            start_position: ot.Position = self._datasource_list[0]._data % ot.Position()
            for single_datasource in self._datasource_list:
                if single_datasource._data % ot.Position() < start_position:
                    start_position = single_datasource._data % ot.Position()
            return start_position.copy()
        return ol.Null()

    def end(self) -> ot.Position:
        if self.len() > 0:
            end_position: ot.Position = self._datasource_list[0]._data % ot.Position() + self._datasource_list[0]._data % ot.Length()
            for single_datasource in self._datasource_list:
                if single_datasource._data % ot.Position() + single_datasource._data % ot.Length() > end_position:
                    end_position = single_datasource._data % ot.Position() + single_datasource._data % ot.Length()
            return end_position # already a copy (+)
        return ol.Null()

    def getPlaylist(self, position: ot.Position = None):
        import operand_element as oe
        play_list = []
        for single_datasource in self._datasource_list:   # Read only (extracts the play list)
            if isinstance(single_datasource._data, oe.Element):
                play_list.extend(single_datasource._data.getPlaylist(position))
        return play_list

    # CHAINABLE OPERATIONS

    def reverse(self) -> 'Sequence':
        super().reverse()
        self.first() << self.last() % ot.Position()
        return self.stack()

    def link(self, and_join: bool = False) -> 'Sequence':
        import operand_element as oe
        self.sort()
        last_element = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                if last_element is not None:
                    last_element << ot.Length(single_datasource._data % od.DataSource( ot.Position() ) - last_element % od.DataSource( ot.Position() ))
                last_element = single_datasource._data
        # Adjust last_element length based on its Measure position
        if last_element is not None:
            last_element << ot.Length(ot.Position(last_element % ro.Measure() + 1) - last_element % od.DataSource( ot.Position() ))
        if and_join:
            self << of.Get(ot.Length())**ot.Duration()
        return self

    def join(self) -> 'Sequence':
        return self << of.Get(ot.Length())**ot.Duration()

    def stack(self) -> 'Sequence':
        import operand_element as oe
        last_position = None
        last_length = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Element):
                if last_position is not None:
                    last_position += last_length
                    single_datasource._data << last_position
                else:
                    last_position = single_datasource._data._position
                last_length = single_datasource._data._length
        return self
    
    def tie(self) -> 'Sequence':
        import operand_element as oe
        last_element = None
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Note):
                if last_element is not None:
                    if single_datasource._data._key_note == last_element._key_note:
                        last_element << ro.Gate(1.0)
                last_element = single_datasource._data
        return self
    
    def smooth(self) -> 'Sequence':
        import operand_element as oe
        last_note = None
        smooth_range = og.KeyNote(ou.Key(12 // 2), -1)  # 6 chromatic steps
        for single_datasource in self._datasource_list:
            if isinstance(single_datasource._data, oe.Note):
                actual_note = single_datasource._data
                if last_note is not None:
                    while actual_note._key_note > last_note._key_note:
                        actual_note._key_note -= ou.Octave(1)
                    while actual_note._key_note < last_note._key_note:
                        actual_note._key_note += ou.Octave(1)
                    if actual_note._key_note - last_note._key_note > smooth_range:
                        actual_note._key_note -= ou.Octave(1)
                last_note = actual_note
        return self

    # operand is the pusher
    def __rrshift__(self, operand: o.Operand) -> 'Sequence':
        import operand_element as oe
        self_copy: Sequence = self.copy()
        match operand:
            case ot.Length() | ro.NoteValue():
                if self_copy.len() > 0:
                    self_copy._datasource_list[0]._data << self_copy._datasource_list[0]._data % ot.Position() + operand
            case ot.Position() | ro.TimeUnit():
                if self_copy.len() > 0:
                    self_copy._datasource_list[0]._data << operand
            case oe.Element() | Sequence():
                return (operand + self).stack()
            case od.Playlist():
                return operand >> od.Playlist(self.getPlaylist())
            case tuple():
                return super().__rrshift__(operand)
        return self_copy.stack()

    def __add__(self, operand: o.Operand) -> 'Sequence':
        import operand_element as oe
        match operand:
            case Sequence() | oe.Element():
                return super().__add__(operand)
            case Container():
                last_datasource: int = min(self.len(), operand.len())
                for datasource_i in range(last_datasource):
                    self._datasource_list[datasource_i]._data += operand._datasource_list[datasource_i]._data
                return self
            case o.Operand() | int() | float() | Fraction():
                for single_datasource in self._datasource_list:
                    single_datasource._data << single_datasource._data + operand
                return self
        return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'Sequence':
        import operand_element as oe
        match operand:
            case Sequence() | oe.Element():
                return super().__sub__(operand)
            case Container():
                last_datasource: int = min(self.len(), operand.len())
                for datasource_i in range(last_datasource):
                    self._datasource_list[datasource_i]._data -= operand._datasource_list[datasource_i]._data
                return self
            case o.Operand() | int() | float() | Fraction():
                for single_datasource in self._datasource_list:
                    single_datasource._data << single_datasource._data - operand
                return self
        return super().__sub__(operand)

    # multiply with a scalar 
    def __mul__(self, operand: o.Operand) -> 'Sequence':
        import operand_element as oe
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
        import operand_element as oe
        match operand:
            case Sequence() | oe.Element():
                ...
            case o.Operand():
                for single_datasource in self._datasource_list:
                    single_datasource._data << single_datasource._data / operand
                return self
            case int(): # Splits the total Length by the integer
                start_position = self.start()
                sequence_length: ot.Length = self.end() - start_position
                new_end_position: ot.Position = start_position + sequence_length / operand
                trimmed_self = self | of.Less(new_end_position)**o.Operand()
                return trimmed_self.copy()
        return super().__truediv__(operand)
    
    def __floordiv__(self, length: ot.Length) -> 'Sequence':
        if isinstance(length, ro.TimeUnit):
            length = ot.Length() << length
        match length:
            case ot.Length():
                import operand_element as oe
                for single_datasource in self._datasource_list:
                    if isinstance(single_datasource._data, oe.Element):
                        single_datasource._data << length
        return self.stack()

class Stack(ol.Label):
    def __rrshift__(self, operand: any) -> Sequence:
        if isinstance(operand, Sequence):
            return operand.stack()
        else:
            return super().__rrshift__(operand)
