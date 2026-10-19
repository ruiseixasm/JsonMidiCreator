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
    def act(self, element: 'Element') -> Self:
        if isinstance(self._chained_operand, Action):
            return self._chained_operand.act(element)
        return self


    def act_new(self, clip: 'Clip', scoped_elements: list['Element']) -> Self:
        if isinstance(self._chained_operand, Action):
            return self._chained_operand.act_new(clip, scoped_elements)
        return self



class Delete(Action):
    """`Action -> Delete`

    Deletes all the unmasked items in the targeted `Container` or elements in it if a `Clip`.

    Args:
        None
    """
    def act(self, element: 'Element') -> Self:
        if element.is_owned() and not element.framed_out():
            owner_clip = element.element_clip()
            owner_clip.delete_item(element)
        return self


    def act_new(self, clip: 'Clip', scoped_elements: list['Element']) -> Self:
        clip.delete(scoped_elements, True)
        return super().act_new(clip, scoped_elements)



class Aggregated(Action):
    """`Action -> Aggregated`

    `Aggregated` means that multiple Elements are processed at once and not just one by one.
    """
    def reuse(self) -> Self:
        return self


    def process_finish(self, element: 'Element') -> Self:
        if element.is_owned():
            targeted_elements = element.scoped_elements()
            if targeted_elements and element is targeted_elements[-1]:
                element.element_clip()._sort_items()
                self.reuse()
        return self



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


    def __neg__(self):
        self._amount *= -1
        return self.reuse()


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
    
    def __str__(self):
        return f'{self._amount}'


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
        return self.reuse()


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
        return self.reuse()

    
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
        return self.reuse()

    
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
        return self.reuse()

    
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
        return self.reuse()



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

    def reuse(self) -> Self:
        self._last_position_beats = Fraction(-1)
        return self

    def act(self, element: 'Element') -> Self:
        if element.is_owned() and isinstance(element, oe.Note):
            element_position: ra.Position = element % ra.Position()
            if element_position > self._last_position_beats:    # Only does a single inversion per position
                self._last_position_beats = element_position % Fraction()
                element_clip: oc.Clip = element.element_clip()
                clip_shallow_copy = element_clip.shallow_copy()
                framed_elements = element.framed_elements()
                if framed_elements is not None:
                    clip_shallow_copy._items = framed_elements
                clip_shallow_copy &= of.Equal(element_position)
                notes = clip_shallow_copy._items    # Already without masked elements (framed)
                self._apply_inversion(notes)
        self.process_finish(element)
        return super().act(element)


    def act_new(self, clip: 'Clip', scoped_elements: list['Element']) -> Self:
        for single_element in scoped_elements:
            if isinstance(single_element, oe.Note):
                element_position: ra.Position = single_element % ra.Position()
                if element_position > self._last_position_beats:    # Only does a single inversion per position
                    self._last_position_beats = element_position % Fraction()
                    element_clip: oc.Clip = single_element.element_clip()
                    clip_shallow_copy = element_clip.shallow_copy()
                    framed_elements = single_element.framed_elements()
                    if framed_elements is not None:
                        clip_shallow_copy._items = framed_elements
                    clip_shallow_copy &= of.Equal(element_position)
                    # This edits the note pitch, it doesn't add new ones
                    self._apply_inversion(clip_shallow_copy._items)
        return super().act_new(clip, scoped_elements)


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


class Arpeggiate(Aggregated):
    """`Action -> Aggregated -> Arpeggiate`

    Represents an Effect with multiple configuration parameters associated to.

    Args:
        Effect() : The Effect to be applied to the elements on each `Position`.
    """
    def __init__(self, *parameters):
        self._order: int = 1    # "Up" by default
        self._duration_beats: Fraction = Fraction(1, 4) # duration in beats, NOT note value
        self._swing: Fraction = Fraction(1, 2)
        self._chaos: ch.Chaos = ch.SinX()
        self._chaotic_sequence: list[oe.Note] = []
        self._processed_element_ids: set[Element] = set()
        super().__init__(*parameters)


    def act(self, element: 'Element') -> Self:
        if element.is_owned():
            if not any(id(element) == single_element_id for single_element_id in self._processed_element_ids):
                element_position: ra.Position = element % ra.Position()
                element_clip: oc.Clip = element.element_clip()
                clip_shallow_copy = element_clip.shallow_copy()
                framed_elements = element.framed_elements()
                if framed_elements is not None:
                    clip_shallow_copy._items = framed_elements
                if clip_shallow_copy._items:
                    clip_shallow_copy &= of.Equal(element_position)
                    elements = clip_shallow_copy._items    # Already without masked elements (framed)
                    # Remove elements from clip
                    element_clip.delete(elements, True)
                    self._processed_element_ids.update(id(single_element) for single_element in elements)
                    new_elements: list[oe.Element] = self.arpeggiate(elements)
                    self._processed_element_ids.update(id(single_element) for single_element in new_elements)
                    # Add new elements to clip
                    element_clip.extend(new_elements)
        return self.process_finish(element)


    def act_new(self, clip: 'Clip', scoped_elements: list['Element']) -> Self:
        new_scoped_elements: list[oe.Element] = []
        for single_element in scoped_elements:
            if not any(id(single_element) == single_element_id for single_element_id in self._processed_element_ids):
                element_position: ra.Position = single_element % ra.Position()
                element_clip: oc.Clip = single_element.element_clip()
                clip_shallow_copy = element_clip.shallow_copy()
                framed_elements = single_element.framed_elements()
                if framed_elements is not None:
                    clip_shallow_copy._items = framed_elements
                if clip_shallow_copy._items:
                    clip_shallow_copy &= of.Equal(element_position)
                    elements = clip_shallow_copy._items    # Already without masked elements (framed)
                    # Remove elements from clip
                    element_clip.delete(elements, True)
                    self._processed_element_ids.update(id(single_element) for single_element in elements)
                    new_elements: list[oe.Element] = self.arpeggiate(elements)
                    self._processed_element_ids.update(id(single_element) for single_element in new_elements)
                    # Add new elements to clip
                    element_clip.extend(new_elements)
                    new_scoped_elements.extend(new_elements)
        return super().act_new(clip, new_scoped_elements)


    def reuse(self) -> Self:
        self._processed_element_ids = set()
        return self


    def _shuffle_list(self, list: list) -> list:
        
        source_picks = [*range(len(list))]
        target_picks = []

        while len(source_picks) > 0:
            target_picks.append(source_picks.pop(self._chaos % int() % len(source_picks)))

        shuffled_list = []
        for pick in target_picks:
            shuffled_list.append(list[pick])

        return shuffled_list


    def arpeggiate(self, notes: list['oe.Note']) -> list['oe.Note']:
        arpeggiated_notes: list['oe.Note'] = []
        if self._order > 0 and len(notes) > 0:

            time_signature: og.TimeSignature = notes[0]._get_time_signature()
            note_start_position: ra.Position = notes[0] % od.Pipe( ra.Position() )
            arpeggio_length: ra.Length = notes[0] % od.Pipe( ra.Length() )
            arpeggio_end_position: ra.Position = note_start_position + arpeggio_length % ra.Position()
            note_length: ra.Length = ra.Length(time_signature, self._duration_beats)
            odd_length: ra.Length = note_length * 2 * self._swing
            even_length: ra.Length = note_length * 2 - odd_length
            
            note_index: int = 0
            while note_start_position < arpeggio_end_position:
                new_note: oe.Note = self._next_note(notes, note_index).copy()
                arpeggiated_notes.append(new_note)
                new_note << note_start_position
                if note_index % 2 == 0:   # Odd note
                    new_note << odd_length
                else:
                    new_note << even_length
                note_end_position: ra.Position = note_start_position + new_note % od.Pipe( ra.Length() )
                if note_end_position > arpeggio_end_position:
                    length_deficit: ra.Length = arpeggio_length - arpeggio_end_position
                    new_note += length_deficit
                    break
                note_start_position = note_end_position
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
                and self._duration_beats        == other._duration_beats \
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
                    case ra.Duration():         return operand._data << od.Pipe( self._duration_beats )
                    case ra.Swing():            return operand._data << od.Pipe( self._swing )
                    case ch.Chaos():            return self._chaos
                    case int():                 return self._order
                    case float():               return float( self._duration_beats )
                    case Fraction():            return self._duration_beats
                    case _:                     return super().__mod__(operand)
            case ou.Direction():        return ou.Direction(self._order)
            case str():                 return ou.Direction(self._order) % str()
            case ra.Duration():         return ra.Duration( self._duration_beats )
            case ra.Swing():            return ra.Swing(self._swing)
            case ch.Chaos():            return self._chaos.copy()
            case int():                 return self._order
            case float():               return float( self._duration_beats )
            case Fraction():            return self._duration_beats
            case Arpeggiate():
                return operand.copy(self)
            case _:                     return super().__mod__(operand)


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["order"]            = o.serialize( self._order )
        serialization["parameters"]["duration_beats"]         = o.serialize( self._duration_beats )
        serialization["parameters"]["swing"]            = o.serialize( self._swing )
        serialization["parameters"]["chaos"]            = o.serialize( self._chaos )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "order" in serialization["parameters"] and "duration_beats" in serialization["parameters"] and
            "swing" in serialization["parameters"] and "chaos" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._order                 = o.deserialize( serialization["parameters"]["order"] )
            self._duration_beats        = o.deserialize( serialization["parameters"]["duration_beats"] )
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
                self._duration_beats        = operand._duration_beats
                self._swing                 = operand._swing
                self._chaos                 = operand._chaos.copy()
            case od.Pipe():
                match operand._data:
                    case ou.Direction():                self._order = operand._data._unit
                    case ra.Duration():             self._duration_beats = operand._data._rational
                    case ra.Swing():                self._swing = operand._data._rational
                    case ch.Chaos():                self._chaos = operand._data
                    case int():                     self._order = operand._data
                    case float():                   self._duration_beats = ra.Duration(operand._data)._rational
                    case Fraction():                self._duration_beats = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Direction():                self._order = operand._unit
            case str():                     self._order = ou.Direction(operand)._unit
            case ra.Duration():             self._duration_beats = operand._rational
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ch.Chaos():                self._chaos << operand
            case int():                     self._order = operand
            case float():                   self._duration_beats = ra.Duration(operand)._rational
            case Fraction():                self._duration_beats = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self



