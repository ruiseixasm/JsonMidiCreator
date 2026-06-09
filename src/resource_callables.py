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
                 extra_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 packed_repeats: int = 1, max_tries: int = 4, no_repetitions: bool = True):
        self._compositions: list[oc.Composition] = []
        self._chaos: ch.Chaos = chaos
        self._extra_exclusion: Callable | None = extra_exclusion
        self._post_processing: Callable | None = post_processing
        self._packed_repeats: int = packed_repeats
        self._max_tries: int = max_tries
        self._no_repetitions = no_repetitions
        self._index: int = 1    # This index start at 1 because 0 is the seed

    def reset(self) -> Self:
        self._compositions = []
        self._index = 1 # This index start at 1 because 0 is the seed
        return self
    
    def new_iteration(self, composition_0: 'oc.Composition') -> 'oc.Composition':
        packed_iteration: oc.Composition = composition_0.empty_copy()
        if not self._compositions:
            self._compositions.append(composition_0) # Avoids repeating the initial clip (seed)
        for _ in range(self._packed_repeats):
            available_tries: int = self._max_tries
            while available_tries > 0:
                new_composition = self._single_iteration(composition_0.copy())
                # Negative index means it didn't got a valid result
                if new_composition._index >= 0 and not self._to_be_excluded(new_composition):
                    new_composition._index = self._index   # Updates it index accordingly to the iteration
                    packed_iteration *= new_composition # does a copy of new_composition
                    break
                available_tries -= 1
            self._index += 1
        return self._apply_post_processing(packed_iteration)

    def _single_iteration(self, composition_0: 'oc.Composition') -> 'oc.Composition':
        return composition_0

    def _to_be_excluded(self, composition: oc.Composition) -> bool:
        # The external user defined method is called if and only if the composition is internally validated
        if self._no_repetitions:
            if composition in self._compositions:
                return True
            # Adds the result to not be considered again (no repetitions)
            self._compositions.append(composition)
        if callable(self._extra_exclusion) and self._extra_exclusion(composition):
            return True
        return False

    def _apply_post_processing(self, composition: oc.Composition) -> oc.Composition:
        if callable(self._post_processing):
            return self._post_processing(composition)
        return composition


class RC_Function(RC_Callables):
    def __init__(self, function: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 chaos: ch.Chaos = ch.SinX(340),
                 extra_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 packed_repeats: int = 1, max_tries: int = 100, no_repetitions: bool = True):
        super().__init__(chaos, extra_exclusion, post_processing, packed_repeats, max_tries, no_repetitions)
        self._function: list[Any] = function


    def _single_iteration(self, composition_0: 'oc.Composition') -> 'oc.Composition':
        if callable(self._function):
            new_composition: oc.Composition = self._function(composition_0)
            return self._apply_post_processing(new_composition)
        return self._apply_post_processing(composition_0.empty_copy())  # No valid Composition made


class RC_Clips(RC_Callables):
    pass

class RC_Splitter(RC_Clips):
    def __init__(self, elements: int = 8,
                 chaos: ch.Chaos = ch.SinX(340),
                 extra_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 packed_repeats: int = 1, max_tries: int = 100, no_repetitions: bool = True):
        super().__init__(chaos, extra_exclusion, post_processing, packed_repeats, max_tries, no_repetitions)
        self._elements: int = elements


    def _single_iteration(self, decoupled_clip_0: 'oc.Clip') -> 'oc.Clip':
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        total_duration_beats = Fraction(0)
        for single_element in decoupled_clip_0._foreground_items():
            total_duration_beats += single_element._duration_beats
        try_i: int = 0
        while try_i < 100:
            iteration_clip: oc.Clip = decoupled_clip_0.copy() # Despite the clip_0 being already a copy, each iteration needs a new one
            try_j: int = 0
            while iteration_clip.len() < self._elements and try_j < 100 * 2:
                continuous_split_step: int = self._chaos % int()
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
                if iteration_clip.len() == self._elements:
                    return iteration_clip
                try_j += 1
            try_i += 1
        decoupled_clip_0._index = -1    # Tags as invalid
        return decoupled_clip_0


class RC_Chooser(RC_Clips):
    def __init__(self, parameters: list[Any] = ["1", "3", "5"],
                 chaos: ch.Chaos = ch.SinX(340),
                 extra_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 packed_repeats: int = 1, max_tries: int = 100, no_repetitions: bool = True):
        super().__init__(chaos, extra_exclusion, post_processing, packed_repeats, max_tries, no_repetitions)
        self._parameters: list[Any] = parameters


    def _single_iteration(self, decoupled_clip_0: 'oc.Clip') -> 'oc.Clip':
        if self._parameters:
            total_parameters: int = len(self._parameters)
            for element in decoupled_clip_0._foreground_items():
                index_choice: int = self._chaos % int()
                chosen_parameter = self._parameters[index_choice % total_parameters]
                element << chosen_parameter
        decoupled_clip_0._index = self._index
        return decoupled_clip_0  # The Clip is already decoupled


