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
import operand_tamer as ot
import operand_chaos as ch


class RO_Operands:
    pass


class RO_Clips(RO_Operands):
    
    def multi(notes: int = 6, rests: int = 1, triplets: int = 1, triads: int = 1) -> 'oc.Clip':
        multi_clip: oc.Clip = oc.Clip()
        for _ in range(notes):
            multi_clip /= oe.Note()
        for _ in range(rests):
            multi_clip /= oe.Rest()
        for _ in range(triplets):
            multi_clip /= oe.Triplet()
        for _ in range(triads):
            multi_clip /= oe.Cluster()
        return multi_clip


class RO_Lists(RO_Operands):
    pass

