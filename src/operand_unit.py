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
        import operand_value as ov
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case Fraction():        return Fraction(self._unit).limit_denominator()
                    case float():           return float(self._unit)
                    case Integer():         return Integer() << od.DataSource( self._unit )
                    case ov.Float():        return ov.Float() << od.DataSource( self._unit )
                    case Unit():            return self
                    case ol.Null() | None:  return ol.Null()
                    case _:                 return self._unit           # returns a int()
            case of.Frame():        return self % (operand % o.Operand())
            case int():             return self._unit
            case float():           return float(self._unit)
            case Fraction():        return Fraction(self._unit).limit_denominator()
            case Integer():         return Integer() << self._unit
            case ov.Float():        return ov.Float() << self._unit
            case ol.Null() | None:  return ol.Null()
            case _:                 return self.copy()

    def __eq__(self, other_number: any) -> bool:
        import operand_value as ov
        match other_number:
            case Unit():
                return self._unit == other_number % od.DataSource( int() )
            case ov.Value():
                self_rational = Fraction( self._unit ).limit_denominator()
                return self_rational == other_number % od.DataSource( Fraction() )
            case int() | float() | Fraction():
                return self._unit == other_number
        return False
    
    def __lt__(self, other_number: any) -> bool:
        import operand_value as ov
        match other_number:
            case Unit():
                return self._unit < other_number % od.DataSource( int() )
            case ov.Value():
                self_rational = Fraction( self._unit ).limit_denominator()
                return self_rational < other_number % od.DataSource( Fraction() )
            case int() | float() | Fraction():
                return self._unit < other_number
        return False
    
    def __gt__(self, other_number: any) -> bool:
        import operand_value as ov
        match other_number:
            case Unit():
                return self._unit > other_number % od.DataSource( int() )
            case ov.Value():
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
        import operand_value as ov
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case int():                     self._unit = operand % o.Operand()
                    case float() | Fraction():      self._unit = int(operand % o.Operand())
                    case Integer() | ov.Float():    self._unit = operand % o.Operand() % od.DataSource( int() )
            case Unit():            self._unit = operand % od.DataSource( int() )
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case int() | float() | Fraction():
                self._unit = int(operand)
            case ov.Float():
                self._unit = operand % int()
        return self

    def __add__(self, number: any) -> 'Unit':
        import operand_value as ov
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case of.Frame():                    return self + (number & self)
            case Unit() | ov.Value():           return self.__class__() << od.DataSource( self._unit + number % od.DataSource() )
            case int() | float() | Fraction():  return self.__class__() << od.DataSource( self._unit + number )
        return self.copy()
    
    def __sub__(self, number: any) -> 'Unit':
        import operand_value as ov
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case of.Frame():                    return self - (number & self)
            case Unit() | ov.Value():           return self.__class__() << od.DataSource( self._unit - number % od.DataSource() )
            case int() | float() | Fraction():  return self.__class__() << od.DataSource( self._unit - number )
        return self.copy()
    
    def __mul__(self, number: any) -> 'Unit':
        import operand_value as ov
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case of.Frame():                    return self * (number & self)
            case Unit() | ov.Value():           return self.__class__() << od.DataSource( self._unit * (number % od.DataSource()) )
            case int() | float() | Fraction():  return self.__class__() << od.DataSource( self._unit * number )
        return self.copy()
    
    def __truediv__(self, number: any) -> 'Unit':
        import operand_value as ov
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case of.Frame():            return self / (number & self)
            case Unit() | ov.Value():
                if number % od.DataSource() != 0:
                    return self.__class__() << od.DataSource( self._unit / (number % od.DataSource()) )
            case int() | float() | Fraction():
                if number != 0:
                    return self.__class__() << od.DataSource( self._unit / number )
        return self.copy()

class Integer(Unit):
    pass

class Key(Unit):
    """
    A Key() is an integer from 0 to 11 that describes the 12 keys of an octave.
    
    Parameters
    ----------
    first : integer_like or string_like
        A number from 0 to 11 with 0 as default or the equivalent string key "C"
    """
    def __init__(self, unit: int | str = None):
        match unit:
            case str():
                super().__init__( Key.keyStrToKeyUnit(unit) )
            case int() | float():
                super().__init__( int(unit) % 12 )
            case _:
                super().__init__( 0 )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():       return super().__mod__(operand)
            case str():                 return Key.getKey(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Unit':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                super().__lshift__(operand)
                self._unit %= 12    # makes sure it's one of the Octave's key
            case Key():             super().__lshift__(operand)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case Unit():            self._unit = operand % int() % 12
            case int() | float():   self._unit = int(operand) % 12
            case str():             self._unit = __class__.keyStrToKeyUnit(operand)
        return self

    _keys: list[str] = ["C",  "C#", "D", "D#", "E",  "F",  "F#", "G", "G#", "A", "A#", "B",
                        "B#", "Db", "D", "Eb", "Fb", "E#", "Gb", "G", "Ab", "A", "Bb", "Cb"]
    
    @staticmethod
    def getKey(note_key: int = 0) -> str:
        return Key._keys[note_key % 12]

    @staticmethod
    def keyStrToKeyUnit(key: str = "C") -> int:
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

class KeySignature(Unit):       # Sharps (+) and Flats (-)
    ...

class Sharps(KeySignature):     # Sharps (#)
    ...

class Flats(KeySignature):      # Flats (b)
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
                match unit.strip().lower():
                    case "i"   | "tonic":                   unit = 1
                    case "ii"  | "supertonic":              unit = 2
                    case "iii" | "mediant":                 unit = 3
                    case "iv"  | "subdominant":             unit = 4
                    case "v"   | "dominant":                unit = 5
                    case "vi"  | "submediant":              unit = 6
                    case "vii" | "viiº" | "leading tone":   unit = 7
                    case _:                                 unit = 1
                super().__init__(unit)
            case int() | float():
                super().__init__(unit)
            case _:
                super().__init__( 1 )

    _degrees_str = ["None" , "I", "ii", "iii", "IV", "V", "vi", "viiº"]

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__._degrees_str[self._unit % len(__class__._degrees_str)]
            case _:             return super().__mod__(operand)

class Type(Unit):
    """
    Type() represents the size of the Chord, like "7th", "9th", etc.
    
    Parameters
    ----------
    first : integer_like or string_like
        A Type Number varies from "1st" to "13th" with "3rd" being the triad default
    """
    def __init__(self, unit: int | str = None):
        match unit:
            case str():
                match unit.strip().lower():
                    case '1'  | "1st":              unit = 1
                    case '3'  | "3rd":              unit = 2
                    case '5'  | "5th":              unit = 3
                    case '7'  | "7th":              unit = 4
                    case '9'  | "9th":              unit = 5
                    case '11' | "11th":             unit = 6
                    case '13' | "13th":             unit = 7
                    case _:                         unit = 3
                super().__init__(unit)
            case int() | float():
                super().__init__(unit)
            case _:
                super().__init__( 3 )

    _types_str = ["None" , "1st", "3rd", "5th", "7th", "9th", "11th", "13th"]

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__._types_str[self._unit % len(__class__._types_str)]
            case _:             return super().__mod__(operand)

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
                match unit.strip().lower():
                    case '1'  | "1st":              unit = 1
                    case '2'  | "2nd":              unit = 2
                    case '3'  | "3rd":              unit = 3
                    case '4'  | "4th":              unit = 4
                    case '5'  | "5th":              unit = 5
                    case '6'  | "6th":              unit = 6
                    case '7'  | "7th":              unit = 7
                    case '8'  | "8th":              unit = 8
                    case _:                         unit = 1
                super().__init__( unit )
            case int() | float():
                super().__init__( unit )
            case _:
                super().__init__( 1 )

        # 1 - First, 2 - Second, 3 - Third, 4 - Fourth, 5 - Fifth, 6 - Sixth, 7 - Seventh,
        # 8 - Eighth, 9 - Ninth, 10 - Tenth, 11 - Eleventh, 12 - Twelfth, 13 - Thirteenth,
        # 14 - Fourteenth, 15 - Fifteenth, 16 - Sixteenth, 17 - Seventeenth, 18 - Eighteenth,
        # 19 - Nineteenth, 20 - Twentieth.

    _modes_str = ["None" , "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__._modes_str[self._unit % len(__class__._modes_str)]
            case _:             return super().__mod__(operand)

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
                match unit.strip().lower():
                    case "sus2":            unit = 1
                    case "sus4":            unit = 2
                    case _:                 unit = 0
                super().__init__( unit )
            case int() | float():
                super().__init__( unit )
            case _:
                super().__init__( 0 )

    _sus_str = ["None" , "sus2", "sus4"]

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case str():         return __class__._sus_str[self._unit % len(__class__._sus_str)]
            case _:             return super().__mod__(operand)

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
        unit = Mode(mode) % od.DataSource()
        super().__init__(unit)

# class Transpose(Unit):
#     """
#     Transpose() does a modal Transpose of a given Scale or Scale.
    
#     Parameters
#     ----------
#     first : integer_like
#         Transpose a given Scale to 1 ("1st") as the default mode
#     """
#     def __init__(self, mode: int = None):
#         unit = Mode(mode) % od.DataSource()
#         super().__init__(unit)

class Modulation(Operation):    # Modal Modulation
    """
    A Modulation() is used to return a modulated Scale from a given Scale or Scale.
    
    Parameters
    ----------
    first : integer_like
        Modulation of a given Scale with 1 ("1st") as the default mode
    """
    def __init__(self, mode: int | str = None):
        unit = Mode(mode) % od.DataSource()
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
        unit = Mode(mode) % od.DataSource()
        super().__init__(unit)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(operand, od.Scale):
            operand.modulate(self._unit)
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
                c.jsonMidiPlay(operand.getPlayList(), False if self._unit == 0 else True )
        return operand

class Print(Unit):
    """
    Print() allows to get on the console the configuration of the source Operand in a JSON layout.
    
    Parameters
    ----------
    first : integer_like
        Sets the indent of the JSON print layout with the default as 4
    """
    def __init__(self, formatted: bool = None):
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

class ControlValue(Midi):
    """
    ControlValue() represents the Control Change value that is sent via Midi
    
    Parameters
    ----------
    first : integer_like
        The ControlValue shall be set from 0 to 127 accordingly to the range of CC Midi values
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class ControlNumber(Midi):
    """
    ControlNumber() represents the number of the Control to be manipulated with the ControlValue values.
    
    Parameters
    ----------
    first : integer_like and string_like
        Allows the direct set with a number or in alternative with a name relative to the Controller
    """
    def __init__(self, unit: str = "Pan"):
        match unit:
            case str():
                super().__init__( ControlNumber.nameToNumber(unit) )
            case int() | float():
                super().__init__(unit)
            case _:
                super().__init__(None)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():       return super().__mod__(operand)
            case str():                 return ControlNumber.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

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
        for controller in ControlNumber._controllers:
            if controller["midi_number"] == number:
                return controller["default_value"]
        return 0

    @staticmethod
    def nameToNumber(number: str = "Pan") -> int:
        for controller in ControlNumber._controllers:
            for controller_name in controller["names"]:
                if controller_name.lower().find(number.strip().lower()) != -1:
                    return controller["midi_number"]
        return 0

    @staticmethod
    def numberToName(number: int) -> str:
        for controller in ControlNumber._controllers:
            if controller["midi_number"] == number:
                return controller["names"][0]
        return "Bank Select"
