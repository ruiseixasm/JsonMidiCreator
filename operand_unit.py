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
# Json Midi Creator Libraries
from operand import Operand
import operand_staff as os
import operand_frame as of
import operand_tag as ot


# Units have never None values and are also const, with no setters
class Unit(Operand):
    def __init__(self, unit: int = None):
        self._unit: int = 0
        self._unit = os.global_staff % self % int() if unit is None else round(unit)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():    return self % (operand % Operand())
            case int():         return round(self._unit)
            case float():       return round(1.0 * self._unit, 9)   # rounding to 9 avoids floating-point errors
            case _:             return ot.Null()

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
   
    def __add__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__(self % int() + unit % int())
            case int() | float(): return self.__class__(self % int() + unit)
        return self
    
    def __sub__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__(self % int() - unit % int())
            case int() | float(): return self.__class__(self % int() - unit)
        return self
    
    def __mul__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__((self % int()) * (unit % int()))
            case int() | float(): return self.__class__(self % int() * unit)
        return self
    
    def __truediv__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__((self % int()) / (unit % int()))
            case int() | float(): return self.__class__(self % int() / unit)
        return self
    
class Key(Unit):
    def __init__(self, key: str = None):
        match key:
            case str():
                super().__init__( Key.keyStrToKeyUnit(key) )
            case int() | float():
                super().__init__( key )
            case _:
                super().__init__( os.global_staff % self % int() )

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

class Octave(Unit):
    def __init__(self, octave: int = None):
        super().__init__(octave)

class Velocity(Unit):
    def __init__(self, velocity: int = None):
        super().__init__(velocity)

class Channel(Unit):
    def __init__(self, channel: int = None):
        super().__init__(channel)

class Scale(Unit):
    def __init__(self, scale: str = "Chromatic"):
        match scale:
            case str():
                super().__init__(Scale.scaleStrToScaleUnit(scale))
            case int() | float():
                super().__init__(scale)
            case _:
                super().__init__(None)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case list():        return Scale.getScale(self % int())
            case str():         return Scale.getScaleName(self % int())
            case _:             return super().__mod__(operand)

    _scale_names = [
        ["Chromatic", "chromatic"],
        # Diatonic Scales
        ["Major", "Maj", "Ionian", "ionian"],
        ["Dorian", "dorian"],
        ["Phrygian", "phrygian"],
        ["Lydian", "lydian"],
        ["Mixolydian", "mixolydian"],
        ["minor", "min", "Aeolian", "aeolian"],
        ["Locrian", "locrian"],
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

class Pitch(Unit):
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

class Inversion(Unit):
    def __init__(self, inversion: int = 0):
        super().__init__(inversion)

class Play(Unit):
    def __init__(self, verbose: bool = False):
        super().__init__(1 if verbose else 0)

class MidiValue(Unit):
    def __init__(self, midi_value: int = None):
        super().__init__(midi_value)

    def getMidi__midi_value(self) -> int:
        return max(min(self % int(), 127), 0)
    
class MidiCC(Unit):
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
