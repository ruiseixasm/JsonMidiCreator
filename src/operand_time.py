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
        # Default values already, no need to wrap them with Default()
        self._measure       = ov.Measure()
        self._beat          = ov.Beat()
        self._step          = ov.Step()
        self._note_value    = ov.NoteValue()
        if time is not None:
            if isinstance(time, int):
                self._measure       << time
            elif isinstance(time, (float, Fraction)):
                self._note_value    << time

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case ov.Measure():      return self._measure
                    case ov.Beat():         return self._beat
                    case ov.Step():         return self._step
                    case ov.NoteValue():    return self._note_value
                    case ol.Null() | None:  return ol.Null()
                    case _:                 return self
            case of.Frame():        return self % (operand % o.Operand())
            case ov.Measure():      return self._measure.copy()
            case ov.Beat():         return self._beat.copy()
            case ov.Step():         return self._step.copy()
            case ov.NoteValue():    return self._note_value.copy()
            case ol.Null() | None:  return ol.Null()
            case _:                 return self.copy()

    def __eq__(self, other_time):
        return self.getTime_rational() == other_time.getTime_rational()
    
    def __lt__(self, other_time):
        return self.getTime_rational() < other_time.getTime_rational()
    
    def __gt__(self, other_time):
        return self.getTime_rational() > other_time.getTime_rational()
    
    def __le__(self, other_time):
        return self == other_time or self < other_time
    
    def __ge__(self, other_time):
        return self == other_time or self > other_time
    
    def getTime_rational(self) -> Fraction:
        return self._measure.getTime_rational() + self._beat.getTime_rational() \
                + self._step.getTime_rational() + self._note_value.getTime_rational()
        
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
                "measure":      self._measure % od.DataSource( float() ),
                "beat":         self._beat % od.DataSource( float() ),
                "step":         self._step % od.DataSource( float() ),
                "note_value":   self._note_value % od.DataSource( float() )
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "measure" in serialization["parameters"] and "beat" in serialization["parameters"] and
            "note_value" in serialization["parameters"] and "step" in serialization["parameters"]):

            self._measure       = ov.Measure()      << od.DataSource( serialization["parameters"]["measure"] )
            self._beat          = ov.Beat()         << od.DataSource( serialization["parameters"]["beat"] )
            self._step          = ov.Step()         << od.DataSource( serialization["parameters"]["step"] )
            self._note_value    = ov.NoteValue()    << od.DataSource( serialization["parameters"]["note_value"] )

        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Time':
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ov.Measure():      self._measure = operand % o.Operand()
                    case ov.Beat():         self._beat = operand % o.Operand()
                    case ov.Step():         self._step = operand % o.Operand()
                    case ov.NoteValue():    self._note_value = operand % o.Operand()
            case Time():
                self._measure       = (operand % od.DataSource( ov.Measure() )).copy()
                self._beat          = (operand % od.DataSource( ov.Beat() )).copy()
                self._step          = (operand % od.DataSource( ov.Step() )).copy()
                self._note_value    = (operand % od.DataSource( ov.NoteValue() )).copy()
            case of.Frame():        self << (operand & self)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ov.Measure():      self._measure << operand
            case ov.Beat():
                self._beat << operand
                self._step << 0
            case ov.Step():
                self._beat << 0
                self._step << operand
            case ov.NoteValue():    self._note_value << operand
            case int():
                self._measure       << operand
            case Fraction() | float():
                self._note_value    << operand
        return self

    # adding two lengths 
    def __add__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        match operand:
            case of.Frame():        return self + (operand & self)
            case Time():            self_copy \
                                        << od.DataSource( self._measure + operand % od.DataSource( ov.Measure() ) ) \
                                        << od.DataSource( self._beat + operand % od.DataSource( ov.Beat() ) ) \
                                        << od.DataSource( self._step + operand % od.DataSource( ov.Step() ) ) \
                                        << od.DataSource( self._note_value + operand % od.DataSource( ov.NoteValue() ) )
            case ov.TimeUnit():     self_copy << od.DataSource( self % od.DataSource( operand ) + operand )
            case int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._measure + operand << self._beat + operand \
                          << self._step + operand << self._note_value + operand
        return self_copy
    
    # subtracting two lengths 
    def __sub__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        match operand:
            case of.Frame():        return self - (operand & self)
            case Time():            self_copy \
                                        << od.DataSource( self._measure - operand % od.DataSource( ov.Measure() ) ) \
                                        << od.DataSource( self._beat - operand % od.DataSource( ov.Beat() ) ) \
                                        << od.DataSource( self._step - operand % od.DataSource( ov.Step() ) ) \
                                        << od.DataSource( self._note_value - operand % od.DataSource( ov.NoteValue() ) )
            case ov.TimeUnit():     self_copy << od.DataSource( self % od.DataSource( operand ) - operand )
            case ov.Value() | ou.Unit() | Fraction() | float() | int():
                self_copy << self._measure - operand << self._beat - operand \
                          << self._step - operand << self._note_value - operand
        return self_copy
    
    def __mul__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        match operand:
            case of.Frame():        return self * (operand & self)
            case Time():            self_copy \
                                        << od.DataSource( self._measure * (operand % od.DataSource( ov.Measure() )) ) \
                                        << od.DataSource( self._beat * (operand % od.DataSource( ov.Beat() )) ) \
                                        << od.DataSource( self._step * (operand % od.DataSource( ov.Step() )) ) \
                                        << od.DataSource( self._note_value * (operand % od.DataSource( ov.NoteValue() )) )
            case ov.TimeUnit():     self_copy << od.DataSource( self % od.DataSource( operand ) * operand )
            case ov.Value() | ou.Unit() | Fraction() | float() | int():
                self_copy << self._measure * operand << self._beat * operand \
                          << self._step * operand << self._note_value * operand
        return self_copy
    
    def __rmul__(self, operand: o.Operand) -> 'Time':
        return self * operand
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        match operand:
            case of.Frame():        return self / (operand & self)
            case Time():            self_copy \
                                        << od.DataSource( self._measure / (operand % od.DataSource( ov.Measure() )) ) \
                                        << od.DataSource( self._beat / (operand % od.DataSource( ov.Beat() )) ) \
                                        << od.DataSource( self._step / (operand % od.DataSource( ov.Step() )) ) \
                                        << od.DataSource( self._note_value / (operand % od.DataSource( ov.NoteValue() )) )
            case ov.TimeUnit():     self_copy << od.DataSource( self % od.DataSource( operand ) / operand )
            case ov.Value() | ou.Unit() | Fraction() | float() | int():
                self_copy << self._measure / operand << self._beat / operand \
                          << self._step / operand << self._note_value / operand
        return self_copy

    def __rtruediv__(self, operand: o.Operand) -> 'Time':
        return self / operand
    
class Position(Time):
    def __init__(self, time: int | float = None):
        super().__init__(time)

    def start(self) -> 'Position':
        return self

    def end(self) -> 'Position':
        return self

class Duration(Time):
    def __init__(self, time: int | float = None):
        super().__init__(time)

class Length(Time):
    def __init__(self, time: int | float = None):
        super().__init__(time)
    
class Identity(Time):
    def __init__(self):
        super().__init__()
        self << 1
        self << 1.0
  