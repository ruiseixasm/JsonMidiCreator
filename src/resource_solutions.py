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
import resource_operands as ro


class RS_Solutions:
    def __init__(self,
                 seed: oc.Composition,
                 iterations: list[int] = [1, 0, 0, 0],
                 measures: int = 1,
                 composition: Optional['oc.Composition'] = None,
                 by_channel: bool = False
            ):
        self._seed: oc.Composition = seed.copy()    # Avoids changing the source Composition
        self._solution: oc.Composition = self._seed
        self._iterations: list[int] = iterations
        self._measures: int = max(measures, 1)
        self._composition: oc.Composition = composition
        self._by_channel: bool = by_channel


    def seed(self) -> 'oc.Composition':
        return self._seed
    
    def solution(self) -> 'oc.Composition':
        return self._solution
    
    def mask(self, *conditions) -> Self:
        self._solution = self._solution.mask(*conditions)
        return self

    def unmask(self) -> Self:
        self._solution = self._solution.base()
        return self


    def iterate(self, iterations: int,
                iterator: Callable[[list | int | float | Fraction, 'oc.Composition'], 'oc.Composition'],
                chaos: ch.Chaos,
                triggers: list | int | float | Fraction,
                title: str = "") -> Self:
        
        def _n_button(composition: 'oc.Composition') -> 'oc.Composition':
            return composition
        # Where the solution is set
        return self.solutionize(iterations, _n_button, title)

    def solutionize(self, iterations: int,
                    n_button: Callable[['oc.Composition'], 'oc.Composition'],
                    title: str = "") -> Self:
        """Where the solution is set"""
        if iterations < 0:
            self._solution >>= og.Plot(by_channel=self._by_channel,
                iterations=iterations * -1,
                n_button=n_button, composition=self._composition, title=title
            )
        else:
            self._solution >>= og.Call(iterations, n_button)
        return self



class RS_Clip(RS_Solutions):
    def __init__(self,
                 seed: oc.Clip,
                 iterations: list[int] = [1, 0, 0, 0],
                 measures: int = 1,
                 composition: Optional['oc.Composition'] = None,
                 by_channel: bool = False
            ):
        super().__init__(seed, iterations, measures, composition, by_channel)
         
    def seed(self) -> 'oc.Clip':
        return self._seed
    
    def solution(self) -> 'oc.Clip':
        return self._solution
    
    
    def iterate(self, iterations: int,
                iterator: Callable[[list | int | float | Fraction, 'oc.Composition'], 'oc.Composition'],
                chaos: ch.Chaos,
                triggers: list | int | float | Fraction,
                title: str = "") -> Self:
        
        def _n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                # Makes sure composition is split first by the the given measures
                for index, _ in enumerate(self._iterations):
                    composition //= ra.Measure(self._measures * index)
                iteration_measures: list[int] = o.list_increment(self._measures)
                if isinstance(triggers, list):
                    measure_triggers: list = triggers   # No need to copy, Chaos does the copy
                results: list = None
                # Here is where each Measure is processed
                new_composition: oc.Composition = composition.empty_copy()
                for iteration_i, measure_iterations in enumerate(self._iterations):
                    composition_measures: list[int] = o.list_add(iteration_measures, self._measures * iteration_i)
                    segmented_composition: oc.Composition = composition * composition_measures
                    if measure_iterations < 0:  # Repeats previous measures unaltered
                        new_composition *= segmented_composition
                    else:   # measure_iterations >= 0
                        if measure_iterations > 0:
                            if not isinstance(triggers, list):
                                measure_triggers: list = [triggers] * segmented_composition.len()
                            results = chaos.reset_tamers().iterate(measure_iterations - 1) % measure_triggers
                            new_composition *= iterator(results, segmented_composition) * iteration_measures
                        elif results is None:
                            new_composition *= segmented_composition
                        else:
                            new_composition *= iterator(results, segmented_composition) * iteration_measures
                return new_composition
            return composition
        # Where the solution is set
        return self.solutionize(iterations, _n_button, title)


    def my_n_button(self,
            iterations: int = 1,
            n_button: Callable[['oc.Composition'], 'oc.Composition'] | None = None,
            title: str | None = None) -> Self:
        """
        Processes the user defined `n_button` associated to the `plot` method.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip) and callable(n_button):
                return n_button(segmented_composition)
            return segmented_composition
        
        if not isinstance(title, str):
            title = "My N Button"
        return self.iterate(iterations, _iterator, ch.Chaos(), [1], title)


    def multi_splitter(self,
            iterations: int = 1,
            durations: list[float] = o.list_repeat([1/8 * 3/2, 1/8, 1/16, 1/32], [1, 4, 8, 2]),
            chaos: ch.Chaos = ch.SinX(340),
            title: str | None = None) -> Self:
        """
        Splits the entire clip along multiple durations
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                split_position: ra.Position = ra.Position(segmented_composition, 0)
                segmented_durations: list[float] = o.list_choose(durations, results)
                for duration in segmented_durations:
                    split_position += ra.Duration(segmented_composition, duration)
                    segmented_composition //= split_position
            return segmented_composition

        if not isinstance(title, str):
            title = "Multi Splitter"
        triggers: list[int] = [1] * len(durations)
        return self.iterate(iterations, _iterator, chaos, triggers, title)


    def rhythm_fast_quantized(self,
            iterations: int = 1,
            durations: list[float] = [1/8 * 3/2, 1/8, 1/16 * 3/2, 1/16, 1/32 * 3/2, 1/32],
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.SinX(340),
            title: str | None = None) -> Self:
        """
        Distributes small note values among the elements
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                new_durations: list[float] = o.list_choose(durations, results)
                segmented_composition << of.Foreach(*new_durations)**ra.NoteValue()
                # These operations shall be done on the base (single Measure)
                segmented_composition.base().stack().quantize().mul([0]).link()
            return segmented_composition

        if not isinstance(title, str):
            title = "Rhythm Fast Quantized"
        return self.iterate(iterations, _iterator, chaos, triggers, title)


    def tonality_conjunct(self,
            iterations: int = 1,
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.Cycle(ra.Modulus(7), ot.Conjunct())**ch.SinX(),
            title: str | None = None) -> Self:
        """
        Adjusts the pitch of each Note in Conjunct whole steps of 0 or 1.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                segmented_composition += of.Foreach(*results)**ou.Degree()
            return segmented_composition

        if not isinstance(title, str):
            title = "Tonality Conjunct"
        return self.iterate(iterations, _iterator, chaos, triggers, title)


    def tonality_conjunct_but_slacked(self,
            iterations: int = 1,
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.Cycle(ra.Modulus(7), ot.Conjunct(ra.Strictness(.75)))**ch.SinX(),
            title: str | None = None) -> Self:
        """
        Adjusts the pitch of each `Note` in Conjunct whole steps of 0 or 1 except in 25% of the times.
        """
        if not isinstance(title, str):
            title = "Tonality Conjunct But Slacked"
        return self.tonality_conjunct(iterations, triggers, chaos, title)


    def sweep_sharps(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(0, ra.Modulus(8)),
            title: str | None = None) -> Self:
        """
        Sweeps all possible sharps for the set Key Signature for all Notes.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                new_key_signature = ou.KeySignature(results[0])  # One iteration
                segmented_composition << new_key_signature << ou.TonicKey(-1)
            return segmented_composition

        if not isinstance(title, str):
            title = "Sweep Sharps"
        return self.iterate(iterations, _iterator, chaos, [1], title)


    def sweep_flats(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(0, ra.Modulus(8)),
            title: str | None = None) -> Self:
        """
        Sweeps all possible flats for the set Key Signature for all Notes.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                new_key_signature = ou.KeySignature(results[0] * -1)  # One iteration
                segmented_composition << new_key_signature << ou.TonicKey(-1)
            return segmented_composition

        if not isinstance(title, str):
            title = "Sweep Flats"
        return self.iterate(iterations, _iterator, chaos, [1], title)


    def sprinkle_accidentals(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Flipper(ra.Modulus(6))**ch.SinX(33),
            title: str | None = None) -> Self:
        """
        Sets accidentals on each measure `Note` accordingly to the set `Chaos`.
        """
        last_accidental: int = 0
        
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            nonlocal last_accidental
            if isinstance(segmented_composition, oc.Clip):
                for single_note in segmented_composition:
                    if isinstance(single_note, oe.Note) and results[0] and chaos % 1:
                        if last_accidental == 0:
                            last_accidental = 1
                            accidental_degree: ou.Degree = ou.Degree(0.1)   # Sharp
                        elif last_accidental > 0:
                            last_accidental = -1
                            accidental_degree: ou.Degree = ou.Degree(0.2)   # Flat
                        else:
                            last_accidental = 0
                            accidental_degree: ou.Degree = ou.Degree(0.0)   # Natural
                        single_note << accidental_degree
            return segmented_composition

        if not isinstance(title, str):
            title = "Sprinkle Accidentals"
        return self.iterate(iterations, _iterator, chaos, 1, title)


    def fine_tune(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(33),
            tune_by: ra.Rational = ra.Step(1),
            title: str | None = None) -> Self:
        """
        Does a single tune, intended to do fine tunning in a chained sequence of tiny changes.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                clip_len: int = segmented_composition.len()
                if clip_len > 0:
                    clip_pick: int = results[0] % clip_len
                    segmented_composition[clip_pick] += tune_by
            return segmented_composition

        if not isinstance(title, str):
            title = "Fine Tune"
        return self.iterate(iterations, _iterator, chaos, [1], title)


    def single_wrapper(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(33),
            wrapper: oe.Element = oe.Retrigger(),
            title: str | None = None) -> Self:
        """
        Wraps a single element in the `Clip` picked by `Chaos`.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                clip_len: int = segmented_composition.len()
                if clip_len > 0:
                    clip_pick: int = results[0] % clip_len
                    # Transforms the original Element into another one
                    segmented_composition[clip_pick] = wrapper.copy(segmented_composition[clip_pick])
            return segmented_composition

        if not isinstance(title, str):
            title = "Single Wrapper"
        return self.iterate(iterations, _iterator, chaos, [1], title)


    def multi_wrapper(self,
            iterations: int = 1,
            durations: list[float] = o.list_repeat([oe.Note(), oe.Triplet(), oe.Cluster()], [6, 1, 2]),
            chaos: ch.Chaos = ch.SinX(340),
            title: str | None = None) -> Self:
        """
        Wraps each element in the `Clip` chosen by `Chaos`.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                split_position: ra.Position = ra.Position(segmented_composition, 0)
                segmented_durations: list[float] = o.list_choose(durations, results)
                for duration in segmented_durations:
                    split_position += ra.Duration(segmented_composition, duration)
                    segmented_composition //= split_position
            return segmented_composition

        if not isinstance(title, str):
            title = "Multi Wrapper"
        return self.iterate(iterations, _iterator, chaos, [1], title)


    def swap_elements(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(25, ot.Different()**ot.Modulo(8)),
            title: str | None = None) -> Self:
        """
        Swaps the place of two elements, no swaps if both picked are the same.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                clip_len: int = segmented_composition.len()
                if clip_len > 0:
                    loci: list[og.Locus] = segmented_composition % [og.Locus()]
                    # Swap elements
                    first_pick: int = results[0] % clip_len
                    second_pick: int = results[1] % clip_len
                    first_element: oe.Element = segmented_composition[first_pick]
                    second_element: oe.Element = segmented_composition[second_pick]
                    segmented_composition._swap(first_element, second_element)
                    # Replaces the respective locus
                    for locus, element in zip(loci, segmented_composition):
                        element << locus
                    # Needs to be sorted due to secondary sorting criteria like Pitch and Channel
                    segmented_composition._sort_items()
            return segmented_composition

        if not isinstance(title, str):
            title = "Swap Elements"
        return self.iterate(iterations, _iterator, chaos, [1, 1], title)


    def swap_loci(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(25, ot.Different()**ot.Modulo(8)),
            title: str | None = None) -> Self:
        """
        Swaps the position of two loci, no swaps if both picked are the same.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                clip_len: int = segmented_composition.len()
                if clip_len > 0:
                    composition_loci: list[og.Locus] = segmented_composition % [og.Locus()]
                    original_durations: list[ra.Duration] = o.list_get(composition_loci, ra.Duration())
                    # Swap loci durations
                    swapped_durations: list[ra.Duration] = o.list_swap(original_durations, results[0], results[1])
                    position_offset: Fraction = Fraction(0)
                    for locus, original_duration, swapped_duration in zip(composition_loci, original_durations, swapped_durations):
                        locus << swapped_duration
                        locus._position_beats += position_offset
                        position_offset += swapped_duration._rational - original_duration._rational
                    # Replaces the respective locus
                    for locus, element in zip(composition_loci, segmented_composition):
                        element << locus
                    # Needs to be sorted due to secondary sorting criteria like Duration
                    segmented_composition._sort_items()
            return segmented_composition

        if not isinstance(title, str):
            title = "Swap Loci"
        return self.iterate(iterations, _iterator, chaos, [1, 1], title)


    def process_parameterization(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(ra.Modulus(4))**ch.SinX(25),
            process: og.Process = og.Swap(),
            parameter: str = 'right',
            title: str | None = None) -> Self:
        """
        Applies a given process with chaotic parametrization.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                clip_len: int = segmented_composition.len()
                if clip_len:
                    process[parameter] = results[0]
                    segmented_composition >>= process
            return segmented_composition

        if not isinstance(title, str):
            title = "Process Parameterization"
        return self.iterate(iterations, _iterator, chaos, [1], title)


    def set_parameter(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(25, ot.Minimum(60)**ot.Modulo(120)),
            parameter: any = ou.Velocity(),
            title: str | None = None) -> Self:
        """
        Applies a given parameter with the given chaos.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                for single_element, single_result in zip(segmented_composition, results):
                    single_element << single_result
            return segmented_composition

        if not isinstance(title, str):
            title = "Set Parameter"
        return self.iterate(iterations, _iterator, chaos, parameter, title)


class RS_Part(RS_Solutions):
    pass



class RS_Song(RS_Solutions):
    pass
    

