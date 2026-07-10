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
import operand_container as oc
import operand_frame as of
import operand_chaos as ch
import operand_tamer as ot

if TYPE_CHECKING:
    from operand_element import Element
    from operand_container import Clip


class Yielder(o.Operand):
    """`Yielder`

    An `Yielder` is intended to be multiplied with an `Element` and result in a `Clip`, the yield of that element as a seed.
    
    Parameters
    ----------
    Length(1), TimeValue, Fraction : The length of the yield.
    """
    def __init__(self, *parameters):
        self._length_beats = Fraction(og.settings._time_signature._top) # top is beats per measure
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case Fraction():
                        return self._length_beats
                    case _:
                        return super().__mod__(operand)
            case Fraction():
                return self._length_beats
            case ra.Length():
                return operand.copy(self, self._length_beats)
            case ra.TimeValue():
                return operand.copy(ra.Beats(self, self._length_beats))
            case _:
                return super().__mod__(operand)
            
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["length_beats"] = self.serialize(self._length_beats)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "length_beats" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._length_beats = self.deserialize(serialization["parameters"]["length_beats"])
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Yielder():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._length_beats = operand._length_beats
            case od.Pipe():
                match operand._data:
                    case Fraction():
                        self._length_beats = operand._data
                    case _:
                        super().__lshift__(operand)
            case Fraction():
                self._length_beats = operand
            case ra.Length():
                if operand > Fraction(0):   # Allows innocuous non positive setting (neutral)
                    self._duration_beats    = operand._rational
            case ra.TimeValue():
                self._duration_beats = ra.Length(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    # NOT imul because it returns something different than a `Sequencer`
    def __mul__(self, element: 'Element') -> 'Clip':    # Mandatory implementation
        return oc.Clip(element)
    

class Sequencer(Yielder):
    """`Yielder -> Sequencer`

    A `Sequencer` as the name implies lets an Element be placed one a Clip accordingly to a sequence of `1`s and `.`s.
    
    Parameters
    ----------
    str("1... 1... 1... 1...") : The sequence being used, where `1` is the step triggering and `.` the non triggering step.
    """
    def __init__(self, *parameters):
        self._trigger_steps = "1... 1... 1... 1..."
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():
                        if isinstance(self._trigger_steps, str):
                            return self._trigger_steps
                    case of.Frame():
                        if isinstance(self._trigger_steps, of.Frame):
                            return self._trigger_steps
                    case _:
                        return super().__mod__(operand)
            case str():
                if isinstance(self._trigger_steps, str):
                    return self._trigger_steps
            case _:
                return super().__mod__(operand)
            
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["trigger_steps"] = self.serialize(self._trigger_steps)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "trigger_steps" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._trigger_steps = self.deserialize(serialization["parameters"]["trigger_steps"])
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Sequencer():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._trigger_steps = self.deep_copy(operand._trigger_steps)
            case od.Pipe():
                match operand._data:
                    case str() | of.Frame():
                        self._trigger_steps = operand._data
                    case _:
                        super().__lshift__(operand)
            case str():
                self._trigger_steps = operand
            case of.Frame():
                self._trigger_steps = operand.copy()
            case _:
                super().__lshift__(operand)
        return self


    def __mul__(self, element: 'Element') -> 'Clip':
        new_clip = oc.Clip()
        if isinstance(element, oe.Element):
            element_0 = element.copy(ra.Position(0))
            match self._trigger_steps:
                case str():
                    steps_place = o.string_to_list(self._trigger_steps)
                    for single_step in steps_place:
                        if single_step == 1:
                            new_clip += element_0   # Implicit copy of element_0
                        element_0 += ra.Step(1)
                case of.Frame():
                    self._trigger_steps._set_inside_container(new_clip)
                    total_length_beats: Fraction = element_0._duration_beats
                    if element_0 % ra.Position() < total_length_beats:
                        if self._trigger_steps.frame(element_0) == ol.Full():
                            new_clip += element_0
                        element_0 += ra.Step(1)
        return new_clip


