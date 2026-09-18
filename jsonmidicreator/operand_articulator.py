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


class Articulator(o.Operand):
    """`Articulator`

    An `Articulator` is intended to manipulate the `Clip`'s `Element`s based on a given `Frame`.
    This can deal with more complex changes than the ones given by simple Element wrapping.
    By including a `Frame` it doesn't require the typical masking associated with a `Process` that
    acts only on the entire Clip.

    Parameters
    ----------
    Frame(All()) : The selector frame of elements to be articulated.
    """
    def __init__(self, *parameters):
        self._frame: of.Frame = of.All()
        super().__init__(*parameters)


    def _get_framed_elements(self, clip: 'oc.clip') -> list['oe.Element']:
        self._frame._set_inside_container(clip)
        unmasked_elements: list[oe.Element] = clip.elements_unmasked()
        return [
            single_element for single_element in unmasked_elements
            if single_element == self._frame.frame(single_element)
        ]

    @staticmethod
    def _add_new_elements(clip: 'oc.Clip', new_elements: list['oe.Element']) -> 'oc.Clip':
        return clip._extend(new_elements)._set_owner_clip()._sort_items()


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case of.Frame():        return of.Frame() << self._frame
                    case _:                 return super().__mod__(operand)
            # Direct Values
            case of.Frame():
                return self._frame.copy()
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["frame"] = o.serialize( self._frame )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Articulator':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "frame" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._frame = o.deserialize( serialization["parameters"]["frame"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Articulator():
                super().__lshift__(operand)
                self._frame = operand._frame.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():
                        self._frame           = operand._data % od.Pipe( int() )
                    case _:
                        super().__lshift__(operand)
            case of.Frame():
                self._frame               = int(max(1, operand % int()))
            case _:
                super().__lshift__(operand)
        return self


