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
import json
# Json Midi Creator Libraries
import creator as c
from operand import Operand
import operand_staff as os
import operand_numeric as on
import operand_frame as of
import operand_tag as ot


# Units have never None values and are also const, with no setters
class Unit(on.Numeric):
    """
    This is a read only type of Operand that has associated an Integer.
    This class is intended to represent parameters that are whole numbers like in midi messages from 0 to 127

    Parameters
    ----------
    first : integer_like
        A read only Integer described as a Unit
    """
    def __init__(self, unit: int = None):
        self._unit: int = 0 if unit is None else round(unit)

    def __mod__(self, operand: Operand) -> Operand:
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
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case int():             return round(self._unit)
            case float():           return round(1.0 * self._unit, 12)   # rounding to 9 avoids floating-point errors
            case ot.Null() | None:  return ot.Null()
            case _:                 return self

    def __eq__(self, other_unit: 'Unit') -> bool:
        return self % int() == other_unit % int()
    
    def __lt__(self, other_unit: 'Unit') -> bool:
        return self % int() < other_unit % int()
    
    def __gt__(self, other_unit: 'Unit') -> bool:
        return self % int() > other_unit % int()
    
    def __le__(self, other_unit: 'Unit') -> bool:
        return not (self > other_unit)
    
    def __ge__(self, other_unit: 'Unit') -> bool:
        return not (self < other_unit)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "unit": self._unit
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "unit" in serialization):

            self._unit = serialization["unit"]
        return self

    def copy(self) -> 'Unit':
        return self.__class__(self._unit)

    def __lshift__(self, operand: Operand) -> 'Unit':
        match operand:
            case of.Frame():        self << (operand & self)
            case Unit():            self._unit = operand % int()
            case int() | float():   self._unit = round(operand)
        return self

    def __add__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case of.Frame():        return self + (unit & self)
            case Unit():            return self.__class__(self._unit + unit._unit)
            case int() | float():   return self.__class__(self._unit + unit)
        return self.copy()
    
    def __sub__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case of.Frame():        return self - (unit & self)
            case Unit():            return self.__class__(self._unit - unit._unit)
            case int() | float():   return self.__class__(self._unit - unit)
        return self.copy()
    
    def __mul__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case of.Frame():        return self * (unit & self)
            case Unit():            return self.__class__(self._unit * unit._unit)
            case int() | float():   return self.__class__(self._unit * unit)
        return self.copy()
    
    def __truediv__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case of.Frame():        return self / (unit & self)
            case Unit():            return self.__class__(self._unit / unit._unit)
            case int() | float():   return self.__class__(self._unit / unit)
        return self.copy()
    
class Key(Unit):
    """
    A Key() is an integer from 0 to 11 that describes the 12 keys of an octave.
    
    Parameters
    ----------
    first : integer_like or string_like
        A read only Integer from 0 to 11 or the equivalent string key like "C#" or "Gb"
    """
    def __init__(self, key: int | str = None):
        match key:
            case str():
                super().__init__( Key.keyStrToKeyUnit(key) )
            case int() | float():
                super().__init__( round(key) % 12 )
            case _:
                super().__init__( 0 )

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case str():         return Key.getKey(self % int())
            case _:             return super().__mod__(operand)

    _keys: list[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
                        "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    
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

class Octave(Unit):
    """
    An Octave() represents the full midi keyboard, varying from -1 to 9 (11 octaves).
    
    Parameters
    ----------
    first : integer_like
        A read only Integer representing the full midi keyboard octave varying from -1 to 9
    """
    def __init__(self, octave: int = None):
        super().__init__(octave)

class Velocity(Unit):
    """
    Velocity() represents the intensity with which a key is pressed.
    
    Parameters
    ----------
    first : integer_like
        A key velocity varies from 0 to 127 with 100 being normally the default
    """
    def __init__(self, velocity: int = None):
        super().__init__(velocity)

class Channel(Unit):
    """
    A Channel() is an identifier normally associated to an instrument in a given midi device.
    
    Parameters
    ----------
    first : integer_like
        For a given device, there are 16 channels ranging from 1 to 16
    """
    def __init__(self, channel: int = None):
        channel = os.global_staff % self % int() if channel is None else round(channel)
        super().__init__(channel)

class KeySignature(Unit):   # Sharps (+) and Flats (-)
    ...

class Scale(Unit):
    """
    A Scale() represents a given scale rooted in the key of C.
    
    Parameters
    ----------
    first : integer_like and string_like
        It can have the name of a scale as input, like, "Major" or "Melodic"
    """
    def __init__(self, scale: str = "Chromatic"):
        match scale:
            case str():
                super().__init__(Scale.scaleStrToScaleUnit(scale))
            case int() | float():
                super().__init__(scale)
            case _:
                scale = os.global_staff % self % int() if scale is None else round(scale)
                super().__init__(scale)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case list():        return Scale.getScale(self % int())
            case str():         return Scale.getScaleName(self % int())
            case _:             return super().__mod__(operand)

    def transpose(self, interval: int = 1) -> int:
        self_scale = Scale._scales[self % int()]
        chromatic_transposition = 0
        if interval > 0:
            while interval != 0:
                chromatic_transposition += 1
                if self_scale[chromatic_transposition % 12] == 1:
                    interval -= 1
        elif interval < 0:
            while interval != 0:
                chromatic_transposition -= 1
                if self_scale[chromatic_transposition % 12] == 1:
                    interval += 1
        return chromatic_transposition

    _scale_names = [
        ["Chromatic", "chromatic"],
        # Diatonic Scales
        ["Major", "Maj", "Ionian", "ionian", "C"],
        ["Dorian", "dorian", "D"],
        ["Phrygian", "phrygian", "E"],
        ["Lydian", "lydian", "F"],
        ["Mixolydian", "mixolydian", "G", "Dominant Seventh", "Dominant seventh", "dominant seventh", "Dominant", "Seventh"],
        ["minor", "min", "Aeolian", "aeolian", "A"],
        ["Locrian", "locrian", "B"],
        # Other Scales
        ["harmonic"],
        ["melodic"],
        ["octatonic_hw"],
        ["octatonic_wh"],
        ["pentatonic_maj", "Pentatonic"],
        ["pentatonic_min", "pentatonic"],
        ["diminished"],
        ["augmented"],
        ["blues"]
    ]
    _scales = [
    #       Db    Eb       Gb    Ab    Bb
    #       C#    D#       F#    G#    A#
    #    C     D     E  F     G     A     B
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        # Diatonic Scales
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        # Other Scales
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
        [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
        [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0]
    ]

    @staticmethod
    def getScale(scale_unit: int = 0):
        return Scale._scales[scale_unit % len(Scale._scales)]

    @staticmethod
    def getScaleName(scale_unit: int = 0):
        return Scale._scale_names[scale_unit % len(Scale._scales)][0]

    @staticmethod
    def scaleStrToScaleUnit(scale_name: str = "Chromatic") -> int:
        for scale_i in range(len(Scale._scale_names)):
            for scale_j in range(len(Scale._scale_names[scale_i])):
                if scale_name.strip() == Scale._scale_names[scale_i][scale_j]:
                    return scale_i
        return 0

class Mode(Unit):
    """
    A Mode() represents its relation with a Tonic key on a scale
    and respective Progressions.
    
    Parameters
    ----------
    first : integer_like
        Accepts a numeral (5) or the string (V) equivalent to the mode
    """
    def __init__(self, mode: int | str = None):
        match mode:
            case str():
                match mode.strip().lower():
                    case "i":   mode = 1
                    case "ii":  mode = 2
                    case "iii": mode = 3
                    case "iv":  mode = 4
                    case "v":   mode = 5
                    case "vi":  mode = 6
                    case "vii": mode = 7
                    case _:     mode = 1
                super().__init__(mode)
            case int() | float():
                super().__init__(mode)
            case _:
                super().__init__( 1 )

class Operation(Unit):
    pass

class Transposition(Operation):
    """
    A Transposition() is used to do a Transposition along a given Scale.
    
    Parameters
    ----------
    first : integer_like
        Accepts a numeral equivalent to the scales playable positions
    """
    def __init__(self, transposition: int = None):
        super().__init__(transposition)

class Progression(Operation):
    """
    A Progression() is used to do a Progression along a given Scale.
    
    Parameters
    ----------
    first : integer_like
        Accepts a numeral equivalent to the the Roman numerals,
        1 instead of I, 4 instead of IV and 5 instead of V
    """
    def __init__(self, mode: int = None):
        super().__init__(mode)

class Inversion(Operation):
    """
    Inversion() sets the degree of inversion of a given chord.
    
    Parameters
    ----------
    first : integer_like
        Inversion sets the degree of chords inversion starting by 0 meaning no inversion
    """
    def __init__(self, inversion: int = None):
        super().__init__(inversion)

class Pitch(Unit):
    """
    Pitch() sets the variation in the pitch to be associated to the PitchBend() Element.
    
    Parameters
    ----------
    first : integer_like
        Pitch variation where 0 is no variation and other values from -8192 to 8191 are the intended variation,
        this variation is 2 semi-tones bellow or above respectively
    """
    def __init__(self, pitch: int = None):
        super().__init__(pitch)

    def getMidi__pitch_pair(self) -> list[int]:
        amount = 8192 + self % int()    # 2^14 = 16384, 16384 / 2 = 8192
        amount = max(min(amount, 16383), 0)
        lsb = amount & 0x7F             # LSB - 0x7F = 127, 7 bits with 1s, 2^7 - 1
        msb = amount >> 7               # MSB - total of 14 bits, 7 for each side, 2^7 = 128
        return [msb, lsb]

#        bend down    center      bend up
#     0 |<----------- |8192| ----------->| 16383
# -8192                   0                 8191
# 14 bits resolution (MSB, LSB). Value = 128 * MSB + LSB
# min : The maximum negative swing is achieved with data byte values of 00, 00. Value = 0
# center: The center (no effect) position is achieved with data byte values of 00, 64 (00H, 40H). Value = 8192
# max : The maximum positive swing is achieved with data byte values of 127, 127 (7FH, 7FH). Value = 16384

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

    def __rrshift__(self, operand: Operand) -> Operand:
        c.jsonMidiPlay(operand.getPlayList(), False if self % int() == 0 else True )
        return operand

class Print(Unit):
    """
    Print() allows to get on the console the configuration of the source Operand in a JSON layout.
    
    Parameters
    ----------
    first : integer_like
        Sets the indent of the JSON print layout
    """
    def __init__(self, indent: int = 4):
        super().__init__(indent)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: Operand) -> Operand:
        serialized_json_str = json.dumps(operand.getSerialization())
        json_object = json.loads(serialized_json_str)
        json_formatted_str = json.dumps(json_object, indent = self % int())
        print(json_formatted_str)
        return operand


class MidiValue(Unit):
    """
    MidiValue() represents the Control Change value that is sent via Midi
    
    Parameters
    ----------
    first : integer_like
        The MidiValue shall be set from 0 to 127 accordingly to the range of CC Midi values
    """
    def __init__(self, midi_value: int = 64):
        super().__init__(midi_value)

    def getMidi__midi_value(self) -> int:
        return max(min(self % int(), 127), 0)
    
class MidiCC(Unit):
    """
    MidiCC() represents the number of the Control to be manipulated with the MidiValue values.
    
    Parameters
    ----------
    first : integer_like and string_like
        Allows the direct set with a number or in alternative with a name relative to the Controller
    """
    def __init__(self, name: str = "Pan"):
        match name:
            case str():
                super().__init__( MidiCC.nameToNumber(name) )
            case int() | float():
                super().__init__(name)
            case _:
                super().__init__(None)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case str():         return MidiCC.numberToName(self % int())
            case _:             return super().__mod__(operand)

    _controllers = [
        {   "midi_number": 0,   "default_value": 0,     "names": ["Bank Select"]    },
        {   "midi_number": 1,   "default_value": 0,     "names": ["Modulation Wheel"]    },
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
        for controller in MidiCC._controllers:
            if controller["midi_number"] == number:
                return controller["default_value"]
        return os.global_staff % MidiCC() % int()

    @staticmethod
    def nameToNumber(name: str = "Pan") -> int:
        for controller in MidiCC._controllers:
            for controller_name in controller["names"]:
                if controller_name.lower().find(name.strip().lower()) != -1:
                    return controller["midi_number"]
        return os.global_staff % MidiCC() % int()

    @staticmethod
    def numberToName(number: int) -> int:
        for controller in MidiCC._controllers:
            if controller["midi_number"] == number:
                return controller["names"][0]
        return os.global_staff % MidiCC() % str()