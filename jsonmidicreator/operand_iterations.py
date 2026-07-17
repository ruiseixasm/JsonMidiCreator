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
from . import creator as c
from . import operand as o

from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_data as od
from . import operand_label as ol
from . import operand_generic as og
from . import operand_element as oe
from . import operand_frame as of
from . import operand_container as oc
from . import operand_chaos as ch
from . import operand_tamer as ot



class Iterations(o.Operand):
    def __init__(self, seed: 'oc.Clip' = oc.Clip(), chaos: ch.Chaos = ch.SinX(340),
                 pre_filter: Optional[Callable[['oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 4, no_repetitions: bool = False, freeze_at: int = -1):
        self._seed: oc.Clip = seed.copy()  # Read Only
        self._iterations: list[oc.Clip] = []
        self._chaos: ch.Chaos = chaos
        self._pre_filter: Callable | None = pre_filter
        self._post_processing: Callable | None = post_process
        self._max_tries: int = max_tries
        self._no_repetitions: bool = no_repetitions
        self._freeze_at: int = freeze_at
        super().__init__()
        

    def __rrshift__(self, operand: o.T) -> Self:
        return self.set_seed(operand)


    def reset(self) -> Self:
        self._iterations = []
        super().reset()
        return self
    
    def set_seed(self, seed: 'oc.Clip') -> Self:
        if isinstance(seed, oc.Clip):
            self._seed = seed.copy()
        return self
    
    def n_function(self, iteration: int) -> 'oc.Clip':
        extra_iterations = iteration - self._index
        if extra_iterations > 0:
            for _ in range(extra_iterations):
                self.iterate()
        return self._iterations[iteration].copy()   # Decoupled
    
    
    def iterate(self) -> Self:
        self._index += 1    # Each new_composition is added to the list, so, the index has to increase
        for _ in range(self._max_tries):    # Gets a non-empty iteration
            candidate: oc.Clip = self._single_iteration()
            if isinstance(self._next_operand, Iterations):
                self._next_operand._seed = candidate
                candidate = self._next_operand._single_iteration()
            if candidate.len() > 0: # Only non empty candidates can be considered as solutions
                if not callable(self._pre_filter) or self._pre_filter(candidate):
                    iteration: oc.Clip = self._post_process(candidate)
                    if not self._no_repetitions or not iteration in self._iterations:
                        iteration._index = self._index
                        self._iterations.append(iteration)
                        return self
        empty_iteration: oc.Clip = self._post_process(self._seed.empty_copy())
        empty_iteration._index = self._index
        self._iterations.append(empty_iteration)
        return self
    
    def get_clip(self) -> 'oc.Clip':
        """Also applies the post processing on the original iteration"""
        if self._freeze_at < 0:
            self.iterate()
        elif self._freeze_at > self._index: # self._index is the last item
            iterations: int = self._freeze_at - self._index
            for _ in range(iterations):
                self.iterate()
        return self._iterations[-1].copy()
    

    def _single_iteration(self) -> 'oc.Clip':
        return self._seed.copy()

    def _pre_exclude(self, clip: oc.Clip) -> bool:
        # The external user defined method is called if and only if the clip is internally validated
        return (not self._no_repetitions or not clip in self._iterations) \
            and (not callable(self._pre_filter) or self._pre_filter(clip))

    def _post_process(self, clip: oc.Clip) -> oc.Clip:
        if callable(self._post_processing):
            return self._post_processing(clip)
        return clip
    
    
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
            case oc.Clip():             return self.get_clip(operand)
            case int():                 return self._freeze_at
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["iterations"]       = self.serialize( self._iterations )
        serialization["parameters"]["chaos"]            = self.serialize( self._chaos )
        serialization["parameters"]["pre_filter"]       = self.serialize( self._pre_filter )
        serialization["parameters"]["post_process"]     = self.serialize( self._post_processing )
        serialization["parameters"]["max_tries"]        = self.serialize( self._max_tries )
        serialization["parameters"]["no_repetitions"]   = self.serialize( self._no_repetitions )
        serialization["parameters"]["freeze_at"]        = self.serialize( self._freeze_at )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "iterations" in serialization["parameters"] and "chaos" in serialization["parameters"] and "pre_filter" in serialization["parameters"] and
            "post_process" in serialization["parameters"] and "max_tries" in serialization["parameters"] and "no_repetitions" in serialization["parameters"] and
            "freeze_at" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._iterations        = self.deserialize( serialization["parameters"]["iterations"] )
            self._chaos             = self.deserialize( serialization["parameters"]["chaos"] )
            self._pre_filter        = self.deserialize( serialization["parameters"]["pre_filter"] )
            self._post_processing   = self.deserialize( serialization["parameters"]["post_process"] )
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
                self._pre_filter        = operand._pre_filter
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
    
    def __getitem__(self, index: int) -> oc.Clip | None:
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
    def __init__(self, seed: 'oc.Clip' = oc.Clip(), function: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 chaos: ch.Chaos = ch.SinX(340),
                 pre_filter: Optional[Callable[['oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(seed, chaos, pre_filter, post_process, max_tries, no_repetitions, freeze_at)
        self._function: list[Any] = function


    def _single_iteration(self) -> 'oc.Clip':
        if callable(self._function):
            new_iteration: oc.Clip = self._function(self._seed.copy())
            return new_iteration._sort_items()  # Safe code
        return self._seed.empty_copy()  # No valid Composition made


class I_DurationsSplitter(Iterations):
    def __init__(self, seed: 'oc.Clip' = oc.Clip(), durations: int = 8,
                 chaos: ch.Chaos = ch.SinX(340),
                 pre_filter: Optional[Callable[['oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(seed, chaos, pre_filter, post_process, max_tries, no_repetitions, freeze_at)
        self._durations: int = durations


    def _single_iteration(self) -> 'oc.Clip':
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        total_duration_beats = Fraction(0)
        seed_copy: oc.Clip = self._seed.copy()
        for single_element in seed_copy.unmasked_items():
            total_duration_beats += single_element._duration_beats
        if total_duration_beats > 0:
            try_i: int = 0
            while try_i < 100:
                iteration_clip: oc.Clip = seed_copy.copy()  # Despite the being already a copy, each iteration needs a new one
                try_j: int = 0
                while iteration_clip.len() < self._durations and try_j < 100 * 2:
                    continuous_split_step: int = self._chaos % int()
                    continuous_split_beat: Fraction = quantization_beats * continuous_split_step % total_duration_beats
                    continuous_start_beat = Fraction(0)
                    for single_element in iteration_clip.unmasked_items():
                        continuous_finish_beat = continuous_start_beat + single_element._duration_beats
                        if continuous_split_beat < continuous_finish_beat:
                            if continuous_split_beat > continuous_start_beat:
                                element_split_position: ra.Position = single_element % ra.Position()
                                element_split_position += continuous_split_beat - continuous_start_beat
                                single_element //= element_split_position
                            break
                        continuous_start_beat = continuous_finish_beat
                    if iteration_clip.len() == self._durations:
                        return iteration_clip._sort_items() # Safe code
                    try_j += 1
                try_i += 1
        return self._seed.empty_copy()   # Tags as invalid


class I_ParametersChooser(Iterations):
    def __init__(self, seed: 'oc.Clip' = oc.Clip(), parameters: list[Any] = ["1", "3", "5"],
                 chaos: ch.Chaos = ch.SinX(340),
                 pre_filter: Optional[Callable[['oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(seed, chaos, pre_filter, post_process, max_tries, no_repetitions, freeze_at)
        self._parameters: list[Any] = parameters


    def _single_iteration(self) -> 'oc.Clip':
        if self._parameters:
            seed_copy: oc.Clip = self._seed.copy()
            total_parameters: int = len(self._parameters)
            for element in seed_copy.unmasked_items():
                index_choice: int = self._chaos % int()
                chosen_parameter = self._parameters[index_choice % total_parameters]
                element << o.Operand.deep_copy(chosen_parameter)    # copy guarantees parameter decoupling
        return seed_copy._sort_items()


class I_ParameterShuffler(Iterations):
    def __init__(self, seed: 'oc.Clip' = oc.Clip(), parameter: Any = ou.Degree(),
                 chaos: ch.Chaos = ch.SinX(340, ot.Increase(1)**ot.Modulo(7)),
                 pre_filter: Optional[Callable[['oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(seed, chaos, pre_filter, post_process, max_tries, no_repetitions, freeze_at)
        self._parameter: Any = parameter

    def _single_iteration(self) -> 'oc.Clip':
        seed_copy: oc.Clip = self._seed.copy()
        clip_elements: list[oe.Element] = seed_copy.unmasked_items()
        clip_len: int = len(clip_elements)
        parameters: list[Any] = [
            element % self._parameter for element in clip_elements
        ]
        picks: list[Any] = []
        for total_indexes in range(clip_len, 0, -1):
            index: int = self._chaos % int() % total_indexes
            picks.append(parameters.pop(index))
        for element, parameter in zip(clip_elements, picks):
            element << parameter
        return seed_copy._sort_items()   # The Clip is already decoupled


class I_ParameterSetter(Iterations):
    def __init__(self, seed: 'oc.Clip' = oc.Clip(), parameter: o.Operand = ou.Degree(),
                 chaos: ch.Chaos = ch.SinX(340, ot.Increase(1)**ot.Modulo(7)),
                 global_setting: bool = False,
                 pre_filter: Optional[Callable[['oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(seed, chaos, pre_filter, post_process, max_tries, no_repetitions, freeze_at)
        self._parameter: o.Operand = parameter
        self._global_setting: bool = global_setting


    def _single_iteration(self) -> 'oc.Clip':
        seed_copy: oc.Clip = self._seed.copy()
        if self._global_setting:
            global_parameter = self._chaos.chaoticize()
            operand = self._parameter.copy(global_parameter)  # copy guarantees operand decoupling
            seed_copy << operand
        else:
            for element in seed_copy.unmasked_items():
                parameter = self._chaos.chaoticize()
                operand = self._parameter.copy(parameter)     # copy guarantees operand decoupling
                element << operand
        return seed_copy._sort_items()   # The Clip is already decoupled


class I_DurationSwapper(Iterations):
    def _single_iteration(self) -> 'oc.Clip':
        seed_copy: oc.Clip = self._seed.copy()
        clip_elements: list[oe.Element] = seed_copy.unmasked_items()
        clip_len: int = len(clip_elements)
        if clip_len > 1:
            indexes: list[int] = [
                i for i in range(clip_len - 1)  # Has to be paired, last index not considered
            ]
            picks: list[int] = []
            for total_indexes in range(clip_len - 1, 0, -1):
                index: int = self._chaos % int() % total_indexes
                picks.append(indexes.pop(index))
            for left_element_i in picks:
                swap: int = self._chaos % int() % 2
                if swap:
                    left_duration = clip_elements[left_element_i] % ra.Duration()
                    right_duration = clip_elements[left_element_i + 1] % ra.Duration()
                    # Direct setting on `seed_copy` elements
                    clip_elements[left_element_i] << right_duration
                    clip_elements[left_element_i + 1] << od.Left(left_duration)
        return seed_copy._sort_items()   # The Clip is already decoupled, elements manipulated directly thus sorting is needed

