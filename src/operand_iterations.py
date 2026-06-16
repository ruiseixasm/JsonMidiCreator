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
import operand_tamer as ot



class Iterations(o.Operand):
    def __init__(self, chaos: ch.Chaos = ch.SinX(340),
                 pre_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 max_tries: int = 4, no_repetitions: bool = False, freeze_at: int = -1):
        self._iterations: list[oc.Composition] = []
        self._chaos: ch.Chaos = chaos
        self._pre_exclusion: Callable | None = pre_exclusion
        self._post_processing: Callable | None = post_processing
        self._max_tries: int = max_tries
        self._no_repetitions: bool = no_repetitions
        self._freeze_at: int = freeze_at
        super().__init__()

    def reset(self) -> Self:
        self._iterations = []
        super().reset()
        return self
    
    def iterate(self, composition_0: 'oc.Composition', times: int = 1) -> Self:
        if times > 0:
            if not self._iterations:
                self._iterations.append(composition_0) # Avoids repeating the initial clip (seed)
            for _ in range(times):
                self._index += 1    # Each new_composition is added to the list, so, the index has to increase
                for _ in range(self._max_tries):    # Gets a non-empty iteration
                    if isinstance(self._next_operand, Iterations):
                        tail_iteration = self._next_operand.new_iteration(composition_0.copy())
                        candidate = self._single_iteration(tail_iteration)
                    else:
                        candidate = self._single_iteration(composition_0.copy())
                    if not callable(self._pre_exclusion) or not self._pre_exclusion(candidate):
                        iteration: oc.Composition = self._post_process(candidate)
                        if not self._no_repetitions or not iteration in self._iterations:
                            iteration._index = self._index
                            self._iterations.append(iteration)
                            return self
                empty_iteration: oc.Composition = self._post_process(composition_0.empty_copy())
                empty_iteration._index = self._index
                self._iterations.append(empty_iteration)
        return self
    
    def new_iteration(self, composition_0: 'oc.Composition') -> 'oc.Composition':
        """Also applies the post processing on the original iteration"""
        if self._freeze_at < 0:
            self.iterate(composition_0)
        elif self._freeze_at > self._index: # self._index is the last item
            iterations: int = self._freeze_at - self._index
            for _ in range(iterations):
                self.iterate(composition_0)
        return self._iterations[-1].copy()


    def _single_iteration(self, composition_0: 'oc.Composition') -> 'oc.Composition':
        return composition_0


    def _pre_exclude(self, composition: oc.Composition) -> bool:
        # The external user defined method is called if and only if the composition is internally validated
        return self._no_repetitions and composition in self._iterations \
            or callable(self._pre_exclusion) and self._pre_exclusion(composition)

    def _post_process(self, composition: oc.Composition) -> oc.Composition:
        if callable(self._post_processing):
            return self._post_processing(composition)
        return composition
    
    def len(self) -> int:
        return len(self._iterations)

    def __pow__(self, operand: 'o.Operand') -> Self:
        '''
        This operator ** tags another Operand to self that will be the target of the << operation and \
            be passed to self afterwards in a chained fashion.
        '''
        if isinstance(operand, Iterations):
            self._next_operand = operand
        elif operand is None:
            self._next_operand = None
        return self
    
    def __eq__(self, other: Any) -> bool:
        match other:
            case Iterations():
                return super().__eq__(other) and self._iterations == other._iterations
            case _:
                return super().__eq__(other)
    
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ch.Chaos():            return self._chaos
                    case _:                     return super().__mod__(operand)
            case ch.Chaos():            return self._chaos.copy()
            case int():                 return self._freeze_at
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["iterations"]       = self.serialize( self._iterations )
        serialization["parameters"]["chaos"]            = self.serialize( self._chaos )
        serialization["parameters"]["pre_exclusion"]    = self.serialize( self._pre_exclusion )
        serialization["parameters"]["post_processing"]  = self.serialize( self._post_processing )
        serialization["parameters"]["max_tries"]        = self.serialize( self._max_tries )
        serialization["parameters"]["no_repetitions"]   = self.serialize( self._no_repetitions )
        serialization["parameters"]["freeze_at"]        = self.serialize( self._freeze_at )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "iterations" in serialization["parameters"] and "chaos" in serialization["parameters"] and "pre_exclusion" in serialization["parameters"] and
            "post_processing" in serialization["parameters"] and "max_tries" in serialization["parameters"] and "no_repetitions" in serialization["parameters"] and
            "freeze_at" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._iterations        = self.deserialize( serialization["parameters"]["iterations"] )
            self._chaos             = self.deserialize( serialization["parameters"]["chaos"] )
            self._pre_exclusion     = self.deserialize( serialization["parameters"]["pre_exclusion"] )
            self._post_processing   = self.deserialize( serialization["parameters"]["post_processing"] )
            self._max_tries         = self.deserialize( serialization["parameters"]["max_tries"] )
            self._no_repetitions    = self.deserialize( serialization["parameters"]["no_repetitions"] )
            self._freeze_at         = self.deserialize( serialization["parameters"]["freeze_at"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Iterations():
                super().__lshift__(operand)
                self._iterations        = operand._iterations.copy()
                self._chaos             = operand._chaos.copy()
                self._pre_exclusion     = operand._pre_exclusion
                self._post_processing   = operand._post_processing
                self._max_tries         = operand._max_tries
                self._no_repetitions    = operand._no_repetitions
                self._freeze_at         = operand._freeze_at
            case od.Pipe():
                match operand._data:
                    case ch.Chaos():            self._chaos = operand._data
                    case int():                 self._freeze_at = operand._data
                    case _:                     super().__lshift__(operand)
            case ch.Chaos():
                self._chaos             = operand.copy()
            case int():
                self._freeze_at         = operand
            case _:
                super().__lshift__(operand)
        return self

    def __imul__(self, number: Union['ou.Unit', 'ra.Rational', int, float, Fraction]) -> Self:
        if self._iterations:
            number = o.number_to_int(number) # Results in a int, like int(float)
            seed_composition = self._iterations[0]
            for _ in range(number):
                self.iterate(seed_composition)
        return self
    
    def __getitem__(self, index: int) -> oc.Composition | None:
        """To set the initial seed, use new_iteration with it"""
        if isinstance(index, int) and self._iterations:
            if index > self._index: # self._index is the last item
                iterations: int = index - self._index
                seed_composition = self._iterations[0]
                for _ in range(iterations):
                    self.iterate(seed_composition)
            return self._iterations[index]
        return None
    

class I_Function(Iterations):
    def __init__(self, function: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 chaos: ch.Chaos = ch.SinX(340),
                 pre_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(chaos, pre_exclusion, post_processing, max_tries, no_repetitions, freeze_at)
        self._function: list[Any] = function


    def _single_iteration(self, composition_0: 'oc.Composition') -> 'oc.Composition':
        if callable(self._function):
            new_iteration: oc.Composition = self._function(composition_0)
            return new_iteration
        return composition_0.empty_copy()  # No valid Composition made


class I_Clips(Iterations):
    pass

class I_Splitter(I_Clips):
    def __init__(self, elements: int = 8,
                 chaos: ch.Chaos = ch.SinX(340),
                 pre_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(chaos, pre_exclusion, post_processing, max_tries, no_repetitions, freeze_at)
        self._elements: int = elements


    def _single_iteration(self, decoupled_clip_0: 'oc.Clip') -> 'oc.Clip':
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        total_duration_beats = Fraction(0)
        for single_element in decoupled_clip_0._unmasked_items():
            total_duration_beats += single_element._duration_beats
        if total_duration_beats > 0:
            try_i: int = 0
            while try_i < 100:
                iteration_clip: oc.Clip = decoupled_clip_0.copy() # Despite the clip_0 being already a copy, each iteration needs a new one
                try_j: int = 0
                while iteration_clip.len() < self._elements and try_j < 100 * 2:
                    continuous_split_step: int = self._chaos % int()
                    continuous_split_beat: Fraction = quantization_beats * continuous_split_step % total_duration_beats
                    continuous_start_beat = Fraction(0)
                    for single_element in iteration_clip._unmasked_items():
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
        return decoupled_clip_0.empty_copy()   # Tags as invalid


class I_Chooser(I_Clips):
    def __init__(self, parameters: list[Any] = ["1", "3", "5"],
                 chaos: ch.Chaos = ch.SinX(340),
                 pre_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(chaos, pre_exclusion, post_processing, max_tries, no_repetitions, freeze_at)
        self._parameters: list[Any] = parameters


    def _single_iteration(self, decoupled_clip_0: 'oc.Clip') -> 'oc.Clip':
        if self._parameters:
            total_parameters: int = len(self._parameters)
            for element in decoupled_clip_0._unmasked_items():
                index_choice: int = self._chaos % int()
                chosen_parameter = self._parameters[index_choice % total_parameters]
                element << chosen_parameter
        return decoupled_clip_0  # The Clip is already decoupled


class I_Setter(I_Clips):
    def __init__(self, operand: o.Operand = ou.Degree(),
                 chaos: ch.Chaos = ch.SinX(340, ot.Increase(1)**ot.Modulo(7)),
                 pre_exclusion: Optional[Callable[['oc.Composition'], bool]] = None,
                 post_processing: Optional[Callable[['oc.Composition'], 'oc.Composition']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(chaos, pre_exclusion, post_processing, max_tries, no_repetitions, freeze_at)
        self._operand: o.Operand = operand


    def _single_iteration(self, decoupled_clip_0: 'oc.Clip') -> 'oc.Clip':
        for element in decoupled_clip_0._unmasked_items():
            setter: Fraction = self._chaos % Fraction()
            parameter = self._operand << setter
            element << parameter
        return decoupled_clip_0  # The Clip is already decoupled


