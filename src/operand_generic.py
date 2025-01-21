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
import enum
import math
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_frame as of
import operand_label as ol
import operand_chaos as ch

TypeGeneric = TypeVar('TypeGeneric', bound='Generic')  # TypeGeneric represents any subclass of Operand


class Generic(o.Operand):
    pass



class TimeSignature(Generic):
    def __init__(self, top: int = 4, bottom: int = 4):
        self._top: int      = 4 if top is None else int(max(1,  top  ))
        # This formula is just to make sure it's a power of 2, it doesn't change the input value if it is already a power of 2
        self._bottom: int   = 4 if \
            not (isinstance(bottom, int) and bottom > 0) else int(math.pow(2, int(max(0, math.log2(  bottom  )))))
        super().__init__()

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand._data:
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case TimeSignature():       return self
                    case ra.BeatsPerMeasure():  return ra.BeatsPerMeasure() << self._top
                    case ra.BeatNoteValue():    return ra.BeatNoteValue() << 1 / self._bottom
                    # Calculated Values
                    case ra.NotesPerMeasure():  return ra.NotesPerMeasure() << self._top / self._bottom
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % (operand._data)
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
        serialization["parameters"]["top"]    = self.serialize( self._top )
        serialization["parameters"]["bottom"] = self.serialize( self._bottom )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'TimeSignature':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "top" in serialization["parameters"] and "bottom" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._top           = self.deserialize( serialization["parameters"]["top"] )
            self._bottom        = self.deserialize( serialization["parameters"]["bottom"] )
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'TimeSignature':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeSignature():
                super().__lshift__(operand)
                self._top               = operand._top
                self._bottom            = operand._bottom
            case od.DataSource():
                match operand._data:
                    case ra.BeatsPerMeasure():
                        self._top           = operand._data % od.DataSource( int() )
                    case ra.BeatNoteValue():
                        if operand._data % od.DataSource( int() ) > 0:
                            # This formula is just to make sure it's a power of 2, it doesn't change the input value if it is already a power of 2
                            self._bottom    = int(math.pow(2, int(max(0, math.log2(1 / (  operand._data % od.DataSource( int() )  ))))))
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.BeatsPerMeasure():
                self._top               = int(max(1, operand % int()))
            case ra.BeatNoteValue():
                if operand % int() > 0:
                    # This formula is just to make sure it's a power of 2, it doesn't change the input value if it is already a power of 2
                    self._bottom        = int(math.pow(2, int(max(0, math.log2(1 / (  operand % int()  ))))))
        return self

class Pitch(Generic):
    def __init__(self, *parameters):
        self._staff_reference: Staff            = defaults._staff
        self._key: int                          = self._staff_reference % ou.Key() // int()
        self._octave: int                       = 4     # By default it's the 4th Octave!
        self._degree: int                       = 1     # By default it's Degree 1
        self._sharp: int                        = 0     # By default not a Sharp or Flat
        self._natural: bool                     = False
        super().__init__(*parameters)


    def set_staff_reference(self, staff_reference: 'Staff' = None) -> 'Pitch':
        if isinstance(staff_reference, Staff):
            self._staff_reference = staff_reference
        return self

    def get_staff_reference(self) -> 'Staff':
        return self._staff_reference

    def reset_staff_reference(self) -> 'Pitch':
        self._staff_reference = defaults._staff
        return self


    def sharp(self, unit: bool = True) -> 'Pitch':
        return self << ou.Sharp(unit)

    def flat(self, unit: bool = True) -> 'Pitch':
        return self << ou.Flat(unit)

    def natural(self, unit: bool = True) -> 'Pitch':
        return self << ou.Natural(unit)

    def degree(self, unit: int = 1) -> 'Pitch':
        return self << ou.Degree(unit)


    # IGNORES THE KEY SIGNATURE (CHROMATIC)
    def get_key_int(self) -> int:

        staff_white_keys: tuple = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)  # Major scale
        accidentals_int: int    = self._staff_reference._key_signature._unit
        key_sharp: int          = 0
        key_int: int            = self._key % 12
        degree_transpose: int   = 0
        if self._degree > 0:
            degree_transpose    = self._degree - 1
        if self._degree < 0:
            degree_transpose    = self._degree + 1

        # strips existent accidentals
        if staff_white_keys[key_int] == 0: # Black key
            if self._key % 24 < 12: # sharps
                key_sharp = 1
                key_int -= 1
            else:                   # flats
                key_sharp = -1
                key_int += 1

        if self._staff_reference._scale.hasScale():
            key_scale: list[int] = self._staff_reference._scale % list() # Scale already modulated
            root_key: int = 0
        else:
            key_scale: list[int] = staff_white_keys     # Major scale
            root_key: int = key_int

        semitone_transpose: int = 0
        while degree_transpose > 0:
            semitone_transpose += 1
            if key_scale[(root_key + semitone_transpose) % 12]:          # Scale key
                degree_transpose -= 1
        while degree_transpose < 0:
            semitone_transpose -= 1
            if key_scale[(root_key + semitone_transpose) % 12]:          # Scale key
                degree_transpose += 1

        key_int += semitone_transpose

        if staff_white_keys[(key_int + semitone_transpose) % 12] == 0:  # Black key
            if self._natural:
                if accidentals_int < 0:
                    key_int += 1
                else:
                    key_int -= 1
        elif not self._natural:
            key_int += key_sharp        # applies pre-existing accidentals (regardless present key)
            if staff_white_keys[key_int % 12] == 1:  # Applies the Sharp or Flat if in a White key
                key_int += self._sharp  # applies Pitch self accidentals

        return key_int


    # APPLIES ONLY FOR KEY SIGNATURES (DEGREES)
    def get_key_float(self) -> float:

        # Whites Keys already sharpened or flattened due to time signature aren't considered (>= 24)
        if self._key < 24 and not (self._staff_reference._scale.hasScale() or self._natural):
            semitone_int: int = self.get_key_int()

            accidentals_int = self._staff_reference._key_signature._unit
            # Circle of Fifths
            sharps_flats = ou.KeySignature._key_signatures[(accidentals_int + 7) % 15] # [+1, 0, -1, ...]
            semitone_transpose = sharps_flats[semitone_int % 12]

            return float(semitone_int + semitone_transpose)
        
        return float(self.get_key_int())


    def octave_key_offset(self, key_offset: int | float) -> tuple[int, int]:
        
        original_key_int: int = self._key % 12
        final_key_int: int = original_key_int + int(key_offset)
        octave_offset: int = final_key_int // 12
        final_key: int = final_key_int % 12
        key_offset = final_key - original_key_int

        return octave_offset, key_offset
    
    def apply_key_offset(self, key_offset: int | float) -> 'Pitch':
        
        expected_pitch: float = self % float() + key_offset
        octave_offset, key_offset = self.octave_key_offset(key_offset)
        self._octave += octave_offset
        self._key += key_offset
        self._key %= 24   # Removes key from Key Signature specificity
        # if self % float() != expected_pitch:
        #     self._natural = True

        return self
    

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Pitch,
        those Parameters are the Key and the Octave.

        Examples
        --------
        >>> pitch = Pitch()
        >>> pitch % Key() >> Print(0)
        {'class': 'Key', 'parameters': {'key': 0}}
        >>> pitch % Key() % str() >> Print(0)
        C
        """
        match operand:
            case od.DataSource():
                match operand._data:
                    case of.Frame():        return self % od.DataSource( operand._data )
                    case Pitch():           return self
                    case ou.Octave():       return ou.Octave() << od.DataSource(self._octave)
                    case ou.Key():          return ou.Key() << od.DataSource(self._key)
                    case ou.Sharp():        return ou.Sharp() << od.DataSource(max(0, self._sharp))
                    case ou.Flat():         return ou.Flat() << od.DataSource(max(0, self._sharp * -1))
                    case ou.Natural():      return ou.Natural() << od.DataSource(self._natural)
                    case ou.Degree():       return ou.Degree() << od.DataSource(self._degree)
                    case int():             return self % int()
                    case float():           return self % float()
                    case str():
                        note_key = self % int() % 12
                        note_key += 12 * max(0, self._sharp * -1)   # second line of the list
                        return ou.Key._keys[note_key]
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % (operand._data)
            case Pitch():           return self.copy()

            case int(): # WITHOUT KEY SIGNATURE
                
                # IGNORES THE KEY SIGNATURE (CHROMATIC)
                return 12 * (self._octave + 1) + self.get_key_int()
             
            case float(): # WITH KEY SIGNATURE

                # RESPECTS THE KEY SIGNATURE
                return 12 * (self._octave + 1) + self.get_key_float()
            
            case ou.Semitone():
                return ou.Semitone(self % float())
            
            case ou.Octave():
                final_pitch: int = int(self % float())
                return ou.Octave( final_pitch // 12 - 1 )
            case ou.Sharp():
                final_pitch: int = int(self % float())
                if self._major_scale[final_pitch % 12] == 0:    # Black key
                    if self._staff_reference._key_signature._unit >= 0:
                        return ou.Sharp(True)
                return ou.Sharp(False)
            case ou.Flat():
                final_pitch: int = int(self % float())
                if self._major_scale[final_pitch % 12] == 0:    # Black key
                    if self._staff_reference._key_signature._unit < 0:
                        return ou.Flat(True)
                return ou.Flat(False)
            case ou.Natural():
                return ou.Natural() << od.DataSource(self._natural)
            
            case ou.KeySignature():
                return self._staff_reference._key_signature.copy()
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                return self._staff_reference._key_signature % operand
            case ou.Key():
                key_unit: int = int(self % float()) % 12
                return ou.Key( key_unit )
            
            case ou.Degree():
                return ou.Degree() << od.DataSource(self._degree)
            
            case str():
                key_note: int = int(self % float()) % 12
                key_line: int = self._key % 48 // 12
                if key_line < 2:
                    if self._staff_reference._key_signature._unit > 0:
                        key_line = 0
                    elif self._staff_reference._key_signature._unit < 0:
                        key_line = 1
                return ou.Key._keys[key_note + key_line * 12]
            
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        match other:
            case Pitch():
                return self % float() == other % float()
            case ou.Octave():
                return self % od.DataSource( ou.Octave() ) == other
            case int() | float() | str() | ou.Key():
                return self % other == other
            case _:
                return super().__eq__(other)
        return False
    
    def __lt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Pitch():
                return self % float() < other % float()
            case ou.Octave():
                return self % od.DataSource( ou.Octave() ) < other
            case int() | float():
                return self % other < other
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Pitch():
                return self % float() > other % float()
            case ou.Octave():
                return self % od.DataSource( ou.Octave() ) > other
            case int() | float():
                return self % other > other
            case _:
                return super().__gt__(other)
        return False
    
    def getSerialization(self) -> dict:

        serialization = super().getSerialization()
        serialization["parameters"]["key"]              = self.serialize( self._key )
        serialization["parameters"]["octave"]           = self.serialize( self._octave )
        serialization["parameters"]["degree"]           = self.serialize( self._degree )
        serialization["parameters"]["sharp"]            = self.serialize( self._sharp )
        serialization["parameters"]["natural"]          = self.serialize( self._natural )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Pitch':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key" in serialization["parameters"] and "sharp" in serialization["parameters"] and "natural" in serialization["parameters"] and
            "degree" in serialization["parameters"] and "octave" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._key           = self.deserialize( serialization["parameters"]["key"] )
            self._octave        = self.deserialize( serialization["parameters"]["octave"] )
            self._degree        = self.deserialize( serialization["parameters"]["degree"] )
            self._sharp         = self.deserialize( serialization["parameters"]["sharp"] )
            self._natural       = self.deserialize( serialization["parameters"]["natural"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                super().__lshift__(operand)
                self._key                   = operand._key
                self._octave                = operand._octave
                self._degree                = operand._degree
                self._sharp                 = operand._sharp
                self._natural               = operand._natural
                self._staff_reference       = operand._staff_reference
            case od.DataSource():
                match operand._data:
                    case ou.Octave():
                        self._octave    = operand._data._unit
                    case ou.Key():
                        self._key       = operand._data._unit
                    case int():
                        self._unit = operand._data
                    case float() | Fraction():
                        self._unit = int(operand._data)
                    case ou.Semitone():
                        self._unit = operand._data._unit
                    case ou.Sharp():
                        self._sharp = operand._data._unit % 2
                    case ou.Flat():
                        self._sharp = operand._data._unit % 2 * -1
                    case ou.Natural():
                        self._natural = operand._data // bool()
                    case ou.Degree():
                        self._degree = operand._data._unit
                    case str():
                        self._sharp     = \
                            ((operand._data).strip().lower().find("#") != -1) * 1 + \
                            ((operand._data).strip().lower().find("b") != -1) * -1
                        self._degree    = (self // ou.Degree() << ou.Degree(operand._data))._unit
                        self._key       = ou.Key(self._key, operand._data)._unit
                    case _:
                        super().__lshift__(operand)


            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Octave():
                octave_offset: ou.Octave = operand - self % ou.Octave()
                self._octave += octave_offset._unit
            case ou.Key():
                self._key = operand._unit
            case None:
                self._key = int( self._staff_reference._key_signature % float() )
            case int():
                if operand == 0:
                    self._key = int( self._staff_reference._key_signature % float() )
                else:
                    self._degree = operand

            case ou.Degree():
                self << operand._unit

            case float() | Fraction() | ou.Semitone():

                # It doesn't take into consideration the Key Signature (int not flat)
                if isinstance(operand, ou.Semitone):
                    key_offset: int = operand._unit - self % int()
                else:
                    key_offset: int = operand - self % int()
                self.apply_key_offset(key_offset)

            case ou.DrumKit():
                self._natural = False
                self._sharp = 0
                self << ou.Degree()         # Makes sure no Degree different of Tonic is in use
                self << operand // float()  # Sets the key number regardless KeySignature or Scale!
            case ou.Sharp():
                if max(0, self._sharp) != operand._unit:
                    self._sharp = operand._unit % 2
            case ou.Flat():
                if max(0, self._sharp * -1) != operand._unit:
                    self._sharp = operand._unit % 2 * -1
            case ou.Natural():
                self._natural = operand // bool()
            case str():
                string: str = operand.strip()
                self._sharp = \
                    (ou.Sharp(max(0, self._sharp)) << string)._unit + \
                    (ou.Flat(max(0, self._sharp * -1)) << string)._unit
                self._degree    = (self // ou.Degree() << operand)._unit
                self._key       = (self // ou.Key() << string)._unit
            case tuple():
                for single_operand in operand:
                    self << single_operand

            case _:
                super().__lshift__(operand)

        return self

    def __add__(self, operand: any) -> 'Pitch':
        self_copy: Pitch = self.copy()
        return self_copy.__iadd__(operand)
    
    def __iadd__(self, operand: any) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                self += operand % float()
            case ou.Octave():
                self._octave += operand._unit
            case int():
                self._degree += operand
            case ou.Degree():
                self._degree += operand._unit
            case ou.Tone():
                key_offset: int = self.move_semitones(operand % int())
                self.apply_key_offset(key_offset)
            case float() | Fraction():
                key_offset: int = int(operand)
                self.apply_key_offset(key_offset)
            case ra.Rational() | ou.Key() | ou.Semitone():
                key_offset: int = operand % int()
                self.apply_key_offset(key_offset)
        return self
    
    def __sub__(self, operand: any) -> 'Pitch':
        self_copy: Pitch = self.copy()
        return self_copy.__isub__(operand)
    
    def __isub__(self, operand: any) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                self -= operand % float()
            case ou.Octave():
                self._octave -= operand._unit
            case int():
                self._degree -= operand
            case ou.Degree():
                self._degree -= operand._unit
            case ou.Tone():
                key_offset: int = self.move_semitones(operand % int()) * -1
                self.apply_key_offset(key_offset)
            case float() | Fraction():
                key_offset: int = int(operand) * -1
                self.apply_key_offset(key_offset)
            case ra.Rational() | ou.Key() | ou.Semitone():
                key_offset: int = operand % int() * -1
                self.apply_key_offset(key_offset)
        return self

    def __mul__(self, operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                new_keynote = self.__class__()
                self_int = self % int()
                multiplied_int = self_int * operand
                new_keynote._key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case float():
                new_keynote = self.__class__()
                self_float = self % float()
                multiplied_int = int(self_float * operand)
                new_keynote._key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case _:
                return super().__mul__(operand)
    
    def __div__(self, operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                new_keynote = self.__class__()
                self_int = self % int()
                multiplied_int = int(self_int / operand)
                new_keynote._key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case float():
                new_keynote = self.__class__()
                self_float = self % float()
                multiplied_int = int(self_float / operand)
                new_keynote._key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case _:
                return super().__div__(operand)


    def move_semitones(self, move_tones: int) -> int:
        scale = self._major_scale    # Major scale for the default staff
        if self._staff_reference._scale.hasScale():
            scale = self._staff_reference._scale % list()
        move_semitones: int = 0
        while move_tones > 0:
            move_semitones += 1
            if scale[(self % int() + move_semitones) % 12]:
                move_tones -= 1
        while move_tones < 0:
            move_semitones -= 1
            if scale[(self % int() + move_semitones) % 12]:
                move_tones += 1
        return move_semitones
    
    _major_scale = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]    # Major scale for the default staff

    _white_keys: dict = {
            "c": 0,
            "d": 2,
            "e": 4,
            "f": 5,
            "g": 7,
            "a": 9,
            "b": 11
         }


class Controller(Generic):
    def __init__(self, *parameters):
        self._number: int       = ou.Number("Pan")._unit
        self._value: int        = ou.Number.getDefault(self._number)
        super().__init__(*parameters)

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
                match operand._data:
                    case ou.Number():           return ou.Number() << od.DataSource(self._number)
                    case ou.Value():            return ou.Value() << od.DataSource(self._value)
                    case Controller():          return self
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case _:                     return super().__mod__(operand)
            case ou.Number():           return ou.Number() << od.DataSource(self._number)
            case ou.Value():            return ou.Value() << od.DataSource(self._value)
            case int():                 return self._value
            case float():               return float(self._value)
            case Controller():          return self.copy()
            case of.Frame():            return self % (operand._data)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Controller') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if self._number == other._number and self % ou.Value() == other % ou.Value():
            return True
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["number"] = self.serialize( self._number )
        serialization["parameters"]["value"]  = self.serialize( self._value )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Controller':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "number" in serialization["parameters"] and "value" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._number    = self.deserialize( serialization["parameters"]["number"] )
            self._value     = self.deserialize( serialization["parameters"]["value"] )
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'Controller':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Controller():
                super().__lshift__(operand)
                self._number    = operand._number
                self._value     = operand._value
            case od.DataSource():
                match operand._data:
                    case ou.Number():    self._number = operand._data._unit
                    case ou.Value():     self._value = operand._data._unit
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Number():
                self._number = operand._unit
            case str():
                self._number = ou.Number(self._number, operand)._unit
            case ou.Value():
                self._value = operand._unit
            case int():
                self._value = operand
            case float():
                self._value = int(operand)
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __add__(self, operand: any) -> 'Controller':
        self_copy: Controller = self.copy()
        return self_copy.__iadd__(operand)

    def __iadd__(self, operand) -> 'Controller':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case o.Operand():
                self._value += operand % int()
            case int():
                self._value += operand
            case float() | Fraction():
                self._value += int(operand)
        return self
    
    def __sub__(self, operand: any) -> 'Controller':
        self_copy: Controller = self.copy()
        return self_copy.__isub__(operand)

    def __isub__(self, operand) -> 'Controller':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case o.Operand():
                self._value -= operand % int()
            case int():
                self._value -= operand
            case float() | Fraction():
                self._value -= int(operand)
        return self


class Scale(Generic):
    """
    A Scale() represents a given scale rooted in the key of C.
    
    Parameters
    ----------
    first : integer_like and string_like
        It can have the name of a scale as input, like, "Major" or "Melodic"
    """
    def __init__(self, *parameters):
        self._scale_list: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major by default
        self._mode: int             = 1
        super().__init__(*parameters)

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
                match operand._data:
                    case ou.Mode():             return ou.Mode() << od.DataSource(self._mode)
                    case list():                return self._scale_list
                    case str():                 return self.get_scale_name(self._scale_list)
                    case int():                 return self.get_scale_number(self._scale_list)
                    case ou.Key():              return ou.Key(self._tonics[ max(0, self.get_scale_number(self._scale_list)) ])
                    case _:                     return super().__mod__(operand)
            case ou.Mode():             return ou.Mode() << od.DataSource(self._mode)
            case list():
                modulated_scale: list[int] = self.modulation(None)
                if self.hasScale() and len(operand) > 0 and isinstance(operand[0], (int, ou.Key)):
                    if isinstance(operand[0], ou.Key):
                        key_int: int = operand[0]._unit
                    else:
                        key_int: int = operand[0]
                    key_scale: list = [0] * 12
                    for key_i in range(12):
                        key_scale[(key_i + key_int) % 12] = modulated_scale[key_i]
                    return key_scale
                return modulated_scale
            case str():                 return self.get_scale_name(self.modulation(None))
            case int():                 return self.get_scale_number(self.modulation(None))
            case ou.Transposition():    return self.transposition(operand % int())
            case ou.Modulation():       return self.modulation(operand % int())
            case ou.Key():              return ou.Key( self.get_tonic_number() )
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
            modulated_scale: list[int] = self.modulation(None)
            while tones > 0:
                transposition += 1
                if modulated_scale[transposition % 12]:
                    tones -= 1
        return transposition

    def modulation(self, mode: int | str = "5th") -> list[int]: # AKA as remode (remoding)
        self_scale = self._scale_list.copy()
        if isinstance(self._scale_list, list) and len(self._scale_list) == 12:
            mode_int = self._mode if mode is None else ou.Mode(mode) % int()
            tones = max(1, mode_int) - 1    # Modes start on 1, so, mode - 1 = tones
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
        serialization["parameters"]["scale_list"]   = self.serialize( self._scale_list )
        serialization["parameters"]["mode"]         = self.serialize( self._mode )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Scale':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "scale_list" in serialization["parameters"] and "mode" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._scale_list    = self.deserialize( serialization["parameters"]["scale_list"] )
            self._mode          = self.deserialize( serialization["parameters"]["mode"] )
        return self
        
    def modulate(self, mode: int | str = "5th") -> 'Scale': # AKA as remode (remoding)
        self._scale_list = self.modulation(mode)
        return self

    def __lshift__(self, operand: any) -> 'Scale':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Scale():
                super().__lshift__(operand)
                self._scale_list    = operand._scale_list.copy()
                self._mode          = operand._mode
            case od.DataSource():
                match operand._data:
                    case ou.Mode():         self._mode = operand._data._unit
                    case _:                 super().__lshift__(operand)
            case od.Serialization():
                self.loadSerialization(operand % od.DataSource( dict() ))
            case int():
                self._mode = operand
            case ou.Mode():
                self._mode = operand._unit
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

    _names: list[list[str]] = [
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
    _scales: list[list[int]] = [
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

    _tonics: list[int] = [
        # Chromatic scale
        0,  # C
        # Diatonic scales
        0,  # C
        2,  # D
        4,  # E
        5,  # F
        7,  # G
        9,  # A
        11, # B
        # Other Scales
        # Harmonic scale
        9,  # A
        # Melodic
        9,  # A
        # Octatonic HW
        0,  # C
        # Octatonic WH
        0,  # C
        # Pentatonic Major
        0,  # C
        # Pentatonic minor
        9,  # A
        # Diminished
        0,  # C
        # Augmented
        0,  # C
        # Blues
        9,  # A
        # Whole-tone
        0   # C
    ]

    def get_tonic_number(self) -> int:
        net_mode: int = self._mode - 1
        self_tonic: int = self._tonics[ max(0, self.get_scale_number(self._scale_list)) ]
        move_tonic: int = 0
        while net_mode > 0:
            move_tonic += 1
            if self._scale_list[move_tonic % 12] == 1:
                net_mode -= 1
        return self_tonic + move_tonic

    @staticmethod
    def get_scale_number(scale: int | str | list = 0) -> int:
        match scale:
            case int():
                total_scales = len(__class__._scales)
                if scale >= 0 and scale < total_scales:
                    return scale
            case str():
                scale_name = scale.strip()
                for index, names in enumerate(__class__._names):
                    for name in names:
                        if name == scale_name:
                            return index
            case list():
                if len(scale) == 12:
                    for index, scale_list in enumerate(__class__._scales):
                        if scale_list == scale:
                            return index
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



class Staff(Generic):
    def __init__(self, *parameters):
        super().__init__()
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._tempo: Fraction                       = Fraction(120)
        self._time_signature: TimeSignature         = TimeSignature(4, 4)
        self._quantization: Fraction                = Fraction(1/16)
        # Key Signature is an alias of Sharps and Flats of a Scale
        self._key_signature: ou.KeySignature        = ou.KeySignature()
        self._scale: Scale                          = Scale([])
        self._measures: int                         = 8
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Staff,
        those Parameters are the ones that define a Staff as global defaults,
        they include the ones relative to the time signature like Beats per Measure
        and Neat Note Value, the Tempo, the Quantization among others.

        Examples
        --------
        >>> defaults % Tempo() % float()
        120.0
        >>> defaults << BeatsPerMeasure(3)
        >>> defaults % BeatsPerMeasure() % float()
        3.0
        """
        match operand:
            case od.DataSource():
                match operand._data:
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case ra.Tempo():            return ra.Tempo(self._tempo)
                    case TimeSignature():       return self._time_signature
                    case ra.Quantization():     return ra.Quantization(self._quantization)
                    case ou.KeySignature():     return self._key_signature
                    case Scale():               return self._scale
                    case ra.BeatsPerMeasure():  return self._time_signature % od.DataSource( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.DataSource( ra.BeatNoteValue() )
                    case ra.Measures():         return ra.Measures(self._measures)
                    # Calculated Values
                    case ra.NotesPerMeasure():
                        return self._time_signature % od.DataSource( ra.NotesPerMeasure() )
                    case ra.StepsPerNote():
                        return ra.StepsPerNote() << od.DataSource( 1 / self._quantization )
                    case ra.StepsPerMeasure():
                        return ra.StepsPerMeasure() \
                            << od.DataSource( self % od.DataSource( ra.StepsPerNote() ) % od.DataSource( Fraction() ) \
                                * (self % od.DataSource( ra.NotesPerMeasure() ) % od.DataSource( Fraction() )))
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % (operand._data)
            # Direct Values
            case of.Frame():            return self % od.DataSource( operand._data )
            case ra.Tempo():            return ra.Tempo(self._tempo)
            case TimeSignature():       return self._time_signature.copy()
            case ra.Quantization():     return ra.Quantization(self._quantization)
            case ou.KeySignature():     return self._key_signature.copy()
            case Scale():               return self._scale.copy()
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                                        return self._key_signature % operand
            case ra.BeatsPerMeasure():  return self._time_signature % ra.BeatsPerMeasure()
            case ra.BeatNoteValue():    return self._time_signature % ra.BeatNoteValue()
            case ra.Measures():         return ra.Measures(self._measures)
            case ou.Measure():          return ou.Measure(self._measures)
            # Calculated Values
            case ou.Key():
                if self._scale.hasScale():
                    return self._scale % ou.Key()
                return self._key_signature % ou.Key()
            case ra.NotesPerMeasure():
                return self._time_signature % ra.NotesPerMeasure()
            case ra.StepsPerNote():
                return ra.StepsPerNote() << 1 / self._quantization
            case ra.StepsPerMeasure():
                return ra.StepsPerMeasure() \
                    << (self % ra.StepsPerNote() % Fraction()) * (self % ra.NotesPerMeasure() % Fraction())
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: 'Staff') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._tempo             == other._tempo \
            and self._time_signature    == other._time_signature \
            and self._quantization      == other._quantization \
            and self._key_signature     == other._key_signature \
            and self._measures          == other._measures

    #######################################################################
    # Conversion (Simple, One-way) | Only destination Staff is considered #
    #######################################################################

    # The most internally called method
    def convertToBeats(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Beats':
        beats: Fraction = Fraction(0)
        match time:
            case ra.Duration(): # The most internally called option
                beats_per_note: int = self._time_signature._bottom
                beats = time._rational * beats_per_note
            case ra.Beats() | ra.Length():
                beats = time._rational
            case ra.Measures():
                beats_per_measure: int = self._time_signature._top
                beats = time._rational * beats_per_measure
            case ra.Steps():
                beats_per_note: int = self._time_signature._bottom
                notes_per_step: Fraction = self._quantization
                beats_per_step: Fraction = beats_per_note * notes_per_step
                beats = time._rational * beats_per_step
            case ou.Measure():
                return self.convertToBeats(ra.Measures(time._unit))
            case ou.Beat():
                return self.convertToBeats(ra.Beats(time._unit))
            case ou.Step():
                return self.convertToBeats(ra.Steps(time._unit))
            case float() | int() | Fraction():
                return self.convertToBeats(ra.Measures(time))
        return ra.Beats(beats).set_staff_reference(self)

    def convertToMeasures(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Measures':
        measures: Fraction = Fraction(0)
        match time:
            case ra.Beats() | ra.Length():
                beats_per_measure: int = self._time_signature._top
                measures = time._rational / beats_per_measure
            case ra.Measures():
                measures = time._rational
            case _:
                return self.convertToMeasures(self.convertToBeats(time))
        return ra.Measures(measures).set_staff_reference(self)

    def convertToSteps(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Steps':
        steps: Fraction = Fraction(0)
        match time:
            case ra.Beats() | ra.Length():
                beats_per_note: int = self._time_signature._bottom
                notes_per_step: Fraction = self._quantization
                beats_per_step: Fraction = beats_per_note * notes_per_step
                steps = time._rational / beats_per_step
            case ra.Steps():
                steps = time._rational
            case _:
                return self.convertToSteps(self.convertToBeats(time))
        return ra.Steps(steps).set_staff_reference(self)

    def convertToDuration(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Duration':
        duration: Fraction = Fraction(0)
        match time:
            case ra.Beats() | ra.Length():
                beats_per_note: int = self._time_signature._bottom
                duration = time._rational / beats_per_note
            case ra.Duration():
                duration = time._rational
            case _:
                return self.convertToDuration( self.convertToBeats(time) )
        return ra.Duration(duration).set_staff_reference(self)

    def convertToMeasure(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Measure':
        if isinstance(time, ra.Length):
            time = time.roundMeasures()
        return ou.Measure( self.convertToMeasures(time)._rational ).set_staff_reference(self)

    def convertToBeat(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Beat':
        if isinstance(time, ra.Length):
            time = time.roundBeats()
        absolute_beat: int = int( self.convertToBeats( time )._rational )
        beats_per_measure: int = self._time_signature._top
        relative_beat: int = absolute_beat % beats_per_measure
        return ou.Beat(relative_beat).set_staff_reference(self)

    def convertToStep(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Step':
        if isinstance(time, ra.Length):
            time = time.roundSteps()
        absolute_step: int = int( self.convertToSteps( time )._rational )
        beats_per_measure: int = self._time_signature._top
        beats_per_note: int = self._time_signature._bottom
        notes_per_step: Fraction = self._quantization
        beats_per_step: Fraction = beats_per_note * notes_per_step
        steps_per_measure: int = int(beats_per_measure / beats_per_step)
        relative_step: int = absolute_step % steps_per_measure
        return ou.Step(relative_step).set_staff_reference(self)

    def convertToLength(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Length':
        beats: ra.Beats = ra.Beats()
        if isinstance(time, (ra.Convertible, ou.TimeUnit)):
            beats = self.convertToBeats(time)
        return ra.Length(beats).set_staff_reference(self)

    def convertToPosition(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Position':
        beats: ra.Beats = ra.Beats()
        if isinstance(time, (ra.Convertible, ou.TimeUnit)):
            beats = self.convertToBeats(time)
        return ra.Position(beats).set_staff_reference(self)

    ################################################################################################################
    # Transformation (Two-way, Context-Dependent) | Both Staffs are considered, the source and the destination one #
    ################################################################################################################

    def transformBeats(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Beats':
        match time:
            case ra.Beats() | ra.Length():
                # beats_b / tempo_b = beats_a / tempo_a => beats_b = beats_a * tempo_b / tempo_a
                beats_a : Fraction = time._rational
                tempo_a : Fraction = time._staff_reference._tempo
                tempo_b : Fraction = self._tempo
                beats_b : Fraction = beats_a * tempo_b / tempo_a
                return ra.Beats(beats_b).set_staff_reference(self)
            case _:
                return self.transformBeats(time._staff_reference.convertToBeats(time))

    def transformMeasures(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Measures':
        return self.convertToMeasures(self.transformBeats(time))

    def transformSteps(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Steps':
        return self.convertToSteps(self.transformBeats(time))

    def transformDuration(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Duration':
        return self.convertToDuration(self.transformBeats(time))

    def transformMeasure(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Measure':
        return self.convertToMeasure(self.transformBeats(time))

    def transformBeat(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Beat':
        return self.convertToBeat(self.transformBeats(time))

    def transformStep(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Step':
        return self.convertToStep(self.transformBeats(time))

    def transformLength(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Length':
        return self.convertToLength(self.transformBeats(time))

    def transformPosition(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ra.Position':
        return self.convertToPosition(self.transformBeats(time))


    def getMinutes(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> Fraction:
        return self.convertToBeats(time)._rational / self._tempo

    def getPlaylist(self, position: 'ra.Position' = None) -> list[dict]:
        import operand_element as oe
        return [{ "time_ms": oe.Element.get_time_ms(self.getMinutes(position)) }]


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tempo"]            = self.serialize( self._tempo )
        serialization["parameters"]["time_signature"]   = self.serialize( self._time_signature )
        serialization["parameters"]["quantization"]     = self.serialize( self._quantization )
        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
        serialization["parameters"]["scale"]            = self.serialize( self._scale )
        serialization["parameters"]["measures"]         = self.serialize( self._measures )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Staff':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "measures" in serialization["parameters"] and "tempo" in serialization["parameters"] and "time_signature" in serialization["parameters"] and
            "key_signature" in serialization["parameters"] and "scale" in serialization["parameters"] and "quantization" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempo             = self.deserialize( serialization["parameters"]["tempo"] )
            self._time_signature    = self.deserialize( serialization["parameters"]["time_signature"] )
            self._quantization      = self.deserialize( serialization["parameters"]["quantization"] )
            self._key_signature     = self.deserialize( serialization["parameters"]["key_signature"] )
            self._scale             = self.deserialize( serialization["parameters"]["scale"] )
            self._measures          = self.deserialize( serialization["parameters"]["measures"] )
        return self
    
    def __lshift__(self, operand: o.Operand) -> 'Staff':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Staff():
                super().__lshift__(operand)
                self._tempo             = operand._tempo
                self._time_signature    << operand._time_signature
                self._quantization      = operand._quantization
                self._key_signature     << operand._key_signature
                self._scale             << operand._scale
                self._measures          = operand._measures
            case od.DataSource():
                match operand._data:
                    case ra.Tempo():            self._tempo = operand._data._rational
                    case TimeSignature():       self._time_signature = operand._data
                    case ra.Quantization():     self._quantization = operand._data._rational
                    case ou.KeySignature():     self._key_signature = operand._data
                    case Scale():               self._scale = operand._data
                    case ra.TimeSignatureData():
                                                self._time_signature << od.DataSource( operand._data )
                    case ra.Measures():         self._measures = operand._data // int()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Tempo():            self._tempo = operand._rational
            case TimeSignature() | ra.TimeSignatureData():
                                        self._time_signature << operand
            case ra.Quantization():     self._quantization = operand._rational
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                                        self._key_signature << operand
            case Scale():               self._scale << operand
            case ra.Measures() | ou.Measure():         
                                        self._measures = operand // int()
            # Calculated Values
            case ra.StepsPerMeasure():
                self._quantization = (self % ra.NotesPerMeasure()) / (operand % Fraction())
            case ra.StepsPerNote():
                self._quantization = 1 / (operand % Fraction())
            case int() | float():
                self._tempo = ra.Tempo(operand)._rational
            case Fraction():
                self._duration = operand
            case str():
                self._tempo = ra.Tempo(self._tempo, operand)._rational
                self._key_signature << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self



class Defaults(Generic):
    def __init__(self, *parameters):
        super().__init__()
        self._staff: Staff                          = Staff()
        self._duration: Fraction                    = Fraction(1/4)
        self._octave: int                           = 4
        self._velocity: int                         = 100
        self._controller: Controller                = Controller("Pan") << ou.Value( ou.Number.getDefault("Pan") )
        self._channel: int                          = 1
        self._device: list                          = list(["Microsoft", "FLUID", "Apple"])
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: any) -> any:
        match operand:
            case od.DataSource():
                match operand._data:
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case Staff():               return self._staff
                    case ra.StaffParameters() | ou.KeySignature() | TimeSignature() \
                        | Scale() | ra.Measures() | ou.Measure() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                        | int() | float() | Fraction() | str():
                                                return self._staff // operand._data
                    case ra.Duration():         return operand << self._duration
                    case ou.Octave():           return ou.Octave(self._octave)
                    case ou.Velocity():         return ou.Velocity(self._velocity)
                    case Controller():          return self._controller
                    case ou.Channel():          return ou.Channel(self._channel)
                    case od.Device():           return od.Device(self._device)
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % (operand._data)
            case Staff():               return self._staff.copy()
            case ra.StaffParameters() | ou.KeySignature() | TimeSignature() \
                | Scale() | ra.Measures() | ou.Measure() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | int() | float() | Fraction() | str():
                                        return self._staff % operand
            case ra.Duration():         return operand.copy() << self._duration
            case ou.Octave():           return ou.Octave(self._octave)
            case ou.Velocity():         return ou.Velocity(self._velocity)
            case Controller():          return self._controller.copy()
            case ou.Number():           return self._controller % ou.Number()
            case ou.Value():            return self._controller % ou.Value()
            case ou.Channel():          return ou.Channel(self._channel)
            case od.Device():           return od.Device(self._device)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Defaults') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._staff             == other._staff \
            and self._duration          == other._duration \
            and self._octave            == other._octave \
            and self._velocity          == other._velocity \
            and self._controller        == other._controller \
            and self._channel           == other._channel \
            and self._device            == other._device
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["staff"]            = self.serialize( self._staff )
        serialization["parameters"]["duration"]         = self.serialize( self._duration )
        serialization["parameters"]["octave"]           = self.serialize( self._octave )
        serialization["parameters"]["velocity"]         = self.serialize( self._velocity )
        serialization["parameters"]["controller"]       = self.serialize( self._controller )
        serialization["parameters"]["channel"]          = self.serialize( self._channel )
        serialization["parameters"]["device"]           = self.serialize( self._device )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Defaults':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"] and "duration" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "velocity" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "device" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._staff             = self.deserialize( serialization["parameters"]["staff"] )
            self._duration          = self.deserialize( serialization["parameters"]["duration"] )
            self._octave            = self.deserialize( serialization["parameters"]["octave"] )
            self._velocity          = self.deserialize( serialization["parameters"]["velocity"] )
            self._controller        = self.deserialize( serialization["parameters"]["controller"] )
            self._channel           = self.deserialize( serialization["parameters"]["channel"] )
            self._device            = self.deserialize( serialization["parameters"]["device"] )
        return self
    
    def __lshift__(self, operand: o.Operand) -> 'Defaults':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Defaults():
                super().__lshift__(operand)
                self._staff             << operand._staff
                self._duration          = operand._duration
                self._octave            = operand._octave
                self._velocity          = operand._velocity
                self._controller        << operand._controller
                self._channel           = operand._channel
                self._device            = operand._device.copy()
            case od.DataSource():
                match operand._data:
                    case Staff():               self._staff = operand._data
                    case ra.Duration():         self._duration = operand._data._rational
                    case ou.Octave():           self._octave = operand._data._unit
                    case ou.Velocity():         self._velocity = operand._data._unit
                    case Controller():          self._controller = operand._data
                    case ou.Channel():          self._channel = operand._data._unit
                    case od.Device():           self._device = operand._data._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.StaffParameters() | ou.KeySignature() | TimeSignature() \
                | Scale() | ra.Measures() | ou.Measure() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | int() | float() | Fraction() | str():
                                        self._staff << operand
            case ra.Duration():         self._duration = operand._rational
            case ou.Octave():           self._octave = operand._unit
            case ou.Velocity():         self._velocity = operand._unit
            case Controller() | ou.Number() | ou.Value():
                                        self._controller << operand
            case ou.Channel():          self._channel = operand._unit
            case od.Device():           self._device = operand._data.copy()
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


# Instantiate the Global Defaults here.
defaults: Defaults = Defaults()


