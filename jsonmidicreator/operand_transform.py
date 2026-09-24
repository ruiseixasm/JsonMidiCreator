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
        if isinstance(self._chained_operand, Transform):
            return self._chained_operand(clip)
        return clip

    def next(self, clip: 'oc.Clip') -> 'oc.Clip':
        """Runs each tail"""


    
    def copy(self, *parameters) -> Self:
        # Frame class IS a Read-only class
        return self


class Operate(Transform):
    """`Transform -> Operate`

    Accepts a `lambda` function to act as a generic transformation.

    Args:
        operator : A callable function that accepts a `Clip` and returns that same `Clip` \
        with the default as `lambda clip: clip`.
    """
    def __init__(self, operator: Callable[['oc.Clip'], 'oc.Clip'] = lambda clip: clip):
        super().__init__()
        self._operator: Callable[['oc.Clip'], 'oc.Clip'] = lambda clip: clip
        if callable(operator):
            self._operator = operator


    def _transform(self, clip: 'Clip') -> 'Clip':
        self._operator(clip)
        return super()._transform(clip)



class Delete(Transform):
    """`Transform -> Delete`

    Deletes all the given items in the present container and propagates the deletion
    of the same items for the containers above.

    Args:
        None
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        clip._delete(clip.elements_unmasked(), True)    # Already recursive
        return super()._transform(clip)



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
        return super()._transform(clip)


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
        return super()._transform(clip)


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
        return super()._transform(clip)



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
        return super()._transform(clip)



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
        return super()._transform(clip)


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
        return super()._transform(clip)


class Decompose(Transform):
    """`Transform -> Decompose`

    Transform each element in its component elements if it's a composed element,
    like a chord that is composed of multiple notes, so, it becomes those multiple notes instead.

    Args:
        None.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        clip.decompose()
        return super()._transform(clip)


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
        return super()._transform(clip)


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
        clip._delete(elements_to_remove, True)
        return super()._transform(clip)



class Interpolate(Transform):
    """`Transform -> Interpolate`

    Interpolates the multiple values of a given `Automation` element by `Channel`.

    Args:
        None.
    """
    @staticmethod
    def _interpolate_list(known_indices, pattern_values) -> list:

        automation = pattern_values[:] # makes a copy of pattern_values
            
        for i in range(len(pattern_values)):
            if automation[i] is None:
                    # Find closest known values before and after
                left_idx = max([idx for idx in known_indices if idx < i], default=None)
                right_idx = min([idx for idx in known_indices if idx > i], default=None)
                    
                if left_idx is None:
                    automation[i] = automation[right_idx]   # Use the right value if no left
                elif right_idx is None:
                    automation[i] = automation[left_idx]    # Use the left value if no right
                else:
                        # Linear interpolation
                    left_val = automation[left_idx]
                    right_val = automation[right_idx]
                    step = (right_val - left_val) / (right_idx - left_idx)
                    automation[i] = int(left_val + step * (i - left_idx))

        return automation


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
                automation = Interpolate._interpolate_list(known_indices, pattern_values)
                position_steps: ra.Steps = ra.Steps(0)
                for index, value in enumerate(automation):
                    if index not in known_indices:   # None adds no Element
                        channel_automation += element_template << value << position_steps
                    position_steps += 1
        return super()._transform(clip)



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
        return super()._transform(clip)


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
        return super()._transform(clip)



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
        return super()._transform(clip)



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
        return super()._transform(clip)



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
        return super()._transform(clip)



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
        clip._delete(remove_items, True)
        return super()._transform(clip)



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



class Edit(Parameterized):
    """`Transform -> Parameterized -> Edit`

    Allows the application of an edition on a targeted `Clip`
        
    Parameters
    ----------
    Locus() : The locus on the targeted `Clip` where the editions happens.
    Clip() : The `Clip` to be used as the source of the edition.
    """
    def __init__(self, locus: og.Locus = None, clip: oc.Clip = None):
        super().__init__()
        self._parameters["locus"] = og.Locus(locus)
        self._parameters["clip"] = oc.Clip(clip)



class Replace(Edit):
    """`Transform -> Parameterized -> Edit -> Replace`

    Allows the substitution on a target `Clip` section by the source `Clip` duration.
        
    Parameters
    ----------
    Locus() : The locus on the targeted `Clip` where the editions happens.
    Clip() : The `Clip` to be used as the source of the edition.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        clip //= self._parameters["locus"]
        clip += self._parameters["clip"] + self._parameters["locus"] % ra.Position(clip)
        return super()._transform(clip)



class Insert(Edit):
    """`Transform -> Parameterized -> Edit -> Insert`

    Allows the insertion on a target `Clip` a section defined by a source `Clip` duration.
        
    Parameters
    ----------
    Locus() : The locus on the targeted `Clip` where the editions happens.
    Clip() : The `Clip` to be used as the source of the edition.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        clip += self._parameters["locus"]
        clip += self._parameters["clip"] + self._parameters["locus"] % ra.Position(clip)
        return super()._transform(clip)



class Overlap(Edit):
    """`Transform -> Parameterized -> Edit -> Overlap`

    Allows the placing over a target `Clip` with a source `Clip` at a given position.
        
    Parameters
    ----------
    Locus() : The locus on the targeted `Clip` where the editions happens.
    Clip() : The `Clip` to be used as the source of the edition.
    """
    def _transform(self, clip: 'Clip') -> 'Clip':
        clip += self._parameters["clip"] + self._parameters["locus"] % ra.Position(clip)
        return super()._transform(clip)
    


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
        clip.filter(*self._parameters["conditions"])
        return super()._transform(clip)



class Sort(Parameterized):
    """`Transform -> Parameterized -> Sort`

    Sorts the contained items by a given parameter type.

    Args:
        parameter (type): Defines the given parameter type to sort by.
        reverse (bool): Reverses the sorting if `True`.
    """
    def __init__(self, parameter: type = og.Pitch, reverse: bool = False):
        super().__init__()
        self._parameters["parameter"] = parameter
        self._parameters["reverse"] = reverse


    def _transform(self, clip: 'Clip') -> 'Clip':
        original_positions: list[Fraction] = [
            element._position_beats for element in clip.elements_unmasked()
        ]
        compare = self._parameters["parameter"]()
        sorted_items: list = self._items.copy().sort(
            key=lambda x: x % compare
        )
        self << od.Pipe( sorted_items )
        if self._parameters["reverse"]:
            self._items.reverse()
        for index, element in enumerate(clip.elements_unmasked()):
            element._position_beats = original_positions[index]
        return super()._transform(clip)




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
        return super()._transform(clip)



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
        return super()._transform(clip)



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
        return super()._transform(clip)



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
        return super()._transform(clip)




class Automate(Parameterized):
    """`Transform -> Parameterized -> Automate`

    Distributes the values given by the Steps pattern in a way very like the stepper Drum Machine fashion.

    Args:
        values (list[int]): The automation values at the triggered steps.
        pattern (str): A string where the 1s in it are where the triggered midi messages are.
        automation (Any): The type of automation wanted, like, Aftertouch, PitchBend or ControlChange,
        the last one being the default.
        interpolate (bool): Does an interpolation per `Step` between the multiple triggered steps.
    """
    def __init__(self, values: list[int] = [100, 70, 30, 100],
                 pattern: str = "1... 1... 1... 1...", automation: Any = "Modulation", interpolate: bool = True):
        super().__init__()
        self._parameters["values"] = values
        self._parameters["pattern"] = pattern
        self._parameters["automation"] = automation
        self._parameters["interpolate"] = interpolate


    def _transform(self, clip: 'Clip') -> 'Clip':
        values = self._parameters["values"]
        pattern = self._parameters["pattern"]
        automation = self._parameters["automation"]
        interpolate = self._parameters["interpolate"]
        if isinstance(pattern, str):
            # ControlChange, PitchBend adn Aftertouch Elements have already 1 Step of Duration
            if isinstance(automation, oe.Aftertouch):
                automate_element: oe.Element = \
                    oe.Aftertouch()._set_owner_clip(clip) \
                    << automation
                # Ensure values is a non-empty list with only integers ≥ 0
                if not (isinstance(values, list) and values and all(isinstance(v, int) for v in values)):
                    values = [30, 70, 50, 0]
            elif isinstance(automation, oe.PitchBend) or automation is None:  # Pitch Bend, special case
                automate_element: oe.Element = \
                    oe.PitchBend()._set_owner_clip(clip) \
                    << automation
                # Ensure values is a non-empty list with only integers ≥ 0
                if not (isinstance(values, list) and values and all(isinstance(v, int) for v in values)):
                    values = [-20*64, -70*64, -50*64, 0*64]
            else:
                automate_element: oe.Element = \
                    oe.ControlChange()._set_owner_clip(clip) \
                    << automation
                # Ensure values is a non-empty list with only integers ≥ 0
                if not (isinstance(values, list) and values and all(isinstance(v, int) and v >= 0 for v in values)):
                    values = [80, 50, 30, 100]
            pattern_values = []
            value_index = 0  # Keep track of which value to use
            for char in pattern.replace(" ", "").replace("-", ""):
                if char == "1":
                    pattern_values.append(values[value_index])
                    value_index = (value_index + 1) % len(values)  # Cycle through values
                else:
                    pattern_values.append(None)  # Empty slots
            automation = pattern_values[:] # makes a copy of pattern_values
            if interpolate:
                # Find indices of known values
                known_indices = [i for i, val in enumerate(pattern_values) if val is not None]
                if not known_indices:
                    raise ValueError("List must contain at least one integer.")
                else:
                    automation = clip._interpolate_list(known_indices, pattern_values)
            position_steps: ra.Steps = ra.Steps(0)
            for value in automation:
                if value is not None:   # None adds no Element
                    clip += automate_element << value << position_steps
                position_steps += 1
        return super()._transform(clip)



class Stepper(Parameterized):
    """`Transform -> Parameterized -> Stepper`

    Sets the steps in a Drum Machine for a given `Element`. The default element is `Note()` for None.

    Args:
        pattern (str): A string where the 1s in it set where the triggered steps are.
        element (Element): A element or any respective parameter that sets each element.
    """
    def __init__(self, pattern: str = "1... 1... 1... 1...", element: 'Element' = None):
        super().__init__()
        self._parameters["pattern"] = pattern
        self._parameters["element"] = element


    def _transform(self, clip: 'Clip') -> 'Clip':
        pattern = self._parameters["pattern"]
        element = self._parameters["element"]    
        if isinstance(pattern, str):
            # Fraction sets the Duration in Steps
            element_element: oe.Note = \
                oe.Note()._set_owner_clip(clip) \
                << Fraction(1) << element
            steps_place = o.string_to_list(pattern)
            position_steps: ra.Steps = ra.Steps(0)
            for single_step in steps_place:
                if single_step == 1:
                    clip += element_element << position_steps
                position_steps += 1
        return super()._transform(clip)



class Arpeggiate(Parameterized):
    """`Transform -> Parameterized -> Arpeggiate`

    Distributes each element accordingly to the configured arpeggio by the parameters given.

    Args:
        Order(1), int : The notes changing order, with 1 being the "Up" order.
        Duration(1/16), float : The duration after which the next note is played following the set `Order`.
        Swing(0.5) : Sets the amount of time the note is effectively pressed relatively to its total duration.
        Chaos(SinX()) : For the `Order` 5, "Chaotic", it uses the set Chaotic `Operand`.
    """
    def __init__(self, parameters: any = None):
        super().__init__()
        self._parameters["parameters"] = parameters


    def _transform(self, clip: 'Clip') -> 'Clip':
        parameters = self._parameters["parameters"]
        arpeggio = og.Arpeggio(parameters)
        arpeggio.arpeggiate_source(clip.elements_unmasked(), clip.start(), ra.Length( clip.net_duration() ))
        return super()._transform(clip)



class Quantize(Parameterized):
    """`Transform -> Parameterized -> Quantize`

    Quantizes a `Clip` by a given amount from 0.0 to 1.0.

    Args:
        amount (float): The amount of quantization to apply from 0.0 to 1.0.
        quantize_duration (bool): Includes the quantization of the `Duration` too.
    """
    def __init__(self, amount: float = 1.0, quantize_duration: bool = False):
        super().__init__()
        self._parameters["amount"] = amount
        self._parameters["quantize_duration"] = quantize_duration


    def _transform(self, clip: 'Clip') -> 'Clip':
        amount = self._amount["parameters"]
        quantize_duration = self._parameters["quantize_duration"]
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        amount_rational: Fraction = ra.Amount(amount) % Fraction()
        for single_element in clip.elements_unmasked():
            # Position On
            element_position_on: Fraction = single_element._position_beats
            unquantized_amount: Fraction = element_position_on % quantization_beats
            quantization_limit: int = round(unquantized_amount / quantization_beats)
            position_on_offset: Fraction = (quantization_limit * quantization_beats - unquantized_amount) * amount_rational
            single_element._position_beats += position_on_offset
            # Position Off
            if quantize_duration:
                element_position_off: Fraction = single_element._position_beats + single_element._duration_beats
                unquantized_amount = element_position_off % quantization_beats
                quantization_limit = round(unquantized_amount / quantization_beats)
                position_off_offset: Fraction = (quantization_limit * quantization_beats - unquantized_amount) * amount_rational
                single_element._duration_beats += position_off_offset
                while single_element._duration_beats <= Fraction(0):
                    single_element._duration_beats += quantization_beats
        return super()._transform(clip)

