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
import operand_chaos as ch



class RC_Callables:
    pass


class RC_Splitter(RC_Callables):
    def __init__(self, *operands):
        self._elements: int = 8
        self._chaos: ch.Chaos = ch.SinX(340)


    def new_iteration(self, clip_0_copy: 'oc.Clip') -> 'oc.Clip':
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        clip_len: int = clip_0_copy.len()
        total_duration_beats = Fraction(0)
        foreground_elements: list[oe.Element] = clip_0_copy._foreground_items()
        for single_element in foreground_elements:
            total_duration_beats += single_element._duration_beats
        while clip_len < self._elements:
            continuous_split_step: int = 1 >> self._chaos
            continuous_split_beat: Fraction = quantization_beats * continuous_split_step % total_duration_beats
            continuous_start_beat = Fraction(0)
            for single_element in foreground_elements:
                continuous_finish_beat: Fraction = continuous_start_beat + single_element._duration_beats
                if continuous_split_beat < continuous_finish_beat:
                    single_element //= single_element % ra.Position() + continuous_split_beat - continuous_start_beat
                    break
                continuous_start_beat = continuous_finish_beat            
        return clip_0_copy

