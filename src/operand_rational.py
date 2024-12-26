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
from typing import Union, TypeVar, TYPE_CHECKING
from fractions import Fraction
import re
# Json Midi Creator Libraries
import operand as o
import operand_staff as os

import operand_unit as ou
import operand_data as od
import operand_frame as of
import operand_label as ol

TypeRational = TypeVar('TypeRational', bound='Rational')  # TypeRational represents any subclass of Operand


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
        super().__init__()
        self._rational: Fraction = Fraction(0)
        if parameters:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
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
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case Fraction():        return self._rational           # returns a Fraction()
                    case float():           return float(self._rational)
                    case int():             return int(self._rational)
                    case str():             return str(self._rational)
                    case ou.IntU():         return ou.IntU() << od.DataSource( self._rational )
                    case FloatR():          return FloatR() << od.DataSource( self._rational )
                    case Rational():        return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Fraction():        return self._rational
            case float():           return float(self._rational)
            case int():             return int(self._rational)
            case str():             return str(self._rational)
            case ou.IntU():         return ou.IntU() << self._rational
            case FloatR():          return FloatR() << self._rational
            case Rational():        return self.copy()
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

    def __lshift__(self, operand: o.Operand) -> 'Rational':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Fraction():
                        self._rational = operand % o.Operand()
                    case float() | int():
                        self._rational = Fraction(operand % o.Operand())
                    case str():
                        try:
                            self._rational = Fraction(operand % o.Operand())
                        except ValueError as e:
                            print(f"Error: {e}, '{operand % o.Operand()}' is not a number!")
                    case FloatR() | ou.IntU():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() )
            case Rational():
                super().__lshift__(operand)
                self._rational = operand._rational
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Fraction():                self._rational = operand
            case float() | int() | str():   self << od.DataSource( operand )
            case ou.IntU():                 self._rational = operand % Fraction()
            case tuple():
                for single_operand in operand:
                    self << single_operand
        if self._limit_denominator > 0:
            self._rational = Fraction(self._rational).limit_denominator(self._limit_denominator)
        return self

    def __add__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                return self.__class__() << od.DataSource( self._rational + value % od.DataSource( Fraction() ) )
            case Fraction():        return self.__class__() << od.DataSource( self._rational + value )
            case float() | int():
                return self.__class__() << od.DataSource( self._rational + Fraction(value) )
        return self.copy()
    
    def __sub__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                return self.__class__() << od.DataSource( self._rational - value % od.DataSource( Fraction() ) )
            case Fraction():        return self.__class__() << od.DataSource( self._rational - value )
            case float() | int():
                return self.__class__() << od.DataSource( self._rational - Fraction(value) )
        return self.copy()
    
    def __mul__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                return self.__class__() << od.DataSource( self._rational * (value % od.DataSource( Fraction() )) )
            case Fraction():        return self.__class__() << od.DataSource( self._rational * value )
            case float() | int():
                return self.__class__() << od.DataSource( self._rational * Fraction(value) )
        return self.copy()
    
    def __truediv__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                if value % od.DataSource( Fraction() ) != 0:
                    return self.__class__() << od.DataSource( self._rational / (value % od.DataSource( Fraction() )) )
            case Fraction():
                if value != 0: return self.__class__() << od.DataSource( self._rational / value )
            case float() | int():
                if Fraction(value) != 0:
                    return self.__class__() << od.DataSource( self._rational / Fraction(value) )
        return self.copy()

class FloatR(Rational):

    _limit_denominator: int = 0 # overrides default limit_denominator

    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
            self << parameters

class Index(FloatR):
    pass

class Split(FloatR):
    pass

class Width(FloatR):
    pass

class Height(FloatR):
    pass

class X(FloatR):
    pass

class Y(FloatR):
    pass

class Z(FloatR):
    pass

class dX(FloatR):
    pass

class dY(FloatR):
    pass

class dZ(FloatR):
    pass

class X0(FloatR):
    pass

class Xn(FloatR):
    pass

class Lambda(FloatR):
    pass

class Negative(Rational):
    def __init__(self, value: float = None):
        super().__init__(0 if value is None else value * (-1))

class RationalDefault(Rational):
    pass

class Quantization(Rational):
    """
    Play() allows to send a given Element to the Player directly without the need of Exporting to the respective .json Player file.
    
    Parameters
    ----------
    first : float_like
        By default it's configured without any verbose, set to 1 or True to enable verbose
    """
    pass

class BeatsPerMeasure(Rational):
    """
    BeatsPerMeasure() sets the top value of a time signature, in a 3/4 time signature 3 are the Beats per Measure.
    
    Parameters
    ----------
    first : float_like
        Time signature Beats per Measure, 3 for 3/4 or 4 for 4/4 
    """
    pass

class BeatNoteValue(Rational):
    """
    BeatNoteValue() sets the Note Value for the Beat, in a 3/4 time signature 1/4 is the Beats Note Value.
    
    Parameters
    ----------
    first : float_like
        Time signature Beat Note Value, 1/4 for 3/4 or 1/8 for 4/8 
    """
    pass

class NotesPerMeasure(Rational):
    """
    NotesPerMeasure() gets how many notes in a Measure and sets the Note Value of a Beat.
    
    Parameters
    ----------
    first : float_like
        Represents 1 Note for a time signature of 4/4 and 1/2 Note for a time signature of 4/8 
    """
    pass

class StepsPerMeasure(Rational):
    """
    StepsPerMeasure() is another way of getting and setting the Quantization.
    16 Steps per Measure means a Quantization of 1/16 in a Time Signature of 4/4.
    
    Parameters
    ----------
    first : float_like
        How many Steps in a Measure
    """
    pass

class StepsPerNote(Rational):
    """
    StepsPerNote() is simply the inverse value of the Quantization, like, 16 for 1/16.
    
    Parameters
    ----------
    first : float_like
        The inverse of the Quantization value
    """
    pass

class Tempo(Rational):
    """
    Tempo() represents the Beats per Minute (BPM).
    
    Parameters
    ----------
    first : float_like
        Beats per Minute
    """

    def __mod__(self, operand: o.Operand) -> o.Operand:
        import operand_rational as ra
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case Fraction():        return self._rational
                    case float():           return float(self._rational)
                    case int():             return int(self._rational)
                    case FloatR():          return FloatR(self._rational)
                    case ou.IntU():         return ou.IntU(self._rational)
                    case Rational():        return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Fraction():        return self._rational
            case float():           return float(self._rational)
            case int():             return int(self._rational)
            case FloatR():          return FloatR(self._rational)
            case ou.IntU():         return ou.IntU(self._rational)
            case Rational():        return self.copy()
            case _:                 return super().__mod__(operand)
             
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Rational':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                # r"\W(.)\1\W" vs "\\W(.)\\1\\W"
                tempo = re.findall(r"\d+(?:\.\d+)?", operand)
                if len(tempo) > 0:
                    self << float(tempo[0])
            case _: super().__lshift__(operand)
        return self






class Time(Rational):
    def __init__(self, *parameters):
        super().__init__()
        self._time_value    = TimeValue()
        if parameters:
            self << parameters

    def time(self: 'Time', beats: float = None) -> 'Time':
        return self << od.DataSource( beats )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Time,
        those Parameters are the respective time unit, like Measure and NoteValue,
        where Position and Length have a Measure while a Duration has a NoteValue.

        Examples
        --------
        >>> position = Position(4.5)
        >>> position % Measure() % float() >> Print()
        4.0
        >>> position % Beat() % float() >> Print()
        2.0
        >>> position % Step() % float() >> Print()
        8.0
        """
        import operand_generic as og
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case TimeValue() | int() | float() | Fraction() | ou.IntU() | FloatR() | Tempo() | og.TimeSignature() | Quantization():
                                            return self._time_value % operand
                    case Time():            return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Measures():
                return Measures(self._time_value)
            case Beats():
                return Beats(self._time_value)
            case Steps():
                return Steps(self._time_value)
            case NoteValue():
                return NoteValue(self._time_value)
            case ou.TimeUnit() | int() | float() | Fraction() | ou.IntU() | FloatR() | Tempo() | og.TimeSignature() | Quantization():
                return self._time_value % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case TimeValue() | ou.TimeUnit():
                return self._time_value == other
            case Time():
                return self._time_value == other._time_value
            case _:
                if other.__class__ == o.Operand:
                    return True
        return False

    def __lt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case TimeValue() | ou.TimeUnit():
                return self._time_value < other
            case Time():
                return self._time_value < other._time_value
        return False
    
    def __gt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case TimeValue() | ou.TimeUnit():
                return self._time_value > other
            case Time():
                return self._time_value > other._time_value
        return False
    
    def __str__(self):
        return f'{self._time_value}'
    
    def getMillis_rational(self) -> Fraction:
        return self._time_value.getMillis_rational()
        
    def getMillis_float(self, rounded = True) -> float:
        if rounded:
            return round(float(self.getMillis_rational()), 3)
        return float(self.getMillis_rational())
        
    def getPlaylist(self, position: 'Position' = None) -> list:
        self_position: Position  = self + Position() if position is None else position
        
        return [
                {
                    "time_ms": self_position.getMillis_float()
                }
            ]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["time_value"] = self.serialize(self._time_value)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Time':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "time_value" in serialization["parameters"] and "class" in serialization["parameters"]["time_value"]):

            super().loadSerialization(serialization)
            self._time_value = self.deserialize(serialization["parameters"]["time_value"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Time':
        import operand_generic as og
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case TimeValue():
                        self._time_value = operand % o.Operand()
            case Time():
                super().__lshift__(operand)
                self._time_value         << operand._time_value
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case TimeValue() | ou.TimeUnit() | int() | ou.IntU() | Fraction() | float() | FloatR():
                self._time_value << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __add__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_value + operand % od.DataSource( TimeValue() ) % od.DataSource( self._time_value ) )
            case TimeValue():
                self_copy << od.DataSource( self._time_value + operand % od.DataSource( self._time_value ) )
            case int() | float() | ou.IntU() | FloatR() | Fraction():
                self_copy << od.DataSource( self._time_value + operand )
        return self_copy
    
    def __sub__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_value - operand % od.DataSource( TimeValue() ) % od.DataSource( self._time_value ) )
            case TimeValue():
                self_copy << od.DataSource( self._time_value - operand % od.DataSource( self._time_value ) )
            case int() | float() | ou.IntU() | FloatR() | Fraction():
                self_copy << od.DataSource( self._time_value - operand )
        return self_copy
    
    def __mul__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_value * (operand % od.DataSource( TimeValue() ) % od.DataSource( self._time_value )) )
            case TimeValue():
                self_copy << od.DataSource( self._time_value * (operand % od.DataSource( self._time_value )) )
            case int() | float() | ou.IntU() | FloatR() | Fraction():
                self_copy << od.DataSource( self._time_value * operand )
        return self_copy
    
    def __rmul__(self, operand: o.Operand) -> 'Time':
        return self * operand
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                if operand % od.DataSource( TimeValue() ) % od.DataSource( self._time_value ) != 0:
                    self_copy << od.DataSource( self._time_value / (operand % od.DataSource( TimeValue() ) % od.DataSource( self._time_value )) )
            case TimeValue():
                if operand % od.DataSource( self._time_value ) != 0:
                    self_copy << od.DataSource( self._time_value / (operand % od.DataSource( self._time_value )) )
            case int() | float() | ou.IntU() | FloatR() | Fraction():
                if operand != 0:
                    self_copy << od.DataSource( self._time_value / operand )
        return self_copy

    def __rtruediv__(self, operand: o.Operand) -> 'Time':
        return self / operand
    
    def start(self) -> 'TimeValue':
        return self.copy()

    def end(self) -> 'TimeValue':
        return self.copy()

    def minimum(self) -> 'TimeValue':
        return self._time_value % int()

    def maximum(self) -> 'TimeValue':
        return self._time_value % int() + 1


class Position(Time):
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: o.Operand) -> 'Position':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | ou.IntU():
                self._time_value << ou.Measure(operand)
            case Fraction() | float() | FloatR():
                self._time_value << Measures(operand)
            case _:
                super().__lshift__(operand)
        return self

class Length(Time):
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: o.Operand) -> 'Length':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | ou.IntU():
                self._time_value << ou.Measure(operand)
            case Fraction() | float() | FloatR():
                self._time_value << Measures(operand)
            case _:
                super().__lshift__(operand)
        return self
    
class Duration(Time):
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: o.Operand) -> 'Duration':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | ou.IntU() | Fraction() | float() | FloatR():
                self._time_value << NoteValue(operand)
            case _:
                super().__lshift__(operand)
        return self


















class TimeValue(Rational):  # Works as Absolute Beats
    """
    TimeUnit() represents any Time Length variables, namely, Measure, Beat, NoteValue and Step.
    
    Parameters
    ----------
    first : float_like
        Not intended to be set directly
    """
    def __init__(self, *parameters):
        import operand_generic as og
        super().__init__()
        if os.staff_available:
            self._tempo: Tempo                       = os.staff._tempo.copy()
            self._time_signature: og.TimeSignature   = os.staff._time_signature.copy()
            self._quantization: Quantization         = os.staff._quantization.copy()
        else:
            self._tempo: Tempo                       = Tempo(120.0)
            self._time_signature: og.TimeSignature   = og.TimeSignature(4, 4)
            self._quantization: Quantization         = Quantization(1/16)
        if parameters:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Measure,
        those Parameters are the Measure length as a Fraction(), a float() an int()
        or even other type of time units, like Beat and Step with the respective conversion.

        Examples
        --------
        >>> measure = Measure(1)
        >>> measure % Beat() % float() >> Print()
        4.0
        """
        import operand_generic as og
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Tempo():               return self._tempo
                    case og.TimeSignature():    return self._time_signature
                    case Quantization():        return self._quantization
                    case _:                     return super().__mod__(operand)
            case Tempo():               return self._tempo.copy()
            case og.TimeSignature():    return self._time_signature.copy()
            case Quantization():        return self._quantization.copy()
            # Conversion to Time Units
            case ou.Measure():          return ou.Measure(Measures(self) % Fraction())
            case ou.Beat():             return ou.Beat(Beats(self) % Fraction())
            case ou.Step():             return ou.Step(Steps(self) % Fraction())
            case _:                     return super().__mod__(operand)

    def getMillis_rational(self) -> Fraction:
        beats: Fraction = self._rational
        beats_per_minute: Fraction = self._tempo._rational
        return beats / beats_per_minute * 60 * 1000
    
    def __eq__(self, other: any) -> bool:
        match other:
            case TimeValue():
                self_class_time_unit = other % od.DataSource( self )
                return self._rational == self_class_time_unit % od.DataSource( Fraction() )
                # return self.getMillis_rational() == other.getMillis_rational()
            case ou.TimeUnit():
                return self % other == other
            case _: return super().__eq__(other)
        return False
    
    def __lt__(self, other: any) -> bool:
        match other:
            case TimeValue():
                self_class_time_unit = other % od.DataSource( self )
                return self._rational < self_class_time_unit % od.DataSource( Fraction() )
                # return self.getMillis_rational() < other.getMillis_rational()
            case ou.TimeUnit():
                return self % other < other
            case _: return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        match other:
            case TimeValue():
                self_class_time_unit = other % od.DataSource( self )
                return self._rational > self_class_time_unit % od.DataSource( Fraction() )
                # return self.getMillis_rational() > other.getMillis_rational()
            case ou.TimeUnit():
                return self % other > other
            case _: return super().__gt__(other)
        return False

    def __str__(self):
        return f'{type(self).__name__}: {self % Fraction()}'
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tempo"]            = self.serialize(self._tempo)
        serialization["parameters"]["time_signature"]   = self.serialize(self._time_signature)
        serialization["parameters"]["quantization"]     = self.serialize(self._quantization)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'TimeValue':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tempo" in serialization["parameters"] and "time_signature" in serialization["parameters"] and
            "quantization" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempo             = self.deserialize(serialization["parameters"]["tempo"])
            self._time_signature    = self.deserialize(serialization["parameters"]["time_signature"])
            self._quantization      = self.deserialize(serialization["parameters"]["quantization"])

        return self

    def __lshift__(self, operand: o.Operand) -> 'TimeValue':
        import operand_generic as og
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Tempo():               self._tempo             = operand % o.Operand()
                    case og.TimeSignature():    self._time_signature    = operand % o.Operand()
                    case Quantization():        self._quantization      = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case TimeValue():
                self._rational          = operand._rational
                self._tempo             << operand._tempo
                self._time_signature    << operand._time_signature
                self._quantization      << operand._quantization
            case Tempo():               self._tempo             << operand
            case og.TimeSignature():    self._time_signature    << operand
            case Quantization():        self._quantization      << operand
            case _:                     super().__lshift__(operand)
        return self

    def __add__(self, other: 'TimeValue') -> 'TimeValue':
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case TimeValue():
                self_class_time_unit = other % od.DataSource( self )
                return self.__class__() << od.DataSource( self._rational + self_class_time_unit % od.DataSource( Fraction() ) )
            case _: return super().__add__(other)
    
    def __sub__(self, other: 'TimeValue') -> 'TimeValue':
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case TimeValue():
                self_class_time_unit = other % od.DataSource( self )
                return self.__class__() << od.DataSource( self._rational - self_class_time_unit % od.DataSource( Fraction() ) )
            case _: return super().__sub__(other)
    
    def __mul__(self, other: 'TimeValue') -> 'TimeValue':
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Gate() | Swing() | ou.Division():
                return self.__class__() << od.DataSource( self._rational * (other % od.DataSource( Fraction() )) )
            case TimeValue():
                self_class_time_unit = other % od.DataSource( self )
                return self.__class__() << od.DataSource( self._rational * (self_class_time_unit % od.DataSource( Fraction() )) )
            case _: return super().__mul__(other)
    
    def __truediv__(self, other: 'TimeValue') -> 'TimeValue':
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Gate() | Swing() | ou.Division():
                if other % od.DataSource( Fraction() ) != 0:
                    return self.__class__() << od.DataSource( self._rational / (other % od.DataSource( Fraction() )) )
            case TimeValue():
                self_class_time_unit = other % od.DataSource( self )
                if self_class_time_unit % od.DataSource( Fraction() ) != 0:
                    return self.__class__() << od.DataSource( self._rational / (self_class_time_unit % od.DataSource( Fraction() )) )
            case _: return super().__truediv__(other)

class Measures(TimeValue):
    """
    Measure() represents the Staff Time Length in Measures, also known as Bar.
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Measure on the Staff
    """

    def __mod__(self, operand: o.Operand) -> o.Operand:
        beats_per_measure: Fraction = self._time_signature % BeatsPerMeasure() % Fraction()
        measures: Fraction = self._rational / beats_per_measure
        match operand:
            case Fraction():        return measures
            case float():           return float(measures)
            case int():             return int(measures)
            case str():             return str(measures)
            case ou.IntU():         return ou.IntU(measures)
            case FloatR():          return FloatR(measures)
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Measures':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        super().__lshift__(operand) # Starts by setting the typical TimeValue parameters
        beats_per_measure: Fraction = self._time_signature % BeatsPerMeasure() % Fraction()
        self._rational *= beats_per_measure
        return self

class Beats(TimeValue):
    """
    A Beat() represents the Staff Time Length in Beat on which the Tempo is based on (BPM).
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Beat on the Staff
    """

    def __mod__(self, operand: o.Operand) -> o.Operand:
        beats_per_beat: Fraction = Fraction(1).limit_denominator(self._limit_denominator)
        beats: Fraction = self._rational / beats_per_beat
        match operand:
            case Fraction():        return beats
            case float():           return float(beats)
            case int():             return int(beats)
            case str():             return str(beats)
            case ou.IntU():         return ou.IntU(beats)
            case FloatR():          return FloatR(beats)
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Beats':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        super().__lshift__(operand) # Starts by setting the typical TimeValue parameters
        beats_per_beat: Fraction = Fraction(1).limit_denominator(self._limit_denominator)
        self._rational *= beats_per_beat
        return self

class Steps(TimeValue):
    """
    A Step() represents the Length given by the Quantization, normally 1/16 Note Value.
    
    Parameters
    ----------
    first : float_like
        Steps as 1, 2, 4, 8
    """

    def __mod__(self, operand: o.Operand) -> o.Operand:
        notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
        notes_per_step: Fraction = self._quantization % Fraction()
        beats_per_step: Fraction = notes_per_step / notes_per_beat
        steps: Fraction = self._rational / beats_per_step
        match operand:
            case Fraction():        return steps
            case float():           return float(steps)
            case int():             return int(steps)
            case str():             return str(steps)
            case ou.IntU():         return ou.IntU(steps)
            case FloatR():          return FloatR(steps)
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Steps':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        super().__lshift__(operand) # Starts by setting the typical TimeValue parameters
        notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
        notes_per_step: Fraction = self._quantization % Fraction()
        beats_per_step: Fraction = notes_per_step / notes_per_beat
        self._rational *= beats_per_step
        return self

class NoteValue(TimeValue):
    """
    NoteValue() represents the Duration of a Note, a Note Value typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    first : float_like
        Note Value as 1, 1/2, 1/4, 1/8, 1/16, 1/32
    """

    def __mod__(self, operand: o.Operand) -> o.Operand:
        notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
        notes: Fraction = self._rational * notes_per_beat
        match operand:
            case Fraction():        return notes
            case float():           return float(notes)
            case int():             return int(notes)
            case str():             return str(notes)
            case ou.IntU():         return ou.IntU(notes)
            case FloatR():          return FloatR(notes)
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'NoteValue':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        super().__lshift__(operand) # Starts by setting the typical TimeValue parameters
        notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
        self._rational /= notes_per_beat
        return self

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

    def __mod__(self, operand: o.Operand) -> o.Operand:
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
            case Fraction():        return self._rational * 2/3
            case float():           return float(self._rational * 2/3)
            case int():             return int(self._rational * 2/3)
            case Dotted():          return self.copy()
            case FloatR():          return ou.Unit() << self._rational * 2/3
            case ou.IntU():         return ou.Unit() << self._rational * 2/3
            case NoteValue():       return NoteValue() << self._rational
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Dotted':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case NoteValue():
                        self._rational = operand % od.DataSource( Fraction() ) * 3/2
                    case _: super().__lshift__(operand)
            case Dotted():          super().__lshift__(operand)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            # It's just a wrapper for NoteValue 3/2
            case Fraction():        self._rational = operand * 3/2
            case float() | int():   self._rational = Fraction(operand).limit_denominator(self._limit_denominator) * 3/2
            case ou.IntU() | FloatR():
                                    self._rational = operand % Fraction() * 3/2
            case NoteValue():       self._rational = operand % Fraction()
            case _: super().__lshift__(operand)
        return self

class Swing(Rational):
    def __init__(self, value: float = None):
        super().__init__( 0.50 if value is None else value )

class Gate(Rational):
    def __init__(self, value: float = None):
        super().__init__( 0.90 if value is None else value )

class Amplitude(Rational):
    def __init__(self, value: float = None):
        super().__init__(value)

class Offset(Rational):
    def __init__(self, value: float = None):
        super().__init__(value)

