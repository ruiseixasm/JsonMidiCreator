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


# Units have never None values and are also const, with no setters
class Unit(Operand):
    def __init__(self, unit: int = None):
        self._unit: int = 0
        self._unit = os.global_staff % self % int() if unit is None else round(unit)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case int():     return round(self._unit)
            case float():   return round(1.0 * self._unit, 9)   # rounding to 9 avoids floating-point errors
            case _:         return operand

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
    
    # CHAINABLE OPERATIONS

    def __add__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__(self % int() + unit % int())
            case int() | float(): return self.__class__(self % int() + unit)
    
    def __sub__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__(self % int() - unit % int())
            case int() | float(): return self.__class__(self % int() - unit)
        return self.__class__(self % int() - unit)
    
    def __mul__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__((self % int()) * (unit % int()))
            case int() | float(): return self.__class__(self % int() * unit)
    
    def __truediv__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__((self % int()) / (unit % int()))
            case int() | float(): return self.__class__(self % int() / unit)
    
class Tempo(Unit):
    def __init__(self, tempo: int = None):
        super().__init__(tempo)

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
            case str():     return Key.getKey(self % int())
            case _:         return super().__mod__(operand)

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

class ValueUnit(Unit):
    def __init__(self, value_unit: int = None):
        super().__init__(value_unit)

class Number(Unit):
    def __init__(self, number: int = None):
        super().__init__(number)

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
            case list():    return Scale.getScale(self % int())
            case str():     return Scale.getScaleName(self % int())
            case _:         return super().__mod__(operand)

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
