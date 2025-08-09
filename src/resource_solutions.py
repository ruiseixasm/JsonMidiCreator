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
    def __init__(self, seed: oc.Composition, plot : og.Plot = og.Plot()):
        self._seed: oc.Composition = seed
        self._plot: og.Plot = plot

    def solution(self) -> 'oc.Composition':
        return self._seed
    
    def mask(self, *conditions) -> Self:
        self._seed = self._seed.mask(*conditions)
        return self

    def unmask(self) -> Self:
        self._seed = self._seed.base()
        return self

    def iterate(self, iterations, n_button, title: str = "") -> Self:
        if iterations < 0:
            self._seed >>= self._plot.set_iterations(iterations * -1).set_n_button(n_button).set_title(title)
        else:
            self._seed >>= og.Call(iterations, n_button)
        return self



class RS_Clip(RS_Solutions):
    def __init__(self, seed: oc.Clip, plot : og.Plot = og.Plot(title="Clip Solutions")):
        super().__init__(seed, plot)
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
            choices: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.SinX(340),
            title: str | None = None) -> Self:
        
        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                chaos.reset_tamers()    # Tamer needs to be reset
                picked_durations = o.list_choose(durations, chaos % choices)
                composition << of.Foreach(*picked_durations)**ra.NoteValue()
                # These operations shall be done on the base (single Measure)
                composition.base().stack().quantize().mul([0]).link()  
                return composition.mul(4)
            return composition
    
        if not isinstance(title, str):
            title = "Rhythm Fast Quantized"
    
        return self.iterate(iterations, n_button, title)


    def tonality_conjunct(self,
            iterations: int = 1,
            choices: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.Cycle(ra.Period(7), ot.Conjunct())**ch.SinX(),
            title: str | None = None) -> Self:
        
        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                chaos.reset_tamers()    # Tamer needs to be reset
                final_degrees = chaos % choices
                new_clip: oc.Clip = self._seed * [0] # Just the first Measure
                new_clip += of.Foreach(*final_degrees)**ou.Degree()
                return new_clip * 4
            return composition
        
        if not isinstance(title, str):
            title = "Tonality Conjunct"
    
        return self.iterate(iterations, n_button, title)


    def tonality_conjunct_but_slacked(self,
            iterations: int = 1,
            choices: list[int] = [2, 4, 4, 2, 1, 1, 3],
            chaos: ch.Chaos = ch.Cycle(ra.Period(7), ot.Conjunct(ra.Strictness(.75)))**ch.SinX(),
            title: str | None = None) -> Self:
        
        if not isinstance(title, str):
            title = "Tonality Conjunct But Slacked"
    
        return self.tonality_conjunct(iterations, choices, chaos, title)


    def sweep_sharps(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(0, ra.Period(8)),
            title: str | None = None) -> Self:
        
        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                chaos.reset_tamers()    # Tamer needs to be reset
                chaos_data = chaos % 1  # One iteration
                key_signature: ou.KeySignature = ou.KeySignature(chaos_data)
                new_clip: oc.Clip = self._seed * [0] # Just the first Measure
                new_clip << key_signature << ou.TonicKey(-1)
                return new_clip * 4
            return composition
    
        if not isinstance(title, str):
            title = "Sweep Sharps"
    
        return self.iterate(iterations, n_button, title)


    def sweep_flats(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Cycle(0, ra.Period(8)),
            title: str | None = None) -> Self:
        
        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            if isinstance(composition, oc.Clip):
                chaos.reset_tamers()    # Tamer needs to be reset
                chaos_data = chaos % 1  # One iteration
                key_signature: ou.KeySignature = ou.KeySignature(chaos_data * -1)
                new_clip: oc.Clip = self._seed * [0] # Just the first Measure
                new_clip << key_signature << ou.TonicKey(-1)
                return new_clip * 4
            return composition
    
        if not isinstance(title, str):
            title = "Sweep Flats"
    
        return self.iterate(iterations, n_button, title)


    def sprinkle_accidentals(self,
            iterations: int = 1,
            chaos: ch.Chaos = ch.Flipper(ra.Period(6))**ch.SinX(33),
            title: str | None = None) -> Self:
        
        last_accidental: int = 0
        
        def n_button(composition: 'oc.Composition') -> 'oc.Composition':
            nonlocal last_accidental
            if isinstance(composition, oc.Clip):
                chaos.reset_tamers()    # Tamer needs to be reset
                chaos_flip: int = chaos % 1
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
    def __init__(self, seed: oc.Part, plot : og.Plot = og.Plot(title="Part Solutions")):
        super().__init__(seed, plot)
        self._seed: oc.Part = seed
         
    def solution(self) -> 'oc.Part':
        return self._seed



class RS_Song(RS_Solutions):
    def __init__(self, seed: oc.Song, plot : og.Plot = og.Plot(title="Song Solutions")):
        super().__init__(seed, plot)
        self._seed: oc.Song = seed
         
    def solution(self) -> 'oc.Song':
        return self._seed
    

