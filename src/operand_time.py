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
        self._time_value    = ra.TimeValue()
        if parameters:
            self << parameters

    def time(self: TypeTime, beats: float = None) -> TypeTime:
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
                    case ra.TimeValue() | int() | float() | Fraction() | ou.IntU() | ra.FloatR() | ra.Tempo() | og.TimeSignature() | ra.Quantization():
                                            return self._time_value % operand
                    case Time():            return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case ra.Measures():
                return ra.Measures(self._time_value)
            case ra.Beats():
                return ra.Beats(self._time_value)
            case ra.Steps():
                return ra.Steps(self._time_value)
            case ra.NoteValue():
                return ra.NoteValue(self._time_value)
            case ou.TimeUnit() | int() | float() | Fraction() | ou.IntU() | ra.FloatR() | ra.Tempo() | og.TimeSignature() | ra.Quantization():
                return self._time_value % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case ra.TimeValue() | ou.TimeUnit():
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
            case ra.TimeValue() | ou.TimeUnit():
                return self._time_value < other
            case Time():
                return self._time_value < other._time_value
        return False
    
    def __gt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case ra.TimeValue() | ou.TimeUnit():
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
                    case ra.TimeValue():
                        self._time_value = operand % o.Operand()
            case Time():
                super().__lshift__(operand)
                self._time_value         << operand._time_value
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.TimeValue() | ou.TimeUnit() | int() | ou.IntU() | Fraction() | float() | ra.FloatR():
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
                self_copy << od.DataSource( self._time_value + operand % od.DataSource( ra.TimeValue() ) % od.DataSource( self._time_value ) )
            case ra.TimeValue():
                self_copy << od.DataSource( self._time_value + operand % od.DataSource( self._time_value ) )
            case int() | float() | ou.IntU() | ra.FloatR() | Fraction():
                self_copy << od.DataSource( self._time_value + operand )
        return self_copy
    
    def __sub__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_value - operand % od.DataSource( ra.TimeValue() ) % od.DataSource( self._time_value ) )
            case ra.TimeValue():
                self_copy << od.DataSource( self._time_value - operand % od.DataSource( self._time_value ) )
            case int() | float() | ou.IntU() | ra.FloatR() | Fraction():
                self_copy << od.DataSource( self._time_value - operand )
        return self_copy
    
    def __mul__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                self_copy << od.DataSource( self._time_value * (operand % od.DataSource( ra.TimeValue() ) % od.DataSource( self._time_value )) )
            case ra.TimeValue():
                self_copy << od.DataSource( self._time_value * (operand % od.DataSource( self._time_value )) )
            case int() | float() | ou.IntU() | ra.FloatR() | Fraction():
                self_copy << od.DataSource( self._time_value * operand )
        return self_copy
    
    def __rmul__(self, operand: o.Operand) -> 'Time':
        return self * operand
    
    def __truediv__(self, operand: o.Operand) -> 'Time':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Time():
                if operand % od.DataSource( ra.TimeValue() ) % od.DataSource( self._time_value ) != 0:
                    self_copy << od.DataSource( self._time_value / (operand % od.DataSource( ra.TimeValue() ) % od.DataSource( self._time_value )) )
            case ra.TimeValue():
                if operand % od.DataSource( self._time_value ) != 0:
                    self_copy << od.DataSource( self._time_value / (operand % od.DataSource( self._time_value )) )
            case int() | float() | ou.IntU() | ra.FloatR() | Fraction():
                if operand != 0:
                    self_copy << od.DataSource( self._time_value / operand )
        return self_copy

    def __rtruediv__(self, operand: o.Operand) -> 'Time':
        return self / operand
    
    def start(self) -> ra.TimeValue:
        return self.copy()

    def end(self) -> ra.TimeValue:
        return self.copy()

    def minimum(self) -> ra.TimeValue:
        return self._time_value % int()

    def maximum(self) -> ra.TimeValue:
        return self._time_value % int() + 1



class Position(Time):
    pass

class Length(Time):
    pass
    
class Duration(Time):
    pass



    # def __init__(self, *parameters):
    #     super().__init__()
    #     self._time_value      = ra.NoteValue()
    #     if parameters:
    #         self << parameters

    # # CHAINABLE OPERATIONS

    # def __lshift__(self, operand: o.Operand) -> 'Duration':
    #     operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
    #     match operand:
    #         case od.DataSource():       super().__lshift__(operand)
    #         case ra.TimeValue(): # Avoids extra processing of TimeUnits like Measure or Beat
    #             self._time_value << operand
    #         case _: super().__lshift__(operand)
    #     return self

    # def __mul__(self, operand: o.Operand) -> 'Duration':
    #     match operand:
    #         case ra.Gate() | ra.Swing() | ou.Division():
    #             return self.__class__() << od.DataSource( self._time_value * (operand % od.DataSource( Fraction() )) )
    #         case _: return super().__mul__(operand)
    
    # def __truediv__(self, operand: o.Operand) -> 'Duration':
    #     match operand:
    #         case ra.Gate() | ra.Swing() | ou.Division():
    #             return self.__class__() << od.DataSource( self._time_value / (operand % od.DataSource( Fraction() )) )
    #         case _: return super().__truediv__(operand)
