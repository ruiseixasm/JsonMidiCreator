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
from creator import *
from operand import Operand

import operand_unit as ou
import operand_length as ol
import operand_data as od
import operand_tag as ot
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
    
    def len(self) -> int:
        return len(self._operand_list)

    def __next__(self):
        if self._element_iterator < len(self._operand_list):
            single_element = self._operand_list[self._element_iterator]
            self._element_iterator += 1
            return single_element
        else:
            self._element_iterator = 0  # Reset to 0 when limit is reached
            raise StopIteration

    def __mod__(self, operand: list) -> list:
        if operand.__class__ == list:
            return self._operand_list
        return []

    def firstOperand(self) -> Operand:
        if len(self._operand_list) > 0:
            return self._operand_list[0]
        return ot.Null()

    def lastOperand(self) -> Operand:
        if len(self._operand_list) > 0:
            return self._operand_list[len(self._operand_list) - 1]
        return ot.Null()
 
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
            for single_element in multi_elements_serialization:
                class_name = single_element["class"]
                operands.append(globals()[class_name]().loadSerialization(single_element))

            self._operand_list = operands
        return self
       
    def copy(self) -> 'Container':
        import operand_element as oe
        multi_elements: list[Operand] = []
        for single_operand in self._operand_list:
            multi_elements.append(single_operand.copy())
        return self.__class__(multi_elements)

    def __lshift__(self, operand: Operand) -> 'Container':
        match operand:
            case list():
                self._operand_list = operand
            case Container():
                self._operand_list = operand % list()
            case Operand():
                for single_operand in self._operand_list:
                    single_operand << operand
        return self

    def __rshift__(self, operand: 'Operand') -> 'MultiElements':
        match operand:
            case ot.Print():
                serialized_json_str = json.dumps(self.getSerialization())
                json_object = json.loads(serialized_json_str)
                json_formatted_str = json.dumps(json_object, indent=4)
                print(json_formatted_str)
                return self
            case _: return operand.__rrshift__(self)

    def __rrshift__(self, other_operand: Operand) -> Operand:
        return self

class MultiElements(Container):  # Just a container of Elements
    def __init__(self, *elements):
        import operand_element as oe
        multi_elements = []
        if multi_elements is not None:
            for single_element in elements:
                if isinstance(single_element, oe.Element):
                    multi_elements.append(single_element)
                elif isinstance(single_element, list) and all(isinstance(elem, oe.Element) for elem in single_element):
                    multi_elements.extend(single_element)
        super().__init__(multi_elements)
        self._selection: of.Selection = None

    def getLastPosition(self) -> ol.Position:
        last_position: ol.Position = ol.Position()
        for single_element in self._operand_list:
            if single_element % ol.Position() > last_position:
                last_position = single_element % ol.Position()
        return last_position

    def getPlayList(self, position: ol.Position = None):
        import operand_element as oe
        play_list = []
        for single_element in self % list():
            if isinstance(single_element, oe.Element):
                play_list.extend(single_element.getPlayList(position))
        return play_list

    # CHAINABLE OPERATIONS

    def __rshift__(self, operand: 'Operand') -> 'MultiElements':
        match operand:
            case ou.Play():
                jsonMidiPlay(self.getPlayList(), operand % int())
                return self
            case od.Save():
                saveJsonMidiCreator(self.getSerialization(), operand % str())
                return self
            case od.Export():
                saveJsonMidiPlay(self.getPlayList(), operand % str())
                return self
            case _: return super().__rshift__(operand)

    def __rrshift__(self, other_operand: Operand) -> Operand:
        import operand_element as oe
        self_first_element = self.firstOperand()
        if type(self_first_element) != ot.Null:
            match other_operand:
                case ot.Null():
                    pass
                case MultiElements():
                    other_last_element = self.lastOperand()
                    if type(other_last_element) != ot.Null:
                        other_last_element >> self_first_element
                case oe.Element(): other_operand % ol.Position() + other_operand % ol.TimeLength() >> self_first_element
                case ol.Position() | ol.TimeLength(): other_operand >> self_first_element
            for single_element_i in range(1, len(self._operand_list)):
                self._operand_list[single_element_i - 1] >> self._operand_list[single_element_i]
        return self

    def __add__(self, operand: Operand) -> 'MultiElements':
        import operand_element as oe
        match operand:
            case MultiElements():
                return MultiElements(self.copy() % list() + operand.copy() % list())
            case oe.Element():
                return MultiElements(self.copy() % list() + [operand.copy()])
            case Operand():
                element_copy = self.copy()
                element_list = element_copy % list()
                for single_element in element_list:
                    single_element << single_element % operand + operand
                return element_copy
            case int(): # repeat n times the last argument if any
                element_copy = self.copy()
                element_list = element_copy % list()
                if len(self._operand_list) > 0:
                    last_element = self._operand_list[len(self._operand_list) - 1]
                    while operand > 0:
                        element_list.append(last_element.copy())
                        operand -= 1
                return element_copy
        return self.copy()

    def __sub__(self, operand: Operand) -> 'MultiElements':
        import operand_element as oe
        match operand:
            case MultiElements():
                return MultiElements(self % list() - operand % list()).copy()
            case oe.Element():
                return MultiElements((self % list()) - [operand]).copy()
            case Operand():
                element_copy = self.copy()
                element_list = element_copy % list()
                for single_element in element_list:
                    single_element << single_element % operand - operand
                return element_copy
            case int(): # repeat n times the last argument if any
                element_copy = self.copy()
                element_list = element_copy % list()
                if len(self._operand_list) > 0:
                    last_element = self._operand_list[len(self._operand_list) - 1]
                    while operand > 0 and len(element_list) > 0:
                        element_list.pop()
                        operand -= 1
                return element_copy
        return self.copy()

    # multiply with a scalar 
    def __mul__(self, operand: Operand) -> 'MultiElements':
        import operand_element as oe
        match operand:
            case Operand():
                element_copy = self.copy()
                element_list = element_copy % list()
                for single_element in element_list:
                    single_element << single_element % operand * operand
                return element_copy
            case int(): # repeat n times the last argument if any
                multi_elements = MultiElements()    # empty list
                while operand > 0:
                    multi_elements += self
                    operand -= 1
                return multi_elements
        return self.copy()
    
    def __truediv__(self, operand: Operand) -> 'MultiElements':
        import operand_element as oe
        match operand:
            case Operand():
                self_copy = self.copy()
                elements_list = self_copy % list()
                for single_element in elements_list:
                    single_element << single_element % operand / operand
                return self_copy
            case int(): # repeat n times the last argument if any
                if operand > 0:
                    self_copy = self.copy()
                    elements_list = self_copy % list()
                    elements_to_be_removed = round(1 - self_copy.len() / operand)
                    while elements_to_be_removed > 0:
                        elements_list.pop()
                        elements_to_be_removed -= 1
                return self_copy
        return self.copy()
    
    def __floordiv__(self, time_length: ol.TimeLength) -> 'MultiElements':
        match time_length:
            case ol.TimeLength():
                starting_position = None
                for single_element in self._operand_list:
                    if starting_position is None:
                        starting_position = single_element % ol.Position()
                    else:
                        starting_position += time_length
                        single_element << ol.Position() << starting_position
        return self
