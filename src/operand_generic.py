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

class KeySignature(Generic):       # Sharps (+) and Flats (-)
    def __init__(self, accidentals: int | str = 0):
        super().__init__()
        self._accidentals: int = 0
        match accidentals:
            case str():
                total_sharps = accidentals.count('#')
                total_flats = accidentals.count('b')
                num_accidentals = total_sharps - total_flats
                # Number of accidentals should range between -7 and +7
                if -7 <= num_accidentals <= 7:
                    self._accidentals = num_accidentals
            case int() | float():
                num_accidentals = int(accidentals)
                # Number of accidentals should range between -7 and +7
                if -7 <= num_accidentals <= 7:
                    self._accidentals = num_accidentals
        self._scale: list = KeySignature.get_key_signed_scale(self._accidentals)
    
    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case KeySignature():        return self
                    case int():                 return self._accidentals
                    case list():                return self._scale
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            case KeySignature():        return self.copy()
            case int():                 return self._accidentals
            case list():                return self._scale.copy()
            case _:                     return super().__mod__(operand)

    def moveKey(self, start_key: int, move_keys: int) -> int:
        next_key = start_key
        while move_keys > 0:
            next_key += 1
            if self._scale[next_key % 12]:
                move_keys -= 1
        while move_keys < 0:
            next_key -= 1
            if self._scale[next_key % 12]:
                move_keys += 1
        return next_key

    def __eq__(self, other_key_signature: 'KeySignature') -> bool:
        if type(self) != type(other_key_signature):
            return False
        return  self._accidentals   == other_key_signature._accidentals \
            and self._scale         == other_key_signature._scale
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "accidentals":  self._accidentals,
                "scale":        self._scale
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "accidentals" in serialization["parameters"] and "scale" in serialization["parameters"]):

            self._accidentals   = serialization["parameters"]["accidentals"]
            self._scale         = serialization["parameters"]["scale"]
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'KeySignature':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():     self._accidentals   = operand % o.Operand()
                    case list():    self._scale         = operand % o.Operand()
            case KeySignature():
                self._accidentals       = operand._accidentals
                self._scale             = operand._scale
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case int():     self._accidentals   = operand
            case list():    self._scale         = operand.copy()
        return self

    @staticmethod
    def get_key_signed_scale(num_accidentals: int) -> list:
        # Base pattern for C Major scale (no sharps or flats)
        base_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # C Major
        rotated_scale = base_scale

        # Number of accidentals should range between -7 and +7
        if -7 <= num_accidentals <= 7:
        
            # Calculate rotation based on the number of sharps/flats
            if num_accidentals > 0:
                # Positive means sharps; rotate to the right
                rotated_scale = base_scale[-num_accidentals:] + base_scale[:-num_accidentals]
            elif num_accidentals < 0:
                # Negative means flats; rotate to the left
                num_accidentals = abs(num_accidentals)
                rotated_scale = base_scale[num_accidentals:] + base_scale[:num_accidentals]

        return rotated_scale

class Key(Generic):
    """
    A Key() is an integer from 0 to 11 that describes the 12 keys of an octave.
    
    Parameters
    ----------
    first : integer_like or string_like
        A number from 0 to 11 with 0 as default or the equivalent string key "C"
    """
    def __init__(self, key: int | str = None):
        super().__init__()
        self._key: int          = 0
        self._static: bool      = False

        self._sharp: ou.Sharp       = ou.Sharp()
        self._flat: ou.Flat         = ou.Flat()
        self._natural:ou.Natural    = ou.Natural()
        match key:
            case str():
                total_sharps = key.count('#')
                key.replace('#', '')
                total_flats = key.count('b')
                key.replace('b', '')
                self._sharp << total_sharps
                self._flat << total_flats
                self._key = Key.key_to_int(key)
            case int() | float():
                self._key = int(key) % 12

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract the Unit, because a Unit is an Integer
        it should be used in conjugation with int(). If used with a float() it
        will return the respective key formatted as a float.

        Examples
        --------
        >>> channel_int = Channel(12) % int()
        >>> print(channel_int)
        12
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case Key():             return self
                    case ou.Sharp():        return self._sharp
                    case ou.Flat():         return self._flat
                    case ou.Natural():      return self._natural
                    case Fraction():        return Fraction(self._key).limit_denominator()
                    case int():             return self._key           # returns a int()
                    case bool():            return self._static        # returns a bool()
                    case float():           return float(self._key)
                    case ou.Integer():      return ou.Integer() << od.DataSource( self._key )
                    case ro.Float():        return ro.Float() << od.DataSource( self._key )
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Key():             return self.copy()
            case ou.Sharp():        return self._sharp.copy()
            case ou.Flat():         return self._flat.copy()
            case ou.Natural():      return self._natural.copy()
            case str():             return Key.int_to_key(self._key)
            case int():
                self_key_note_transpose_int = 0
                if self._natural == 0:
                    self_key_note_transpose_int = (self._sharp - self._flat) % od.DataSource( int() )
                return self._key + self_key_note_transpose_int
            case bool():            return self._static        # returns a bool()
            case float():           return float(self._key)
            case Fraction():        return Fraction(self._key).limit_denominator()
            case ou.Integer():      return ou.Integer() << self._key
            case ro.Float():        return ro.Float() << self._key
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_key: any) -> bool:
        return self % int() == other_key % int()
    
    def __lt__(self, other_key: any) -> bool:
        return self % int() < other_key % int()
    
    def __gt__(self, other_key: any) -> bool:
        return self % int() > other_key % int()
    
    def __le__(self, other_key: any) -> bool:
        return self == other_key or self < other_key
    
    def __ge__(self, other_key: any) -> bool:
        return self == other_key or self > other_key
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "key": self._key,
                "static": self._static,
                "flat": self._flat % od.DataSource( int() ),
                "sharp": self._sharp % od.DataSource( int() ),
                "natural": self._natural % od.DataSource( int() )
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key" in serialization["parameters"] and "static" in serialization["parameters"] and "flat" in serialization["parameters"] and "sharp" in serialization["parameters"] and "natural" in serialization["parameters"]):

            self._key       = serialization["parameters"]["key"]
            self._static    = serialization["parameters"]["static"]
            self._flat      = ou.Flat()     << serialization["parameters"]["flat"]
            self._sharp     = ou.Sharp()    << serialization["parameters"]["sharp"]
            self._natural   = ou.Natural()  << serialization["parameters"]["natural"]
        return self

    def __lshift__(self, operand: o.Operand) -> 'Key':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():                     self._key = operand % o.Operand() % 12
                    case bool():                    self._static = operand % o.Operand()
                    case float() | Fraction():      self._key = int(operand % o.Operand()) % 12
                    case ou.Semitone() | ou.Integer() | ro.Float():
                                                    self._key = operand % o.Operand() % od.DataSource( int() ) % 12
                    case ou.Sharp():                self._sharp = operand
                    case ou.Flat():                 self._flat = operand
                    case ou.Natural():              self._natural = operand
                    case str():
                                                    total_sharps = operand.count('#')
                                                    operand.replace('#', '')
                                                    total_flats = operand.count('b')
                                                    operand.replace('b', '')
                                                    self._sharp << total_sharps
                                                    self._flat << total_flats
                                                    self._key = Key.key_to_int(operand)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Key():
                                    self._key       =  operand % od.DataSource( int() )
                                    self._sharp     = (operand % od.DataSource( ou.Sharp() )).copy()
                                    self._flat      = (operand % od.DataSource( ou.Flat() )).copy()
                                    self._natural   = (operand % od.DataSource( ou.Natural() )).copy()
            case ou.Sharp():        self._sharp << operand
            case ou.Flat():         self._flat << operand
            case ou.Natural():      self._natural << operand
            case ou.Semitone() | ou.Integer() | ro.Float():
                                    self._key = operand % int() % 12
            case int() | float() | Fraction():
                                    self._key = int(operand) % 12
            case bool():            self._static = operand
            case str():
                                    total_sharps = operand.count('#')
                                    operand.replace('#', '')
                                    total_flats = operand.count('b')
                                    operand.replace('b', '')
                                    self._sharp << total_sharps
                                    self._flat << total_flats
                                    self._key = Key.key_to_int(operand)
        return self

    def __add__(self, number: any) -> 'Key':
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case self.__class__() | ou.Semitone() | ou.Integer() | ro.Float():
                                        return self.copy() << od.DataSource( self._key + number % od.DataSource( int() ) )
            case int() | float() | Fraction():
                                        return self.copy() << od.DataSource( self._key + number )
        return self.copy()
    
    def __sub__(self, number: any) -> 'Key':
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case self.__class__() | ou.Semitone() | ou.Integer() | ro.Float():
                                        return self.copy() << od.DataSource( self._key - number % od.DataSource( int() ) )
            case int() | float() | Fraction():
                                        return self.copy() << od.DataSource( self._key - number )
        return self.copy()
    
    _keys: list[str] = ["C",  "C#", "D", "D#", "E",  "F",  "F#", "G", "G#", "A", "A#", "B",
                        "B#", "Db", "D", "Eb", "Fb", "E#", "Gb", "G", "Ab", "A", "Bb", "Cb"]
    
    @staticmethod
    def int_to_key(note_key: int = 0) -> str:
        return Key._keys[note_key % 12]

    @staticmethod
    def key_to_int(key: str = "C") -> int:
        for key_i in range(len(Key._keys)):
            if Key._keys[key_i].lower().find(key.strip().lower()) != -1:
                return key_i % 12
        return 0

class Root(Key):
    pass

class Home(Key):
    pass

class Tonic(Key):
    pass

class KeyNote(Key):
    def __init__(self, key: int | str = None):
        super().__init__(key)
        self._octave: ou.Octave     = ou.Octave()

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
                    case ou.Midi():
                        octave_int = self._octave % od.DataSource( int() )
                        key_int = super().__mod__( int() )
                        return ou.Midi() << 12 * (octave_int + 1) + key_int
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % (operand % o.Operand())
            case KeyNote():         return self.copy()
            case ou.Octave():       return self._octave.copy()
            case ou.Midi():
                octave_int = self._octave % od.DataSource( int() )
                key_int = super().__mod__( int() )
                return ou.Midi() << 12 * (octave_int + 1) + key_int
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_keynote: 'KeyNote') -> bool:
        if self % ou.Octave() == other_keynote % ou.Octave() and super().__eq__(other_keynote):
            return True
        return False
    
    def __lt__(self, other_keynote: 'KeyNote') -> bool:
        if self % ou.Octave() < other_keynote % ou.Octave():    return True
        if self % ou.Octave() > other_keynote % ou.Octave():    return False
        if super().__lt__(other_keynote):                       return True
        return False
    
    def __gt__(self, other_keynote: 'KeyNote') -> bool:
        if self % ou.Octave() > other_keynote % ou.Octave():    return True
        if self % ou.Octave() < other_keynote % ou.Octave():    return False
        if super().__gt__(other_keynote):                       return True
        return False
    
    def __le__(self, other_keynote: 'KeyNote') -> bool:
        return self == other_keynote or self < other_keynote
    
    def __ge__(self, other_keynote: 'KeyNote') -> bool:
        return self == other_keynote or self > other_keynote
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["octave"]   = self._octave % od.DataSource( float() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "octave" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._octave      = ou.Octave() << od.DataSource( serialization["parameters"]["octave"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'KeyNote':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Octave():       self._octave = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case KeyNote():
                super().__lshift__(operand)
                self._octave = (operand % od.DataSource( ou.Octave() )).copy()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Octave():   self._octave << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand) -> 'KeyNote':
        key_int: int = self._key
        octave_int: int = self._octave % od.DataSource( int() )
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyNote():
                key_int += operand % od.DataSource( int() )
                octave_int += operand % ou.Octave() % od.DataSource( int() ) + key_int // 12
            case ou.Octave():
                octave_int += operand % od.DataSource( int() )
            case Key():
                key_int += operand % int()
            case int():
                key_int += operand
                octave_int += key_int // 12
            case float() | Fraction():
                key_int += round(operand)
                octave_int += key_int // 12
            case ou.Semitone() | ou.Integer() | ro.Rational() | ro.Float():
                key_int += operand % od.DataSource( int() )
                octave_int += key_int // 12
            case _: return super().__add__(operand)
        return self.copy() << key_int << (ou.Octave() << octave_int)
     
    def __sub__(self, operand) -> 'KeyNote':
        key_int: int = self._key
        octave_int: int = self._octave % od.DataSource( int() )
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyNote():
                key_int -= operand % od.DataSource( int() )
                octave_int -= operand % ou.Octave() % od.DataSource( int() ) - max(-1 * key_int + 11, 0) // 12
            case ou.Octave():
                octave_int -= operand % od.DataSource( int() )
            case Key():
                key_int -= operand % int()
            case int():
                key_int -= operand
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case float():
                key_int -= round(operand)
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case ou.Semitone() | ou.Integer() | ro.Rational() | ro.Float():
                key_int -= operand % od.DataSource( int() )
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case _: return super().__sub__(operand)
        return self.copy() << key_int << (ou.Octave() << octave_int)

class Controller(Generic):
    def __init__(self, number: int | str = None):
        super().__init__()
        self._number: ou.Number  = ou.Number( number )
        self._value: ou.Value    = ou.Value( ou.Number.getDefault(self._number % od.DataSource( int() )) )

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

    def __eq__(self, other: 'Controller') -> bool:
        if self % ou.Number() == other % ou.Number() and self % ou.Value() == other % ou.Value():
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
                self._number = (operand % od.DataSource( ou.Number() )).copy()
                self._value = (operand % od.DataSource( ou.Value() )).copy()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Number():    self._number << operand
            case ou.Value() | int() | float():
                                        self._value << operand
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
