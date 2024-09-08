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
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_staff as os
import operand_unit as ou
import operand_rational as ro
import operand_data as od
import operand_frame as of
import operand_label as ol


class Generic(o.Operand):
    pass

class KeyNote(Generic):
    def __init__(self, key: int | str = None):
        super().__init__()
        self._key: ou.Key = ou.Key(key)
        self._octave: ou.Octave = ou.Octave()

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a KeyNote,
        those Parameters are the Key and the Octave.

        Examples
        --------
        >>> key_note = KeyNote()
        >>> key_note % Key() >> Print(0)
        {'class': 'Key', 'parameters': {'unit': 0}}
        >>> key_note % Key() % str() >> Print(0)
        C
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case ou.Key():          return self._key
                    case ou.Octave():       return self._octave
                    case int():
                        key = self._key % od.DataSource( int() )
                        octave = self._octave % od.DataSource( int() )
                        return 12 * (octave + 1) + key
                    case KeyNote():         return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case ou.Key():          return self._key.copy()
            case ou.Octave():       return self._octave.copy()
            case int():
                key = self._key % int()
                octave = self._octave % int()
                return 12 * (octave + 1) + key
            case KeyNote():         return self.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_keynote: 'KeyNote') -> bool:
        if self % ou.Octave() == other_keynote % ou.Octave() and self % ou.Key() == other_keynote % ou.Key():
            return True
        return False
    
    def __lt__(self, other_keynote: 'KeyNote') -> bool:
        if self % ou.Octave() < other_keynote % ou.Octave():    return True
        if self % ou.Octave() > other_keynote % ou.Octave():    return False
        if self % ou.Key() < other_keynote % ou.Key():          return True
        return False
    
    def __gt__(self, other_keynote: 'KeyNote') -> bool:
        if self % ou.Octave() > other_keynote % ou.Octave():    return True
        if self % ou.Octave() < other_keynote % ou.Octave():    return False
        if self % ou.Key() > other_keynote % ou.Key():          return True
        return False
    
    def __le__(self, other_keynote: 'KeyNote') -> bool:
        return self == other_keynote or self < other_keynote
    
    def __ge__(self, other_keynote: 'KeyNote') -> bool:
        return self == other_keynote or self > other_keynote
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "key":      self._key % od.DataSource( int() ),
                "octave":   self._octave % od.DataSource( int() )
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key" in serialization["parameters"] and "octave" in serialization["parameters"]):

            self._key       = ou.Key()      << od.DataSource( serialization["parameters"]["key"] )
            self._octave    = ou.Octave()   << od.DataSource( serialization["parameters"]["octave"] )
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'KeyNote':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Key():          self._key = operand % o.Operand()
                    case ou.Octave():       self._octave = operand % o.Operand()
            case KeyNote():
                self._key = (operand % od.DataSource( ou.Key() )).copy()
                self._octave = (operand % od.DataSource( ou.Octave() )).copy()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Key() | str():  self._key << operand
            case ou.Octave():       self._octave << operand
            case int():
                self._key       << operand      # key << already does % 12
                self._octave    << operand // 12
            case float():
                number = round(operand)
                self._key       << number       # key << already does % 12
                self._octave    << number // 12
            case ou.Unit() | ro.Rational():
                number = operand % od.DataSource( int() )
                self._key       << number       # key << already does % 12
                self._octave    << number // 12
        return self

    def __add__(self, operand) -> 'KeyNote':
        key_int: int = self._key % od.DataSource( int() )
        octave_int: int = self._octave % od.DataSource( int() )
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyNote():
                key_int += operand % ou.Key() % od.DataSource( int() )
                octave_int += operand % ou.Octave() % od.DataSource( int() ) + key_int // 12
            case ou.Key():
                key_int += operand % od.DataSource( int() )
            case ou.Octave():
                octave_int += operand % od.DataSource( int() )
            case int():
                key_int += operand
                octave_int += key_int // 12
            case float() | Fraction():
                key_int += round(operand)
                octave_int += key_int // 12
            case ou.Integer() | ro.Float():
                key_int += operand % od.DataSource( int() )
                octave_int += key_int // 12
            case _: return self.copy()
        return KeyNote() << (ou.Key() << key_int) << (ou.Octave() << octave_int)
     
    def __sub__(self, operand) -> 'KeyNote':
        key_int: int = self._key % od.DataSource( int() )
        octave_int: int = self._octave % od.DataSource( int() )
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyNote():
                key_int -= operand % ou.Key() % od.DataSource( int() )
                octave_int -= operand % ou.Octave() % od.DataSource( int() ) - max(-1 * key_int + 11, 0) // 12
            case ou.Key():
                key_int -= operand % od.DataSource( int() )
            case ou.Octave():
                octave_int -= operand % od.DataSource( int() )
            case int():
                key_int -= operand
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case float():
                key_int -= round(operand)
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case ou.Unit() | ro.Rational():
                key_int -= operand % od.DataSource( int() )
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case _: return self.copy()
        return KeyNote() << (ou.Key() << key_int) << (ou.Octave() << octave_int)

class Controller(Generic):
    def __init__(self, number: int | str = None):
        super().__init__()
        self._control_number: ou.Number  = ou.Number( number )
        self._control_value: ou.Value    = ou.Value( ou.Number.getDefault(self._control_number % od.DataSource( int() )) )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Controller,
        those Parameters are the Controller Number and Value.

        Examples
        --------
        >>> controller = Controller()
        >>> controller % Number() >> Print(0)
        {'class': 'Key', 'parameters': {'unit': 0}}
        >>> controller % Value() >> Print(0)
        C
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case ou.Number():           return self._control_number
                    case ou.Value():            return self._control_value
                    case Controller():          return self
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            case ou.Number():           return self._control_number.copy()
            case ou.Value():            return self._control_value.copy()
            case int() | float():       return self._control_value % int()
            case Controller():          return self.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Controller') -> bool:
        if self % ou.Number() == other % ou.Number() and self % ou.Value() == other % ou.Value():
            return True
        return False
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "control_number":   self._control_number % od.DataSource( int() ),
                "control_value":    self._control_value % od.DataSource( int() )
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "control_number" in serialization["parameters"] and "control_value" in serialization["parameters"]):

            self._control_number    = ou.Number()    << od.DataSource( serialization["parameters"]["control_number"] )
            self._control_value     = ou.Value()     << od.DataSource( serialization["parameters"]["control_value"] )
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Controller':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Number():    self._control_number = operand % o.Operand()
                    case ou.Value():     self._control_value = operand % o.Operand()
            case Controller():
                self._control_number = (operand % od.DataSource( ou.Number() )).copy()
                self._control_value = (operand % od.DataSource( ou.Value() )).copy()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Number():    self._control_number << operand
            case ou.Value() | int() | float():
                                        self._control_value << operand
        return self

    def __add__(self, operand) -> 'Controller':
        control_value: ou.Value = self._control_value
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Controller():
                control_value += operand % ou.Value() % int()
            case ou.Value():
                control_value += operand % int()
            case int() | float() | ou.Integer() | ro.Float() | Fraction():
                control_value += operand
            case _:
                return self.copy()
        return self.copy() << control_value
    
    def __sub__(self, operand) -> 'Controller':
        control_value: ou.Value = self._control_value
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Controller():
                control_value -= operand % ou.Value() % int()
            case ou.Value():
                control_value -= operand % int()
            case int() | float() | ou.Integer() | ro.Float() | Fraction():
                control_value -= operand
            case _:
                return self.copy()
        return self.copy() << control_value
