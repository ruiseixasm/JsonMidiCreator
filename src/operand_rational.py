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
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Tuple, Optional, Any, Self, Generic
from fractions import Fraction
import re
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_data as od
import operand_frame as of
import operand_label as ol


# Fraction objects are immutable, so modifications create new objects rather than changing existing ones.
# Assignments and passing around fractions involve copying references, not duplicating the actual object data.
# Due to immutability, you can safely assume Fraction behaves with value semantics—modifications don't affect the original object.
    # int * float results in a float
    # Fraction * float results in a float
    # Fraction * Fraction results in a Fraction

class Rational(o.Operand):
    """
    This is a type of Operand that has associated to a Fractional number.
    This class is intended to represent time based variables that are ratios like the typical 1/4 note value

    Parameters
    ----------
    first : float_like
        A fraction like 1/4 or 0.9 or 1.24
    """
    
    _limit_denominator: int = 1000000  # default value of limit_denominator

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
            case od.DataSource():
                match operand._data:
                    case Fraction():        return self._rational           # returns a Fraction()
                    case float():           return float(self._rational)
                    case int():             return int(self._rational)
                    case of.Frame():        return self % od.DataSource( operand._data )
                    case str():             return str(self._rational)
                    case Rational() | ou.Unit():
                                            return operand.__class__() << od.DataSource( self._rational )
                    case _:                 return super().__mod__(operand)
            case Fraction():        return self._rational
            case float():           return float(self._rational)
            case int():             return int(self._rational)
            case of.Frame():        return self % (operand._data)
            case str():             return str(self._rational)
            case Rational() | ou.Unit():
                                    return operand.__class__() << od.DataSource( self._rational )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Rational():
                return self._rational == other._rational
            case int() | float() | ou.Unit():
                return self % od.DataSource( other ) == other
            case _:
                if other.__class__ == o.Operand:
                    return True
        return False
    
    def __lt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Rational():
                return self._rational < other._rational
            case int() | float() | ou.Unit():
                return self % od.DataSource( other ) < other
        return False
    
    def __gt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Rational():
                return self._rational > other._rational
            case int() | float() | ou.Unit():
                return self % od.DataSource( other ) > other
        return False
    
    def __le__(self, other: any) -> bool:
        return self == other or self < other
    
    def __ge__(self, other: any) -> bool:
        return self == other or self > other
    
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
            self._rational = Fraction( serialization["parameters"]["fraction"] )
            if self._limit_denominator > 0:
                self._rational = Fraction(self._rational).limit_denominator(self._limit_denominator)
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Rational():
                super().__lshift__(operand)
                self._rational = operand._rational
            case od.DataSource():
                match operand._data:
                    case Fraction():
                        self._rational = operand._data
                    case float() | int():
                        self._rational = Fraction(operand._data)
                    case str():
                        try:
                            self._rational = Fraction(operand._data)
                        except ValueError as e:
                            print(f"Error: {e}, '{operand._data}' is not a number!")
                    case Rational() | ou.Unit():
                        self._rational = operand._data % od.DataSource( Fraction() )
            case Fraction():
                self._rational = operand
            case float() | int():
                self._rational = Fraction(operand)
            case str():
                self << od.DataSource( operand )
            case ou.Unit():
                self._rational = operand % Fraction()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case tuple():
                for single_operand in operand:
                    self << single_operand
        if self._limit_denominator > 0 and not isinstance(operand, tuple):
            self._rational = Fraction(self._rational).limit_denominator(self._limit_denominator)
        return self

    def __iadd__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                self += value % od.DataSource( Fraction() )
            case Fraction() | int():
                self._rational += value
            case float():
                if self._limit_denominator > 0:
                    self._rational += Fraction(value).limit_denominator(self._limit_denominator)
                else:
                    self._rational += Fraction(value)
        return self
    
    def __isub__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                self -= value % od.DataSource( Fraction() )
            case Fraction() | int():
                self._rational -= value
            case float():
                if self._limit_denominator > 0:
                    self._rational -= Fraction(value).limit_denominator(self._limit_denominator)
                else:
                    self._rational -= Fraction(value)
        return self
    
    def __imul__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                self *= value % od.DataSource( Fraction() )
            case Fraction() | int():
                self._rational *= value
            case float():
                if self._limit_denominator > 0:
                    self._rational *= Fraction(value).limit_denominator(self._limit_denominator)
                else:
                    self._rational *= Fraction(value)
        return self
    
    def __itruediv__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                self /= value % od.DataSource( Fraction() )
            case Fraction() | int():
                if value != 0:
                    self._rational /= value
            case float():
                if value != 0:
                    if self._limit_denominator > 0:
                        self._rational /= Fraction(value).limit_denominator(self._limit_denominator)
                    else:
                        self._rational /= Fraction(value)
        return self

class HiPrecision(Rational):

    _limit_denominator: int = 0 # overrides default limit_denominator

class Index(HiPrecision):
    pass

class Split(HiPrecision):
    pass

class Width(HiPrecision):
    pass

class Height(HiPrecision):
    pass

class X(HiPrecision):
    pass

class Y(HiPrecision):
    pass

class Z(HiPrecision):
    pass

class dX(HiPrecision):
    pass

class dY(HiPrecision):
    pass

class dZ(HiPrecision):
    pass

class X0(HiPrecision):
    pass

class Xn(HiPrecision):
    pass

class Lambda(HiPrecision):
    pass

class Negative(Rational):
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case Fraction():        return self._rational * -1
            case float():           return float(self._rational * -1)
            case int():             return int(self._rational * -1)
            case of.Frame():        return self % (operand._data)
            case str():             return str(self._rational * -1)
            case Rational() | ou.Unit():
                                    return operand.__class__() << od.DataSource( self._rational )
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
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

class RationalDefault(Rational):
    pass



class StaffParameter(Rational):
    pass

class TimeSignatureParameter(StaffParameter):
    pass

class BeatsPerMeasure(TimeSignatureParameter):
    """
    BeatsPerMeasure() sets the top value of a time signature, in a 3/4 time signature 3 are the Beats per Measure.
    The default is 4, 4 Beats per Measure.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 4 BeatsPerMeasure.
    
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
    """
    BeatNoteValue() represents the Note Value for the Beat, in a 3/4 time signature 1/4 is the Beats Note Value.
    The default is 1/4, 1/4 NoteValue for each Beat.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 1/4 BeatNoteValue.
    
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
    """
    NotesPerMeasure() represents the Note Value for a single Measure, in a 3/4 time signature 3/4 is the Measure Note Value.
    The default is 1, 1 NoteValue for each Measure. This is just an output parameter and not a setting one.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 1/4 NotesPerMeasure.
    
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
    """
    StepsPerMeasure() represents the Note Value for a single Measure, in a 3/4 time signature with 
    a Quantization of 1/16 you get 12 Steps per each Measure.
    The default is 16, 16 Steps for each Measure. This concerns Staff objects Quantization.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 16 StepsPerMeasure.
    
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
    """
    StepsPerNote() represents the inversion of the Quantization, for a Quantization of 1/16 
    you will get 16 Notes per Step.
    The default is 16, 16 Steps for each Note. This concerns Staff objects Quantization.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 16 StepsPerNote.
    
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
    """
    Tempo() represents the Staff Beats per Minute (BPM). The default is 120 BPM.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 120 BPM of Tempo.
    
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
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
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
    """
    Quantization() represents the Note Value of each Step. The default is 1/16.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 1/16 NoteValue of Quantization.
    
    Examples
    --------
    Gets the Staff Steps per Measure:
    >>> staff = Staff() << Quantization(1/8)
    >>> staff % Quantization() % Fraction() >> Print()
    1/8
    """
    def __init__(self, *parameters):
        super().__init__(1/16, *parameters)


class Convertible(Rational):
    def __init__(self, *parameters):
        import operand_generic as og
        self._staff_reference: og.Staff     = og.defaults._staff
        super().__init__(*parameters)

    if TYPE_CHECKING:
        from operand_generic import Staff

    def set_staff_reference(self, staff_reference: 'Staff' = None) -> Self:
        import operand_generic as og
        if isinstance(staff_reference, og.Staff):
            self._staff_reference = staff_reference
        return self

    def get_staff_reference(self) -> 'Staff':
        return self._staff_reference

    def reset_staff_reference(self) -> Self:
        import operand_generic as og
        self._staff_reference = og.defaults._staff
        return self

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case Beats():               return self._staff_reference.convertToBeats(self)
            case Measures():            return self._staff_reference.convertToMeasures(self)
            case Duration():            return self._staff_reference.convertToDuration(self)
            case Steps():               return self._staff_reference.convertToSteps(self)
            case ou.Measure():          return self._staff_reference.convertToMeasure(self)
            case ou.Beat():             return self._staff_reference.convertToBeat(self)
            case ou.Step():             return self._staff_reference.convertToStep(self)
            case Position():            return self._staff_reference.convertToPosition(self)
            case Length():              return self._staff_reference.convertToLength(self)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Length() | TimeValue() | Duration():
                return self._staff_reference.convertToBeats(self)._rational == self._staff_reference.convertToBeats(other)._rational
            case ou.TimeUnit() | int() | float():
                return self % other == other
            case _:
                return super().__eq__(other)
        return False

    def __lt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Length() | TimeValue() | Duration():
                return self._staff_reference.convertToBeats(self)._rational < self._staff_reference.convertToBeats(other)._rational
            case ou.TimeUnit() | int() | float():
                return self % other < other
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Length() | TimeValue() | Duration():
                return self._staff_reference.convertToBeats(self)._rational > self._staff_reference.convertToBeats(other)._rational
            case ou.TimeUnit() | int() | float():
                return self % other > other
            case _:
                return super().__gt__(other)
        return False

    #######################################################################
    # Conversion (Simple, One-way) | Only destination Staff is considered #
    #######################################################################

    def convertToBeats(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Beats':
        match time:
            case None:
                return self._staff_reference.convertToBeats(self)
            case _:
                return self._staff_reference.convertToBeats(time)

    def convertToMeasures(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Measures':
        match time:
            case None:
                return self._staff_reference.convertToMeasures(self)
            case _:
                return self._staff_reference.convertToMeasures(time)
        
    def convertToSteps(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Steps':
        match time:
            case None:
                return self._staff_reference.convertToSteps(self)
            case _:
                return self._staff_reference.convertToSteps(time)

    def convertToDuration(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Duration':
        match time:
            case None:
                return self._staff_reference.convertToDuration(self)
            case _:
                return self._staff_reference.convertToDuration(time)

    def convertToMeasure(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'ou.Measure':
        match time:
            case None:
                return self._staff_reference.convertToMeasure(self)
            case _:
                return self._staff_reference.convertToMeasure(time)

    def convertToBeat(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'ou.Beat':
        match time:
            case None:
                return self._staff_reference.convertToBeat(self)
            case _:
                return self._staff_reference.convertToBeat(time)

    def convertToStep(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'ou.Step':
        match time:
            case None:
                return self._staff_reference.convertToStep(self)
            case _:
                return self._staff_reference.convertToStep(time)

    def convertToLength(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Length':
        match time:
            case None:
                return self._staff_reference.convertToLength(self)
            case _:
                return self._staff_reference.convertToLength(time)

    def convertToPosition(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Position':
        match time:
            case None:
                return self._staff_reference.convertToPosition(self)
            case _:
                return self._staff_reference.convertToPosition(time)

    ################################################################################################################
    # Transformation (Two-way, Context-Dependent) | Both Staffs are considered, the source and the destination one #
    ################################################################################################################

    def transformBeats(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Beats':
        match time:
            case None:
                return self._staff_reference.transformBeats(self)
            case _:
                return self._staff_reference.transformBeats(time)

    def transformMeasures(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Measures':
        match time:
            case None:
                return self._staff_reference.transformMeasures(self)
            case _:
                return self._staff_reference.transformMeasures(time)

    def transformSteps(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Steps':
        match time:
            case None:
                return self._staff_reference.transformSteps(self)
            case _:
                return self._staff_reference.transformSteps(time)

    def transformDuration(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Duration':
        match time:
            case None:
                return self._staff_reference.transformDuration(self)
            case _:
                return self._staff_reference.transformDuration(time)

    def transformMeasure(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'ou.Measure':
        match time:
            case None:
                return self._staff_reference.transformMeasure(self)
            case _:
                return self._staff_reference.transformMeasure(time)

    def transformBeat(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'ou.Beat':
        match time:
            case None:
                return self._staff_reference.transformBeat(self)
            case _:
                return self._staff_reference.transformBeat(time)

    def transformStep(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'ou.Step':
        match time:
            case None:
                return self._staff_reference.transformStep(self)
            case _:
                return self._staff_reference.transformStep(time)

    def transformLength(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Length':
        match time:
            case None:
                return self._staff_reference.transformLength(self)
            case _:
                return self._staff_reference.transformLength(time)

    def transformPosition(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> 'Position':
        match time:
            case None:
                return self._staff_reference.transformPosition(self)
            case _:
                return self._staff_reference.transformPosition(time)


    def getMillis_rational(self, time: Union['Convertible', 'ou.TimeUnit'] = None) -> Fraction:
        match time:
            case None:
                return self._staff_reference.getMinutes(self)
            case _:
                return self._staff_reference.getMinutes(time)

    def getPlaylist(self, position: 'Position' = None) -> list:
        match position:
            case None:
                return self._staff_reference.getPlaylist(self)
            case _:
                return self._staff_reference.getPlaylist(position)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
                self._staff_reference = operand._staff_reference
            case _:
                super().__lshift__(operand)
        return self



class Length(Convertible):
    """
    Length() is a Parameter applicable to Element and Clip objects. The input and output
    is given in Measures and their TimeUnit returns are rounded up to the next one.
    Internally though, the values are in Beats and can be directly accessed with the "//" operator.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 0 of Length.
    
    Examples
    --------
    Gets the Note default Length from 1/4 NoteValue:
    >>> note = Note()
    >>> note % Length() % float() >> Print()
    0.25
    >>> note % Length() // float() >> Print()
    1.0
    """

    def position(self, beats: float = None) -> Self:
        return self << od.DataSource( beats )

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
            case int():                 return self._staff_reference.convertToMeasure(self) % int()
            case float():               return self._staff_reference.convertToMeasures(self) % float()
            case Fraction():            return self._staff_reference.convertToMeasures(self) % Fraction()
            case _:                     return super().__mod__(operand)

    def __str__(self):
        return f'Span Beats = {self._rational}'

    # Length round type: (...]
    def roundMeasures(self) -> 'Length':
        measures: Fraction = self.convertToMeasures()._rational
        if measures.denominator != 1:
            measures = Fraction(int(measures) + 1)  # moves forward one unit
        else:
            measures = Fraction( int(measures) )
        return self.convertToLength( Measures(measures) )

    # Length round type: (...]
    def roundBeats(self) -> 'Length':
        beats: Fraction = self.convertToBeats()._rational
        if beats.denominator != 1:
            beats = Fraction(int(beats) + 1)  # moves forward one unit
        else:
            beats = Fraction( int(beats) )
        return self.convertToLength( Beats(beats) )
    
    # Length round type: (...]
    def roundSteps(self) -> 'Length':
        steps: Fraction = self.convertToSteps()._rational
        if steps.denominator != 1:
            steps = Fraction(int(steps) + 1)  # moves forward one unit
        else:
            steps = Fraction( int(steps) )
        return self.convertToLength( Steps(steps) )

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Length():
                super().__lshift__(operand)
            case TimeValue() | Duration():
                self._rational = self._staff_reference.convertToBeats(operand)._rational
            case ou.Measure():
                measure_beats: Beats = self._staff_reference.convertToBeats(self) \
                    - self._staff_reference.convertToBeats(self._staff_reference.convertToMeasure(self))
                self._rational = (self._staff_reference.convertToBeats(operand) + measure_beats)._rational
            case ou.Beat() | ou.Step():
                self_measure: ou.Measure = self._staff_reference.convertToMeasure(self)
                self._rational = (self.convertToBeats(self_measure) + self.convertToBeats(operand))._rational
            case int() | float() | Fraction():
                self << Measures(operand)
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'Length':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Length() | TimeValue() | Duration() | ou.TimeUnit():  # Implicit Length conversion
                self._rational += self._staff_reference.convertToBeats(operand)._rational
            case int() | float() | Fraction():
                self += Measures(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Length':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Length() | TimeValue() | Duration() | ou.TimeUnit():  # Implicit Length conversion
                self._rational -= self._staff_reference.convertToBeats(operand)._rational
            case int() | float() | Fraction():
                self -= Measures(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Length':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Length():
                multiplier: Fraction = operand.convertToMeasures()._rational
                return super().__imul__(multiplier)
        return super().__imul__(operand)
    
    def __itruediv__(self, operand: any) -> 'Length':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Length():
                divider: Fraction = operand.convertToMeasures()._rational
                return super().__itruediv__(divider)
        return super().__itruediv__(operand)


class Position(Length):
    
    # Position round type: [...)
    def roundMeasures(self) -> 'Position':
        measures: Fraction = self.convertToMeasures()._rational
        measures = Fraction( int(measures) )
        return self.convertToPosition( Measures(measures) )

    # Position round type: [...)
    def roundBeats(self) -> 'Position':
        beats: Fraction = self.convertToBeats()._rational
        beats = Fraction( int(beats) )
        return self.convertToPosition( Beats(beats) )
    
    # Position round type: [...)
    def roundSteps(self) -> 'Position':
        steps: Fraction = self.convertToSteps()._rational
        steps = Fraction( int(steps) )
        return self.convertToPosition( Steps(steps) )


class TimeValue(Convertible):  # Works as Absolute Beats
    """
    TimeUnit() represents any Time Length variables, namely, Measure, Beat, NoteValue and Step.
    
    Parameters
    ----------
    first : float_like
        Not intended to be set directly
    """
    pass


class Measures(TimeValue):
    """
    Measure() represents the Staff Time Length in Measures, also known as Bar.
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Measure on the Staff
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case Convertible() | ou.TimeUnit():
                self._rational = self._staff_reference.convertToMeasures(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_generic as og
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case Convertible() | ou.TimeUnit():
                self._rational = self._staff_reference.convertToMeasures(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'Measures':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__iadd__(self._staff_reference.convertToMeasures(operand)._rational)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Measures':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__isub__(self._staff_reference.convertToMeasures(operand)._rational)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Measures':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__imul__(self._staff_reference.convertToMeasures(operand)._rational)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Measures':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__itruediv__(self._staff_reference.convertToMeasures(operand)._rational)
            case _:
                super().__itruediv__(operand)
        return self


class Beats(TimeValue):
    """
    A Beat() represents the Staff Time Length in Beat on which the Tempo is based on (BPM).
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Beat on the Staff
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_generic as og
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case Convertible() | ou.TimeUnit():
                self._rational = self._staff_reference.convertToBeats(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case Convertible() | ou.TimeUnit():
                self._rational = self._staff_reference.convertToBeats(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__iadd__(self._staff_reference.convertToBeats(operand)._rational)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__isub__(self._staff_reference.convertToBeats(operand)._rational)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__imul__(self._staff_reference.convertToBeats(operand)._rational)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__itruediv__(self._staff_reference.convertToBeats(operand)._rational)
            case _:
                super().__itruediv__(operand)
        return self


class Steps(TimeValue):
    """
    A Step() represents the Length given by the Quantization, normally 1/16 Note Value.
    
    Parameters
    ----------
    first : float_like
        Steps as 1, 2, 4, 8
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case Convertible() | ou.TimeUnit():
                self._rational = self._staff_reference.convertToSteps(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_generic as og
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case Convertible() | ou.TimeUnit():
                self._rational = self._staff_reference.convertToSteps(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__iadd__(self._staff_reference.convertToSteps(operand)._rational)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__isub__(self._staff_reference.convertToSteps(operand)._rational)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__imul__(self._staff_reference.convertToSteps(operand)._rational)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__itruediv__(self._staff_reference.convertToSteps(operand)._rational)
            case _:
                super().__itruediv__(operand)
        return self


class Duration(Convertible):
    """
    NoteValue() represents the Duration of a Note, a Note Value typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    first : float_like
        Note Value as 1, 1/2, 1/4, 1/8, 1/16, 1/32
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case Convertible() | ou.TimeUnit():
                self._rational = self._staff_reference.convertToDuration(operand)._rational
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__iadd__(self._staff_reference.convertToDuration(operand)._rational)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__isub__(self._staff_reference.convertToDuration(operand)._rational)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__imul__(self._staff_reference.convertToDuration(operand)._rational)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Convertible() | ou.TimeUnit():
                super().__itruediv__(self._staff_reference.convertToDuration(operand)._rational)
            case _:
                super().__itruediv__(operand)
        return self


# NoteValue as an Alias to Duration
NoteValue = Duration

class Dotted(Duration):
    """
    A Dotted() represents the Note Value of a Dotted Note, a Dotted Note Value typically comes as 1/4* and 1/8*.
    Dots are equivalent to the following Note Values:
        | 1*    = (1    + 1/2)   = 3/2
        | 1/2*  = (1/2  + 1/4)   = 3/4
        | 1/4*  = (1/4  + 1/8)   = 3/8
        | 1/8*  = (1/8  + 1/16)  = 3/16
        | 1/16* = (1/16 + 1/32)  = 3/32
        | 1/32* = (1/32 + 1/64)  = 3/64
    
    Parameters
    ----------
    first : float_like
        Note Value as 1, 1/2, 1/4, 1/8, 1/16, 1/32
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
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource() | Duration() | od.Serialization():
                super().__lshift__(operand)
            # It's just a wrapper for NoteValue 3/2
            case int() | float() | Fraction():
                super().__lshift__(operand) # Starts by setting the self._rational as NoteValue
                # Then it's multiplied by 3/2 because it's a Dotted Note
                self._rational = self._rational * 3 / 2 # Retains the Fraction
                # DON'T DO THIS: "self._rational *= 3/2"
            case _:
                if not isinstance(operand, (Rational, ou.Unit)):
                    super().__lshift__(operand)
        return self

class Swing(Rational):
    pass

class Gate(Rational):
    pass

class Amplitude(Rational):
    pass

class Offset(Rational):
    pass

