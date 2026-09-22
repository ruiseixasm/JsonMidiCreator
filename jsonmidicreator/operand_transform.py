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
# Json Midi Creator Libraries
from . import creator as c
from . import operand as o

from . import operand_label as ol
from . import operand_data as od
from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_generic as og
from . import operand_element as oe
from . import operand_container as oc
from . import operand_frame as of
from . import operand_chaos as ch
from . import operand_tamer as ot

if TYPE_CHECKING:
    from operand_element import Element
    from operand_container import Clip


class Transform(o.Operand):
    """`Transform`

    `Transform` is intended to manipulate a `Clip` based on a given transformation process.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        return clip
    


class Edit(Transform):
    """`Transform -> Edit`

    Allows the application of an edition on a targeted `Clip`
        
    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the targeted `Clip` where the editions starts.
    Clip() : The `Clip` to be used as the source of the edition.
    """
    def __init__(self, *parameters):
        from . import operand_container as oc
        self._position_beats: Fraction = Fraction(0)
        self._source_clip: oc.Clip = oc.Clip()
        super().__init__(*parameters)


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Position():
                        return operand._data << ra.Position(self._time_signature, self._position_beats)
                    case _:                 return self._source_clip % operand
            case ra.Position():
                return operand.copy(self._source_clip._time_signature, self._position_beats)
            case ra.TimeUnit():
                # For TimeUnit only the `% operand` does the measure_module of it
                return ra.Position(self._source_clip._time_signature, self._position_beats) % operand
            case ra.Duration() | ra.Length():
                return operand.copy(self._source_clip._time_signature, self._source_clip % operand)
            case ra.TimeValue():
                return operand.copy(ra.Beats(self._time_signature, self._source_clip % ra.Duration() % operand))
            case og.Locus():
                edit_locus: og.Locus = og.Locus() << self % ra.Position()
                edit_locus << self % ra.Duration()
                return edit_locus
            case list():            return self % og.Locus() % list()
            case int():             return self._source_clip % ra.Position() % ra.Measure() % int()
            case og.Segment():         return operand.copy(self % ra.Position())
            case float():           return self._source_clip % ra.Duration() % float()
            case Fraction():        return self._source_clip % ra.Duration() % Fraction()
            case _:                 return self._source_clip % operand


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["position_beats"]   = o.serialize(self._position_beats)
        serialization["parameters"]["source_clip"]      = o.serialize(self._source_clip)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Element':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position_beats" in serialization["parameters"] and "source_clip" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position_beats    = o.deserialize(serialization["parameters"]["position_beats"])
            self._source_clip       = o.deserialize(serialization["parameters"]["source_clip"])
        return self

    def __lshift__(self, operand: any) -> Self:
        from . import operand_element as oe
        from . import operand_container as oc
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Edit():
                super().__lshift__(operand)
                self._position_beats    = operand._position_beats
                self._source_clip       = operand._source_clip.copy()
            case od.Pipe():
                match operand._data:
                    case ra.Position():     self._position_beats = operand._data._rational
                    case _:                 self._source_clip << operand
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Position():
                self._position_beats        = operand._rational
            case ra.Convertible():
                # The setting of the TimeUnit depends on the Element position
                self._position_beats = ra.Position(self._source_clip._time_signature, self._position_beats, operand) % Fraction()
            case og.Locus():
                self._position_beats = operand._position_beats
            case list():
                self << og.Locus(operand)
            case str():
                self << ra.Convertible.get_convertible_from_string(operand)
            case int():
                self._position_beats = ra.Measure(self._source_clip._time_signature, operand) % ra.Beats() % Fraction()
            case og.Segment():
                if operand._segment:
                    self << ra.Measure(operand._segment[0])
                    if len(operand._segment) == 2:
                        self << ra.Beat(operand._segment[1])
                    elif len(operand._segment) > 2:
                        self << ra.Step(operand._segment[2])
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                self._source_clip << operand
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case ra.Position():
                self._position_beats += operand._rational
            case _:
                self._source_clip += operand
        return self

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case ra.Position():
                self._position_beats -= operand._rational
            case _:
                self._source_clip -= operand
        return self


class Replace(Edit):
    """`Transform -> Edit -> Replace`

    Allows the substitution on a target `Clip` section by the source `Clip` duration.
        
    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the targeted `Clip` where the editions starts.
    Clip() : The `Clip` to be used as the source of the edition.
    """
    
    def _transform(self, clip: 'Clip') -> 'Clip':
        splitting_locus = og.Locus(self._source_clip, ra.Position(self._position_beats))
        splitting_locus << self._source_clip % ra.Duration()
        clip //= splitting_locus
        clip += self._source_clip + self % ra.Position()
        return clip


class Insert(Edit):
    """`Transform -> Edit -> Insert`

    Allows the insertion on a target `Clip` a section defined by a source `Clip` duration.
        
    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the targeted `Clip` where the editions starts.
    Clip() : The `Clip` to be used as the source of the edition.
    """
    
    def _transform(self, clip: 'Clip') -> 'Clip':
        insertion_locus = og.Locus(self._source_clip, ra.Position(self._position_beats))
        insertion_locus << self._source_clip % ra.Duration()
        clip += insertion_locus
        clip += self._source_clip + self % ra.Position()
        return clip


class Overlap(Edit):
    """`Transform -> Edit -> Overlap`

    Allows the placing over a target `Clip` with a source `Clip` at a given position.
        
    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the targeted `Clip` where the editions starts.
    Clip() : The `Clip` to be used as the source of the edition.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        clip += self._source_clip + self % ra.Position()
        return clip
    


class Sort(Transform):
    """`Generic -> Transform -> Sort`

    Sorts the contained items by a given parameter type.

    Args:
        parameter (type): Defines the given parameter type to sort by.
        reverse (bool): Reverses the sorting if `True`.
    """
    def __init__(self, parameter: type = og.Pitch, reverse: bool = False):
        self._parameter = parameter
        self._reverse = reverse
        super().__init__()


    def _transform(self, clip: 'Clip') -> 'Clip':
        original_positions: list[Fraction] = [
            element._position_beats for element in clip.elements_unmasked()
        ]
        compare = self._parameter()
        sorted_items: list = self._items.copy().sort(
            key=lambda x: x % compare
        )
        self << od.Pipe( sorted_items )
        if self._reverse:
            self._items.reverse()
        for index, element in enumerate(clip.elements_unmasked()):
            element._position_beats = original_positions[index]
        return clip


class Extend(Transform):
    """`Transform -> Extend`

    Extends (stretches) the given clip along a given length.

    Args:
        length(2.0) : The length along which the clip will be extended (stretched).
    """
    def __init__(self, length: 'ra.Length' = None):
        self._length: ra.Length = length
        super().__init__()

    def _transform(self, clip: 'Clip') -> 'Clip':
        if self._length is None:
            self._length = ra.Length(2.0)
        original_self: Clip = clip.shallow_copy()
        original_self_duration: ra.Duration = clip % ra.Duration()
        while clip % ra.Duration() + original_self_duration <= self._length:
            clip.__itruediv__(original_self)
        return clip


class Fill(Transform):
    """`Transform -> Fill`

    Adds up Rests to empty spaces (lengths) in a staff for each Measure.

    Args:
        None
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        shallow_copy: Clip = clip.shallow_copy()._sort_items()
        shallow_copy_len: int = shallow_copy.len_unmasked()
        for index in range(shallow_copy_len):
            current_element: oe.Element = shallow_copy._items[index]
            next_element: oe.Element = shallow_copy._items[index + 1]
            if current_element.finish() < next_element.start():
                rest_length: ra.Length = ra.Length( next_element.start() - current_element.finish() )
                rest_element: oe.Rest = \
                    oe.Rest()._set_owner_clip(clip) \
                    << rest_length
                clip += rest_element
        
        last_element: oe.Element = shallow_copy[shallow_copy_len - 1]
        staff_end: ra.Position = (last_element.finish() % ra.Length()).roundMeasures() % ra.Position()
        if last_element.finish() < staff_end:
            rest_length: ra.Length = ra.Length( staff_end - last_element.finish() )
            rest_element: oe.Rest = \
                oe.Rest()._set_owner_clip(clip) \
                << rest_length
            clip += rest_element
        return clip


class Fit(Transform):
    """`Transform -> Fit`

    Moves the `Position` of the following Elements to match the finish of the previous
    `Element` by keeping its finish Position, meaning, by changing its `Duration`.

    Args:
        None
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        for i, single_element in enumerate(clip._items):
            # Sets the Position and the Duration
            if i > 0:   # Not the first Element
                previous_element = clip._items[i - 1]
                previous_element_finish_beats = previous_element._position_beats + previous_element._duration_beats
                single_element_finish_beats = single_element._position_beats + single_element._duration_beats
                if previous_element_finish_beats < single_element_finish_beats:
                    single_element._duration_beats = single_element_finish_beats - previous_element_finish_beats
                    single_element._position_beats = previous_element_finish_beats
        return clip


class Monofy(Transform):
    """`Transform -> Monofy`

    Cuts out any part of an element Duration that overlaps with the next element.

    Args:
        None
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        if clip.len_unmasked() > 1:
            # Starts by sorting by Position
            shallow_copy: Clip = clip.shallow_copy()._sort_items()
            for index in range(shallow_copy.len_unmasked()):
                current_element: oe.Element = shallow_copy._items[index]
                next_element: oe.Element = shallow_copy._items[index + 1]
                if current_element.finish() > next_element.start():
                    new_length: ra.Length = ra.Length( next_element.start() - current_element.start() )
                    current_element << new_length
        return clip


class Invert(Transform):
    """`Transform -> Invert`

    `Invert` is similar to `Mirror` but based in a center defined by the first note on which all notes are vertically mirrored.

    Args:
        by_degree (bool): If `True` an inversion by Degree accordingly to the Key Signature, similar to the typical Staff, if False, \
            does a chromatic inversion by pitch like in a piano roll. The default is `True`.
    """
    def __init__(self, by_degree: bool = True):
        self._by_degree: bool = by_degree
        super().__init__()


    def _transform(self, clip: 'Clip') -> 'Clip':
        if self._by_degree:
            center_degree_0: ou.Degree = None
            
            for note in clip.elements_unmasked():
                if isinstance(note, oe.Note):
                    center_degree_0 = note._pitch._absolute_degree_0()
                    break

            for note in clip.elements_unmasked():
                if isinstance(note, oe.Note):
                    note_degree_0: ou.Degree = note._pitch._absolute_degree_0()
                    degree_distance: ou.Degree = note_degree_0 - center_degree_0
                    # Removes twice, safer than removing 2x
                    note._pitch -= degree_distance  # Recenter position
                    note._pitch -= degree_distance  # Moves in opposite direction
        else:
            pitch_centroid: int = None
            for note in clip.elements_unmasked():
                if isinstance(note, oe.Note):
                    pitch_centroid = note._pitch.get_absolute_pitch()
                    break
            for note in clip.elements_unmasked():
                if isinstance(note, oe.Note):
                    note_pitch: int = note._pitch.get_absolute_pitch()
                    if note_pitch != pitch_centroid:
                        note._pitch << 2 * pitch_centroid - note_pitch
        return clip



class Mirror(Transform):
    """`Transform -> Mirror`

    `Mirror` is similar to reverse but instead of reversing the elements position it reverses the
    Note's respective Pitch, like vertically mirrored.

    Args:
        by_degree (bool): If `True` a mirror by Degree accordingly to the Key Signature, similar to the typical Staff, if False, \
            does a chromatic mirror by pitch like in a piano roll. The default is `True`.
    """
    def __init__(self, by_degree: bool = True):
        self._by_degree: bool = by_degree
        super().__init__()


    def _transform(self, clip: 'Clip') -> 'Clip':
        if self._by_degree:
            top_absolute_degree: ou.Degree | None = None
            base_absolute_degree: ou.Degree | None = None
            for element in clip.elements_unmasked():
                if isinstance(element, oe.Note):
                    note_absolute_degree: ou.Degree = element % od.Pipe(ou.Degree())
                    if top_absolute_degree is None:
                        top_absolute_degree = note_absolute_degree
                        base_absolute_degree = note_absolute_degree
                    elif note_absolute_degree > top_absolute_degree:
                        top_absolute_degree = note_absolute_degree
                    elif note_absolute_degree < base_absolute_degree:
                        base_absolute_degree = note_absolute_degree
            if top_absolute_degree is not None:
                for element in clip.elements_unmasked():
                    if isinstance(element, oe.Note):
                        note_absolute_degree: ou.Degree = element % od.Pipe(ou.Degree())
                        degree_from_top: ou.Degree = top_absolute_degree - note_absolute_degree
                        degree_from_base: ou.Degree = note_absolute_degree - base_absolute_degree
                        element += degree_from_top - degree_from_base
        else:
            higher_pitch: og.Pitch | None = None
            lower_pitch: og.Pitch | None = None
            for element in clip.elements_unmasked():
                if isinstance(element, oe.Note):
                    note_pitch: og.Pitch = element._pitch
                    if higher_pitch is None:
                        higher_pitch = note_pitch
                        lower_pitch = note_pitch
                    elif note_pitch > higher_pitch:
                        higher_pitch = note_pitch
                    elif note_pitch < lower_pitch:
                        lower_pitch = note_pitch
            if higher_pitch is not None:
                top_pitch_int: int = higher_pitch.get_absolute_pitch()
                bottom_pitch_int: int = lower_pitch.get_absolute_pitch()

                for element in clip.elements_unmasked():
                    if isinstance(element, oe.Note):
                        note_pitch: og.Pitch = element._pitch
                        note_pitch_int: int = note_pitch.get_absolute_pitch()
                        new_pitch: int = top_pitch_int - (note_pitch_int - bottom_pitch_int)
                        note_pitch.set_absolute_pitch(new_pitch)
        return clip



class Flip(Transform):
    """`Transform -> Flip`

    `Flip` works like `Reverse` but it's agnostic about the Measure keeping the elements positional range.

    Args:
        None
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        position_duration_beats: list[dict[str, Fraction]] = []
        for index, single_element in enumerate(clip.elements_unmasked()):
            position_duration_dict: dict[str, Fraction] = {
                "duration": single_element._duration_beats
            }
            if index == 0:
                position_duration_dict["position"] = single_element._position_beats
            else:
                position_duration_dict["position"] = \
                    position_duration_beats[0]["position"] + position_duration_beats[0]["duration"]
            position_duration_beats.insert(0, position_duration_dict)   # last one at position 0
        for index, single_element in enumerate(clip.elements_unmasked()):
            single_element._position_beats = position_duration_beats[index]["position"]
            single_element._duration_beats = position_duration_beats[index]["duration"]
        return clip



class Rotate(Transform):
    """`Transform -> Rotate`

    `Rotate` does a right rotation of all elements by a given amount of rotation

    Args:
        amount (int): The right rotation amount of the list index, displacement.
        move_duration (bool): Rotates the duration of the elements too (the default).
    """
    def __init__(self, amount: int = 1, move_duration = True):
        self._amount: int = amount
        self._move_duration: int = move_duration
        super().__init__()


    def _transform(self, clip: 'Clip') -> 'Clip':
        rotated_elements: list[oe.Element] = clip.elements_unmasked().copy()
        elements_locus: list[og.Locus] = [
            single_element % og.Locus() for single_element in rotated_elements
        ]
        for _ in range(self._amount):
            rotated_elements = o.list_rotate(rotated_elements, self._amount)
            if self._move_duration:
                for rotated_elements, single_locus in zip(rotated_elements, elements_locus):
                    single_locus._duration_beats = rotated_elements._duration_beats
                remainder_duration_beats: Fraction = Fraction(0)
                for rotated_elements, single_locus in zip(rotated_elements, elements_locus):
                    single_locus._position_beats += remainder_duration_beats
                    remainder_duration_beats += rotated_elements._duration_beats - single_locus._duration_beats
        for rotated_elements, single_locus in zip(rotated_elements, elements_locus):
            rotated_elements << single_locus
        return clip



