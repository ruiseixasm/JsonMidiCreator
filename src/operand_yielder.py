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

if TYPE_CHECKING:
    from operand_container import Clip


class Yielder(o.Operand):
    """`Yielder`

    Generates `Element` items accordingly to a given logic.

    Parameters
    ----------
    Element(Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    """
    def __init__(self, *parameters):
        self._element: oe.Element = oe.Note()
        self._measures: int = 4
        super().__init__(*parameters)

    def _set_element_parameter(self, element: 'oe.Element', parameter: Any) -> 'oe.Element':
        return element << parameter

    def _get_yielded_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = []
        if isinstance(self._next_operand, Yielder):
            yielded_elements = self._next_operand._yield_elements()
            if yielded_elements:    # Stretches the elements like a Drum Machine
                target_beats_per_measure: Fraction = self._element._time_signature % ra.BeatsPerMeasure() % Fraction()
                _last_measure: ra.Measure = ra.Measure(0)
                for new_element in yielded_elements:
                    new_element._owner_clip = None  # Safe code
                    beats_per_measure_ratio: Fraction = target_beats_per_measure / new_element._time_signature._top
                    new_element._position_beats *= beats_per_measure_ratio
                    new_element._duration_beats *= beats_per_measure_ratio
                    new_element._time_signature << self._element._time_signature
                    if new_element % ra.Measure() > _last_measure:
                        _last_measure = new_element % ra.Measure()
                if _last_measure > self._measures - 1:
                    truncated_elements: list[oe.Element] = []
                    for new_element in yielded_elements:
                        element_measure: ra.Measure = new_element % ra.Measure()
                        if element_measure < self._measures:
                            truncated_elements.append(new_element)
                    return truncated_elements
                extended_elements: list[oe.Element] = []
                _extended_measure: ra.Measure = ra.Measure(0)
                while _last_measure < self._measures - 1:
                    for new_element in yielded_elements:
                        element_measure: ra.Measure = new_element % ra.Measure()
                        target_measure: ra.Measure = _last_measure + element_measure + 1
                        if target_measure < self._measures:
                            copied_element: oe.Element = new_element.copy(target_measure)
                            extended_elements.append(copied_element)
                            if copied_element % ra.Measure() > _extended_measure:
                                _extended_measure = copied_element % ra.Measure()
                    _last_measure = _extended_measure
                yielded_elements.extend(extended_elements)
        return yielded_elements
    
    def _yield_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = self._get_yielded_elements()
        if not yielded_elements:
            next_position: ra.Position = self._element.start()
            end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
            while next_position < end_position:
                new_element: oe.Element = self._element.copy(next_position)
                yielded_elements.append(new_element)
                next_position = new_element.finish()
        return yielded_elements


    def __eq__(self, other: o.Operand) -> bool:
        import operand_container as oc
        match other:
            case Yielder():
                return self._element == other._element and self._measures == other._measures
            case oc.Composition():
                return self.__mod__(oc.Clip()) == other
            case od.Conditional():
                return other == self
            case _:
                return super().__eq__(other)

    def __mod__(self, operand: o.T) -> o.T:
        import operand_container as oc
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
            case ra.Measures() | ra.Measure():
                return operand.copy(self._measures)
            case int():
                return self._measures
            case oc.Clip():
                yielded_elements: list[oe.Element] = self._yield_elements()
                yielded_clip: oc.Clip = oc.Clip(self._element._time_signature)
                yielded_clip._items = yielded_elements
                return yielded_clip._set_owner_clip()._sort_items()
            case _:
                return self._element.__mod__(operand)

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
                        self._element._owner_clip = None  # Safe code
                    case ra.Measures() | ra.Measure():
                        self._measures = operand._data % int()
                    case int():
                        self._measures = operand._data
                    case _:
                        super().__lshift__(operand)
            case oe.Element():
                self._element = operand.copy()
                self._element._owner_clip = None  # Safe code
            case ra.Measures() | ra.Measure():
                self._measures = operand % int()
            case int():
                self._measures = operand
            case _:
                self._element << operand
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

    def __add__(self, operand: any) -> 'Clip':
        import operand_container as oc
        return self.__mod__(oc.Clip()).__iadd__(operand)
    
    def __sub__(self, operand: any) -> 'Clip':
        import operand_container as oc
        return self.__mod__(oc.Clip()).__isub__(operand)
    
    def __mul__(self, operand: any) -> 'Clip':
        import operand_container as oc
        return self.__mod__(oc.Clip()).__imul__(operand)
    
    def __truediv__(self, operand: any) -> 'Clip':
        import operand_container as oc
        return self.__mod__(oc.Clip()).__itruediv__(operand)
    
    def __floordiv__(self, operand: any) -> 'Clip':
        import operand_container as oc
        return self.__mod__(oc.Clip()).__ifloordiv__(operand)


class YieldOnBeat(Yielder):
    """`Yielder -> YieldOnBeat`

    Places the given `Element` on each `Beat`!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    """
    def __init__(self, *parameters):
        super().__init__(ra.Steps(1), *parameters)

    def _yield_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = []
        next_position: ra.Position = self._element.start() << ra.Beats(0)
        end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
        while next_position < end_position:
            new_element: oe.Element = self._element.copy(next_position)
            yielded_elements.append(new_element)
            next_position += ra.Beats(1)
        return yielded_elements


class YieldOffBeat(Yielder):
    """`Yielder -> YieldOffBeat`

    Places the given `Element` off the `Beat`!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    """
    def __init__(self, *parameters):
        super().__init__(ra.Steps(1), *parameters)

    def _yield_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = []
        next_position: ra.Position = self._element.start() << ra.Beats(1/2)
        end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
        while next_position < end_position:
            new_element: oe.Element = self._element.copy(next_position)
            yielded_elements.append(new_element)
            next_position += ra.Beats(1)
        return yielded_elements


class YieldDownBeat(Yielder):
    """`Yielder -> YieldDownBeat`

    Places the given `Element` on each Down Beat (the first `Beat` in each `Measure`)!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    """
    def __init__(self, *parameters):
        super().__init__(ra.Steps(1), *parameters)

    def _yield_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = []
        next_position: ra.Position = self._element.start() << ra.Beats(0)
        end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
        while next_position < end_position:
            new_element: oe.Element = self._element.copy(next_position)
            yielded_elements.append(new_element)
            next_position += ra.Measures(1)
        return yielded_elements


class YieldUpBeat(Yielder):
    """`Yielder -> YieldUpBeat`

    Places the given `Element` on each Up Beat (the last off Beat in each `Measure`)!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    """
    def __init__(self, *parameters):
        super().__init__(ra.Steps(1), *parameters)

    def _yield_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = []
        next_position: ra.Position = self._element.start() << ra.Measures(1)
        next_position -= ra.Beats(1/2)
        end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
        while next_position < end_position:
            new_element: oe.Element = self._element.copy(next_position)
            yielded_elements.append(new_element)
            next_position += ra.Measures(1)
        return yielded_elements


class YieldPattern(Yielder):
    """`Yielder -> YieldPattern`

    Places the given `Element` stacked accordingly to each given item in the pattern!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    list([ra.Beats(2/3)]) : The given parameters for each yield of elements.
    """
    def __init__(self, *parameters):
        self._pattern: list[Any] = [ra.Beats(2/3)]
        super().__init__(*parameters)

    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case YieldPattern():
                return super().__eq__(other) and self._pattern == other._pattern
            case _:
                return super().__eq__(other)

    def _yield_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = self._get_yielded_elements()
        if self._pattern:
            parameters_len: int = len(self._pattern)
            _parameter_i: int = 0
            if yielded_elements:
                previous_measure: int = 0
                for new_element in yielded_elements:
                    next_measure: int = new_element.start() % int() % self._measures
                    if next_measure > previous_measure and next_measure == 0:
                        _parameter_i = 0
                    previous_measure = next_measure
                    parameter: Any = self._pattern[_parameter_i % parameters_len]
                    self._set_element_parameter(new_element, parameter)
                    _parameter_i += 1
            else:
                next_position: ra.Position = self._element.start()
                end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
                while next_position < end_position:
                    new_element: oe.Element = self._element.copy(next_position)
                    yielded_elements.append(new_element)
                    parameter: Any = self._pattern[_parameter_i % parameters_len]
                    self._set_element_parameter(new_element, parameter)
                    next_position = new_element.finish()
                    _parameter_i += 1
        return yielded_elements


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():
                        return self._pattern
                    case _:
                        return super().__mod__(operand)
            case list():
                return o.Operand.deep_copy(self._pattern)
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
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    list([1/4, 1/4, 1/4, 1/4]) : The `Duration` parameters for each yield of elements.
    """
    pass


class YieldSteps(YieldPositions):
    """`Yielder -> YieldPattern -> YieldPositions -> YieldSteps`

    Places the given `Element` in each of the set Steps. Steps are 0 based!

    Parameters
    ----------
    Element(oe.Note(ra.Steps(1))) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    list([0, 4, 8, 12]) : The `Steps` parameters for each yield of elements.
    """
    def __init__(self, *parameters):
        super().__init__(oe.Note(ra.Steps(1)), [0, 4, 8, 12], *parameters)

    def _set_element_parameter(self, element: 'oe.Element', parameter: Any) -> 'oe.Element':
        return element << ra.Step(parameter)

    def _yield_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = []
        if self._pattern:
            parameters_len: int = len(self._pattern)
            next_position: ra.Position = self._element.start()
            end_position: ra.Position = next_position.copy(ra.Measures(self._measures))
            _parameter_i: int = 0
            while next_position < end_position:
                new_element: oe.Element = self._element.copy(next_position)
                yielded_elements.append(new_element)
                parameter: Any = self._pattern[_parameter_i % parameters_len]
                self._set_element_parameter(new_element, parameter)
                _parameter_i += 1
                if _parameter_i % parameters_len == 0:
                    next_position += ra.Measure(1)
        return yielded_elements


class YieldParameter(YieldPattern):
    """`Yielder -> YieldPattern -> YieldParameter`

    Generates a series of elements with the respective duration stacked on each other \
        where each one are set with the given Parameter.

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    list(['1', '3', '5']) : The non positional parameters for each yield of elements.
    Parameter(Pitch()) : Parameter that is intended to be set on each Yielded `Element`.
    """
    def __init__(self, *parameters):
        self._parameter: Any = og.Pitch()
        super().__init__(['1', '3', '5'], *parameters)

    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case YieldParameter():
                return super().__eq__(other) and self._parameter == other._parameter
            case _:
                return super().__eq__(other)

    def _set_element_parameter(self, element: 'oe.Element', parameter: Any) -> 'oe.Element':
        return element << (element % self._parameter << parameter)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case od.Parameter():
                        return operand._data << self._parameter
                    case _:
                        return super().__mod__(operand)
            case od.Parameter():
                return od.Parameter(o.Operand.deep_copy(self._parameter))
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["parameter"] = self.serialize(self._parameter)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "parameter" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._parameter = self.deserialize(serialization["parameters"]["parameter"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case YieldParameter():
                super().__lshift__(operand)
                self._parameter = o.Operand.deep_copy(operand._parameter)
            case od.Pipe():
                match operand._data:
                    case od.Parameter():
                        self._parameter = operand._data._data
                    case _:
                        super().__lshift__(operand)
            case od.Parameter():
                self._parameter = o.Operand.deep_copy(operand._data)
            case _:
                super().__lshift__(operand)
        return self


class YieldDegree(YieldParameter):
    """`Yielder -> YieldPattern -> YieldParameter -> YieldDegree`

    Generates a series of elements with the respective given duration stacked on each other \
        with the respective `Degree`.

    Parameters
    ----------
    Element(Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    list([1, 3, 5]) : The `Degree` parameters for each yield of elements.
    Parameter(Degree()) : Parameter that is intended to be set on each Yielded `Element`.
    """
    def __init__(self, *parameters):
        super().__init__([1, 3, 5], od.Parameter(ou.Degree()), *parameters)


class YieldDuration(YieldParameter):
    """`Yielder -> YieldPattern -> YieldParameter -> YieldDurations`

    Places the given `Element` stacked accordingly to each given `Duration`!

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    list([1/4]) : The `Duration` parameters for each yield of elements.
    Parameter(Duration()) : Parameter that is intended to be set on each Yielded `Element`.
    """
    def __init__(self, *parameters):
        super().__init__([1/4], od.Parameter(ra.Duration()), *parameters)



class YieldGrid(Yielder):
    """`Yielder -> YieldGrid`

    Places the given `Element` on each Step given by a grid of `channel: step`.

    Parameters
    ----------
    Element(oe.Note()) : The `Element` to be used as source for all yielded ones.
    Measures(4), Measure(4), int(4) : The `Measures` sets the length where the Yield will be returned.
    dict({1:[0, 8], 2:[4, 12], 7:[0, 2, 4, 6, 8, 10, 12, 14]}) : The steps as list in each channel as index.
    """
    def __init__(self, *parameters):
        self._grid: dict[int, list[int]] = {
            1: [0, 8],
            2: [4, 12],
            7: [0, 2, 4, 6, 8, 10, 12, 14]
        }
        super().__init__(ra.Steps(1), *parameters)

    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case YieldGrid():
                return super().__eq__(other) and self._grid == other._grid
            case _:
                return super().__eq__(other)

    def _yield_elements(self) -> list['oe.Element']:
        yielded_elements: list[oe.Element] = []
        for channel, steps in self._grid.items():
            for step in steps:
                new_element: oe.Element = self._element.copy()
                yielded_elements.append(new_element)
                parameter: Any = (ou.Channel(channel), ra.Step(step))
                self._set_element_parameter(new_element, parameter)
        return yielded_elements


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case dict():
                        return self._grid
                    case _:
                        return super().__mod__(operand)
            case dict():
                return o.Operand.deep_copy(self._grid)
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["grid"] = self.serialize(self._grid)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "grid" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._grid = self.deserialize(serialization["parameters"]["grid"])
        return self

    def __lshift__(self, operand: any) -> Self:
        match operand:
            case YieldGrid():
                super().__lshift__(operand)
                self._grid = o.Operand.deep_copy(operand._grid)
            case od.Pipe():
                match operand._data:
                    case dict():
                        self._grid = operand._data
                    case _:
                        super().__lshift__(operand)
            case dict():
                self._grid = o.Operand.deep_copy(operand)
            case _:
                super().__lshift__(operand)
        return self

