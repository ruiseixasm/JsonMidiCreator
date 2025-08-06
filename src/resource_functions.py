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


class F_Function:
    def get_iterate_function(self) -> Callable[['oc.Composition'], 'oc.Composition']:
        return lambda composition: self.iterate(composition)
    
    def iterate(self, composition: 'oc.Composition') -> 'oc.Composition':
        return composition


class F_Rhythm(F_Function):
    pass

class F_Rhythm_Fast_Quantized(F_Rhythm):
    def __init__(self,
                 durations: list[float] = [1/8 * 3/2, 1/8, 1/16 * 3/2, 1/16, 1/32 * 3/2, 1/32],
                 choices: list[int] = [2, 4, 4, 2, 1, 1, 3],
                 chaos: ch.Chaos = ch.SinX(340)):
        # floats are implicitly Note Values for `Element` operands
        self.durations: list[float] = durations
        self.choices: list[int] = choices
        self.chaos: ch.Chaos = chaos

    def iterate(self, clip: 'oc.Clip') -> 'oc.Clip':
        if isinstance(clip, oc.Clip):
            self.chaos._tamer.reset()   # Tamer needs to be reset
            picked_durations = o.list_choose(self.durations, self.chaos % self.choices)
            clip << of.Foreach(*picked_durations)**ra.NoteValue()
            return clip.stack().quantize().mul([0]).link().mul(4)
        return clip


class F_Pitch(F_Function):
    pass

