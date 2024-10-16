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

class TimeSignature(Generic):
    def __init__(self, top: int = 4, bottom: int = 4):
        super().__init__()
        self._top: int      = 4 if top is None else top
        self._bottom: int   = 4 if bottom is None else bottom

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case TimeSignature():       return self
                    case ro.BeatsPerMeasure():  return ro.BeatsPerMeasure() << self._top
                    case ro.BeatNoteValue():    return ro.BeatNoteValue() << 1 / self._bottom
                    # Calculated Values
                    case ro.NotesPerMeasure():  return ro.NotesPerMeasure() << self._top / self._bottom
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            case TimeSignature():       return self.copy()
            # Direct Values
            case ro.BeatsPerMeasure():  return ro.BeatsPerMeasure() << self._top
            case ro.BeatNoteValue():    return ro.BeatNoteValue() << 1 / self._bottom
            # Calculated Values
            case ro.NotesPerMeasure():  return ro.NotesPerMeasure() << self._top / self._bottom
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_time_signature: 'TimeSignature') -> bool:
        other_time_signature = self & other_time_signature    # Processes the tailed self operands or the Frame operand if any exists
        if other_time_signature.__class__ == o.Operand:
            return True
        if type(self) != type(other_time_signature):
            return False
        return  self._top           == other_time_signature._top \
            and self._bottom        == other_time_signature._bottom
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "top":          self._top,
                "bottom":       self._bottom
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "top" in serialization["parameters"] and "bottom" in serialization["parameters"]):

            self._top           = serialization["parameters"]["top"]
            self._bottom        = serialization["parameters"]["bottom"]
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'TimeSignature':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ro.BeatsPerMeasure():  self._top       = operand % o.Operand() % od.DataSource( int() )
                    case ro.BeatNoteValue():    self._bottom    = round(1 / (operand % o.Operand() % od.DataSource( int() )))
            case TimeSignature():
                self._top               = operand._top
                self._bottom            = operand._bottom
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ro.BeatsPerMeasure():  self._top       = operand % o.Operand() % int()
            case ro.BeatNoteValue():    self._bottom    = round(1 / (operand % o.Operand() % int()))
        return self

class KeyNote(Generic):
    def __init__(self, *parameters):
        super().__init__()
        self._octave: ou.Octave     = ou.Octave()
        self._key: ou.Key           = ou.Key()
        self._natural: ou.Natural   = ou.Natural()
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a KeyNote,
        those Parameters are the Key and the Octave.

        Examples
        --------
        >>> key_note = KeyNote()
        >>> key_note % Key() >> Print(0)
        {'class': 'Key', 'parameters': {'key': 0}}
        >>> key_note % Key() % str() >> Print(0)
        C
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case KeyNote():         return self
                    case ou.Octave():       return self._octave
                    case ou.Key():          return self._key
                    case ou.Natural():      return self._natural
                    case int():
                        octave_int: int     = self._octave._unit
                        key_int: int        = self._key._unit
                        not_natural: bool   = self._natural._unit == 0
                        if not_natural:
                            key_signature: ou.KeySignature = os.staff._key_signature
                            key_int += (key_signature % list())[key_int]    # already % 12
                        key_degree: ou.Key = self._key.copy() << key_int
                        return 12 * (octave_int + 1) + key_int
                        # return 12 * (octave_int + 1) + key_degree.getKeyDegree() % int()
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case KeyNote():         return self.copy()
            case ou.Octave():       return self._octave.copy()
            case ou.Key():          return self._key.copy()
            case ou.Flat():         return self._key % ou.Flat()
            case ou.Natural():      return self._natural.copy()
            case int():
                octave_int: int     = self._octave._unit
                key_int: int        = self._key._unit
                not_natural: bool   = self._natural._unit == 0
                if not_natural:
                    key_signature: ou.KeySignature = os.staff._key_signature
                    key_int += (key_signature % list())[key_int]    # already % 12
                key_degree: ou.Key = self._key.copy() << key_int
                return 12 * (octave_int + 1) + key_int
                # return 12 * (octave_int + 1) + key_degree.getKeyDegree() % int()
            case _:                 return super().__mod__(operand)

    def __eq__(self, operand: any) -> bool:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        if operand.__class__ == o.Operand:
            return True
        match operand:
            case KeyNote():
                return self % int() == operand % int()
            case str() | ou.Key():
                return self._key    == operand
            case int() | ou.Octave():
                return self._octave == operand
        return False
    
    def __lt__(self, operand: any) -> bool:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyNote():
                return self % int() < operand % int()
            case str() | ou.Key():
                return self._key    < operand
            case int() | ou.Octave():
                return self._octave < operand
        return False
    
    def __gt__(self, operand: any) -> bool:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyNote():
                return self % int() > operand % int()
            case str() | ou.Key():
                return self._key    > operand
            case int() | ou.Octave():
                return self._octave > operand
        return False
    
    def __le__(self, operand: any) -> bool:
        return self == operand or self < operand
    
    def __ge__(self, operand: any) -> bool:
        return self == operand or self > operand
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "key":      self._key.getSerialization(),
                "octave":   self._octave % od.DataSource( int() ),
                "natural":  self._natural % od.DataSource( int() )
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "octave" in serialization["parameters"] and "key" in serialization["parameters"] and 
            "natural" in serialization["parameters"]):

            self._key       = ou.Key().loadSerialization(serialization["parameters"]["key"])
            self._octave    = ou.Octave()   << od.DataSource( serialization["parameters"]["octave"] )
            self._natural   = ou.Natural()  << od.DataSource( serialization["parameters"]["natural"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'KeyNote':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Octave():       self._octave    = operand % o.Operand()
                    case ou.Key():
                                            self._key       = operand % o.Operand()
                                            self._key._unit %= 12
                    case ou.Natural():      self._natural   = operand % o.Operand()
            case KeyNote():
                self._octave    << operand._octave
                self._key       << operand._key
                self._natural   << operand._natural
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Octave() | int() | ou.Integer():
                self._octave << operand
            case ou.Key() | float() | str() | ou.Semitone():
                self._key << operand
                self._key._unit %= 12
            case ou.Flat():
                self._key << operand
            case ou.Natural():
                self._natural << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __add__(self, operand) -> 'KeyNote':
        key_copy: ou.Key = self._key.copy()
        octave_int: int  = self._octave._unit
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        self_copy: KeyNote = self.copy()
        match operand:
            case KeyNote():
                key_copy += float(operand._key._unit)
                octave_int += operand._octave._unit + key_copy._unit // 12
            case ou.Octave():
                octave_int += operand._unit
            case ou.Key() | int() | float() | Fraction() | ou.Semitone() | ou.Integer() | ro.Rational() | ro.Float():
                key_copy += operand
                octave_int += key_copy._unit // 12
            case _: return super().__add__(operand)
        return self_copy << (ou.Key() << key_copy._unit % 12) << (ou.Octave() << octave_int)
    
    def __sub__(self, operand) -> 'KeyNote':
        key_copy: ou.Key = self._key.copy()
        octave_int: int  = self._octave._unit
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        self_copy: KeyNote = self.copy()
        match operand:
            case KeyNote():
                key_copy -= float(operand._key._unit)
                octave_int -= operand._octave._unit - max(-1 * key_copy._unit + 11, 0) // 12
            case ou.Octave():
                octave_int -= operand._unit
            case ou.Key() | int() | float() | Fraction() | ou.Semitone() | ou.Integer() | ro.Rational() | ro.Float():
                key_copy -= operand
                octave_int -= max(-1 * key_copy._unit + 11, 0) // 12
            case _: return super().__add__(operand)
        return self_copy << (ou.Key() << key_copy._unit % 12) << (ou.Octave() << octave_int)

class Controller(Generic):
    def __init__(self, *parameters):
        super().__init__()
        self._number: ou.Number  = ou.Number()
        self._value: ou.Value    = ou.Value()
        if len(parameters) > 0:
            self << parameters
        self._value: ou.Value    = ou.Value( ou.Number.getDefault(self._number % od.DataSource( int() )) )
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Controller,
        those Parameters are the Controller Number and Value.

        Examples
        --------
        >>> controller = Controller("Balance")
        >>> controller % Number() >> Print(0)
        {'class': 'Number', 'parameters': {'unit': 8}}
        >>> controller % Value() >> Print(0)
        {'class': 'Value', 'parameters': {'unit': 64}}
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case ou.Number():           return self._number
                    case ou.Value():            return self._value
                    case Controller():          return self
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            case ou.Number():           return self._number.copy()
            case ou.Value():            return self._value.copy()
            case int() | float():       return self._value % int()
            case Controller():          return self.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_controller: 'Controller') -> bool:
        other_controller = self & other_controller    # Processes the tailed self operands or the Frame operand if any exists
        if other_controller.__class__ == o.Operand:
            return True
        if self % ou.Number() == other_controller % ou.Number() and self % ou.Value() == other_controller % ou.Value():
            return True
        return False
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "number":   self._number % od.DataSource( int() ),
                "value":    self._value % od.DataSource( int() )
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "number" in serialization["parameters"] and "value" in serialization["parameters"]):

            self._number    = ou.Number()    << od.DataSource( serialization["parameters"]["number"] )
            self._value     = ou.Value()     << od.DataSource( serialization["parameters"]["value"] )
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Controller':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Number():    self._number = operand % o.Operand()
                    case ou.Value():     self._value = operand % o.Operand()
            case Controller():
                self._number    << operand._number
                self._value     << operand._value
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Number() | str():
                self._number << operand
            case ou.Value() | int() | float():
                self._value << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __add__(self, operand) -> 'Controller':
        value: ou.Value = self._value
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Controller():
                value += operand % ou.Value() % int()
            case ou.Value():
                value += operand % int()
            case int() | float() | ou.Integer() | ro.Float() | Fraction():
                value += operand
            case _:
                return self.copy()
        return self.copy() << value
    
    def __sub__(self, operand) -> 'Controller':
        value: ou.Value = self._value
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Controller():
                value -= operand % ou.Value() % int()
            case ou.Value():
                value -= operand % int()
            case int() | float() | ou.Integer() | ro.Float() | Fraction():
                value -= operand
            case _:
                return self.copy()
        return self.copy() << value
