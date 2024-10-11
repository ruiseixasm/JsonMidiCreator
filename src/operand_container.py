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
        self._operand_list = []
        for single_operand in operands:
            match single_operand:
                case Container():
                    self._operand_list.extend(single_operand.copy() % list())
                case list():
                    for operand in single_operand:
                        self._operand_list.append(operand.copy())
                case o.Operand():
                    self._operand_list.append(single_operand.copy())
                case _:
                    self._operand_list.append(single_operand)
        self._element_iterator = 0
        
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._element_iterator < len(self._operand_list):
            single_operand = self._operand_list[self._element_iterator]
            self._element_iterator += 1
            return single_operand
        else:
            self._element_iterator = 0  # Reset to 0 when limit is reached
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
            case od.DataSource():   return self._operand_list
            case list():
                operands: list[o.Operand] = []
                for single_operand in self._operand_list:
                    match single_operand:
                        case o.Operand():
                            operands.append(single_operand.copy())
                        case _:
                            operands.append(single_operand)
                return operands
            case Container():       return self.copy()
            case ol.Len():          return self.len()
            case ol.First():        return self.first()
            case ol.Last():         return self.last()
            case ou.Middle():       return self.middle(operand % int())
            case _:                 return super().__mod__(operand)

    def len(self) -> int:
        return len(self._operand_list)

    def __eq__(self, other_container: 'Container') -> bool:
        if type(self) == type(other_container):
            return self._operand_list == other_container % od.DataSource( list() )
            # When comparing lists containing objects in Python using the == operator,
            # Python will call the __eq__ method on the objects if it is defined,
            # rather than comparing their references directly.
            # If the __eq__ method is not defined for the objects, then the default behavior
            # (which usually involves comparing object identities, like references,
            # using the is operator) will be used.
        return False
    
    def first(self) -> o.Operand:
        if len(self._operand_list) > 0:
            return self._operand_list[0]
        return ol.Null()

    def last(self) -> o.Operand:
        if len(self._operand_list) > 0:
            return self._operand_list[len(self._operand_list) - 1]
        return ol.Null()

    def middle(self, nth: int) -> o.Operand:
        if nth > 0:
            index = nth - 1
            if len(self._operand_list) > index:
                return self._operand_list[index]
        return ol.Null()
 
    def getSerialization(self):
        operands_serialization = []
        for single_operand in self._operand_list:
            if isinstance(single_operand, o.Operand):
                operands_serialization.append(single_operand.getSerialization())
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

            operands = []
            operands_serialization = serialization["parameters"]["operands"]
            for single_operand_serialization in operands_serialization:
                if "class" in single_operand_serialization:
                    new_operand = self.getOperand(single_operand_serialization["class"])
                    if new_operand: operands.append(new_operand.loadSerialization(single_operand_serialization))
            self._operand_list = operands
        return self
       
    def copy(self) -> 'Container':
        container_copy: Container = self.__class__()
        for item in self._operand_list:
            match item:
                case o.Operand():
                    container_copy._operand_list.append( item.copy() )
                case _:
                    container_copy._operand_list.append( item )
        return container_copy
    
    def sort(self, compare: o.Operand = None) -> 'Container':
        compare = ot.Position() if compare is None else compare
        for operand_i in range(self.len() - 1):
            sorted_list = True
            for operand_j in range(self.len() - 1 - operand_i):
                if self._operand_list[operand_j] % compare > self._operand_list[operand_j + 1] % compare:
                    temporary_operand = self._operand_list[operand_j]
                    self._operand_list[operand_j] = self._operand_list[operand_j + 1]
                    self._operand_list[operand_j + 1] = temporary_operand
                    sorted_list = False
            if sorted_list: break
        return self

    def reverse(self) -> 'Container':
        for operand_i in range(self.len() // 2):
            tail_operand = self._operand_list[self.len() - 1 - operand_i]
            self._operand_list[self.len() - 1 - operand_i] = self._operand_list[operand_i]
            self._operand_list[operand_i] = tail_operand
        return self

    def __lshift__(self, operand: o.Operand) -> 'Container':
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case list():        self._operand_list = operand % o.Operand()
            case Container():
                last_item: int = min(self.len(), operand.len())
                for item_i in range(last_item):
                    self._operand_list[item_i] << operand._operand_list[item_i]
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                operands: list[o.Operand] = []
                for single_operand in operand:
                    match single_operand:
                        case o.Operand():
                            operands.append(single_operand.copy())
                        case _:
                            operands.append(single_operand)
                self._operand_list = operands
            case o.Operand() | int() | float(): # Works for Frame too
                for single_operand in self._operand_list:
                    single_operand << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __add__(self, operand: o.Operand) -> 'Container':
        match operand:
            case Container():
                self_copy: Container = self.__class__()
                self_copy << self._operand_list + operand._operand_list
                return self_copy
            case o.Operand():
                self_copy: Container = self.copy()
                self_copy._operand_list.append(operand.copy())
                return self_copy
            case int() | ou.Integer(): # repeat n times the last argument if any
                self_copy: Container = self.copy()
                operand_list = self_copy % list()
                if len(self._operand_list) > 0:
                    last_operand = self._operand_list[len(self._operand_list) - 1]
                    while operand > 0:
                        operand_list.append(last_operand.copy())
                        operand -= 1
                return self_copy
            case ol.Null(): return ol.Null()
        return self.copy()
    
    def __radd__(self, operand: o.Operand) -> o.Operand:
        self_copy: Container = self.copy()
        match operand:
            case o.Operand():
                self_copy._operand_list.insert(0, operand.copy())
            case int(): # repeat n times the first argument if any
                operand_list = self_copy % list()
                if len(self._operand_list) > 0:
                    first_operand = self._operand_list[0]
                    while operand > 0:
                        operand_list.insert(0, first_operand.copy())
                        operand -= 1
            case ol.Null(): return ol.Null()
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Container':
        self_copy: Container = self.copy()
        match operand:
            case Container():
                # Exclude items based on equality (==) comparison
                self_copy._operand_list = [
                        item for item in self_copy._operand_list
                        if all(item != operand_item for operand_item in operand)
                    ]
            case o.Operand():
                self_copy._operand_list = [item for item in self_copy._operand_list if item != operand]
            case int(): # repeat n times the last argument if any
                operand_list = self_copy % list()
                if len(self._operand_list) > 0:
                    last_operand = self._operand_list[len(self._operand_list) - 1]
                    while operand > 0 and len(operand_list) > 0:
                        operand_list.pop()
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
                many_operands = self.__class__()    # empty list
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
                    elements_list = self_copy % list()
                    elements_to_be_removed = round(1 - self_copy.len() / operand)
                    while elements_to_be_removed > 0:
                        elements_list.pop()
                        elements_to_be_removed -= 1
            case ol.Null(): return ol.Null()
        return self_copy

    def __pow__(self, operand: 'o.Operand') -> 'Container':
        for single_operand in self._operand_list:
            single_operand.__pow__(operand)
        return self

    def __or__(self, operand: any) -> 'Container':
        new_container: Container = self.__class__()
        match operand:
            case Container():
                new_container._operand_list.extend(self._operand_list)
                new_container._operand_list.extend(operand._operand_list)
            case _:
                new_container._operand_list = [item for item in self._operand_list if item == operand]
        return new_container

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
            case ol.Start():        return self.start()
            case ol.End():          return self.end()
            case ot.Length():
                import operand_element as oe
                total_length = ot.Length()
                for elem in self._operand_list:
                    if isinstance(elem, oe.Element):
                        total_length += elem % od.DataSource( ot.Length() )
                return total_length
            case _:                 return super().__mod__(operand)

    def start(self) -> ot.Position:
        if self.len() > 0:
            start_position: ot.Position = self._operand_list[0] % ot.Position()
            for single_element in self._operand_list:
                if single_element % ot.Position() < start_position:
                    start_position = single_element % ot.Position()
            return start_position.copy()
        return ol.Null()

    def end(self) -> ot.Position:
        if self.len() > 0:
            end_position: ot.Position = self._operand_list[0] % ot.Position() + self._operand_list[0] % ot.Length()
            for single_operand in self._operand_list:
                if single_operand % ot.Position() + single_operand % ot.Length() > end_position:
                    end_position = single_operand % ot.Position() + single_operand % ot.Length()
            return end_position # already a copy (+)
        return ol.Null()

    def getPlaylist(self, position: ot.Position = None):
        import operand_element as oe
        play_list = []
        for single_operand in self._operand_list:   # Read only (extracts the play list)
            if isinstance(single_operand, oe.Element):
                play_list.extend(single_operand.getPlaylist(position))
        return play_list

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Sequence':
        match operand:
            case tuple():
                last_item: int = min(self.len(), len(operand))
                for item_i in range(last_item):
                    self._operand_list[item_i] << operand[item_i]
            case _: super().__lshift__(operand)
        return self

    def reverse(self) -> 'Sequence':
        super().reverse()
        self.first() << self.last() % ot.Position()
        return self.stack()

    def link(self) -> 'Sequence':
        import operand_element as oe
        self.sort()
        last_element = None
        for elem in self._operand_list:
            if isinstance(elem, oe.Element):
                if last_element is not None:
                    last_element << ot.Length(elem % od.DataSource( ot.Position() ) - last_element % od.DataSource( ot.Position() ))
                last_element = elem
        return self

    def stack(self) -> 'Sequence':
        import operand_element as oe
        last_position = None
        last_length = None
        for single_element in self._operand_list:
            if last_position is not None:
                last_position += last_length
                single_element << last_position
            else:
                last_position = single_element._position
            last_length = single_element._length
        return self

    # operand is the pusher
    def __rrshift__(self, operand: o.Operand) -> 'Sequence':
        import operand_element as oe
        self_copy: Sequence = self.copy()
        match operand:
            case ot.Position():
                if self_copy.len() > 0:
                    self_copy._operand_list[0] << operand
            case ot.Length():
                if self_copy.len() > 0:
                    self_copy._operand_list[0] << self_copy._operand_list[0] % ot.Position() + operand
            case oe.Element() | Sequence():
                return (operand + self).stack()
            case tuple():
                # Apply >> sequentially across the elements in the tuple
                result = operand[0]  # Start with the first element
                for elem in operand[1:]:
                    if isinstance(elem, o.Operand):
                        result >>= elem  # Chain elements in the tuple
                return result >> self
        return self_copy.stack()

    def __add__(self, operand: o.Operand) -> 'Sequence':
        import operand_element as oe
        match operand:
            case Sequence() | oe.Element():
                return super().__add__(operand)
            case Container():
                last_item: int = min(self.len(), operand.len())
                for item_i in range(last_item):
                    self._operand_list[item_i] += operand._operand_list[item_i]
                return self
            case tuple():
                last_item: int = min(self.len(), len(operand))
                for item_i in range(last_item):
                    self._operand_list[item_i] << self._operand_list[item_i] + operand[item_i]
                return self
            case o.Operand() | int() | float() | Fraction():
                for single_operand in self._operand_list:
                    single_operand << single_operand + operand
                return self
        return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'Sequence':
        import operand_element as oe
        match operand:
            case Sequence() | oe.Element():
                return super().__sub__(operand)
            case Container():
                last_item: int = min(self.len(), operand.len())
                for item_i in range(last_item):
                    self._operand_list[item_i] -= operand._operand_list[item_i]
                return self
            case tuple():
                last_item: int = min(self.len(), len(operand))
                for item_i in range(last_item):
                    self._operand_list[item_i] << self._operand_list[item_i] - operand[item_i]
                return self
            case o.Operand() | int() | float() | Fraction():
                for single_operand in self % od.DataSource( list() ):
                    single_operand << single_operand - operand
                return self
        return super().__sub__(operand)

    # multiply with a scalar 
    def __mul__(self, operand: o.Operand) -> 'Sequence':
        import operand_element as oe
        match operand:
            case Sequence() | oe.Element():
                ...
            case o.Operand():
                for single_operand in self._operand_list:
                    single_operand << single_operand * operand
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
                for single_operand in self._operand_list:
                    single_operand << single_operand / operand
                return self
            case int(): # Splits the total Length by the integer
                start_position = self.start()
                sequence_length: ot.Length = self.end() - start_position
                new_end_position: ot.Position = start_position + sequence_length / operand
                trimmed_self = self | of.Lower(new_end_position)**o.Operand()
                return trimmed_self.copy()
        return super().__truediv__(operand)
    
    def __floordiv__(self, length: ot.Length) -> 'Sequence':
        if isinstance(length, ro.TimeUnit):
            length = ot.Length() << length
        match length:
            case ot.Length():
                import operand_element as oe
                for single_operand in self._operand_list:
                    if isinstance(single_operand, oe.Element):
                        single_operand << length
        return self.stack()
