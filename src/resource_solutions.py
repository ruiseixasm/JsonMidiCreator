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


class RS_Solutions:
    def __init__(self,
                 seed: oc.Composition,
                 measures: list[int] = [0, 0, 0, 0],
                 c_button: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 title: str | None = None):
        self._seed: oc.Composition = seed
        self._measures: list[int] = measures
        self._c_button = c_button
        self._title: str | None = title


    def solution(self) -> 'oc.Composition':
        return self._seed
    
    def mask(self, *conditions) -> Self:
        self._seed = self._seed.mask(*conditions)
        return self

    def unmask(self) -> Self:
        self._seed = self._seed.base()
        return self


    def iterate(self, iterations,
                measure_iterator: Callable[[list | int | float | Fraction], 'oc.Composition'],
                chaos: ch.Chaos,
                triggers: list | int | float | Fraction,
                by_channel: bool = False,
                title: str = "") -> Self:

        # Resets parameters for the next Solution
        _choices = None

        def _n_button(composition: 'oc.Composition') -> 'oc.Composition':
            nonlocal _choices
            new_composition: oc.Composition = composition.empty_copy()
            # Each iteration results in new choices
            if isinstance(triggers, list):
                measure_triggers: list = triggers
            else:
                measure_triggers: list = [triggers] * composition.len()
            _choices = chaos.reset_tamers() % measure_triggers
            # Here is where each Measure is processed
            for measure_i, measure_iterations in enumerate(self._measures):
                if measure_iterations >= 0:
                    if isinstance(triggers, list):
                        measure_triggers: list = triggers
                    else:
                        measure_triggers: list = [triggers] * (composition * [measure_i]).len()
                    if measure_iterations > 0:
                        _choices = chaos.reset_tamers() * (measure_iterations - 1) % measure_triggers
                    new_composition *= measure_iterator(_choices, measure_i, composition) * [0]
                else:
                    new_composition *= composition * [measure_i]
            return new_composition

        if iterations < 0:
            if isinstance(self._title, str):
                title = self._title
            self._seed >>= og.Plot(by_channel=by_channel,
                iterations=iterations * -1,
                n_button=_n_button, c_button=self._c_button, title=title
            )
        else:
            self._seed >>= og.Call(iterations, _n_button)
        return self



class RS_Clip(RS_Solutions):
    def __init__(self,
                 seed: oc.Composition,
                 measures: list[int] = [0, 0, 0, 0],
                 c_button: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 title: str | None = None):
        super().__init__(seed, measures, c_button, title)
        self._seed: oc.Clip = seed
         
    def solution(self) -> 'oc.Clip':
        return self._seed
    

    def my_n_button(self,
            iterations: int = 1,
            n_button: Callable[['oc.Composition'], 'oc.Composition'] | None = None,
            by_channel: bool = False,
            title: str | None = None) -> Self:
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip) and callable(n_button):
                return n_button(composition * [measure_i])
            return composition
        
        if not isinstance(title, str):
            title = "My N Button"
        return self.iterate(iterations, _measure_iterator, ch.Chaos(), [1], by_channel, title)


    def rhythm_fast_quantized(self,
            iterations: int = 1,
            durations: list[float] = [1/8 * 3/2, 1/8, 1/16 * 3/2, 1/16, 1/32 * 3/2, 1/32],
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.SinX(340),
            by_channel: bool = False,
            title: str | None = None) -> Self:
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                measure_clip: oc.Clip = self._seed.copy()
                new_durations: list[float] = o.list_choose(durations, choices)
                measure_clip << of.Foreach(*new_durations)**ra.NoteValue()
                # These operations shall be done on the base (single Measure)
                measure_clip.base().stack().quantize().mul([0]).link()
                return measure_clip
            return composition

        if not isinstance(title, str):
            title = "Rhythm Fast Quantized"
    
        return self.iterate(iterations, _measure_iterator, chaos, triggers, by_channel, title)


    def tonality_conjunct(self,
            iterations: int = 1,
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.Cycle(ra.Period(7), ot.Conjunct())**ch.SinX(),
            by_channel: bool = False,
            title: str | None = None) -> Self:
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                measure_clip: oc.Clip = self._seed * [measure_i]
                measure_clip += of.Foreach(*choices)**ou.Degree()
                return measure_clip
            return composition

        if not isinstance(title, str):
            title = "Tonality Conjunct"
    
        return self.iterate(iterations, _measure_iterator, chaos, triggers, by_channel, title)


    def tonality_conjunct_but_slacked(self,
            iterations: int = 1,
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.Cycle(ra.Period(7), ot.Conjunct(ra.Strictness(.75)))**ch.SinX(),
            by_channel: bool = False,
            title: str | None = None) -> Self:
        
        if not isinstance(title, str):
            title = "Tonality Conjunct But Slacked"
    
        return self.tonality_conjunct(iterations, triggers, chaos, by_channel, title)


    def sweep_sharps(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(0, ra.Period(8)),
            by_channel: bool = False,
            title: str | None = None) -> Self:
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                measure_clip: oc.Clip = self._seed * [measure_i]
                new_key_signature = ou.KeySignature(choices[0])  # One iteration
                measure_clip << new_key_signature << ou.TonicKey(-1)
                return measure_clip
            return composition

        if not isinstance(title, str):
            title = "Sweep Sharps"
    
        return self.iterate(iterations, _measure_iterator, chaos, [1], by_channel, title)


    def sweep_flats(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(0, ra.Period(8)),
            by_channel: bool = False,
            title: str | None = None) -> Self:
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                measure_clip: oc.Clip = self._seed * [measure_i]
                new_key_signature = ou.KeySignature(choices[0] * -1)  # One iteration
                measure_clip << new_key_signature << ou.TonicKey(-1)
                return measure_clip
            return composition

        if not isinstance(title, str):
            title = "Sweep Flats"
    
        return self.iterate(iterations, _measure_iterator, chaos, [1], by_channel, title)


    def sprinkle_accidentals(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Flipper(ra.Period(6))**ch.SinX(33),
            by_channel: bool = False,
            title: str | None = None) -> Self:
        
        last_accidental: int = 0
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            nonlocal last_accidental
            if isinstance(composition, oc.Clip):
                measure_clip: oc.Clip = self._seed * [measure_i]
                chaos_flip: int = choices[0]
                if chaos_flip > 0:
                    if last_accidental == 0:
                        last_accidental = 1
                        accidental_degree: ou.Degree = ou.Degree(0.1)   # Sharp
                    elif last_accidental > 0:
                        last_accidental = -1
                        accidental_degree: ou.Degree = ou.Degree(0.2)   # Flat
                    else:
                        last_accidental = 0
                        accidental_degree: ou.Degree = ou.Degree(0.0)   # Natural
                    measure_clip << accidental_degree
                return measure_clip
            return composition

        if not isinstance(title, str):
            title = "Sprinkle Accidentals"
    
        return self.iterate(iterations, _measure_iterator, chaos, 1, by_channel, title)



class RS_Part(RS_Solutions):
    pass



class RS_Song(RS_Solutions):
    pass
    

