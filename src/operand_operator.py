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
import math
# Json Midi Creator Libraries
import creator as c
from operand import Operand
import operand_time as ot
import operand_value as ov
import operand_data as od
import operand_label as ol
import operand_frame as of
import operand_container as oc
import operand_element as oe


class Operator(Operand):
    """
    An Operator processes an Operand with an Integer input and an Operand output.

    Parameters
    ----------
    first : Operand_like
        A Operand to be regulated
    """
    def __init__(self, operand: Operand = None):
        self._operand = int() if operand is None else operand
        self._operator_list: list[Operator] = []

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case od.OperandData():
                match operand % Operand():
                    case list():            return self._operator_list
                    case Operand():         return self._operand
            case of.Frame():        return self % (operand % Operand())
            case list():            return self._operator_list
            case ol.Null() | None:  return ol.Null()
            case Operand():         return self._operand
            case _:                 return self

    def getSerialization(self):
        operators_serialization = []
        for single_operator in self % list():
            operators_serialization.append(single_operator.getSerialization())
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "operand": self._operand.getSerialization(),
                "operator_list": operators_serialization
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "operand" in serialization["parameters"] and "class" in serialization["parameters"]["operand"] and "operator_list" in serialization["parameters"]):

            operand_class = serialization["parameters"]["operand"]["class"]
            self._operand = globals()[operand_class]().loadSerialization(serialization["parameters"]["operand"])
            operator_list = []
            operators_serialization = serialization["parameters"]["operator_list"]
            for single_operator in operators_serialization:
                class_name = single_operator["class"]
                operator_list.append(globals()[class_name]().loadSerialization(single_operator))
            self._operator_list = operator_list
        return self
  
    def copy(self) -> 'Operator':
        return self.__class__() << od.OperandData( self._operand ) << od.OperandData( self._operator_list )

    def __lshift__(self, operand: Operand) -> 'Operator':
        match operand:
            case od.OperandData():
                match operand % Operand():
                    case list():            self._operator_list = operand % Operand()
                    case _:                 self._operand = operand % Operand()
            case Operator():
                self._operator_list = operand % od.OperandData( list() )
                self._operand       = operand % od.OperandData( Operand() )
            case of.Frame():        self << (operand & self)
            case list():            self._operator_list = operand
            case ol.Null | None:    return self
            case _:                 self._operand = operand
        return self

    def __or__(self, operand: 'Operand') -> 'Operand':
        match operand:
            case Operator():
                self._operator_list.insert(operand)
                return self
            case Operand():
                for single_operator in self._operator_list:
                    operand = single_operator | operand
                # self._operator_list = []    # Saved operators are used only once
        return operand

    def __ror__(self, operand: Operand) -> Operand:
        return self.__or__(operand)

class Oscillator(Operator):
    """
    This Operator has a function returns the given Operand regulated accordingly to the Oscillator parameters.

    Parameters
    ----------
    first : Operand_like
        A Operand to be regulated
    """
    def __init__(self, operand: Operand = None):
        super().__init__(operand)
        self._position: ot.Position     = ot.Position()
        self._length: ot.Length         = ot.Length() << ov.Measure(1)  # wavelength (360º)
        self._amplitude: ov.Amplitude   = ov.Amplitude(16)
        self._offset: ov.Offset         = ov.Offset(64)
        
    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case od.OperandData():      return super().__mod__(operand)
            case ot.Position():         return self._position
            case ot.Length():           return self._length
            case ov.Amplitude():        return self._amplitude
            case ov.Offset():           return self._offset
            case _:                     return super().__mod__(operand)

    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["position"] = self._position.getSerialization()
        element_serialization["parameters"]["length"] = self._length.getSerialization()
        element_serialization["parameters"]["amplitude"] = self._amplitude % float()
        element_serialization["parameters"]["offset"] = self._offset % float()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Oscillator':
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "length" in serialization["parameters"] and
            "amplitude" in serialization["parameters"] and "offset" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position = ot.Position().loadSerialization(serialization["parameters"]["position"])
            self._length = ot.Length().loadSerialization(serialization["parameters"]["length"])
            self._amplitude = ov.Amplitude(serialization["parameters"]["amplitude"])
            self._offset = ov.Offset(serialization["parameters"]["offset"])
        return self
      
    def copy(self) -> 'Oscillator':
        return super().copy() \
            << od.OperandData( self._position.copy() ) << od.OperandData( self._length.copy() ) \
            << od.OperandData( self._amplitude.copy() ) << od.OperandData( self._offset.copy() )

    def __lshift__(self, operand: Operand) -> 'Oscillator':
        match operand:
            case od.OperandData():
                match operand % Operand():
                    case ot.Position():     self._position = operand % Operand()
                    case ot.Length():       self._length = operand % Operand()
                    case ov.Amplitude():    self._amplitude = operand % Operand()
                    case ov.Offset():       self._offset = operand % Operand()
                    case _:                 super().__lshift__(operand)
            case Oscillator():
                super().__lshift__(operand)
                self._position      = operand % od.OperandData( ot.Position() )
                self._length        = operand % od.OperandData( ot.Length() )
                self._amplitude     = operand % od.OperandData( ov.Amplitude() )
                self._offset        = operand % od.OperandData( ov.Offset() )
            case ot.Position():     self._position = operand
            case ot.Length():       self._length = operand
            case ov.Amplitude():    self._amplitude = operand
            case ov.Offset():       self._offset = operand
            case _: super().__lshift__(operand)
        return self

    def __or__(self, operand: 'Operand') -> 'Operand':
        operand = super().__or__(operand)
        match operand:
            case oc.Sequence():
                for single_element in operand:
                    self | single_element
            case oe.Element():
                element_position: ot.Position = operand % ot.Position()
                wave_time_rational = element_position.getTime_rational() - self._position.getTime_rational()
                wavelength_rational = self._length.getTime_rational()
                wave_time_angle = wave_time_rational / wavelength_rational * 360 # degrees
                # int * float results in a float
                # Fraction * float results in a float
                # Fraction * Fraction results in a Fraction
                wave_time_amplitude_int = round(self._amplitude % Fraction() * math.sin(math.radians(wave_time_angle)))
                wave_time_amplitude_int += self._offset % int()
                if isinstance(self._operand, Operand):
                    operand << (self._operand.copy() << wave_time_amplitude_int)
                else:
                    operand << wave_time_amplitude_int
        return operand

class Line(Operator):
    ...
