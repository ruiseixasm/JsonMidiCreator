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
import operand_data as od
import operand_frame as of
import operand_label as ol


class Generic(o.Operand):
    pass

class KeyNote(Generic):
    def __init__(self, key: int | str = None):
        self._key: ou.Key = ou.Key(key)
        self._octave: ou.Octave = ou.Octave()

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Key():          return self._key
                    case ou.Octave():       return self._octave
                    case _:
                        key = self._key % od.DataSource()
                        octave = self._octave % od.DataSource()
                        return 12 * (octave + 1) + key
            case of.Frame():        return self % (operand % o.Operand())
            case ou.Key():          return self._key.copy()
            case ou.Octave():       return self._octave.copy()
            case int():
                key = self._key % int()
                octave = self._octave % int()
                return 12 * (octave + 1) + key
            case ol.Null() | None:  return ol.Null()
            case _:                 return self.copy()

    def __eq__(self, other: 'KeyNote') -> bool:
        if self % ou.Octave() == other % ou.Octave() and self % ou.Key() == other % ou.Key():
            return True
        return False
    
    def __lt__(self, other: 'KeyNote') -> bool:
        if self % ou.Octave() < other % ou.Octave():    return True
        if self % ou.Octave() > other % ou.Octave():    return False
        if self % ou.Key() < other % ou.Key():          return True
        return False
    
    def __gt__(self, other: 'KeyNote') -> bool:
        if self % ou.Octave() > other % ou.Octave():    return True
        if self % ou.Octave() < other % ou.Octave():    return False
        if self % ou.Key() > other % ou.Key():          return True
        return False
    
    def __le__(self, other: 'KeyNote') -> bool:
        return not (self > other)
    
    def __ge__(self, other: 'KeyNote') -> bool:
        return not (self < other)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "key":      self._key % int(),
                "octave":   self._octave % int()
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
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Key():          self._key = operand % o.Operand()
                    case ou.Octave():       self._octave = operand % o.Operand()
            case KeyNote():
                self._key = (operand % od.DataSource( ou.Key() )).copy()
                self._octave = (operand % od.DataSource( ou.Octave() )).copy()
            case of.Frame():        self << (operand & self)
            case od.Load():
                self.loadSerialization( operand.getSerialization() )
            case ou.Key() | str():  self._key << operand
            case ou.Octave():       self._octave << operand
            case int():
                self._key       << operand    # key already does % 12
                self._octave    << operand // 12
        return self

    def __add__(self, operand) -> 'KeyNote':
        key_int: int = self._key % int()
        octave_int: int = self._octave % int()
        match operand:
            case of.Frame():
                return self + (operand & self)
            case int():
                key_int += operand
                octave_int += key_int // 12
            case ou.Key():
                key_int += operand % int()
                octave_int += key_int // 12
            case ou.Octave():
                octave_int += operand % int()
            case KeyNote():
                key_int += operand % ou.Key() % int()
                octave_int += operand % ou.Octave() % int() + key_int // 12
            case _: return self.copy()
        return KeyNote() << ou.Key(key_int) << ou.Octave(octave_int)
     
    def __sub__(self, operand) -> 'KeyNote':
        key_int: int = self._key % int()
        octave_int: int = self._octave % int()
        match operand:
            case of.Frame():
                return self - (operand & self)
            case int():
                key_int -= operand
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case ou.Key():
                key_int -= operand % int()
                octave_int -= max(-1 * key_int + 11, 0) // 12
            case ou.Octave():
                octave_int -= operand % int()
            case KeyNote():
                key_int -= operand % ou.Key() % int()
                octave_int -= operand % ou.Octave() % int() - max(-1 * key_int + 11, 0) // 12
            case _: return self.copy()
        return KeyNote() << ou.Key(key_int) << ou.Octave(octave_int)

class GenericScale(Generic):
    """
    A Scale() represents a given scale rooted in the key of C.
    
    Parameters
    ----------
    first : integer_like and string_like
        It can have the name of a scale as input, like, "Major" or "Melodic"
    """
    def __init__(self, scale: list[int] | str | int = None):
        self._scale: list[int] = [1] * 12   # DEFAULT GIVEN BY STAFF
        match scale:
            case list():
                if len(scale) == 12: self._scale = scale.copy()
            case str():
                scale_number = __class__.str_to_scale(scale)
                if scale_number >= 0:
                    self._scale = __class__._scale_scales[scale_number].copy()
                super().__init__(__class__.str_to_scale(scale))
            case int() | float():
                scale_number = round(scale)
                total_scales = len(__class__._scale_scales)
                if scale_number >= 0 and scale_number < total_scales:
                    self._scale = __class__._scale_scales[scale_number].copy()
            case _:
                scale = os.staff % od.DataSource( self ) % int() if scale is None else round(scale)
                super().__init__(scale)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():       return super().__mod__(operand)
            case list():                return self._scale.copy()
            case str():                 return __class__.get_scale_name(self._unit % len(__class__._scale_scales))
            case od.DataScale():        return od.DataScale() << __class__._scale_scales[self._unit % len(__class__._scale_scales)]
            case ou.Transposition():    return self.transposition(operand % int())
            case ou.Modulation():       return self.modulation(operand % int())
            case _:                     return super().__mod__(operand)

    def keys(self) -> int:
        scale_keys = 0
        self_scale = __class__._scale_scales[self._unit % len(__class__._scale_scales)]
        for key in self_scale:
            scale_keys += key
        return scale_keys

    def transposition(self, mode: int | str = "5th") -> int:
        transposition = 0
        mode_transpose = ou.Mode(mode) % od.DataSource() - 1
        self_scale = __class__._scale_scales[self._unit % len(__class__._scale_scales)]
        while mode_transpose > 0:
            transposition += 1
            if self_scale[transposition % 12]:
                mode_transpose -= 1
        return transposition

    def modulation(self, mode: int | str = "5th") -> list: # AKA as remode (remoding)
        self_scale = __class__._scale_scales[self._unit % len(__class__._scale_scales)]
        self_scale_copy = self_scale.copy()
        transposition = self.transposition(mode)
        if transposition != 0:
            for key_i in range(12):
                self_scale_copy[key_i] = self_scale[(key_i + transposition) % 12]
        return self_scale_copy

    def modulate(self, mode: int | str = "5th") -> 'GenericScale': # AKA as remode (remoding)
        modulated_scale = self.modulation(mode)
        for scale_i in range(len(__class__._scale_scales)):
            if __class__._scale_scales[scale_i] == modulated_scale:
                self._unit = scale_i
                break
        return self

    _scale_names = [
        ["Chromatic", "chromatic"],
        # Diatonic Scales
        ["Major", "Maj", "maj", "M", "Ionian", "ionian", "C", "1", "1st", "First"],
        ["Dorian", "dorian", "D", "2", "2nd", "Second"],
        ["Phrygian", "phrygian", "E", "3", "3rd", "Third"],
        ["Lydian", "lydian", "F", "4", "4th", "Fourth"],
        ["Mixolydian", "mixolydian", "G", "5", "5th", "Fifth"],
        ["minor", "min", "m", "Aeolian", "aeolian", "A", "6", "6th", "Sixth"],
        ["Locrian", "locrian", "B", "7", "7th", "Seventh"],
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
    _scale_scales = [
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
    def get_scale_name(scale_unit: int | list = 0) -> str:
        match scale_unit:
            case int():
                return __class__._scale_names[scale_unit % len(__class__._scale_scales)][0]
            case list():
                if len(scale_unit) == 12:
                    for scale_i in range(len(__class__._scale_scales)):
                        if __class__._scale_scales[scale_i] == scale_unit:
                            return __class__._scale_names[scale_i][0]
                else:
                    return "Empty Scale!"
        return "Unknown Scale!"

    @staticmethod
    def str_to_scale(scale_name: str = "Chromatic") -> int:
        for scale_i in range(len(__class__._scale_names)):
            for scale_j in range(len(__class__._scale_names[scale_i])):
                if scale_name.strip() == __class__._scale_names[scale_i][scale_j]:
                    return scale_i
        return -1

class Controller(Generic):
    def __init__(self, number: int | str = None):
        self._control_number: ou.ControlNumber  = ou.ControlNumber( number )
        self._control_value: ou.ControlValue    = ou.ControlValue( ou.ControlNumber.getDefault(self._control_number % int()) )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.ControlNumber():    return self._control_number
                    case ou.ControlValue():     return self._control_value
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            case ou.ControlNumber():    return self._control_number.copy()
            case ou.ControlValue():     return self._control_value.copy()
            case int() | float():       return self._control_value % int()
            case ol.Null() | None:      return ol.Null()
            case _:                     return self.copy()

    def __eq__(self, other: 'Controller') -> bool:
        if self % ou.ControlNumber() == other % ou.ControlNumber() and self % ou.ControlValue() == other % ou.ControlValue():
            return True
        return False
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "control_number":   self._control_number % int(),
                "control_value":    self._control_value % int()
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "control_number" in serialization["parameters"] and "control_value" in serialization["parameters"]):

            self._control_number    = ou.ControlNumber()    << od.DataSource( serialization["parameters"]["control_number"] )
            self._control_value     = ou.ControlValue()     << od.DataSource( serialization["parameters"]["control_value"] )
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Controller':
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.ControlNumber():    self._control_number = operand % o.Operand()
                    case ou.ControlValue():     self._control_value = operand % o.Operand()
            case Controller():
                self._control_number = (operand % od.DataSource( ou.ControlNumber() )).copy()
                self._control_value = (operand % od.DataSource( ou.ControlValue() )).copy()
            case of.Frame():            self << (operand & self)
            case od.Load():
                self.loadSerialization( operand.getSerialization() )
            case ou.ControlNumber():    self._control_number << operand
            case ou.ControlValue() | int() | float():
                                        self._control_value << operand
        return self

    def __add__(self, operand) -> 'Controller':
        control_value_int: int = self._control_value % int()
        match operand:
            case of.Frame():
                return self + (operand & self)
            case int():
                control_value_int += operand
            case ou.ControlValue():
                control_value_int += operand % int()
            case Controller():
                control_value_int += operand % ou.ControlValue() % int()
            case _:
                return self.copy()
        return self.copy() << control_value_int
    
    def __sub__(self, operand) -> 'Controller':
        control_value_int: int = self._control_value % int()
        match operand:
            case of.Frame():
                return self - (operand & self)
            case int():
                control_value_int -= operand
            case ou.ControlValue():
                control_value_int -= operand % int()
            case Controller():
                control_value_int -= operand % ou.ControlValue() % int()
            case _:
                return self.copy()
        return self.copy() << control_value_int
