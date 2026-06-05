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
    def __init__(self, chaos: ch.Chaos = ch.SinX(340),
                 exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 max_tries: int = 100, no_repetitions: bool = True):
        self._compositions: list[oc.Composition] = []
        self._chaos: ch.Chaos = chaos
        self._exclusion: Callable | None = exclusion
        self._post_processing: Callable | None = post_processing
        self._max_tries: int = max_tries
        self._no_repetitions = no_repetitions

    def reset(self) -> Self:
        self._compositions = []
        return self
    
    def _apply_exclusion(self, composition: oc.Composition) -> bool:
        # For efficiency reasons the repetitions check should come after
        if callable(self._exclusion) and self._exclusion(composition) \
            or self._no_repetitions and composition in self._compositions:
                return True
        self._compositions.append(composition)
        return False

    def _apply_post_processing(self, composition: oc.Composition) -> oc.Composition:
        if callable(self._post_processing):
            return self._post_processing(composition)
        return composition


class RC_Clips(RC_Callables):
    pass

class RC_Splitter(RC_Clips):
    def __init__(self, elements: int = 8,
                 chaos: ch.Chaos = ch.SinX(340),
                 exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 max_tries: int = 100, no_repetitions: bool = True):
        super().__init__(chaos, exclusion, post_processing, max_tries, no_repetitions)
        self._elements: int = elements


    def new_iteration(self, clip_0: 'oc.Clip') -> 'oc.Clip':
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        total_duration_beats = Fraction(0)
        for single_element in clip_0._foreground_items():
            total_duration_beats += single_element._duration_beats
        self._compositions.append(clip_0) # Avoids repeating the initial clip (seed)
        try_i: int = 0
        while try_i < self._max_tries:
            iteration_clip: oc.Clip = clip_0.copy()
            try_j: int = 0
            while iteration_clip.len() < self._elements and try_j < self._max_tries * 2:
                continuous_split_step: int = 1 >> self._chaos
                continuous_split_beat: Fraction = quantization_beats * continuous_split_step % total_duration_beats
                continuous_start_beat = Fraction(0)
                for single_element in iteration_clip._foreground_items():
                    continuous_finish_beat = continuous_start_beat + single_element._duration_beats
                    if continuous_split_beat < continuous_finish_beat:
                        if continuous_split_beat > continuous_start_beat:
                            element_split_position: ra.Position = single_element % ra.Position()
                            element_split_position += continuous_split_beat - continuous_start_beat
                            single_element //= element_split_position
                        break
                    continuous_start_beat = continuous_finish_beat
                if iteration_clip.len() == self._elements and not self._apply_exclusion(iteration_clip):
                    return self._apply_post_processing(iteration_clip)
                try_j += 1
            try_i += 1
        return clip_0.empty_copy()  # No valid Clip made

