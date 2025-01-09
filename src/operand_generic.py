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

import operand_staff as os
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
        self._key_signature: ou.KeySignature    = os.staff._key_signature.copy()
        self._key: int                          = int( self._key_signature % float() )
        self._octave: int                       = 4     # By default it's the 4th Octave!
        self._degree: int                       = 1     # By default it's Degree 1
        self._sharp: bool                       = False
        self._flat: bool                        = False
        self._natural: bool                     = False
        self._scale: Scale                      = Scale([])
        super().__init__(*parameters)

    def key_signature(self, sharps_flats: int = 0, major: bool = True) -> 'Pitch':
        return self << ou.KeySignature(sharps_flats, ou.Major(major))

    def sharp(self, unit: bool = True) -> 'Pitch':
        return self << ou.Sharp(unit)

    def flat(self, unit: bool = True) -> 'Pitch':
        return self << ou.Flat(unit)

    def natural(self, unit: bool = True) -> 'Pitch':
        return self << ou.Natural(unit)

    def degree(self, unit: int = 1) -> 'Pitch':
        return self << ou.Degree(unit)

    def scale(self, scale: list[int] | str = []) -> 'Pitch':
        return self << Scale(scale)


    # IGNORES THE KEY SIGNATURE (CHROMATIC)
    def get_key_int(self) -> int:
        staff_white_keys        = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major scale
        accidentals_int: int    = self._key_signature._unit
        sharp: ou.Sharp         = ou.Sharp(False)
        flat: ou.Flat           = ou.Flat(False)
        key_int: int            = self._key % 12
        degree_transpose: int   = 0
        if self._degree > 0:
            degree_transpose    = self._degree - 1
        if self._degree < 0:
            degree_transpose    = self._degree + 1

        # strips existent accidentals
        if staff_white_keys[key_int] == 0: # Black key
            if self._key % 24 < 12:   # sharps
                sharp << True
                key_int -= 1
            else:                               # flats
                flat << True
                key_int += 1

        key_scale = staff_white_keys  # Major scale
        if self._scale.hasScale():
            key_scale = self._scale % list()  # Already modulated

        semitone_transpose: int = 0
        while degree_transpose > 0:
            semitone_transpose += 1
            if key_scale[(key_int + semitone_transpose) % 12]:          # Scale key
                degree_transpose -= 1
        while degree_transpose < 0:
            semitone_transpose -= 1
            if key_scale[(key_int + semitone_transpose) % 12]:          # Scale key
                degree_transpose += 1

        key_int += semitone_transpose

        if staff_white_keys[(key_int + semitone_transpose) % 12] == 0:  # Black key
            if self._natural:
                if accidentals_int < 0:
                    key_int += 1
                else:
                    key_int -= 1
        elif not self._natural:
            key_int += (1 if self._sharp or sharp else 0) - (1 if self._flat or flat else 0)   # applies accidentals

        return key_int


    # APPLIES ONLY FOR KEY SIGNATURES (DEGREES)
    def get_key_float(self) -> float:

        # Whites Keys already sharpened or flattened due to time signature aren't considered (>= 24)
        if self._key < 24 and not (self._scale.hasScale() or self._natural):
            semitone_int: int = self.get_key_int()

            accidentals_int = self._key_signature._unit
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
        
        octave_offset, key_offset = self.octave_key_offset(key_offset)
        self._octave += octave_offset
        self._key += key_offset
        self._key %= 24   # Removes key from Key Signature specificity

        return self
    

    def __mod__(self, operand: o.Operand) -> o.Operand:
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
                    case ou.KeySignature(): return self._key_signature
                    case ou.Sharp():        return ou.Sharp() << od.DataSource(self._sharp)
                    case ou.Flat():         return self._flat
                    case ou.Natural():      return ou.Natural() << od.DataSource(self._natural)
                    case ou.Degree():       return ou.Degree() << od.DataSource(self._degree)
                    case Scale():           return self._scale
                    case int():             return self % int()
                    case float():           return self % float()
                    case str():
                        note_key = self % int() % 12
                        note_key += 12 * (self._flat)   # second line of the list
                        return ou.Key._keys[note_key]
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % (operand._data)
            case Pitch():           return self.copy()
            case ou.Octave():
                final_pitch: int = int(self % float())
                return ou.Octave( final_pitch // 12 - 1 )
            case ou.Sharp():
                final_pitch: int = int(self % float())
                if self._major_scale[final_pitch % 12] == 0:    # Black key
                    if self._key_signature._unit >= 0:
                        return ou.Sharp(True)
                return ou.Sharp(False)
            case ou.Flat():
                final_pitch: int = int(self % float())
                if self._major_scale[final_pitch % 12] == 0:    # Black key
                    if self._key_signature._unit < 0:
                        return ou.Flat(True)
                return ou.Flat(False)
            case ou.Natural():
                return ou.Natural() << od.DataSource(self._natural)
            
            case ou.KeySignature():
                return self._key_signature.copy()
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                return self._key_signature % operand
            case ou.Key():
                key_unit: int = int(self % float()) % 12
                return ou.Key( key_unit )
            
            case ou.Degree():
                return ou.Degree() << od.DataSource(self._degree)
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                                    return self._key_signature % operand
            case Scale():
                if self._scale.hasScale():
                    return self._scale.copy()
                return self._key_signature % operand
            case ou.Mode() | list():
                return (self % Scale()) % operand
            
            case str():
                key_note: int = int(self % float()) % 12
                key_line: int = self._key % 48 // 12
                if key_line < 2:
                    if self._key_signature._unit > 0:
                        key_line = 0
                    elif self._key_signature._unit < 0:
                        key_line = 1
                return ou.Key._keys[key_note + key_line * 12]
            
            case int(): # WITHOUT KEY SIGNATURE
                
                # IGNORES THE KEY SIGNATURE (CHROMATIC)
                return 12 * (self._octave + 1) + self.get_key_int()
             
            case float(): # WITH KEY SIGNATURE

                # RESPECTS THE KEY SIGNATURE
                return 12 * (self._octave + 1) + self.get_key_float()
            
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
        # self.octave_correction()    # Needed due to possible changes in staff KeySignature without immediate propagation (notice)
        serialization = super().getSerialization()

        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
        serialization["parameters"]["key"]              = self.serialize( self._key )
        serialization["parameters"]["octave"]           = self.serialize( self._octave )
        serialization["parameters"]["degree"]           = self.serialize( self._degree )
        serialization["parameters"]["sharp"]            = self.serialize( self._sharp )
        serialization["parameters"]["flat"]             = self.serialize( self._flat )
        serialization["parameters"]["natural"]          = self.serialize( self._natural )
        serialization["parameters"]["scale"]            = self.serialize( self._scale )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Pitch':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key_signature" in serialization["parameters"] and "key" in serialization["parameters"] and
            "sharp" in serialization["parameters"] and "flat" in serialization["parameters"] and "natural" in serialization["parameters"] and
            "degree" in serialization["parameters"] and "scale" in serialization["parameters"] and "octave" in serialization["parameters"]):

            super().loadSerialization(serialization)

            self._key_signature = self.deserialize( serialization["parameters"]["key_signature"] )
            self._key           = self.deserialize( serialization["parameters"]["key"] )
            self._octave        = self.deserialize( serialization["parameters"]["octave"] )
            self._degree        = self.deserialize( serialization["parameters"]["degree"] )
            self._sharp         = self.deserialize( serialization["parameters"]["sharp"] )
            self._flat          = self.deserialize( serialization["parameters"]["flat"] )
            self._natural       = self.deserialize( serialization["parameters"]["natural"] )
            self._scale         = self.deserialize( serialization["parameters"]["scale"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                super().__lshift__(operand)
                self._key_signature         << operand._key_signature
                self._key                   = operand._key
                self._octave                = operand._octave
                self._degree                = operand._degree
                self._sharp                 = operand._sharp
                self._flat                  = operand._flat
                self._natural               = operand._natural
                self._scale                 << operand._scale
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
                        self._unit = operand._data % od.DataSource( int() )
                    case ou.KeySignature():
                        self._key_signature = operand._data
                    case ou.Sharp():
                        self._sharp = operand._data // bool()
                    case ou.Flat():
                        self._flat  = operand._data // bool()
                    case ou.Natural():
                        self._natural = operand._data // bool()
                    case ou.Degree():
                        self._degree = operand._data // int()
                    case Scale():
                        self._scale << operand._data
                    case str():
                        self._flat      = ((operand._data).strip().lower().find("b") != -1) * 1
                        self._degree    = (self // ou.Degree() << ou.Degree(operand._data)) // int()
                        self._key       = ou.Key(operand._data) // int()
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
                self._key = int( self._key_signature % float() )
            case int():
                if operand == 0:
                    self._key = int( self._key_signature % float() )
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
                self << ou.KeySignature()   # Makes sure no Key Signature is in use
                self << ou.Degree()         # Makes sure no Degree different of Tonic is in use
                self << operand // float()
            case ou.Sharp():
                self._sharp = operand // bool()
            case ou.Flat():
                self._flat = operand // bool()
            case ou.Natural():
                self._natural = operand // bool()
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                self._key_signature << operand
                self._key = int( self._key_signature % float() )
            case Scale() | ou.Mode():
                self._scale     << operand
            case str():
                string: str = operand.strip()
                new_sharp: ou.Sharp = ou.Sharp(self._sharp) << string
                new_flat: ou.Flat = ou.Flat(self._flat) << string
                if new_sharp != self._sharp:
                    self._sharp = new_sharp // bool()
                    if new_sharp:
                        self._flat = False
                elif new_flat != self._flat:
                    if new_flat:
                        self._sharp = False
                    self._flat = new_flat // bool()
                self._degree    = (self // ou.Degree() << operand)._unit
                self._key       = (self // ou.Key() << string)._unit
            case tuple():
                for single_operand in operand:
                    self << single_operand

            case _:
                super().__lshift__(operand)

        return self

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
                new_keynote._key = sum_int % 12
                new_keynote._octave = sum_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case ou.Octave():
                self_copy._octave += operand._unit
            case float():
                key_offset: int = int(operand)
                self_copy.apply_key_offset(key_offset)
            case ou.Tone():
                key_offset: int = self.move_semitones(operand % int())
                self_copy.apply_key_offset(key_offset)
            case Fraction() | ra.Rational() | ou.Key() | ou.Semitone():
                key_offset: int = operand % int()
                self_copy.apply_key_offset(key_offset)
            case int() | ou.Unit():
                self_copy._degree = (self // ou.Degree() + operand)._unit
            case _:
                return super().__add__(operand)

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
                new_keynote._key = delta_int % 12
                new_keynote._octave = delta_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case ou.Octave():
                self_copy._octave -= operand._unit
            case float():
                key_offset: int = int(operand) * -1
                self_copy.apply_key_offset(key_offset)
            case ou.Tone():
                key_offset: int = self.move_semitones(operand % int()) * -1
                self_copy.apply_key_offset(key_offset)
            case Fraction() | ra.Rational() | ou.Key() | ou.Semitone():
                key_offset: int = operand % int() * -1
                self_copy.apply_key_offset(key_offset)
            case int() | ou.Unit():
                self_copy._degree = (self // ou.Degree() - operand)._unit
            case _:
                return super().__sub__(operand)

        return self_copy

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
        if self._scale.hasScale():
            scale = self._scale % list()
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
                self._number = ou.Number(operand)._unit
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

    def __add__(self, operand) -> 'Controller':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        value: int = self._value
        match operand:
            case o.Operand():
                value += operand % int()
            case int():
                value += operand
            case float() | Fraction():
                value += int(operand)
        return self.copy() << value
    
    def __sub__(self, operand) -> 'Controller':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        value: int = self._value
        match operand:
            case o.Operand():
                value -= operand % int()
            case int():
                value -= operand
            case float() | Fraction():
                value -= int(operand)
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
                    case str():                 return __class__.get_scale_name(self._scale_list)
                    case int():                 return __class__.get_scale_number(self._scale_list)
                    case _:                     return super().__mod__(operand)
            case ou.Mode():             return ou.Mode() << od.DataSource(self._mode)
            case list():                return self.modulation(None)
            case str():                 return __class__.get_scale_name(self.modulation(None))
            case int():                 return __class__.get_scale_number(self.modulation(None))
            case ou.Transposition():    return self.transposition(operand % int())
            case ou.Modulation():       return self.modulation(operand % int())
            case ou.Key():
                if self.hasScale():
                    key_int: int = int(operand % float())
                    key_scale: list = [0] * 12
                    for key_i in range(12):
                        key_scale[(key_i + key_int) % 12] = self._scale_list[key_i]
                    return key_scale
                return []
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

