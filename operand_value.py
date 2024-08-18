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
from typing import Union
# Json Midi Creator Libraries
from operand import Operand
import operand_staff as os
import operand_numeric as on
import operand_unit as ou
import operand_frame as of
import operand_tag as ot


class Value(on.Numeric):
    """
    This is a read only type of Operand that has associated a Rational number.
    This class is intended to represent time based variables that are ratios like the typical 1/4 note value

    Parameters
    ----------
    first : float_like
        A read only Rational described as a Value
    """
    def __init__(self, value: float = None):
        self._value: float = 0.0
        self._value = os.global_staff % self % float() if value is None else round(1.0 * value, 12)  # rounding to 9 avoids floating-point errors

    def __mod__(self, operand: Operand) -> Operand:
        """
        The % symbol is used to extract the Value, because a Value is an Rational
        it should be used in conjugation with float(). If used with a int() it
        will return the respective rounded value as int().

        Examples
        --------
        >>> note_value_float = NoteValue(1/4) % float()
        >>> print(note_value_float)
        0.25
        """
        match operand:
            case of.Frame():    return self % (operand % Operand())
            case float():       return round(1.0 * self._value, 12)  # rounding to 9 avoids floating-point errors
            case int():         return round(self._value)
            case _:             return ot.Null()

    def __eq__(self, other_value: 'Value') -> bool:
        return self % float() == other_value % float()
    
    def __lt__(self, other_value: 'Value') -> bool:
        return self % float() < other_value % float()
    
    def __gt__(self, other_value: 'Value') -> bool:
        return self % float() > other_value % float()
    
    def __le__(self, other_value: 'Value') -> bool:
        return not (self > other_value)
    
    def __ge__(self, other_value: 'Value') -> bool:
        return not (self < other_value)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "value": self._value
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "value" in serialization):

            self._value = serialization["value"]
        return self

    def copy(self) -> 'Value':
        return self.__class__(self._value)

    def __lshift__(self, operand: Operand) -> 'Value':
        match operand:
            case Value():           self._value = operand % float()
            case float() | int():   self._value = round(1.0 * operand, 12)
        return self

    def __add__(self, value: Union['Value', float, int]) -> 'Value':
        match value:
            case Value(): return self.__class__(self % float() + value % float())
            case float() | int(): return self.__class__(self % float() + value)
            case ot.Null(): return ot.Null()
        return self
    
    def __sub__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value(): return self.__class__(self % float() - value % float())
            case float() | int(): return self.__class__(self % float() - value)
            case ot.Null(): return ot.Null()
        return self
    
    def __mul__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value(): return self.__class__((self % float()) * (value % float()))
            case float() | int(): return self.__class__(self % float() * value)
            case ot.Null(): return ot.Null()
        return self
    
    def __truediv__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value():
                if value % float() != 0:
                    return self.__class__((self % float()) / (value % float()))
            case float() | int():
                if value != 0:
                    return self.__class__(self % float() / value)
            case ot.Null(): return ot.Null()
        return self

class Quantization(Value):
    """
    Play() allows to send a given Element to the Player directly without the need of Exporting to the respective .json Player file.
    
    Parameters
    ----------
    first : float_like
        By default it's configured without any verbose, set to 1 or True to enable verbose
    """
    def __init__(self, quantization: float = None):
        super().__init__(quantization)

class BeatsPerMeasure(Value):
    """
    BeatsPerMeasure() sets the top value of a time signature, in a 3/4 time signature 3 are the Beats per Measure.
    
    Parameters
    ----------
    first : float_like
        Time signature Beats per Measure, 3 for 3/4 or 4 for 4/4 
    """
    def __init__(self, beats_per_measure: float = None):
        super().__init__(beats_per_measure)

class BeatNoteValue(Value):
    """
    BeatNoteValue() sets the Note Value for the Beat, in a 3/4 time signature 1/4 is the Beats Note Value.
    
    Parameters
    ----------
    first : float_like
        Time signature Beat Note Value, 1/4 for 3/4 or 1/8 for 4/8 
    """
    def __init__(self, beat_note_value: float = None):
        super().__init__(beat_note_value)

class NotesPerMeasure(Value):
    """
    NotesPerMeasure() gets how many notes in a Measure and sets the Note Value of a Beat.
    
    Parameters
    ----------
    first : float_like
        Represents 1 Note for a time signature of 4/4 and 1/2 Note for a time signature of 4/8 
    """
    def __init__(self, notes_per_measure: float = None):
        super().__init__(notes_per_measure)

class StepsPerMeasure(Value):
    """
    StepsPerMeasure() is another way of getting and setting the Quantization.
    16 Steps per Measure means a Quantization of 1/16 in a Time Signature of 4/4.
    
    Parameters
    ----------
    first : float_like
        How many Steps in a Measure
    """
    def __init__(self, steps_per_measure: float = None):
        super().__init__(steps_per_measure)

class StepsPerNote(Value):
    """
    StepsPerNote() is simply the inverse value of the Quantization, like, 16 for 1/16.
    
    Parameters
    ----------
    first : float_like
        The inverse of the Quantization value
    """
    def __init__(self, steps_per_note: float = None):
        super().__init__(steps_per_note)

class Tempo(Value):
    """
    Tempo() represents the Beats per Minute (BPM).
    
    Parameters
    ----------
    first : float_like
        Beats per Minute
    """
    def __init__(self, tempo: int = None):
        super().__init__(tempo)

class TimeUnit(Value):
    """
    TimeUnit() represents any Time Length variables, namely, Measure, Beat, NoteValue and Step.
    
    Parameters
    ----------
    first : float_like
        Not intended to be set directly
    """
    def __init__(self, value: float = None):
        value = 0 if value is None else round(1.0 * value, 12)  # rounding to 9 avoids floating-point errors
        super().__init__(value)

class Measure(TimeUnit):
    """
    Measure() represents the Staff Time Length in Measures, also known as Bar.
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Measure on the Staff
    """
    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return Beat(1).getTime_ms() * (os.global_staff % BeatsPerMeasure() % float()) * self._value
     
class Beat(TimeUnit):
    """
    A Beat() represents the Staff Time Length in Beat on which the Tempo is based on (BPM).
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Beat on the Staff
    """
    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return 60.0 * 1000 / (os.global_staff % Tempo() % float()) * self._value
    
class NoteValue(TimeUnit):
    """
    NoteValue() represents the Duration of a Note, a Note Value typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    first : float_like
        Note Value as 1, 1/2, 1/4, 1/8, 1/16, 1/32
    """
    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return Beat(1).getTime_ms() / (os.global_staff % BeatNoteValue() % float()) * self._value

class Dotted(NoteValue):
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
    def __init__(self, value: float = None):
        super().__init__(value)

    def __mod__(self, operand: Operand) -> Operand:
        """
        The % symbol is used to extract the Value, because a Value is an Rational
        it should be used in conjugation with float(). If used with a int() it
        will return the respective rounded value as int().

        Examples
        --------
        >>> note_value_float = Dotted(1/4) % float()
        >>> print(note_value_float)
        0.375
        """
        match operand:
            case of.Frame():    return self % (operand % Operand())
            case float():       return round(1.0 * self._value * (3/2), 12)  # rounding to 9 avoids floating-point errors
            case int():         return round(self._value * (3/2))
            case _:             return ot.Null()

class Step(TimeUnit):
    """
    A Step() represents the Length given by the Quantization, normally 1/16 Note Value.
    
    Parameters
    ----------
    first : float_like
        Steps as 1, 2, 4, 8
    """
    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return NoteValue(1).getTime_ms() / (os.global_staff % StepsPerNote() % float()) * self._value
    
class Swing(Value):
    def __init__(self, swing: float = None):
        super().__init__( 0.50 if swing is None else swing )

class Gate(Value):
    def __init__(self, gate: float = None):
        super().__init__( 0.90 if gate is None else gate )

