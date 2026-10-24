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


class Action(o.Operand):
    """`Action`

    `Action` is intended to manipulate unmasked `Elements` in a `Clip` based on a given named action.
    The `action` method always returns the exact same inputted `Clip`.
    Contrary to a `Transformation`, an `Action` can be framed because it targets the Clip elements.
    """
    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        if isinstance(self._chained_operand, Action):
            return self._chained_operand.act(clip, scoped_elements)
        return clip



class Delete(Action):
    """`Action -> Delete`

    Deletes all the given elements in the targeted `Clip` keeping all the remaining ones.

    Args:
        None
    """
    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        clip.delete(scoped_elements, True)
        return super().act(clip, scoped_elements)


class Keep(Action):
    """`Action -> Keep`

    Keeps all the given elements in the targeted `Clip` by deleting all the unmasked remaining ones.

    Args:
        None
    """
    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        unmasked_elements: list[oe.Element] = clip.elements_unmasked()
        deleted_elements: list[oe.Element] = [
            single_masked for single_masked in unmasked_elements
            if not any(single_masked is single_scoped for single_scoped in scoped_elements)
        ]
        clip.delete(deleted_elements, True)
        return super().act(clip, scoped_elements)



class Aggregated(Action):
    """`Action -> Aggregated`

    `Aggregated` means that multiple Elements are processed at once and not just one by one,
    normally aggregated or grouped by `Position`.
    """
    pass



class AmountedAction(Aggregated):
    """`Action -> Aggregated -> AmountedAction`

    `AmountedAction` means an `Action` with an amount associated.
    
    Parameters
    ----------
    int(1) : Sets the amount for the Action
    """
    def __init__(self, *parameters):
        self._amount: int = 1
        super().__init__(*parameters)


    def __str__(self):
        return f'{self._amount}'

    def __neg__(self):
        self._amount *= -1
        return self

    def __bool__(self) -> bool:  # For Python 3
        return self._amount != 0

    def __nonzero__(self) -> bool:  # For Python 2
        return self.__bool__()
    
    def __not__(self) -> bool:
        return self._amount == 0
    
    def __eq__(self, other: any) -> bool:
        from . import operand_rational as ra
        match other:
            case AmountedAction():
                return self._amount == other._amount
            case int() | float() | Fraction():
                return self._amount == other
            case ou.Unit():
                return self._amount == other._unit
            case ra.Rational():
                return self._amount == int( other._rational )
            case od.Conditional():
                return other == self
        return False
    
    def __lt__(self, other: any) -> bool:
        from . import operand_rational as ra
        match other:
            case AmountedAction():
                return self._amount < other._amount
            case int() | float() | Fraction():
                return self._amount < other
            case ou.Unit():
                return self._amount < other._unit
            case ra.Rational():
                return self._amount < int( other._rational )
        return False
    
    def __gt__(self, other: any) -> bool:
        from . import operand_rational as ra
        match other:
            case AmountedAction():
                return self._amount > other._amount
            case int() | float() | Fraction():
                return self._amount > other
            case ou.Unit():
                return self._amount > other._unit
            case ra.Rational():
                return self._amount > int( other._rational )
        return False
    

    def __mod__(self, operand: o.T) -> o.T:
        from . import operand_rational as ra
        match operand:
            case od.Pipe():
                match operand._data:
                    case bool():            return False if self._amount == 0 else True   # bool is a subclass of int !!
                    case int():             return self._amount           # returns a int()
                    case Fraction():        return Fraction(self._amount)
                    case float():           return float(self._amount)
                    case _:                 return super().__mod__(operand)
            case bool():            return False if self._amount == 0 else True   # bool is a subclass of int !!
            case int():             return self._amount
            case Fraction():        return Fraction(self._amount)
            case float():           return float(self._amount)
            case ra.Rational():     return operand.copy() << od.Pipe( self._amount )
            case ou.Unit():            return operand.copy(self)
            case str():             return str(self._amount)
            case _:                 return super().__mod__(operand)


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["amount"] = self._amount
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "amount" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._amount = serialization["parameters"]["amount"]
        return self


    def __lshift__(self, operand: any) -> Self:
        from . import operand_rational as ra
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case AmountedAction():
                super().__lshift__(operand)
                self._amount = operand._amount
            case od.Pipe():
                match operand._data:
                    case float() | Fraction() | bool():   # bool is a subclass of int !!
                                                    self._amount = int(operand._data)
                    case int():                     self._amount = operand._data
                    case ou.Unit() | ra.Rational():    self._amount = operand._data % od.Pipe( int() )
            case float() | Fraction() | bool():   # bool is a subclass of int !!
                self._amount = int(operand)
            case int():
                self._amount = operand
            case ra.Rational():
                self._amount = operand % int()
            case str():
                try:
                    self << int(operand)
                except ValueError as e:
                    pass    # No need to print anything
                    # print(f"Error: {e}, '{operand}' is not a number!")
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ol.Null():
                return self
            case o.Operand():
                self << operand % self
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


    def __iadd__(self, number: any) -> Self:
        from . import operand_rational as ra
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case AmountedAction():
                self._amount += number._amount
            case int() | Fraction() | float():
                self._amount = int( self._amount + number )
            case ou.Unit():
                self._amount += number._unit
            case ra.Rational():
                self._amount = int( self._amount + number._rational )
        return self

    
    def __isub__(self, number: any) -> Self:
        from . import operand_rational as ra
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case AmountedAction():
                self._amount -= number._amount
            case int() | Fraction() | float():
                self._amount = int( self._amount - number )
            case ou.Unit():
                self._amount -= number._unit
            case ra.Rational():
                self._amount = int( self._amount - number._rational )
        return self

    
    def __imul__(self, number: any) -> Self:
        from . import operand_rational as ra
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case AmountedAction():
                self._amount *= number._amount
            case int() | Fraction() | float():
                self._amount = int( self._amount * number )
            case ou.Unit():
                self._amount *= number._unit
            case ra.Rational():
                self._amount = int( self._amount * number._rational )
        return self

    
    def __itruediv__(self, number: any) -> Self:
        from . import operand_rational as ra
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case AmountedAction():
                if number._amount != 0:
                    self._amount /= number._amount
            case int() | Fraction() | float():
                if number != 0:
                    self._amount = int( self._amount / number )
            case ou.Unit():
                if number._unit != 0:
                    self._amount = int( self._amount / number._unit )
            case ra.Rational():
                if number._rational != 0:
                    self._amount = int( self._amount / number._rational )
        return self



class Rotate(AmountedAction):
    """`Action -> Aggregated -> AmountedAction -> Rotate`

    `Rotate` does a left rotation of all elements by a given amount of rotation while keeping their structure.

    Args:
        Measure(1), TimeUnit : Rotates the duration of the elements too (1 Measure is the default)
        int(1) : The left rotation amount of the list index, displacement
    """
    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        element_loci: list[og.Locus] = [  # Decoupled data
            single_element % og.Locus() for single_element in scoped_elements
        ]
        # Does an implicit copy of `scoped_elements`
        rotated_elements = o.list_rotate(scoped_elements, self._amount)
        remainder_duration_beats: Fraction = Fraction(0)
        for single_element, single_locus in zip(rotated_elements, element_loci):  # Duration doesn't change
            single_element._position_beats = single_locus._position_beats + remainder_duration_beats
            remainder_duration_beats += single_element._duration_beats - single_locus._duration_beats
        return clip._sort_items()


class RotateLoci(AmountedAction):
    """`Action -> Aggregated -> AmountedAction -> RotateLoci`

    `RotateLoci` does a left rotation of all elements loci by a given amount of rotation.

    Args:
        Measure(1), TimeUnit : Rotates the duration of the elements too (1 Measure is the default)
        int(1) : The left rotation amount of the list index, displacement
    """
    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        element_loci: list[og.Locus] = [  # Decoupled data
            single_element % og.Locus() for single_element in scoped_elements
        ]
        # Does an implicit copy of `scoped_elements`
        rotated_elements = o.list_rotate(scoped_elements, self._amount)
        for single_element, single_locus in zip(rotated_elements, element_loci):
            single_element << single_locus
        return clip._sort_items()



class RotateSteps(AmountedAction):
    """`Action -> Aggregated -> AmountedAction -> RotateSteps`

    `RotateSteps` does a left rotation of all elements by a given amount of rotation among a given `Length`.

    Args:
        Measure(1), TimeUnit : Rotates the duration of the elements too (1 Measure is the default)
        int(1) : The left rotation amount of the list index, displacement
    """
    def __init__(self, *parameters):
        self._time_unit: ra.TimeUnit = ra.Measure(1)
        super().__init__(*parameters)


    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        if not scoped_elements:
            return clip

        length_beats: Fraction = self._time_unit.copy(clip) % ra.Beats() % Fraction()
        if length_beats <= 0:
            return clip

        # Convert the signed rotation amount from steps to beats.
        shift_beats: Fraction = ra.Step(clip, self._amount) % ra.Beats() % Fraction()

        # Rotate positions within globally aligned quantization intervals.
        for single_element in scoped_elements:
            position_beats = single_element._position_beats
            segment_start_beats = (position_beats // length_beats) * length_beats

            single_element._position_beats = (
                segment_start_beats + (position_beats - segment_start_beats - shift_beats) % length_beats
            )

        return clip._sort_items()


    def __mod__(self, operand: o.T) -> o.T:
        from . import operand_rational as ra
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.TimeUnit():     return self._time_unit
                    case _:                 return super().__mod__(operand)
            case ra.TimeUnit():
                return self._time_unit.copy()
            case ra.Length():
                return operand.copy(self._time_unit)
            case _:
                return super().__mod__(operand)


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["time_unit"] = self._time_unit
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "time_unit" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._time_unit = serialization["parameters"]["time_unit"]
        return self


    def __lshift__(self, operand: any) -> Self:
        from . import operand_rational as ra
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case RotateSteps():
                super().__lshift__(operand)
                self._time_unit = operand._time_unit.copy()
            case od.Pipe():
                match operand._data:
                    case ra.TimeUnit():             self._time_unit = operand._data
                    case _:                         super().__lshift__(operand)
            case ra.TimeUnit():
                self._time_unit = operand.copy()
            case ra.Length():
                self << ra.Beat(operand._rational)
            case _:
                super().__lshift__(operand)
        return self



class Invert(AmountedAction):
    """`Action -> Aggregated -> AmountedAction -> Invert`

    Invert() inverts the selected elements for each given position.
    
    Parameters
    ----------
    int(1) : Sets the degree of inversion starting by 0 meaning no inversion
    """
    def __init__(self, *parameters):
        self._last_position_beats = Fraction(-1)
        super().__init__(*parameters)


    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        for single_element in scoped_elements:
            if isinstance(single_element, oe.Note):
                element_position: ra.Position = single_element % ra.Position()
                if element_position > self._last_position_beats:    # Only does a single inversion per position
                    self._last_position_beats = element_position % Fraction()
                    element_clip: oc.Clip = single_element.element_clip()
                    clip_shallow_copy = element_clip.empty_copy()
                    clip_shallow_copy._items = scoped_elements.copy()
                    clip_shallow_copy &= of.Equal(element_position)
                    # This edits the note pitch, it doesn't add new ones
                    self._apply_inversion(clip_shallow_copy._items)
        clip._sort_items()
        return super().act(clip, scoped_elements)


    def _apply_inversion(self, notes: list['oe.Note']) -> list['oe.Note']:
        # Where the inversions are done
        inversion: int = self._amount % len(notes)
        if inversion > 0:
            first_note = notes[inversion]
            not_first_note = True
            while not_first_note:   # Try to implement while inversion > 0 here
                not_first_note = False
                for single_note in notes:
                    if single_note._pitch < first_note._pitch:   # Critical operation
                        single_note << single_note % ou.Octave() + 1
                        if single_note % od.Pipe( int() ) < 128:
                            not_first_note = True # to result in another while loop
        # Final Octave adjustment
        octave_offset: ou.Octave = ou.Octave( self._amount // len(notes) )
        if octave_offset != 0:
            for single_note in notes:
                single_note += octave_offset
        return notes


class Sustain(Aggregated):
    """`Action -> Aggregated -> Sustain`

    `Sustain` extends the duration of all notes like if the sustain pedal was pressed all the time.
    It keeps retriggering the though, meaning, they are released only when they are retriggered.

    It works like sustain for with the total duration up to the last released note.

    Parameters
    ----------
    Any(None) : The `Operand` to be used as input.
    """
    @staticmethod
    def _sustain_notes(notes: list['oe.Note']) -> dict[int, list['oe.Note']]:
        global_finish = Fraction(0)
        sustained_channel_pitch_notes: dict[int, list[oe.Note]] = {} # channel_pitch based
        # Add the hanged notes and respective sustain duration
        for single_note in notes:
            note_finish: Fraction = single_note % ra.Finish() % Fraction()
            # Critical line setting the absolute finish
            global_finish = max(global_finish, note_finish)
            channel_0: int = single_note._channel_0
            pitch: int = single_note._pitch.get_absolute_pitch()
            channel_pitch: int = channel_0 << 7 | pitch # (4 bits, 7 bits)
            if channel_pitch in sustained_channel_pitch_notes:
                channel_pitch_notes: list[oe.Note] = sustained_channel_pitch_notes[channel_pitch]
                channel_pitch_notes[-1] << ra.Finish(single_note % ra.Start())
                channel_pitch_notes.append(single_note.copy())
            else:
                sustained_channel_pitch_notes[channel_pitch] = [single_note.copy()]
        # Extend all rotted notes to the global finish
        for channel_pitch_notes in sustained_channel_pitch_notes.values():
            channel_pitch_notes[-1] << ra.Finish(global_finish)
        return sustained_channel_pitch_notes


    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        scoped_notes: list[oe.Note] = [
            single_note for single_note in scoped_elements
            if isinstance(single_note, oe.Note)
        ]
        clip.delete(scoped_notes, True)
        sustained_notes: list['oe.Note'] = []
        sustained_channel_pitch_notes: dict[int, list[oe.Note]] = Sustain._sustain_notes(scoped_notes)
        for channel_pitch_notes in sustained_channel_pitch_notes.values():
            sustained_notes.extend(channel_pitch_notes)
        return clip.extend(sustained_notes)._sort_items()



class Arpeggiate(Aggregated):
    """`Action -> Aggregated -> Arpeggiate`

    `Arpeggiate` lets a group of simultaneously played notes to be played in sequence accordingly to the Arpeggio configuration.

    Parameters
    ----------
    Order(1), int : The notes changing order, with 1 being the "Up" order.
    Rate(Steps(1)), float : The Rate note value after which the next note is played following the set `Order`.
    Swing(0.5) : Sets the amount of time the note is effectively pressed relatively to its total duration.
    Chaos(SinX()) : For the `Order` 5, "Chaotic", it uses the set Chaotic `Operand`.
    """
    def __init__(self, *parameters):
        self._order: int = 1    # "Up" by default
        self._rate_beats: Fraction = og.settings._quantization  # Quantization is a Beats value already
        self._swing: Fraction = Fraction(1, 2)
        self._chaos: ch.Chaos = ch.SinX()
        self._chaotic_sequence: list[oe.Note] = []
        self._processed_element_ids: set[Element] = set()
        super().__init__(*parameters)


    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        new_scoped_elements: list[oe.Element] = []
        for single_element in scoped_elements:
            if isinstance(single_element, oe.Note) \
                and not any(id(single_element) == single_element_id for single_element_id in self._processed_element_ids):
                # The single_element and all on the same position will be replaced
                element_position: ra.Position = single_element % ra.Position()
                element_clip: oc.Clip = single_element.element_clip()
                clip_shallow_copy = element_clip.empty_copy()
                clip_shallow_copy._items = scoped_elements.copy()
                if clip_shallow_copy._items:
                    clip_shallow_copy &= of.Equal(element_position, of.ElementType(oe.Note))
                    notes = clip_shallow_copy._items    # Already without masked elements (framed)
                    # Remove elements from clip
                    element_clip.delete(notes, True)
                    self._processed_element_ids.update(id(single_note) for single_note in notes)
                    new_notes: list[oe.Element] = self._arpeggiate(notes)
                    # Add new elements to clip
                    element_clip.extend(new_notes)
                    new_scoped_elements.extend(new_notes)
        clip._sort_items()
        return super().act(clip, new_scoped_elements)


    def _shuffle_list(self, list: list) -> list:
        
        source_picks = [*range(len(list))]
        target_picks = []

        while len(source_picks) > 0:
            target_picks.append(source_picks.pop(self._chaos % int() % len(source_picks)))

        shuffled_list = []
        for pick in target_picks:
            shuffled_list.append(list[pick])

        return shuffled_list


    def _arpeggiate(self, notes: list['oe.Note']) -> list['oe.Note']:
        arpeggiated_notes: list['oe.Note'] = []
        if self._order > 0 and len(notes) > 0:

            note_start_position: ra.Position = notes[0] % od.Pipe( ra.Position() )
            pressed_notes: list[oe.Note] = [
                single_note for single_note in notes
                if single_note._position_beats + single_note._duration_beats > note_start_position
            ]
            if pressed_notes:
                time_signature: og.TimeSignature = pressed_notes[0]._get_time_signature()
                rate_length: ra.Length = ra.Length(time_signature, self._rate_beats)
                odd_length: ra.Length = rate_length * 2 * self._swing
                even_length: ra.Length = rate_length * 2 - odd_length
                note_index: int = 0
                while pressed_notes:
                    new_note: oe.Note = self._next_note(notes, note_index).copy()
                    new_note_finish: ra.Position = new_note.finish()
                    if new_note_finish > note_start_position: # Simply skip released notes
                        arpeggiated_notes.append(new_note)
                        new_note << note_start_position
                        new_length: ra.Length = odd_length
                        if note_index % 2:  # Even nth note
                            new_length = even_length
                        new_finish: ra.Position = note_start_position + new_length
                        if new_note_finish < new_finish:    # Don't change new note duration
                            note_end_position: ra.Position = new_note_finish
                        else:
                            new_note << new_length  # Sets smaller length
                            note_end_position: ra.Position = new_finish
                        note_start_position = note_end_position
                        # Filter out released notes
                        pressed_notes = [
                            single_note for single_note in pressed_notes
                            if single_note._position_beats + single_note._duration_beats > note_start_position
                        ]
                    note_index += 1
        return arpeggiated_notes


    def _next_note(self, notes: list['oe.Note'], index: int) -> 'oe.Note':
        """Returns a Note according to the arpeggio order."""
        size = len(notes)
        match ou.Direction.numberToName(self._order):
            case "Down":
                return notes[-(index % size) - 1]
            case "UpDown":
                index %= max(1, 2 * size - 2)
                return notes[index if index < size else 2 * size - 2 - index]
            case "DownUp":
                index %= max(1, 2 * size - 2)
                return notes[size - 1 - index if index < size else index - size + 1]
            case "Chaotic":
                if index % size == 0:
                    self._chaotic_sequence = self._shuffle_list(notes)
                return self._chaotic_sequence[index % size]
            case _:
                return notes[index % size]

    
    def __eq__(self, other: 'Arpeggiate') -> bool:
        if type(self) != type(other):
            return False
        if isinstance(other, Arpeggiate):
            return  self._order                 == other._order \
                and self._rate_beats            == other._rate_beats \
                and self._chaos                 == other._chaos
        if isinstance(other, od.Conditional):
            return other == self
        return super().__eq__(other)
    

    def __mod__(self, operand: o.T) -> o.T:
        from . import operand_chaos as ch
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Direction():        return operand._data << od.Pipe( self._order )
                    case ra.Rate():             return operand._data << od.Pipe( self._rate_beats )
                    case ra.Swing():            return operand._data << od.Pipe( self._swing )
                    case ch.Chaos():            return self._chaos
                    case int():                 return self._order
                    case float():               return float( self._rate_beats )
                    case Fraction():            return self._rate_beats
                    case _:                     return super().__mod__(operand)
            case ou.Direction():        return ou.Direction(self._order)
            case str():                 return ou.Direction(self._order) % str()
            case ra.Rate():             return ra.Rate( self._rate_beats )
            case ra.Swing():            return ra.Swing(self._swing)
            case ch.Chaos():            return self._chaos.copy()
            case int():                 return self._order
            case float():               return float( self._rate_beats )
            case Fraction():            return self._rate_beats
            case Arpeggiate():
                return operand.copy(self)
            case _:                     return super().__mod__(operand)


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["order"]            = o.serialize( self._order )
        serialization["parameters"]["rate"]             = o.serialize( self._rate_beats )
        serialization["parameters"]["swing"]            = o.serialize( self._swing )
        serialization["parameters"]["chaos"]            = o.serialize( self._chaos )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "order" in serialization["parameters"] and "rate" in serialization["parameters"] and
            "swing" in serialization["parameters"] and "chaos" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._order                 = o.deserialize( serialization["parameters"]["order"] )
            self._rate_beats            = o.deserialize( serialization["parameters"]["rate"] )
            self._swing                 = o.deserialize( serialization["parameters"]["swing"] )
            self._chaos                 = o.deserialize( serialization["parameters"]["chaos"] )
        return self
    

    def __lshift__(self, operand: any) -> Self:
        from . import operand_chaos as ch
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Arpeggiate():
                super().__lshift__(operand)
                self._order                 = operand._order
                self._rate_beats            = operand._rate_beats
                self._swing                 = operand._swing
                self._chaos                 = operand._chaos.copy()
            case od.Pipe():
                match operand._data:
                    case ou.Direction():            self._order = operand._data._unit
                    case ra.Rate():                 self._rate_beats = operand._data._rational
                    case ra.Swing():                self._swing = operand._data._rational
                    case ch.Chaos():                self._chaos = operand._data
                    case int():                     self._order = operand._data
                    case float():                   self._rate_beats = ra.Rate(operand._data)._rational
                    case Fraction():                self._rate_beats = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Direction():            self._order = operand._unit
            case str():                     self._order = ou.Direction(operand)._unit
            case ra.Rate():                 self._rate_beats = operand._rational
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ch.Chaos():                self._chaos << operand
            case int():                     self._order = operand
            case float():                   self._rate_beats = ra.Rate(operand)._rational
            case Fraction():                self._rate_beats = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self



class Retrigger(Aggregated):
    """`Action -> Aggregated -> Retrigger`

    A `Retrigger` repeats the `Element` accordingly to a given Rate.

    Parameters
    ----------
    Rate(Steps(1)), int, float : int for steps and float for note value.
    Swing(0.5) : Sets the amount of time the Element is effectively placed relatively to its total duration.
    """
    def __init__(self, *parameters):
        self._rate_beats: Fraction  = og.settings._quantization # Quantization is a Beats value already
        self._swing: Fraction       = Fraction(1, 2)
        super().__init__(*parameters)


    def act(self, clip: 'Clip', scoped_elements: list['Element']) -> 'Clip':
        retriggered_elements: list['oe.Element'] = []
        clip.delete(scoped_elements, True)
        for single_element in scoped_elements:
            retriggered_elements.extend(self._repeat_element(single_element))
        clip.extend(retriggered_elements)


    def _repeat_element(self, single_element: 'oe.Element') -> list['oe.Element']:
        repeated_elements: list[oe.Note] = []
        single_note_position: Fraction = single_element._position_beats
        single_note_finish: Fraction = single_note_position + single_element._duration_beats
        total_retriggers: int = int(single_element._duration_beats / self._rate_beats)
        self._swing = max(Fraction(0), self._swing, min(Fraction(1), self._swing))
        for repeat_i in range(total_retriggers + 1):
            new_element = single_element.copy()
            repeated_elements.append(new_element)
            if repeat_i % 2 == 0:
                new_element._duration_beats = self._rate_beats * 2 * self._swing
                new_element._position_beats = single_note_position + self._rate_beats * repeat_i
            else:
                new_element._duration_beats = self._rate_beats * 2 * (1 - self._swing)
                new_element._position_beats = single_note_position + self._rate_beats * (repeat_i + 1)
                new_element._position_beats -= new_element._duration_beats
            # Trim exceeding duration
            new_note_finish: Fraction = new_element._position_beats + new_element._duration_beats
            if new_note_finish >= single_note_finish:
                new_element._duration_beats -= new_note_finish - single_note_finish
                break
        return repeated_elements


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Rate():     return operand._data << od.Pipe(self._count)
                    case ra.Swing():        return operand._data << od.Pipe(self._swing)
                    case _:                 return super().__mod__(operand)
            case ra.Rate():        return ra.Rate() << od.Pipe(self._count)
            case ra.Swing():        return ra.Swing() << od.Pipe(self._swing)
            # Returns the SYMBOLIC value of each note
            case ra.Rate():
                return operand.copy(self._rate_beats)
            case ra.TimeValue():
                return operand.copy(ra.Rate(self._rate_beats))
            case float():           return self % ra.NoteValue() % float()
            case int():             return self % ra.Steps() % int()
            case _:                 return super().__mod__(operand)


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["rate"]     = o.serialize( self._rate_beats )
        serialization["parameters"]["swing"]    = o.serialize( self._swing )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "rate" in serialization["parameters"] and "swing" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._rate_beats        = o.deserialize( serialization["parameters"]["rate"] )
            self._swing             = o.deserialize( serialization["parameters"]["swing"] )
        return self


    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Retrigger():
                super().__lshift__(operand)
                self._rate_beats        = operand._rate_beats
                self._swing             = operand._swing
            case od.Pipe():
                match operand._data:
                    case ra.Rate():                 self._rate_beats = operand._data._rational
                    case ra.Swing():                self._swing = operand._data._rational
                    case _:                         super().__lshift__(operand)
            case ra.Rate():
                if operand > 0:
                    self._duration = operand._rational
            case ra.TimeValue():
                if operand > 0:
                    self << ra.Rate(operand)
            case float():
                if operand > 0:
                    self << ra.NoteValue(operand)
            case int():
                if operand > 0:
                    self << ra.Steps(operand)
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case _:
                super().__lshift__(operand)
        return self


