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
import math
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_staff as os
import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_frame as of
import operand_label as ol


class Generic(o.Operand):
    pass

class Track(Generic):
    # Class variable to keep track of the next track ID
    _next_track_id: int  = 0 # This is the unit ultimate value

    def __init__(self, *parameters):
        super().__init__()
        self._track_id: int             = Track._next_track_id
        Track._next_track_id += 1
        self._name: str                 = "Unnamed"
        self._midi_track: ou.MidiTrack  = ou.MidiTrack()
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     return self._name
                    case ou.Channel():              return self._midi_track._channel
                    case od.Device():               return self._midi_track._device
                    case _:                         return super().__mod__(operand)
            case str():                 return self._name
            case ou.Channel():          return self._midi_track._channel.copy()
            case od.Device():           return self._midi_track._device.copy()
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["name"]         = self.serialize(self._name)
        serialization["parameters"]["midi_track"]   = self.serialize(self._midi_track)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Track':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "name" in serialization["parameters"] and "midi_track" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._name          = self.deserialize(serialization["parameters"]["name"])
            self._midi_track    = self.deserialize(serialization["parameters"]["midi_track"])
        return self

    def __lshift__(self, operand: o.Operand) -> 'Track':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case str():                     self._name = operand % o.Operand()
                    case ou.MidiTrack():            self._midi_track = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Track():
                super().__lshift__(operand)
                self._name          = operand._name
                self._midi_track    << operand._midi_track
            case str():             self._name = operand
            case ou.MidiTrack():    self._midi_track << operand
            case ou.Channel():      self._midi_track._channel << operand
            case od.Device():       self._midi_track._device << operand
            case _:                 super().__lshift__(operand)
        return self

class TimeSignature(Generic):
    def __init__(self, top: int = 4, bottom: int = 4):
        super().__init__()
        self._top: int      = 4 if top is None else int(max(1, top))
        self._bottom: int   = 4 if bottom is None else int(math.pow(2, int(max(0, math.log2(bottom)))))

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case TimeSignature():       return self
                    case ra.BeatsPerMeasure():  return ra.BeatsPerMeasure() << self._top
                    case ra.BeatNoteValue():    return ra.BeatNoteValue() << 1 / self._bottom
                    # Calculated Values
                    case ra.NotesPerMeasure():  return ra.NotesPerMeasure() << self._top / self._bottom
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            case TimeSignature():       return self.copy()
            # Direct Values
            case ra.BeatsPerMeasure():  return ra.BeatsPerMeasure() << self._top
            case ra.BeatNoteValue():    return ra.BeatNoteValue() << 1 / self._bottom
            # Calculated Values
            case ra.NotesPerMeasure():  return ra.NotesPerMeasure() << self._top / self._bottom
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_signature: 'TimeSignature') -> bool:
        other_signature = self & other_signature    # Processes the tailed self operands or the Frame operand if any exists
        if other_signature.__class__ == o.Operand:
            return True
        if type(self) != type(other_signature):
            return False
        return  self._top           == other_signature._top \
            and self._bottom        == other_signature._bottom
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["top"]    = self._top
        serialization["parameters"]["bottom"] = self._bottom
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'TimeSignature':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "top" in serialization["parameters"] and "bottom" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._top           = serialization["parameters"]["top"]
            self._bottom        = serialization["parameters"]["bottom"]
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'TimeSignature':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ra.BeatsPerMeasure():  self._top       = operand % o.Operand() % od.DataSource( int() )
                    case ra.BeatNoteValue():    self._bottom    = round(1 / (operand % o.Operand() % od.DataSource( int() )))
            case TimeSignature():
                super().__lshift__(operand)
                self._top               = operand._top
                self._bottom            = operand._bottom
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.BeatsPerMeasure():  self._top       = int(max(1, operand % o.Operand() % int()))
            case ra.BeatNoteValue():    self._bottom    = int(math.pow(2, int(max(0, math.log2(1 / (operand % o.Operand() % int()))))))
        return self

class Pitch(Generic):
    def __init__(self, *parameters):
        super().__init__()
        self._octave: ou.Octave     = ou.Octave(4)  # By default it's the 4th Octave!
        self._key: ou.Key           = ou.Key()      # By default it's the Tonic key
        self._key_offset: int       = 0
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Pitch,
        those Parameters are the Key and the Octave.

        Examples
        --------
        >>> key_note = Pitch()
        >>> key_note % Key() >> Print(0)
        {'class': 'Key', 'parameters': {'key': 0}}
        >>> key_note % Key() % str() >> Print(0)
        C
        """
        self.octave_correction()    # Needed due to possible changes in staff KeySignature without immediate propagation (notice)
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case Pitch():         return self
                    case ou.Octave():       return self._octave
                    case ou.Key():          return self._key
                    case int():             return self % int()
                    case float():           return self % float()
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case Pitch():         return self.copy()
            case ou.Octave():       return self._octave.copy()
            case ou.Key():          return self._key.copy()
            case ou.Integer() | ou.Flat() | ou.Natural() | ou.Degree() | Scale() | ou.Mode() | list() | str():
                return self._key % operand
            case int():
                # IGNORES THE KEY SIGNATURE (CHROMATIC)
                return 12 * (self._octave._unit + 1) + self._key % int() + self._key_offset
            case float():
                # RESPECTS THE KEY SIGNATURE
                return 12 * (self._octave._unit + 1) + self._key % float() + self._key_offset
            case _:                 return super().__mod__(operand)

    def __eq__(self, operand: any) -> bool:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        if operand.__class__ == o.Operand:
            return True
        match operand:
            case Pitch():
                return self % float() == operand % float()
            case str() | ou.Key():
                return self._key    == operand
            case int() | ou.Octave():
                return self % od.DataSource( ou.Octave() ) == operand
        return False
    
    def __lt__(self, operand: any) -> bool:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                return self % float() < operand % float()
            case str() | ou.Key():
                return self._key    < operand
            case int() | ou.Octave():
                return self % od.DataSource( ou.Octave() ) < operand
        return False
    
    def __gt__(self, operand: any) -> bool:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                return self % float() > operand % float()
            case str() | ou.Key():
                return self._key    > operand
            case int() | ou.Octave():
                return self % od.DataSource( ou.Octave() ) > operand
        return False
    
    def __le__(self, operand: any) -> bool:
        return self == operand or self < operand
    
    def __ge__(self, operand: any) -> bool:
        return self == operand or self > operand
    
    def getSerialization(self) -> dict:
        self.octave_correction()    # Needed due to possible changes in staff KeySignature without immediate propagation (notice)
        serialization = super().getSerialization()
        serialization["parameters"]["key"]        = self._key.getSerialization()
        serialization["parameters"]["octave"]     = self._octave.getSerialization()
        serialization["parameters"]["key_offset"] = self._key_offset
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Pitch':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "octave" in serialization["parameters"] and "key" in serialization["parameters"] and "key_offset" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._key           = ou.Key().loadSerialization(serialization["parameters"]["key"])
            self._octave        = ou.Octave().loadSerialization(serialization["parameters"]["octave"])
            self._key_offset    = serialization["parameters"]["key_offset"]
            self.octave_correction()    # Needed due to possible changes in staff KeySignature without immediate propagation (notice)
        return self

    def __lshift__(self, operand: o.Operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Octave():       self._octave    = operand % o.Operand()
                    case ou.Key():          self._key       = operand % o.Operand()
            case Pitch():
                super().__lshift__(operand)
                self._octave    << operand._octave
                self._key       << operand._key
                self._key_offset = operand._key_offset
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Octave() | int() | ou.Integer():
                self._octave << operand
            case ou.Key() | float() | str() | ou.Semitone() | ou.Sharp() | ou.Flat() | ou.Natural() | ou.Degree() | Scale() | ou.Mode():
                self._key << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        if not isinstance(operand, tuple):
            self.octave_correction()
        return self
    
    def octave_correction(self):
        gross_octave: int = (12 * (self._octave._unit + 1) + int(self._key % float()) + self._key_offset) // 12 - 1
        octave_offset: int = gross_octave - self._octave._unit
        self._key_offset -= 12 * octave_offset
        self._octave._unit += octave_offset

    def __add__(self, operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        self_copy: Pitch = self.copy()
        match operand:
            case Pitch():
                # REVIEW TO DO A SUM OF "Pitch % int()" OF BOTH KEY NOTES
                new_keynote = self.__class__()
                self_int = self % int()
                operand_int = operand % int()
                sum_int = self_int + operand_int
                new_keynote._key << sum_int % 12
                new_keynote._octave._unit = sum_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case ou.Octave():
                self_copy._octave._unit += operand._unit
            case ou.Key() | int() | float() | Fraction() | ou.Unit() | ra.Rational():
                self_copy._key += operand   # This results in a key with degree 1 and unit = key % int()
            case _: return super().__add__(operand)
        self_copy.octave_correction()
        return self_copy
    
    def __sub__(self, operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        self_copy: Pitch = self.copy()
        match operand:
            case Pitch(): # It may result in negative KeyNotes (unplayable)!
                # REVIEW TO DO A SUM OF "Pitch % int()" OF BOTH KEY NOTES
                new_keynote = self.__class__()
                self_int = self % int()
                operand_int = operand % int()
                delta_int = self_int - operand_int
                new_keynote._key << delta_int % 12
                new_keynote._octave._unit = delta_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case ou.Octave():
                self_copy._octave._unit -= operand._unit
            case ou.Key() | int() | float() | Fraction() | ou.Unit() | ra.Rational():
                self_copy._key -= operand
            case _: return super().__add__(operand)
        self_copy.octave_correction()
        return self_copy

    def __mul__(self, operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                new_keynote = self.__class__()
                self_int = self % int()
                multiplied_int = self_int * operand
                new_keynote._key << multiplied_int % 12
                new_keynote._octave._unit = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case float():
                new_keynote = self.__class__()
                self_float = self % float()
                multiplied_int = int(self_float * operand)
                new_keynote._key << multiplied_int % 12
                new_keynote._octave._unit = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case _: return super().__mul__(operand)
    
    def __div__(self, operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                new_keynote = self.__class__()
                self_int = self % int()
                multiplied_int = int(self_int / operand)
                new_keynote._key << multiplied_int % 12
                new_keynote._octave._unit = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case float():
                new_keynote = self.__class__()
                self_float = self % float()
                multiplied_int = int(self_float / operand)
                new_keynote._key << multiplied_int % 12
                new_keynote._octave._unit = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case _: return super().__div__(operand)
    
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

    def __eq__(self, other: 'Controller') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if self % ou.Number() == other % ou.Number() and self % ou.Value() == other % ou.Value():
            return True
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["number"] = self._number.getSerialization()
        serialization["parameters"]["value"]  = self._value.getSerialization()
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Controller':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "number" in serialization["parameters"] and "value" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._number    = ou.Number().loadSerialization(serialization["parameters"]["number"])
            self._value     = ou.Value().loadSerialization(serialization["parameters"]["value"])
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Controller':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Number():    self._number = operand % o.Operand()
                    case ou.Value():     self._value = operand % o.Operand()
            case Controller():
                super().__lshift__(operand)
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
            case int() | float() | ou.Integer() | ra.Float() | Fraction():
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
            case int() | float() | ou.Integer() | ra.Float() | Fraction():
                value -= operand
            case _:
                return self.copy()
        return self.copy() << value

class Scale(Generic):
    """
    A Scale() represents a given scale rooted in the key of C.
    
    Parameters
    ----------
    first : integer_like and string_like
        It can have the name of a scale as input, like, "Major" or "Melodic"
    """
    def __init__(self, *parameters):
        super().__init__()
        self._scale_list: list[int] = []
        self._mode: ou.Mode         = ou.Mode()
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, a Scale has many extraction modes
        one type of extraction is its list() type of Parameter representing a scale
        but it's also possible to extract the same scale on other Tonic() key based on C.

        Examples
        --------
        >>> major_scale = Scale()
        >>> (major_scale >> Modulate("5th")) % str() >> Print()
        Mixolydian
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Mode():             return self._mode
                    case list():                return self._scale_list
                    case str():                 return __class__.get_scale_name(self._scale_list)
                    case int():                 return __class__.get_scale_number(self._scale_list)
                    case _:                     return super().__mod__(operand)
            case ou.Mode():             return self._mode.copy()
            case list():                return self.modulation(None)
            case str():                 return __class__.get_scale_name(self.modulation(None))
            case int():                 return __class__.get_scale_number(self.modulation(None))
            case ou.Transposition():    return self.transposition(operand % int())
            case ou.Modulation():       return self.modulation(operand % int())
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Scale') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._scale_list == other._scale_list
    
    def hasScale(self) -> bool:
        if self._scale_list == [] or self._scale_list == -1 or self._scale_list == "":
            return False
        return True

    def keys(self) -> int:
        scale_keys = 0
        self_scale = self._scale_list
        for key in self_scale:
            scale_keys += key
        return scale_keys

    def transposition(self, tones: int) -> int:        # Starting in C
        transposition = 0
        if isinstance(self._scale_list, list) and len(self._scale_list) == 12:
            modulated_scale = self.modulation(None)
            while tones > 0:
                transposition += 1
                if modulated_scale[transposition % 12]:
                    tones -= 1
        return transposition

    def modulation(self, mode: int | str = "5th") -> list: # AKA as remode (remoding)
        self_scale = self._scale_list.copy()
        if isinstance(self._scale_list, list) and len(self._scale_list) == 12:
            mode = self._mode if mode is None else mode
            # transposition = self.transposition(max(1, mode % int()) - 1)
            tones = max(1, mode % int()) - 1    # Modes start on 1, so, mode - 1 = tones
            transposition = 0
            if isinstance(self._scale_list, list) and len(self._scale_list) == 12:
                while tones > 0:
                    transposition += 1
                    if self._scale_list[transposition % 12]:
                        tones -= 1
            if transposition != 0:
                for key_i in range(12):
                    self_scale[key_i] = self._scale_list[(key_i + transposition) % 12]
        return self_scale

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["scale_list"]   = self._scale_list
        serialization["parameters"]["mode"]         = self._mode % od.DataSource( int() )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Scale':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "scale_list" in serialization["parameters"] and "mode" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._scale_list    = serialization["parameters"]["scale_list"]
            self._mode          = ou.Mode()     << od.DataSource( serialization["parameters"]["mode"] )
        return self
        
    def modulate(self, mode: int | str = "5th") -> 'Scale': # AKA as remode (remoding)
        self._scale_list = self.modulation(mode)
        return self

    def __lshift__(self, operand: any) -> 'Scale':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Mode():         self._mode = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case Scale():
                super().__lshift__(operand)
                self._scale_list    = operand._scale_list.copy()
                self._mode          << operand._mode
            case od.Serialization():
                self.loadSerialization(operand % od.DataSource( dict() ))
            case ou.Mode() | int():
                self._mode << operand
            case str():
                self_scale = __class__.get_scale(operand)
                if len(self_scale) == 12:
                    self._scale_list = self_scale.copy()
            case list():
                if len(operand) == 12 and all(x in {0, 1} for x in operand):
                    self._scale_list = operand.copy()
                elif operand == []:
                    self._scale_list = []
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _: super().__lshift__(operand)
        return self

    _names = [
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
        ["Diminished", "diminished"],
        ["Augmented", "augmented"],
        ["Blues", "blues"],
        ["Whole-tone", "Whole tone", "Whole", "whole"]
    ]
    _scales = [
    #       Db    Eb       Gb    Ab    Bb
    #       C#    D#       F#    G#    A#
    #    C     D     E  F     G     A     B
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        # Diatonic Scales
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],   # Major
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],   # Dorian
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],   # Phrygian
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],   # Lydian
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],   # Mixolydian
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],   # minor (Aeolian)
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],   # Locrian
        # Other Scales
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],   # Harmonic
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],   # Melodic
        [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],   # Octatonic HW
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],   # Octatonic WH
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],   # Pentatonic Major
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],   # Pentatonic minor
        [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],   # Diminished
        [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],   # Augmented
        [1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0],   # Blues
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]    # Whole-tone
    ]

    @staticmethod
    def get_scale_number(scale: int | str | list = 0) -> int:
        match scale:
            case int():
                total_scales = len(__class__._scales)
                if scale >= 0 and scale < total_scales:
                    return scale
            case str():
                for scale_i in range(len(__class__._names)):
                    for scale_j in range(len(__class__._names[scale_i])):
                        if scale.strip() == __class__._names[scale_i][scale_j]:
                            return scale_i
            case list():
                if len(scale) == 12:
                    for scale_i in range(len(__class__._scales)):
                        if __class__._scales[scale_i] == scale:
                            return scale_i
        return -1

    @staticmethod
    def get_scale_name(scale: int | str | list = 0) -> str:
        scale_number = __class__.get_scale_number(scale)
        if scale_number < 0:
            return "Unknown Scale!"
        else:
            return __class__._names[scale_number][0]

    @staticmethod
    def get_scale(scale: int | str | list = 0) -> list:
        if scale != [] and scale != -1 and scale != "":
            scale_number = __class__.get_scale_number(scale)
            if scale_number >= 0:
                return __class__._scales[scale_number]
        return []   # Has no scale at all

