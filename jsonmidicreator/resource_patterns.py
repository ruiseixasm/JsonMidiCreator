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
from . import creator as c
from . import operand as o

from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_data as od
from . import operand_label as ol
from . import operand_generic as og
from . import operand_element as oe
from . import operand_frame as of
from . import operand_container as oc
from . import operand_chaos as ch


def pattern_funky_syncopation(drum_kit: 'og.DrumKit', channel: int = 1) -> 'oc.Clip':
    kick_line: str      = "t::Kick, :_3S, :_7S, :_10S"
    snare_line: str     = "t:_4S:Snare"
    ghost_line: str     = "t:_2S:Snare:50, :_6S, :_9S, :_11S"
    c_hat_line: str     = "t::Close Hat:80," + ":," * 15

    clip = oc.Clip()
    clip += od.Line(kick_line)
    clip += od.Line(snare_line)
    clip += od.Line(ghost_line)
    clip += od.Line(c_hat_line)

    return clip
