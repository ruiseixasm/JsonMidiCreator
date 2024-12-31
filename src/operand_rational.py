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
                    case Rational() | ou.Unit():
                                            return operand.__class__() << od.DataSource( self._rational )
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Fraction():        return self._rational
            case float():           return float(self._rational)
            case int():             return int(self._rational)
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
                    case Rational() | ou.Unit():
                        self._rational = operand % o.Operand() % od.DataSource( Fraction() )
            case Rational():
                super().__lshift__(operand)
                self._rational = operand._rational
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Fraction():                self._rational = operand
            case float() | int() | str():   self << od.DataSource( operand )
            case ou.Unit():
                self._rational = operand % Fraction()
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

class HiPrecision(Rational):

    _limit_denominator: int = 0 # overrides default limit_denominator

    def __init__(self, *parameters):
        super().__init__()
        if len(parameters) > 0:
            self << parameters

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
    def __init__(self, value: float = None):
        super().__init__(0 if value is None else value * (-1))

class RationalDefault(Rational):
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





class Span(Rational):
    def __init__(self, *parameters):
        import operand_generic as og
        super().__init__()
        self._tempo: Tempo                       = os.staff._tempo.copy()
        self._time_signature: og.TimeSignature   = os.staff._time_signature.copy()
        self._quantization: Quantization         = os.staff._quantization.copy()
        if parameters:
            self << parameters

    def time(self: 'Span', beats: float = None) -> 'Span':
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
                    case Tempo():               return self._tempo
                    case og.TimeSignature():    return self._time_signature
                    case Quantization():        return self._quantization
                    case _:                     return super().__mod__(operand)
            case Measures():            return self.getMeasures()
            case Beats():               return self.getBeats()
            case Steps():               return self.getSteps()
            case Duration():            return self.getDuration()
            case ou.Measure():          return self.getMeasure()
            case ou.Beat():             return self.getBeat()
            case ou.Step():             return self.getStep()
            case Tempo():               return self._tempo.copy()
            case og.TimeSignature():    return self._time_signature.copy()
            case BeatsPerMeasure() | BeatNoteValue() | NotesPerMeasure():
                                        return self._time_signature % operand
            case Quantization():        return self._quantization.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Span():
                return self == self.getBeats(other)
            case TimeValue() | ou.TimeUnit() | int() | float():
                return self % other == other
            case _:
                if other.__class__ == o.Operand:
                    return True
        return False

    def __lt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Span():
                return self < self.getBeats(other)
            case TimeValue() | ou.TimeUnit() | int() | float():
                return self % other < other
        return False
    
    def __gt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Span():
                return self > self.getBeats(other)
            case TimeValue() | ou.TimeUnit() | int() | float():
                return self % other > other
        return False
    
    def __str__(self):
        return f'Time Steps = {self._rational}'
    

    def getTime(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> 'Span':
        beats: Fraction = Fraction(0)
        match time_value:
            case None:
                return Span(self)
            case Span() | TimeValue() | ou.TimeUnit():
                time_beats: Beats = self.getBeats(time_value)
                return Span(time_beats)
        return Span(beats)

    def getMeasures(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> 'Measures':
        measures: Fraction = Fraction(0)
        match time_value:
            case None:
                return self.getMeasures(Beats(self._rational))
            case Span():
                time_beats: Beats = self.getBeats(time_value)
                return self.getMeasures(time_beats)
            case Measures():
                measures = time_value._rational
            case Beats():
                beats_per_measure: Fraction = self._time_signature % BeatsPerMeasure() % Fraction()
                measures = time_value._rational / beats_per_measure
            case Steps():
                beats = self.getBeats(time_value)
                measures = self.getMeasures(beats)
            case Duration():
                beats = self.getBeats(time_value)
                measures = self.getMeasures(beats)
            case ou.Measure():
                return self.getMeasures(Measures(time_value % Fraction()))
            case ou.Beat():
                return self.getMeasures(Beats(time_value % Fraction()))
            case ou.Step():
                return self.getMeasures(Steps(time_value % Fraction()))
        return Measures(measures)

    def getBeats(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> 'Beats':
        beats: Fraction = Fraction(0)
        match time_value:
            case None:
                return Beats(self._rational)
            case Span():
                # beats_b / tempo_b = beats_a / tempo_a => beats_b = beats_a * tempo_b / tempo_a
                beats_a : Fraction = time_value._rational
                tempo_a : Fraction = time_value._tempo._rational
                tempo_b : Fraction = self._tempo._rational
                beats_b : Fraction = beats_a * tempo_b / tempo_a
                return Beats(beats_b)
            case Measures():
                beats_per_measure: Fraction = self._time_signature % BeatsPerMeasure() % Fraction()
                beats = time_value._rational * beats_per_measure
            case Beats():
                beats = time_value._rational
            case Steps():
                notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
                notes_per_step: Fraction = self._quantization % Fraction()
                beats_per_step: Fraction = notes_per_step / notes_per_beat
                beats = time_value._rational * beats_per_step
            case Duration():
                notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
                beats = time_value._rational / notes_per_beat
            case ou.Measure():
                return self.getBeats(Measures(time_value % Fraction()))
            case ou.Beat():
                return self.getBeats(Beats(time_value % Fraction()))
            case ou.Step():
                return self.getBeats(Steps(time_value % Fraction()))
        return Beats(beats)

    def getSteps(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> 'Steps':
        steps: Fraction = Fraction(0)
        match time_value:
            case None:
                return self.getSteps(Beats(self._rational))
            case Span():
                time_beats: Beats = self.getBeats(time_value)
                return self.getSteps(time_beats)
            case Measures():
                beats = self.getBeats(time_value)
                steps = self.getSteps(beats)
            case Beats():
                notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
                notes_per_step: Fraction = self._quantization % Fraction()
                beats_per_step: Fraction = notes_per_step / notes_per_beat
                steps = time_value._rational / beats_per_step
            case Steps():
                steps = time_value._rational
            case Duration():
                beats = self.getBeats(time_value)
                steps = self.getSteps(beats)
            case ou.Measure():
                return self.getSteps(Measures(time_value % Fraction()))
            case ou.Beat():
                return self.getSteps(Beats(time_value % Fraction()))
            case ou.Step():
                return self.getSteps(Steps(time_value % Fraction()))
        return Steps(steps)

    def getDuration(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> 'Duration':
        note_value: Fraction = Fraction(0)
        match time_value:
            case None:
                return self.getDuration(Beats(self._rational))
            case Span():
                time_beats: Beats = self.getBeats(time_value)
                return self.getDuration(time_beats)
            case Measures():
                beats = self.getBeats(time_value)
                note_value = self.getDuration(beats)
            case Beats():
                notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
                note_value = time_value._rational * notes_per_beat
            case Steps():
                beats = self.getBeats(time_value)
                note_value = self.getDuration(beats)
            case Duration():
                note_value = time_value._rational
            case ou.Measure():
                return self.getDuration(Measures(time_value % Fraction()))
            case ou.Beat():
                return self.getDuration(Beats(time_value % Fraction()))
            case ou.Step():
                return self.getDuration(Steps(time_value % Fraction()))
        return Duration(note_value)


    def getMeasure(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> 'ou.Measure':
        measure: int = 0
        match time_value:
            case None:
                return self.getMeasure(Beats(self._rational))
            case Span():
                time_beats: Beats = self.getBeats(time_value)
                return self.getMeasure(time_beats)
            case TimeValue() | ou.TimeUnit():
                measure = self.getMeasures(time_value) % int()
        return ou.Measure(measure)

    def getBeat(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> 'ou.Beat':
        beat: int = 0
        match time_value:
            case None:
                return self.getBeat(Beats(self._rational))
            case Span():
                time_beats: Beats = self.getBeats(time_value)
                return self.getBeat(time_beats)
            case TimeValue() | ou.TimeUnit():
                beats_per_measure: int = self._time_signature % BeatsPerMeasure() % int()
                beat = self.getBeats(time_value) % int() % beats_per_measure
        return ou.Beat(beat)

    def getStep(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> 'ou.Step':
        step: int = 0
        match time_value:
            case None:
                return self.getStep(Beats(self._rational))
            case Span():
                time_beats: Beats = self.getBeats(time_value)
                return self.getStep(time_beats)
            case TimeValue() | ou.TimeUnit():
                beats_per_measure: Fraction = self._time_signature % BeatsPerMeasure() % Fraction()
                notes_per_beat: Fraction = self._time_signature % BeatNoteValue() % Fraction()
                notes_per_step: Fraction = self._quantization % Fraction()
                beats_per_step: Fraction = notes_per_step / notes_per_beat
                steps_per_measure: int = int(beats_per_measure / beats_per_step)
                step = self.getSteps(time_value) % int() % steps_per_measure
        return ou.Step(step)


    def getMillis_rational(self, time_value: Union['Span', 'TimeValue', 'ou.TimeUnit'] = None) -> Fraction:
        beats: Fraction = self._rational
        beats_per_minute: Fraction = self._tempo._rational
        if time_value is not None:
            beats = self.getBeats(time_value) % od.DataSource( Fraction() )
        return beats / beats_per_minute * 60 * 1000
    
    def getPlaylist(self, position: 'Position' = None) -> list:
        import operand_element as oe
        self_position: Position  = self + Position() if position is None else position
        
        return [
                {
                    "time_ms": oe.Element.get_time_ms(self_position.getMillis_rational())
                }
            ]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tempo"]            = self.serialize(self._tempo)
        serialization["parameters"]["time_signature"]   = self.serialize(self._time_signature)
        serialization["parameters"]["quantization"]     = self.serialize(self._quantization)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Span':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tempo" in serialization["parameters"] and "time_signature" in serialization["parameters"] and
            "quantization" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempo             = self.deserialize(serialization["parameters"]["tempo"])
            self._time_signature    = self.deserialize(serialization["parameters"]["time_signature"])
            self._quantization      = self.deserialize(serialization["parameters"]["quantization"])

        return self

    def __lshift__(self, operand: o.Operand) -> 'Span':
        import operand_generic as og
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Tempo():               self._tempo             = operand % o.Operand()
                    case og.TimeSignature():    self._time_signature    = operand % o.Operand()
                    case Quantization():        self._quantization      = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case Span():
                super().__lshift__(operand)
                self._tempo             << operand._tempo
                self._time_signature    << operand._time_signature
                self._quantization      << operand._quantization
            case TimeValue():
                self._rational = self.getBeats(operand) % Fraction()
            case ou.Measure():
                measure_beats: Beats = self.getBeats() - self.getBeats(self.getMeasure())
                self._rational = (self.getBeats(operand) + measure_beats) % od.DataSource( Fraction() )
            case ou.Beat() | ou.Step():
                self_measure: ou.Measure = self.getMeasure()
                self._rational = (self.getBeats(self_measure) + self.getBeats(operand)) % od.DataSource( Fraction() )
            case Tempo():
                self._tempo             << operand
            case og.TimeSignature() | BeatsPerMeasure() | BeatNoteValue() | NotesPerMeasure():
                self._time_signature    << operand
            case Quantization():
                self._quantization      << operand
            case _:
                super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Span':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Span() | TimeValue() | ou.TimeUnit():
                self_copy._rational += self.getBeats(operand) % od.DataSource( Fraction() )
        return self_copy
    
    def __sub__(self, operand: o.Operand) -> 'Span':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Span() | TimeValue() | ou.TimeUnit():
                self_copy._rational -= self.getBeats(operand) % od.DataSource( Fraction() )
        return self_copy
    
    def __mul__(self, operand: o.Operand) -> 'Span':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Span():
                multiplier: Fraction = operand.getMeasures() % od.DataSource( Fraction() )
                return super().__mul__(multiplier)
        return super().__mul__(operand)
    
    def __truediv__(self, operand: o.Operand) -> 'Span':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Span():
                divider: Fraction = operand.getMeasures() % od.DataSource( Fraction() )
                return super().__truediv__(divider)
        return super().__truediv__(operand)

    def __rmul__(self, operand: o.Operand) -> 'Span':
        return self * operand
    
    def __rtruediv__(self, operand: o.Operand) -> 'Span':
        return self / operand
    
    


class Length(Span):
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Length':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | float() | Fraction():
                self << Measures(operand)
            case _:
                super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Length':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | float() | Fraction():
                return self + Measures(operand)
        return super().__add__(operand)
    
    def __sub__(self, operand: o.Operand) -> 'Length':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | float() | Fraction():
                return self - Measures(operand)
        return super().__sub__(operand)
    
class Position(Length):
    pass
    
# class NoteValue(Time):
#     # CHAINABLE OPERATIONS

#     def __lshift__(self, operand: o.Operand) -> 'NoteValue':
#         operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
#         match operand:
#             case int() | float() | Fraction():
#                 self << Duration(operand)
#             case _:
#                 super().__lshift__(operand)
#         return self

#     def __add__(self, operand: o.Operand) -> 'NoteValue':
#         operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
#         match operand:
#             case int() | float() | Fraction():
#                 return self + Duration(operand)
#         return super().__add__(operand)
    
#     def __sub__(self, operand: o.Operand) -> 'NoteValue':
#         operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
#         match operand:
#             case int() | float() | Fraction():
#                 return self - Duration(operand)
#         return super().__sub__(operand)
    




class TimeValue(Rational):  # Works as Absolute Beats
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
    pass

class Beats(TimeValue):
    """
    A Beat() represents the Staff Time Length in Beat on which the Tempo is based on (BPM).
    
    Parameters
    ----------
    first : float_like
        Proportional value to a Beat on the Staff
    """
    pass

class Steps(TimeValue):
    """
    A Step() represents the Length given by the Quantization, normally 1/16 Note Value.
    
    Parameters
    ----------
    first : float_like
        Steps as 1, 2, 4, 8
    """
    pass

class Duration(TimeValue):
    """
    NoteValue() represents the Duration of a Note, a Note Value typically comes as 1/4, 1/8 and 1/16.
    
    Parameters
    ----------
    first : float_like
        Note Value as 1, 1/2, 1/4, 1/8, 1/16, 1/32
    """
    pass

class NoteValue(Duration):
    pass

class Quantization(NoteValue):
    """
    Play() allows to send a given Element to the Player directly without the need of Exporting to the respective .json Player file.
    
    Parameters
    ----------
    first : float_like
        By default it's configured without any verbose, set to 1 or True to enable verbose
    """
    pass

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
            case int() | float() | Fraction():
                # Reverses the value by multiplying it by 3/2 because it's a Dotted Note
                other_rational: Fraction = self._rational * 2/3
                if isinstance(operand, int):
                    return int(other_rational)
                if isinstance(operand, float):
                    return float(other_rational)
                return Fraction(other_rational).limit_denominator(self._limit_denominator)
            case _: return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Dotted':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource() | Duration() | od.Serialization():
                super().__lshift__(operand)
            # It's just a wrapper for NoteValue 3/2
            case int() | float() | Fraction():
                super().__lshift__(operand) # Starts by setting the self._rational as NoteValue
                # Then it's multiplied by 3/2 because it's a Dotted Note
                self._rational *= 3/2
            case _:
                if not isinstance(operand, (Rational, ou.Unit)):
                    super().__lshift__(operand)
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

