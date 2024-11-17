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
from fractions import Fraction
import re
# Json Midi Creator Libraries
import operand as o
import operand_staff as os

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
    def __init__(self, *parameters):
        super().__init__()
        self._rational: Fraction = Fraction(0).limit_denominator()
        if len(parameters) > 0:
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
                    case ou.Integer():      return ou.Integer() << od.DataSource( self._rational )
                    case Float():           return Float() << od.DataSource( self._rational )
                    case Rational():        return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Fraction():        return self._rational
            case float():           return float(self._rational)
            case int():             return int(self._rational)
            case str():             return str(self._rational)
            case ou.Integer():      return ou.Integer() << self._rational
            case Float():           return Float() << self._rational
            case Rational():        return self.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_number: any) -> bool:
        other_number = self & other_number    # Processes the tailed self operands or the Frame operand if any exists
        match other_number:
            case Rational() | ou.Unit():
                return self._rational == other_number % od.DataSource( Fraction() )
            case int() | float():
                other_rational = Fraction( other_number ).limit_denominator()
                return self._rational == other_rational
            case _:
                if other_number.__class__ == o.Operand:
                    return True
        return False
    
    def __lt__(self, other_number: any) -> bool:
        other_number = self & other_number    # Processes the tailed self operands or the Frame operand if any exists
        match other_number:
            case Rational() | ou.Unit():
                return self._rational < other_number % od.DataSource( Fraction() )
            case int() | float():
                other_rational = Fraction( other_number ).limit_denominator()
                return self._rational < other_rational
        return False
    
    def __gt__(self, other_number: any) -> bool:
        other_number = self & other_number    # Processes the tailed self operands or the Frame operand if any exists
        match other_number:
            case Rational() | ou.Unit():
                return self._rational > other_number % od.DataSource( Fraction() )
            case int() | float():
                other_rational = Fraction( other_number ).limit_denominator()
                return self._rational > other_rational
        return False
    
    def __le__(self, other_number: any) -> bool:
        return self == other_number or self < other_number
    
    def __ge__(self, other_number: any) -> bool:
        return self == other_number or self > other_number
    
    def __str__(self):
        return f'{self._rational}'
    
    def getSerialization(self) -> dict:
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "fraction": str(self._rational),
                "float": float(self._rational)
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "fraction" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._rational = Fraction(serialization["parameters"]["fraction"]).limit_denominator()
        return self

    def __lshift__(self, operand: o.Operand) -> 'Rational':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Fraction():                self._rational = operand % o.Operand()
                    case float() | int() | str():   self._rational = Fraction(operand % o.Operand()).limit_denominator()
                    case Float() | ou.Integer():    self._rational = operand % o.Operand() % od.DataSource( Fraction() )
            case Rational():
                super().__lshift__(operand)
                self._rational = operand._rational
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Fraction():                self._rational = operand
            case float() | int() | str():   self._rational = Fraction(operand).limit_denominator()
            case ou.Integer():              self._rational = operand % Fraction()
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __add__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                return self.__class__() << od.DataSource( self._rational + value % od.DataSource( Fraction() ) )
            case Fraction():        return self.__class__() << od.DataSource( self._rational + value )
            case float() | int():   return self.__class__() << od.DataSource( self._rational + Fraction(value).limit_denominator() )
        return self.copy()
    
    def __sub__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                return self.__class__() << od.DataSource( self._rational - value % od.DataSource( Fraction() ) )
            case Fraction():        return self.__class__() << od.DataSource( self._rational - value )
            case float() | int():   return self.__class__() << od.DataSource( self._rational - Fraction(value).limit_denominator() )
        return self.copy()
    
    def __mul__(self, value: Union['Rational', 'ou.Unit', Fraction, float, int]) -> 'Rational':
        value = self & value    # Processes the tailed self operands or the Frame operand if any exists
        match value:
            case Rational() | ou.Unit():
                return self.__class__() << od.DataSource( self._rational * (value % od.DataSource( Fraction() )) )
            case Fraction():        return self.__class__() << od.DataSource( self._rational * value )
            case float() | int():   return self.__class__() << od.DataSource( self._rational * Fraction(value).limit_denominator() )
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
                if Fraction(value).limit_denominator() != 0:
                    return self.__class__() << od.DataSource( self._rational / Fraction(value).limit_denominator() )
        return self.copy()

class Float(Rational):
    pass

class Index(Rational):
    pass

class Split(Rational):
    pass

class Width(Rational):
    pass

class Height(Rational):
    pass

class X(Rational):
    pass

class Y(Rational):
    pass

class Z(Rational):
    pass

class dX(Rational):
    pass

class dY(Rational):
    pass

class dZ(Rational):
    pass

class X0(Rational):
    pass

class Xn(Rational):
    pass

class Lambda(Rational):
    pass

class Negative(Rational):
    def __init__(self, value: float = None):
        super().__init__(value * (-1))

class Quantization(Rational):
    """
    Play() allows to send a given Element to the Player directly without the need of Exporting to the respective .json Player file.
    
    Parameters
    ----------
    first : float_like
        By default it's configured without any verbose, set to 1 or True to enable verbose
    """
    def __init__(self, value: float = None):
        super().__init__(value)

class BeatsPerMeasure(Rational):
    """
    BeatsPerMeasure() sets the top value of a time signature, in a 3/4 time signature 3 are the Beats per Measure.
    
    Parameters
    ----------
    first : float_like
        Time signature Beats per Measure, 3 for 3/4 or 4 for 4/4 
    """
    def __init__(self, value: float = None):
        super().__init__(value)

class BeatNoteValue(Rational):
    """
    BeatNoteValue() sets the Note Value for the Beat, in a 3/4 time signature 1/4 is the Beats Note Value.
    
    Parameters
    ----------
    first : float_like
        Time signature Beat Note Value, 1/4 for 3/4 or 1/8 for 4/8 
    """
    def __init__(self, value: float = None):
        super().__init__(value)

class NotesPerMeasure(Rational):
    """
    NotesPerMeasure() gets how many notes in a Measure and sets the Note Value of a Beat.
    
    Parameters
    ----------
    first : float_like
        Represents 1 Note for a time signature of 4/4 and 1/2 Note for a time signature of 4/8 
    """
    def __init__(self, value: float = None):
        super().__init__(value)

class StepsPerMeasure(Rational):
    """
    StepsPerMeasure() is another way of getting and setting the Quantization.
    16 Steps per Measure means a Quantization of 1/16 in a Time Signature of 4/4.
    
    Parameters
    ----------
    first : float_like
        How many Steps in a Measure
    """
    def __init__(self, value: float = None):
        super().__init__(value)

class StepsPerNote(Rational):
    """
    StepsPerNote() is simply the inverse value of the Quantization, like, 16 for 1/16.
    
    Parameters
    ----------
    first : float_like
        The inverse of the Quantization value
    """
    def __init__(self, value: float = None):
        super().__init__(value)

class Tempo(Rational):
    """
    Tempo() represents the Beats per Minute (BPM).
    
    Parameters
    ----------
    first : float_like
        Beats per Minute
    """
    def __init__(self, value: int = None):
        super().__init__(value)

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

class TimeUnit(Rational):
    """
    TimeUnit() represents any Time Length variables, namely, Measure, Beat, NoteValue and Step.
    
    Parameters
    ----------
    first : float_like
        Not intended to be set directly
    """
    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
            self << parameters

    def getTime_rational(self) -> Fraction:
        return self._rational * 0
    
    def __eq__(self, other_time_unit: any) -> bool:
        match other_time_unit:
            case TimeUnit():
                self_class_time_unit = other_time_unit % od.DataSource( self )
                return self._rational == self_class_time_unit % od.DataSource( Fraction() )
            case _: return super().__eq__(other_time_unit)
        return False
    
    def __lt__(self, other_time_unit: any) -> bool:
        match other_time_unit:
            case TimeUnit():
                self_class_time_unit = other_time_unit % od.DataSource( self )
                return self._rational < self_class_time_unit % od.DataSource( Fraction() )
            case _: return super().__lt__(other_time_unit)
        return False
    
    def __gt__(self, other_time_unit: any) -> bool:
        match other_time_unit:
            case TimeUnit():
                self_class_time_unit = other_time_unit % od.DataSource( self )
                return self._rational > self_class_time_unit % od.DataSource( Fraction() )
            case _: return super().__gt__(other_time_unit)
        return False

    def __str__(self):
        return f'{type(self).__name__}: {self % Fraction()}'
    
    # CHAINABLE OPERATIONS

    def __add__(self, other_time_unit: 'TimeUnit') -> 'TimeUnit':
        other_time_unit = self & other_time_unit    # Processes the tailed self operands or the Frame operand if any exists
        match other_time_unit:
            case TimeUnit():
                self_class_time_unit = other_time_unit % od.DataSource( self )
                return self.__class__() << od.DataSource( self._rational + self_class_time_unit % od.DataSource( Fraction() ) )
            case _: return super().__add__(other_time_unit)
    
    def __sub__(self, other_time_unit: 'TimeUnit') -> 'TimeUnit':
        other_time_unit = self & other_time_unit    # Processes the tailed self operands or the Frame operand if any exists
        match other_time_unit:
            case TimeUnit():
                self_class_time_unit = other_time_unit % od.DataSource( self )
                return self.__class__() << od.DataSource( self._rational - self_class_time_unit % od.DataSource( Fraction() ) )
            case _: return super().__sub__(other_time_unit)
    
    def __mul__(self, other_time_unit: 'TimeUnit') -> 'TimeUnit':
        other_time_unit = self & other_time_unit    # Processes the tailed self operands or the Frame operand if any exists
        match other_time_unit:
            case Gate() | Swing() | ou.Division():
                return self.__class__() << od.DataSource( self._rational * (other_time_unit % od.DataSource( Fraction() )) )
            case TimeUnit():
                self_class_time_unit = other_time_unit % od.DataSource( self )
                return self.__class__() << od.DataSource( self._rational * (self_class_time_unit % od.DataSource( Fraction() )) )
            case _: return super().__mul__(other_time_unit)
    
    def __truediv__(self, other_time_unit: 'TimeUnit') -> 'TimeUnit':
        other_time_unit = self & other_time_unit    # Processes the tailed self operands or the Frame operand if any exists
        match other_time_unit:
            case Gate() | Swing() | ou.Division():
                if other_time_unit % od.DataSource( Fraction() ) != 0:
                    return self.__class__() << od.DataSource( self._rational / (other_time_unit % od.DataSource( Fraction() )) )
            case TimeUnit():
                self_class_time_unit = other_time_unit % od.DataSource( self )
                if self_class_time_unit % od.DataSource( Fraction() ) != 0:
                    return self.__class__() << od.DataSource( self._rational / (self_class_time_unit % od.DataSource( Fraction() )) )
            case _: return super().__truediv__(other_time_unit)

class Measure(TimeUnit):
    """
    Measure() represents the Staff Time Length in Measures, also known as Bar.
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Measure on the Staff
    """
    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
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
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Measure():         return self
                    case Beat():            return Beat() << od.DataSource(
                                                    self._rational * \
                                                        (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction())
                                                )
                    case Step():            return Step() << od.DataSource(
                                                    self._rational * \
                                                        (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction())
                                                )
                    case NoteValue():       return NoteValue() << od.DataSource(
                                                    self._rational * \
                                                        (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction())
                                                )
                    case _:                 return super().__mod__(operand)
            case Measure():         return self.copy()
            case Beat():            return Beat() << self._rational * \
                                                        (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction())
            case Step():            return Step() << self._rational * \
                                                        (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction())
            case NoteValue():       return NoteValue() << self._rational * \
                                                        (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction())
            case _:                 return super().__mod__(operand)

    def getTime_rational(self) -> Fraction:
        return self._rational * Beat(1).getTime_rational() * (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction())

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Measure':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    # case Measure():
                    #     self._rational = operand % o.Operand() % od.DataSource( Fraction() )
                    case Beat():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) / \
                            (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction())
                    case Step():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) / \
                            (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction())
                    case NoteValue():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) / \
                            (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction())
                    case _: super().__lshift__(operand)
            # case Measure():
            #     self._rational = operand % o.Operand() % Fraction()
            case Beat():
                self._rational = int(self._rational) + operand._rational / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction())
            case Step():
                self._rational = int(self._rational) + operand._rational / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction())
            case NoteValue():
                self._rational = operand._rational / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction())
            case _: super().__lshift__(operand)
        return self

class Beat(TimeUnit):
    """
    A Beat() represents the Staff Time Length in Beat on which the Tempo is based on (BPM).
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Beat on the Staff
    """
    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Beat,
        those Parameters are the Beat length as a Fraction(), a float() an int()
        or even other type of time units, like Measure and Step with the respective conversion.

        Examples
        --------
        >>> beat = Beat(1)
        >>> beat % NoteValue() % float() >> Print()
        0.25
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Measure():         return Measure() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
                                                )
                    case Beat():            return self
                    case Step():            return Step() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
                                                )
                    case NoteValue():       return NoteValue() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
                                                )
                    case _:                 return super().__mod__(operand)
            case Measure():         return Measure() << self._rational / \
                                                        ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
            case Beat():            return self.copy()
            case Step():            return Step() << self._rational / \
                                                        ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
            case NoteValue():       return NoteValue() << self._rational / \
                                                        ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
            case _:                 return super().__mod__(operand)

    def getTime_rational(self) -> Fraction:
        # Because the multiplication (*) is done with integers, 60 and 1000, the Fractions remain as Fraction
        return self._rational / (os.staff % od.DataSource( Tempo() ) % Fraction()) * 60 * 1000

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Beat':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Measure():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
                    case Step():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) \
                            / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
                    case NoteValue():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) \
                            / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
                    case _: super().__lshift__(operand)
            case Measure():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
            case Step():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) \
                    / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
            case NoteValue():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) \
                    / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
            case _: super().__lshift__(operand)
        return self

class Step(TimeUnit):
    """
    A Step() represents the Length given by the Quantization, normally 1/16 Note Value.
    
    Parameters
    ----------
    first : float_like
        Steps as 1, 2, 4, 8
    """
    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Step,
        those Parameters are the Step length as a Fraction(), a float() an int()
        or even other type of time units, like Measure and Step with the respective
        conversion accordingly to the set Quantization.

        Examples
        --------
        >>> step = Step(1)
        >>> step % NoteValue() % Fraction() >> Print()
        1/16
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Measure():         return Measure() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
                                                )
                    case Beat():            return Beat() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
                                                )
                    case Step():            return self
                    case NoteValue():       return NoteValue() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
                                                )
                    case _:                 return super().__mod__(operand)
            case Measure():         return Measure() << self._rational / \
                                                        ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
            case Beat():            return Beat() << self._rational / \
                                                        ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
            case Step():            return self.copy()
            case NoteValue():       return NoteValue() << self._rational / \
                                                        ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
            case _:                 return super().__mod__(operand)

    def getTime_rational(self) -> Fraction:
        return self._rational * NoteValue(1).getTime_rational() / (os.staff % StepsPerNote() % Fraction())

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Step':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Measure():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
                    case Beat():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) \
                            / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
                    case NoteValue():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) \
                            / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
                    case _: super().__lshift__(operand)
            case Measure():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
            case Beat():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) \
                    / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
            case NoteValue():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) \
                    / (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
            case _: super().__lshift__(operand)
        return self

class NoteValue(TimeUnit):
    """
    NoteValue() represents the Duration of a Note, a Note Value typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    first : float_like
        Note Value as 1, 1/2, 1/4, 1/8, 1/16, 1/32
    """
    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a NoteValue,
        those Parameters are the NoteValue length as a Fraction(), a float() an int()
        or even other type of time units, like Measure and Beat with the respective
        conversion accordingly to the note value of set time signature.

        Examples
        --------
        >>> note_value = NoteValue(1)
        >>> note_value % Beat() % Fraction() >> Print()
        4
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Measure():         return Measure() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
                                                )
                    case Beat():            return Beat() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
                                                )
                    case Step():            return Step() << od.DataSource(
                                                    self._rational / \
                                                        ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
                                                )
                    case NoteValue():       return self
                    case _:                 return super().__mod__(operand)
            case Measure():         return Measure() << self._rational / \
                                                        ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
            case Beat():            return Beat() << self._rational / \
                                                        ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
            case Step():            return Step() << self._rational / \
                                                        ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) \
                                                        / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
            case NoteValue():       return self.copy()
            case _:                 return super().__mod__(operand)

    def getTime_rational(self) -> Fraction:
        return self._rational * Beat(1).getTime_rational() / (os.staff % od.DataSource( BeatNoteValue() ) % Fraction())
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'NoteValue':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Measure():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
                    case Beat():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) \
                            / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
                    case Step():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() ) * \
                            ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) \
                            / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
                    case _: super().__lshift__(operand)
            case Measure():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) )
            case Beat():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) \
                    / (os.staff % od.DataSource( BeatsPerMeasure() ) % Fraction()) )
            case Step():
                self._rational = operand % Fraction() * \
                    ( (os.staff % od.DataSource( NotesPerMeasure() ) % Fraction()) \
                    / (os.staff % od.DataSource( StepsPerMeasure() ) % Fraction()) )
            case _: super().__lshift__(operand)
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
    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
            self << parameters

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
            case od.DataSource():
                match operand % o.Operand():
                    case NoteValue():       return NoteValue() << self._rational
                    case _:                 return super().__mod__(operand)
            case Fraction():        return self._rational * 2/3
            case float():           return float(self._rational * 2/3)
            case int():             return int(self._rational * 2/3)
            case Dotted():          return self.copy()
            case Float():           return ou.Unit() << self._rational * 2/3
            case ou.Integer():      return ou.Unit() << self._rational * 2/3
            case NoteValue():       return NoteValue() << self._rational
            case _:                 return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Rational':
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
            case float() | int():   self._rational = Fraction(operand).limit_denominator() * 3/2
            case ou.Integer() | Float():
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

