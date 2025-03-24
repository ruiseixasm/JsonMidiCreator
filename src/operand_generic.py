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


class Generic(o.Operand):
    pass


class TimeSignature(Generic):
    def __init__(self, top: int = 4, bottom: int = 4):
        self._top: int      = 4 if top is None else int(max(1,  top  ))
        # This formula is just to make sure it's a power of 2, it doesn't change the input value if it is already a power of 2
        self._bottom: int   = 4 if \
            not (isinstance(bottom, int) and bottom > 0) else int(math.pow(2, int(max(0, math.log2(  bottom  )))))
        super().__init__()

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.DataSource():
                match operand._data:
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case TimeSignature():       return self
                    case ra.BeatsPerMeasure():  return ra.BeatsPerMeasure() << self._top
                    case ra.BeatNoteValue():    return ra.BeatNoteValue() << 1 / self._bottom
                    # Calculated Values
                    case ra.NotesPerMeasure():  return ra.NotesPerMeasure() << self._top / self._bottom
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
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
        if isinstance(other_signature, od.Conditional):
            return other_signature == self
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
        
    def __lshift__(self, operand: any) -> Self:
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
        self._tonic_key: int                    = self._staff_reference % ou.Key() % int()
        self._octave: int                       = 4     # By default it's the 4th Octave!
        self._degree: int                       = 1     # By default it's Degree 1
        self._sharp: int                        = 0     # By default not a Sharp or Flat
        self._natural: bool                     = False
        super().__init__(*parameters)


    def set_staff_reference(self, staff_reference: 'Staff' = None) -> Self:
        if isinstance(staff_reference, Staff):
            self._staff_reference = staff_reference
        return self

    def get_staff_reference(self) -> 'Staff':
        return self._staff_reference

    def reset_staff_reference(self) -> Self:
        self._staff_reference = defaults._staff
        return self

    def get_accidental(self) -> bool | int:
        # parameter decorators like Sharp and Natural
        if self._natural:
            return True         # returns as bool
        if self._sharp != 0:
            return self._sharp  # returns as int
        return False


    def sharp(self, unit: bool = True) -> Self:
        return self << ou.Sharp(unit)

    def flat(self, unit: bool = True) -> Self:
        return self << ou.Flat(unit)

    def natural(self, unit: bool = True) -> Self:
        return self << ou.Natural(unit)

    def degree(self, unit: int = 1) -> Self:
        return self << ou.Degree(unit)


    def get_key_degree(self, key_int: int) -> int:
        tonic_key: int = self._tonic_key % 12
        staff_scale: list[int] = self._staff_reference % list()
        total_keys: int = sum(1 for key in staff_scale if key != 0)

        degree_0: int = 0
        
        # tonic_key goes UP and then DOWN (results in flat or natural)
        while tonic_key < key_int:
            if staff_scale[ (key_int - tonic_key) % 12 ] == 1:  # Scale key
                degree_0 += 1
            tonic_key += 1
        while tonic_key > key_int:
            if staff_scale[ (key_int - tonic_key) % 12 ] == 1:  # Scale key
                degree_0 -= 1
            tonic_key -= 1

        if staff_scale[ (key_int - self._tonic_key % 12) % 12 ] == 0:  # Key NOT on the scale
            if self._tonic_key // 12 == 1:  # Checks the tonic key line
                if self._tonic_key % 12 > key_int:
                    degree_0 -= 1
            else:
                if self._tonic_key % 12 < key_int:
                    degree_0 += 1

        # Sets the Degree as Positive
        degree_0 %= total_keys

        return degree_0 + 1 # Degree base 1 (I)

    def get_key_int(self) -> int:

        staff_scale: list[int] = self._staff_reference % list()
        total_keys: int = sum(1 for key in staff_scale if key != 0)

        degree_0: int = self._degree - 1    # From base 1 to base 0
        degree_0 %= total_keys

        degree_transposition: int = 0
        while degree_0 > 0:
            degree_transposition += 1
            if staff_scale[ degree_transposition % 12 ] == 1:  # Scale key
                degree_0 -= 1

        key_int: int = self._tonic_key % 12 + degree_transposition

        return key_int

    def get_key_float(self, measure: int = 0) -> float:
        key_int: int = self.get_key_int()

        # Final parameter decorators like Sharp and Natural
        if self._natural:
            self._staff_reference.add_accidental(measure, key_int, True)
            if self._major_scale[key_int % 12] == 0:  # Black key
                accidentals_int: int = self._staff_reference._key_signature._unit
                if accidentals_int < 0:
                    key_int += 1
                else:
                    key_int -= 1
        elif self._sharp != 0:
            self._staff_reference.add_accidental(measure, key_int, self._sharp)
            if self._major_scale[key_int % 12] == 1:  # White key
                key_int += self._sharp  # applies Pitch self accidentals
        # Check staff accidentals
        else:
            staff_accidentals = self._staff_reference.get_accidental(measure, key_int)
            if staff_accidentals:    # Staff only set Sharps and Flats
                if self._major_scale[key_int % 12] == 1:  # White key
                    key_int += staff_accidentals    # applies Pitch self accidentals
        return float(key_int)


    def octave_key_offset(self, key_offset: int) -> tuple[int, int]:
        
        octave_tonic_key: int = self._tonic_key % 12
        moved_key: int = octave_tonic_key + key_offset
        octave_key: int = moved_key % 12
        octave_offset: int = moved_key // 12
        key_offset = octave_key - octave_tonic_key

        return octave_offset, key_offset
    
    def apply_key_offset(self, key_offset: int) -> Self:
        
        octave_offset_int, key_offset_int = self.octave_key_offset(key_offset)
        self._octave += octave_offset_int
        self._tonic_key += key_offset_int

        return self
    
    def set_chromatic_pitch(self, pitch: int | float) -> Self:
        
        # Reset purely decorative parameters
        self._natural = False
        self._sharp = 0

        # Excludes the effect of purely decorative parameters
        key_offset: int = int( pitch - self % float() )
        return self.apply_key_offset(key_offset)


    def octave_degree_offset(self, degree_offset: int) -> tuple[int, int]:
        
        self_degree_0: int = 0
        if self._degree > 0:
            self_degree_0 = self._degree - 1
        elif self._degree < 0:
            self_degree_0 = self._degree + 1

        staff_scale: list[int] = self._staff_reference % list()
        total_degrees: int = sum(1 for key in staff_scale if key != 0)

        self_octave_degree_0: int = self_degree_0 % total_degrees
        moved_degree_0: int = self_octave_degree_0 + degree_offset
        octave_degree_0: int = moved_degree_0 % total_degrees
        octave_offset: int = moved_degree_0 // total_degrees
        degree_offset = octave_degree_0 - self_octave_degree_0

        return octave_offset, degree_offset
    
    def apply_degree_offset(self, degree_offset: int) -> Self:
        
        octave_offset_int, degree_offset_int = self.octave_degree_offset(degree_offset)
        self._octave += octave_offset_int
        self._degree += degree_offset_int

        return self
    
    def set_degree(self, degree: int) -> Self:

        self_degree_0: int = 0
        if self._degree > 0:
            self_degree_0 = self._degree - 1
        elif self._degree < 0:
            self_degree_0 = self._degree + 1

        degree_0: int = 0
        if degree > 0:
            degree_0 = degree - 1
        elif degree < 0:
            degree_0 = degree + 1

        return self.apply_degree_offset( degree_0 - self_degree_0 )


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
            case self.__class__():
                return self.copy()
            case od.DataSource():
                match operand._data:
                    case of.Frame():        return self % od.DataSource( operand._data )
                    case ou.Octave():       return operand._data << od.DataSource(self._octave)
                    case ou.Tonic():        return operand._data << od.DataSource(self._tonic_key)    # Must come before than Key()
                    case ou.Sharp():        return operand._data << od.DataSource(max(0, self._sharp))
                    case ou.Flat():         return operand._data << od.DataSource(max(0, self._sharp * -1))
                    case ou.Natural():      return operand._data << od.DataSource(self._natural)
                    case ou.Degree():       return operand._data << od.DataSource(self._degree)
                    case int():             return self._degree
                    case float():           return float(self._tonic_key)
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % operand

            case int():
                self_degree_0: int = 0
                if self._degree > 0:
                    self_degree_0 = self._degree - 1
                elif self._degree < 0:
                    self_degree_0 = self._degree + 1
                staff_scale: list[int] = self._staff_reference % list()
                total_degrees: int = sum(1 for key in staff_scale if key != 0)

                return self_degree_0 % total_degrees + 1
             
            case float() | Fraction():
                return float( 12 * (self._octave + 1) + self.get_key_float( int(operand) ) )
            
            case ou.Semitone():
                return ou.Semitone(self % float())
            
            case ou.Tonic():    # Must come before than Key()
                return ou.Tonic(self._tonic_key)
            case ou.Octave():
                final_pitch: int = int(self % float())
                return ou.Octave( final_pitch // 12 - 1 )
            
            case ou.Degree():
                return ou.Degree(self % int())
             
            case ou.Sharp():
                final_pitch: int = int(self % float())
                if self._major_scale[final_pitch % 12] == 0:    # Black key
                    if self._staff_reference._key_signature._unit >= 0:
                        return ou.Sharp(1)
                return ou.Sharp(0)
            case ou.Flat():
                final_pitch: int = int(self % float())
                if self._major_scale[final_pitch % 12] == 0:    # Black key
                    if self._staff_reference._key_signature._unit < 0:
                        return ou.Flat(1)
                return ou.Flat(0)
            case ou.Natural():
                return ou.Natural() << od.DataSource(self._natural)
            
            case ou.KeySignature():
                return self._staff_reference._key_signature.copy()
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                return self._staff_reference._key_signature % operand
            case ou.Key():
                self_pitch: int = int( self % float() )
                key_note: int = self_pitch % 12
                key_line: int = self._tonic_key // 12
                if not self._staff_reference._scale.hasScale() \
                    and self._staff_reference._key_signature.is_enharmonic(self._tonic_key, key_note):
                    key_line += 2    # All Sharps/Flats
                return ou.Key( float(key_note + key_line * 12) )
            
            case str():
                return self % ou.Key() % str()
            
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        match other:
            case Pitch():
                return self % float(-1.0) == other % float(-1.0)
            case ou.Octave():
                return self % od.DataSource( ou.Octave() ) == other
            case int() | float() | str() | ou.Key():
                return self % other == other
            case od.Conditional():
                return other == self
            case _:
                return super().__eq__(other)
        return False
    
    def __lt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Pitch():
                return self % float(-1.0) < other % float(-1.0)
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
                return self % float(-1.0) > other % float(-1.0)
            case ou.Octave():
                return self % od.DataSource( ou.Octave() ) > other
            case int() | float():
                return self % other > other
            case _:
                return super().__gt__(other)
        return False
    
    def getSerialization(self) -> dict:

        serialization = super().getSerialization()
        serialization["parameters"]["tonic_key"]        = self.serialize( self._tonic_key )
        serialization["parameters"]["octave"]           = self.serialize( self._octave )
        serialization["parameters"]["degree"]           = self.serialize( self._degree )
        serialization["parameters"]["sharp"]            = self.serialize( self._sharp )
        serialization["parameters"]["natural"]          = self.serialize( self._natural )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tonic_key" in serialization["parameters"] and "sharp" in serialization["parameters"] and "natural" in serialization["parameters"] and
            "degree" in serialization["parameters"] and "octave" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tonic_key     = self.deserialize( serialization["parameters"]["tonic_key"] )
            self._octave        = self.deserialize( serialization["parameters"]["octave"] )
            self._degree        = self.deserialize( serialization["parameters"]["degree"] )
            self._sharp         = self.deserialize( serialization["parameters"]["sharp"] )
            self._natural       = self.deserialize( serialization["parameters"]["natural"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                super().__lshift__(operand)
                self._tonic_key             = operand._tonic_key
                self._octave                = operand._octave
                self._degree                = operand._degree
                self._sharp                 = operand._sharp
                self._natural               = operand._natural
                self._staff_reference       = operand._staff_reference
            case od.DataSource():
                match operand._data:
                    case ou.Tonic():    # Must come before than Key()
                        self._tonic_key = operand._data._unit
                    case ou.Octave():
                        self._octave    = operand._data._unit
                    case int():
                        self._unit = operand._data
                    case float() | Fraction():
                        self._unit = int(operand._data)
                    case ou.Semitone():
                        self._unit = operand._data._unit
                    case ou.Sharp():
                        self._sharp = operand._data._unit
                    case ou.Flat():
                        self._sharp = operand._data._unit * -1
                    case ou.Natural():
                        self._natural = operand._data // bool()
                    case ou.Degree():
                        self._degree = operand._data._unit
                    case str():
                        self._sharp     = \
                            ((operand._data).strip().lower().find("#") != -1) * 1 + \
                            ((operand._data).strip().lower().find("b") != -1) * -1
                        self._degree    = (self // ou.Degree() << ou.Degree(operand._data))._unit
                        self._tonic_key       = ou.Key(self._tonic_key, operand._data)._unit
                    case _:
                        super().__lshift__(operand)


            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Tonic():    # Must come before than Key()
                self._tonic_key = operand._unit % 24
            case ou.Octave():
                octave_offset: ou.Octave = operand - self % ou.Octave()
                self._octave += octave_offset._unit
            case ou.Key():
                self._sharp = 0
                self._natural = False
                self._degree = self.get_key_degree(operand._unit % 12)
            case None:
                self << 0   # Resets the Tonic key
                self << 1   # Resets the degree to I
                self._octave = 4
                self._sharp = 0
                self._natural = False
            case int():
                if operand == 0:
                    self._tonic_key = int( self._staff_reference % float() )
                else:
                    staff_scale: list[int] = self._staff_reference % list()
                    total_degrees: int = sum(1 for key in staff_scale if key != 0)
                    self._degree = (operand - 1) % total_degrees + 1

                    # self.set_degree(operand)

            case ou.Degree():
                self << operand._unit

            case float() | Fraction():
                self.set_chromatic_pitch(int(operand))
            case ou.Semitone():
                self.set_chromatic_pitch(operand._unit)
            case ou.Tone():
                self._tonic_key = operand._unit % 12
                self._octave = operand._unit // 12 - 1

            case ou.DrumKit():
                self._natural = False
                self._sharp = 0
                self << ou.Degree()         # Makes sure no Degree different of Tonic is in use
                self << operand // float()  # Sets the key number regardless KeySignature or Scale!
            case ou.Sharp():
                if max(0, self._sharp) != operand._unit:
                    self._sharp = operand._unit % 3
            case ou.Flat():
                if max(0, self._sharp * -1) != operand._unit:
                    self._sharp = operand._unit % 3 * -1
            case ou.Natural():
                self._natural = operand // bool()
            case str():
                string: str = operand.strip()
                self._sharp = \
                    (ou.Sharp(max(0, self._sharp)) << string)._unit + \
                    (ou.Flat(max(0, self._sharp * -1)) << string)._unit
                self._degree    = (self % ou.Degree() << operand)._unit
                self._tonic_key = (self % ou.Key() << string)._unit
            case tuple():
                for single_operand in operand:
                    self << single_operand

            case _:
                super().__lshift__(operand)

        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                self += operand % float(-1.0)
            case ou.Octave():
                self._octave += operand._unit
            case int():
                self.apply_degree_offset(operand)
            case ou.Degree():
                self.apply_degree_offset(operand._unit)
            case ou.Tone():
                new_pitch: float = self % float(-1.0) + self.move_semitones(operand % int())
                self.set_chromatic_pitch(new_pitch)
            case ou.Tonic():
                self._tonic_key += operand._unit
            case float() | Fraction():
                new_pitch: float = self % float(-1.0) + float(operand)
                self.set_chromatic_pitch(new_pitch)
            case ra.Rational() | ou.Key() | ou.Semitone():
                new_pitch: float = self % float(-1.0) + operand % float(-1.0)
                self.set_chromatic_pitch(new_pitch)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                self -= operand % float(-1.0)
            case ou.Octave():
                self._octave -= operand._unit
            case int():
                self.apply_degree_offset(-operand)
            case ou.Degree():
                self.apply_degree_offset(-operand._unit)
            case ou.Tone():
                new_pitch: float = self % float(-1.0) - self.move_semitones(operand % int())
                self.set_chromatic_pitch(new_pitch)
            case ou.Tonic():
                self._tonic_key -= operand._unit
            case float() | Fraction():
                new_pitch: float = self % float(-1.0) - float(operand)
                self.set_chromatic_pitch(new_pitch)
            case ra.Rational() | ou.Key() | ou.Semitone():
                new_pitch: float = self % float(-1.0) - operand % float(-1.0)
                self.set_chromatic_pitch(new_pitch)
        return self

    def __mul__(self, operand) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                new_keynote = self.__class__()
                self_int = self % int()
                multiplied_int = self_int * operand
                new_keynote._tonic_key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case float():
                new_keynote = self.__class__()
                self_float = self % float(-1.0)
                multiplied_int = int(self_float * operand)
                new_keynote._tonic_key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case _:
                return super().__mul__(operand)
    
    def __div__(self, operand) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                new_keynote = self.__class__()
                self_int = self % int()
                multiplied_int = int(self_int / operand)
                new_keynote._tonic_key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case float():
                new_keynote = self.__class__()
                self_float = self % float(-1.0)
                multiplied_int = int(self_float / operand)
                new_keynote._tonic_key = multiplied_int % 12
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
    
    _major_scale = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)    # Major scale for the default staff

    _white_keys: dict = {
            "c": 0,
            "d": 2,
            "e": 4,
            "f": 5,
            "g": 7,
            "a": 9,
            "b": 11
         }

    def snap(self, up: bool = False) -> Self:
        scale_list: list[int] = self._staff_reference % list()
        self_pitch: float = self % float(-1.0)
        pitch_offset: float = 0.0
        if up:
            pitch_step: float = 1.0
        else:
            pitch_step: float = -1.0
        while scale_list[int(self_pitch + pitch_offset)] == 0:
            pitch_offset += pitch_step
        if pitch_offset > 0.0:
            self += pitch_offset
        return self

class Controller(Generic):
    def __init__(self, *parameters):
        self._number: int       = ou.Number("Pan")._unit
        self._value: int        = ou.Number.getDefault(self._number)
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
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
            case self.__class__():
                return self.copy()
            case od.DataSource():
                match operand._data:
                    case ou.Number():           return operand._data << od.DataSource(self._number)
                    case ou.Value():            return operand._data << od.DataSource(self._value)
                    case Controller():          return self
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case _:                     return super().__mod__(operand)
            case ou.Number():           return operand.copy() << od.DataSource(self._number)
            case ou.Value():            return operand.copy() << od.DataSource(self._value)
            case int():                 return self._value
            case float():               return float(self._value)
            case Controller():          return self.copy()
            case of.Frame():            return self % operand
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Controller') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if self._number == other._number and self % ou.Value() == other % ou.Value():
            return True
        if isinstance(other, od.Conditional):
            return other == self
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
        
    def __lshift__(self, operand: any) -> Self:
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

    def __mod__(self, operand: o.T) -> o.T:
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
            case self.__class__():
                return self.copy()
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
            case ou.Tonic():            return ou.Tonic(self % float())
            case ou.Key():              return ou.Key( self.get_tonic_number() )
            case float():               return float( self.get_tonic_number() )
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Scale') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        if isinstance(other, od.Conditional):
            return other == self
        return  self._scale_list == other._scale_list
    
    def hasScale(self) -> bool:
        if self._scale_list == [] or self._scale_list == -1 or self._scale_list == "":
            return False
        return True

    def keys(self) -> int:
        return sum(1 for key in self._scale_list if key != 0)

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

    def __lshift__(self, operand: any) -> Self:
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
                if len(operand) == 12 and all(x in {0, 1} for x in operand) and any(x == 1 for x in operand):
                    self._scale_list = operand.copy()
                elif operand == []:
                    self._scale_list = []
            case None:
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
        # Volatile variable not intended to be user defined
        self._accidentals: dict[int, dict[int, int]] = { 0: {} }
        self._tied_notes: dict[int, dict[str, any]] = {}
        self._stacked_notes: dict[float,    # note on time
                                  dict[int,     # status byte
                                       dict[int,    # pitch
                                            set[tuple[str]]]]    # set of devices tuple
                            ] = {}

    def reset_accidentals(self) -> Self:
        self._accidentals = { 0: {} }
        return self

    def add_accidental(self, measure: int, pitch: int, accidental: bool | int) -> Self:
        if measure >= 0 and self is not defaults._staff: # defaults's staff remains clean
            if measure not in self._accidentals:
                # It's a new measure, includes cleaning every Measure before
                self._accidentals = {
                    measure: {}
                }
            if accidental is True:
                self._accidentals[measure].pop(pitch, None)
            elif accidental is not False:
                self._accidentals[measure][pitch] = accidental
        return self

    def get_accidental(self, measure: int, pitch: int) -> bool | int:
        if measure in self._accidentals and pitch in self._accidentals[measure]:
            return self._accidentals[measure][pitch]
        return False

    def reset_tied_note(self) -> Self:
        self._tied_notes = {}
        return self

    def add_tied_note(self, pitch: int, position: Fraction, length: Fraction, note_list: list) -> Self:
        if self is not defaults._staff: # defaults's staff remains clean
            tied_note = {
                "position":     position,
                "length":       length,
                "note_list":    note_list
            }
            self._tied_notes[pitch] = tied_note
        return self

    def set_tied_note_length(self, pitch: int, length: Fraction) -> Self:
        if pitch in self._tied_notes:
            self._tied_notes[pitch]["length"] = length
        return self
    
    def get_tied_note(self, pitch: int):
        if pitch in self._tied_notes:
            return self._tied_notes[pitch]
        return None

    def stack_note(self, note_on: float, channel_byte: int, pitch: int, device: list[str] = []) -> bool:
        if self is not defaults._staff: # defaults's staff remains clean
            device_tuple: tuple[str] = tuple(device)
            if note_on not in self._stacked_notes:
                self._stacked_notes[note_on] = {}
            if channel_byte not in self._stacked_notes[note_on]:
                self._stacked_notes[note_on][channel_byte] = {}
            if pitch not in self._stacked_notes[note_on][channel_byte]:
                self._stacked_notes[note_on][channel_byte][pitch] = set()
            if device_tuple not in self._stacked_notes[note_on][channel_byte][pitch]:
                self._stacked_notes[note_on][channel_byte][pitch].add(device_tuple)
            else:   # It's an Overlapping note
                return False
        return True

    def reset_stacked_notes(self) -> Self:
        self._stacked_notes = {}
        return self


    def __mod__(self, operand: o.T) -> o.T:
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
            case self.__class__():
                return self.copy()
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
            case of.Frame():            return self % operand
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
            case ou.Tonic():
                return ou.Tonic(self % float())
            case ou.Key():
                if self._scale.hasScale():
                    return self._scale % ou.Key()
                return self._key_signature % ou.Key()
            case list():
                if self._scale.hasScale():
                    return self._scale % list()
                return self._key_signature.get_scale_list() # Faster this way
            case float():
                if self._scale.hasScale():
                    return self._scale % float()
                return self._key_signature % float()
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
        if isinstance(other, od.Conditional):
            return other == self
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
            case ra.Beats() | ra.Measurement():
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
            case ra.Beats() | ra.Measurement():
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
            case ra.Beats() | ra.Measurement():
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
            case ra.Beats() | ra.Measurement():
                beats_per_note: int = self._time_signature._bottom
                duration = time._rational / beats_per_note
            case ra.Duration():
                duration = time._rational
            case _:
                return self.convertToDuration( self.convertToBeats(time) )
        return ra.Duration(duration).set_staff_reference(self)

    def convertToMeasure(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Measure':
        if isinstance(time, ra.Measurement):
            time = time.roundMeasures()
        return ou.Measure( self.convertToMeasures(time)._rational ).set_staff_reference(self)

    def convertToBeat(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Beat':
        if isinstance(time, ra.Measurement):
            time = time.roundBeats()
        absolute_beat: int = int( self.convertToBeats( time )._rational )
        beats_per_measure: int = self._time_signature._top
        relative_beat: int = absolute_beat % beats_per_measure
        return ou.Beat(relative_beat).set_staff_reference(self)

    def convertToStep(self, time: Union['ra.Convertible', 'ou.TimeUnit']) -> 'ou.Step':
        if isinstance(time, ra.Measurement):
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
            case ra.Beats() | ra.Measurement():
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
    
    def __lshift__(self, operand: any) -> Self:
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
                    case ra.TimeSignatureParameter():
                                                self._time_signature << od.DataSource( operand._data )
                    case ra.Measures():         self._measures = operand._data // int()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Tempo():            self._tempo = operand._rational
            case TimeSignature() | ra.TimeSignatureParameter():
                                        self._time_signature << operand
            case ra.Quantization():     self._quantization = operand._rational
            case Scale():               self._scale << operand
            case ra.Measures() | ou.Measure():         
                                        self._measures = operand // int()
            # Calculated Values
            case ra.StepsPerMeasure():
                self._quantization = self % ra.NotesPerMeasure() / operand % Fraction()
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
            case _:
                self._key_signature << operand
        return self


class Arpeggio(Generic):
    def __init__(self, *parameters):
        self._order: int = 1    # "Up" by default
        self._duration_notevalue: Fraction = ra.Duration(1/16)._rational
        self._swing: Fraction = ra.Swing(0.5)._rational
        self._chaos: ch.Chaos = ch.SinX()
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.DataSource():
                match operand._data:
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case ou.Order():            return operand._data << od.DataSource( self._order )
                    case ra.Duration():         return operand._data << od.DataSource( self._duration_notevalue )
                    case ra.Swing():            return operand._data << od.DataSource( self._swing )
                    case ch.Chaos():            return self._chaos
                    case int():                 return self._order
                    case float():               return float( self._duration_notevalue )
                    case Fraction():            return self._duration_notevalue
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case ou.Order():            return ou.Order(self._order)
            case str():                 return ou.Order(self._order) % str()
            case ra.Duration():         return ra.Duration( self._duration_notevalue )
            case ra.Swing():            return ra.Swing(self._swing)
            case ch.Chaos():            return self._chaos.copy()
            case int():                 return self._order
            case float():               return float( self._duration_notevalue )
            case Fraction():            return self._duration_notevalue
            case _:                     return super().__mod__(operand)


    def _shuffle_list(self, list: list) -> list:
        
        source_picks = [*range(len(list))]
        target_picks = []

        while len(source_picks) > 0:
            target_picks.append(source_picks.pop(self._chaos * 1 % int() % len(source_picks)))

        shuffled_list = []
        for pick in target_picks:
            shuffled_list.append(list[pick])

        return shuffled_list

    from operand_element import Element

    def _generate_sequence(self, elements: list[Element]) -> list[Element]:
        """Generates the sequence of the arpeggio order."""
        match ou.Order.numberToName( self._order ):
            case "Up":
                return elements
            case "Down":
                return elements[::-1]
            case "UpDown":
                return elements + elements[-2:0:-1]  # Ascend then descend
            case "DownUp":
                return elements[::-1] + elements[1:-1]  # Descend then ascend
            case "Chaotic":
                return self._shuffle_list(elements)
            case _:
                return elements  # Default to "Up"

    def arpeggiate(self, elements: list[Element]) -> list[Element]:
        from operand_element import Element

        if self._order > 0 and len(elements) > 0:

            staff_reference: Staff = elements[0]._staff_reference
            element_start_position: ra.Position = elements[0] // ra.Position()
            arpeggio_length: ra.Length = elements[0] // ra.Length()
            arpeggio_end_position: ra.Position = arpeggio_length.convertToPosition()
            element_length: ra.Length = staff_reference.convertToLength(ra.Duration(self._duration_notevalue))
            odd_length: ra.Length = element_length * 2 * self._swing
            even_length: ra.Length = element_length * 2 - odd_length
            
            sequenced_elements: list[Element] = self._generate_sequence(elements)
            arpeggiated_elements: list[Element] = []
            nth_element: int = 1
            while element_start_position < arpeggio_end_position:
                for source_element in sequenced_elements:
                    new_element: Element = source_element.copy()
                    arpeggiated_elements.append(new_element)
                    new_element << element_start_position
                    if nth_element % 2 == 1:   # Odd element
                        new_element << odd_length
                    else:
                        new_element << even_length
                    element_end_position: ra.Position = element_start_position + new_element // ra.Length()
                    if element_end_position > arpeggio_end_position:
                        length_deficit: ra.Length = arpeggio_length - arpeggio_end_position
                        new_element += length_deficit
                        break
                    element_start_position = element_end_position
                    nth_element += 1
            return arpeggiated_elements

        return elements

    def arpeggiate_source(self, elements: list[Element], start_position: ra.Position, arpeggio_length: ra.Length) -> list[Element]:
        from operand_element import Element

        if self._order > 0 and len(elements) > 0:

            element_start_position: ra.Position = start_position
            total_elements: int = len(elements)
            element_length: ra.Length = arpeggio_length / total_elements
            odd_length: ra.Length = element_length * 2 * self._swing
            even_length: ra.Length = element_length * 2 - odd_length
            
            sequenced_elements: list[Element] = self._generate_sequence(elements)
            nth_element: int = 1
            for element_i in range(total_elements):
                elements[element_i] = sequenced_elements[element_i]
                elements[element_i] << element_start_position
                if nth_element % 2 == 1:   # Odd element
                    elements[element_i] << odd_length
                else:
                    elements[element_i] << even_length
                element_start_position += elements[element_i] // ra.Length()
                nth_element += 1

        return elements

    def __eq__(self, other: 'Arpeggio') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        if isinstance(other, Arpeggio):
            return  self._order                 == other._order \
                and self._duration_notevalue    == other._duration_notevalue \
                and self._chaos                 == other._chaos
        if isinstance(other, od.Conditional):
            return other == self
        return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["order"]            = self.serialize( self._order )
        serialization["parameters"]["duration"]         = self.serialize( self._duration_notevalue )
        serialization["parameters"]["swing"]            = self.serialize( self._swing )
        serialization["parameters"]["chaos"]            = self.serialize( self._chaos )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "order" in serialization["parameters"] and "duration" in serialization["parameters"] and
            "swing" in serialization["parameters"] and "chaos" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._order                 = self.deserialize( serialization["parameters"]["order"] )
            self._duration_notevalue    = self.deserialize( serialization["parameters"]["duration"] )
            self._swing                 = self.deserialize( serialization["parameters"]["swing"] )
            self._chaos                 = self.deserialize( serialization["parameters"]["chaos"] )
        return self
    
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Arpeggio():
                super().__lshift__(operand)
                self._order                 = operand._order
                self._duration_notevalue    = operand._duration_notevalue
                self._swing                 = operand._swing
                self._chaos                 << operand._chaos
            case od.DataSource():
                match operand._data:
                    case ou.Order():                self._order = operand._data._unit
                    case ra.Duration():             self._duration_notevalue = operand._data._rational
                    case ra.Swing():                self._swing = operand._data._rational
                    case ch.Chaos():                self._chaos = operand._data
                    case int():                     self._order = operand._data
                    case float():                   self._duration_notevalue = ra.Duration(operand._data)._rational
                    case Fraction():                self._duration_notevalue = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Order():                self._order = operand._unit
            case str():                     self._order = ou.Order(operand)._unit
            case ra.Duration():             self._duration_notevalue = operand._rational
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ch.Chaos():                self._chaos << operand
            case int():                     self._order = operand
            case float():                   self._duration_notevalue = ra.Duration(operand)._rational
            case Fraction():                self._duration_notevalue = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __imul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> Self:
        self._initiated = True
        self._chaos * number
        self._index += self.convert_to_int(number)    # keeps track of each iteration
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

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case self.__class__():
                return self.copy()
            case od.DataSource():
                match operand._data:
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case Staff():               return self._staff
                    case ra.StaffParameter() | ou.KeySignature() | TimeSignature() \
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
            case of.Frame():            return self % operand
            case Staff():               return self._staff.copy()
            case ra.StaffParameter() | ou.KeySignature() | TimeSignature() \
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
        if isinstance(other, od.Conditional):
            return other == self
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

    def loadSerialization(self, serialization: dict) -> Self:
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
    
    def __lshift__(self, operand: any) -> Self:
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
            case ra.StaffParameter() | ou.KeySignature() | TimeSignature() \
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


