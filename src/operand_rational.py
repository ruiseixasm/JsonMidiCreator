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
        import operand_element as oe
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
            case ol.Null():
                return self
            case o.Operand():
                self << operand % self
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

class ChaosParameters(Rational):
    """Sets the precision that avoids `Chaos` returning inconsistent values among distinct OS!"""
    _limit_denominator: int = 1_000_000 # overrides default limit_denominator

class Index(ChaosParameters):
    """`Rational -> ChaosParameters -> Index`"""
    pass

class Numeral(ChaosParameters):
    """`Rational -> ChaosParameters -> Numeral`"""
    pass

class Result(ChaosParameters):
    """`Rational -> ChaosParameters -> Result`"""
    pass

class Split(ChaosParameters):
    """`Rational -> ChaosParameters -> Split`"""
    pass

class Width(ChaosParameters):
    """`Rational -> ChaosParameters -> Width`"""
    pass

class Height(ChaosParameters):
    """`Rational -> ChaosParameters -> Height`"""
    pass

class dX(ChaosParameters):
    """`Rational -> ChaosParameters -> dX`"""
    pass

class dY(ChaosParameters):
    """`Rational -> ChaosParameters -> dY`"""
    pass

class dZ(ChaosParameters):
    """`Rational -> ChaosParameters -> dZ`"""
    pass

class X0(ChaosParameters):
    """`Rational -> ChaosParameters -> X0`"""
    pass

class Xn(ChaosParameters):
    """`Rational -> ChaosParameters -> Xn`"""
    pass

class Y0(ChaosParameters):
    """`Rational -> ChaosParameters -> Y0`"""
    pass

class Yn(ChaosParameters):
    """`Rational -> ChaosParameters -> Yn`"""
    pass

class Z0(ChaosParameters):
    """`Rational -> ChaosParameters -> Z0`"""
    pass

class Zn(ChaosParameters):
    """`Rational -> ChaosParameters -> Zn`"""
    pass

class Lambda(ChaosParameters):
    """`Rational -> ChaosParameters -> Lambda`"""
    pass

class Modulus(ChaosParameters):
    """`Rational -> ChaosParameters -> Modulus`"""
    pass


class Amount(Rational):
    """`Rational -> Amount`"""
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

class Strictness(Rational):
    """
    `Rational -> Strictness`

    To be used with a `Tamer` to set the probability of no slack, meaning, the probability of being processed, enforced.
    
    Parameters
    ----------
    Fraction(1), int(), float() : A number from 0 to 1 as a probability of no slack.
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)


class Tempo(Rational):
    """`Rational -> Tempo`

    Tempo() represents the TimeSignature Beats per Minute (BPM). The default is 120 BPM.

    Parameters
    ----------
    Fraction(120) : The playing tempo with the default as 120 BPM (Beats Per Minute).
    
    Examples
    --------
    Gets the TimeSignature Steps per Measure:
    >>> staff = TimeSignature(Tempo(110))
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


class TimeSignatureParameter(Rational):
    """`Rational -> TimeSignatureParameter`"""
    pass

class TimeSignatureParameter(TimeSignatureParameter):
    """`Rational -> TimeSignatureParameter -> TimeSignatureParameter`"""
    pass

class BeatsPerMeasure(TimeSignatureParameter):
    """`Rational -> TimeSignatureParameter -> TimeSignatureParameter -> BeatsPerMeasure`

    BeatsPerMeasure is the **top** number of the time signature,
    in a 3/4 time signature 3 are the Beats per Measure. The default is 4, 4 Beats per Measure.

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
    """`Rational -> TimeSignatureParameter -> TimeSignatureParameter -> BeatNoteValue`

    BeatNoteValue is the inverted **bottom** number of the time signature, represents the Note Value for the Beat,
    in a 3/4 time signature 1/4 is the Beats Note Value. The default is 1/4, 1/4 NoteValue for each Beat.

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
    """`Rational -> TimeSignatureParameter -> TimeSignatureParameter -> NotesPerMeasure`

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

class StepsPerMeasure(TimeSignatureParameter):
    """`Rational -> TimeSignatureParameter -> StepsPerMeasure`

    StepsPerMeasure() represents the Note Value for a single Measure, in a 3/4 time signature with 
    a Quantization of 1/16 you get 12 Steps per each Measure.
    The default is 16, 16 Steps for each Measure. This concerns TimeSignature objects Quantization.

    Parameters
    ----------
    Fraction(16) : The amount of `Steps` in a `Measure`.
    
    Examples
    --------
    Gets the TimeSignature Steps per Measure:
    >>> staff = TimeSignature()
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

class StepsPerNote(TimeSignatureParameter):
    """`Rational -> TimeSignatureParameter -> StepsPerNote`

    StepsPerNote() represents the inversion of the Quantization, for a Quantization of 1/16 
    you will get 16 Notes per Step.
    The default is 16, 16 Steps for each Note. This concerns TimeSignature objects Quantization.

    Parameters
    ----------
    Fraction(16) : The amount of `Steps` per each `Note`.
    
    Examples
    --------
    Gets the TimeSignature Steps per Measure:
    >>> staff = TimeSignature()
    >>> staff << TimeSignature(3, 4)
    >>> steps_per_note = staff % StepsPerNote()
    >>> steps_per_note % Fraction() >> Print()
    16

    Gets the TimeSignature Quantization:
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
    from operand_generic import TimeSignature

class Convertible(Rational):
    def __init__(self, *parameters):
        import operand_generic as og
        # By default Time values have no TimeSignature reference,
        # so, they aren't transformed, just converted !!
        self._time_signature_reference: og.TimeSignature = None
        super().__init__(*parameters)

    # By default considers beats as the self_time, meaning, no conversion is done to the values
    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        return self_time

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        return beats

    def _get_beats(self, other_time_signature: 'TimeSignature' = None) -> Fraction:
        return self._convert_to_beats(self._rational, other_time_signature)

    def _set_with_beats(self, beats: Fraction) -> Self:
        self._rational = self._convert_from_beats(beats)
        return self

    def _get_self_time(self) -> Fraction:
        return self._convert_from_beats(self._rational)


    def _get_time_signature(self, other_time_signature: 'TimeSignature' = None) -> 'TimeSignature':
        import operand_generic as og
        if self._time_signature_reference is None:
            if isinstance(other_time_signature, og.TimeSignature):
                return other_time_signature
            return og.settings._time_signature
        return self._time_signature_reference


    @staticmethod
    def _round_timeunit(timeunit: o.T) -> o.T:
        if isinstance(timeunit, TimeUnit):
            timeunit._rational = Fraction(int(timeunit._rational), 1)
        return timeunit

    def roundMeasures(self) -> Self:
        return self.copy(self % Measure())

    def roundBeats(self) -> Self:
        return self.copy(self % Beat())
    
    def roundSteps(self) -> Self:
        return self.copy(self % Step())


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case Convertible():
                self_beats: Fraction = self._get_beats(operand._time_signature_reference)
                if isinstance(operand, TimeUnit):
                    converted_timeunit: o.T = operand.copy(self._time_signature_reference)._set_with_beats(self_beats)
                    return self._round_timeunit(converted_timeunit)
                return operand.copy(self._time_signature_reference)._set_with_beats(self_beats)
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case TimeUnit() | int() | float():
                return self % other == other
            case Convertible():
                return self._get_beats(other._time_signature_reference) == other._get_beats(self._time_signature_reference)
            case _:
                return super().__eq__(other)
        return False

    def __lt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case TimeUnit() | int() | float():
                return self % other < other
            case Convertible():
                return self._get_beats(other._time_signature_reference) < other._get_beats(self._time_signature_reference)
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case TimeUnit() | int() | float():
                return self % other > other
            case Convertible():
                return self._get_beats(other._time_signature_reference) > other._get_beats(self._time_signature_reference)
            case _:
                return super().__gt__(other)
        return False


    def getPlaylist(self) -> list[dict]:
        import operand_generic as og
        beats: Fraction = self % Beats() % Fraction()
        return og.settings.getPlaylist(beats)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_generic as og
        import operand_element as oe
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand._time_signature_reference
                # Needs to go very easy to avoid infinite Recursion
                operand_beats: Beats = operand._get_beats(self._time_signature_reference)
                self._set_with_beats(operand_beats)
            case oe.Element() | oc.Composition():
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand._get_time_signature()
            case og.TimeSignature():
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand
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

    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature(other_time_signature)
        beats_per_measure: int = time_signature._top
        return self_time * beats_per_measure

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature()
        beats_per_measure: int = time_signature._top
        return beats / beats_per_measure

    def _get_beats(self, other_time_signature: 'TimeSignature' = None) -> Fraction:
        return self._rational   # Kept as beats already

    def _set_with_beats(self, beats: Fraction) -> Self:
        self._rational = beats  # Kept as beats already
        return self

    @staticmethod
    def _round_timeunit(timeunit: o.T) -> o.T:
        if isinstance(timeunit, TimeUnit):
            round_timeunit: Fraction = Fraction(int(timeunit._rational), 1)
            if timeunit != round_timeunit:
                round_timeunit += 1
            timeunit._rational = round_timeunit
        return timeunit

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
            case TimeUnit():
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand._time_signature_reference
                self._rational = operand % Beats(self._time_signature_reference) % Fraction()
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
                self._rational += operand % Beats(self._time_signature_reference) % Fraction()
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
                self._rational -= operand % Beats(self._time_signature_reference) % Fraction()
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
                operand_measures: Measures = operand % Measures(self._time_signature_reference)
                self << self_measures * operand_measures
            case _:
                super().__imul__(operand)
        return self
    
    # THE DEFAULT INTERPRETATION OF MEASUREMENTS IS IN MEASURES (RELEVANT FOR MULTIPLICATION AND DIVISION)
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():  # Implicit Measurement conversion
                self_measures: Measures = self % Measures()
                operand_measures: Measures = operand % Measures(self._time_signature_reference)
                if operand_measures != Measures(0):
                    self << self_measures / operand_measures
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
    Fraction(0) : The position on the `TimeSignature` measured in `Measures`.
    
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

    @staticmethod
    def _round_timeunit(timeunit: o.T) -> o.T:
        if isinstance(timeunit, TimeUnit):
            timeunit._set_position_value()  # Because for position TimeUnit is relative to Measure!
            timeunit._rational = Fraction(int(timeunit._rational), 1)
        return timeunit

    def __eq__(self, other: any) -> bool:
        import operand_generic as og
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case og.Segment():
                return other == self
            case _:
                return super().__eq__(other)
        return False

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit():
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand._time_signature_reference
                # This preserves the position in the Measure
                self += operand - self % operand    # operand >= actual_unit
            case _:
                super().__lshift__(operand)
        return self

    # Measurement round type: [...)
    def roundMeasures(self) -> Self:
        return self.copy(self % Measure() % Measures())

    # Measurement round type: [...)
    def roundBeats(self) -> Self:
        return self.copy(self % Beats() % Beat() % Beats())
    
    # Measurement round type: [...)
    def roundSteps(self) -> Self:
        return self.copy(self % Steps() % Step() % Steps())


class Length(Measurement):
    """`Rational -> Convertible -> Measurement -> Length`

    Length() is a Parameter applicable to `Element` and `Clip` objects. The input and output
    is given in `Measures` and their `TimeUnit` returns are rounded up to the NEXT one.
    Internally though, the values are in `Beats` and can be directly accessed with the `//` operator.

    Parameters
    ----------
    Fraction(0) : Represents the duration along the `TimeSignature` in `Measures`.
    
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


class Duration(Measurement):
    """`Rational -> Convertible -> Measurement -> Duration`

    Duration() represents the Note Value duration of a `Note`, a `Duration` typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    Fraction(0) : Duration as 1, 1/2, 1/4, 1/8, 1/16, 1/32.
    """
    
    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature(other_time_signature)
        beats_per_note: int = time_signature._bottom
        return self_time * beats_per_note

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature()
        beats_per_note: int = time_signature._bottom
        return beats / beats_per_note

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case float() | int():
                return self % NoteValue() % operand
            case _:
                return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case float() | int():
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
            case float() | int():
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
            case float() | int():
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
    Fraction(0) : Proportional value to a `Measure` on the `TimeSignature`.
    """
    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature(other_time_signature)
        beats_per_measure: int = time_signature._top
        return self_time * beats_per_measure

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature()
        beats_per_measure: int = time_signature._top
        return beats / beats_per_measure

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
    Fraction(0) : Proportional value to a `Beat` on the `TimeSignature`.
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

class Quantization(Beats):
    """`Rational -> Convertible -> Beats -> Quantization`

    Quantization() represents the Step duration in Beats. The default is 1/4 Beat.

    Parameters
    ----------
    float(1/4) : The `Beat` ratio of each `Step`.
    
    Examples
    --------
    Gets the TimeSignature Steps per Measure:
    >>> settings << Quantization(1/8)
    >>> settings % Quantization() % Fraction() >> Print()
    1/8
    """
    def __init__(self, *parameters):
        super().__init__(1/4, *parameters)


class Steps(TimeValue):
    """`Rational -> Convertible -> TimeValue -> Steps`

    A Step() represents the Length given by the `Quantization`, normally 1/4 Beats.
    
    Parameters
    ----------
    Fraction(0) : Steps as 1, 2, 4, 8...
    """
    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        import operand_generic as og
        beats_per_step: Fraction = og.settings._quantization    # Quantization is in Beats ratio
        return self_time * beats_per_step

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        import operand_generic as og
        beats_per_step: Fraction = og.settings._quantization    # Quantization is in Beats ratio
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


class NoteValue(TimeValue):
    """`Rational -> Convertible -> TimeValue -> NoteValue`

    NoteValue() represents the Note Value duration of a `Note`, a `NoteValue` typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    float(1/4) : NoteValue as 1, 1/2, 1/4, 1/8, 1/16, 1/32.
    """
    def __init__(self, *parameters):
        super().__init__(1/4, *parameters)

    def _get_self_time(self) -> Fraction:
        return self._rational
    

    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature(other_time_signature)
        beats_per_note: int = time_signature._bottom
        return self_time * beats_per_note

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature()
        beats_per_note: int = time_signature._bottom
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

class Dotted(NoteValue):
    """`Rational -> Convertible -> TimeValue -> NoteValue -> Dotted`

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


class TimeUnit(Convertible):
    """`Rational -> Convertible -> TimeUnit`
    """
    def __init__(self, *parameters):
        import operand_generic as og
        # By default Time values have no TimeSignature reference,
        # so, they aren't transformed, just converted !!
        self._time_signature_reference: og.TimeSignature = None
        super().__init__(*parameters)

    def _get_self_time(self) -> Fraction:
        return Fraction( int(self._rational) )
    

    def _set_position_value(self) -> Self:
        return self


    def __eq__(self, other: any) -> bool:
        import operand_generic as og
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Convertible():
                return self._get_beats(other._time_signature_reference) \
                    == other._get_beats(self._time_signature_reference)
            case og.Segment():
                return other == self
            case _:
                return super().__eq__(other)
        return False

    def __lt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Convertible():
                return self._get_beats(other._time_signature_reference) \
                    < other._get_beats(self._time_signature_reference)
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Convertible():
                return self._get_beats(other._time_signature_reference) \
                    > other._get_beats(self._time_signature_reference)
            case _:
                return super().__gt__(other)
        return False

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        super().__lshift__(operand)
        # Makes sure it's unitary (int)
        self._rational = Fraction(int(self._rational), 1)
        return self


class Measure(TimeUnit):
    """`Rational -> Convertible -> TimeUnit -> Measure`

    A Measure() represents the basic unit of a TimeSignature division.

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
    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature(other_time_signature)
        beats_per_measure: int = time_signature._top
        self_time: Fraction = self._get_self_time()
        return self_time * beats_per_measure

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        time_signature: TimeSignature = self._get_time_signature()
        beats_per_measure: int = time_signature._top
        return beats / beats_per_measure    # As value NOT unitary


    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> 'Measure':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__iadd__( operand % Measure(self._time_signature_reference) % Fraction() )
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Measure':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__isub__( operand % Measure(self._time_signature_reference) % Fraction() )
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Measure':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__imul__( operand % Measure(self._time_signature_reference) % Fraction() )
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Measure':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__itruediv__( operand % Measure(self._time_signature_reference) % Fraction() )
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
    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        self_time: Fraction = self._get_self_time()
        return self_time

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        return beats    # As value NOT unitary

    def _set_position_value(self) -> Self:
        time_signature: TimeSignature = self._get_time_signature()
        beats_per_measure: int = time_signature._top
        return self << self._rational % beats_per_measure

    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> 'Beat':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__iadd__( operand % Beat(self._time_signature_reference) % Fraction() )
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Beat':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__isub__( operand % Beat(self._time_signature_reference) % Fraction() )
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Beat':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__imul__( operand % Beat(self._time_signature_reference) % Fraction() )
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Beat':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__itruediv__( operand % Beat(self._time_signature_reference) % Fraction() )
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
    def _convert_to_beats(self, self_time: Fraction, other_time_signature: 'TimeSignature' = None) -> Fraction:
        import operand_generic as og
        beats_per_step: Fraction = og.settings._quantization    # Quantization is in Beats ratio
        return int(self_time) * beats_per_step

    def _convert_from_beats(self, beats: Fraction) -> Fraction:
        import operand_generic as og
        beats_per_step: Fraction = og.settings._quantization    # Quantization is in Beats ratio
        return beats / beats_per_step   # As value NOT unitary

    def _set_position_value(self) -> Self:
        import operand_generic as og
        beats_per_step: Fraction = og.settings._quantization    # Quantization is in Beats ratio
        time_signature: TimeSignature = self._get_time_signature()
        beats_per_measure: int = time_signature._top
        steps_per_measure: int = int(beats_per_measure / beats_per_step)
        return self << self._rational % steps_per_measure

    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> 'Step':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__iadd__( operand % Step(self._time_signature_reference) % Fraction() )
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Step':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__isub__( operand % Step(self._time_signature_reference) % Fraction() )
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Step':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__imul__( operand % Step(self._time_signature_reference) % Fraction() )
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Step':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                super().__itruediv__( operand % Step(self._time_signature_reference) % Fraction() )
            case _:
                super().__itruediv__(operand)
        return self


class Swing(Rational):
    """`Rational -> Swing`"""
    pass

class Gate(Rational):
    """`Rational -> Gate`"""
    pass

