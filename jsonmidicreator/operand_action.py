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
from . import creator as c
from . import operand as o

from . import operand_label as ol
from . import operand_data as od
from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_generic as og
from . import operand_element as oe
from . import operand_container as oc
from . import operand_frame as of
from . import operand_chaos as ch
from . import operand_tamer as ot

if TYPE_CHECKING:
    from operand_element import Element
    from operand_container import Clip


class Action(o.Operand):
    """`Action`

    `Action` is intended to manipulate unmasked `Elements` in a `Clip` based on a given named action.
    The `action` method always returns the exact same inputted `Clip`.
    """
    def act(self, clip: 'Clip') -> 'Clip':
        for unmasked_element in clip.elements_unmasked():
            self._single_act(unmasked_element)
        return clip._sort_items()


    def _single_act(self, element: 'Element') -> 'Element':
        return element



class Delete_2(Action):
    """`Label -> Delete`

    Deletes all the unmasked items in the targeted `Container` or elements in it if a `Clip`.

    Args:
        None
    """
    def _single_act(self, element: 'Element') -> 'Element':
        if element._owner_clip is not None:
            element._owner_clip._delete_item(element, True)
        return element




