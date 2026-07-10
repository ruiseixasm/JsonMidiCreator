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
    """
    # CHAINABLE OPERATIONS

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
                    case Data():                    return self
                    case ol.Null() | None:          return ol.Null()
                    case _:                         return self._data
            case Data():
                return operand.copy(self)
            case _:                         return self.deep_copy(self._data)
            
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["data"] = self.serialize(self._data)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Data':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "data" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._data = self.deserialize(serialization["parameters"]["data"])
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Sequencer():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            case od.Pipe():
                self._data = operand._data
            case _:
                self._data = self.deep_copy(operand)
        return self

    # NOT imul because it returns something different than a `Sequencer`
    def __mul__(self, element: 'Element') -> 'Clip':
        new_clip = oc.Clip()
        if isinstance(self._trigger_steps, str) and isinstance(element, oe.Element):
            steps_place = o.string_to_list(self._trigger_steps)
            position_step: ra.Step = ra.Step(0)
            element_0 = element.copy(ra.Position(0))
            for single_step in steps_place:
                if single_step == 1:
                    new_clip += element_0 + position_step
                position_step += 1
        return new_clip


