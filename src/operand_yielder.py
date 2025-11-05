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
    Measures(4) : The `Measures` sets the length where the Yield will be returned.
    """
    def __init__(self, *parameters):
        self._element: oe.Element = oe.Note()
        self._measures: int = 4
        super().__init__(*parameters)

    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case Yielder():
                return self._element == other._element and self._measures == other._measures
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
                    case ra.Measures() | ra.Measure():
                        return operand << self._measures
                    case _:
                        return super().__mod__(operand)
            case oe.Element():
                return self._element.copy()
            case list():
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                if not yielded_elements:
                    next_position: ra.Position = self._element.start()
                    end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
                    while next_position < end_position:
                        new_element: oe.Element = self._element.copy(next_position)
                        yielded_elements.append(new_element)
                        next_position = new_element.finish()
                return yielded_elements
            case ra.Measures() | ra.Measure():
                return operand.copy(self._measures)
            case int():
                return self._measures
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["element"]  = self.serialize(self._element)
        serialization["parameters"]["measures"] = self.serialize(self._measures)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "element" in serialization["parameters"] and "measures" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._element   = self.deserialize(serialization["parameters"]["element"])
            self._measures  = self.deserialize(serialization["parameters"]["measures"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Yielder():
                super().__lshift__(operand)
                self._element   = operand._element.copy()
                self._measures  = operand._measures
            case od.Pipe():
                match operand._data:
                    case oe.Element():
                        self._element = operand._data
                    case ra.Measures() | ra.Measure():
                        self._measures = operand._data % int()
                    case int():
                        self._measures = operand._data
                    case _:
                        super().__lshift__(operand)
            case oe.Element():
                self._element = operand.copy()
            case ra.Measures() | ra.Measure():
                self._measures = operand % int()
            case int():
                self._measures = operand
            case og.TimeSignature():
                if isinstance(self._next_operand, Yielder):
                    self._next_operand << operand
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


class YieldPattern(Yielder):
    """`Yielder -> YieldPattern`

    Places the given `Element` stacked accordingly to each given item in the pattern!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4) : The `Measures` sets the length where the Yield will be returned.
    list([1/4, 1/4, 1/4, 1/4]) : The given parameters for each yield of elements.
    """
    def __init__(self, *parameters):
        self._pattern: list[Any] = [1/4, 1/4, 1/4, 1/4]
        super().__init__(*parameters)

    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case YieldPattern():
                return super().__eq__(other) and self._pattern == other._pattern
            case _:
                return super().__eq__(other)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():
                        return self._pattern
                    case _:
                        return super().__mod__(operand)
            case list():
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                if self._pattern:
                    self._index = 0
                    parameters_len: int = len(self._pattern)
                    if yielded_elements:
                        for element in yielded_elements:
                            element << self._pattern[self._index % parameters_len]
                            self._index += 1
                    else:
                        next_position: ra.Position = self._element.start()
                        end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
                        while next_position < end_position:
                            new_element: oe.Element = self._element.copy(next_position)
                            element_parameter = self._pattern[self._index % parameters_len]
                            yielded_elements.append(new_element << element_parameter)
                            next_position = new_element.finish()
                            self._index += 1
                else:
                    return super().__mod__(operand)
                return yielded_elements
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pattern"] = self.serialize(self._pattern)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pattern" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pattern = self.deserialize(serialization["parameters"]["pattern"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case YieldPattern():
                super().__lshift__(operand)
                self._pattern = o.Operand.deep_copy(operand._pattern)
            case od.Pipe():
                match operand._data:
                    case list():
                        self._pattern = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                self._pattern = o.Operand.deep_copy(operand)
            case _:
                super().__lshift__(operand)
        return self

class YieldPositions(YieldPattern):
    """`Yielder -> YieldPattern -> YieldPositions`

    Places the given `Element` stacked accordingly to each given pattern!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4) : The `Measures` sets the length where the Yield will be returned.
    list([1/4, 1/4, 1/4, 1/4]) : The `Duration` parameters for each yield of elements.
    """
    pass

class YieldDurations(YieldPositions):
    """`Yielder -> YieldPattern -> YieldPositions -> YieldDurations`

    Places the given `Element` stacked accordingly to each given `Duration`!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4) : The `Measures` sets the length where the Yield will be returned.
    list([1/4, 1/4, 1/4, 1/4]) : The `Duration` parameters for each yield of elements.
    """
    def __init__(self, *parameters):
        super().__init__([1/4, 1/4, 1/4, 1/4], *parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case list():
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                element_duration: ra.Duration = self._element % ra.Duration()
                if self._pattern:
                    self._index = 0
                    parameters_len: int = len(self._pattern)
                    if yielded_elements:
                        for element in yielded_elements:
                            duration_parameter = element_duration << self._pattern[self._index % parameters_len]
                            element << duration_parameter
                            self._index += 1
                    else:
                        next_position: ra.Position = self._element.start()
                        end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
                        while next_position < end_position:
                            new_element: oe.Element = self._element.copy(next_position)
                            duration_parameter = element_duration << self._pattern[self._index % parameters_len]
                            yielded_elements.append(new_element << duration_parameter)
                            next_position = new_element.finish()
                            self._index += 1
                else:
                    return super().__mod__(operand)
                return yielded_elements
            case _:
                return super().__mod__(operand)


class YieldSteps(YieldPositions):
    """`Yielder -> YieldPattern -> YieldPositions -> YieldSteps`

    Places the given `Element` in each of the set Steps. Steps are 0 based!

    Parameters
    ----------
    Element(oe.Note(ra.Steps(1))) : The `Element` to be used as source for all yielded ones.
    Measures(4) : The `Measures` sets the length where the Yield will be returned.
    list([0, 4, 8, 12]) : The `Steps` parameters for each yield of elements.
    """
    def __init__(self, *parameters):
        super().__init__(oe.Note(ra.Steps(1)), [0, 4, 8, 12], *parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case list():
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                if self._pattern:
                    self._index = 0
                    parameters_len: int = len(self._pattern)
                    if yielded_elements:
                        for element in yielded_elements:
                            step_parameter = self._pattern[self._index % parameters_len]
                            element << ra.Step(step_parameter)
                            self._index += 1
                    else:
                        next_position: ra.Position = self._element.start()
                        end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
                        while next_position < end_position:
                            step_parameter = self._pattern[self._index % parameters_len]
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


class YieldPitches(YieldPattern):
    """`Yielder -> YieldPattern -> YieldPitches`

    Sets the `Element` pitches accordingly to each given pattern!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4) : The `Measures` sets the length where the Yield will be returned.
    list([1/4, 1/4, 1/4, 1/4]) : The `Duration` parameters for each yield of elements.
    """
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case list():
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                if not yielded_elements:
                    next_position: ra.Position = self._element.start()
                    end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
                    while next_position < end_position:
                        new_element: oe.Element = self._element.copy(next_position)
                        yielded_elements.append(new_element)
                        next_position = new_element.finish()
                else:
                    return super().__mod__(operand)
                return yielded_elements
            case _:
                return super().__mod__(operand)


class YieldDegrees(YieldPitches):
    """`Yielder -> YieldPattern -> YieldPitches -> YieldDegrees`

    Generates a series of elements with the respective given duration stacked on each other \
        with the respective `Degree`.

    Parameters
    ----------
    Element(Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4) : The `Measures` sets the length where the Yield will be returned.
    list([1, 3, 5]) : The `Degree` parameters for each yield of elements.
    """
    def __init__(self, *parameters):
        super().__init__([1, 3, 5], *parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case list():
                yielded_elements: list[oe.Element] = []
                if isinstance(self._next_operand, Yielder):
                    yielded_elements = self._next_operand.__mod__(operand)
                if not yielded_elements:
                    yielded_elements = super().__mod__(operand)
                if self._pattern:
                    self._index = 0
                    parameters_len: int = len(self._pattern)
                    for element in yielded_elements:
                        degree_parameter = self._pattern[self._index % parameters_len]
                        element << ou.Degree(degree_parameter)
                        self._index += 1
                return yielded_elements
            case _:
                return super().__mod__(operand)



