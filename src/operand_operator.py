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
import operand as o
import operand_time as ot
import operand_value as ov
import operand_data as od
import operand_label as ol
import operand_frame as of
import operand_container as oc
import operand_element as oe



class Operator(o.Operand):
    """
    An Operator processes an Operand with an Integer input and an Operand output.

    Parameters
    ----------
    first : o.Operand_like
        A Operand to be regulated
    """
    def __init__(self, operand: o.Operand = None):
        super().__init__()
        self._operand = int() if operand is None else operand
        self._operator_list: list[Operator] = []

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case list():            return self._operator_list
                    case o.Operand():       return self._operand
                    case ol.Null() | None:  return ol.Null()
                    case _:                 return self
            case of.Frame():        return self % (operand % o.Operand())
            case list():            return self._operator_list.copy()
            # case list():            return self._operator_list.copy()
            case ol.Null() | None:  return ol.Null()
            case o.Operand():       return self._operand.copy()
            case _:                 return self.copy()

    def __eq__(self, other_operator: 'Operator') -> bool:
        if type(self) == type(other_operator):
            return  self._operator_list == other_operator % od.DataSource( list() ) \
                and self._operand == other_operator % od.DataSource( o.Operand() )
        return False
    
    def getSerialization(self):
        operators_serialization = []
        for single_operator in self % list():
            operators_serialization.append(single_operator.getSerialization())
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "operand":          self._operand.getSerialization(),
                "operator_list":    operators_serialization
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "operand" in serialization["parameters"] and "class" in serialization["parameters"]["operand"] and "parameters" in serialization["parameters"]["operand"]
            and "operator_list" in serialization["parameters"]):

            self._operand = o.Operand().loadSerialization(serialization["parameters"]["operand"])
            operator_list = []
            operators_serialization = serialization["parameters"]["operator_list"]
            for single_operator_serialization in operators_serialization:
                operator_class_name = single_operator_serialization["class"]
                single_operator = self.getOperand(operator_class_name)
                if single_operator: operator_list.append( single_operator.loadSerialization(single_operator_serialization) )
            self._operator_list = operator_list
        return self
  
    def __lshift__(self, operand: o.Operand) -> 'Operator':
        if isinstance(operand, of.Frame):
            operand &= self         # The Frame MUST be apply the the root self and not the tailed self operand
        operand = self & operand    # Processes the tailed self operands if existent
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case list():            self._operator_list = operand % o.Operand()
                    case _:                 self._operand = operand % o.Operand()
            case Operator():
                operator_list = []
                for single_operator in operand % od.DataSource( list() ):
                    operator_list.append(single_operator.copy())
                self._operator_list = operator_list
                self._operand       = (operand % od.DataSource( o.Operand() )).copy()
            case of.Frame():        self << (operand & self)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                operator_list = []
                for single_operator in operand:
                    operator_list.append(single_operator.copy())
                self._operator_list = operator_list
            case o.Operand():       self._operand << operand
            case ol.Null() | None:  return self
            case _:                 self._operand = operand
        return self

    def __or__(self, operand: any):
        match operand:
            case Operator():
                self._operator_list.insert(operand)
                return self
            case o.Operand():
                for single_operator in self._operator_list:
                    operand = single_operator | operand
                # self._operator_list = []    # Saved operators are used only once
        return operand

    def __ror__(self, operand: o.Operand) -> o.Operand:
        return self.__or__(operand)

class Oscillator(Operator):
    """
    This Operator has a function returns the given Operand regulated accordingly to the Oscillator parameters.

    Parameters
    ----------
    first : o.Operand_like
        A Operand to be regulated
    """
    def __init__(self, operand: o.Operand = None):
        super().__init__(operand)
        self._position: ot.Position     = ot.Position()
        self._length: ot.Length         = ot.Length() << ov.Measure(1)  # wavelength (360º)
        self._amplitude: ov.Amplitude   = ov.Amplitude(0)
        self._offset: ov.Offset         = ov.Offset(0)
        
    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ot.Position():         return self._position
                    case ot.Length():           return self._length
                    case ov.Amplitude():        return self._amplitude
                    case ov.Offset():           return self._offset
                    case _:                     return super().__mod__(operand)
            case ot.Position():         return self._position.copy()
            case ot.Length():           return self._length.copy()
            case ov.Amplitude():        return self._amplitude.copy()
            case ov.Offset():           return self._offset.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_operator: 'Operator') -> bool:
        if super().__eq__(other_operator):
            return  self._position == other_operator % od.DataSource( ot.Position() ) \
                and self._length == other_operator % od.DataSource( ot.Length() ) \
                and self._amplitude == other_operator % od.DataSource( ov.Amplitude() ) \
                and self._offset == other_operator % od.DataSource( ov.Offset() )
        return False
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["position"]     = self._position.getSerialization()
        element_serialization["parameters"]["length"]       = self._length.getSerialization()
        element_serialization["parameters"]["amplitude"]    = self._amplitude % od.DataSource( float() )
        element_serialization["parameters"]["offset"]       = self._offset % od.DataSource( float() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Oscillator':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "length" in serialization["parameters"] and
            "amplitude" in serialization["parameters"] and "offset" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position  = ot.Position().loadSerialization(serialization["parameters"]["position"])
            self._length    = ot.Length().loadSerialization(serialization["parameters"]["length"])
            self._amplitude = ov.Amplitude()    << od.DataSource( serialization["parameters"]["amplitude"] )
            self._offset    = ov.Offset()       << od.DataSource( serialization["parameters"]["offset"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Oscillator':
        if isinstance(operand, of.Frame):
            operand &= self         # The Frame MUST be apply the the root self and not the tailed self operand
        operand = self & operand    # Processes the tailed self operands if existent
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ot.Position():     self._position = operand % o.Operand()
                    case ot.Length():       self._length = operand % o.Operand()
                    case ov.Amplitude():    self._amplitude = operand % o.Operand()
                    case ov.Offset():       self._offset = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case Oscillator():
                super().__lshift__(operand)
                self._position      = (operand % od.DataSource( ot.Position() )).copy()
                self._length        = (operand % od.DataSource( ot.Length() )).copy()
                self._amplitude     = (operand % od.DataSource( ov.Amplitude() )).copy()
                self._offset        = (operand % od.DataSource( ov.Offset() )).copy()
            case ot.Position():     self._position << operand
            case ot.Length():       self._length << operand
            case ov.Amplitude():    self._amplitude << operand
            case ov.Offset():       self._offset << operand
            case _: super().__lshift__(operand)
        return self

    def __or__(self, operand: any):
        operand = super().__or__(operand)
        match operand:
            case oc.Sequence():
                for single_element in operand:
                    self | single_element
            case oe.Element() | ot.Position():
                element_position: ot.Position = operand % ot.Position()
                wave_time_rational = element_position.getTime_rational() - self._position.getTime_rational()
                wavelength_rational = self._length.getTime_rational()
                wave_time_angle = wave_time_rational / wavelength_rational * 360 # degrees
                # int * float results in a float
                # Fraction * float results in a float
                # Fraction * Fraction results in a Fraction
                wave_time_amplitude_int = round(self._amplitude % Fraction() * math.sin(math.radians(wave_time_angle)))
                wave_time_amplitude_int += self._offset % int()
                if isinstance(self._operand, o.Operand):
                    operand << (self._operand.copy() << wave_time_amplitude_int)
                else:
                    operand << wave_time_amplitude_int
        return operand

class Line(Operator):
    ...
