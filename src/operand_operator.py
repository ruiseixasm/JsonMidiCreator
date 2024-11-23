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
import operand_rational as ra
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
        """
        The % symbol is used to extract a Parameter, in the case of a Operator,
        those Parameters are the Operator's Operand and the list of chained Operators.

        Examples
        --------
        >>> operator = Operator(Key())
        >>> operator % Operand() >> Print(0)
        {'class': 'Key', 'parameters': {'unit': 0}}
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case list():            return self._operator_list
                    case Operator():        return self
                    case ol.Null() | None:  return ol.Null()
                    case o.Operand():       return self._operand
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case list():            return self._operator_list.copy()
            # case list():            return self._operator_list.copy()
            case Operator():        return self.copy()
            case ol.Null() | None:  return ol.Null()
            case o.Operand():       return self._operand.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: 'Operator') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) == type(other):
            return  self._operator_list == other % od.DataSource( list() ) \
                and self._operand == other % od.DataSource( o.Operand() )
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["operand"]       = self.serialize( self._operand )
        serialization["parameters"]["operator_list"] = self.serialize(self._operator_list)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Operator':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "operand" in serialization["parameters"] and "class" in serialization["parameters"]["operand"] and "parameters" in serialization["parameters"]["operand"]
            and "operator_list" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._operand = self.deserialize( serialization["parameters"]["operand"] )
            self._operator_list = self.deserialize(serialization["parameters"]["operator_list"])
        return self
  
    def __lshift__(self, operand: o.Operand) -> 'Operator':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case list():            self._operator_list = operand % o.Operand()
                    case _:                 self._operand = operand % o.Operand()
            case Operator():
                super().__lshift__(operand)
                operator_list = []
                for single_operator in operand % od.DataSource( list() ):
                    operator_list.append(single_operator.copy())
                self._operator_list = operator_list
                self._operand       = (operand % od.DataSource( o.Operand() )).copy()
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
        self._length: ot.Length         = ot.Length() << ra.Measure(1)  # wavelength (360º)
        self._amplitude: ra.Amplitude   = ra.Amplitude(0)
        self._offset: ra.Offset         = ra.Offset(0)
        
    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Oscillator,
        those Parameters are the Oscillator's Operand and the list of chained Operators.

        Examples
        --------
        >>> oscillator = Oscillator(Velocity())
        >>> oscillator % Operand() >> Print(0)
        {'class': 'Velocity', 'parameters': {'unit': 0}}
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ot.Position():         return self._position
                    case ot.Length():           return self._length
                    case ra.Amplitude():        return self._amplitude
                    case ra.Offset():           return self._offset
                    case _:                     return super().__mod__(operand)
            case ot.Position():         return self._position.copy()
            case ot.Length():           return self._length.copy()
            case ra.Amplitude():        return self._amplitude.copy()
            case ra.Offset():           return self._offset.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Operator') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if super().__eq__(other):
            return  self._position == other % od.DataSource( ot.Position() ) \
                and self._length == other % od.DataSource( ot.Length() ) \
                and self._amplitude == other % od.DataSource( ra.Amplitude() ) \
                and self._offset == other % od.DataSource( ra.Offset() )
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["position"]     = self.serialize( self._position )
        serialization["parameters"]["length"]       = self.serialize( self._length )
        serialization["parameters"]["amplitude"]    = self.serialize( self._amplitude )
        serialization["parameters"]["offset"]       = self.serialize( self._offset )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Oscillator':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "length" in serialization["parameters"] and
            "amplitude" in serialization["parameters"] and "offset" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position  = self.deserialize( serialization["parameters"]["position"] )
            self._length    = self.deserialize(serialization["parameters"]["length"])
            self._amplitude = self.deserialize( serialization["parameters"]["amplitude"] )
            self._offset    = self.deserialize( serialization["parameters"]["offset"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Oscillator':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ot.Position():     self._position = operand % o.Operand()
                    case ot.Length():       self._length = operand % o.Operand()
                    case ra.Amplitude():    self._amplitude = operand % o.Operand()
                    case ra.Offset():       self._offset = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case Oscillator():
                super().__lshift__(operand)
                self._position      = (operand % od.DataSource( ot.Position() )).copy()
                self._length        = (operand % od.DataSource( ot.Length() )).copy()
                self._amplitude     = (operand % od.DataSource( ra.Amplitude() )).copy()
                self._offset        = (operand % od.DataSource( ra.Offset() )).copy()
            case ot.Position():     self._position << operand
            case ot.Length():       self._length << operand
            case ra.Amplitude():    self._amplitude << operand
            case ra.Offset():       self._offset << operand
            case _: super().__lshift__(operand)
        return self

    def __or__(self, operand: any):
        operand = super().__or__(operand)
        match operand:
            case oc.Sequence():
                for single_data in operand:
                    self | single_data
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
                    operand << (self._operand << wave_time_amplitude_int)
                else:
                    operand << wave_time_amplitude_int
        return operand

class Line(Operator):
    ...
