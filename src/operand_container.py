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
import json
import enum
# Json Midi Creator Libraries
import creator as c
from operand import Operand

import operand_unit as ou
import operand_value as ov
import operand_time as ot
import operand_data as od
import operand_label as ol
import operand_generic as og
import operand_frame as of

class Container(Operand):
    def __init__(self, *operands):
        self._operand_list = []
        for single_operand in operands:
            match single_operand:
                case list():
                    self._operand_list.extend(single_operand)
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

    def len(self) -> int:
        return len(self._operand_list)

    def __mod__(self, operand: list) -> list:
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case list():            return self._operand_list
            case ol.Null() | None:  return ol.Null()
            case _:                 return self

    def firstOperand(self) -> Operand:
        if len(self._operand_list) > 0:
            return self._operand_list[0]
        return ol.Null()

    def lastOperand(self) -> Operand:
        if len(self._operand_list) > 0:
            return self._operand_list[len(self._operand_list) - 1]
        return ol.Null()
 
    def getSerialization(self):
        operands_serialization = []
        for single_operand in self % list():
            operands_serialization.append(single_operand.getSerialization())
        return {
            "class": self.__class__.__name__,
            "operands": operands_serialization
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "operands" in serialization):

            operands = []
            multi_elements_serialization = serialization["operands"]
            for single_operand in multi_elements_serialization:
                class_name = single_operand["class"]
                operands.append(globals()[class_name]().loadSerialization(single_operand))

            self._operand_list = operands
        return self
       
    def copy(self) -> 'Container':
        many_operands: list[Operand] = []
        for single_operand in self._operand_list:
            many_operands.append(single_operand.copy())
        return self.__class__(many_operands)

    def __lshift__(self, operand: Operand) -> 'Container':
        match operand:
            case Container():
                self._operand_list = operand % list()
            case list():
                self._operand_list = operand
            case Operand():
                for single_operand in self._operand_list:
                    single_operand << operand
            case od.Load():
                serialization = c.loadJsonMidiCreator(operand % str())
                self.loadSerialization(serialization)
            case Chain():
                for single_operand in operand:
                    self << single_operand
        return self

    # operand is the pusher
    def __rrshift__(self, other_operand: Operand) -> Operand:
        return self

    def __add__(self, operand: Operand) -> 'Sequence':
        import operand_element as oe
        self_copy = self.copy()
        match operand:
            case Sequence():
                return Sequence(self.copy() % list() + operand.copy() % list())
            case oe.Element():
                return Sequence(self.copy() % list() + [operand.copy()])
            case Operand():
                operand_list = self_copy % list()
                for single_operand in operand_list:
                    single_operand << single_operand + operand
            case int(): # repeat n times the last argument if any
                operand_list = self_copy % list()
                if len(self._operand_list) > 0:
                    last_operand = self._operand_list[len(self._operand_list) - 1]
                    while operand > 0:
                        operand_list.append(last_operand.copy())
                        operand -= 1
            case ol.Null(): return ol.Null()
        return self_copy

    def __sub__(self, operand: Operand) -> 'Sequence':
        import operand_element as oe
        self_copy = self.copy()
        match operand:
            case Sequence():
                return Sequence(self.copy() % list() - operand.copy() % list())
            case oe.Element():
                return Sequence(self.copy() % list() - [operand.copy()])
            case Operand():
                operand_list = self_copy % list()
                for single_operand in operand_list:
                    single_operand << single_operand - operand
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
    def __mul__(self, operand: Operand) -> 'Sequence':
        import operand_element as oe
        self_copy = self.copy()
        match operand:
            case Sequence():
                return self_copy
            case oe.Element():
                return self_copy
            case Operand():
                operand_list = self_copy % list()
                for single_operand in operand_list:
                    single_operand << single_operand * operand
            case int(): # repeat n times the last argument if any
                many_operands = Sequence()    # empty list
                while operand > 0:
                    many_operands += self
                    operand -= 1
                return many_operands
            case ol.Null(): return ol.Null()
        return self_copy
    
    def __truediv__(self, operand: Operand) -> 'Sequence':
        import operand_element as oe
        self_copy = self.copy()
        match operand:
            case Sequence():
                return self_copy
            case oe.Element():
                return self_copy
            case Operand():
                elements_list = self_copy % list()
                for single_operand in elements_list:
                    single_operand << single_operand / operand
            case int(): # remove n last arguments if any
                if operand > 0:
                    elements_list = self_copy % list()
                    elements_to_be_removed = round(1 - self_copy.len() / operand)
                    while elements_to_be_removed > 0:
                        elements_list.pop()
                        elements_to_be_removed -= 1
            case ol.Null(): return ol.Null()
        return self_copy
    
    def __floordiv__(self, length: ot.Length) -> 'Sequence':
        if isinstance(length, ov.TimeUnit):
            length = ot.Length() << length
        match length:
            case ot.Length():
                import operand_element as oe
                starting_position = None
                for single_operand in self._operand_list:
                    if isinstance(single_operand, oe.Element):
                        if starting_position is None:
                            starting_position = single_operand % ot.Position()
                        else:
                            starting_position += length
                            single_operand << ot.Position() << starting_position
        return self

class Sequence(Container):  # Just a container of Elements
    def __init__(self, *operands):
        super().__init__(*operands)

    def getLastPosition(self) -> ot.Position:
        last_position: ot.Position = ot.Position()
        for single_operand in self._operand_list:
            if single_operand % ot.Position() > last_position:
                last_position = single_operand % ot.Position()
        return last_position

    def getPlayList(self, position: ot.Position = None):
        import operand_element as oe
        play_list = []
        for single_operand in self % list():
            if isinstance(single_operand, oe.Element) or isinstance(single_operand, Sequence):
                play_list.extend(single_operand.getPlayList(position))
        return play_list

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: Operand) -> Operand:
        self_first_element = self.firstOperand()
        if type(self_first_element) != ol.Null:
            import operand_element as oe
            match operand:
                case ol.Null(): pass
                case Sequence():
                    other_last_element = self.lastOperand()
                    if type(other_last_element) != ol.Null:
                        other_last_element >> self_first_element
                case oe.Element(): operand % ot.Position() + operand % ot.Length() >> self_first_element
                case ot.Position() | ot.Length(): operand >> self_first_element
            for single_element_i in range(1, len(self._operand_list)):
                self._operand_list[single_element_i - 1] >> self._operand_list[single_element_i]
        return self

class Chain(Container):
    def __init__(self, *operands):
        multi_operands = []
        if operands is not None:
            for single_operand in operands:
                match single_operand:
                    case Operand(): multi_operands.append(single_operand)
                    case list():    multi_operands.extend(single_operand)
        super().__init__(multi_operands)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: Operand) -> 'Chain':
        match operand:
            case of.Frame():        self << (operand & self)
            case Chain():           self._operand_list = operand % list()
            case Operand():         self._operand_list.append(operand)
            case list():            self._operand_list.extend(operand)
        return self
