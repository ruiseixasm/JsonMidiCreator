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
        super().__init__(*parameters)
        if not isinstance(self._data, str): # Makes sure it's a string
            self._data = "1... 1... 1... 1..."

    # NOT imul because it returns something different than a `Sequencer`
    def __mul__(self, element: 'Element') -> 'Clip':
        import operand_rational as ra
        import operand_element as oe
        import operand_container as oc
        new_clip = oc.Clip()
        if isinstance(self._data, str) and isinstance(element, oe.Element):
            steps_place = o.string_to_list(self._data)
            position_step: ra.Step = ra.Step(0)
            element_0 = element.copy(ra.Position(0))
            for single_step in steps_place:
                if single_step == 1:
                    new_clip += element_0 + position_step
                position_step += 1
        return new_clip


