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
import json
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_staff as os
import operand_data as od

import operand_frame as of
import operand_label as ol


# Units have never None values and are also const, with no setters
class Unit(o.Operand):
    """
    This type of Operand is associated to an Integer.
    This class is intended to represent parameters that are whole numbers like midi messages from 0 to 127

    Parameters
    ----------
    first : integer_like
        An Integer described as a Unit
    """
    def __init__(self, unit: int = None):
        super().__init__()
        self._unit: int = 0 if unit is None else int(unit)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract the Unit, because a Unit is an Integer
        it should be used in conjugation with int(). If used with a float() it
        will return the respective unit formatted as a float.

        Examples
        --------
        >>> channel_int = Channel(12) % int()
        >>> print(channel_int)
        12
        """
        import operand_rational as ro
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case Fraction():        return Fraction(self._unit).limit_denominator()
                    case int():             return self._unit           # returns a int()
                    case float():           return float(self._unit)
                    case Integer():         return Integer() << od.DataSource( self._unit )
                    case ro.Float():        return ro.Float() << od.DataSource( self._unit )
                    case Unit():            return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case int():             return self._unit
            case float():           return float(self._unit)
            case Fraction():        return Fraction(self._unit).limit_denominator()
            case Integer():         return Integer() << self._unit
            case ro.Float():        return ro.Float() << self._unit
            case Unit():            return self.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_number: any) -> bool:
        import operand_rational as ro
        other_number = self & other_number    # Processes the tailed self operands or the Frame operand if any exists
        match other_number:
            case Unit():
                return self._unit == other_number._unit
            case ro.Rational():
                self_rational = Fraction( self._unit ).limit_denominator()
                return self_rational == other_number % od.DataSource( Fraction() )
            case int() | float() | Fraction():
                return self._unit == other_number
            case _:
                if other_number.__class__ == o.Operand:
                    return True
        return False
    
    def __lt__(self, other_number: any) -> bool:
        import operand_rational as ro
        other_number = self & other_number    # Processes the tailed self operands or the Frame operand if any exists
        match other_number:
            case Unit():
                return self._unit < other_number._unit
            case ro.Rational():
                self_rational = Fraction( self._unit ).limit_denominator()
                return self_rational < other_number % od.DataSource( Fraction() )
            case int() | float() | Fraction():
                return self._unit < other_number
        return False
    
    def __gt__(self, other_number: any) -> bool:
        import operand_rational as ro
        other_number = self & other_number    # Processes the tailed self operands or the Frame operand if any exists
        match other_number:
            case Unit():
                return self._unit > other_number._unit
            case ro.Rational():
                self_rational = Fraction( self._unit ).limit_denominator()
                return self_rational > other_number % od.DataSource( Fraction() )
            case int() | float() | Fraction():
                return self._unit > other_number
        return False
    
    def __le__(self, other_number: any) -> bool:
        return self == other_number or self < other_number
    
    def __ge__(self, other_number: any) -> bool:
        return self == other_number or self > other_number
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "unit": self._unit
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "unit" in serialization["parameters"]):

            self._unit = serialization["parameters"]["unit"]
        return self

    def __lshift__(self, operand: o.Operand) -> 'Unit':
        import operand_rational as ro
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():                     self._unit = operand % o.Operand()
                    case float() | Fraction():      self._unit = int(operand % o.Operand())
                    case Integer() | ro.Float():    self._unit = operand % o.Operand() % od.DataSource( int() )
            case self.__class__():          self._unit = operand._unit
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case int() | float() | Fraction():
                self._unit = int(operand)
            case ro.Float():
                self._unit = operand % int()
        return self

    def __add__(self, number: any) -> 'Unit':
        import operand_rational as ro
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case self.__class__() | Integer() | ro.Float():
                                        return self.__class__() << od.DataSource( self._unit + number % od.DataSource( int() ) )
            case int() | float() | Fraction():
                                        return self.__class__() << od.DataSource( self._unit + number )
        return self.copy()
    
    def __sub__(self, number: any) -> 'Unit':
        import operand_rational as ro
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case self.__class__() | Integer() | ro.Float():
                                        return self.__class__() << od.DataSource( self._unit - number % od.DataSource( int() ) )
            case int() | float() | Fraction():
                                        return self.__class__() << od.DataSource( self._unit - number )
        return self.copy()
    
    def __mul__(self, number: any) -> 'Unit':
        import operand_rational as ro
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case self.__class__() | Integer() | ro.Float():
                                        return self.__class__() << od.DataSource( self._unit * (number % od.DataSource( int() )) )
            case int() | float() | Fraction():
                                        return self.__class__() << od.DataSource( self._unit * number )
        return self.copy()
    
    def __truediv__(self, number: any) -> 'Unit':
        import operand_rational as ro
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case self.__class__() | Integer() | ro.Float():
                                    if number % od.DataSource( int() ) != 0:
                                        return self.__class__() << od.DataSource( self._unit / (number % od.DataSource( int() )) )
            case int() | float() | Fraction():
                                    if number != 0:
                                        return self.__class__() << od.DataSource( self._unit / number )
        return self.copy()

class Integer(Unit):
    pass

class Semitone(Unit):
    pass

class KeySignature(Unit):       # Sharps (+) and Flats (-)
    def __init__(self, accidentals: int | str = 0):
        super().__init__()
        match accidentals:
            case str():
                total_sharps = accidentals.count('#')
                total_flats = accidentals.count('b')
                num_accidentals = total_sharps - total_flats
                # Number of accidentals should range between -7 and +7
                if -7 <= num_accidentals <= 7:
                    self._unit = num_accidentals
            case int() | float():
                num_accidentals = int(accidentals)
                # Number of accidentals should range between -7 and +7
                if -7 <= num_accidentals <= 7:
                    self._unit = num_accidentals
    
    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case KeySignature():        return self
                    case int():                 return self._unit
                    case list():                return self % list()
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            case KeySignature():        return self.copy()
            case int():                 return self._unit
            case list():
                key_signature = KeySignature._key_signatures[(self._unit + 7) % 15]
                key_signature_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major scale
                for key_i in range(12):
                    if key_signature[key_i] != 0:
                        key_signature_scale[key_i] = 0
                        key_signature_scale[(key_i + key_signature[key_i]) % 12] = 1
                return key_signature_scale
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_key_signature: 'KeySignature') -> bool:
        other_key_signature = self & other_key_signature    # Processes the tailed self operands or the Frame operand if any exists
        if other_key_signature.__class__ == o.Operand:
            return True
        if type(self) != type(other_key_signature):
            return False
        return  self._unit   == other_key_signature._unit
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'KeySignature':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():     self._unit   = operand % o.Operand()
            case KeySignature():
                self._unit       = operand._unit
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case int():     self._unit   = operand
        return self

    _key_signatures: list[list] = [
    #     C      D      E   F      G      A      B
        [-1, 0, -1, 0, -1, -1, 0, -1, 0, -1, 0, -1],    # -7
        [-1, 0, -1, 0, -1, -0, 0, -1, 0, -1, 0, -1],    # -6
        [-0, 0, -1, 0, -1, -0, 0, -1, 0, -1, 0, -1],    # -5
        [-0, 0, -1, 0, -1, -0, 0, -0, 0, -1, 0, -1],    # -4
        [-0, 0, -0, 0, -1, -0, 0, -0, 0, -1, 0, -1],    # -3
        [-0, 0, -0, 0, -1, -0, 0, -0, 0, -0, 0, -1],    # -2
        [-0, 0, -0, 0, -0, -0, 0, -0, 0, -0, 0, -1],    # -1
    #     C      D      E   F      G      A      B
        [+0, 0, +0, 0, +0, +0, 0, +0, 0, +0, 0, +0],    # +0
    #     C      D      E   F      G      A      B
        [+0, 0, +0, 0, +0, +1, 0, +0, 0, +0, 0, +0],    # +1
        [+1, 0, +0, 0, +0, +1, 0, +0, 0, +0, 0, +0],    # +2
        [+1, 0, +0, 0, +0, +1, 0, +1, 0, +0, 0, +0],    # +3
        [+1, 0, +1, 0, +0, +1, 0, +1, 0, +0, 0, +0],    # +4
        [+1, 0, +1, 0, +0, +1, 0, +1, 0, +1, 0, +0],    # +5
        [+1, 0, +1, 0, +1, +1, 0, +1, 0, +1, 0, +0],    # +6
        [+1, 0, +1, 0, +1, +1, 0, +1, 0, +1, 0, +1],    # +7
    ]

class Key(Unit):
    """
    A Key() is an integer from 0 to 11 that describes the 12 keys of an octave.
    
    Parameters
    ----------
    first : integer_like or string_like
        A number from 0 to 11 with 0 as default or the equivalent string key "C"
    """
    def __init__(self, *parameters):
        super().__init__()
        self._flat: Flat        = Flat()
        self._natural: Natural  = Natural()
        self._degree: Degree    = Degree(1)
        self._scale: od.Scale   = od.Scale([])
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case Flat():            return self._flat
                    case Natural():         return self._natural
                    case Degree():          return self._degree
                    case od.Scale():        return self._scale
                    case float():           return self % float()
                    case _:                 return super().__mod__(operand)
            case Flat():            return self._flat.copy()
            case Natural():         return self._natural.copy()
            case Degree():          return self._degree.copy()
            case od.Scale():        return self._scale.copy()
            case float():
                if self._scale.hasScale() or os.staff._scale.hasScale():
                    return self._unit
                else:
                    key_int: int            = self._unit
                    key_signature: KeySignature = os.staff._key_signature
                    key_signature_scale     = key_signature % list()
                    not_natural: bool       = self._natural._unit == 0
                    if not_natural:
                        accidentals_int = key_signature._unit
                        sharps_flats = KeySignature._key_signatures[(accidentals_int + 7) % 15]
                        key_int += sharps_flats[key_int % 12]
                    key_offset: int      = 0
                    if key_signature_scale[key_int % 12] == 0:
                        if self._flat._unit:
                            key_offset = +1
                        else:
                            key_offset = -1
                    key_int += key_offset
                    degree_transpose: int   = 0
                    if self._degree._unit > 0:
                        degree_transpose    = self._degree._unit - 1    # Where the self._degree is processed
                    elif self._degree._unit < 0:
                        degree_transpose    = self._degree._unit + 1    # Where the self._degree is processed
                    semitone_transpose: int = 0
                    while degree_transpose > 0:
                        semitone_transpose += 1
                        if key_signature_scale[(key_int + semitone_transpose) % 12]:
                            degree_transpose -= 1
                    while degree_transpose < 0:
                        semitone_transpose -= 1
                        if key_signature_scale[(key_int + semitone_transpose) % 12]:
                            degree_transpose += 1
                    return float(key_int - key_offset + semitone_transpose)
            case _:                 return super().__mod__(operand)

    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["flat"]     = self._flat._unit
        element_serialization["parameters"]["natural"]  = self._natural._unit
        element_serialization["parameters"]["degree"]   = self._degree._unit
        element_serialization["parameters"]["scale"]    = self._scale._data
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "flat" in serialization["parameters"] and "natural" in serialization["parameters"] and "degree" in serialization["parameters"] and
            "scale" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._flat      = Flat()    << od.DataSource( serialization["parameters"]["flat"] )
            self._natural   = Natural() << od.DataSource( serialization["parameters"]["natural"] )
            self._degree    = Degree()  << od.DataSource( serialization["parameters"]["degree"] )
            self._scale     = od.Scale(serialization["parameters"]["scale"])
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Key':
        import operand_rational as ro
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():                     self._unit = operand % o.Operand()
                    case float() | Fraction():      self._unit = int(operand % o.Operand())
                    case Semitone() | Integer() | ro.Float():
                                                    self._unit = operand % o.Operand() % od.DataSource( int() )
                    case Flat():
                        self._flat << operand % o.Operand()
                    case Natural():
                        self._natural << operand % o.Operand()
                    case Degree():
                        self._degree << operand % o.Operand()
                    case od.Scale():
                        self._scale << operand % o.Operand()
                    case str():
                        self._flat << ((operand % o.Operand()).strip().lower().find("b") != -1) * 1
                        self._unit = Key.key_to_int(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case Key():
                self._unit          = operand._unit
                self._flat._unit    = operand._flat._unit
                self._natural._unit = operand._natural._unit
                self._degree._unit  = operand._degree._unit
                self._scale         = operand._scale.copy()
            case Semitone() | Integer() | ro.Float():
                                    self._unit = operand % int()
            case int() | float() | Fraction():
                                    self._unit = int(operand)
            case Flat():
                 self._flat << operand
            case Natural():
                self._natural << operand
            case Degree():
                self._degree << operand
            case od.Scale():
                self._scale << operand
            case str():
                self._flat << (operand.strip().lower().find("b") != -1) * 1
                self._unit = Key.key_to_int(operand)
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:                 super().__lshift__(operand)
        return self

    def __add__(self, operand: any) -> 'Unit':
        import operand_rational as ro
        operand = self & operand      # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int(): return self.__class__() << od.DataSource( self._unit + self.move_semitones(operand) )
            case Integer():
                        return self.__class__() << od.DataSource( self._unit + self.move_semitones(operand._unit) )
            case Semitone():
                        return self.__class__() << od.DataSource( self._unit + operand._unit )
            case Degree():
                self_copy: Key = self.copy()
                if self_copy._degree._unit > 0:
                    self_copy._degree._unit -= 1
                elif self_copy._degree._unit < 0:
                    self_copy._degree._unit += 1
                self_copy._degree._unit += operand._unit
                return self_copy
            case _:     return super().__add__(operand)
    
    def __sub__(self, operand: any) -> 'Unit':
        import operand_rational as ro
        operand = self & operand      # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int(): return self.__class__() << od.DataSource( self._unit + self.move_semitones(operand * -1) )
            case Integer():
                        return self.__class__() << od.DataSource( self._unit + self.move_semitones(operand._unit * -1) )
            case Semitone():
                        return self.__class__() << od.DataSource( self._unit - operand._unit )
            case Degree():
                self_copy: Key = self.copy()
                if self_copy._degree._unit > 0:
                    self_copy._degree._unit -= 1
                elif self_copy._degree._unit < 0:
                    self_copy._degree._unit += 1
                self_copy._degree._unit -= operand._unit
                return self_copy
            case _:     return super().__sub__(operand)
    
    def move_semitones(self, move_keys: int) -> int:
        scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]    # Major scale for the default staff
        if self._scale.hasScale():
            scale = self._scale % list()
        elif os.staff._scale.hasScale():
            scale = os.staff._scale % list()
        move_semitones: int = 0
        while move_keys > 0:
            move_semitones += 1
            if scale[(self._unit + move_semitones) % 12]:
                move_keys -= 1
        while move_keys < 0:
            move_semitones -= 1
            if scale[(self._unit + move_semitones) % 12]:
                move_keys += 1
        return move_semitones

    _keys: list[str]    = ["C",  "C#", "D", "D#", "E",  "F",  "F#", "G", "G#", "A", "A#", "B",
                           "C",  "Db", "D", "Eb", "E",  "F",  "Gb", "G", "Ab", "A", "Bb", "B",
                           "B#", "C#", "D", "D#", "Fb", "E#", "F#", "G", "G#", "A", "A#", "Cb"]
    
    def int_to_key(self, note_key: int = 0) -> str:
        note_key %= 12
        note_key += 12 * (self._flat._unit != 0)
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

class Octave(Unit):
    """
    An Octave() represents the full midi keyboard, varying from -1 to 9 (11 octaves).
    
    Parameters
    ----------
    first : integer_like
        An Integer representing the full midi keyboard octave varying from -1 to 9
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class Sharp(Unit):      # Sharp (#)
    ...

class Flat(Unit):       # Flat (b)
    ...

class Natural(Unit):    # Natural (?)
    ...

class Degree(Unit):
    """
    A Degree() represents its relation with a Tonic key on a scale
    and respective Progressions.
    
    Parameters
    ----------
    first : integer_like
        Accepts a numeral (5) or the string (V) with 1 as the default
    """
    def __init__(self, unit: int | str = None):
        match unit:
            case str():
                super().__init__( __class__.stringToNumber(unit) )
            case int() | float():
                super().__init__( unit )
            case _:
                super().__init__( 1 )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Size':
        import operand_rational as ro
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self._unit = __class__.stringToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self._unit = __class__.stringToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _degrees_str = ["None" , "I", "ii", "iii", "IV", "V", "vi", "viiº"]

    @staticmethod
    def stringToNumber(string: str) -> int:
        match string.strip().lower():
            case "i"   | "tonic":                   return 1
            case "ii"  | "supertonic":              return 2
            case "iii" | "mediant":                 return 3
            case "iv"  | "subdominant":             return 4
            case "v"   | "dominant":                return 5
            case "vi"  | "submediant":              return 6
            case "vii" | "viiº" | "leading tone":   return 7
            case _:                                 return 1

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._degrees_str[number % len(__class__._degrees_str)]

class Size(Unit):
    """
    Size() represents the size of the Chord, like "7th", "9th", etc.
    
    Parameters
    ----------
    first : integer_like or string_like
        A Size Number varies from "1st" to "13th" with "3rd" being the triad default
    """
    def __init__(self, unit: int | str = None):
        match unit:
            case str():
                super().__init__( __class__.stringToNumber(unit) )
            case int() | float():
                super().__init__( unit )
            case _:
                super().__init__( 3 )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Size':
        import operand_rational as ro
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self._unit = __class__.stringToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self._unit = __class__.stringToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _types_str = ["None" , "1st", "3rd", "5th", "7th", "9th", "11th", "13th"]

    @staticmethod
    def stringToNumber(string: str) -> int:
        match string.strip().lower():
            case '1'  | "1st":              return 1
            case '3'  | "3rd":              return 2
            case '5'  | "5th":              return 3
            case '7'  | "7th":              return 4
            case '9'  | "9th":              return 5
            case '11' | "11th":             return 6
            case '13' | "13th":             return 7
            case _:                         return 3

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._types_str[number % len(__class__._types_str)]

class Mode(Unit):
    """
    Mode() represents the different scales (e.g., Ionian, Dorian, Phrygian)
    derived from the degrees of the major scale.
    
    Parameters
    ----------
    first : integer_like or string_like
        A Mode Number varies from 1 to 7 with 1 being normally the default
    """
    def __init__(self, unit: int | str = None):
        match unit:
            case str():
                super().__init__( __class__.stringToNumber(unit) )
            case int() | float():
                super().__init__( unit )
            case _:
                super().__init__( 1 )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Size':
        import operand_rational as ro
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self._unit = __class__.stringToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self._unit = __class__.stringToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

        # 1 - First, 2 - Second, 3 - Third, 4 - Fourth, 5 - Fifth, 6 - Sixth, 7 - Seventh,
        # 8 - Eighth, 9 - Ninth, 10 - Tenth, 11 - Eleventh, 12 - Twelfth, 13 - Thirteenth,
        # 14 - Fourteenth, 15 - Fifteenth, 16 - Sixteenth, 17 - Seventeenth, 18 - Eighteenth,
        # 19 - Nineteenth, 20 - Twentieth.

    _modes_str = ["None" , "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]

    @staticmethod
    def stringToNumber(string: str) -> int:
        match string.strip().lower():
            case '1'  | "1st":              return 1
            case '2'  | "2nd":              return 2
            case '3'  | "3rd":              return 3
            case '4'  | "4th":              return 4
            case '5'  | "5th":              return 5
            case '6'  | "6th":              return 6
            case '7'  | "7th":              return 7
            case '8'  | "8th":              return 8
            case _:                         return 1

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._modes_str[number % len(__class__._modes_str)]

class Sus(Unit):
    """
    Sus() represents the suspended chord flavor, sus2 or sus4.
    
    Parameters
    ----------
    first : integer_like or string_like
        A sus Number can be 0, 1 or 2 with 0 being normal not suspended chord
    """
    def __init__(self, unit: int | str = None):
        match unit:
            case str():
                super().__init__( __class__.stringToNumber(unit) )
            case int() | float():
                super().__init__( unit )
            case _:
                super().__init__( 0 )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Size':
        import operand_rational as ro
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self._unit = __class__.stringToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self._unit = __class__.stringToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _sus_str = ["None" , "sus2", "sus4"]

    @staticmethod
    def stringToNumber(string: str) -> int:
        match string.strip().lower():
            case "sus2":            return 1
            case "sus4":            return 2
            case _:                 return 0

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._sus_str[number % len(__class__._sus_str)]

class Division(Unit):
    """
    A Division() is used in conjugation with a Tuplet as not the usual 3 of the Triplet.
    
    Parameters
    ----------
    first : integer_like
        The amount of notes grouped together with the default of 3 (Triplet)
    """
    def __init__(self, unit: int = None):
        super().__init__(3 if unit is None else unit)

class Operation(Unit):
    pass

class Transposition(Operation):
    """
    A Transposition() is used to do a modal Transposition along a given Scale.
    
    Parameters
    ----------
    first : integer_like
        Transposition along the given Scale with 1 ("1st") as the default mode
    """
    def __init__(self, mode: int | str = None):
        unit = Mode(mode) % od.DataSource( int() )
        super().__init__(unit)

class Modulation(Operation):    # Modal Modulation
    """
    A Modulation() is used to return a modulated Scale from a given Scale or Scale.
    
    Parameters
    ----------
    first : integer_like
        Modulation of a given Scale with 1 ("1st") as the default mode
    """
    def __init__(self, mode: int | str = None):
        unit = Mode(mode) % od.DataSource( int() )
        super().__init__(unit)

class Modulate(Operation):    # Modal Modulation
    """
    Modulate() is used to modulate the self Scale or Scale.
    
    Parameters
    ----------
    first : integer_like
        Modulate a given Scale to 1 ("1st") as the default mode
    """
    def __init__(self, mode: int | str = None):
        unit = Mode(mode) % od.DataSource( int() )
        super().__init__(unit)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(operand, od.Scale):
            operand = operand.copy().modulate(self._unit)
        return operand

class Progression(Operation):
    """
    A Progression() is used to do a Progression along a given Scale.
    
    Parameters
    ----------
    first : integer_like
        Accepts a numeral equivalent to the the Roman numerals,
        1 instead of I, 4 instead of IV and 5 instead of V
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class Inversion(Operation):
    """
    Inversion() sets the degree of inversion of a given chord.
    
    Parameters
    ----------
    first : integer_like
        Inversion sets the degree of chords inversion starting by 0 meaning no inversion
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class Play(Unit):
    """
    Play() allows to send a given Element to the Player directly without the need of Exporting to the respective .json Player file.
    
    Parameters
    ----------
    first : integer_like
        By default it's configured without any verbose, set to 1 or True to enable verbose
    """
    def __init__(self, verbose: bool = False):
        super().__init__(1 if verbose else 0)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case o.Operand():
                c.jsonMidiPlay(operand.getPlaylist(), False if self._unit == 0 else True )
            case tuple():
                rshift_operands = None
                for single_operand in operand:
                    if isinstance(single_operand, o.Operand):
                        if rshift_operands is not None:
                            rshift_operands >>= single_operand
                        else:
                            rshift_operands = single_operand
                return rshift_operands >> self
        return operand

class Print(Unit):
    """
    Print() allows to get on the console the configuration of the source Operand in a JSON layout.
    
    Parameters
    ----------
    first : integer_like
        Sets the indent of the JSON print layout with the default as 4
    """
    def __init__(self, formatted: bool = True):
        super().__init__( 1 if formatted is None else formatted )

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case o.Operand():
                operand_serialization = operand.getSerialization()
                if self._unit:
                    serialized_json_str = json.dumps(operand_serialization)
                    json_object = json.loads(serialized_json_str)
                    json_formatted_str = json.dumps(json_object, indent=4)
                    print(json_formatted_str)
                else:
                    print(operand_serialization)
            case _: print(operand)
        return operand

class Link(Unit):
    def __init__(self, and_join: bool = False):
        super().__init__( 0 if and_join is None else and_join )
        
    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.link(bool(self._unit))
        return operand

class Middle(Unit):
    """
    Middle() represent the Nth Operand in a Container or Sequence.
    
    Parameters
    ----------
    first : integer_like
        The Nth Operand in a Container like 2 for the 2nd Operand
    """
    def __init__(self, unit: int = None):
        super().__init__( 1 if unit is None else unit )

class PPQN(Unit):
    """
    PPQN() represent Pulses Per Quarter Note for Midi clock.
    
    Parameters
    ----------
    first : integer_like
        The typical and the default value is 24, but it can be set multiples of 24
    """
    def __init__(self, unit: int = None):
        super().__init__( 24 if unit is None else unit )

class Midi(Unit):
    pass

class Velocity(Midi):
    """
    Velocity() represents the velocity or strength by which a key is pressed.
    
    Parameters
    ----------
    first : integer_like
        A key velocity varies from 0 to 127
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class Pressure(Midi):
    """
    Pressure() represents the intensity with which a key is pressed after being down.
    
    Parameters
    ----------
    first : integer_like
        A key pressure varies from 0 to 127
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class Program(Midi):
    """
    Program() represents the Program Number associated to a given Instrument.
    
    Parameters
    ----------
    first : integer_like
        A Program Number varies from 0 to 127
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class Channel(Midi):
    """
    A Channel() is an identifier normally associated to an instrument in a given midi device.
    
    Parameters
    ----------
    first : integer_like
        For a given device, there are 16 channels ranging from 1 to 16
    """
    def __init__(self, unit: int = None):
        super().__init__( os.staff % od.DataSource( self ) % int() if unit is None else unit )

class Pitch(Midi):
    """
    Pitch() sets the variation in the pitch to be associated to the PitchBend() Element.
    
    Parameters
    ----------
    first : integer_like
        Pitch variation where 0 is no variation and other values from -8192 to 8191 are the intended variation,
        this variation is 2 semi-tones bellow or above respectively
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():   return super().__mod__(operand)
            case ol.MSB():
                amount = 8192 + self._unit    # 2^14 = 16384, 16384 / 2 = 8192
                amount = max(min(amount, 16383), 0) # midi safe
                msb = amount >> 7               # MSB - total of 14 bits, 7 for each side, 2^7 = 128
                return msb
            case ol.LSB():
                amount = 8192 + self._unit    # 2^14 = 16384, 16384 / 2 = 8192
                amount = max(min(amount, 16383), 0) # midi safe
                lsb = amount & 0x7F             # LSB - 0x7F = 127, 7 bits with 1s, 2^7 - 1
                return lsb
            case _:                 return super().__mod__(operand)

# For example, if the pitch bend range is set to ±2 half-tones (which is common), then:
#     8192 (center value) means no pitch change.
#     0 means maximum downward bend (−2 half-tones).
#     16383 means maximum upward bend (+2 half-tones).

#        bend down    center      bend up
#     0 |<----------- |8192| ----------->| 16383
# -8192                   0                 8191
# 14 bits resolution (MSB, LSB). Value = 128 * MSB + LSB
# min : The maximum negative swing is achieved with data byte values of 00, 00. Value = 0
# center: The center (no effect) position is achieved with data byte values of 00, 64 (00H, 40H). Value = 8192
# max : The maximum positive swing is achieved with data byte values of 127, 127 (7FH, 7FH). Value = 16384

class Value(Midi):
    """
    Value() represents the Control Change value that is sent via Midi
    
    Parameters
    ----------
    first : integer_like
        The Value shall be set from 0 to 127 accordingly to the range of CC Midi values
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class Number(Midi):
    """
    Number() represents the number of the Control to be manipulated with the Value values.
    
    Parameters
    ----------
    first : integer_like and string_like
        Allows the direct set with a number or in alternative with a name relative to the Controller
    """
    def __init__(self, unit: str = "Pan"):
        match unit:
            case str():
                super().__init__( Number.nameToNumber(unit) )
            case int() | float():
                super().__init__(unit)
            case _:
                super().__init__(None)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():       return super().__mod__(operand)
            case str():                 return Number.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Number':
        import operand_rational as ro
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self._unit = Number.nameToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self._unit = Number.nameToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _controllers = [
        {   "midi_number": 0,   "default_value": 0,     "names": ["Bank Select"]    },
        {   "midi_number": 1,   "default_value": 0,     "names": ["Modulation Wheel", "Modulation"]    },
        {   "midi_number": 2,   "default_value": 0,     "names": ["Breath Controller"]    },
        
        {   "midi_number": 4,   "default_value": 0,     "names": ["Foot Controller", "Foot Pedal"]    },
        {   "midi_number": 5,   "default_value": 0,     "names": ["Portamento Time"]    },
        {   "midi_number": 6,   "default_value": 0,     "names": ["Data Entry MSB"]    },
        {   "midi_number": 7,   "default_value": 100,   "names": ["Main Volume"]    },
        {   "midi_number": 8,   "default_value": 64,    "names": ["Balance"]    },
        
        {   "midi_number": 10,  "default_value": 64,    "names": ["Pan"]    },
        {   "midi_number": 11,  "default_value": 0,     "names": ["Expression"]    },
        {   "midi_number": 12,  "default_value": 0,     "names": ["Effect Control 1"]    },
        {   "midi_number": 13,  "default_value": 0,     "names": ["Effect Control 2"]    },
        
        {   "midi_number": 64,  "default_value": 0,     "names": ["Sustain", "Damper Pedal"]    },
        {   "midi_number": 65,  "default_value": 0,     "names": ["Portamento"]    },
        {   "midi_number": 66,  "default_value": 0,     "names": ["Sostenuto"]    },
        {   "midi_number": 67,  "default_value": 0,     "names": ["Soft Pedal"]    },
        {   "midi_number": 68,  "default_value": 0,     "names": ["Legato Footswitch"]    },
        {   "midi_number": 69,  "default_value": 0,     "names": ["Hold 2"]    },
        {   "midi_number": 70,  "default_value": 0,     "names": ["Sound Variation"]    },
        {   "midi_number": 71,  "default_value": 0,     "names": ["Timbre", "Harmonic Content", "Resonance"]    },
        {   "midi_number": 72,  "default_value": 64,    "names": ["Release Time"]    },
        {   "midi_number": 73,  "default_value": 64,    "names": ["Attack Time"]    },
        {   "midi_number": 74,  "default_value": 64,    "names": ["Brightness", "Frequency Cutoff"]    },

        {   "midi_number": 84,  "default_value": 0,     "names": ["Portamento Control"]    },

        {   "midi_number": 91,  "default_value": 0,     "names": ["Reverb"]    },
        {   "midi_number": 92,  "default_value": 0,     "names": ["Tremolo"]    },
        {   "midi_number": 93,  "default_value": 0,     "names": ["Chorus"]    },
        {   "midi_number": 94,  "default_value": 0,     "names": ["Detune"]    },
        {   "midi_number": 95,  "default_value": 0,     "names": ["Phaser"]    },
        {   "midi_number": 96,  "default_value": 0,     "names": ["Data Increment"]    },
        {   "midi_number": 97,  "default_value": 0,     "names": ["Data Decrement"]    },

        {   "midi_number": 120, "default_value": 0,     "names": ["All Sounds Off"]    },
        {   "midi_number": 121, "default_value": 0,     "names": ["Reset All Controllers"]    },
        {   "midi_number": 122, "default_value": 127,   "names": ["Local Control", "Local Keyboard"]    },
        {   "midi_number": 123, "default_value": 0,     "names": ["All Notes Off"]    },
        {   "midi_number": 124, "default_value": 0,     "names": ["Omni Off"]    },
        {   "midi_number": 125, "default_value": 0,     "names": ["Omni On"]    },
        {   "midi_number": 126, "default_value": 0,     "names": ["Mono On", "Monophonic"]    },
        {   "midi_number": 127, "default_value": 0,     "names": ["Poly On", "Polyphonic"]    },
    ]

    @staticmethod
    def getDefault(number: int) -> int:
        for controller in Number._controllers:
            if controller["midi_number"] == number:
                return controller["default_value"]
        return 0

    @staticmethod
    def nameToNumber(number: str = "Pan") -> int:
        for controller in Number._controllers:
            for controller_name in controller["names"]:
                if controller_name.lower().find(number.strip().lower()) != -1:
                    return controller["midi_number"]
        return 0

    @staticmethod
    def numberToName(number: int) -> str:
        for controller in Number._controllers:
            if controller["midi_number"] == number:
                return controller["names"][0]
        return "Bank Select"
