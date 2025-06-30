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

class Tempo(StaffParameter):
    """`Rational -> StaffParameter -> Tempo`

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

class Quantization(StaffParameter):
    """`Rational -> StaffParameter -> Quantization`

    Quantization() represents the Note Value of each Step. The default is 1/16.

    Parameters
    ----------
    Fraction(1/16) : The Note value of each `Step`.
    
    Examples
    --------
    Gets the Staff Steps per Measure:
    >>> staff = Staff() << Quantization(1/8)
    >>> staff % Quantization() % Fraction() >> Print()
    1/8
    """
    def __init__(self, *parameters):
        super().__init__(1/16, *parameters)

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


class Minutes(Rational):
    """`Rational -> Minutes`"""
    pass

class Convertible(Rational):
    def __init__(self, *parameters):
        import operand_generic as og
        # By default Time values have no Staff reference,
        # so, they aren't transformed, just converted !!
        self._staff_reference: og.Staff = None
        super().__init__(*parameters)

    if TYPE_CHECKING:
        from operand_generic import Staff

    def _set_staff_reference(self, staff_reference: 'Staff' = None) -> Self:
        import operand_generic as og
        if isinstance(staff_reference, og.Staff):
            self._staff_reference = staff_reference
        return self

    def _get_staff_reference(self) -> 'Staff':
        return self._staff_reference

    def _reset_staff_reference(self) -> Self:
        self._staff_reference = None
        return self

    def _get_staff(self, other: Union['Convertible', 'ou.TimeUnit', 'Staff'] = None) -> 'Staff':
        import operand_generic as og
        if self._staff_reference is None:
            if isinstance(other, (Convertible, ou.TimeUnit)):
                if other._staff_reference is not None:
                    return other._staff_reference
            elif isinstance(other, og.Staff):
                return other
            return og.defaults._staff
        return self._staff_reference
    

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case Beats():               return self._get_staff(operand).convertToBeats(self)
            case Measures():            return self._get_staff(operand).convertToMeasures(self)
            case Duration():            return self._get_staff(operand).convertToDuration(self)
            case Steps():               return self._get_staff(operand).convertToSteps(self)
            case ou.Measure():          return self._get_staff(operand).convertToMeasure(self)
            case ou.Beat():             return self._get_staff(operand).convertToBeat(self)
            case ou.Step():             return self._get_staff(operand).convertToStep(self)
            case Position():            return self._get_staff(operand).convertToPosition(self)
            case Length():              return self._get_staff(operand).convertToLength(self)
            case Minutes():             return Minutes( self._get_staff().getMinutes(self) )
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Convertible():
                return self._get_staff(other).convertToBeats(self)._rational \
                    == self._get_staff(other).convertToBeats(other)._rational
            case ou.TimeUnit() | int() | float():
                return self % other == other
            case _:
                return super().__eq__(other)
        return False

    def __lt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Measurement() | TimeValue() | Duration():
                return self._get_staff(other).convertToBeats(self)._rational \
                    < self._get_staff(other).convertToBeats(other)._rational
            case ou.TimeUnit() | int() | float():
                return self % other < other
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Measurement() | TimeValue() | Duration():
                return self._get_staff(other).convertToBeats(self)._rational \
                    > self._get_staff(other).convertToBeats(other)._rational
            case ou.TimeUnit() | int() | float():
                return self % other > other
            case _:
                return super().__gt__(other)
        return False

    def convertToBeats(self) -> 'Beats':
        return self._get_staff().convertToBeats(self)

    def convertToMeasures(self) -> 'Measures':
        return self._get_staff().convertToMeasures(self)

    def convertToSteps(self) -> 'Steps':
        return self._get_staff().convertToSteps(self)

    def convertToDuration(self) -> 'Duration':
        return self._get_staff().convertToDuration(self)

    def convertToMeasure(self) -> 'ou.Measure':
        return self._get_staff().convertToMeasure(self)

    def convertToBeat(self) -> 'ou.Beat':
        return self._get_staff().convertToBeat(self)

    def convertToStep(self) -> 'ou.Step':
        return self._get_staff().convertToStep(self)

    def convertToPosition(self) -> 'Position':
        return self._get_staff().convertToPosition(self)

    def convertToLength(self) -> 'Length':
        return self._get_staff().convertToLength(self)


    def getMinutes(self) -> Fraction:
        return self._get_staff().getMinutes(self)

    def getPlaylist(self) -> list[dict]:
        return self._get_staff().getPlaylist(self)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_generic as og
        import operand_element as oe
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                super().__lshift__(operand)
            case oe.Element() | oc.Composition():
                self._set_staff_reference(operand._get_staff())
            case og.Staff() | None:
                self._set_staff_reference(operand)
            case _:
                super().__lshift__(operand)
        return self

class Measurement(Convertible):
    """`Rational -> Convertible -> Measurement`

    Measurement() represents either a Length or a Position.
    """
    def measurement(self, beats: float = None) -> Self:
        return self << od.Pipe( beats )

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
            case int():                 return self._get_staff().convertToMeasure(self) % int()
            case float():               return self._get_staff().convertToMeasures(self) % float()
            case Fraction():            return self._get_staff().convertToMeasures(self) % Fraction()
            case _:                     return super().__mod__(operand)

    # Position round type: [...)
    def roundMeasures(self) -> Self:
        self_copy: Measurement = self.copy()
        measures: Fraction = self_copy.convertToMeasures()._rational
        measures = Fraction( int(measures) )
        self_copy._rational = self_copy._get_staff().convertToBeats( Measures(measures) )._rational
        return self_copy

    # Position round type: [...)
    def roundBeats(self) -> Self:
        self_copy: Measurement = self.copy()
        beats: Fraction = self_copy.convertToBeats()._rational
        beats = Fraction( int(beats) )
        self_copy._rational = beats
        return self_copy
    
    # Position round type: [...)
    def roundSteps(self) -> Self:
        self_copy: Measurement = self.copy()
        steps: Fraction = self_copy.convertToSteps()._rational
        steps = Fraction( int(steps) )
        self_copy._rational = self_copy._get_staff().convertToBeats( Steps(steps) )._rational
        return self_copy

    def __str__(self):
        return f'Span Beats = {self._rational}'

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = self._get_staff(operand).convertToBeats(operand)._rational
            case ou.Measure():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                measure_beats: Beats = self._get_staff(operand).convertToBeats(self) \
                    - self._get_staff(operand).convertToBeats(self._get_staff(operand).convertToMeasure(self))
                self._rational = (self._get_staff(operand).convertToBeats(operand) + measure_beats)._rational
            case ou.Beat() | ou.Step():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self_measure: ou.Measure = self._get_staff(operand).convertToMeasure(self)
                self._rational = (
                    self._get_staff(operand).convertToBeats(self_measure) + self._get_staff(operand).convertToBeats(operand)
                    )._rational
            case int() | float() | Fraction():
                self << Measures(operand)
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():  # Implicit Measurement conversion
                self._rational += self._get_staff(operand).convertToBeats(operand)._rational
            case int() | float() | Fraction():
                self += Measures(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():  # Implicit Measurement conversion
                self._rational -= self._get_staff(operand).convertToBeats(operand)._rational
            case int() | float() | Fraction():
                self -= Measures(operand)
        return self
    
    # THE DEFAULT INTERPRETATION OF MEASUREMENTS IS IN MEASURES (RELEVANT FOR MULTIPLICATION AND DIVISION)
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():  # Implicit Measurement conversion
                self_measures: Measures = self % Measures()
                operand_measures: Measures = operand % Measures()
                self << self_measures * operand_measures
            case int() | float() | Fraction():
                self *= Measures(operand)  # Default variable is Measures
        return self
    
    # THE DEFAULT INTERPRETATION OF MEASUREMENTS IS IN MEASURES (RELEVANT FOR MULTIPLICATION AND DIVISION)
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():  # Implicit Measurement conversion
                self_measures: Measures = self % Measures()
                operand_measures: Measures = operand % Measures()
                if operand_measures != Measures(0):
                    self << self_measures / operand_measures
            case int() | float() | Fraction():
                self /= Measures(operand)  # Default variable is Measures
        return self


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
        return rounded_length + Measures(1)

    # Measurement/Length round type: (...]
    def roundBeats(self) -> Self:
        rounded_length: Length = super().roundBeats()
        if rounded_length == self:
            return rounded_length
        return rounded_length + Beats(1)
    
    # Measurement/Length round type: (...]
    def roundSteps(self) -> Self:
        rounded_length: Length = super().roundSteps()
        if rounded_length == self:
            return rounded_length
        return rounded_length + Steps(1)


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


class TimeValue(Convertible):  # Works as Absolute Beats
    """`Rational -> Convertible -> TimeValue`

    TimeValue() represents any Time variables like `Measure`, `Beat`, `Duration` and `Step`.
    
    Parameters
    ----------
    Fraction(0) : The default value is 0.
    """
    pass


class Measures(TimeValue):
    """`Rational -> Convertible -> TimeValue -> Measures`

    Measures() represents the fundamental unitary staff time Length, also known as Bar.
    
    Parameters
    ----------
    Fraction(0) : Proportional value to a `Measure` on the `Staff`.
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = self._get_staff(operand).convertToMeasures(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'Measures':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__iadd__(self._get_staff(operand).convertToMeasures(operand)._rational)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Measures':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__isub__(self._get_staff(operand).convertToMeasures(operand)._rational)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Measures':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__imul__(self._get_staff(operand).convertToMeasures(operand)._rational)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Measures':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__itruediv__(self._get_staff(operand).convertToMeasures(operand)._rational)
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
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = self._get_staff(operand).convertToBeats(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__iadd__(self._get_staff(operand).convertToBeats(operand)._rational)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__isub__(self._get_staff(operand).convertToBeats(operand)._rational)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__imul__(self._get_staff(operand).convertToBeats(operand)._rational)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__itruediv__(self._get_staff(operand).convertToBeats(operand)._rational)
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
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = self._get_staff(operand).convertToSteps(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__iadd__(self._get_staff(operand).convertToSteps(operand)._rational)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__isub__(self._get_staff(operand).convertToSteps(operand)._rational)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__imul__(self._get_staff(operand).convertToSteps(operand)._rational)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__itruediv__(self._get_staff(operand).convertToSteps(operand)._rational)
            case _:
                super().__itruediv__(operand)
        return self


class Duration(Convertible):
    """`Rational -> Convertible -> Duration`

    Duration() represents the Note Value duration of a `Note`, a `Duration` typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    Fraction(0) : Duration as 1, 1/2, 1/4, 1/8, 1/16, 1/32.
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Dotted():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = operand._rational * 2 / 3
            case Duration():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = operand._rational
            case Convertible() | ou.TimeUnit():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = self._get_staff(operand).convertToDuration(operand)._rational
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
            case Convertible() | ou.TimeUnit():
                super().__iadd__(self._get_staff(operand).convertToDuration(operand)._rational)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__isub__(self._get_staff(operand).convertToDuration(operand)._rational)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__imul__(self._get_staff(operand).convertToDuration(operand)._rational)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__itruediv__(self._get_staff(operand).convertToDuration(operand)._rational)
            case _:
                super().__itruediv__(operand)
        return self

# NoteValue as an Alias to Duration
NoteValue = Duration


class Dotted(Duration):
    """`Rational -> Convertible -> Duration -> Dotted`

    A Dotted() represents the Note Value of a Dotted Note, a Dotted Note Value typically comes as 1/4* and 1/8*.
    Dots are equivalent to the following Note Values:
        1*    = (1    + 1/2)   = 3/2;
        1/2*  = (1/2  + 1/4)   = 3/4;
        1/4*  = (1/4  + 1/8)   = 3/8;
        1/8*  = (1/8  + 1/16)  = 3/16;
        1/16* = (1/16 + 1/32)  = 3/32;
        1/32* = (1/32 + 1/64)  = 3/64.
    
    Parameters
    ----------
    Fraction(0) : Note Value as 1, 1/2, 1/4, 1/8, 1/16, 1/32.
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
            case int() | float() | Fraction():
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
            case Dotted():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = operand._rational
            case Duration():
                if self._staff_reference is None:
                    self._staff_reference = operand._staff_reference
                self._rational = operand._rational * 3 / 2
            case od.Pipe() | Duration() | od.Serialization():
                super().__lshift__(operand)
            # It's just a wrapper for NoteValue 3/2
            case int() | float() | Fraction():
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
                if not isinstance(operand, (Rational, ou.Unit)):
                    super().__lshift__(operand)
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

