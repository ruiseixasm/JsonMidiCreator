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
import enum
import math
from types import FunctionType
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


class Mutation(o.Operand):
    """`Mutation`

    Mutation can be Haploid or Diploid, the second one adds a second Clip so that Shuffle
    of Clips becomes a Diploid process.

    Parameters
    ----------
    first : any_like
        Any type of parameter can be used to set Mutation. Self clip as None is de default.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._chaos: ch.Chaos           = ch.SinX()
        self._step: int | float         = 1
        self._parameter: type           = ra.Position
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter


    def shuffle_list(self, list: list) -> list:
        
        source_picks = [*range(len(list))]
        target_picks = []

        while len(source_picks) > 0:
            target_picks.append(source_picks.pop(self._chaos * self._step % int() % len(source_picks)))

        shuffled_list = []
        for pick in target_picks:
            shuffled_list.append(list[pick])

        return shuffled_list

    def mutate(self, clip: o.T) -> o.T:
        match clip:
            case oc.Clip():
                self.mutate(clip)
        return clip

    # Clip or Mutation is the input >> (NO COPIES!) (PASSTHROUGH)
    def __rrshift__(self, clip: o.T) -> o.T:
        return self.mutate(clip)


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case ch.Chaos():        return self._chaos
                    case int():             return int(self._step)
                    case float():           return float(self._step)
                    case type():            return self._parameter
                    case _:                 return super().__mod__(operand)
            case ch.Chaos():        return self._chaos.copy()
            case int():             return int(self._step)
            case float():           return float(self._step)
            case type():            return self._parameter
            case ra.Index():        return ra.Index(self._index)
            case ou.Next():         return self * operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, Mutation):
            return self._chaos == other._chaos and self._parameter == other._parameter
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["chaos"]            = self.serialize(self._chaos)
        serialization["parameters"]["step"]             = self.serialize(self._step)
        serialization["parameters"]["parameter"]        = self._parameter.__name__
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "chaos" in serialization["parameters"] and "step" in serialization["parameters"] and "parameter" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._chaos             = self.deserialize(serialization["parameters"]["chaos"])
            self._step              = self.deserialize(serialization["parameters"]["step"])
            parameter: type = o.find_class_by_name( o.Operand, serialization["parameters"]["parameter"] )
            if parameter:
                self._parameter     = parameter
            else:
                self._parameter     = ra.Position
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Mutation():
                super().__lshift__(operand)
                self._chaos         << operand._chaos
                self._step          = operand._step
                self._parameter     = operand._parameter
            case od.DataSource():
                match operand._data:
                    case ch.Chaos():                self._chaos = operand._data
                    case int() | float():           self._step = operand._data
                    case type():                    self._parameter = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ch.Chaos():        self._chaos << operand
            case int() | float():   self._step = operand
            case type():            self._parameter = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


class Haploid(Mutation):
    pass

class Choosing(Haploid):
    def __init__(self, *parameters):
        super().__init__()
        self._choice: of.Choice = of.Choice()
        self._parameter = o.Operand # Directly returns the Pick content
        self._choice_frame: of.Frame = of.Foreach(self._chaos)**self._choice**self._parameter()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def mutate(self, clip: o.T) -> o.T:
        if isinstance(clip, oc.Clip):
            clip << self._choice_frame
        return clip

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case of.Choice():         return self._choice
                    case _:                 return super().__mod__(operand)
            case of.Choice():         return self._choice
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["choice"] = self.serialize(self._choice)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "choice" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._choice = self.deserialize(serialization["parameters"]["choice"])
        self._choice_frame: of.Frame = of.Foreach(self._chaos)**self._choice**self._parameter()
        return self
        
    def __lshift__(self, operand: any) -> Self:
        if not isinstance(operand, of.Choice):
            operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Choosing():
                super().__lshift__(operand)
                self._choice = operand._choice.copy()
            case od.DataSource():
                match operand._data:
                    case of.Choice():         self._choice = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case of.Choice():     self._choice = operand.copy()
            case _:             super().__lshift__(operand)
        
        self._choice_frame: of.Frame = of.Foreach(self._chaos)**self._choice**self._parameter()
        return self

class Picking(Haploid):
    def __init__(self, *parameters):
        super().__init__()
        self._pick: of.Pick = of.Pick()
        self._parameter = o.Operand # Directly returns the Pick content
        self._pick_frame: of.Frame = of.Foreach(self._chaos)**self._pick**self._parameter()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def mutate(self, clip: o.T) -> o.T:
        if isinstance(clip, oc.Clip):
            clip << self._pick_frame
        return clip

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case of.Pick():         return self._pick
                    case _:                 return super().__mod__(operand)
            case of.Pick():         return self._pick
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pick"] = self.serialize(self._pick)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pick" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pick = self.deserialize(serialization["parameters"]["pick"])
        self._pick_frame: of.Frame = of.Foreach(self._chaos)**self._pick**self._parameter()
        return self
        
    def __lshift__(self, operand: any) -> Self:
        if not isinstance(operand, of.Pick):
            operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Picking():
                super().__lshift__(operand)
                self._pick = operand._pick.copy()
            case od.DataSource():
                match operand._data:
                    case of.Pick():         self._pick = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case of.Pick():     self._pick = operand.copy()
            case _:             super().__lshift__(operand)
        
        self._pick_frame: of.Frame = of.Foreach(self._chaos)**self._pick**self._parameter()
        return self


class Diploid(Mutation):
    pass

class Swapping(Diploid):
    def __init__(self, *parameters):
        super().__init__()
        self._clip: oc.Clip             = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def setup(self, clip: oc.Clip) -> bool:
        if clip is None:
            self._clip = None
        elif isinstance(clip, oc.Clip):
            if self._clip is None:
                self._clip = clip.copy()
            return True
        return False

    def swap(self, clip: oc.Clip, source_clip_index: int, target_clip_index: int) -> Self:
            
        parameter_instance = self._parameter()
        source_clip_len: int = self._clip.len()
        target_clip_len: int = clip.len()
        if isinstance(parameter_instance, od.DataSource):
            element_switch: oe.Element = clip[source_clip_index % target_clip_len]
            clip[target_clip_index % target_clip_len] = self._clip[source_clip_index % source_clip_len]
            self._clip[source_clip_index % source_clip_len] = element_switch
        else:
            parameter_switch: any = clip[source_clip_index % target_clip_len] % parameter_instance
            clip[target_clip_index % target_clip_len] << self._clip[source_clip_index % source_clip_len] % parameter_instance
            self._clip[source_clip_index % source_clip_len] << parameter_switch

        return self


    def mutate(self, clip: oc.Clip) -> oc.Clip:
        if self.setup(clip):
            
            source_picks: list[int] = [*range(self._clip.len())]
            target_picks: list[int] = [*range(clip.len())]

            while len(source_picks) > 0 and len(target_picks) > 0:

                source_index: int = self._chaos * self._step % int() % len(source_picks)
                source_clip_index: int = source_picks[source_index]
                del source_picks[source_index]

                target_index: int = self._chaos * self._step % int() % len(target_picks)
                target_clip_index: int = target_picks[target_index]
                del target_picks[target_index]

                self.swap(clip, source_clip_index, target_clip_index)

        return clip

    def len(self) -> int:
        if isinstance(self._clip, oc.Clip):
            return self._clip.len()
        return 0


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case oc.Clip():         return self._clip
                    case _:                 return super().__mod__(operand)
            case oc.Clip():         return self.deep_copy(self._clip)
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["clip"]             = self.serialize(self._clip)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "clip" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._clip              = self.deserialize(serialization["parameters"]["clip"])
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Swapping():
                super().__lshift__(operand)
                self._clip          = self.deep_copy( operand._clip )
            case od.DataSource():
                match operand._data:
                    case oc.Clip():                 self._clip = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case oc.Clip():         self._clip = operand.copy() # Avoids None case error
            case _:                 super().__lshift__(operand)
        return self
    
    def __imul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> Self:
        self._initiated = True
        self._chaos * number
        self._index += self.convert_to_int(number)    # keeps track of each iteration
        return self

    def __or__(self, operand: any) -> Self:
        return self.shallow_copy().__ior__(operand)

    def __ior__(self, operand: any) -> Self:
        return self.__itruediv__(operand)

    def __itruediv__(self, operand: any) -> Self:
        match operand:
            case Swapping():
                self.mutate(operand._clip.copy())
            case oc.Clip():
                self.mutate(operand.copy())
        return self

    def empty_copy(self, *parameters) -> Self:
        empty_copy: Swapping = self.__class__()
        # COPY THE SELF OPERANDS RECURSIVELY
        if self._next_operand:
            empty_copy._next_operand = self.deep_copy(self._next_operand)
        empty_copy._chaos           << self._chaos
        empty_copy._step            = self._step
        empty_copy._parameter       = self._parameter
        for single_parameter in parameters:
            empty_copy << single_parameter
        return empty_copy

    def shallow_copy(self, *parameters) -> Self:
        shallow_copy: Swapping      = self.empty_copy()
        if isinstance(self._clip, oc.Clip):
            shallow_copy._clip = self._clip.shallow_copy()
        for single_parameter in parameters:
            shallow_copy << single_parameter
        return shallow_copy
    
    def reset(self, *parameters) -> Self:
        super().reset(*parameters)
        self._clip = None
        self._chaos.reset()
        return self


class Translocation(Swapping):
    def __init__(self, *parameters):
        super().__init__()
        self._parameter = od.DataSource # Translocation is all about the elements themselves
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter
            
    def mutate(self, clip: oc.Clip) -> oc.Clip:
        if self.setup(clip):
            
            self._parameter = od.DataSource # Translocation is all about the elements themselves
            source_incision: int = self._chaos * self._step % int() % self._clip.len()
            target_incision: int = self._chaos * self._step % int() % clip.len()

            clip._items[target_incision:], self._clip._items[source_incision:] \
                = self._clip._items[source_incision:], clip._items[target_incision:]

        return clip


class Crossover(Swapping):

    def mutate(self, clip: oc.Clip) -> oc.Clip:
        if self.setup(clip):
            clip_len: int = clip.len()
            for element_i in range(clip_len):
                if self._chaos * self._step % int() % 2 == 0:   # Even
                    self.swap(clip, element_i, element_i)
        return clip

class Operation(Mutation):
    def __init__(self, *parameters):
        super().__init__()
        self._clips: list[oc.Clip] = []
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case list():            return self._clips
                    case _:                 return super().__mod__(operand)
            case list():            return self.deep_copy(self._clips)
            case _:                 return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["clips"] = self.serialize(self._clips)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "clips" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._clips = self.deserialize(serialization["parameters"]["clips"])
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Operation():
                super().__lshift__(operand)
                self._clips = self.deep_copy(operand._clips)
            case od.DataSource():
                match operand._data:
                    case list():            self._clips = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():        self._clips = self.deep_copy(operand)
            case _:             super().__lshift__(operand)
        
        return self

    def __iadd__(self, operand: any) -> Self:
        match operand:
            case oc.Clip():
                if operand.len() > 0:
                    self._clips.append(operand.copy())
            case list():
                for clip in operand:
                    self += clip
            case tuple():
                for single_operand in operand:
                    self += single_operand
            case _:
                super().__iadd__(operand)
        return self

    def __isub__(self, operand: any) -> Self:
        match operand:
            case oc.Clip():
                self._clips = [
                        single_clip for single_clip in self._clips if single_clip != operand
                    ]
            case list():
                self._clips = [
                        single_clip for single_clip in self._clips
                        if all(single_clip != operand_clip for operand_clip in operand)
                    ]

            case tuple():
                for single_operand in operand:
                    self -= single_operand
            case _:
                super().__isub__(operand)
        return self

class Multiplication(Operation):
    def mutate(self, clip: o.T) -> o.T:
        if isinstance(clip, oc.Clip):
            shuffled_clips: list[oc.Clip] = self.shuffle_list(self._clips)
            multiplied_clips: oc.Clip = oc.Clip()
            for single_clip in shuffled_clips:
                multiplied_clips *= single_clip
            clip <<= multiplied_clips // list()
        return clip

class Division(Operation):
    def mutate(self, clip: o.T) -> o.T:
        if isinstance(clip, oc.Clip):
            shuffled_clips: list[oc.Clip] = self.shuffle_list(self._clips)
            multiplied_clips: oc.Clip = oc.Clip()
            for single_clip in shuffled_clips:
                multiplied_clips /= single_clip
            clip <<= multiplied_clips // list()
        return clip
