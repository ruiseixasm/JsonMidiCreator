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
import re
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_data as od
import operand_frame as of
import operand_label as ol


class Rational(o.Operand):
    """`Rational`

    This is a type of Operand that has associated to a Fractional number (Rational).
    This class is intended to represent time based variables that are ratios like the typical 1/4 note value

    Parameters
    ----------
    Fraction(0), float, int : Sets its single parameter value.
    """
    _limit_denominator: int = 1_000_000 # default value of limit_denominator

    def check_denominator(self, rational: Fraction) -> Fraction:
        if self._limit_denominator > 0:
            rational = rational.limit_denominator(self._limit_denominator)
        return rational

    def __init__(self, *parameters):
        self._rational: Fraction = Fraction(0)
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract the Rational, because a Rational is an Fraction
        it should be used in conjugation with a float(). If used with an int() it
        will return the respective floored value as int().

        Examples
        --------
        >>> note_value = NoteValue(3/4)
        >>> note_value % float() >> Print()
        0.75
        >>> note_value % int() >> Print()
        0
        """
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case Fraction():        return self._rational           # returns a Fraction()
                    case float():           return float(self._rational)
                    case int():             return int(self._rational)
                    case of.Frame():        return self % od.Pipe( operand._data )
                    case str():             return str(self._rational)
                    case Rational() | ou.Unit():
                                            return operand.__class__() << od.Pipe( self._rational )
                    case _:                 return super().__mod__(operand)
            case Fraction():        return self._rational
            case float():           return float(self._rational)
            case int():             return int(self._rational)
            case of.Frame():        return self % operand
            case str():             return str(self._rational)
            case Rational() | ou.Unit():
                                    return operand.__class__() << od.Pipe( self._rational )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case int():
                return self._rational == other
            case float():
                return self._rational == self.check_denominator( Fraction(other) )
            case Fraction():
                return self._rational == self.check_denominator( other )
            case Rational():
                return self._rational == self.check_denominator( other._rational )
            case ou.Unit():
                return int( self._rational ) == other._unit
            case od.Conditional():
                return other == self
            case _:
                if other.__class__ == o.Operand:
                    return True
        return False
    
    def __lt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case int():
                return self._rational < other
            case float():
                return self._rational < self.check_denominator( Fraction(other) )
            case Fraction():
                return self._rational < self.check_denominator( other )
            case Rational():
                return self._rational < self.check_denominator( other._rational )
            case ou.Unit():
                return int( self._rational ) < other._unit
        return False
    
    def __gt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case int():
                return self._rational > other
            case float():
                return self._rational > self.check_denominator( Fraction(other) )
            case Fraction():
                return self._rational > self.check_denominator( other )
            case Rational():
                return self._rational > self.check_denominator( other._rational )
            case ou.Unit():
                return int( self._rational ) > other._unit
        return False
    
    def __str__(self):
        return f'{self._rational}'
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["fraction"] = str( self._rational )
        serialization["parameters"]["float"]    = float(self._rational) # For extra info
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Rational':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "fraction" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._rational = self.check_denominator( Fraction( serialization["parameters"]["fraction"] ) )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Rational():
                super().__lshift__(operand)
                if self._limit_denominator != operand._limit_denominator:
                    self._rational = self.check_denominator( operand._rational )
                else:
                    self._rational = operand._rational
            case od.Pipe():
                match operand._data:
                    case int():
                        self._rational = Fraction(operand._data)
                    case float():
                        self._rational = self.check_denominator( Fraction(operand._data) )
                    case Fraction():
                        self._rational = self.check_denominator( operand._data )
                    case Rational():
                        self._rational = self.check_denominator( operand._data._rational )
                    case ou.Unit():
                        self._rational = Fraction(operand._data._unit)
                    case str():
                        try:
                            self._rational = Fraction(operand._data)
                        except ValueError as e:
                            print(f"Error: {e}, '{operand._data}' is not a number!")
            case int():
                self._rational = Fraction(operand)
            case float():
                self._rational = self.check_denominator( Fraction(operand) )
            case Fraction():
                self._rational = self.check_denominator( operand )
            case ou.Unit():
                self._rational = Fraction(operand._unit)
            case str():
                self << od.Pipe( operand )
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __iadd__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self._tail_lshift(value)    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case int():
                self._rational += value
            case float() | Fraction():
                self._rational = self.check_denominator( Fraction(self._rational + value) )
            case Rational():
                self._rational = self.check_denominator( self._rational + value._rational )
            case ou.Unit():
                self._rational += value._unit
        return self
    
    def __isub__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self._tail_lshift(value)    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case int():
                self._rational -= value
            case float() | Fraction():
                self._rational = self.check_denominator( Fraction(self._rational - value) )
            case Rational():
                self._rational = self.check_denominator( self._rational - value._rational )
            case ou.Unit():
                self._rational -= value._unit
        return self
    
    def __imul__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self._tail_lshift(value)    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case int():
                self._rational *= value
            case float() | Fraction():
                self._rational = self.check_denominator( Fraction(self._rational * value) )
            case Rational():
                self._rational = self.check_denominator( self._rational * value._rational )
            case ou.Unit():
                self._rational *= value._unit
        return self
    
    def __itruediv__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self._tail_lshift(value)    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case int():
                if value != 0:
                    self._rational /= value
            case float() | Fraction():
                if value != 0:
                    self._rational = self.check_denominator( Fraction(self._rational / value) )
            case Rational():
                if value._rational != 0:
                    self._rational = self.check_denominator( self._rational / value._rational )
            case ou.Unit():
                if value._unit != 0:
                    self._rational /= value._unit
        return self

class HiPrecision(Rational):
    """`Rational -> HiPrecision`

    HiPrecision `Rational`s have no limit on the denominator, so, they represent the highest
    `Fraction` precision than the usual 1_000_000.

    Parameters
    ----------
    Fraction(0) : Like the typical `Rational` but with high precision instead.
    """
    _limit_denominator: int = 0 # overrides default limit_denominator

class Index(HiPrecision):
    """`Rational -> HiPrecision -> Index`"""
    pass

class Split(HiPrecision):
    """`Rational -> HiPrecision -> Split`"""
    pass

class Width(HiPrecision):
    """`Rational -> HiPrecision -> Width`"""
    pass

class Height(HiPrecision):
    """`Rational -> HiPrecision -> Height`"""
    pass

class dX(HiPrecision):
    """`Rational -> HiPrecision -> dX`"""
    pass

class dY(HiPrecision):
    """`Rational -> HiPrecision -> dY`"""
    pass

class dZ(HiPrecision):
    """`Rational -> HiPrecision -> dZ`"""
    pass

class X0(HiPrecision):
    """`Rational -> HiPrecision -> X0`"""
    pass

class Xn(HiPrecision):
    """`Rational -> HiPrecision -> Xn`"""
    pass

class Y0(HiPrecision):
    """`Rational -> HiPrecision -> Y0`"""
    pass

class Yn(HiPrecision):
    """`Rational -> HiPrecision -> Yn`"""
    pass

class Z0(HiPrecision):
    """`Rational -> HiPrecision -> Z0`"""
    pass

class Zn(HiPrecision):
    """`Rational -> HiPrecision -> Zn`"""
    pass

class Lambda(HiPrecision):
    """`Rational -> HiPrecision -> Lambda`"""
    pass

class Negative(Rational):
    """`Rational -> Negative`"""
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case Fraction():        return self._rational * -1
            case float():           return float(self._rational * -1)
            case int():             return int(self._rational * -1)
            case of.Frame():        return self % operand
            case str():             return str(self._rational * -1)
            case Rational() | ou.Unit():
                                    return operand.__class__() << od.Pipe( self._rational )
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Negative():
                super().__lshift__(operand)
                self._rational = operand._rational
            case int() | float() | Fraction() | Rational() | ou.Unit():
                super().__lshift__(operand)
                self._rational *= -1
            case str():
                try:
                    self._rational = Fraction(operand) * -1
                except ValueError as e:
                    print(f"Error: {e}, '{operand}' is not a number!")
            case _:
                super().__lshift__(operand)
        return self

class Probability(Rational):
    """`Rational -> Probability`"""
    pass


class Tempo(Rational):
    """`Rational -> Tempo`

    Tempo() represents the Staff Beats per Minute (BPM). The default is 120 BPM.

    Parameters
    ----------
    Fraction(120) : The playing tempo with the default as 120 BPM (Beats Per Minute).
    
    Examples
    --------
    Gets the Staff Steps per Measure:
    >>> staff = Staff(Tempo(110))
    >>> staff % Tempo() % Fraction() >> Print()
    110
    """
    def __init__(self, *parameters):
        super().__init__(120, *parameters)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                # r"\W(.)\1\W" vs "\\W(.)\\1\\W"
                tempo = re.findall(r"\d+(?:\.\d+)?", operand)
                if len(tempo) > 0:
                    self << float(tempo[0])
            case _: super().__lshift__(operand)
        # Makes sure it's positive
        self._rational = max(Fraction(1), self._rational)
        return self

    def __iadd__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Tempo':
        super().__iadd__(value)
        # Makes sure it's positive
        self._rational = max(Fraction(1), self._rational)
        return self
    
    def __isub__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Tempo':
        super().__isub__(value)
        # Makes sure it's positive
        self._rational = max(Fraction(1), self._rational)
        return self
    
    def __imul__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Tempo':
        super().__imul__(value)
        # Makes sure it's positive
        self._rational = max(Fraction(1), self._rational)
        return self
    
    def __itruediv__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Tempo':
        super().__itruediv__(value)
        # Makes sure it's positive
        self._rational = max(Fraction(1), self._rational)
        return self


class StaffParameter(Rational):
    """`Rational -> StaffParameter`"""
    pass

class TimeSignatureParameter(StaffParameter):
    """`Rational -> StaffParameter -> TimeSignatureParameter`"""
    pass

class BeatsPerMeasure(TimeSignatureParameter):
    """`Rational -> StaffParameter -> TimeSignatureParameter -> BeatsPerMeasure`

    BeatsPerMeasure() sets the top value of a time signature, in a 3/4 time signature 3 are the Beats per Measure.
    The default is 4, 4 Beats per Measure.

    Parameters
    ----------
    Fraction(4) : The last passed argument is the one being considered.
    
    Examples
    --------
    Sets the TimeSignature as 3 Beats per Measure:
    >>> time_signature = TimeSignature()
    >>> time_signature << BeatsPerMeasure(3)

    Default BeatsPerMeasure (4):
    >>> beats_per_measure = BeatsPerMeasure()
    """
    def __init__(self, *parameters):
        super().__init__(4, *parameters)

class BeatNoteValue(TimeSignatureParameter):
    """`Rational -> StaffParameter -> TimeSignatureParameter -> BeatNoteValue`

    BeatNoteValue() represents the Note Value for the Beat, in a 3/4 time signature 1/4 is the Beats Note Value.
    The default is 1/4, 1/4 NoteValue for each Beat.

    Parameters
    ----------
    Fraction(1/4) : The last passed argument is the one being considered. If no parameters are provided,
    
    Examples
    --------
    Sets the TimeSignature as 1/2 NoteValue per Beat:
    >>> time_signature = TimeSignature()
    >>> time_signature << BeatNoteValue(2)

    Default BeatNoteValue (1/4):
    >>> notes_per_beat = BeatNoteValue()
    """
    def __init__(self, *parameters):
        super().__init__(1/4, *parameters)

class NotesPerMeasure(TimeSignatureParameter):
    """`Rational -> StaffParameter -> TimeSignatureParameter -> NotesPerMeasure`

    NotesPerMeasure() represents the Note Value for a single Measure, in a 3/4 time signature 3/4 is the Measure Note Value.
    The default is 1, 1 NoteValue for each Measure. This is just an output parameter and not a setting one.

    Parameters
    ----------
    Fraction(1) : The value of the `Note` for a `Measure`.
    
    Examples
    --------
    Gets the TimeSignature NoteValue per Measure:
    >>> time_signature = TimeSignature(3, 4)
    >>> notes_per_measure = time_signature % NotesPerMeasure()
    >>> notes_per_measure % Fraction() >> Print()
    3/4

    Default NotesPerMeasure (1):
    >>> notes_per_measure = NotesPerMeasure()
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

class StepsPerMeasure(StaffParameter):
    """`Rational -> StaffParameter -> StepsPerMeasure`

    StepsPerMeasure() represents the Note Value for a single Measure, in a 3/4 time signature with 
    a Quantization of 1/16 you get 12 Steps per each Measure.
    The default is 16, 16 Steps for each Measure. This concerns Staff objects Quantization.

    Parameters
    ----------
    Fraction(16) : The amount of `Steps` in a `Measure`.
    
    Examples
    --------
    Gets the Staff Steps per Measure:
    >>> staff = Staff()
    >>> staff << TimeSignature(3, 4)
    >>> steps_per_measure = staff % StepsPerMeasure()
    >>> steps_per_measure % Fraction() >> Print()
    12

    Default StepsPerMeasure (16):
    >>> staff << TimeSignature(4, 4)
    >>> steps_per_measure = staff % StepsPerMeasure()
    >>> steps_per_measure % Fraction() >> Print()
    16
    """
    def __init__(self, *parameters):
        super().__init__(16, *parameters)

class StepsPerNote(StaffParameter):
    """`Rational -> StaffParameter -> StepsPerNote`

    StepsPerNote() represents the inversion of the Quantization, for a Quantization of 1/16 
    you will get 16 Notes per Step.
    The default is 16, 16 Steps for each Note. This concerns Staff objects Quantization.

    Parameters
    ----------
    Fraction(16) : The amount of `Steps` per each `Note`.
    
    Examples
    --------
    Gets the Staff Steps per Measure:
    >>> staff = Staff()
    >>> staff << TimeSignature(3, 4)
    >>> steps_per_note = staff % StepsPerNote()
    >>> steps_per_note % Fraction() >> Print()
    16

    Gets the Staff Quantization:
    >>> staff << StepsPerNote(32)
    >>> staff % Quantization() % Fraction() >> Print()
    1/32
    """
    def __init__(self, *parameters):
        super().__init__(16, *parameters)


class Minutes(Rational):
    """`Rational -> Minutes`"""
    pass


if TYPE_CHECKING:
    from operand_generic import Staff

class Convertible(Rational):
    def __init__(self, *parameters):
        import operand_generic as og
        # By default Time values have no Staff reference,
        # so, they aren't transformed, just converted !!
        self._staff_reference: og.Staff = None
        super().__init__(*parameters)

    # By default considers beats as the self_time, meaning, no conversion is done to the values
    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        return self_time

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        return beats

    def _get_beats(self, other_staff: 'Staff' = None) -> Fraction:
        return self._convert_to_beats(self._rational, other_staff)

    def _set_with_beats(self, beats: Fraction) -> Self:
        self._rational = self._convert_from_beats(beats)
        return self

    def _get_self_time(self) -> Fraction:
        return self._convert_from_beats(self._rational)


    def _set_staff_reference(self, staff_reference: 'Staff' = None) -> Self:
        import operand_generic as og
        if isinstance(staff_reference, og.Staff):
            self._staff_reference = staff_reference
        return self

    def _reset_staff_reference(self) -> Self:
        self._staff_reference = None
        return self

    def _get_staff(self, other_staff: 'Staff' = None) -> 'Staff':
        import operand_generic as og
        if self._staff_reference is None:
            if isinstance(other_staff, og.Staff):
                return other_staff
            return og.settings._staff
        return self._staff_reference


    # Position round type: [...)
    def roundMeasures(self) -> Self:
        measures: Measures = self % Measures()
        measures << measures % int()
        self << measures
        return self # NO copy !

    # Position round type: [...)
    def roundBeats(self) -> Self:
        beats: Beats = self % Beats()
        beats << beats % int()
        self << beats
        return self # NO copy !
    
    # Position round type: [...)
    def roundSteps(self) -> Self:
        steps: Steps = self % Steps()
        steps << steps % int()
        self << steps
        return self # NO copy !


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case Convertible():
                self_beats: Fraction = self._get_beats(operand._staff_reference)
                return operand.copy(self._staff_reference)._set_with_beats(self_beats)
            # Fraction sets the value directly
            case Fraction():            return self._rational
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case TimeUnit() | int() | float():
                return self % other == other
            case Convertible():
                return self._get_beats(other._staff_reference) == other._get_beats(self._staff_reference)
            case _:
                return super().__eq__(other)
        return False

    def __lt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case TimeUnit() | int() | float():
                return self % other < other
            case Convertible():
                return self._get_beats(other._staff_reference) < other._get_beats(self._staff_reference)
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case TimeUnit() | int() | float():
                return self % other > other
            case Convertible():
                return self._get_beats(other._staff_reference) > other._get_beats(self._staff_reference)
            case _:
                return super().__gt__(other)
        return False


    def getPlaylist(self) -> list[dict]:
        beats: Fraction = self % Beats() % Fraction()
        return self._get_staff().getPlaylist(beats)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_generic as og
        import operand_element as oe
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                # Needs to go very easy to avoid infinite Recursion
                operand_beats: Beats = operand._get_beats(self._staff_reference)
                self._set_with_beats(operand_beats)
            case oe.Element() | oc.Composition():
                if self._staff_reference is None:
                    self._staff_reference = operand._get_staff()
            case og.Staff():
                if self._staff_reference is None:
                    self._staff_reference = operand
            case Fraction():
                self._rational = operand
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                self += operand % self % Fraction()
            case Fraction():
                self._rational += operand
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                self -= operand % self % Fraction()
            case Fraction():
                self._rational -= operand
            case _:
                super().__isub__(operand)
        return self
    
    # THE DEFAULT INTERPRETATION OF MEASUREMENTS IS IN MEASURES (RELEVANT FOR MULTIPLICATION AND DIVISION)
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                self *= operand % self % Fraction()
            case Fraction():
                self._rational *= operand
            case _:
                super().__imul__(operand)
        return self
    
    # THE DEFAULT INTERPRETATION OF MEASUREMENTS IS IN MEASURES (RELEVANT FOR MULTIPLICATION AND DIVISION)
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                self /= operand % self % Fraction()
            case Fraction():
                if operand != 0:
                    self._rational /= operand
            case _:
                super().__itruediv__(operand)
        return self


class Measurement(Convertible):
    """`Rational -> Convertible -> Measurement`

    Measurement() represents either a Length or a Position.
    """

    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        time_staff: Staff = self._get_staff(other_staff)
        beats_per_measure: int = time_staff._time_signature._top
        return self_time * beats_per_measure

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_staff: Staff = self._get_staff()
        beats_per_measure: int = time_staff._time_signature._top
        return beats / beats_per_measure

    def _get_beats(self, other_staff: 'Staff' = None) -> Fraction:
        return self._rational   # Kept as beats already

    def _set_with_beats(self, beats: Fraction) -> Self:
        self._rational = beats  # Kept as beats already
        return self

    
    def measurement(self, beats: float = None) -> Self:
        return self << od.Pipe( beats )


    # Measurement round type: [...)
    def roundMeasures(self) -> Self:
        self_measures: Measures = self % Measures()
        return self.copy(self_measures.roundMeasures())

    # Measurement round type: [...)
    def roundBeats(self) -> Self:
        self_beats: Beats = self % Beats()
        return self.copy(self_beats.roundBeats())
    
    # Measurement round type: [...)
    def roundSteps(self) -> Self:
        self_steps: Steps = self % Steps()
        return self.copy(self_steps.roundSteps())


    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Time,
        those Parameters are the respective time unit, like Measure and NoteValue,
        where Length and Length have a Measure while a Duration has a NoteValue.

        Examples
        --------
        >>> position = Length(4.5)
        >>> position % Measure() % float() >> Print()
        4.0
        >>> position % Beat() % float() >> Print()
        2.0
        >>> position % Step() % float() >> Print()
        8.0
        """
        match operand:
            case int():                 return self % Measure() % int()     # Measure, NOT Measures
            case float():               return self % Measures() % float()
            case _:                     return super().__mod__(operand)

    def __str__(self):
        return f'Span Beats = {self._rational}'

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                match operand:
                    case Measure():
                        actual_measure: Measure = self % Measure()
                        offset_measure: Measure = operand - actual_measure
                        self += Measures(offset_measure)
                        # self_beats: Beats = self % Beats()
                        # measure_beats: Beats = self_beats - self_beats.copy().roundMeasures()
                        # operand_beats: Beats = operand % Beats(self._staff_reference)
                        # operand_beats.roundMeasures()
                        # self._rational = (operand_beats + measure_beats) % Fraction()

                    # # CAN'T USE THIS YET, FAILS AT COPYING BEAT AS IS !!
                    # case Beat():
                    #     actual_beat: Beat = self % Beat()
                    #     offset_beat: Beat = operand - actual_beat
                    #     self += Beats(offset_beat)
                    case Beat() | Step():
                        self_beats: Beats = self % Beats()
                        self_beats.roundMeasures()
                        self_beats += operand
                        self._rational = self_beats._rational
                    case Measurement() | Beats():
                        self._rational = operand._rational  # Both are in beats
                    case Convertible():
                        self._rational = operand % Beats(self._staff_reference) % Fraction()
                    case _:
                        super().__lshift__(operand)
            case int() | float():
                self << Measures(operand)
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Measurement() | Beats() | Beat():
                self._rational += operand._rational  # Both are in beats
            case Convertible():  # Implicit Measurement conversion
                self._rational += operand % Beats(self._staff_reference) % Fraction()
            case int() | float():
                self += Measures(operand)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Measurement() | Beats() | Beat():
                self._rational -= operand._rational  # Both are in beats
            case Convertible():  # Implicit Measurement conversion
                self._rational -= operand % Beats(self._staff_reference) % Fraction()
            case int() | float():
                self -= Measures(operand)
            case _:
                super().__isub__(operand)
        return self
    
    # THE DEFAULT INTERPRETATION OF MEASUREMENTS IS IN MEASURES (RELEVANT FOR MULTIPLICATION AND DIVISION)
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():  # Implicit Measurement conversion
                self_measures: Measures = self % Measures()
                operand_measures: Measures = operand % Measures(self._staff_reference)
                self << self_measures * operand_measures
            case int() | float():
                self *= Measures(operand)  # Default variable is Measures
            case _:
                super().__imul__(operand)
        return self
    
    # THE DEFAULT INTERPRETATION OF MEASUREMENTS IS IN MEASURES (RELEVANT FOR MULTIPLICATION AND DIVISION)
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():  # Implicit Measurement conversion
                self_measures: Measures = self % Measures()
                operand_measures: Measures = operand % Measures(self._staff_reference)
                if operand_measures != Measures(0):
                    self << self_measures / operand_measures
            case int() | float():
                if operand != 0:
                    self /= Measures(operand)  # Default variable is Measures
            case _:
                super().__itruediv__(operand)
        return self

class Position(Measurement):
    """`Rational -> Convertible -> Measurement -> Position`

    Position() is a Parameter applicable to `Element` and `Clip` objects. The input and output
    is given in `Measures` and their `TimeUnit` returns are rounded up to the SAME one.
    Internally though, the values are in `Beats` and can be directly accessed with the `//` operator.

    Parameters
    ----------
    Fraction(0) : The position on the `Staff` measured in `Measures`.
    
    Examples
    --------
    Gets the Note default Position from 1/4 NoteValue:
    >>> note = Note()
    >>> note % Position() % float() >> Print()
    0.25
    >>> note % Position() % Beats() % float() >> Print()
    1.0
    """
    def position(self, beats: float = None) -> Self:
        return self << od.Pipe( beats )

    # # Position round type: [...) + 1
    # def roundMeasures(self) -> Self:
    #     rounded_position: Position = super().roundMeasures()
    #     return rounded_position.__iadd__(Measure(1))

    # # Position round type: [...) + 1
    # def roundBeats(self) -> Self:
    #     rounded_position: Position = super().roundBeats()
    #     return rounded_position.__iadd__(Beat(1))
    
    # # Position round type: [...) + 1
    # def roundSteps(self) -> Self:
    #     rounded_position: Position = super().roundSteps()
    #     return rounded_position.__iadd__(Step(1))


class Length(Measurement):
    """`Rational -> Convertible -> Measurement -> Length`

    Length() is a Parameter applicable to `Element` and `Clip` objects. The input and output
    is given in `Measures` and their `TimeUnit` returns are rounded up to the NEXT one.
    Internally though, the values are in `Beats` and can be directly accessed with the `//` operator.

    Parameters
    ----------
    Fraction(0) : Represents the duration along the `Staff` in `Measures`.
    
    Examples
    --------
    Gets the Note default Length from 1/4 NoteValue:
    >>> note = Note()
    >>> note % Length() % float() >> Print()
    0.25
    >>> note % Length() % Beats() % float() >> Print()
    1.0
    """
    def length(self, beats: float = None) -> Self:
        return self << od.Pipe( beats )

    # Measurement/Length round type: (...]
    def roundMeasures(self) -> Self:
        rounded_length: Length = super().roundMeasures()
        if rounded_length == self:
            return rounded_length
        return rounded_length.__iadd__(Measure(1))

    # Measurement/Length round type: (...]
    def roundBeats(self) -> Self:
        rounded_length: Length = super().roundBeats()
        if rounded_length == self:
            return rounded_length
        return rounded_length.__iadd__(Beat(1))
    
    # Measurement/Length round type: (...]
    def roundSteps(self) -> Self:
        rounded_length: Length = super().roundSteps()
        if rounded_length == self:
            return rounded_length
        return rounded_length.__iadd__(Step(1))


class Duration(Measurement):
    """`Rational -> Convertible -> Measurement -> Duration`

    Duration() represents the Note Value duration of a `Note`, a `Duration` typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    Fraction(0) : Duration as 1, 1/2, 1/4, 1/8, 1/16, 1/32.
    """
    
    # Measurement/Duration round type: (...]
    def roundMeasures(self) -> Self:
        rounded_duration: Duration = super().roundMeasures()
        if rounded_duration == self:
            return rounded_duration
        return rounded_duration.__iadd__(Measure(1))

    # Measurement/Duration round type: (...]
    def roundBeats(self) -> Self:
        rounded_duration: Duration = super().roundBeats()
        if rounded_duration == self:
            return rounded_duration
        return rounded_duration.__iadd__(Beat(1))
    
    # Measurement/Duration round type: (...]
    def roundSteps(self) -> Self:
        rounded_duration: Duration = super().roundSteps()
        if rounded_duration == self:
            return rounded_duration
        return rounded_duration.__iadd__(Step(1))


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case float() | int():
                return self % NoteValue() % operand
            case _:
                return super().__mod__(operand)

    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        time_staff: Staff = self._get_staff(other_staff)
        beats_per_note: int = time_staff._time_signature._bottom
        return self_time * beats_per_note

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_staff: Staff = self._get_staff()
        beats_per_note: int = time_staff._time_signature._bottom
        return beats / beats_per_note


    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | float():
                self << NoteValue(operand)
            case str():
                time_division: str = operand.strip().upper()
                match time_division:
                    case "1/1" | "1":       super().__lshift__(1)
                    case "1/2":             super().__lshift__(1/2)
                    case "1/4":             super().__lshift__(1/4)
                    case "1/6" | "1/4T":    super().__lshift__(1/6)
                    case "1/8":             super().__lshift__(1/8)
                    case "1/12" | "1/8T":   super().__lshift__(1/12)
                    case "1/16":            super().__lshift__(1/16)
                    case "1/24" | "1/16T":  super().__lshift__(1/24)
                    case "1/32":            super().__lshift__(1/32)
                    case "1/48" | "1/32T":  super().__lshift__(1/48)
                    case "1/64":            super().__lshift__(1/64)
                    case "1/96" | "1/64T":  super().__lshift__(1/96)
                    case _:                 super().__lshift__(operand)
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                self_notevalue: NoteValue = self % NoteValue()
                operand_notevalue: NoteValue = operand % NoteValue()
                self << self_notevalue + operand_notevalue
            case int() | float():
                self += NoteValue(operand)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                self_notevalue: NoteValue = self % NoteValue()
                operand_notevalue: NoteValue = operand % NoteValue()
                self << self_notevalue - operand_notevalue
            case int() | float():
                self -= NoteValue(operand)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                self_notevalue: NoteValue = self % NoteValue()
                operand_notevalue: NoteValue = operand % NoteValue()
                self << self_notevalue * operand_notevalue
            case int() | float():
                self *= NoteValue(operand)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                self_notevalue: NoteValue = self % NoteValue()
                operand_notevalue: NoteValue = operand % NoteValue()
                if operand_notevalue != NoteValue(0):
                    self << self_notevalue / operand_notevalue
            case int() | float():
                self /= NoteValue(operand)
            case _:
                super().__itruediv__(operand)
        return self


class TimeValue(Convertible):  # Works as Absolute Beats
    """`Rational -> Convertible -> TimeValue`

    TimeValue() represents any Time variables like `Measure`, `Beat`, `Duration` and `Step`.
    
    Parameters
    ----------
    Fraction(0) : The default value is 0.
    """
    def _get_self_time(self) -> Fraction:
        return self._rational


class Measures(TimeValue):
    """`Rational -> Convertible -> TimeValue -> Measures`

    Measures() represents the fundamental unitary staff time Length, also known as Bar.
    
    Parameters
    ----------
    Fraction(0) : Proportional value to a `Measure` on the `Staff`.
    """
    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        time_staff: Staff = self._get_staff(other_staff)
        beats_per_measure: int = time_staff._time_signature._top
        return self_time * beats_per_measure

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_staff: Staff = self._get_staff()
        beats_per_measure: int = time_staff._time_signature._top
        return beats / beats_per_measure

    # Position round type: [...)
    def roundMeasures(self) -> Self:
        self << int(self._rational)
        return self # NO copy !


    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> 'Measures':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Measures():
                self._rational += operand._rational
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Measures':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Measures():
                self._rational -= operand._rational
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Measures':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Measures():
                self._rational *= operand._rational
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Measures':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Measures():
                if operand._rational != 0:
                    self._rational /= operand._rational
            case _:
                super().__itruediv__(operand)
        return self


class Beats(TimeValue):
    """`Rational -> Convertible -> TimeValue -> Beats`

    Beats() represents the staff Time Length in `Beats` on which the `Tempo` is based on (BPM).
    
    Parameters
    ----------
    Fraction(0) : Proportional value to a `Beat` on the `Staff`.
    """

    # Position round type: [...)
    def roundBeats(self) -> Self:
        self << int(self._rational)
        return self # NO copy !
    
    
    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Beats():
                self._rational += operand._rational
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Beats():
                self._rational -= operand._rational
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Beats():
                self._rational *= operand._rational
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Beats():
                if operand._rational != 0:
                    self._rational /= operand._rational
            case _:
                super().__itruediv__(operand)
        return self


class Steps(TimeValue):
    """`Rational -> Convertible -> TimeValue -> Steps`

    A Step() represents the Length given by the `Quantization`, normally 1/16 Note Value.
    
    Parameters
    ----------
    Fraction(0) : Steps as 1, 2, 4, 8...
    """
    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        import operand_generic as og
        notes_per_step: Fraction = og.settings._quantization
        time_staff: Staff = self._get_staff(other_staff)
        beats_per_note: int = time_staff._time_signature._bottom
        beats_per_step: Fraction = beats_per_note * notes_per_step
        return self_time * beats_per_step

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        import operand_generic as og
        notes_per_step: Fraction = og.settings._quantization
        time_staff: Staff = self._get_staff()
        beats_per_note: int = time_staff._time_signature._bottom
        beats_per_step: Fraction = beats_per_note * notes_per_step
        return beats / beats_per_step

    # Position round type: [...)
    def roundSteps(self) -> Self:
        self << int(self._rational)
        return self # NO copy !


    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Steps():
                self._rational += operand._rational
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Steps():
                self._rational -= operand._rational
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Steps():
                self._rational *= operand._rational
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Steps():
                if operand._rational != 0:
                    self._rational /= operand._rational
            case _:
                super().__itruediv__(operand)
        return self


class TimeUnit(Convertible):
    """`Rational -> Convertible -> TimeUnit`
    """
    def __init__(self, *parameters):
        import operand_generic as og
        # By default Time values have no Staff reference,
        # so, they aren't transformed, just converted !!
        self._staff_reference: og.Staff = None
        super().__init__(*parameters)

    def _get_self_time(self) -> Fraction:
        return Fraction( int(self._rational) )
    

    def __eq__(self, other: any) -> bool:
        import operand_rational as ra
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Convertible():
                return self._get_beats(other._staff_reference) \
                    == other._get_beats(self._staff_reference)
            case _:
                return super().__eq__(other)
        return False

    def __lt__(self, other: any) -> bool:
        import operand_rational as ra
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Convertible():
                return self._get_beats(other._staff_reference) \
                    < other._get_beats(self._staff_reference)
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        import operand_rational as ra
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Convertible():
                return self._get_beats(other._staff_reference) \
                    > other._get_beats(self._staff_reference)
            case _:
                return super().__gt__(other)
        return False


    if TYPE_CHECKING:
        from operand_rational import Convertible, Position, Length, Duration, Measures, Beats, Steps, Minutes



    def getPlaylist(self) -> list[dict]:
        return self._get_staff().getPlaylist(self)


class Measure(TimeUnit):
    """`Rational -> Convertible -> TimeUnit -> Measure`

    A Measure() represents the basic unit of a Staff division.

    Parameters
    ----------
    int(0) : Measure is similar to `Measures` but as integer only.
    
    Examples
    --------
    Creating a Measure with a single value (it will be rounded to 1):
    >>> measure = Measure(1.5)
    
    Creating a Measure with multiple values (the last will determine the amount of Measures):
    >>> measure = Measure(1, 0.5, Fraction(1, 4))

    Default Measure (0):
    >>> measure = Measure()
    """
    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        time_staff: Staff = self._get_staff(other_staff)
        beats_per_measure: int = time_staff._time_signature._top
        self_time: Fraction = self._get_self_time()
        return self_time * beats_per_measure

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_staff: Staff = self._get_staff()
        beats_per_measure: int = time_staff._time_signature._top
        relative_measure: int = int(beats / beats_per_measure)
        return Fraction( relative_measure )


    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> 'Measure':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__iadd__( operand % Measure(self._staff_reference) % Fraction() )
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Measure':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__isub__( operand % Measure(self._staff_reference) % Fraction() )
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Measure':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__imul__( operand % Measure(self._staff_reference) % Fraction() )
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Measure':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__itruediv__( operand % Measure(self._staff_reference) % Fraction() )
            case _:
                super().__itruediv__(operand)
        return self


class Beat(TimeUnit):
    """`Rational -> Convertible -> TimeUnit -> Beat`

    A Beat() represents the basic unit of a TimeSignature in relation to Measures (Ex 4 per Measure),
    and is set as an integer without decimal places.
    Its return from Length and Position objects represents their rounded value accordingly.

    Parameters
    ----------
    int(0) : The beat as an integer even when a float is given.
    
    Examples
    --------
    Creating a Beat with a single value:
    >>> beat = Beat(1.5)
    
    Creating a Beat with multiple values (the last will determine the amount of Beats):
    >>> beat = Beat(1, 0.5, Fraction(1, 4))

    Default Beat (0):
    >>> beat = Beat()
    """
    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        self_time: Fraction = self._get_self_time()
        return self_time

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_staff: Staff = self._get_staff()
        absolute_beat: int = int(beats)
        beats_per_measure: int = time_staff._time_signature._top
        relative_beat: int = absolute_beat % beats_per_measure
        return Fraction( relative_beat )


    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> 'Beat':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__iadd__( operand % Beat(self._staff_reference) % Fraction() )
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Beat':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__isub__( operand % Beat(self._staff_reference) % Fraction() )
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Beat':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__imul__( operand % Beat(self._staff_reference) % Fraction() )
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Beat':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__itruediv__( operand % Beat(self._staff_reference) % Fraction() )
            case _:
                super().__itruediv__(operand)
        return self


class Step(TimeUnit):
    """`Rational -> Convertible -> TimeUnit -> Step`

    A Step() represents an unit of Quantization (Ex 1/16) as an integer without decimal places.
    Its return from Length and Position objects represents their rounded value accordingly.

    Parameters
    ----------
    int(0) : The step as an integer even when a float is given, aka, quantized step.
    
    Examples
    --------
    Creating a Step with a single value:
    >>> step = Step(1.5)
    
    Creating a Step with multiple values (the last will determine the amount of Steps):
    >>> step = Step(1, 0.5, Fraction(1, 4))

    Default Step (0):
    >>> step = Step()
    """
    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        import operand_generic as og
        notes_per_step: Fraction = og.settings._quantization
        time_staff: Staff = self._get_staff(other_staff)
        beats_per_note: int = time_staff._time_signature._bottom
        beats_per_step: Fraction = beats_per_note * notes_per_step
        self_time: Fraction = self._get_self_time()
        return self_time * beats_per_step

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        import operand_generic as og
        notes_per_step: Fraction = og.settings._quantization
        time_staff: Staff = self._get_staff()
        beats_per_note: int = time_staff._time_signature._bottom
        beats_per_step: Fraction = beats_per_note * notes_per_step
        absolute_step: int = int(beats / beats_per_step)

        beats_per_measure: int = time_staff._time_signature._top
        steps_per_measure: int = int(beats_per_measure / beats_per_step)
        relative_step: int = absolute_step % steps_per_measure
        return Fraction( relative_step )


    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> 'Step':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__iadd__( operand % Step(self._staff_reference) % Fraction() )
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Step':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__isub__( operand % Step(self._staff_reference) % Fraction() )
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Step':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__imul__( operand % Step(self._staff_reference) % Fraction() )
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Step':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__itruediv__( operand % Step(self._staff_reference) % Fraction() )
            case _:
                super().__itruediv__(operand)
        return self


class NoteValue(Convertible):
    """`Rational -> Convertible -> NoteValue`

    NoteValue() represents the Note Value duration of a `Note`, a `NoteValue` typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    float(1/4) : NoteValue as 1, 1/2, 1/4, 1/8, 1/16, 1/32.
    """
    def __init__(self, *parameters):
        super().__init__(1/4, *parameters)

    def _get_self_time(self) -> Fraction:
        return self._rational
    

    def _convert_to_beats(self, self_time: Fraction, other_staff: 'Staff' = None) -> Fraction:
        time_staff: Staff = self._get_staff(other_staff)
        beats_per_note: int = time_staff._time_signature._bottom
        return self_time * beats_per_note

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_staff: Staff = self._get_staff()
        beats_per_note: int = time_staff._time_signature._bottom
        return beats / beats_per_note


    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                time_division: str = operand.strip().upper()
                match time_division:
                    case "1/1" | "1":       super().__lshift__(1)
                    case "1/2":             super().__lshift__(1/2)
                    case "1/4":             super().__lshift__(1/4)
                    case "1/6" | "1/4T":    super().__lshift__(1/6)
                    case "1/8":             super().__lshift__(1/8)
                    case "1/12" | "1/8T":   super().__lshift__(1/12)
                    case "1/16":            super().__lshift__(1/16)
                    case "1/24" | "1/16T":  super().__lshift__(1/24)
                    case "1/32":            super().__lshift__(1/32)
                    case "1/48" | "1/32T":  super().__lshift__(1/48)
                    case "1/64":            super().__lshift__(1/64)
                    case "1/96" | "1/64T":  super().__lshift__(1/96)
                    case _:                 super().__lshift__(operand)
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case NoteValue():
                self._rational += operand._rational
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case NoteValue():
                self._rational -= operand._rational
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case NoteValue():
                self._rational *= operand._rational
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case NoteValue():
                if operand._rational != 0:
                    self._rational /= operand._rational
            case _:
                super().__itruediv__(operand)
        return self

class Quantization(NoteValue):
    """`Rational -> Convertible -> NoteValue -> Quantization`

    Quantization() represents the Note Value of each Step. The default is 1/16.

    Parameters
    ----------
    float(1/16) : The Note value of each `Step`.
    
    Examples
    --------
    Gets the Staff Steps per Measure:
    >>> settings << Quantization(1/8)
    >>> settings % Quantization() % Fraction() >> Print()
    1/8
    """
    def __init__(self, *parameters):
        super().__init__(1/16, *parameters)

class Dotted(NoteValue):
    """`Rational -> Convertible -> NoteValue -> Dotted`

    A Dotted() represents the Note Value of a Dotted Note, a Dotted Note Value typically comes as 1/4* and 1/8*.
    Dots are equivalent to the following Note Values:

        +--------+-------------+------------+
        | Dotted | Equivalence | Note Value |
        +--------+-------------+------------+
        | 1      | 1    + 1/2  | 3/2        |
        | 1/2    | 1/2  + 1/4  | 3/4        |
        | 1/4    | 1/4  + 1/8  | 3/8        |
        | 1/8    | 1/8  + 1/16 | 3/16       |
        | 1/16   | 1/16 + 1/32 | 3/32       |
        | 1/32   | 1/32 + 1/64 | 3/64       |
        +--------+-------------+------------+
    
    Parameters
    ----------
    float(1/4) : Note Value as 1, 1/2, 1/4, 1/8, 1/16, 1/32.
    """

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Dotted Note,
        those Parameters are the Dotted length as a Fraction(), a float() an int()
        or even other type of time units, like Measure and Beat with the respective
        conversion accordingly to the note value of set time signature.

        Examples
        --------
        >>> dotted = Dotted(1/4)
        >>> dotted % NoteValue() % Fraction()
        Fraction(3, 8)
        >>> dotted % Dotted() % Fraction()
        Fraction(1, 4)
        >>> dotted % Beat() % Fraction()
        Fraction(3, 2)
        """
        match operand:
            case Dotted():
                return self.copy()
            case int() | float():
                # Reverses the value by multiplying it by 3/2 because it's a Dotted Note
                other_rational: Fraction = self._rational * 2/3
                if isinstance(operand, int):
                    return int(other_rational)
                if isinstance(operand, float):
                    return float(other_rational)
                return other_rational
            case _: return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe() | od.Serialization():
                super().__lshift__(operand)
            # It's just a wrapper for NoteValue 3/2
            case int() | float():
                super().__lshift__(operand) # Starts by setting the self._rational as NoteValue
                # Then it's multiplied by 3/2 because it's a Dotted Note
                self._rational = self._rational * 3 / 2 # Retains the Fraction
                # DON'T DO THIS: "self._rational *= 3/2"
            case str():
                time_division: str = operand.strip().upper()
                match time_division:
                    case "1/1" | "1":       super().__lshift__(1 * 3/2)
                    case "1/2":             super().__lshift__(1/2 * 3/2)
                    case "1/4":             super().__lshift__(1/4 * 3/2)
                    case "1/6" | "1/4T":    super().__lshift__(1/6 * 3/2)
                    case "1/8":             super().__lshift__(1/8 * 3/2)
                    case "1/12" | "1/8T":   super().__lshift__(1/12 * 3/2)
                    case "1/16":            super().__lshift__(1/16 * 3/2)
                    case "1/24" | "1/16T":  super().__lshift__(1/24 * 3/2)
                    case "1/32":            super().__lshift__(1/32 * 3/2)
                    case "1/48" | "1/32T":  super().__lshift__(1/48 * 3/2)
                    case "1/64":            super().__lshift__(1/64 * 3/2)
                    case "1/96" | "1/64T":  super().__lshift__(1/96 * 3/2)
                    case _:                 super().__lshift__(operand)
            case _:
                super().__lshift__(operand)
        return self

    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Dotted():
                self._rational *= operand._rational * 2 / 3 # Reverses evocation of the numerical input
            case int() | float():
                self *= Dotted(operand)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Dotted():
                if operand._rational != 0:
                    self._rational /= operand._rational * 2 / 3 # Reverses evocation of the numerical input
            case int() | float():
                self /= Dotted(operand)
            case _:
                super().__itruediv__(operand)
        return self


class Swing(Rational):
    """`Rational -> Swing`"""
    pass

class Gate(Rational):
    """`Rational -> Gate`"""
    pass

class Period(Rational):
    """`Rational -> Period`"""
    pass

