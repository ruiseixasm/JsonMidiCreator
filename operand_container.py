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
import enum
# Json Midi Creator Libraries
from creator import *
from operand import Operand

import operand_unit as ou
import operand_length as ol
import operand_generic as og
import operand_setup as os

class Container(Operand):
    pass

class MultiElements(Container):  # Just a container of Elements
    def __init__(self, *multi_elements):
        import operand_element as oe
        self._multi_elements = []
        if multi_elements is not None:
            for single_element in multi_elements:
                if isinstance(single_element, oe.Element):
                    self._multi_elements.append(single_element)
                elif isinstance(single_element, list) and all(isinstance(elem, oe.Element) for elem in single_element):
                    self._multi_elements.extend(single_element)
        self._selection: os.Selection = None
        self._element_iterator = 0

    def len(self) -> int:
        return len(self._multi_elements)

    def __iter__(self):
        return self
    
    def __next__(self):
        if self._element_iterator < len(self._multi_elements):
            single_element = self._multi_elements[self._element_iterator]
            self._element_iterator += 1
            return single_element
        else:
            self._element_iterator = 0  # Reset to 0 when limit is reached
            raise StopIteration
        
    def getLastPosition(self) -> ol.Position:
        last_position: ol.Position = ol.Position()
        for single_element in self._multi_elements:
            if single_element % ol.Position() > last_position:
                last_position = single_element % ol.Position()
        return last_position

    def __mod__(self, operand: list) -> list:
        if operand.__class__ == list:
            return self._multi_elements
        return []

    def firstElement(self) -> Operand:
        if len(self._multi_elements) > 0:
            return self._multi_elements[0]
        return og.Null()

    def lastElement(self) -> Operand:
        if len(self._multi_elements) > 0:
            return self._multi_elements[len(self._multi_elements) - 1]
        return og.Null()

    def getPlayList(self, position: ol.Position = None):
        import operand_element as oe
        play_list = []
        for single_element in self % list():
            if isinstance(single_element, oe.Element):
                play_list.extend(single_element.getPlayList(position))
        return play_list

    def getSerialization(self):
        multi_elements_serialization = []
        for single_element in self % list():
            multi_elements_serialization.append(single_element.getSerialization())
        return {
            "class": self.__class__.__name__,
            "multi_elements": multi_elements_serialization
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "multi_elements" in serialization):

            multi_elements = []
            multi_elements_serialization = serialization["multi_elements"]
            for single_element in multi_elements_serialization:
                class_name = single_element["class"]
                multi_elements.append(globals()[class_name]().loadSerialization(single_element))

            self._multi_elements = multi_elements
        return self
        
    def copy(self) -> 'MultiElements':
        import operand_element as oe
        multi_elements: list[oe.Element] = []
        for single_element in self._multi_elements:
            multi_elements.append(single_element.copy())
        return MultiElements(multi_elements)

    def __lshift__(self, operand: Operand) -> 'MultiElements':
        match operand:
            case list():
                self._multi_elements = operand
            case MultiElements():
                self._multi_elements = operand % list()
            case Operand():
                for single_element in self._multi_elements:
                    single_element << operand
        return self

    def __rshift__(self, operand: 'Operand') -> 'MultiElements':
        match operand:
            case ou.Play():
                jsonMidiPlay(self.getPlayList(), operand % int())
                return self
            case _: return operand.__rrshift__(self)

    def __rrshift__(self, other_operand: Operand) -> Operand:
        import operand_element as oe
        self_first_element = self.firstElement()
        if type(self_first_element) != og.Null:
            match other_operand:
                case og.Null():
                    pass
                case MultiElements():
                    other_last_element = self.lastElement()
                    if type(other_last_element) != og.Null:
                        other_last_element >> self_first_element
                case oe.Element(): other_operand % ol.Position() + other_operand % ol.TimeLength() >> self_first_element
                case ol.Position() | ol.TimeLength(): other_operand >> self_first_element
            for single_element_i in range(1, len(self._multi_elements)):
                self._multi_elements[single_element_i - 1] >> self._multi_elements[single_element_i]
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
                if len(self._multi_elements) > 0:
                    last_element = self._multi_elements[len(self._multi_elements) - 1]
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
                if len(self._multi_elements) > 0:
                    last_element = self._multi_elements[len(self._multi_elements) - 1]
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
                for single_element in self._multi_elements:
                    if starting_position is None:
                        starting_position = single_element % ol.Position()
                    else:
                        starting_position += time_length
                        single_element << ol.Position() << starting_position
        return self
