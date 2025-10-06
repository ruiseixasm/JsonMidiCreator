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
        if isinstance(seed, oe.Element):
            seed = oc.Clip(seed)
        self._seed: oc.Composition = seed.copy()    # Avoids changing the source Composition
        self._solution: oc.Composition = self._seed
        self._iterations: list[int] = iterations
        self._measures: int = max(measures, 1)
        if isinstance(composition, oe.Element):
            composition = oc.Clip(seed)
        self._composition: oc.Composition = composition
        self._by_channel: bool = by_channel


    def seed(self, *parameters) -> 'oc.Composition':
        return self._seed << parameters
    
    def solution(self, *parameters) -> 'oc.Composition':
        return self._solution << parameters

    
    def set(self, *parameters) -> Self:
        self._solution << parameters
        return self
    
    def mask(self, *conditions) -> Self:
        self._solution.mask(*conditions)
        return self

    def unmask(self) -> Self:
        self._solution.unmask()
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
        if iterations > 0:
            self._solution >>= og.Plot(by_channel=self._by_channel, iterations=iterations,
                n_button=n_button, composition=self._composition, title=title
            )
        else:
            self._solution >>= og.Call(iterations * -1, n_button)
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
         
    def seed(self, *parameters) -> 'oc.Clip':
        return self._seed << parameters
    
    def solution(self, *parameters) -> 'oc.Clip':
        return self._solution << parameters
    
    
    def iterate(self, iterations: int,
                iterator: Callable[[list | int | float | Fraction, 'oc.Composition'], 'oc.Composition'],
                chaos: ch.Chaos,
                triggers: int | float | Fraction,
                title: str = "") -> Self:
        
        def _n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                # Makes sure the ENTIRE composition is split first by the the given measures
                masked: bool = composition._masked
                measure: ra.Measure = ra.Measure(0)
                composition._masked = False
                for _ in self._iterations:
                    measure += self._measures
                    composition //= measure
                composition._masked = masked

                iteration_measures: list[int] = o.list_increment(self._measures)
                previous_measures: list[int] = []
                if triggers > 0:
                    measure_triggers: list = [triggers] * int(triggers)
                results: list = None
                # Here is where each Measure is processed
                new_composition: oc.Composition = composition.empty_copy()
                for iteration_i, measure_iterations in enumerate(self._iterations):
                    if measure_iterations == 0:
                        new_composition *= new_composition * previous_measures
                    else:
                        composition_measures: list[int] = o.list_add(iteration_measures, self._measures * iteration_i)
                        segmented_composition: oc.Composition = composition * composition_measures
                        if measure_iterations > 0:
                            if not triggers > 0:
                                measure_triggers: list = [triggers] * segmented_composition.len()
                            results = measure_triggers >> chaos.iterate(measure_iterations - 1)
                            new_composition *= iterator(results, segmented_composition) * iteration_measures
                            chaos.reset_tamers()
                        else:   # measure_iterations < 0
                            new_composition *= segmented_composition
                        previous_measures = o.list_add(iteration_measures, self._measures * iteration_i)
                return new_composition
            return composition
        # Where the solution is set
        return self.solutionize(iterations, _n_button, title)


# USER METHODS

    def user_n_button(self,
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
        return self.iterate(iterations, _iterator, ch.Chaos(), 1, title)



# DURATION METHODS

    def duration_splitter(self,
            iterations: int = 1,
            durations: list[float] = o.list_repeat([1/4, 1/8 * 3/2, 1/8, 1/16, 1/32], [8, 1, 4, 6, 2]),
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
            title = "Duration Splitter"
        return self.iterate(iterations, _iterator, chaos, len(durations), title)


    def duration_rearrangement(self,
            iterations: int = 1,
            durations: list[float] = o.list_repeat([1/4, 1/8 * 3/2, 1/8, 1/16, 1/32], [8, 1, 4, 6, 2]),
            normalize: bool = True,
            quantization_amount: float = 1.0,
            chaos: ch.Chaos = ch.SinX(340),
            title: str | None = None) -> Self:
        """
        Distributes the given Durations or existing ones if `0` is given.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):

                segmented_durations: list[float] = o.list_choose(durations, results)
                total_duration_beats: Fraction = Fraction(0)
                for single_element in segmented_composition._unmasked_items():
                    total_duration_beats += single_element._duration_beats

                total_elements: int = segmented_composition.len()
                if total_elements > 1 and segmented_durations:

                    splits_positions: set[Fraction] = set()
                    next_position_beats: Fraction = Fraction(0)
                    duration_index: int = 0

                    if normalize:

                        while len(splits_positions) < total_elements:
                            next_duration: Fraction = ra.Duration(
                                    segmented_composition,
                                    segmented_durations[duration_index % len(segmented_durations)]
                                ) % Fraction()
                            if next_duration <= Fraction(0):
                                next_duration = segmented_composition[duration_index % total_elements]._duration_beats
                            next_position_beats += next_duration
                            if Fraction(0) < next_position_beats % total_duration_beats < total_duration_beats:
                                splits_positions.add(
                                    next_position_beats % total_duration_beats
                                )
                            duration_index += 1
                        
                    else:

                        while len(splits_positions) < total_elements - 1:
                            next_duration: Fraction = ra.Duration(
                                    segmented_composition,
                                    segmented_durations[duration_index % len(segmented_durations)]
                                ) % Fraction()
                            if next_duration <= Fraction(0):
                                next_duration = segmented_composition[duration_index % total_elements]._duration_beats
                            next_position_beats += next_duration
                            if Fraction(0) < next_position_beats % total_duration_beats < total_duration_beats:
                                splits_positions.add(
                                    next_position_beats % total_duration_beats
                                )
                            duration_index += 1
                        
                        splits_positions.add(total_duration_beats)
                    
                    sorted_splits_positions: list[Fraction] = sorted(list(splits_positions))

                    if normalize:
                        last_split_position: Fraction = sorted_splits_positions[-1]
                        expand_ratio: Fraction = total_duration_beats / last_split_position
                        for index, _ in enumerate(sorted_splits_positions):
                            sorted_splits_positions[index] *= expand_ratio

                    next_position_offset: Fraction = Fraction(0)
                    for element, split_position_0 in zip(segmented_composition, sorted_splits_positions):
                        split_position: Fraction = segmented_composition[0]._position_beats + split_position_0
                        element._position_beats += next_position_offset
                        next_position_offset += split_position - (element._position_beats + element._duration_beats)
                        element._duration_beats = split_position - element._position_beats
                    
                    quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
                    amount_rational: Fraction = ra.Amount(quantization_amount) % Fraction()
                    previous_element: oe.Element | None = None
                    for index, single_element in enumerate(segmented_composition._unmasked_items()):
                        if previous_element is not None:

                            element_position_on: Fraction = single_element._position_beats
                            unquantized_amount: Fraction = element_position_on % quantization_beats
                            quantization_limit: int = round(unquantized_amount / quantization_beats)
                            position_on_offset: Fraction = (quantization_limit * quantization_beats - unquantized_amount) * amount_rational
                            while position_on_offset <= previous_element._duration_beats:
                                position_on_offset += quantization_beats    # A simplification
                            while position_on_offset >= single_element._duration_beats:
                                position_on_offset -= quantization_beats
                            single_element._position_beats += position_on_offset
                            single_element._duration_beats -= position_on_offset
                            previous_element._duration_beats += position_on_offset

                        previous_element = single_element

                    segmented_composition._sort_items()

            return segmented_composition

        if not isinstance(title, str):
            title = "Duration Rearrangement"
        return self.iterate(iterations, _iterator, chaos, len(durations), title)


    def duration_fast_rhythm(self,
            iterations: int = 1,
            durations: list[float] = [1/8 * 3/2, 1/8, 1/16 * 3/2, 1/16, 1/32 * 3/2, 1/32],
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
                segmented_composition.stack().quantize().mul([0]).link()
            return segmented_composition

        if not isinstance(title, str):
            title = "Duration Fast Rhythm"
        return self.iterate(iterations, _iterator, chaos, len(durations), title)


# PITCH METHODS

    def pitch_similar_motion(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(ot.Decrease(3)**ot.Modulo(6)),
            pitch_parameter: ou.PitchParameter = ou.Degree(),
            title: str | None = None) -> Self:
        """
        Adjusts the `Degree` of each `Note` while respecting the original motion pattern.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                if chaos._tamer._index > 0:
                    clip_pitches: list = segmented_composition % of.InputType(oe.Note)**[og.Pitch(), int()]
                    if clip_pitches:
                        clip_pattern: list[int] = []
                        for index, pitch in enumerate(clip_pitches):
                            if index == 0:
                                clip_pattern.append(results[0])
                            else:
                                clip_pattern.append(pitch - clip_pitches[index - 1])
                        pattern_chaos._tamer << clip_pattern    # Updates the Pattern tamer
                        pattern_results: list[int] = clip_pattern >> pattern_chaos
                        segmented_composition << \
                            of.InputType(oe.Note)**of.Previous(od.Pipe(pitch_parameter), first_null=False)**of.Add(*pattern_results)**od.Pipe()
                        pattern_chaos.reset_tamers()
            return segmented_composition

        if not isinstance(title, str):
            title = f"Pitch Similar Motion of {pitch_parameter.__class__.__name__}"
        pattern_chaos: ch.Chaos = chaos.copy()
        pattern_chaos << ot.Pattern()**pattern_chaos._tamer # Expands tamer with Pattern
        return self.iterate(iterations, _iterator, chaos, 1, title)

    def pitch_contrary_motion(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(ot.Decrease(3)**ot.Modulo(6)),
            pitch_parameter: ou.PitchParameter = ou.Degree(),
            title: str | None = None) -> Self:
        """
        Adjusts the `Degree` of each `Note` while respecting the original motion pattern.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                if chaos._tamer._index > 0:
                    clip_pitches: list = segmented_composition % of.InputType(oe.Note)**[og.Pitch(), int()]
                    clip_pitches = o.list_mul(clip_pitches, -1) # Reverses the pitches pattern
                    if clip_pitches:
                        clip_pattern: list[int] = []
                        for index, pitch in enumerate(clip_pitches):
                            if index == 0:
                                clip_pattern.append(results[0])
                            else:
                                clip_pattern.append(pitch - clip_pitches[index - 1])
                        pattern_chaos._tamer << clip_pattern    # Updates the Pattern tamer
                        pattern_results: list[int] = clip_pattern >> pattern_chaos
                        segmented_composition << \
                            of.InputType(oe.Note)**of.Previous(od.Pipe(pitch_parameter), first_null=False)**of.Add(*pattern_results)**od.Pipe()
                        pattern_chaos.reset_tamers()
            return segmented_composition

        if not isinstance(title, str):
            title = f"Pitch Contrary Motion of {pitch_parameter.__class__.__name__}"
        pattern_chaos: ch.Chaos = chaos.copy()
        pattern_chaos << ot.Pattern()**pattern_chaos._tamer # Expands tamer with Pattern
        return self.iterate(iterations, _iterator, chaos, 1, title)


    def pitch_tonality_conjunct(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(ra.Modulus(7), ot.Conjunct())**ch.SinX(),
            triggers: int | float | Fraction = 7,
            title: str | None = None) -> Self:
        """
        Adjusts the pitch of each Note in Conjunct whole steps of 0 or 1.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                segmented_composition += of.Foreach(*results)**ou.Degree()
            return segmented_composition

        if not isinstance(title, str):
            title = "Pitch Tonality Conjunct"
        return self.iterate(iterations, _iterator, chaos, triggers, title)


    def pitch_tonality_conjunct_but_slacked(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(ra.Modulus(7), ot.Conjunct(ra.Strictness(.75)))**ch.SinX(),
            triggers: int = 7,
            title: str | None = None) -> Self:
        """
        Adjusts the pitch of each `Note` in Conjunct whole steps of 0 or 1 except in 25% of the times.
        """
        if not isinstance(title, str):
            title = "Pitch Tonality Conjunct But Slacked"
        return self.pitch_tonality_conjunct(iterations, chaos, triggers, title)



    def pitch_sweep_sharps(self,
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
            title = "Pitch Sweep Sharps"
        return self.iterate(iterations, _iterator, chaos, 1, title)


    def pitch_sweep_flats(self,
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
            title = "Pitch Sweep Flats"
        return self.iterate(iterations, _iterator, chaos, 1, title)


    def pitch_sprinkle_accidentals(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(33, ot.Switch()**ot.Modulo(6)),
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
            title = "Pitch Sprinkle Accidentals"
        return self.iterate(iterations, _iterator, chaos, 0, title)


# PARAMETER METHODS

    def parameter_measure(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.SinX(ot.Decrease(3)**ot.Modulo(6)),
            parameter: any = ou.Degree(),
            title: str | None = None) -> Self:
        """
        Processes the imputed parameter to be added for each `Measure`.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                new_foreach_measure: of.Frame = of.Mux(ra.Measure())**of.Foreach(*results)**parameter
                return segmented_composition.add(new_foreach_measure)
            return segmented_composition
        
        if not isinstance(title, str):
            title = "Parameter Measure"
        return self.iterate(iterations, _iterator, chaos, self._measures, title)


    def parameter_shuffled(self,
            iterations: int = 1,
            parameter: Any = og.Locus(),
            chaos: ch.Chaos = ch.SinX(),
            title: str | None = None) -> Self:
        """
        Shuffles a given parameter among the unmasked elements in the original `Composition`.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                nonlocal parameter  # This binds the outer parameter to the inner function
                existent_parameters: list = segmented_composition % [parameter]
                picked_parameters: list = []
                for result in results:
                    picked_parameters.append( existent_parameters.pop(result % len(existent_parameters)) )
                for single_element, shuffled_parameter in zip(segmented_composition, picked_parameters):
                    single_element << shuffled_parameter
                segmented_composition._sort_items() # Necessary because setting the elements directly doesn't do it
            return segmented_composition

        if not isinstance(title, str):
            title = "Parameter Shuffled"
        return self.iterate(iterations, _iterator, chaos, 0, title)



    def parameter_single_element(self,
            iterations: int = 1,
            parameter: Any = ra.Step(1),
            chaos: ch.Chaos = ch.SinX(33),
            title: str | None = None) -> Self:
        """
        Does a single tune, intended to do fine tunning in a chained sequence of tiny changes.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                clip_len: int = segmented_composition.len()
                if clip_len > 0:
                    clip_pick: int = results[0] % clip_len
                    segmented_composition[clip_pick] += parameter
            return segmented_composition

        if not isinstance(title, str):
            title = "Parameter Single Element"
        return self.iterate(iterations, _iterator, chaos, 1, title)


    def parameter_global_set(self,
            iterations: int = 1,
            parameter: any = of.Equal(ra.Measure(1))**ou.KeySignature(),
            chaos: ch.Chaos = ch.SinX(25, ot.Decrease(3)**ot.Modulo(7)),
            title: str | None = None) -> Self:
        """
        Sets a given parameter to the entire `Clip`.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                if isinstance(parameter, o.Operand):
                    parameter << results[0]
                segmented_composition << parameter
            return segmented_composition
        
        if not isinstance(title, str):
            title = "Parameter Global Set"
        return self.iterate(iterations, _iterator, chaos, Fraction(1), title)


    def parameter_global_add(self,
            iterations: int = 1,
            parameter: any = of.Even()**ra.Position()**ra.Steps(),
            chaos: ch.Chaos = ch.SinX(25, ot.Modulo(3)),
            title: str | None = None) -> Self:
        """
        Adds a given parameter to the entire `Clip`.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                if isinstance(parameter, o.Operand):
                    parameter << results[0]
                segmented_composition += parameter
            return segmented_composition
        
        if not isinstance(title, str):
            title = "Parameter Global Add"
        return self.iterate(iterations, _iterator, chaos, Fraction(1), title)


    def process_parameterization(self,
            iterations: int = 1,
            process: og.Process = og.Swap(),
            parameter: str = 'right',
            chaos: ch.Chaos = ch.Cycle(ra.Modulus(4))**ch.SinX(25),
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
        return self.iterate(iterations, _iterator, chaos, 1, title)


    def set_parameter(self,
            iterations: int = 1,
            parameter: any = ou.Velocity(),
            chaos: ch.Chaos = ch.SinX(25, ot.Minimum(60)**ot.Modulo(120)),
            triggers: int | float | Fraction = 0,
            title: str | None = None) -> Self:
        """
        Applies a given parameter with the given chaos.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                parameter_results: list = results
                if isinstance(parameter, o.Operand):
                    parameter_results = o.list_wrap(results, parameter)
                segmented_composition << of.Foreach(*parameter_results)
            return segmented_composition
        
        if not isinstance(title, str):
            title = "Set Parameter"
        return self.iterate(iterations, _iterator, chaos, triggers, title)


    def operate_parameter(self,
            iterations: int = 1,
            parameter: Any = ou.Degree(),
            operator: Callable[['oe.Element', Any], Any] = lambda element, result: element.add(result),
            chaos: ch.Chaos = ch.SinX(ot.Increase(1)**ot.Modulo(7)),
            triggers: int | float | Fraction = 0,
            title: str | None = None) -> Self:
        """
        Applies any operator between elements and computed values.
        
        Args:
            iterations: Number of iterations
            chaos: Chaos generator for values
            parameter: Parameter to compute values from
            operator: Function that takes (element, value) and applies operation
            title: Optional title for the operation
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                parameter_results: list = results
                if isinstance(parameter, o.Operand):
                    parameter_results = o.list_wrap(results, parameter)
                for index, single_element in enumerate(segmented_composition):
                    operator(single_element, parameter_results[index % len(results)])  # Apply custom operator
            return segmented_composition

        if not isinstance(title, str):
            title = "Operate Parameter"
        
        return self.iterate(iterations, _iterator, chaos, triggers, title)



# WRAPPER METHODS

    def wrapper_single_element(self,
            iterations: int = 1,
            wrappers: list['oe.Element'] = [oe.Triplet(), oe.Cluster()],
            chaos: ch.Chaos = ch.SinX(33),
            title: str | None = None) -> Self:
        """
        Wraps a single element in the `Clip` picked by `Chaos`.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                clip_len: int = segmented_composition.len()
                if clip_len > 0:
                    element_pick: int = results[0] % clip_len
                    wrapper: oe.Element = wrappers[results[1] % len(wrappers)]
                    if isinstance(wrapper, oe.Element):
                        # Transforms the original Element into another one
                        segmented_composition[element_pick] = wrapper.copy(segmented_composition[element_pick])
            return segmented_composition

        if not isinstance(title, str):
            title = "Wrapper Single Element"
        return self.iterate(iterations, _iterator, chaos, 2, title)


    def wrapper_multi_element(self,
            iterations: int = 1,
            wrappers: list['oe.Element'] = o.list_repeat([oe.Note(), oe.Triplet(), oe.Cluster()], [6, 1, 2]),
            chaos: ch.Chaos = ch.SinX(340),
            title: str | None = None) -> Self:
        """
        Wraps each element in the `Clip` chosen by `Chaos`.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                segmented_wrappers: list[oe.Element] = o.list_choose(wrappers, results)
                for single_element, wrapper in zip(segmented_composition, segmented_wrappers):
                    if isinstance(wrapper, oe.Element):
                        segmented_composition._replace(single_element, wrapper.copy(single_element))
            return segmented_composition

        if not isinstance(title, str):
            title = "Wrapper Multi Element"
        return self.iterate(iterations, _iterator, chaos, 0, title)



# LOCUS METHODS

    def locus_swap_elements(self,
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
            title = "Locus Swap Elements"
        return self.iterate(iterations, _iterator, chaos, 2, title)


    def locus_swap_loci(self,
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
            title = "Locus Swap Loci"
        return self.iterate(iterations, _iterator, chaos, 2, title)





    def match_time_signature(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Ripple(ra.Steps(5)),
            title: str | None = None) -> Self:
        """
        Readjusts the Time Signature `Tempo` without changing the composition timing.
        """
        def _iterator(results: list, segmented_composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(segmented_composition, oc.Clip):
                original_tempo: Fraction = og.settings % ra.Tempo() % Fraction()
                new_tempo: Fraction = original_tempo + results[0]
                tempo_ratio: Fraction = new_tempo / original_tempo
                for element in segmented_composition:
                    element *= tempo_ratio
            return segmented_composition

        if not isinstance(title, str):
            title = "Match Time Signature"
        return self.iterate(iterations, _iterator, chaos, 1, title)


class RS_Part(RS_Solutions):
    pass



class RS_Song(RS_Solutions):
    pass
    

