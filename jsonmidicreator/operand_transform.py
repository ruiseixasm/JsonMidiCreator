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
    """`Transform -> Sort`

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



class Link(Transform):
    """`Transform -> Link`

    Adjusts the `Duration` of each element to link its finish with the start of the next element.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        unmasked_elements: list[oe.Element] = clip.elements_unmasked()
        last_index: int = len(unmasked_elements) - 1
        for i, single_element in enumerate(unmasked_elements):
            # Sets the Duration
            if i < last_index:   # Not the last Element
                next_element = unmasked_elements[i + 1]
                if next_element._position_beats > single_element._position_beats:
                    single_element._duration_beats = next_element._position_beats - single_element._position_beats
        return clip



class Stack(Transform):
    """`Transform -> Stack`

    Moves each Element to start at the finish `Position` of the previous one.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        unmasked_elements: list[oe.Element] = clip.elements_unmasked()
        for index, single_element in enumerate(unmasked_elements):
            if index > 0:   # Not the first element
                duration_beats: Fraction = unmasked_elements[index - 1]._duration_beats
                single_element._position_beats = unmasked_elements[index - 1]._position_beats + duration_beats  # Stacks on Element Duration
        return clip


class Close(Transform):
    """`Transform -> Close`

    Sets the finish `Position` of the last `Element` to match the end if its occupying `Measure`.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        unmasked_elements: list[oe.Element] = clip.elements_unmasked()
        if unmasked_elements:
            last_index: int = len(unmasked_elements) - 1
            last_element: oe.Element = unmasked_elements[last_index]
            last_element._duration_beats = self.gross_length()._rational - last_element._position_beats
        return self


class Decompose(Transform):
    """`Transform -> Decompose`

    Transform each element in its component elements if it's a composed element,
    like a chord that is composed of multiple notes, so, it becomes those multiple notes instead.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        return clip.decompose()


class Tie(Transform):
    """`Transform -> Tie`

    Adjusts the pitch of successive notes to the previous one and sets all Notes as tied.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        clip_notes: list[oe.Note] = [
            single_note for single_note in clip.elements_unmasked() if type(single_note) is oe.Note
        ]
        last_extended_notes: dict[int, oe.Note] = {}
        for single_note in clip_notes:
            note_channel_pitch: int = single_note._channel_0 << 8 | single_note._pitch.get_absolute_pitch()
            if note_channel_pitch in last_extended_notes:
                homologous_note: oe.Note = last_extended_notes[note_channel_pitch]
                homologous_note_finish_position_beats: Fraction = homologous_note.finish()._rational
                single_note_start_position_beats: Fraction = single_note._position_beats
                if single_note_start_position_beats == homologous_note_finish_position_beats:
                    single_note << ou.Tied(True)
            last_extended_notes[note_channel_pitch] = single_note   # Overrides previous existing notes (sorted by position)
        return clip


class Merge(Transform):
    """`Transform -> Merge`

    Adjusts the pitch of successive notes to the previous one and sets all Notes as tied.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        previous_element: oe.Element | None = None
        elements_to_remove: list[oe.Element] = []
        for unmasked_element in clip.elements_unmasked():
            if previous_element is not None and unmasked_element.start() == previous_element.finish():
                elements_to_remove.append(unmasked_element)
                previous_element._duration_beats += unmasked_element._duration_beats
                continue
            previous_element = unmasked_element
        return clip._delete(elements_to_remove, True)



class Interpolate(Transform):
    """`Transform -> Interpolate`

    Interpolates the multiple values of a given `Automation` element by `Channel`.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        automation_clip: Clip = clip.select(of.InputType(oe.Automatable))
        plotlist: list[dict] = automation_clip.getPlotlist()
        automation_channels: list[int] = plotlist[0]["channels"]["automation"]
        for channel_0 in automation_channels:
            channel_automation: Clip = automation_clip.select(ou.Channel(channel_0 + 1))
            if channel_automation.len_unmasked() > 1:
                element_template: oe.Element = channel_automation[0].copy()
                # Find indices of known values
                known_indices = [
                    element % ra.Position() % ra.Steps() % int() for element in channel_automation._items
                ]
                total_messages: int = known_indices[-1] - known_indices[0] + 1
                pattern_values = [ None ] * total_messages
                element_index: int = 0
                for index in range(total_messages):
                    if index in known_indices:
                        # Extracts int as what is being automated
                        pattern_values[index] = channel_automation[element_index] % int()
                        element_index += 1
                # Calls a static method
                automation = clip._interpolate_list(known_indices, pattern_values)
                position_steps: ra.Steps = ra.Steps(0)
                for index, value in enumerate(automation):
                    if index not in known_indices:   # None adds no Element
                        channel_automation += element_template << value << position_steps
                    position_steps += 1
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



class Reverse(Transform):
    """`Transform -> Reverse`

    Reverses the sequence of the clip concerning the elements `Position`.

    Args:
        None
    """
    def __init__(self, amount: int = 1, reverse_duration = True):
        self._amount: int = amount
        self._move_duration: int = reverse_duration
        super().__init__()


    def _transform(self, clip: 'Clip') -> 'Clip':
        reversed_elements: list[oe.Element] = clip.elements_unmasked().copy()
        elements_locus: list[og.Locus] = [  # Decoupled data
            single_element % og.Locus() for single_element in reversed_elements
        ]
        reversed_elements = o.list_reverse(reversed_elements)
        if self._move_duration:
            remainder_duration_beats: Fraction = Fraction(0)
            for single_element, single_locus in zip(reversed_elements, elements_locus):  # Duration doesn't change
                single_element._position_beats = single_locus._position_beats + remainder_duration_beats
                remainder_duration_beats += single_element._duration_beats - single_locus._duration_beats
        else:
            for single_element, single_locus in zip(reversed_elements, elements_locus):
                single_element << single_locus
        return clip



class Rotate(Transform):
    """`Transform -> Rotate`

    `Rotate` does a left rotation of all elements by a given amount of rotation

    Args:
        amount (int): The left rotation amount of the list index, displacement.
        move_duration (bool): Rotates the duration of the elements too (the default).
    """
    def __init__(self, amount: int = 1, rotate_duration = True):
        self._amount: int = amount
        self._move_duration: int = rotate_duration
        super().__init__()


    def _transform(self, clip: 'Clip') -> 'Clip':
        rotated_elements: list[oe.Element] = clip.elements_unmasked().copy()
        elements_locus: list[og.Locus] = [  # Decoupled data
            single_element % og.Locus() for single_element in rotated_elements
        ]
        rotated_elements = o.list_rotate(rotated_elements, self._amount)
        if self._move_duration:
            remainder_duration_beats: Fraction = Fraction(0)
            for single_element, single_locus in zip(rotated_elements, elements_locus):  # Duration doesn't change
                single_element._position_beats = single_locus._position_beats + remainder_duration_beats
                remainder_duration_beats += single_element._duration_beats - single_locus._duration_beats
        else:
            for single_element, single_locus in zip(rotated_elements, elements_locus):
                single_element << single_locus
        return clip



class Clean(Transform):
    """`Transform -> Clean`

    With time a `Clip` may accumulate redundant Elements, this method removes all those elements.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        unique_items: list[oe.Element] = []
        remove_items: list[oe.Element] = []
        for single_element in clip._items:
            for unique_element in unique_items:
                if single_element == unique_element:
                    remove_items.append(single_element)
                    break
            unique_items.append(single_element)
        return clip._delete(remove_items, True)



class Parameterized(Transform):
    """`Transform -> Parameterized`

    A `Parameterized` transformation allows the setting of multiple parameters in it.

    Parameters
    ----------
    tuple() : A parameterized `Transform` has multiple parameters setting the respective transformation.
    """
    def __init__(self, parameters: tuple = tuple()):
        super().__init__()
        self._parameters: dict[str, Any] = {}   # Empty by default


class Filter(Parameterized):
    """`Transform -> Parameterized -> Filter`

    A `Filter` works exactly like a `Mask` with the difference of keeping just \
        the matching items and deleting everything else.

    Args:
        condition (Any): Sets a condition to be compared with `==` operator.
    """
    def __init__(self, *conditions):
        super().__init__()
        self._parameters["conditions"] = conditions


    def _transform(self, clip: 'Clip') -> 'Clip':
        return clip.filter(*self._parameters["conditions"])



class Smooth(Parameterized):
    """`Transform -> Parameterized -> Smooth`

    Adjusts each `Note` octave to have the closest pitch to the first, previous one or both.

    Args:
        algorithm_type (int): Sets the type of algorithm to be used accordingly to the next table:
            +------+---------------------------------------------------------------------------+
            | Type | Description                                                               |
            +------+---------------------------------------------------------------------------+
            | 1    | Considers both pitch distances, from the first note and the previous one. |
            | 2    | Considers only the previous note pitch distance.                          |
            | 3    | Considers only the first note pitch distance.                             |
            | 4    | Considers the middle_pitch in relation to the previous one.               |
            | 5    | Considers the middle_pitch in relation to the first note. (default)       |
            +------+---------------------------------------------------------------------------+
    """
    def __init__(self, algorithm_type: int = 5):
        super().__init__()
        self._parameters["algorithm_type"] = algorithm_type


    def _transform(self, clip: 'Clip') -> 'Clip':
        first_pitch: int | None = None
        previous_pitch: int | None = None
        algorithm_type = self._parameters["algorithm_type"]
        for note in clip.elements_unmasked():
            if isinstance(note, oe.Note):    # Only Notes have Pitch
                if algorithm_type < 4:
                    note_pitch: int = note._pitch.get_absolute_pitch()
                    if first_pitch is None:
                        previous_pitch = first_pitch = note_pitch
                    else:
                        delta_pitch: int = note_pitch
                        if algorithm_type == 3:
                            delta_pitch -= first_pitch
                        else:
                            delta_pitch -= previous_pitch
                        octave_offset: int = delta_pitch // 12
                        remaining_delta: int = delta_pitch % 12
                        if remaining_delta > 6:
                            octave_offset += 1
                        elif remaining_delta < -6:
                            octave_offset -= 1
                        if algorithm_type == 1:
                            expected_pitch: int = note_pitch - octave_offset * 12
                            alternative_pitch: int = expected_pitch
                            if first_pitch > expected_pitch:
                                alternative_pitch += 12
                            else:
                                alternative_pitch -= 12
                            delta_expected_pitch: int = abs(expected_pitch - first_pitch) + abs(expected_pitch - previous_pitch)
                            delta_alternative_pitch: int = abs(alternative_pitch - first_pitch) + abs(alternative_pitch - previous_pitch)
                            if delta_alternative_pitch < delta_expected_pitch:
                                octave_offset -= (alternative_pitch - expected_pitch) // 12
                        note -= ou.Octave(octave_offset)
                        previous_pitch = note_pitch - octave_offset * 12
                else:   # center pitch based
                    note_pitch: int = note.pitch_centroid()
                    if note_pitch >= 0:
                        if first_pitch is None:
                            previous_pitch = first_pitch = note_pitch
                        else:
                            if note_pitch > previous_pitch:
                                above_pitch: int = note_pitch
                                while note_pitch > previous_pitch:
                                    above_pitch = note_pitch
                                    note_pitch = note.decrease_pitch_centroid().pitch_centroid()
                                if above_pitch - previous_pitch <= previous_pitch - note_pitch:
                                    note_pitch = note.increase_pitch_centroid().pitch_centroid()
                            elif note_pitch < previous_pitch:
                                below_pitch: int = note_pitch
                                while note_pitch < previous_pitch:
                                    below_pitch = note_pitch
                                    note_pitch = note.increase_pitch_centroid().pitch_centroid()
                                if previous_pitch - below_pitch <= note_pitch - previous_pitch:
                                    note_pitch = note.decrease_pitch_centroid().pitch_centroid()
                        if algorithm_type == 4:
                            previous_pitch = note_pitch
        return clip



class Slur(Parameterized):
    """`Transform -> Parameterized -> Slur`

    Changes the note `Gate` in order to crate a small overlap.

    Args:
        gate (float): Can be given a different gate from 1.05, de default.
    """
    def __init__(self, gate: float = 1.05):
        super().__init__()
        self._parameters["gate"] = gate


    def _transform(self, clip: 'Clip') -> 'Clip':
        last_element = None
        for item in clip.elements_unmasked():
            if isinstance(item, oe.Note):
                if last_element is not None:
                    last_element << ra.Gate(self._parameters["gate"])
                last_element = item
        return clip



class Join(Parameterized):
    """`Transform -> Parameterized -> Join`

    Joins all same type notes with the same `Pitch` as a single `Note`, from left to right.

    Args:
        decompose (bool): If `True`, decomposes elements derived from `Note` first (the default).
        strict (bool): If `True`, the finish position of the previous note has to match the start position
        of the next one (the default).
    """
    def __init__(self, decompose: bool = True, strict: bool = True):
        super().__init__()
        self._parameters["decompose"] = decompose
        self._parameters["strict"] = strict


    def _transform(self, clip: 'Clip') -> 'Clip':
        decompose = self._parameters["decompose"]
        strict = self._parameters["strict"]
        if decompose: clip.decompose()
        clip_notes: list[oe.Note] = [
            single_note for single_note in clip.elements_unmasked() if type(single_note) is oe.Note
        ]
        joined_notes: list[oe.Note] = []
        last_extended_notes: dict[int, oe.Note] = {}
        for single_note in clip_notes:
            note_channel_pitch: int = single_note._channel_0 << 8 | single_note._pitch.get_absolute_pitch()
            if note_channel_pitch in last_extended_notes:
                homologous_note: oe.Note = last_extended_notes[note_channel_pitch]
                homologous_note_finish_position_beats: Fraction = homologous_note.finish()._rational
                single_note_start_position_beats: Fraction = single_note._position_beats
                single_note_finish_position_beats: Fraction = single_note.finish()._rational
                if single_note_start_position_beats == homologous_note_finish_position_beats:
                    homologous_note._duration_beats += single_note._duration_beats
                    joined_notes.append(single_note)
                elif not strict and single_note_finish_position_beats > homologous_note_finish_position_beats:
                    homologous_note._duration_beats += single_note_finish_position_beats - homologous_note_finish_position_beats
                else:
                    last_extended_notes[note_channel_pitch] = single_note
            else:
                last_extended_notes[note_channel_pitch] = single_note   # Overrides previous existing notes (sorted by position)
        clip._delete(joined_notes)
        return clip



class Oscillate(Parameterized):
    """`Transform -> Parameterized -> Oscillate`

    Applies for each item element the value at the given position given by the oscillator function at
    that same position.

    Args:
        amplitude (int): Amplitude of the wave.
        wavelength (float): The length of the wave in note value.
        offset (int): Sets the horizontal axis of the wave.
        phase (int): Sets the starting degree of the wave.
        parameter (type): The parameter used as the one being automated by the wave.
    """
    def __init__(self, amplitude: int = 63, wavelength: float = 1/1, offset: int = 0, phase: int = 0,
                 parameter: type = None):
        super().__init__()
        self._parameters["amplitude"] = amplitude
        self._parameters["wavelength"] = wavelength
        self._parameters["offset"] = offset
        self._parameters["phase"] = phase
        self._parameters["parameter"] = parameter


    def _transform(self, clip: 'Clip') -> 'Clip':
        amplitude = self._parameters["amplitude"]
        wavelength = self._parameters["wavelength"]
        offset = self._parameters["offset"]
        phase = self._parameters["phase"]
        parameter = self._parameters["parameter"]
        for single_element in clip.elements_unmasked():
            element_position: ra.Position = single_element % ra.Position()
            wavelength_duration: Fraction = ra.Duration(wavelength)._rational
            wavelength_position: Fraction = element_position % ra.Duration() % Fraction()
            wavelength_ratio: Fraction = wavelength_position / wavelength_duration
            # The default unit of measurement of Position and Length is in Measures !!
            wave_phase: float = float(wavelength_ratio * 360 + phase)   # degrees
            # int * float results in a float
            # Fraction * float results in a float
            # Fraction * Fraction results in a Fraction
            value: int = int(amplitude * math.sin(math.radians(wave_phase)))
            value += offset
            if parameter is not None:
                single_element << parameter(value)
            else:
                single_element << value # Most of the time
        return clip



