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
                 by_channel: bool = False,
                 c_button: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 title: str | None = None):
        self._seed: oc.Composition = seed
        self._measures: list[int] = measures
        self._by_channel: bool = by_channel
        self._c_button = c_button
        self._title: str | None = title
        # Solution n_button parameters
        self._measure_iterator: Callable[[list | int | float | Fraction], 'oc.Composition'] | None = None
        self._chaos: ch.Chaos | None = None
        self._triggers: list | int | float | Fraction | None = None # Immutable for each Solution
        self._choices: list | None = None


    def solution(self) -> 'oc.Composition':
        return self._seed
    
    def mask(self, *conditions) -> Self:
        self._seed = self._seed.mask(*conditions)
        return self

    def unmask(self) -> Self:
        self._seed = self._seed.base()
        return self


    def iterate(self, iterations, n_button, title: str = "") -> Self:

        # Resets parameters for the next Solution
        self._choices = None

        def _n_button(composition: 'oc.Composition') -> 'oc.Composition':
            new_composition: oc.Composition = composition.empty_copy()
            for measure_i, iterations in enumerate(self._measures):
                if iterations >= 0 or self._choices is None:
                    if isinstance(self._triggers, list):
                        measure_triggers: list = self._triggers
                    else:
                        measure_triggers: list = [self._triggers] * (composition * [measure_i] % int())
                    if iterations > 0 or self._choices is None:
                        self._choices = self._chaos.reset_tamers() * iterations % measure_triggers
                    new_composition *= self._measure_iterator(self._choices, measure_i, composition) * [0]
                else:
                    new_composition *= composition * [measure_i]
            return new_composition

        if iterations < 0:
            if isinstance(self._title, str):
                title = self._title
            self._seed >>= og.Plot(self._by_channel,
                iterations=iterations * -1,
                n_button=n_button, c_button=self._c_button, title=title
            )
        else:
            self._seed >>= og.Call(iterations, n_button)
        return self



class RS_Clip(RS_Solutions):
    def __init__(self,
                 seed: oc.Composition,
                 measures: list[int] = [0, 0, 0, 0],
                 by_channel: bool = False,
                 c_button: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 title: str | None = None):
        super().__init__(seed, measures, by_channel, c_button, title)
        self._seed: oc.Clip = seed
         
    def solution(self) -> 'oc.Clip':
        return self._seed
    

    def my_n_button(self,
            iterations: int = 1,
            n_button: Callable[['oc.Composition'], 'oc.Composition'] | None = None,
            title: str | None = None) -> Self:
        
        if callable(n_button):
            if not isinstance(title, str):
                title = "My N Button"
            return self.iterate(iterations, n_button, title)
        return self


    def rhythm_fast_quantized(self,
            iterations: int = 1,
            durations: list[float] = [1/8 * 3/2, 1/8, 1/16 * 3/2, 1/16, 1/32 * 3/2, 1/32],
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.SinX(340),
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
        
        self._measure_iterator = _measure_iterator
        self._chaos = chaos
        self._triggers = triggers # Immutable for each Solution

        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                new_durations: list[float] = o.list_choose(durations, chaos.reset_tamers() % triggers)
                new_clip: oc.Clip = self._seed.empty_copy()
                for measure_iteration in self._measures:
                    measure_clip: oc.Clip = self._seed.copy()
                    if measure_iteration >= 0:
                        if measure_iteration > 0:
                            new_durations = o.list_choose(durations, chaos.reset_tamers() * measure_iteration % triggers)
                        measure_clip << of.Foreach(*new_durations)**ra.NoteValue()
                    # These operations shall be done on the base (single Measure)
                    measure_clip.base().stack().quantize().mul([0]).link()
                    new_clip *= measure_clip
                return new_clip
            return composition
    
        if not isinstance(title, str):
            title = "Rhythm Fast Quantized"
    
        return self.iterate(iterations, n_button, title)


    def tonality_conjunct(self,
            iterations: int = 1,
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.Cycle(ra.Period(7), ot.Conjunct())**ch.SinX(),
            title: str | None = None) -> Self:
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                measure_clip: oc.Clip = self._seed * [measure_i]
                measure_clip += of.Foreach(*choices)**ou.Degree()
                return measure_clip
            return composition
        
        self._measure_iterator = _measure_iterator
        self._chaos = chaos
        self._triggers = triggers # Immutable for each Solution

        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                new_degrees = chaos.reset_tamers() % triggers
                new_clip: oc.Clip = self._seed.empty_copy()
                for measure, measure_iteration in enumerate(self._measures):
                    measure_clip: oc.Clip = self._seed * [measure]
                    if measure_iteration >= 0:
                        if measure_iteration > 0:
                            new_degrees = chaos.reset_tamers() * measure_iteration % triggers
                        measure_clip += of.Foreach(*new_degrees)**ou.Degree()
                    new_clip *= measure_clip
                return new_clip
            return composition
        
        if not isinstance(title, str):
            title = "Tonality Conjunct"
    
        return self.iterate(iterations, n_button, title)


    def tonality_conjunct_but_slacked(self,
            iterations: int = 1,
            triggers: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.Cycle(ra.Period(7), ot.Conjunct(ra.Strictness(.75)))**ch.SinX(),
            title: str | None = None) -> Self:
        
        if not isinstance(title, str):
            title = "Tonality Conjunct But Slacked"
    
        return self.tonality_conjunct(iterations, triggers, chaos, title)


    def sweep_sharps(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(0, ra.Period(8)),
            title: str | None = None) -> Self:
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                measure_clip: oc.Clip = self._seed * [measure_i]
                new_key_signature = ou.KeySignature(choices[0])  # One iteration
                measure_clip << new_key_signature << ou.TonicKey(-1)
                return measure_clip
            return composition
        
        self._measure_iterator = _measure_iterator
        self._chaos = chaos
        self._triggers = 1 # Immutable for each Solution

        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                new_key_signature = ou.KeySignature(chaos.reset_tamers() % 1)  # One iteration
                new_clip: oc.Clip = self._seed.empty_copy()
                for measure, measure_iteration in enumerate(self._measures):
                    measure_clip: oc.Clip = self._seed * [measure]
                    if measure_iteration >= 0:
                        if measure_iteration > 0:
                            new_key_signature = ou.KeySignature(chaos.reset_tamers() % measure_iteration)  # One iteration
                        measure_clip << new_key_signature << ou.TonicKey(-1)
                    new_clip *= measure_clip
                return new_clip
            return composition
    
        if not isinstance(title, str):
            title = "Sweep Sharps"
    
        return self.iterate(iterations, n_button, title)


    def sweep_flats(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(0, ra.Period(8)),
            title: str | None = None) -> Self:
        
        def _measure_iterator(choices: list, measure_i: int, composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                measure_clip: oc.Clip = self._seed * [measure_i]
                new_key_signature = ou.KeySignature(choices[0] * -1)  # One iteration
                measure_clip << new_key_signature << ou.TonicKey(-1)
                return measure_clip
            return composition
        
        self._measure_iterator = _measure_iterator
        self._chaos = chaos
        self._triggers = 1 # Immutable for each Solution

        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                new_key_signature = ou.KeySignature(chaos.reset_tamers() % 1 * -1)  # One iteration
                new_clip: oc.Clip = self._seed.empty_copy()
                for measure, measure_iteration in enumerate(self._measures):
                    measure_clip: oc.Clip = self._seed * [measure]
                    if measure_iteration >= 0:
                        if measure_iteration > 0:
                            new_key_signature = ou.KeySignature(chaos.reset_tamers() % measure_iteration * -1)  # One iteration
                        measure_clip << new_key_signature << ou.TonicKey(-1)
                    new_clip *= measure_clip
                return new_clip
            return composition
    
        if not isinstance(title, str):
            title = "Sweep Flats"
    
        return self.iterate(iterations, n_button, title)


    def sprinkle_accidentals(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Flipper(ra.Period(6))**ch.SinX(33),
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
        
        self._measure_iterator = _measure_iterator
        self._chaos = chaos
        self._triggers = 1 # Immutable for each Solution

        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            nonlocal last_accidental
            if isinstance(composition, oc.Clip):
                chaos_flip: int = chaos.reset_tamers() % 1
                new_clip: oc.Clip = self._seed * [0] # Just the first Measure
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
                    new_clip << accidental_degree
                return new_clip * 4
            return composition
    
        if not isinstance(title, str):
            title = "Sprinkle Accidentals"
    
        return self.iterate(iterations, n_button, title)



class RS_Part(RS_Solutions):
    pass



class RS_Song(RS_Solutions):
    pass
    

