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
    def __init__(self, chaos: ch.Chaos = ch.SinX(340),
                 pre_filter: Optional[Callable[['oc.Clip', 'oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 4, no_repetitions: bool = False, freeze_at: int = -1):
        self._seed: oc.Clip = oc.Clip() # Read-Only
        self._iterations: list[oc.Clip] = []
        self._chaos: ch.Chaos = chaos
        self._pre_filter: Callable[['oc.Clip', 'oc.Clip'], bool] | None = pre_filter
        self._post_process: Callable[['oc.Clip'], 'oc.Clip'] | None = post_process
        self._max_tries: int = max_tries
        self._no_repetitions: bool = no_repetitions
        self._freeze_at: int = freeze_at
        super().__init__()
        

    def set_seed(self, seed: 'oc.Clip') -> Self:
        if isinstance(seed, oc.Clip):
            self._seed = seed.copy()
        return self
    
    def __rrshift__(self, clip: 'oc.Clip') -> Self:
        return self.set_seed(clip)

    def reset(self) -> Self:
        self._iterations = []
        super().reset()
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
            if isinstance(self._chained_operand, Iterations):
                self._chained_operand._seed = candidate
                candidate = self._chained_operand._single_iteration()
            if candidate.len() > 0: # Only non empty candidates can be considered as solutions
                if not callable(self._pre_filter) or self._pre_filter(candidate, self._seed):
                    if callable(self._post_process):
                        candidate = self._post_process(candidate)
                    if not self._no_repetitions or not candidate in self._iterations:
                        candidate._index = self._index
                        self._iterations.append(candidate)
                        return self
        empty_iteration: oc.Clip = self._seed.empty_copy()
        if callable(self._post_process):
            empty_iteration = self._post_process(empty_iteration)
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

    
    def len(self) -> int:
        return len(self._iterations)

    def __pow__(self, operand: 'o.Operand') -> Self:
        '''
        This operator ** tags another Operand to self that will be the target of the << operation and \
            be passed to self afterwards in a chained fashion.
        '''
        if isinstance(operand, Iterations):
            self._chained_operand = operand
        elif operand is None:
            self._chained_operand = None
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
                    case oc.Clip():             return self._seed
                    case ch.Chaos():            return self._chaos
                    case _:                     return super().__mod__(operand)
            case ch.Chaos():            return self._chaos.copy()
            case oc.Clip():             return self.get_clip()
            case int():                 return self._freeze_at
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["seed"]             = o.serialize( self._seed )
        serialization["parameters"]["iterations"]       = o.serialize( self._iterations )
        serialization["parameters"]["chaos"]            = o.serialize( self._chaos )
        serialization["parameters"]["pre_filter"]       = o.serialize( self._pre_filter )
        serialization["parameters"]["post_process"]     = o.serialize( self._post_process )
        serialization["parameters"]["max_tries"]        = o.serialize( self._max_tries )
        serialization["parameters"]["no_repetitions"]   = o.serialize( self._no_repetitions )
        serialization["parameters"]["freeze_at"]        = o.serialize( self._freeze_at )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "seed" in serialization["parameters"] and "iterations" in serialization["parameters"] and "chaos" in serialization["parameters"] and "pre_filter" in serialization["parameters"] and
            "post_process" in serialization["parameters"] and "max_tries" in serialization["parameters"] and "no_repetitions" in serialization["parameters"] and
            "freeze_at" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._seed              = o.deserialize( serialization["parameters"]["seed"] )
            self._iterations        = o.deserialize( serialization["parameters"]["iterations"] )
            self._chaos             = o.deserialize( serialization["parameters"]["chaos"] )
            self._pre_filter        = o.deserialize( serialization["parameters"]["pre_filter"] )
            self._post_process   = o.deserialize( serialization["parameters"]["post_process"] )
            self._max_tries         = o.deserialize( serialization["parameters"]["max_tries"] )
            self._no_repetitions    = o.deserialize( serialization["parameters"]["no_repetitions"] )
            self._freeze_at         = o.deserialize( serialization["parameters"]["freeze_at"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Iterations():
                super().__lshift__(operand)
                self._seed              = operand._seed.copy()
                self._iterations        = operand._iterations.copy()
                self._chaos             = operand._chaos.copy()
                self._pre_filter        = operand._pre_filter
                self._post_process   = operand._post_process
                self._max_tries         = operand._max_tries
                self._no_repetitions    = operand._no_repetitions
                self._freeze_at         = operand._freeze_at
            case od.Pipe():
                match operand._data:
                    case oc.Clip():             self._seed = operand._data
                    case ch.Chaos():            self._chaos = operand._data
                    case int():                 self._freeze_at = operand._data
                    case _:                     super().__lshift__(operand)
            case oc.Clip():
                self._seed = operand.copy()
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
            for _ in range(number):
                self.iterate()
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
    


class I_ChooseParameter(Iterations):
    def __init__(self, parameters: list[Any] = ["1", "3", "5"],
                 chaos: ch.Chaos = ch.SinX(340),
                 pre_filter: Optional[Callable[['oc.Clip', 'oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(chaos, pre_filter, post_process, max_tries, no_repetitions, freeze_at)
        self._parameters: list[Any] = parameters


    def _single_iteration(self) -> 'oc.Clip':
        if self._parameters:
            seed_copy: oc.Clip = self._seed.copy()
            total_parameters: int = len(self._parameters)
            for element in seed_copy.elements_unmasked():
                index_choice: int = self._chaos % int()
                chosen_parameter = self._parameters[index_choice % total_parameters]
                element << o.deep_copy(chosen_parameter)    # copy guarantees parameter decoupling
        return seed_copy._sort_items()



class I_SetParameter(Iterations):
    def __init__(self, parameter: o.Operand = ou.Degree(),
                 global_setting: bool = False,
                 chaos: ch.Chaos = ch.SinX(340, ot.Increase(1)**ot.Modulo(7)),
                 pre_filter: Optional[Callable[['oc.Clip', 'oc.Clip'], bool]] = None,
                 post_process: Optional[Callable[['oc.Clip'], 'oc.Clip']] = None,
                 max_tries: int = 100, no_repetitions: bool = False, freeze_at: int = -1):
        super().__init__(chaos, pre_filter, post_process, max_tries, no_repetitions, freeze_at)
        self._parameter: o.Operand = parameter
        self._global_setting: bool = global_setting


    def _single_iteration(self) -> 'oc.Clip':
        seed_copy: oc.Clip = self._seed.copy()
        if self._global_setting:
            global_parameter = self._chaos.chaoticize()
            operand = self._parameter.copy(global_parameter)  # copy guarantees operand decoupling
            seed_copy << operand
        else:
            for element in seed_copy.elements_unmasked():
                parameter = self._chaos.chaoticize()
                operand = self._parameter.copy(parameter)     # copy guarantees operand decoupling
                element << operand
        return seed_copy._sort_items()   # The Clip is already decoupled


class I_AddElements(Iterations):
    
    def _single_iteration(self) -> 'oc.Clip':
        seed_copy: oc.Clip = self._seed.copy()
        steps_length: int = seed_copy % ra.Length() % ra.Step() % int()
        stepped_elements: list[oe.Element] = [None] * steps_length
        free_steps: list[bool] = [True] * steps_length
        for single_element in seed_copy._items:
            element_step: int = single_element % ra.Step() % int()
            stepped_elements[element_step] = single_element
            free_steps[element_step] = False
        previous_element: oe.Element | None = None
        for step in range(steps_length):
            if stepped_elements[step] is not None:
                previous_element = stepped_elements[step]
            elif previous_element is not None:
                stepped_elements[step] = previous_element
            else:
                stepped_elements[step] = seed_copy._items[-1]
                previous_element = seed_copy._items[-1]
        for step, step_free in enumerate(free_steps):
            if step_free:
                chaotic_rational: Fraction = self._trigger_steps % Fraction() % 1
                # `1 - chaotic_rational` in order to preserve result in chained Probabilities or alike, 1 remains 1 and 0 remains 0, no flipping
                result = 1 if 1 - chaotic_rational < self._parameter else 0
                if result == 1: # Add new element
                    new_element: oe.Element = stepped_elements[step].copy(ra.Step(step))
                    seed_copy += new_element
        return seed_copy._sort_items()   # The Clip is already decoupled


class I_RemoveElements(Iterations):
    
    def _single_iteration(self) -> 'oc.Clip':
        seed_copy: oc.Clip = self._seed.empty_copy()
        for single_element in self._seed._items:
            if not single_element._masked:
                chaotic_rational: Fraction = self._trigger_steps % Fraction() % 1
                # `1 - chaotic_rational` in order to preserve result in chained Probabilities or alike, 1 remains 1 and 0 remains 0, no flipping
                result = 1 if 1 - chaotic_rational < self._parameter else 0
                if result == 1:
                    continue    # Drops it, not added
            seed_copy += single_element
        return seed_copy    # If removed no change in sorting, thus, no need to sort


