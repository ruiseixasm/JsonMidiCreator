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
import math
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_label as ol
import operand_data as od
import operand_unit as ou
import operand_rational as ra
import operand_generic as og
import operand_element as oe
import operand_frame as of
import operand_chaos as ch
import operand_tamer as ot


class Yielder(o.Operand):
    """`Yielder`

    Generates `Element` items accordingly to a given logic.

    Parameters
    ----------
    Element(Note()) : The `Element` to be used as source for all yielded ones.
    list([1/4, 1/4, 1/4, 1/4]) : The parameters for each yield of elements.
    Length(4) : The `Length` where the Yield will be returned.
    """
    def __init__(self, *parameters):
        self._element: oe.Element = oe.Note()
        self._parameters: list[Any] = []
        self._length_beats: Fraction = ra.Length(4)._rational
        self._chaos: ch.Chaos = ch.Sequence()
        super().__init__(*parameters)

    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case Yielder():
                return self._element == other._element \
                    and self._parameters == other._parameters \
                    and self._length_beats == other._length_beats
            case od.Conditional():
                return other == self
            case _:
                return super().__eq__(other)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case oe.Element():
                        return self._element
                    case list():
                        return self._parameters
                    case ra.Length():
                        return operand << self._length_beats
                    case ch.Chaos():
                        return self._chaos
                    case _:
                        return super().__mod__(operand)
            case oe.Element():
                return self._element.copy()
            case list():
                self._index = 0
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                if self._parameters:
                    parameters_len: int = len(self._parameters)
                    if yielded_elements:
                        for element in yielded_elements:
                            element << self._parameters[self._index % parameters_len]
                            self._index += 1
                    else:
                        next_position: ra.Position = self._element.start()
                        while next_position < self._length_beats:
                            new_parameter = self._parameters[self._index % parameters_len]
                            new_element: oe.Element = self._element.copy(next_position)
                            yielded_elements.append(new_element << new_parameter)
                            next_position = new_element.finish()
                            self._index += 1
                elif not yielded_elements:
                    while next_position < self._length_beats:
                        new_element: oe.Element = self._element.copy(next_position)
                        yielded_elements.append(new_element)
                        next_position = new_element.finish()
                        self._index += 1
                return yielded_elements
            case ra.Length():
                return ra.Length(self._length_beats)
            case ch.Chaos():
                return self._chaos.copy()
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["element"]      = self.serialize(self._element)
        serialization["parameters"]["parameters"]   = self.serialize(self._parameters)
        serialization["parameters"]["length"]       = self.serialize(self._length_beats)
        serialization["parameters"]["chaos"]        = self.serialize(self._chaos)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "element" in serialization["parameters"] and "parameters" in serialization["parameters"] and
            "length" in serialization["parameters"] and "chaos" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._element       = self.deserialize(serialization["parameters"]["element"])
            self._parameters    = self.deserialize(serialization["parameters"]["parameters"])
            self._length_beats  = self.deserialize(serialization["parameters"]["length"])
            self._chaos         = self.deserialize(serialization["parameters"]["chaos"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Yielder():
                super().__lshift__(operand)
                self._element       = operand._element.copy()
                self._parameters    = o.Operand.deep_copy(operand._parameters)
                self._length_beats  = operand._length_beats
                self._chaos         = operand._chaos.copy()
            case od.Pipe():
                match operand._data:
                    case oe.Element():
                        self._element = operand._data
                    case list():
                        self._parameters = operand._data
                    case ra.Length():
                        self._length_beats = operand._data._rational
                    case ch.Chaos():
                        self._chaos = operand._data
                    case _:
                        super().__lshift__(operand)
            case oe.Element():
                self._element = operand.copy()
            case list():
                self._parameters = o.Operand.deep_copy(operand)
            case ra.Length():
                self._length_beats = operand._rational
            case ch.Chaos():
                self._chaos = operand.copy()
            case og.TimeSignature():
                self._element << operand
            case _:
                super().__lshift__(operand)
        return self

    def __pow__(self, operand: 'o.Operand') -> Self:
        '''
        This operator ** tags another Operand to self that will be the target of the << operation and \
            be passed to self afterwards in a chained fashion.
        '''
        if isinstance(operand, Yielder):
            self._next_operand = operand
        elif operand is None:
            self._next_operand = None
        return self
    

class YieldSteps(Yielder):
    """`Yielder -> YieldSteps`

    Places the given `Element` in each of the set Steps. Steps are 0 based!

    Parameters
    ----------
    Element(Note()) : The `Element` to be used as source for all yielded ones.
    list([0, 4, 8, 12]) : The `Steps` parameters for each yield of elements.
    Length(4) : The `Length` where the Yield will be returned.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._element << ra.Steps(1)
        self._parameters = [0, 4, 8, 12]
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case list():
                self._index = 0
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                if self._parameters:
                    parameters_len: int = len(self._parameters)
                    if yielded_elements:
                        for element in yielded_elements:
                            step_parameter = self._parameters[self._index % parameters_len]
                            element << ra.Step(step_parameter)
                            self._index += 1
                    else:
                        next_position: ra.Position = self._element.start()
                        while next_position < self._length_beats:
                            step_parameter = self._parameters[self._index % parameters_len]
                            new_element: oe.Element = self._element.copy(next_position)
                            yielded_elements.append(new_element << ra.Step(step_parameter))
                            self._index += 1
                            if self._index % parameters_len == 0:
                                next_position += ra.Measure(1)
                else:
                    return super().__mod__(operand)
                return yielded_elements
            case _:
                return super().__mod__(operand)


class YieldDegrees(Yielder):
    """`Yielder -> YieldDegrees`

    Generates a series of elements with the respective given duration stacked on each other \
        with the respective `Degree`.

    Parameters
    ----------
    Element(Note()) : The `Element` to be used as source for all yielded ones.
    list([1, 3, 5]) : The `Degree` parameters for each yield of elements.
    Length(4) : The `Length` where the Yield will be returned.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._parameters = [1, 3, 5]
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case list():
                self._index = 0
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                if self._parameters:
                    parameters_len: int = len(self._parameters)
                    if yielded_elements:
                        for element in yielded_elements:
                            degree_parameter = self._parameters[self._index % parameters_len]
                            element << ou.Degree(degree_parameter)
                            self._index += 1
                    else:
                        next_position: ra.Position = self._element.start()
                        while next_position < self._length_beats:
                            degree_parameter = self._parameters[self._index % parameters_len]
                            new_element: oe.Element = self._element.copy(next_position)
                            yielded_elements.append(new_element << ou.Degree(degree_parameter))
                            next_position = new_element.finish()
                            self._index += 1
                else:
                    return super().__mod__(operand)
                return yielded_elements
            case _:
                return super().__mod__(operand)




