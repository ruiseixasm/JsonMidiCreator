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
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_staff as os
import operand_rational as ra
import operand_unit as ou
import operand_data as od
import operand_frame as of
import operand_label as ol

TypeTime = TypeVar('TypeTime', bound='Time')  # TypeTime represents any subclass of Operand


class Time(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        self._time_unit      = ra.Measure()
        if len(parameters) > 0:
            self << parameters

    def time(self: TypeTime, number: int = None) -> TypeTime:
        return self << od.DataSource( number )

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
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case ra.TimeUnit():     return self._time_unit % od.DataSource( operand % o.Operand() )
                    case Time():            return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Time():            return self.copy()
            case ra.Measure():
                return ra.Measure() << self._time_unit % operand % int()
            case ra.Beat() | ra.Step():
                return operand.__class__() << (ra.Measure() << self._time_unit % Fraction() - self._time_unit % int())
            case ra.TimeUnit() | int() | float() | Fraction() | ou.IntU() | ra.FloatR():
                return self._time_unit % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case ra.NoteValue():
                return self._time_unit % od.DataSource( other ) % od.DataSource( Fraction() ) == other % od.DataSource( Fraction() )
            case ra.Measure():
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) == other % od.DataSource( int() )
            case ra.Beat(): # LAST % REQUIRED FOR POSITION GREATER THAN MEASURE 0!
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) % (os.staff % od.DataSource( ra.BeatsPerMeasure() ) % int()) \
                    == other % od.DataSource( int() ) % (os.staff % od.DataSource( ra.BeatsPerMeasure() ) % int())
            case ra.Step(): # LAST % REQUIRED FOR POSITION GREATER THAN MEASURE 0!
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) % (os.staff % od.DataSource( ra.StepsPerMeasure() ) % int()) \
                    == other % od.DataSource( int() ) % (os.staff % od.DataSource( ra.StepsPerMeasure() ) % int())
            case Time():
                return self.getTime_rational() == other.getTime_rational()
            case _:
                if other.__class__ == o.Operand:
                    return True
        return False

    def __lt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case ra.NoteValue():
                return self._time_unit % od.DataSource( other ) % od.DataSource( Fraction() ) < other % od.DataSource( Fraction() )
            case ra.Measure():
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) < other % od.DataSource( int() )
            case ra.Beat():
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) % (os.staff % od.DataSource( ra.BeatsPerMeasure() ) % int()) \
                    < other % od.DataSource( int() ) % (os.staff % od.DataSource( ra.BeatsPerMeasure() ) % int())
            case ra.Step():
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) % (os.staff % od.DataSource( ra.StepsPerMeasure() ) % int()) \
                    < other % od.DataSource( int() ) % (os.staff % od.DataSource( ra.StepsPerMeasure() ) % int())
            case Time():
                return self.getTime_rational() < other.getTime_rational()
        return False
    
    def __gt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case ra.NoteValue():
                return self._time_unit % od.DataSource( other ) % od.DataSource( Fraction() ) > other % od.DataSource( Fraction() )
            case ra.Measure():
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) > other % od.DataSource( int() )
            case ra.Beat():
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) % (os.staff % od.DataSource( ra.BeatsPerMeasure() ) % int()) \
                    > other % od.DataSource( int() ) % (os.staff % od.DataSource( ra.BeatsPerMeasure() ) % int())
            case ra.Step():
                return self._time_unit % od.DataSource( other ) % od.DataSource( int() ) % (os.staff % od.DataSource( ra.StepsPerMeasure() ) % int()) \
                    > other % od.DataSource( int() ) % (os.staff % od.DataSource( ra.StepsPerMeasure() ) % int())
            case Time():
                return self.getTime_rational() > other.getTime_rational()
        return False
    
    def __le__(self, other: any) -> bool:
        return self == other or self < other
    
    def __ge__(self, other: any) -> bool:
        return self == other or self > other

    def __str__(self):
        return f'{self._time_unit}'
    
    def getTime_rational(self) -> Fraction:
        return self._time_unit.getTime_rational()
        
    def getTime_ms(self, rounded = True) -> float:
        if rounded:
            return round(float(self.getTime_rational()), 3)
        return float(self.getTime_rational())
        
    def getPlaylist(self, position: 'Position' = None) -> list:
        self_position: Position  = self + Position() if position is None else position
        
        return [
                {
                    "time_ms": self_position.getTime_ms()
                }
            ]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["time_unit"] = self.serialize(self._time_unit)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Time':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "time_unit" in serialization["parameters"] and "class" in serialization["parameters"]["time_unit"]):

            super().loadSerialization(serialization)
            self._time_unit = self.deserialize(serialization["parameters"]["time_unit"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Time':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ra.TimeUnit():
                        self._time_unit << operand % o.Operand() % od.DataSource( self._time_unit )
            case Time():
                super().__lshift__(operand)
                self._time_unit         << operand._time_unit
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Measure():
                if operand % int() == operand % Fraction():
                    # Meant to change just the Measure
                    self._time_unit << operand % int() \
                        + (self._time_unit % Fraction() - self._time_unit % int())
                else:
                    self._time_unit     << operand
            case ra.Beat() | ra.Step():
                self._time_unit << self._time_unit % int()  # Resets to zero Beats/Steps
                self._time_unit += operand
            case ra.TimeUnit():
                self._time_unit << operand
            case int() | ou.IntU():
                # Meant to change just the Measure
                self._time_unit << (self._time_unit % Fraction() - self._time_unit % int()) + operand
            case Fraction() | float() | ra.FloatR():
                self._time_unit         << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __add__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_unit + operand % od.DataSource( ra.TimeUnit() ) % od.DataSource( self._time_unit ) )
            case ra.TimeUnit():
                self_copy << od.DataSource( self._time_unit + operand % od.DataSource( self._time_unit ) )
            case int() | float() | ou.IntU() | ra.FloatR() | Fraction():
                self_copy << od.DataSource( self._time_unit + operand )
        return self_copy
    
    def __sub__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_unit - operand % od.DataSource( ra.TimeUnit() ) % od.DataSource( self._time_unit ) )
            case ra.TimeUnit():
                self_copy << od.DataSource( self._time_unit - operand % od.DataSource( self._time_unit ) )
            case int() | float() | ou.IntU() | ra.FloatR() | Fraction():
                self_copy << od.DataSource( self._time_unit - operand )
        return self_copy
    
    def __mul__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_unit * (operand % od.DataSource( ra.TimeUnit() ) % od.DataSource( self._time_unit )) )
            case ra.TimeUnit():
                self_copy << od.DataSource( self._time_unit * (operand % od.DataSource( self._time_unit )) )
            case int() | float() | ou.IntU() | ra.FloatR() | Fraction():
                self_copy << od.DataSource( self._time_unit * operand )
        return self_copy
    
    def __rmul__(self, operand: o.Operand) -> 'Time':
        return self * operand
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                if operand % od.DataSource( ra.TimeUnit() ) % od.DataSource( self._time_unit ) != 0:
                    self_copy << od.DataSource( self._time_unit / (operand % od.DataSource( ra.TimeUnit() ) % od.DataSource( self._time_unit )) )
            case ra.TimeUnit():
                if operand % od.DataSource( self._time_unit ) != 0:
                    self_copy << od.DataSource( self._time_unit / (operand % od.DataSource( self._time_unit )) )
            case int() | float() | ou.IntU() | ra.FloatR() | Fraction():
                if operand != 0:
                    self_copy << od.DataSource( self._time_unit / operand )
        return self_copy

    def __rtruediv__(self, operand: o.Operand) -> 'Time':
        return self / operand
    
    def start(self) -> ra.TimeUnit:
        return self.copy()

    def end(self) -> ra.TimeUnit:
        return self.copy()

    def minimum(self) -> ra.TimeUnit:
        return self._time_unit % int()

    def maximum(self) -> ra.TimeUnit:
        return self._time_unit % int() + 1

class Position(Time):
    def __init__(self, *parameters):
        super().__init__(parameters)

class Length(Time):
    def __init__(self, *parameters):
        super().__init__(parameters)
    
class Duration(Time):
    def __init__(self, *parameters):
        super().__init__()
        self._time_unit      = ra.NoteValue()
        if len(parameters) > 0:
            self << parameters

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Time':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():       super().__lshift__(operand)
            case ra.TimeUnit(): # Avoids extra processing of TimeUnits like Measure or Beat
                self._time_unit << operand
            case _: super().__lshift__(operand)
        return self

    def __mul__(self, operand: o.Operand) -> 'Time':
        match operand:
            case ra.Gate() | ra.Swing() | ou.Division():
                return self.__class__() << od.DataSource( self._time_unit * (operand % od.DataSource( Fraction() )) )
            case _: return super().__mul__(operand)
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        match operand:
            case ra.Gate() | ra.Swing() | ou.Division():
                return self.__class__() << od.DataSource( self._time_unit / (operand % od.DataSource( Fraction() )) )
            case _: return super().__truediv__(operand)
