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
from types import FunctionType
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_label as ol
import operand_generic as og
import operand_element as oe
import operand_frame as of
import operand_container as oc
import operand_chaos as ch
import operand_mutation as om
import operand_selection as os


class Patterns(o.Operand):
    pass


class Drums(Patterns):

    def four_on_the_floor(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Uniformly accented beat in 4/4 time in which the bass drum is hit on every beat (1, 2, 3, 4)."""
        pattern: oc.Clip = oe.Note(kick) * 4
        pattern += oe.Note(snare, ra.Duration(1/2)) * 2 + ra.Beats(1)
        pattern += oe.Note(hi_hats) * 4 + ra.Beats(1/2)
        return pattern << ra.Duration(1/16)



