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
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_staff as os
import operand_rational as ro
import operand_unit as ou
import operand_data as od
import operand_frame as of
import operand_label as ol


class Time(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        self._time_unit      = ro.Measure()
        if len(parameters) > 0:
            self << parameters

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
                    case ro.TimeUnit():     return self._time_unit % od.DataSource( operand % o.Operand() )
                    case Time():            return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Time():            return self.copy()
            case ro.Measure():
                return ro.Measure() << self._time_unit % operand % int()
            case ro.Beat() | ro.Step():
                return operand.__class__() << (ro.Measure() << self._time_unit % Fraction() - self._time_unit % int())
            case ro.TimeUnit() | int() | float() | Fraction() | ou.Integer() | ro.Float():
                return self._time_unit % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_time: any) -> bool:
        other_time = self & other_time    # Processes the tailed self operands or the Frame operand if any exists
        match other_time:
            case ro.NoteValue():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( Fraction() ) == other_time % od.DataSource( Fraction() )
            case ro.Measure():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) == other_time % od.DataSource( int() )
            case ro.Beat():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ro.BeatsPerMeasure() ) % int()) \
                    == other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ro.BeatsPerMeasure() ) % int())
            case ro.Step():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ro.StepsPerMeasure() ) % int()) \
                    == other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ro.StepsPerMeasure() ) % int())
            case Time():
                return self.getTime_rational() == other_time.getTime_rational()
            case _:
                if other_time.__class__ == o.Operand:
                    return True
        return False

    def __lt__(self, other_time: any) -> bool:
        other_time = self & other_time    # Processes the tailed self operands or the Frame operand if any exists
        match other_time:
            case ro.NoteValue():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( Fraction() ) < other_time % od.DataSource( Fraction() )
            case ro.Measure():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) < other_time % od.DataSource( int() )
            case ro.Beat():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ro.BeatsPerMeasure() ) % int()) \
                    < other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ro.BeatsPerMeasure() ) % int())
            case ro.Step():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ro.StepsPerMeasure() ) % int()) \
                    < other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ro.StepsPerMeasure() ) % int())
            case Time():
                return self.getTime_rational() < other_time.getTime_rational()
        return False
    
    def __gt__(self, other_time: any) -> bool:
        other_time = self & other_time    # Processes the tailed self operands or the Frame operand if any exists
        match other_time:
            case ro.NoteValue():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( Fraction() ) > other_time % od.DataSource( Fraction() )
            case ro.Measure():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) > other_time % od.DataSource( int() )
            case ro.Beat():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ro.BeatsPerMeasure() ) % int()) \
                    > other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ro.BeatsPerMeasure() ) % int())
            case ro.Step():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ro.StepsPerMeasure() ) % int()) \
                    > other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ro.StepsPerMeasure() ) % int())
            case Time():
                return self.getTime_rational() > other_time.getTime_rational()
        return False
    
    def __le__(self, other_time: any) -> bool:
        return self == other_time or self < other_time
    
    def __ge__(self, other_time: any) -> bool:
        return self == other_time or self > other_time

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

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "time_unit":    self._time_unit.getSerialization()
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "time_unit" in serialization["parameters"] and "class" in serialization["parameters"]["time_unit"]):
                new_operand = self.getOperand(serialization["parameters"]["time_unit"]["class"])
                if new_operand:
                    self._time_unit = new_operand.loadSerialization(serialization["parameters"]["time_unit"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Time':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.TimeUnit():
                        self._time_unit << operand % o.Operand() % od.DataSource( self._time_unit )
            case Time():
                self._time_unit         << operand._time_unit
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ro.Measure():
                if operand % int() == operand % Fraction():
                    # Meant to change just the Measure
                    self._time_unit << operand % int() \
                        + (self._time_unit % Fraction() - self._time_unit % int())
                else:
                    self._time_unit     << operand
            case ro.Beat() | ro.Step():
                self._time_unit << self._time_unit % int()  # Resets to zero Beats/Steps
                self._time_unit += operand
            case ro.TimeUnit():
                self._time_unit << operand
            case int() | ou.Integer():
                # Meant to change just the Measure
                self._time_unit << (self._time_unit % Fraction() - self._time_unit % int()) + operand
            case Fraction() | float() | ro.Float():
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
                self_copy << od.DataSource( self._time_unit + operand % od.DataSource( ro.TimeUnit() ) % od.DataSource( self._time_unit ) )
            case ro.TimeUnit():
                self_copy << od.DataSource( self._time_unit + operand % od.DataSource( self._time_unit ) )
            case int() | float() | ou.Integer() | ro.Float() | Fraction():
                self_copy << od.DataSource( self._time_unit + operand )
        return self_copy
    
    def __sub__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_unit - operand % od.DataSource( ro.TimeUnit() ) % od.DataSource( self._time_unit ) )
            case ro.TimeUnit():
                self_copy << od.DataSource( self._time_unit - operand % od.DataSource( self._time_unit ) )
            case int() | float() | ou.Integer() | ro.Float() | Fraction():
                self_copy << od.DataSource( self._time_unit - operand )
        return self_copy
    
    def __mul__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_unit * (operand % od.DataSource( ro.TimeUnit() ) % od.DataSource( self._time_unit )) )
            case ro.TimeUnit():
                self_copy << od.DataSource( self._time_unit * (operand % od.DataSource( self._time_unit )) )
            case int() | float() | ou.Integer() | ro.Float() | Fraction():
                self_copy << od.DataSource( self._time_unit * operand )
        return self_copy
    
    def __rmul__(self, operand: o.Operand) -> 'Time':
        return self * operand
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                if operand % od.DataSource( ro.TimeUnit() ) % od.DataSource( self._time_unit ) != 0:
                    self_copy << od.DataSource( self._time_unit / (operand % od.DataSource( ro.TimeUnit() ) % od.DataSource( self._time_unit )) )
            case ro.TimeUnit():
                if operand % od.DataSource( self._time_unit ) != 0:
                    self_copy << od.DataSource( self._time_unit / (operand % od.DataSource( self._time_unit )) )
            case int() | float() | ou.Integer() | ro.Float() | Fraction():
                if operand != 0:
                    self_copy << od.DataSource( self._time_unit / operand )
        return self_copy

    def __rtruediv__(self, operand: o.Operand) -> 'Time':
        return self / operand
    
    def start(self) -> ro.TimeUnit:
        return self.copy()

    def end(self) -> ro.TimeUnit:
        return self.copy()

    def minimum(self) -> ro.TimeUnit:
        return self._time_unit % int()

    def maximum(self) -> ro.TimeUnit:
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
        self._time_unit      = ro.NoteValue()
        if len(parameters) > 0:
            self << parameters

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Time':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():       super().__lshift__(operand)
            case ro.TimeUnit(): # Avoids extra processing of TimeUnits like Measure or Beat
                self._time_unit << operand
            case _: super().__lshift__(operand)
        return self

    def __mul__(self, operand: o.Operand) -> 'Time':
        match operand:
            case ro.Gate() | ro.Swing() | ou.Division():
                return self.__class__() << od.DataSource( self._time_unit * (operand % od.DataSource( Fraction() )) )
            case _: return super().__mul__(operand)
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        match operand:
            case ro.Gate() | ro.Swing() | ou.Division():
                return self.__class__() << od.DataSource( self._time_unit / (operand % od.DataSource( Fraction() )) )
            case _: return super().__truediv__(operand)
