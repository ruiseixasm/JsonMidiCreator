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
import json
import re
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_staff as os
import operand_data as od

import operand_frame as of
import operand_label as ol

TypeUnit = TypeVar('TypeUnit', bound='Unit')  # TypeUnit represents any subclass of Operand


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
    def __init__(self, *parameters):
        super().__init__()
        self._unit: int = 0
        if parameters:
            self << parameters

    def unit(self: TypeUnit, number: int = None) -> TypeUnit:
        return self << od.DataSource( number )

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
        import operand_rational as ra
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case Fraction():        return Fraction(self._unit)
                    case int():             return self._unit           # returns a int()
                    case float():           return float(self._unit)
                    case Unit() | ra.Rational():
                                            return operand.__class__() << od.DataSource( self._unit )
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case int():             return self._unit
            case bool():            return False if self._unit == 0 else True
            case float():           return float(self._unit)
            case Fraction():        return Fraction(self._unit)
            case Unit() | ra.Rational():
                                    return operand.__class__() << od.DataSource( self._unit )
            case _:                 return super().__mod__(operand)

    def __bool__(self) -> bool:  # For Python 3
        return self._unit != 0

    def __nonzero__(self) -> bool:  # For Python 2
        return self.__bool__()
    
    def __not__(self) -> bool:
        return self._unit == 0
    
    def __eq__(self, other: any) -> bool:
        import operand_rational as ra
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Unit():
                return self._unit == other._unit
            case ra.Rational():
                self_rational = Fraction( self._unit )
                return self_rational == other % od.DataSource( Fraction() )
            case int() | float() | Fraction():
                return self._unit == other
            case _:
                if other.__class__ == o.Operand:
                    return True
        return False
    
    def __lt__(self, other: any) -> bool:
        import operand_rational as ra
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Unit():
                return self._unit < other._unit
            case ra.Rational():
                self_rational = Fraction( self._unit )
                return self_rational < other % od.DataSource( Fraction() )
            case int() | float() | Fraction():
                return self._unit < other
        return False
    
    def __gt__(self, other: any) -> bool:
        import operand_rational as ra
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Unit():
                return self._unit > other._unit
            case ra.Rational():
                self_rational = Fraction( self._unit )
                return self_rational > other % od.DataSource( Fraction() )
            case int() | float() | Fraction():
                return self._unit > other
        return False
    
    def __le__(self, other: any) -> bool:
        return self == other or self < other
    
    def __ge__(self, other: any) -> bool:
        return self == other or self > other
    
    def __str__(self):
        return f'{self._unit}'
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["unit"] = self._unit
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Unit':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "unit" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._unit = serialization["parameters"]["unit"]
        return self

    def __lshift__(self, operand: o.Operand) -> 'Unit':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():                     self._unit = operand % o.Operand()
                    case float() | Fraction() | bool():
                                                    self._unit = int(operand % o.Operand())
                    case Unit() | ra.Rational():    self._unit = operand % o.Operand() % od.DataSource( int() )
            case Unit():
                super().__lshift__(operand)
                self._unit = operand._unit
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case int() | float() | Fraction():
                self._unit = int(operand)
            case bool():
                self._unit = 1 if operand else 0
            case ra.Rational():
                self._unit = operand % int()
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __add__(self, number: any) -> 'Unit':
        import operand_rational as ra
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case Unit() | ra.Rational():
                return self.__class__() << od.DataSource( self._unit + number % od.DataSource( int() ) )
            case int() | float() | Fraction():
                return self.__class__() << od.DataSource( self._unit + number )
        return self.copy()
    
    def __sub__(self, number: any) -> 'Unit':
        import operand_rational as ra
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case Unit() | ra.Rational():
                return self.__class__() << od.DataSource( self._unit - number % od.DataSource( int() ) )
            case int() | float() | Fraction():
                return self.__class__() << od.DataSource( self._unit - number )
        return self.copy()
    
    def __mul__(self, number: any) -> 'Unit':
        import operand_rational as ra
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case Unit() | ra.Rational():
                return self.__class__() << od.DataSource( self._unit * (number % od.DataSource( int() )) )
            case int() | float() | Fraction():
                return self.__class__() << od.DataSource( self._unit * number )
        return self.copy()
    
    def __truediv__(self, number: any) -> 'Unit':
        import operand_rational as ra
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case Unit() | ra.Rational():
                if number % od.DataSource( int() ) != 0:
                    return self.__class__() << od.DataSource( self._unit / (number % od.DataSource( int() )) )
            case int() | float() | Fraction():
                if number != 0:
                    return self.__class__() << od.DataSource( self._unit / number )
        return self.copy()

class Next(Unit):
    def __init__(self, *parameters):
        super().__init__(1)
        if len(parameters) > 0:
            self << parameters

class Previous(Unit):
    def __init__(self, *parameters):
        super().__init__(1)
        if len(parameters) > 0:
            self << parameters

class TimeUnit(Unit):
    pass

class Measure(TimeUnit):
    pass

class Beat(TimeUnit):
    pass

class Step(TimeUnit):
    pass

class Tone(Unit):
    pass

class Semitone(Unit):
    pass

class KeySignature(Unit):       # Sharps (+) and Flats (-)
    def __init__(self, *parameters):
        super().__init__()
        self._major: Major          = Major()
        if parameters:
            self << parameters
    
    def get_tonic_key(self) -> int:
        circle_fifths_position: int = self._unit
        zero_key_int: int = 0  # C (Major)
        if not self._major:
            zero_key_int = 9   # A (minor)
        return (zero_key_int + circle_fifths_position * 7) % 12

    def __mod__(self, operand: o.Operand) -> o.Operand:
        import operand_generic as og
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case KeySignature():        return self
                    case list():                return self % list()
                    case Major():               return self._major
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            case KeySignature():        return self.copy()
            case int():                 return self.get_tonic_key()
            case float():
                tonic_key_int: int = self.get_tonic_key()
                if self._unit < 0:
                    tonic_key_int += 12   # 2nd line for sharps
                # Special case of bellow -5 or above +5 turns in the circle of fifths
                if self._unit < -5 or self._unit > 5:
                    tonic_key_int += 24   # 3rd and 4th lines respectively
                return float(tonic_key_int)
            
            case Key():
                return Key(self % float())
            case Major():               return self._major.copy()
            case Minor():               return Minor(not (self._major % bool()))
            case Sharps():
                if self._unit > 0:
                    return Sharps(self._unit)
                return Sharps(0)
            case Flats():
                if self._unit < 0:
                    return Flats(self._unit * -1)
                return Flats(0)
            case og.Scale():            return og.Scale(self % list())
            case list():
                key_signature_scale: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major scale
                if self._unit != 0:
                    key_signature = KeySignature._key_signatures[(self._unit + 7) % 15]
                    for key_i in range(11, -1, -1): # range(12) results in a bug
                        if key_signature[key_i] != 0:
                            key_signature_scale[key_i] = 0
                            key_signature_scale[(key_i + key_signature[key_i]) % 12] = 1
                return key_signature_scale
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_signature: 'KeySignature') -> bool:
        other_signature = self & other_signature    # Processes the tailed self operands or the Frame operand if any exists
        if other_signature.__class__ == o.Operand:
            return True
        if isinstance(other_signature, KeySignature):
            return self._unit == other_signature._unit and self._major == other_signature._major
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["major"]            = self.serialize( self._major )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeySignature':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "major" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._major         = self.deserialize( serialization["parameters"]["major"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'KeySignature':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():     self._unit      = operand % o.Operand()
                    case Major():   self._major     = operand % o.Operand()
            case KeySignature():
                super().__lshift__(operand)
                self._major._unit   = operand._major._unit
            case int():     self._unit   = operand
            case Major():   self._major  << operand
            case Minor():   self._major  << (operand % int() == 0)
            case Sharps() | Flats():
                self._unit = operand._unit
                if isinstance(operand, Flats):
                    self._unit *= -1
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    sharps = re.findall(r"#+", operand)
                    if len(sharps) > 0:
                        self._unit = len(sharps[0])
                    else:
                        flats = re.findall(r"b+", operand)
                        if len(flats) > 0:
                            self._unit = -len(flats[0])
            case _: 
                super().__lshift__(operand)
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
        [+1, 0, +1, 0, +1, +1, 0, +1, 0, +1, 0, +1]     # +7
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
        import operand_generic as og
        super().__init__()
        # self._key_signature: KeySignature   = os.staff._key_signature.copy()
        # self._unit                          = self._key_signature.get_tonic_key()
        # self._sharp: Sharp                  = Sharp(0)
        # self._flat: Flat                    = Flat(0)
        # self._natural: Natural              = Natural(0)
        # self._degree: Degree                = Degree(1)
        # self._scale: og.Scale               = og.Scale([])
        if parameters:
            self << parameters

    def key_signature(self: 'Key', key_signature: 'KeySignature' = None) -> 'Key':
        self._key_signature = key_signature
        return self

    def sharp(self: 'Key', unit: int = None) -> 'Key':
        return self << od.DataSource( Sharp(unit) )

    def flat(self: 'Key', unit: int = None) -> 'Key':
        return self << od.DataSource( Flat(unit) )

    def natural(self: 'Key', unit: int = None) -> 'Key':
        return self << od.DataSource( Natural(unit) )

    def degree(self: 'Key', unit: int = None) -> 'Key':
        return self << od.DataSource( Degree(unit) )

    def scale(self: 'Key', scale: list[int] | str = None) -> 'Key':
        import operand_generic as og
        return self << od.DataSource( og.Scale(scale) )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        import operand_generic as og
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case float():           return self % float()
                    case str():
                        note_key = self % int() % 12
                        note_key += 12 * (self._flat._unit != 0)
                        return Key._keys[note_key]
                    case _:                 return super().__mod__(operand)

            case int():
                return self._unit % 12

            case float():
                return float(self._unit % 48)

            case str():
                return Key._keys[self._unit % 48]

            case Sharp():
                self_unit: int = self._unit % 48
                if self_unit < 12 or (self_unit >= 24 and self_unit < 48): 
                    return Sharp(self._accidentals[self_unit])
                return Sharp(0)
            case Flat():
                self_unit: int = self._unit % 48
                if self_unit >= 32 or (self_unit >= 12 and self_unit < 24): 
                    return Flat(self._accidentals[self_unit])
                return Flat(0)

            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        import operand_generic as og
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return self % int() == other % int()    # This get's in consideration the just final key pressed
            case str():
                return self % str() == other
            case _:
                return super().__eq__(other)
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Key':
        import operand_rational as ra
        import operand_generic as og
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():
                        self._unit = operand % o.Operand()
                    case float() | Fraction():
                        self._unit = int(operand % o.Operand())
                    case Semitone():
                        self._unit = operand % o.Operand() % od.DataSource( int() )
                        self << Degree(1)

                    case str():
                        self._unit = self.getStringToNumber(operand % o.Operand()) % 48
                    case _:
                        super().__lshift__(operand)
          

            case int():
                self._unit = operand % 12
            case float():
                self._unit = int(operand) % 48

            case str():
                self._unit = self.getStringToNumber(operand) % 48
                

            case _:
                super().__lshift__(operand)
        return self

    def __add__(self, operand: any) -> 'Key':
        return super().__add__(operand)

    def __sub__(self, operand: any) -> 'Key':
        return super().__sub__(operand)

    _keys: list[str]            = ["C",  "C#", "D", "D#", "E",  "F",  "F#", "G", "G#", "A", "A#", "B",      # Black Sharps
                                   "C",  "Db", "D", "Eb", "E",  "F",  "Gb", "G", "Ab", "A", "Bb", "B",      # Black Flats
                                   "B#", "C#", "D", "D#", "E",  "E#", "F#", "G", "G#", "A", "A#", "B",      # All Sharps
                                   "C",  "Db", "D", "Eb", "Fb", "F",  "Gb", "G", "Ab", "A", "Bb", "Cb"]     # All Flats

    _accidentals: list[int]     = [ 0,    1,    0,   1,    0,    0,    1,    0,   1,    0,   1,    0,       # Black Sharps
                                    0,    1,    0,   1,    0,    0,    1,    0,   1,    0,   1,    0,       # Black Flats
                                    1,    1,    0,   1,    0,    1,    1,    0,   1,    0,   1,    0,       # All Sharps
                                    0,    1,    0,   1,    1,    0,    1,    0,   1,    0,   1,    1]       # All Flats
    
    def getStringToNumber(self, key: str = "C") -> int:
        key_to_find: str = key.strip().lower()
        for index, value in enumerate(Key._keys):
            if value.lower().find(key_to_find) != -1:
                return index
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
    def __init__(self, *parameters):
        super().__init__(1, *parameters) # By default it's 1 to be used in basic operations like + and -

class Sharps(Unit):  # Sharps (###)
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Sharps':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_sharps = len(re.findall(r"#", operand))
                    if total_sharps > 0:
                        self._unit = total_sharps
            case _: super().__lshift__(operand)
        return self

class Sharp(Sharps):  # Sharp (#)
    pass

class Flats(Unit):   # Flats (bbb)
    def __init__(self, *parameters):
        super().__init__(1)
        if len(parameters) > 0:
            self << parameters

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Flats':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_flats = len(re.findall(r"b", operand))
                    if total_flats > 0:
                        self._unit = total_flats
            case _: super().__lshift__(operand)
        return self

class Flat(Flats):   # Flat (b)
    pass

class Boolean(Unit):
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

    # def __or__(self, operand: any) -> 'Boolean':
    #     operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
    #     match operand:
    #         case bool():
    #             return self._unit != 0 or operand
    #         case Boolean():
    #             return self._unit != 0 or operand._unit != 0
    #     return False

class Default(Boolean):
    pass

class Stackable(Boolean):
    pass

class Tied(Boolean):
    pass

class Major(Boolean):
    pass

class Minor(Boolean):
    pass

class Natural(Boolean):     # Natural (n)
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> 'Natural':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                elif len(re.findall(r"n", operand)) > 0:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Dominant(Boolean):    # Flats the seventh
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> 'Diminished':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                operand = operand.replace("#", "").replace("b", "").lower()
                if operand.find("º") == -1 and len(re.findall(r"\d+", operand)) > 0 \
                    and re.sub(r'[^a-z]', '', operand) in {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'}:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Diminished(Boolean):  # Flats the third and the fifth
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> 'Diminished':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.find("º") != -1 or operand.lower().find("dim") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Augmented(Boolean):   # Sharps the fifth
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> 'Augmented':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("aug") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Sus2(Boolean):        # Second instead of the third
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> 'Sus2':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("sus2") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Sus4(Boolean):        # Fourth instead of the third
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> 'Sus4':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("sus4") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Mode(Unit):
    """
    Mode() represents the different scales (e.g., Ionian, Dorian, Phrygian)
    derived from the degrees of the major scale.
    
    Parameters
    ----------
    first : integer_like or string_like
        A Mode Number varies from 1 to 7 with 1 being normally the default
    """
    def __init__(self, *parameters):
        super().__init__(1)         # By default the mode is 1 (1st)
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Mode':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self.stringToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self.stringToNumber(operand)
            case _:                 super().__lshift__(operand)
        self._unit = max(1, self._unit)
        return self

        # 1 - First, 2 - Second, 3 - Third, 4 - Fourth, 5 - Fifth, 6 - Sixth, 7 - Seventh,
        # 8 - Eighth, 9 - Ninth, 10 - Tenth, 11 - Eleventh, 12 - Twelfth, 13 - Thirteenth,
        # 14 - Fourteenth, 15 - Fifteenth, 16 - Sixteenth, 17 - Seventeenth, 18 - Eighteenth,
        # 19 - Nineteenth, 20 - Twentieth.

    _modes_str = ["None" , "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]

    def stringToNumber(self, string: str):
        match string.strip().lower():
            case '1'  | "1st":              self._unit = 1
            case '2'  | "2nd":              self._unit = 2
            case '3'  | "3rd":              self._unit = 3
            case '4'  | "4th":              self._unit = 4
            case '5'  | "5th":              self._unit = 5
            case '6'  | "6th":              self._unit = 6
            case '7'  | "7th":              self._unit = 7
            case '8'  | "8th":              self._unit = 8

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._modes_str[number % len(__class__._modes_str)]

class Degree(Unit):
    """
    A Degree() represents its relation with a Tonic key on a scale
    and respective Progressions.
    
    Parameters
    ----------
    first : integer_like
        Accepts a numeral (5) or the string (V) with 1 as the default
    """
    def __init__(self, *parameters):
        super().__init__(0)             # Default Degree is I (tonic) has unit = 0
        if len(parameters) > 0:
            self << parameters

    _degree = ("I", "ii", "iii", "IV", "V", "vi", "viiº")

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case int() | float() | Fraction():
                self_unit: int = self._unit
                if self_unit < 0:
                    self_unit -= 1
                else:
                    self_unit += 1
                match operand:
                    case Fraction():    return Fraction(self_unit)
                    case float():       return float(self_unit)
                    case _:             return self_unit
            case str():
                return __class__._degree[self._unit % 7]
            case _:
                return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Degree':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():
                        self.stringSetDegree(operand % o.Operand())
                    case _:
                        super().__lshift__(operand)
            case int() | float() | Fraction():
                self._unit = int(operand)
                if self._unit > 0:
                    self._unit -= 1
                elif self._unit < 0:
                    self._unit += 1
            case str():
                self.stringSetDegree(operand)
            case _:
                super().__lshift__(operand)
        return self

    def stringSetDegree(self, string: str) -> None:
        string = string.strip()
        match re.sub(r'[^a-z]', '', string.lower()):    # also removes "º" (base 0)
            case "i"   | "tonic":                   self._unit = 0
            case "ii"  | "supertonic":              self._unit = 1
            case "iii" | "mediant":                 self._unit = 2
            case "iv"  | "subdominant":             self._unit = 3
            case "v"   | "dominant":                self._unit = 4
            case "vi"  | "submediant":              self._unit = 5
            case "vii" | "leading tone":            self._unit = 6

class Size(Unit):
    """
    Size() represents the size of the Chord, like "7th", "9th", etc.
    
    Parameters
    ----------
    first : integer_like or string_like
        A Size Number varies from "1st" to "13th" with "3rd" being the triad default
    """
    def __init__(self, *parameters):
        super().__init__(3)         # Default Size is 3
        if len(parameters) > 0:
            self << parameters
            
    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'Size':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self.stringToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self.stringToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _types_str = ["None" , "1st", "3rd", "5th", "7th", "9th", "11th", "13th"]

    def stringToNumber(self, string: str):
        size = re.findall(r"\d+", string)
        if len(size) > 0:
            match size[0].lower():
                case '1'  | "1st":              self._unit = 1
                case '3'  | "3rd":              self._unit = 2
                case '5'  | "5th":              self._unit = 3
                case '7'  | "7th":              self._unit = 4
                case '9'  | "9th":              self._unit = 5
                case '11' | "11th":             self._unit = 6
                case '13' | "13th":             self._unit = 7

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._types_str[number % len(__class__._types_str)]

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
    def __init__(self, tones: int = 5):
        super().__init__(tones)

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
        import operand_generic as og
        if isinstance(operand, og.Scale):
            operand = operand.copy().modulate(self._unit)
            return operand
        else:
            return super().__rrshift__(operand)

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

class MidiTrack(Midi):
    """
    A MidiTrack() is how arrangements are split in multiple compositions in Midi files.
    
    Parameters
    ----------
    first : integer_like
        For a given track concerning a composition, there default is 0.
    """
    def __init__(self, *parameters):
        super().__init__(1)
        self._name: str = "Track 1"
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     return self._name
                    case _:                         return super().__mod__(operand)
            case str():                 return self._name
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        import operand_generic as og
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._name      == other % od.DataSource( str() )
            case str():
                return self._name       == other
            case _:
                return super().__eq__(other)    # Compares the _unit integer value
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["name"]     = self.serialize(self._name)            # It's a string already
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'MidiTrack':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "name" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._name      = self.deserialize(serialization["parameters"]["name"])     # It's a string already
        return self

    def __lshift__(self, operand: o.Operand) -> 'MidiTrack':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self._name = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case MidiTrack():
                super().__lshift__(operand)
                self._name          = operand._name
            case str():             self._name = operand
            case _:                 super().__lshift__(operand)
        return self

# Alias to the class MidiTrack
Track = MidiTrack

class Channel(Midi):
    """
    A Channel() is an identifier normally associated to an instrument in a given midi device.
    
    Parameters
    ----------
    first : integer_like
        For a given device, there are 16 channels ranging from 1 to 16
    """
    def __init__(self, unit: int = None):
        super().__init__( os.staff._channel % int() if unit is None else unit )

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

class Bend(Midi):
    """
    Bend() sets the bending of the pitch to be associated to the PitchBend() Element.
    
    Parameters
    ----------
    first : integer_like
        Pitch bending where 0 is no bending and other values from -8192 to 8191 are the intended bending,
        this bending is 2 semi-tones bellow or above respectively
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

class Program(Midi):
    """
    Program() represents the Program Number associated to a given Instrument.
    
    Parameters
    ----------
    first : integer_like
        A Program Number varies from 0 to 127
    """
    def __init__(self, unit: str = "Piano"):
        super().__init__()
        match unit:
            case str():
                self.nameToNumber(unit)
            case int() | float():
                self._unit = int(unit)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     return Program.numberToName(self._unit)
                    case _:                         return super().__mod__(operand)
            case str():                 return Program.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Program':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self.nameToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self.nameToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _instruments = [
                                                                            # Piano
        {   "midi_instrument": 0,   "names": ["Acoustic grand piano", "Piano"]    },
        {   "midi_instrument": 1,   "names": ["Bright acoustic piano"]    },
        {   "midi_instrument": 2,   "names": ["Electric grand piano"]    },
        {   "midi_instrument": 3,   "names": ["Honky tonk piano"]    },
        {   "midi_instrument": 4,   "names": ["Electric piano 1"]    },
        {   "midi_instrument": 5,   "names": ["Electric piano 2"]    },
        {   "midi_instrument": 6,   "names": ["Harpsicord"]    },
        {   "midi_instrument": 7,   "names": ["Clavinet"]    },
                                                                            # Chromatic percussion
        {   "midi_instrument": 8,   "names": ["Celesta", "Chromatic percussion"]    },
        {   "midi_instrument": 9,   "names": ["Glockenspiel"]    },
        {   "midi_instrument": 10,  "names": ["Music box"]    },
        {   "midi_instrument": 11,  "names": ["Vibraphone"]    },
        {   "midi_instrument": 12,  "names": ["Marimba"]    },
        {   "midi_instrument": 13,  "names": ["Xylophone"]    },
        {   "midi_instrument": 14,  "names": ["Tubular bell"]    },
        {   "midi_instrument": 15,  "names": ["Dulcimer"]    },
                                                                            # Organ
        {   "midi_instrument": 16,  "names": ["Hammond", "Drawbar organ", "Organ"]    },
        {   "midi_instrument": 17,  "names": ["Percussive organ"]    },
        {   "midi_instrument": 18,  "names": ["Rock organ"]    },
        {   "midi_instrument": 19,  "names": ["Church organ"]    },
        {   "midi_instrument": 20,  "names": ["Reed organ"]    },
        {   "midi_instrument": 21,  "names": ["Accordion"]    },
        {   "midi_instrument": 22,  "names": ["Harmonica"]    },
        {   "midi_instrument": 23,  "names": ["Tango accordion"]    },
                                                                            # Guitar
        {   "midi_instrument": 24,  "names": ["Nylon string acoustic guitar", "Guitar"]    },
        {   "midi_instrument": 25,  "names": ["Steel string acoustic guitar"]    },
        {   "midi_instrument": 26,  "names": ["Jazz electric guitar"]    },
        {   "midi_instrument": 27,  "names": ["Clean electric guitar"]    },
        {   "midi_instrument": 28,  "names": ["Muted electric guitar"]    },
        {   "midi_instrument": 29,  "names": ["Overdriven guitar"]    },
        {   "midi_instrument": 30,  "names": ["Distortion guitar"]    },
        {   "midi_instrument": 31,  "names": ["Guitar harmonics"]    },
                                                                            # Bass
        {   "midi_instrument": 32,  "names": ["Acoustic bass", "Bass"]    },
        {   "midi_instrument": 33,  "names": ["Fingered electric bass"]    },
        {   "midi_instrument": 34,  "names": ["Picked electric bass"]    },
        {   "midi_instrument": 35,  "names": ["Fretless bass"]    },
        {   "midi_instrument": 36,  "names": ["Slap bass 1"]    },
        {   "midi_instrument": 37,  "names": ["Slap bass 2"]    },
        {   "midi_instrument": 38,  "names": ["Synth bass 1"]    },
        {   "midi_instrument": 39,  "names": ["Synth bass 2"]    },
                                                                            # Strings
        {   "midi_instrument": 40,  "names": ["Violin", "Strings"]    },
        {   "midi_instrument": 41,  "names": ["Viola"]    },
        {   "midi_instrument": 42,  "names": ["Cello"]    },
        {   "midi_instrument": 43,  "names": ["Contrabass"]    },
        {   "midi_instrument": 44,  "names": ["Tremolo strings"]    },
        {   "midi_instrument": 45,  "names": ["Pizzicato strings"]    },
        {   "midi_instrument": 46,  "names": ["Orchestral strings", "Harp"]    },
        {   "midi_instrument": 47,  "names": ["Timpani"]    },
                                                                            # Ensemble
        {   "midi_instrument": 48,  "names": ["String ensemble 1", "Ensemble"]    },
        {   "midi_instrument": 49,  "names": ["String ensemble 2", "Slow strings"]    },
        {   "midi_instrument": 50,  "names": ["Synth strings 1"]    },
        {   "midi_instrument": 51,  "names": ["Synth strings 2"]    },
        {   "midi_instrument": 52,  "names": ["Choir aahs"]    },
        {   "midi_instrument": 53,  "names": ["Voice oohs"]    },
        {   "midi_instrument": 54,  "names": ["Synth choir", "Voice"]    },
        {   "midi_instrument": 55,  "names": ["Orchestra hit"]    },
                                                                            # Brass
        {   "midi_instrument": 56,  "names": ["Trumpet", "Brass"]    },
        {   "midi_instrument": 57,  "names": ["Trombone"]    },
        {   "midi_instrument": 58,  "names": ["Tuba"]    },
        {   "midi_instrument": 59,  "names": ["Muted trumpet"]    },
        {   "midi_instrument": 60,  "names": ["French horn"]    },
        {   "midi_instrument": 61,  "names": ["Brass ensemble"]    },
        {   "midi_instrument": 62,  "names": ["Synth brass 1"]    },
        {   "midi_instrument": 63,  "names": ["Synth brass 2"]    },
                                                                            # Reed
        {   "midi_instrument": 64,  "names": ["Soprano sax", "Reed"]    },
        {   "midi_instrument": 65,  "names": ["Alto sax"]    },
        {   "midi_instrument": 66,  "names": ["Tenor sax"]    },
        {   "midi_instrument": 67,  "names": ["Baritone sax"]    },
        {   "midi_instrument": 68,  "names": ["Oboe"]    },
        {   "midi_instrument": 69,  "names": ["English horn"]    },
        {   "midi_instrument": 70,  "names": ["Bassoon"]    },
        {   "midi_instrument": 71,  "names": ["Clarinet"]    },
                                                                            # Pipe
        {   "midi_instrument": 72,  "names": ["Piccolo", "Pipe"]    },
        {   "midi_instrument": 73,  "names": ["Flute"]    },
        {   "midi_instrument": 74,  "names": ["Recorder"]    },
        {   "midi_instrument": 75,  "names": ["Pan flute"]    },
        {   "midi_instrument": 76,  "names": ["Bottle blow", "Blown bottle"]    },
        {   "midi_instrument": 77,  "names": ["Shakuhachi"]    },
        {   "midi_instrument": 78,  "names": ["Whistle"]    },
        {   "midi_instrument": 79,  "names": ["Ocarina"]    },
                                                                            # Synth lead
        {   "midi_instrument": 80,  "names": ["Synth square wave", "Synth lead"]    },
        {   "midi_instrument": 81,  "names": ["Synth saw wave"]    },
        {   "midi_instrument": 82,  "names": ["Synth calliope"]    },
        {   "midi_instrument": 83,  "names": ["Synth chiff"]    },
        {   "midi_instrument": 84,  "names": ["Synth charang"]    },
        {   "midi_instrument": 85,  "names": ["Synth voice"]    },
        {   "midi_instrument": 86,  "names": ["Synth fifths saw"]    },
        {   "midi_instrument": 87,  "names": ["Synth brass and lead"]    },
                                                                            # Synth pad
        {   "midi_instrument": 88,  "names": ["Fantasia", "New age", "Synth pad"]    },
        {   "midi_instrument": 89,  "names": ["Warm pad"]    },
        {   "midi_instrument": 90,  "names": ["Polysynth"]    },
        {   "midi_instrument": 91,  "names": ["Space vox", "Choir"]    },
        {   "midi_instrument": 92,  "names": ["Bowed glass"]    },
        {   "midi_instrument": 93,  "names": ["Metal pad"]    },
        {   "midi_instrument": 94,  "names": ["Halo pad"]    },
        {   "midi_instrument": 95,  "names": ["Sweep pad"]    },
                                                                            # Synth effects
        {   "midi_instrument": 96,  "names": ["Ice rain", "Synth effects"]    },
        {   "midi_instrument": 97,  "names": ["Soundtrack"]    },
        {   "midi_instrument": 98,  "names": ["Crystal"]    },
        {   "midi_instrument": 99,  "names": ["Atmosphere"]    },
        {   "midi_instrument": 100, "names": ["Brightness"]    },
        {   "midi_instrument": 101, "names": ["Goblins"]    },
        {   "midi_instrument": 102, "names": ["Echo drops", "Echoes"]    },
        {   "midi_instrument": 103, "names": ["Sci fi"]    },
                                                                            # Ethnic
        {   "midi_instrument": 104, "names": ["Sitar", "Ethnic"]    },
        {   "midi_instrument": 105, "names": ["Banjo"]    },
        {   "midi_instrument": 106, "names": ["Shamisen"]    },
        {   "midi_instrument": 107, "names": ["Koto"]    },
        {   "midi_instrument": 108, "names": ["Kalimba"]    },
        {   "midi_instrument": 109, "names": ["Bag pipe"]    },
        {   "midi_instrument": 110, "names": ["Fiddle"]    },
        {   "midi_instrument": 111, "names": ["Shanai"]    },
                                                                            # Percussive
        {   "midi_instrument": 112, "names": ["Tinkle bell", "Percussive"]    },
        {   "midi_instrument": 113, "names": ["Agogo"]    },
        {   "midi_instrument": 114, "names": ["Steel drums"]    },
        {   "midi_instrument": 115, "names": ["Woodblock"]    },
        {   "midi_instrument": 116, "names": ["Taiko drum"]    },
        {   "midi_instrument": 117, "names": ["Melodic tom"]    },
        {   "midi_instrument": 118, "names": ["Synth drum"]    },
        {   "midi_instrument": 119, "names": ["Reverse cymbal"]    },
                                                                            # Sound effects
        {   "midi_instrument": 120, "names": ["Guitar fret noise", "Sound effects"]    },
        {   "midi_instrument": 121, "names": ["Breath noise"]    },
        {   "midi_instrument": 122, "names": ["Seashore"]    },
        {   "midi_instrument": 123, "names": ["Bird tweet"]    },
        {   "midi_instrument": 124, "names": ["Telephone ring"]    },
        {   "midi_instrument": 125, "names": ["Helicopter"]    },
        {   "midi_instrument": 126, "names": ["Applause"]    },
        {   "midi_instrument": 127, "names": ["Gunshot"]    }
    ]

    def nameToNumber(self, name: str = "Piano"):
        # Convert input words to lowercase
        name_split = name.lower().split()
        # Iterate over the instruments list
        for instrument in Program._instruments:
            for instrument_name in instrument["names"]:
                # Check if all input words are present in the name string
                if all(word in instrument_name.lower() for word in name_split):
                    self._unit = instrument["midi_instrument"]
                    return

    @staticmethod
    def numberToName(number: int) -> str:
        for instrument in Program._instruments:
            if instrument["midi_instrument"] == number:
                return instrument["names"][0]
        return "Unknown instrument!"

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
        super().__init__()
        match unit:
            case str():
                self.nameToNumber(unit)
            case int() | float():
                self._unit = int(unit)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():       return super().__mod__(operand)
            case str():                 return Number.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Number':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self.nameToNumber(operand % o.Operand())
                    case _:                         super().__lshift__(operand)
            case str():             self.nameToNumber(operand)
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
        {   "midi_number": 127, "default_value": 0,     "names": ["Poly On", "Polyphonic"]    }
    ]

    @staticmethod
    def getDefault(number: int) -> int:
        for controller in Number._controllers:
            if controller["midi_number"] == number:
                return controller["default_value"]
        return 0

    def nameToNumber(self, name: str = "Pan"):
        for controller in Number._controllers:
            for controller_name in controller["names"]:
                if controller_name.lower().find(name.strip().lower()) != -1:
                    self._unit = controller["midi_number"]
                    return

    @staticmethod
    def numberToName(number: int) -> str:
        for controller in Number._controllers:
            if controller["midi_number"] == number:
                return controller["names"][0]
        return "Unknown controller!"
