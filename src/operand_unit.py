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
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Tuple, Optional, Any, Generic
from typing import Self

from fractions import Fraction
import json
import re
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_data as od

import operand_frame as of
import operand_label as ol


class Unit(o.Operand):
    """`Unit`

    This type of Operand is associated to an Integer.
    This class is intended to represent parameters that are whole numbers like midi messages from 0 to 127.

    Parameters
    ----------
    int(0), Fraction, float : Sets its single parameter value.
    """
    def __init__(self, *parameters):
        self._unit: int = 0
        super().__init__(*parameters)

    def unit(self, number: int = None) -> Self:
        return self << od.Pipe( number )

    def __mod__(self, operand: o.T) -> o.T:
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
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case bool():            return False if self._unit == 0 else True   # bool is a subclass of int !!
                    case int():             return self._unit           # returns a int()
                    case Fraction():        return Fraction(self._unit)
                    case float():           return float(self._unit)
                    case of.Frame():        return self % od.Pipe( operand._data )
                    case Unit() | ra.Rational():
                                            return operand.__class__() << od.Pipe( self._unit )
                    case _:                 return super().__mod__(operand)
            case bool():            return False if self._unit == 0 else True   # bool is a subclass of int !!
            case int():             return self._unit
            case Fraction():        return Fraction(self._unit)
            case float():           return float(self._unit)
            case of.Frame():        return self % operand
            case Unit() | ra.Rational():
                                    return operand.__class__() << od.Pipe( self._unit )
            case str():             return str(self._unit)
            case _:                 return super().__mod__(operand)

    def __bool__(self) -> bool:  # For Python 3
        return self._unit != 0

    def __nonzero__(self) -> bool:  # For Python 2
        return self.__bool__()
    
    def __not__(self) -> bool:
        return self._unit == 0
    
    def __eq__(self, other: any) -> bool:
        import operand_rational as ra
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case int() | float() | Fraction():
                return self._unit == other
            case Unit():
                return self._unit == other._unit
            case ra.Rational():
                return self._unit == int( other._rational )
            case od.Conditional():
                return other == self
            case _:
                if other.__class__ == o.Operand:
                    return True
        return False
    
    def __lt__(self, other: any) -> bool:
        import operand_rational as ra
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case int() | float() | Fraction():
                return self._unit < other
            case Unit():
                return self._unit < other._unit
            case ra.Rational():
                return self._unit < int( other._rational )
        return False
    
    def __gt__(self, other: any) -> bool:
        import operand_rational as ra
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case int() | float() | Fraction():
                return self._unit > other
            case Unit():
                return self._unit > other._unit
            case ra.Rational():
                return self._unit > int( other._rational )
        return False
    
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

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        import operand_element as oe
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Unit():
                super().__lshift__(operand)
                self._unit = operand._unit
            case od.Pipe():
                match operand._data:
                    case float() | Fraction() | bool():   # bool is a subclass of int !!
                                                    self._unit = int(operand._data)
                    case int():                     self._unit = operand._data
                    case Unit() | ra.Rational():    self._unit = operand._data % od.Pipe( int() )
            case float() | Fraction() | bool():   # bool is a subclass of int !!
                self._unit = int(operand)
            case int():
                self._unit = operand
            case ra.Rational():
                self._unit = operand % int()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ol.Null():
                return self
            case o.Operand():
                self << operand % self
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __iadd__(self, number: any) -> Self:
        import operand_rational as ra
        number = self._tail_lshift(number)      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case int() | Fraction() | float():
                self._unit = int( self._unit + number )
            case Unit():
                self._unit += number._unit
            case ra.Rational():
                self._unit = int( self._unit + number._rational )
        return self
    
    def __isub__(self, number: any) -> Self:
        import operand_rational as ra
        number = self._tail_lshift(number)      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case int() | Fraction() | float():
                self._unit = int( self._unit - number )
            case Unit():
                self._unit -= number._unit
            case ra.Rational():
                self._unit = int( self._unit - number._rational )
        return self
    
    def __imul__(self, number: any) -> Self:
        import operand_rational as ra
        number = self._tail_lshift(number)      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case int() | Fraction() | float():
                self._unit = int( self._unit * number )
            case Unit():
                self._unit *= number._unit
            case ra.Rational():
                self._unit = int( self._unit * number._rational )
        return self
    
    def __itruediv__(self, number: any) -> Self:
        import operand_rational as ra
        number = self._tail_lshift(number)      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case int() | Fraction() | float():
                if number != 0:
                    self._unit = int( self._unit / number )
            case Unit():
                if number._unit != 0:
                    self._unit = int( self._unit / number._unit )
            case ra.Rational():
                if number._rational != 0:
                    self._unit = int( self._unit / number._rational )
        return self

class Total(Unit):
    """`Unit -> Total`
    """
    pass

class PitchParameter(Unit):
    """`Unit -> PitchParameter`
    """
    pass

class Accidentals(PitchParameter):
    """`Unit -> PitchParameter -> Accidentals`
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

class Sharps(Accidentals):  # Sharps (###)
    """`Unit -> PitchParameter -> Accidentals -> Sharps`

    Sharps() is intended to be used with KeySignature to set its amount of Sharps.
    
    Parameters
    ----------
    int(1) : Sets the amount of sharps from 0 to 7 where 3 means "###".
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_sharps = len(re.findall(r"#", operand))
                    if total_sharps > 0:
                        self._unit = total_sharps
            case _:
                super().__lshift__(operand)
        return self

class Flats(Accidentals):   # Flats (bbb)
    """`Unit -> Accidentals -> Flats`

    Flats() is intended to be used with KeySignature to set its amount of Flats.
    
    Parameters
    ----------
    int(1) : Sets the amount of flats from 0 to 7 where 3 means "bbb".
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_flats = len(re.findall(r"b", operand))
                    if total_flats > 0:
                        self._unit = total_flats
            case _:
                super().__lshift__(operand)
        return self


class KeySignature(PitchParameter):       # Sharps (+) and Flats (-)
    """`Unit -> PitchParameter -> KeySignature`

    A KeySignature() consists in an integer from -7 to 7 describing the amount
    of Sharps for positive values and the amount of Flats for negative values.
    It also sets the type as Major or minor key signature.
    
    Parameters
    ----------
    int(0) : By default it has no Sharps or Flats, it's the C Major scale.
    bool(True) : By default it considers the Major scale.
    """
    def __init__(self, *parameters):
        self._major: bool = True
        self._mode_0: int = 0
        super().__init__(*parameters)
    
    _major_scale = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)    # Major scale for the default staff

    def get_tonic_key(self) -> int:
        circle_fifths_position: int = self._unit
        zero_key_int: int = 0  # C (Major)
        if not self._major:
            zero_key_int = 9   # A (minor)
        return (zero_key_int + circle_fifths_position * 7) % 12

    def get_scale_list(self) -> list[int]:
        if self._major: #                      A
            return [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major scale
                #                              |
        else:   #   ----------------------------
                #   |
            return [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]  # minor scale
                #   A

    def get_scale(self) -> list[int]:
        match self._mode_0 % 7:
            case 0: # Major Scale (C)
                return [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
            case 5: # minor scale (A)
                return [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
            case 1: # 1 dorian    (D)
                return [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0]
            case 2: # phrygian    (E)
                return [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0]
            case 3: # lydian      (F)
                return [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1]
            case 4: # mixolydian  (G)
                return [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0]
            case 6: # locrian     (B)
                return [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0]
        return [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]


    def is_enharmonic(self, tonic_key: int, key: int) -> bool:
        # if self._major_scale[tonic_key % 12] != 1:
        #     return True
        self_key_signature: list[int] = self._key_signatures[(self._unit + 7) % 15]
        return self_key_signature[key % 12] != 0


    def __mod__(self, operand: o.T) -> o.T:
        import operand_generic as og
        match operand:
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case KeySignature():        return self
                    case list():                return self % list()
                    case Major():               return Major() << od.Pipe(self._major)
                    case Mode():                return Mode(self._mode_0 + 1)
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case KeySignature():        return self.copy()
            case int():                 return self._unit
            case float():
                return float(self._mode_0 + 1)
            case TonicKey():
                return TonicKey(self.get_tonic_key())
            case Key():
                tonic_key: int = self.get_tonic_key()
                key_line: int = 0
                if self._unit < 0:
                    key_line = 1
                # It happens only for 7 Flats (-7) (Cb)
                if self.is_enharmonic(tonic_key, tonic_key):
                    key_line += 2    # All Sharps/Flats
                return Key( float(tonic_key + key_line * 12) )
            
            case Major():               return Major() << od.Pipe(self._major)
            case Minor():               return Minor() << od.Pipe(not self._major)
            case Sharps():
                if self._unit > 0:
                    return Sharps(self._unit)
                return Sharps(0)
            case Flats():
                if self._unit < 0:
                    return Flats(self._unit * -1)
                return Flats(0)
            case og.Scale():            return og.Scale(self % list())
            case Mode():                return Mode(self._mode_0 + 1)
            case list():                return self.get_scale()
            case str():
                if self._unit < 0:
                    flats: int = self._unit * -1
                    return "b" * flats
                return "#" * self._unit
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, KeySignature):
            return \
                self._unit == other._unit and self._major == other._major and \
                self._mode_0 == other._mode_0
        if isinstance(other, od.Conditional):
            return other == self
        return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["major"]            = self.serialize( self._major )
        serialization["parameters"]["mode_0"]           = self.serialize( self._mode_0 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeySignature':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "major" in serialization["parameters"] and "mode_0" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._major         = self.deserialize( serialization["parameters"]["major"] )
            self._mode_0        = self.deserialize( serialization["parameters"]["mode_0"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        import operand_generic as og
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeySignature():
                super().__lshift__(operand)
                self._major     = operand._major
                self._mode_0    = operand._mode_0
            case od.Pipe():
                match operand._data:
                    case int():     self._unit      = operand._data
                    case Major():   self._major     = operand._data.__mod__(od.Pipe( bool() ))
                    case Mode():    self._mode_0    = operand._data._unit - 1
            case int():     self._unit   = operand
            case float():   self._mode_0 = int(operand - 1)
            case Major() | Minor():
                self._major = operand == Major(True)
                if self._major:
                    self._mode_0 = 0    # Major
                else:
                    self._mode_0 = 5    # minor
            case Sharps() | Flats():
                self._unit = operand._unit
                if isinstance(operand, Flats):
                    self._unit *= -1
            case Key():
                if self._major:
                    self._unit = self._major_keys_accidentals[ operand % int() ]
                else:
                    self._unit = self._minor_keys_accidentals[ operand % int() ]
                major_scale: tuple[int] = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)
                major_pitch: int = operand._unit % 12
                if major_scale[major_pitch]:
                    self._mode_0 = sum(major_scale[:major_pitch]) # for indexes < operand._unit % 12
            case Mode():
                self._mode_0 = operand._unit - 1
            case og.Scale():
                for mode_0 in range(7):
                    if self.get_scale() == operand._scale:
                        self._mode_0 = mode_0
                        break
            case str(): # Processes series of "#" and "b"
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

    _sharps_and_flats: dict[int, tuple[int]] = {
        #    C     D     E  F     G     A     B
        -7: (0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1),
        -6: (0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1),
        -5: (0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0),
        -4: (0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0),
        -3: (0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0),
        -2: (0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0),
        -1: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0),
         0: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        +1: (0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0),
        +2: (0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0),
        +3: (0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0),
        +4: (0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0),
        +5: (0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0),
        +6: (0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0),
        +7: (1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0)
        #    C     D     E  F     G     A     B
    }

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

    _major_keys_accidentals: dict[int, int] = {
        23:     -7,     # Cb (11 + 12 = 23)

        18:     -6,     # Gb
        10:     -6,     # A#

        13:     -5,     # Db

        20:     -4,     # Ab
        8:      -4,     # G#

        15:     -3,     # Eb
        3:      -3,     # D#

        22:     -2,     # Bb
        5:      -1,     # F
        0:      +0,     # C
        7:      +1,     # G
        2:      +2,     # D
        9:      +3,     # A
        4:      +4,     # E
        11:     +5,     # B
        6:      +6,     # F#
        1:      +7      # C#
    }

    _minor_keys_accidentals: dict[int, int] = {
        20:     -7,     # Ab (8 + 12 = 20)
        3:      -6,     # Eb
        22:     -5,     # Bb
        5:      -4,     # F
        0:      -3,     # C
        7:      -2,     # G
        2:      -1,     # D
        9:      +0,     # A
        4:      +1,     # E
        11:     +2,     # B
        6:      +3,     # F#

        1:      +4,     # C#
        13:     +4,     # Db

        8:      +5,     # G#

        3:      +6,     # D#
        15:     +6,     # Eb

        10:     +7,     # A#
        18:     +7      # Gb
    }


class Tone(PitchParameter):
    """`Unit -> PitchParameter -> Tone`

    A Tone() represents a Key change in a given KeySignature or Scale, AKA whole-step.
    
    Parameters
    ----------
    int(0) : An Integer representing the amount of whole-steps, from 0 to higher.
    """
    pass

class Semitone(PitchParameter):
    """`Unit -> PitchParameter -> Semitone`

    A Semitone() represents a pitch in a Chromatic scale, AKA half-step.
    
    Parameters
    ----------
    int(0) : An Integer representing the amount of Chromatic steps, from 0 to 127.
    """
    pass


class Key(PitchParameter):
    """`Unit -> PitchParameter -> Key`

    A `Key` is an integer from 0 to 11 (12 to 23 for flats) that describes
    the 12 keys of an octave. A `Key` is processed like if it was a `TargetKey`.
    
    Parameters
    ----------
    int(0) : A number from 0 to 11 with 0 as default or the equivalent string key "C"
    """
    def key_signature(self, key_signature: 'KeySignature' = None) -> Self:
        self._key_signature = key_signature
        return self

    def sharp(self, unit: int = None) -> Self:
        return self << od.Pipe( Sharp(unit) )

    def flat(self, unit: int = None) -> Self:
        return self << od.Pipe( Flat(unit) )

    def natural(self, unit: int = None) -> Self:
        return self << od.Pipe( Natural(unit) )

    def degree(self, unit: int = None) -> Self:
        return self << od.Pipe( Degree(unit) )

    def scale(self, scale: list[int] | str = None) -> Self:
        import operand_generic as og
        return self << od.Pipe( og.Scale(scale) )

    def __mod__(self, operand: o.T) -> o.T:
        import operand_generic as og
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():
                        return Key._keys[self._unit % 48]
                    case _:
                        return super().__mod__(operand)

            case str():
                return Key._keys[self._unit % 48]

            case Sharp():
                line: int = self._unit // 12
                if line % 2 == 0:   # Even line
                    return Sharp(self._accidentals[self._unit % 48])
                return Sharp(0)
            case Flat():
                line: int = self._unit // 12
                if line % 2 == 1:   # Odd line
                    return Flat(self._accidentals[self._unit % 48] * -1)
                return Flat(0)

            case _:
                return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        import operand_generic as og
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return self % int() == other % int()    # This get's in consideration the just final key pressed
            case str():
                return self % str() == other
            case _:
                return super().__eq__(other)
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        import operand_generic as og
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe():
                match operand._data:
                    case int():
                        self._unit = operand._data
                    case float() | Fraction():
                        self._unit = int(operand._data)
                    case Semitone():
                        self._unit = operand._data % od.Pipe( int() )
                        self << Degree(1)

                    case str():
                        self._unit = self.getStringToNumber(operand._data) % 48
                    case _:
                        super().__lshift__(operand)

            case str():
                self_unit: int = self.getStringToNumber(operand)
                if self_unit != -1:
                    self._unit = self_unit

            case _:
                super().__lshift__(operand)
        return self

    _keys: list[str] = [
        "C",   "C#", "D",   "D#", "E",   "F",   "F#", "G",   "G#", "A",   "A#", "B",    # Black Sharps
        "C",   "Db", "D",   "Eb", "E",   "F",   "Gb", "G",   "Ab", "A",   "Bb", "B",    # Black Flats
        "B#",  "C#", "C##", "D#", "D##", "E#",  "F#", "F##", "G#", "G##", "A#", "A##",  # All Sharps
        "Dbb", "Db", "Ebb", "Eb", "Fb",  "Gbb", "Gb", "Abb", "Ab", "Bbb", "Bb", "Cb"    # All Flats
    ]

    _accidentals: list[int] = [
         0,    +1,    0,    +1,    0,     0,    +1,    0,    +1,    0,    +1,    0,     # Black Sharps
         0,    -1,    0,    -1,    0,     0,    -1,    0,    -1,    0,    -1,    0,     # Black Flats
        +1,    +1,   +2,    +1,   +2,    +1,    +1,   +2,    +1,   +2,    +1,   +2,     # All Sharps
        -2,    -1,   -2,    -1,   -1,    -2,    -1,   -2,    -1,   -2,    -1,   -1      # All Flats
    ]
    
    def getStringToNumber(self, key: str = "C") -> int:
        key_to_find: str = key.strip().lower()
        for index, value in enumerate(Key._keys):
            if value.lower().find(key_to_find) != -1:
                return index
        return -1

class TonicKey(Key):
    """`Unit -> PitchParameter -> Key -> TonicKey`

    An `TonicKey` represents the root note of a given pitch, with same pitch to a Degree of 1.
    The default value is the Tonic key is 0 representing the key of C.
    
    Parameters
    ----------
    int(0) : An Integer representing the key offset relative to the key of C.
    """
    pass

class RootKey(Key):
    """`Unit -> PitchParameter -> Key -> RootKey`

    An `RootKey` represents the note at the configured Degree, so for a Tonic C the IV Root Key
    becomes the Key F.
    
    Parameters
    ----------
    int(0) : An Integer representing the key offset relative to the key of C.
    """
    pass

class TargetKey(Key):
    """`Unit -> PitchParameter -> Key -> TargetKey`

    An `TargetKey` Key represents the actually played Key, meaning, the Key after rooted in a given
    `Degree` and Transposed by a given `Transposition`.
    
    Parameters
    ----------
    int(0) : An Integer representing the key offset relative to the key of C.
    """
    pass


class Octave(PitchParameter):
    """`Unit -> PitchParameter -> Octave`

    An Octave() represents the full midi keyboard, varying from -1 to 9 (11 octaves).
    
    Parameters
    ----------
    int(1) : An Integer representing the full midi keyboard octave varying from -1 to 9
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters) # By default it's 1 to be used in basic operations like + and -

class Degree(PitchParameter):
    """`Unit -> PitchParameter -> Degree`

    A Degree() represents its relation with a Tonic key on a scale and respective Progressions.
    Note that `Degree(-1)` sets the `Pitch` Degree to I and its Tonic key accordingly to its `Keysignature`.
    
    Parameters
    ----------
    int(1) : Accepts a numeral (5) or the string (V) with 1 as the default
    """
    def __init__(self, *parameters):
        self._semitones: float = 0.0
        super().__init__(1, *parameters) # By default the degree it's 1 (I, Tonic)

    _degree = ("I", "ii", "iii", "IV", "V", "vi", "viiº")

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, Degree):
            return self % float() == other % float()
        if isinstance(other, od.Conditional):
            return other == self
        return self % other == other
    
    def __lt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if isinstance(other, Degree):
            return self % float() < other % float()
        if isinstance(other, od.Conditional):
            return other < self
        return super().__lt__(other)
    
    def __gt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if isinstance(other, Degree):
            return self % float() > other % float()
        if isinstance(other, od.Conditional):
            return other > self
        return super().__gt__(other)
    

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case float():
                return round(self._unit + self._semitones, 1)
            case str():
                adjusted_degree: int = self._unit
                if adjusted_degree > 0:
                    adjusted_degree -= 1
                return __class__._degree[adjusted_degree % 7]
            case Sharp():
                semitones_int: int = round(self._semitones * 10)
                if semitones_int % 2 == 1:
                    return Sharp(round((semitones_int + 1) / 2))
                if semitones_int > 0:
                    return Sharp(self % Flat() * -1)
                return Sharp(0)
            case Flat():
                semitones_int: int = round(self._semitones * 10)
                if semitones_int % 2 == 0:
                    return Flat(round(semitones_int / 2))
                if semitones_int > 0:
                    return Flat(self % Sharp() * -1)
                return Flat(0)
            case Natural():
                if self._semitones == 0.0:
                    return Natural(True)
                return Natural(False)
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["semitones"] = self.serialize( self._semitones )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeySignature':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "semitones" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._semitones = self.deserialize( serialization["parameters"]["semitones"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Degree():
                self._unit      = operand._unit
                self._semitones = operand._semitones
            case od.Pipe():
                match operand._data:
                    case str():
                        self.stringSetDegree(operand._data)
                    case _:
                        super().__lshift__(operand)
            case float():
                self._unit = round(operand)
                self._semitones = round(operand - self._unit, 1)
            case str():
                self.stringSetDegree(operand)
            case Sharp():
                if operand < 0:
                    self << Flat(operand * -1)
                else:
                    self._semitones = round(min(0.9, max(0.0, operand._unit * 0.2 - 0.1)), 1)
            case Flat():
                if operand < 0:
                    self << Sharp(operand * -1)
                else:
                    self._semitones = round(min(0.9, max(0.0, operand._unit * 0.2)), 1)
            case Natural():
                self._semitones = 0.0
            case _:
                super().__lshift__(operand)
        return self


    def __iadd__(self, number: any) -> Self:
        number = self._tail_lshift(number)      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case Sharp():
                self << self % Sharp() + number
            case Flat():
                self << self % Flat() + number
            case Natural():
                return self # Does nothing
            case _:
                super().__iadd__(number)
        return self
    
    def __isub__(self, number: any) -> Self:
        number = self._tail_lshift(number)      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case Sharp():
                self << self % Sharp() - number
            case Flat():
                self << self % Flat() - number
            case Natural():
                return self # Does nothing
            case _:
                super().__iadd__(number)
        return self
    

    def stringSetDegree(self, string: str) -> Self:
        string = string.strip()
        match re.sub(r'[^a-z]', '', string.lower()):    # also removes "º" (base 0)
            case "i"   | "tonic":                   self._unit = 1
            case "ii"  | "supertonic":              self._unit = 2
            case "iii" | "mediant":                 self._unit = 3
            case "iv"  | "subdominant":             self._unit = 4
            case "v"   | "dominant":                self._unit = 5
            case "vi"  | "submediant":              self._unit = 6
            case "vii" | "leading tone":            self._unit = 7
        return self


class Transposition(PitchParameter):
    """`Unit -> PitchParameter -> Transposition`

    `Transposition` represents a transposition made by tones along a given Scale
    depending on the Pitch having its own Scale or not respectively.
    
    Parameters
    ----------
    int(0) : By default the `Root` note has no shifting, pitch unchanged.
    """
    pass

class Tones(Transposition):
    """`Unit -> PitchParameter -> Transposition -> Tones`

    A `Tones` represent the amount of the Transposition, it's a shorthand for `Transposition`
    and shall not be confused with `Tone`.
    
    Parameters
    ----------
    int(0) : By default the `Root` note has no transposition, pitch unchanged.
    """
    pass


class Sharp(PitchParameter):  # Sharp (#)
    """`Unit -> PitchParameter -> Sharp`

    A Sharp() sets a given Pitch as Sharped or not.
    
    Parameters
    ----------
    int(1) : Accepts a boolean or a numeral (0 or 1) to set Sharp as true or false
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_sharps = len(re.findall(r"#", operand))
                    if total_sharps > 0:
                        self._unit = 1
            case _:
                super().__lshift__(operand)
        return self


class Flat(PitchParameter):   # Flat (b)
    """`Unit -> PitchParameter -> Flat`

    A Flat() sets a given Pitch as Flatten or not.
    
    Parameters
    ----------
    int(1) : Accepts a boolean or a numeral (0 or 1) to set Flat as true or false
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_flats = len(re.findall(r"b", operand))
                    if total_flats > 0:
                        self._unit = 1
            case _:
                super().__lshift__(operand)
        return self

class Order(Unit):
    """`Unit -> Order`

    Sets which order to be used in the Arpeggiator.
    
        +-------+---------+
        | Value | Order   |
        +-------+---------+
        | 0     | None    |
        | 1     | Up      |
        | 2     | Down    |
        | 3     | UpDown  |
        | 4     | Chaotic |
        +----------+------+

    Parameters
    ----------
    int(0), str : Sets the Arpeggiator order.
    """
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     return Order.numberToName(self._unit)
                    case _:                         return super().__mod__(operand)
            case str():                 return Order.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     self.nameToNumber(operand._data)
                    case _:                         super().__lshift__(operand)
            case str():             self.nameToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _name_order: dict = {
        "None":         0,
        "Up":           1,
        "Down":         2,
        "UpDown":       3,
        "DownUp":       4,
        "Chaotic":      5
    }

    _order_name: dict = {
        0:              "None",
        1:              "Up",
        2:              "Down",
        3:              "UpDown",
        4:              "DownUp",
        5:              "Chaotic"
    }

    def nameToNumber(self, order: str = "Up"):
        # Convert input words to lowercase
        order_split = order.lower().split()
        # Iterate over the instruments list
        for key, value in Order._name_order.items():
            # Check if all input words are present in the order string
            if all(word in key.lower() for word in order_split):
                self._unit = value
                return

    @staticmethod
    def numberToName(number: int) -> str:
        if 0 <= number < len(Order._order_name):
            return Order._order_name[number]
        return "Unknown Order!"



class DrumKit(Unit):
    """`Unit -> DrumKit`

    Auxiliary object that represents the standard Midi Drum Kit.
    
    Parameters
    ----------
    int(35) : Accepts a numeral (35 to 82) or a String like "Drum".
    Channel(10), float : Sets the `Channel` associated with the kit.
    """
    def __init__(self, *parameters):
        self._channel_0: int = 9    # is the 10 base 1
        super().__init__(35, *parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     return DrumKit.numberToName(self._unit)
                    case Channel():                 return operand._data << self._channel_0 + 1
                    case _:                         return super().__mod__(operand)
            case str():                 return DrumKit.numberToName(self._unit)
            case Channel():             return Channel(self._channel_0 + 1)
            case float():               return float(self._channel_0 + 1)
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["channel_0"] = self.serialize(self._channel_0)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "channel_0" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._channel_0 = self.deserialize(serialization["parameters"]["channel_0"])
        return self
        
    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     self.nameToNumber(operand._data)
                    case Channel():                 self._channel_0 = 0x0F & operand._data._unit - 1
                    case _:                         super().__lshift__(operand)
            case str():             self.nameToNumber(operand)
            case Channel():         self._channel_0 = 0x0F & operand._unit - 1
            case float():           self._channel_0 = 0x0F & int(operand) - 1
            case _:                 super().__lshift__(operand)
        return self

    _drum_kit: dict = {
        "Acoustic Bass Drum":       35,
        "Bass Drum 1":              36,
        "Side Stick":               37,
        "Acoustic Snare":           38,
        "Hand Clap":                39,
        "Electric Snare":           40,
        "Low Floor Tom":            41,
        "Closed Hi-Hat":            42,
        "High Floor Tom":           43,
        "Pedal Hi-Hat":             44,
        "Low Tom":                  45,
        "Open Hi-Hat":              46,
        "Low-Mid Tom":              47,
        "Hi-Mid Tom":               48,
        "Crash Cymbal 1":           49,
        "High Tom":                 50,
        "Ride Cymbal 1":            51,
        "Chinese Cymbal":           52,
        "Ride Bell":                53,
        "Tambourine":               54,
        "Splash Cymbal":            55,
        "Cowbell":                  56,
        "Crash Symbol 2":           57,
        "Vibraslap":                58,
        "Ride Cymbal 2":            59,
        "Hi Bongo":                 60,
        "Low Bongo":                61,
        "Mute Hi Conga":            62,
        "Open Hi Conga":            63,
        "Low Conga":                64,
        "High Timbale":             65,
        "Low Timbale":              66,
        "High Agogo":               67,
        "Low Agogo":                68,
        "Cabasa":                   69,
        "Maracas":                  70,
        "Short Whistle":            71,
        "Long Whistle":             72,
        "Short Guiro":              73,
        "Long Guiro":               74,
        "Calves":                   75,
        "Hi Wood Block":            76,
        "Low Wood Block":           77,
        "Mute Cuica":               78,
        "Open Cuica":               79,
        "Mute Triangle":            80,
        "Open Triangle":            81,
        "Shaker":                   82
    }

    def nameToNumber(self, name: str = "Snare"):
        # Convert input words to lowercase
        name_split = name.lower().split()
        # Iterate over the instruments list
        for key, value in DrumKit._drum_kit.items():
            # Check if all input words are present in the name string
            if all(word in key.lower() for word in name_split):
                self._unit = value
                return

    @staticmethod
    def numberToName(number: int) -> str:
        for key, value in DrumKit._drum_kit.items():
            if value == number:
                return key
        return "Unknown Drum Kit!"


class Boolean(Unit):
    """`Unit -> Boolean`"""
    def __init__(self, *parameters):
        super().__init__(True, *parameters)

class Tied(Boolean):
    """`Unit -> Boolean -> Tied`

    Sets the respective Notes or derived elements as Tied.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set Tied as true or false. True is the Default.
    """
    pass

class Default(Boolean):
    """`Unit -> Boolean -> Default`"""
    pass

class Enable(Boolean):
    """`Unit -> Boolean -> Enable`"""
    pass

class Disable(Boolean):
    """`Unit -> Boolean -> Disable`"""
    pass

class Quality(Boolean):
    """`Unit -> Boolean -> Quality`"""
    pass

class Major(Quality):
    """`Unit -> Boolean -> Quality -> Major`

    Sets the respective Key Signature as Major, the default.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set as Major the Key Signature
    """
    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Minor():
                return self._unit != other._unit
            case _:
                return super().__eq__(other)    # Compares the _unit integer value

class Minor(Quality):
    """`Unit -> Boolean -> Quality -> Minor`

    Sets the respective Key Signature as minor.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set as minor the Key Signature
    """
    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Major():
                return self._unit != other._unit
            case _:
                return super().__eq__(other)    # Compares the _unit integer value

class Natural(Boolean):     # Natural (n)
    """`Unit -> Boolean -> Natural`

    Sets the respective Pitch as Natural, in which case sharps and flats aren't applied.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set as Natural the Pitch
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                elif len(re.findall(r"n", operand)) > 0:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Dominant(Boolean):    # Flats the seventh
    """`Unit -> Boolean -> Dominant`

    Sets the respective Chord configuration by flatting the seventh key.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set as Dominant the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
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
    """`Unit -> Boolean -> Diminished`

    Sets the respective Chord configuration by flatting the third and the fifth key.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set as Diminished the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.find("º") != -1 or operand.lower().find("dim") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Augmented(Boolean):   # Sharps the fifth
    """`Unit -> Boolean -> Augmented`

    Sets the respective Chord configuration by sharping the fifth key.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set as Augmented the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("aug") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Sus2(Boolean):        # Second instead of the third
    """`Unit -> Boolean -> Sus2`

    Sets the respective Chord configuration by replacing the third with the second degree.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set as Sus2 the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("sus2") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Sus4(Boolean):        # Fourth instead of the third
    """`Unit -> Boolean -> Sus4`

    Sets the respective Chord configuration by replacing the third with the fourth degree.
    
    Parameters
    ----------
    bool(True), int : Accepts a boolean or a numeral (0 or 1) to set as Sus4 the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("sus4") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class NRPN(Boolean):
    """`Unit -> Boolean -> NRPN`
    """
    pass

class HighResolution(Boolean):
    """`Unit -> Boolean -> HighResolution`
    """
    pass


class Mode(Unit):
    """`Unit -> Mode`

    Mode() represents the different scales (e.g., Ionian, Dorian, Phrygian)
    derived from the degrees of the major scale.
    
    Parameters
    ----------
    int(1) : A Mode Number varies from 1 to 7 with 1 being the default
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)         # By default the mode is 1 (1st)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     self.stringToNumber(operand._data)
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
            case '1'  | "1st" | "major" | "ionian":
                self._unit = 1
            case '2'  | "2nd" | "dorian":
                self._unit = 2
            case '3'  | "3rd" | "phrygian":
                self._unit = 3
            case '4'  | "4th" | "lydian":
                self._unit = 4
            case '5'  | "5th" | "mixolydian":
                self._unit = 5
            case '6'  | "6th" | "minor" | "aeolian":
                self._unit = 6
            case '7'  | "7th" | "locrian":
                self._unit = 7
            case '8'  | "8th":
                self._unit = 8

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._modes_str[number % len(__class__._modes_str)]

class Size(Unit):
    """`Unit -> Size`

    Size() represents the size of the Chord, like "7th", "9th", etc, or
    as the total number of keys, like integer 3, representing a triad, the default.
    
    Parameters
    ----------
    int(3) : A Size Number varies from "1st" to "13th" with "3rd" being the triad default
    """
    def __init__(self, *parameters):
        super().__init__(3, *parameters)         # Default Size is 3
            
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     self.stringToNumber(operand._data)
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


class Inversion(Unit):
    """`Unit -> Inversion`

    Inversion() sets the degree of inversion of a given chord.
    
    Parameters
    ----------
    int(1) : Inversion sets the degree of chords inversion starting by 0 meaning no inversion
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)


class Midi(Unit):
    """`Unit -> Midi`
    """
    pass

class PPQN(Midi):
    """`Unit -> Midi -> PPQN`

    PPQN() represent Pulses Per Quarter Note for Midi clock.
    
    Parameters
    ----------
    int(24) : The typical and the default value is 24, but it can be set( multiples of 24
    """
    def __init__(self, *parameters):
        super().__init__(24, *parameters)

class ClockStopModes(Midi):
    """`Unit -> Midi -> ClockStopModes`"""
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     return ClockStopModes._stop_modes_int[self._unit % 4]
                    case _:                         return super().__mod__(operand)
            case str():                 return ClockStopModes._stop_modes_int[self._unit % 4]
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():
                        mode_name: str = operand._data.strip()
                        if mode_name in ClockStopModes._stop_modes_str:
                            self._unit = ClockStopModes._stop_modes_str[mode_name]
                    case _:                         super().__lshift__(operand)
            case str():
                mode_name: str = operand.strip()
                if mode_name in ClockStopModes._stop_modes_str:
                    self._unit = ClockStopModes._stop_modes_str[mode_name]
            case _:                 super().__lshift__(operand)
        return self

    _stop_modes_str: dict[str, int] = {
        "Stop":     0,
        "Pause":    1,
        "Continue": 2,
        "Total":    3
    }

    _stop_modes_int: dict[int, str] = {
        0:          "Stop",
        1:          "Pause",
        2:          "Continue",
        3:          "Total"
    }


class MidiTrack(Midi):
    """`Unit -> Midi -> MidiTrack`

    A MidiTrack() is how arrangements are split in multiple compositions in Midi files.
    
    Parameters
    ----------
    int(1) : For a given track concerning a composition, there default is 1.
    str("Track 1") : The name of the Track, there default is "Track 1".
    """
    def __init__(self, *parameters):
        import operand_generic as og
        self._name: str             = "Track 1"
        self._devices: list[str]    = og.settings._devices.copy()
        super().__init__(1, *parameters)

    def devices(self, devices: list[str] = None) -> Self:
        import operand_generic as og
        if devices is not None:
            self._devices = devices
        else:
            self._devices = og.settings._devices.copy()
        return self

    def __mod__(self, operand: o.T) -> o.T:
        import operand_container as oc
        match operand:
            case od.Pipe():
                match operand._data:
                    case TrackNumber():         return operand._data << od.Pipe(self._unit)
                    case od.TrackName():        return operand._data << od.Pipe(self._name)
                    case oc.Devices():          return oc.Devices(self._devices)
                    case str():                 return self._name
                    case _:                     return super().__mod__(operand)
            case TrackNumber():         return TrackNumber(self._unit)
            case od.TrackName():        return od.TrackName(self._name)
            case str():                 return self._name
            case oc.Devices():          return oc.Devices(self._devices)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._name == other._name and self._devices == other._devices
            case TrackNumber():
                return self._unit == other._unit
            case od.TrackName():
                return self._unit == other._data
            case str():
                return self._name == other
            case _:
                return super().__eq__(other)    # Compares the _unit integer value
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["name"]     = self._name    # It's a string already
        serialization["parameters"]["devices"]  = self.serialize(self._devices)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "name" in serialization["parameters"] and "devices" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._name      = serialization["parameters"]["name"]    # It's a string already
            self._devices   = self.deserialize(serialization["parameters"]["devices"])
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case MidiTrack():
                super().__lshift__(operand)
                self._name      = operand._name
                self._devices   = operand._devices.copy()
            case od.Pipe():
                match operand._data:
                    case TrackNumber():         self._unit = operand._data._unit
                    case od.TrackName():        self._name = operand._data._data
                    case str():                 self._name = operand._data
                    case oc.Devices():          self._devices = operand % od.Pipe( list() )
                    case _:                     super().__lshift__(operand)
            case TrackNumber():         self._unit = operand._unit
            case od.TrackName():        self._name = operand._data
            case str():                 self._name = operand
            case oc.Devices():          self._devices = operand % list()
            case od.Device():           self._devices = oc.Devices(self._devices, operand) % od.Pipe( list() )
            case _:                     super().__lshift__(operand)
        return self


class TrackNumber(Midi):
    """`Unit -> Midi -> TrackNumber`
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)         # By default is Track number 1


class Channel(Midi):
    """`Unit -> Midi -> Channel`

    A Channel() is an identifier normally associated to an instrument in a given midi device.
    
    Parameters
    ----------
    int(1) : For a given device, there are 16 channels ranging from 1 to 16
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)         # By default is channel 1

class Velocity(Midi):
    """`Unit -> Midi -> Velocity`

    Velocity() represents the velocity or strength by which a key is pressed.
    
    Parameters
    ----------
    int(100) : A key velocity varies from 0 to 127
    """
    def __init__(self, *parameters):
        super().__init__(100, *parameters)         # By default is velocity 100

class Program(Midi):
    """`Unit -> Midi -> Program`

    Program() represents the Program Number associated to a given Instrument.
    
    Parameters
    ----------
    int(1) : A Program Number varies from 1 to 128 or it's known name like "Piano"
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)    # By default is 1 the Piano

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     return Program.numberToName(self._unit)
                    case _:                         return super().__mod__(operand)
            case int():                 return self._unit + 1
            case str():                 return Program.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     self.nameToNumber(operand._data)
                    case _:                         super().__lshift__(operand)
            case int():
                self._unit = operand - 1
            case str():
                operand = operand.strip()
                if operand.isdigit():
                    self._unit = int(operand) - 1
                else:
                    self.nameToNumber(operand)
            case _:
                super().__lshift__(operand)
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
    """`Unit -> Midi -> Value`

    Value() represents the Control Change value that is sent via Midi
    
    Parameters
    ----------
    int(0) : The Value shall be set from 0 to 127 or 0 to 16,383
        accordingly to the range of CC Midi values for 7 and 14 bits respectively
    """
    pass

class Pressure(Value):
    """`Unit -> Midi -> Value -> Pressure`

    Pressure() represents the intensity with which a key is pressed after being down.
    
    Parameters
    ----------
    first : integer_like
        A key pressure varies from 0 to 127
    """
    pass

class Bend(Value):
    """`Unit -> Midi -> Value -> Bend`

    Bend() sets the bending of the pitch to be associated to the PitchBend() Element.
    
    Parameters
    ----------
    int(0) : Pitch bending where 0 is no bending and other values from -8192 to 8191 are the intended bending,
        this bending is 2 semi-tones bellow or above respectively
    """
    pass

class Bank(Midi):   # Value of 0 means no Bank selected because Banks are 1 based
    """`Unit -> Midi -> Bank`
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)        # By default is 1 the Bank "A"

class Number(Midi):
    """`Unit -> Midi -> Number`

    Number() represents the number of the Control to be manipulated with the Value values.
    
    Parameters
    ----------
    int(0) : Allows the direct set with a number or in alternative with a name relative to the Controller
    """
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():       return super().__mod__(operand)
            case str():                 return Number.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.Pipe():
                match operand._data:
                    case str():                     self._unit = self.nameToNumber(operand._data)
                    case _:                         super().__lshift__(operand)
            case str():             self._unit = self.nameToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    @staticmethod
    def getDefaultValue(number: int | str) -> int:
        if isinstance(number, str):
            number = Number.nameToNumber(number)
        for controller in Number._controllers:
            if controller["midi_number"] == number:
                return controller["default_value"]
        return 0

    @staticmethod
    def nameToNumber(name: str = "Pan") -> int:
        for controller in Number._controllers:
            for controller_name in controller["names"]:
                if controller_name.lower().find(name.strip().lower()) != -1:
                    return controller["midi_number"]
        return 10   # Default is Pan

    @staticmethod
    def numberToName(number: int) -> str:
        for controller in Number._controllers:
            if controller["midi_number"] == number:
                return controller["names"][0]
        return "Unknown controller!"

    _controllers: list[dict[str, int | list[str]]] = [
        {   "midi_number": 0,   "default_value": 0,     "names": ["Bank Select"]    },
        {   "midi_number": 1,   "default_value": 0,     "names": ["Modulation Wheel", "Modulation"]    },
        {   "midi_number": 2,   "default_value": 0,     "names": ["Breath Controller"]    },
        
        {   "midi_number": 4,   "default_value": 0,     "names": ["Foot Controller", "Foot Pedal"]    },
        {   "midi_number": 5,   "default_value": 0,     "names": ["Portamento Time"]    },
        {   "midi_number": 6,   "default_value": 0,     "names": ["Data Entry MSB", "Data", "Value", "Data MSB", "Value MSB"]    },
        {   "midi_number": 7,   "default_value": 100,   "names": ["Main Volume"]    },
        {   "midi_number": 8,   "default_value": 64,    "names": ["Balance"]    },
        
        {   "midi_number": 10,  "default_value": 64,    "names": ["Pan"]    },
        {   "midi_number": 11,  "default_value": 0,     "names": ["Expression"]    },
        {   "midi_number": 12,  "default_value": 0,     "names": ["Effect Control 1"]    },
        {   "midi_number": 13,  "default_value": 0,     "names": ["Effect Control 2"]    },
        
        {   "midi_number": 38,  "default_value": 0,     "names": ["Data Entry LSB", "Data LSB", "Value LSB"]    },

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

        {   "midi_number": 98,  "default_value": 0,     "names": ["NRPN LSB", "LSB"]    },
        {   "midi_number": 99,  "default_value": 0,     "names": ["NRPN MSB", "MSB"]    },

        {   "midi_number": 120, "default_value": 0,     "names": ["All Sounds Off"]    },
        {   "midi_number": 121, "default_value": 0,     "names": ["Reset All Controllers"]    },
        {   "midi_number": 122, "default_value": 127,   "names": ["Local Control", "Local Keyboard"]    },
        {   "midi_number": 123, "default_value": 0,     "names": ["All Notes Off"]    },
        {   "midi_number": 124, "default_value": 0,     "names": ["Omni Off"]    },
        {   "midi_number": 125, "default_value": 0,     "names": ["Omni On"]    },
        {   "midi_number": 126, "default_value": 0,     "names": ["Mono On", "Monophonic"]    },
        {   "midi_number": 127, "default_value": 0,     "names": ["Poly On", "Polyphonic"]    }
    ]

class MSB(Midi):
    """`Unit -> Midi -> MSB`
    """
    pass


class LSB(Midi):
    """`Unit -> Midi -> LSB`
    """
    pass

