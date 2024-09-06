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
import operand_value as ov
import operand_unit as ou
import operand_data as od
import operand_frame as of
import operand_label as ol


class Time(o.Operand):
    def __init__(self, time: int | float = None):
        super().__init__()
        self._time_unit: ov.TimeUnit    = ov.TimeUnit() << time

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case ov.TimeUnit():     return self._time_unit % od.DataSource( operand % o.Operand() )
                    case Time():            return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case ov.TimeUnit():     return self._time_unit % operand
            case Time():            return self.copy()
            case _:                 return ol.Null()

    def __eq__(self, other_time: any) -> bool:
        match other_time:
            case ov.NoteValue():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( Fraction() ) == other_time % od.DataSource( Fraction() )
            case ov.Measure():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) == other_time % od.DataSource( int() )
            case ov.Beat():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ov.BeatsPerMeasure() ) % int()) \
                    == other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ov.BeatsPerMeasure() ) % int())
            case ov.Step():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ov.StepsPerMeasure() ) % int()) \
                    == other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ov.StepsPerMeasure() ) % int())
            case Time():
                return self.getTime_rational() == other_time.getTime_rational()
        return False

    def __lt__(self, other_time: any) -> bool:
        match other_time:
            case ov.NoteValue():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( Fraction() ) < other_time % od.DataSource( Fraction() )
            case ov.Measure():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) < other_time % od.DataSource( int() )
            case ov.Beat():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ov.BeatsPerMeasure() ) % int()) \
                    < other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ov.BeatsPerMeasure() ) % int())
            case ov.Step():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ov.StepsPerMeasure() ) % int()) \
                    < other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ov.StepsPerMeasure() ) % int())
            case Time():
                return self.getTime_rational() < other_time.getTime_rational()
        return False
    
    def __gt__(self, other_time: any) -> bool:
        match other_time:
            case ov.NoteValue():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( Fraction() ) > other_time % od.DataSource( Fraction() )
            case ov.Measure():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) > other_time % od.DataSource( int() )
            case ov.Beat():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ov.BeatsPerMeasure() ) % int()) \
                    > other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ov.BeatsPerMeasure() ) % int())
            case ov.Step():
                return self._time_unit % od.DataSource( other_time ) % od.DataSource( int() ) % (os.staff % od.DataSource( ov.StepsPerMeasure() ) % int()) \
                    > other_time % od.DataSource( int() ) % (os.staff % od.DataSource( ov.StepsPerMeasure() ) % int())
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
        
    def getPlayList(self, position: 'Position' = None) -> list:
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
                operand = self.getOperand(serialization["parameters"]["time_unit"]["class"])
                if operand:
                    self._time_unit = operand.loadSerialization(serialization["parameters"]["time_unit"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Time':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    # case ov.Measure():
                    #     self._time_unit << od.DataSource( operand % od.DataSource( int() ) + (self._time_unit - self._time_unit % od.DataSource( int() )) )
                    # case ov.Beat():
                    #     beat_measure = ov.Measure() << operand % (os.staff % od.DataSource( ov.BeatsPerMeasure() ) % int())
                    #     self._time_unit << od.DataSource( self._time_unit % od.DataSource( int() ) + beat_measure % od.DataSource( int() ) )
                    # case ov.Step():
                    #     step_measure = ov.Measure() << operand % (os.staff % od.DataSource( ov.StepsPerMeasure() ) % int())
                    #     self._time_unit << od.DataSource( self._time_unit % od.DataSource( int() ) + step_measure % od.DataSource( int() ) )
                    case ov.TimeUnit():         self._time_unit = operand % o.Operand() % od.DataSource( self._time_unit )
            case Time():
                self._time_unit         << operand % od.DataSource( ov.TimeUnit() )
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ov.Measure():
                measure_int = operand % int()
                if operand % Fraction() == measure_int:
                    self._time_unit << measure_int + (self._time_unit % Fraction() - self._time_unit % int())
                else:
                    self._time_unit << operand
            # case ov.Beat():
            #     beat_measure = ov.Measure() << operand % (os.staff % od.DataSource( ov.BeatsPerMeasure() ) % int())
            #     self._time_unit << self._time_unit % int() + beat_measure % int()
            # case ov.Step():
            #     step_measure = ov.Measure() << operand % (os.staff % od.DataSource( ov.StepsPerMeasure() ) % int())
            #     self._time_unit << self._time_unit % int() + step_measure % int()
            case ov.TimeUnit():
                self._time_unit << operand
            case Fraction() | float() | int():
                self._time_unit         << operand
        return self

    def __add__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():            self_copy << od.DataSource( self._time_unit + operand % od.DataSource( ov.TimeUnit() ) % od.DataSource( self._time_unit ) )
            case ov.TimeUnit():     self_copy << od.DataSource( self._time_unit + operand % od.DataSource( self._time_unit ) )
            case int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << od.DataSource( self._time_unit + operand )
        return self_copy
    
    def __sub__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():            self_copy << od.DataSource( self._time_unit - operand % od.DataSource( ov.TimeUnit() ) % od.DataSource( self._time_unit ) )
            case ov.TimeUnit():     self_copy << od.DataSource( self._time_unit - operand % od.DataSource( self._time_unit ) )
            case int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << od.DataSource( self._time_unit - operand )
        return self_copy
    
    def __mul__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():            self_copy << od.DataSource( self._time_unit * (operand % od.DataSource( ov.TimeUnit() ) % od.DataSource( self._time_unit )) )
            case ov.TimeUnit():     self_copy << od.DataSource( self._time_unit * (operand % od.DataSource( self._time_unit )) )
            case int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << od.DataSource( self._time_unit * operand )
        return self_copy
    
    def __rmul__(self, operand: o.Operand) -> 'Time':
        return self * operand
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                if operand % od.DataSource( ov.TimeUnit() ) % od.DataSource( self._time_unit ) != 0:
                    self_copy << od.DataSource( self._time_unit / (operand % od.DataSource( ov.TimeUnit() ) % od.DataSource( self._time_unit )) )
            case ov.TimeUnit():
                if operand % od.DataSource( self._time_unit ) != 0:
                    self_copy << od.DataSource( self._time_unit / (operand % od.DataSource( self._time_unit )) )
            case int() | float() | ou.Integer() | ov.Float() | Fraction():
                if operand != 0:
                    self_copy << od.DataSource( self._time_unit / operand )
        return self_copy

    def __rtruediv__(self, operand: o.Operand) -> 'Time':
        return self / operand
    
    def start(self) -> ov.TimeUnit:
        return self.copy()

    def end(self) -> ov.TimeUnit:
        return self.copy()

    def minimum(self) -> ov.TimeUnit:
        return self._time_unit % int()

    def maximum(self) -> ov.TimeUnit:
        return self._time_unit % int() + 1

class Position(Time):
    def __init__(self, time: int | float = None):
        super().__init__()
        self._time_unit      = ov.Measure() << time

class Length(Time):
    def __init__(self, time: int | float = None):
        super().__init__()
        self._time_unit      = ov.Measure() << time
    
class Duration(Time):
    def __init__(self, time: int | float = None):
        super().__init__()
        self._time_unit      = ov.NoteValue() << time

    # CHAINABLE OPERATIONS

    # def __lshift__(self, operand: o.Operand) -> 'Time':
    #     operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
    #     match operand:
    #         case od.DataSource():
    #             match operand % o.Operand():
    #                 case ov.TimeUnit():
    #                     self._time_unit << od.DataSource( operand % o.Operand() % od.DataSource( self._time_unit ) )
    #                 case _:                     super().__lshift__(operand)
    #         case ov.TimeUnit():
    #             self._time_unit << operand
    #         case _: super().__lshift__(operand)
    #     return self

    def __mul__(self, operand: o.Operand) -> 'Time':
        match operand:
            case ov.Gate() | ov.Swing() | ou.Division():
                return self.__class__() << od.DataSource( self._time_unit * (operand % od.DataSource( Fraction() )) )
            case _: return super().__mul__(operand)
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        match operand:
            case ov.Gate() | ov.Swing() | ou.Division():
                return self.__class__() << od.DataSource( self._time_unit / (operand % od.DataSource( Fraction() )) )
            case _: return super().__truediv__(operand)
