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
        super().__init__()
        self._top: int      = 4 if top is None else int(max(1,  top  ))
        # This formula is just to make sure it's a power of 2, it doesn't change the input value if it is already a power of 2
        self._bottom: int   = 4 if \
            not (isinstance(bottom, int) and bottom > 0) else int(math.pow(2, int(max(0, math.log2(  bottom  )))))

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
            case od.DataSource():
                match operand % o.Operand():
                    case ra.BeatsPerMeasure():
                        self._top           = operand % o.Operand() % od.DataSource( int() )
                    case ra.BeatNoteValue():
                        if operand % o.Operand() % od.DataSource( int() ) > 0:
                            # This formula is just to make sure it's a power of 2, it doesn't change the input value if it is already a power of 2
                            self._bottom    = int(math.pow(2, int(max(0, math.log2(1 / (  operand % o.Operand() % od.DataSource( int() )  ))))))
            case TimeSignature():
                super().__lshift__(operand)
                self._top               = operand._top
                self._bottom            = operand._bottom
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
        super().__init__()
        
        self._key_signature: ou.KeySignature    = os.staff._key_signature.copy()
        self._key_key: ou.Key                   = ou.Key( self._key_signature.get_tonic_key() )
        self._sharp: ou.Sharp                   = ou.Sharp(0)
        self._flat: ou.Flat                     = ou.Flat(0)
        self._natural: ou.Natural               = ou.Natural(0)
        self._degree: ou.Degree                 = ou.Degree(1)
        self._scale: Scale                      = Scale([])

        self._octave: ou.Octave     = ou.Octave(4)  # By default it's the 4th Octave!
        self._key: ou.Key           = ou.Key()      # By default it's the Tonic key
        self._key_offset: int       = 0
        if len(parameters) > 0:
            self << parameters

    def key_signature(self, key_signature: 'ou.KeySignature' = None) -> 'Pitch':
        self._key_signature = key_signature
        return self

    def sharp(self, unit: int = None) -> 'Pitch':
        return self << od.DataSource( ou.Sharp(unit) )

    def flat(self, unit: int = None) -> 'Pitch':
        return self << od.DataSource( ou.Flat(unit) )

    def natural(self, unit: int = None) -> 'Pitch':
        return self << od.DataSource( ou.Natural(unit) )

    def degree(self, unit: int = None) -> 'Pitch':
        return self << od.DataSource( ou.Degree(unit) )

    def scale(self, scale: list[int] | str = None) -> 'Pitch':
        return self << od.DataSource( Scale(scale) )

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
        self.octave_correction()    # Needed due to possible changes in staff KeySignature without immediate propagation (notice)
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():        return self % od.DataSource( operand % o.Operand() )
                    case Pitch():           return self
                    case ou.Octave():       return self._octave
                    case ou.Key():          return self._key
                    case int():             return self % int()
                    case float():           return self % float()




                    case ou.KeySignature(): return self._key_signature
                    case ou.Sharp():        return self._sharp
                    case ou.Flat():         return self._flat
                    case ou.Natural():      return self._natural
                    case ou.Degree():       return self._degree
                    case Scale():           return self._scale
                    case float():           return self % float()
                    case str():
                        note_key = self % int() % 12
                        note_key += 12 * (self._flat._unit != 0)
                        return Key._keys[note_key]
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % (operand % o.Operand())
            case Pitch():           return self.copy()
            case ou.Octave():       return self._octave.copy()
            case ou.Key():          return self._key.copy()
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | ou.Unit() | ou.Natural() | ou.Degree() | Scale() | ou.Mode() | list() | str():
                return self._key % operand
            case int():
                # IGNORES THE KEY SIGNATURE (CHROMATIC)
                return 12 * (self._octave._unit + 1) + self._key % int() + self._key_offset
            case float():
                # RESPECTS THE KEY SIGNATURE
                return 12 * (self._octave._unit + 1) + self._key % float() + self._key_offset
            


            case ou.KeySignature(): return self._key_signature.copy() 
            case ou.Sharp():        return self._sharp.copy()
            case ou.Flat():         return self._flat.copy()
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                                    return self._key_signature % operand
            case ou.Natural():      return self._natural.copy()
            case ou.Degree():       return self._degree.copy()
            case Scale():
                if self._scale.hasScale():
                    return self._scale.copy()
                return self._key_signature % operand
            case ou.Mode() | list():
                return (self % Scale()) % operand
            case str():
                note_key = int(self % float()) % 12
                if Key._major_scale[note_key] == 0 and self._key_signature._unit < 0:
                    note_key += 12  # In case of FLAT Key Signature
                return Key._keys[note_key]
            case int(): # WITHOUT KEY SIGNATURE
                staff_white_keys        = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major scale
                accidentals_int: int    = self._key_signature._unit
                key_int: int            = self._unit
                degree_transpose: int   = self._degree._unit
                semitone_transpose: int = 0

                key_scale = staff_white_keys  # Major scale
                if self._scale.hasScale():
                    key_scale = self._scale % list()  # Already modulated

                while degree_transpose > 0:
                    semitone_transpose += 1
                    if key_scale[(key_int + semitone_transpose) % 12]:
                        degree_transpose -= 1
                while degree_transpose < 0:
                    semitone_transpose -= 1
                    if key_scale[(key_int + semitone_transpose) % 12]:
                        degree_transpose += 1

                key_int += semitone_transpose

                if staff_white_keys[(key_int + semitone_transpose) % 12] == 0:
                    if self._natural:
                        if accidentals_int < 0:
                            key_int += 1
                        else:
                            key_int -= 1
                    return key_int
                elif self._natural:
                    return key_int
                return key_int + self._sharp._unit - self._flat._unit
             
            case float(): # WITH KEY SIGNATURE
                # APPLIES ONLY FOR KEY SIGNATURES (DEGREES)
                if not (self._scale.hasScale() or self._natural):
                    semitone_int: int            = self % int()

                    accidentals_int = self._key_signature % int()
                    # Circle of Fifths
                    sharps_flats = KeySignature._key_signatures[(accidentals_int + 7) % 15] # [+1, 0, -1, ...]
                    semitone_transpose = sharps_flats[semitone_int % 12]
                    return float(semitone_int + semitone_transpose)
                return float(self % int())


            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        match other:
            case Pitch():
                return self % float() == other % float()
            case str() | ou.Key():
                return self._key    == other
            case int() | ou.Octave():
                return self % od.DataSource( ou.Octave() ) == other
            

            case self.__class__():
                return self % float() == other % float()    # This get's in consideration the just final key pressed
            case str():
                return self % str() == other
            case _:
                return super().__eq__(other)


        return False
    
    def __lt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Pitch():
                return self % float() < other % float()
            case str() | ou.Key():
                return self._key    < other
            case int() | ou.Octave():
                return self % od.DataSource( ou.Octave() ) < other




        return False
    
    def __gt__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Pitch():
                return self % float() > other % float()
            case str() | ou.Key():
                return self._key    > other
            case int() | ou.Octave():
                return self % od.DataSource( ou.Octave() ) > other
            




        return False
    
    def getSerialization(self) -> dict:
        self.octave_correction()    # Needed due to possible changes in staff KeySignature without immediate propagation (notice)
        serialization = super().getSerialization()

        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
        serialization["parameters"]["key_key"]          = self.serialize( self._key_key )
        serialization["parameters"]["sharp"]            = self.serialize( self._sharp )
        serialization["parameters"]["flat"]             = self.serialize( self._flat )
        serialization["parameters"]["natural"]          = self.serialize( self._natural )
        serialization["parameters"]["degree"]           = self.serialize( self._degree )
        serialization["parameters"]["scale"]            = self.serialize( self._scale )

        serialization["parameters"]["key"]        = self.serialize( self._key )
        serialization["parameters"]["octave"]     = self.serialize( self._octave )
        serialization["parameters"]["key_offset"] = self.serialize( self._key_offset )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Pitch':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key_signature" in serialization["parameters"] and "key_key" in serialization["parameters"] and
            "sharp" in serialization["parameters"] and "flat" in serialization["parameters"] and
            "natural" in serialization["parameters"] and "degree" in serialization["parameters"] and "scale" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "key" in serialization["parameters"] and "key_offset" in serialization["parameters"]):

            super().loadSerialization(serialization)

            self._key_signature = self.deserialize( serialization["parameters"]["key_signature"] )
            self._key_key       = self.deserialize( serialization["parameters"]["key_key"] )
            self._sharp         = self.deserialize( serialization["parameters"]["sharp"] )
            self._flat          = self.deserialize( serialization["parameters"]["flat"] )
            self._natural       = self.deserialize( serialization["parameters"]["natural"] )
            self._degree        = self.deserialize( serialization["parameters"]["degree"] )
            self._scale         = self.deserialize( serialization["parameters"]["scale"] )

            self._key           = self.deserialize( serialization["parameters"]["key"] )
            self._octave        = self.deserialize( serialization["parameters"]["octave"] )
            self._key_offset    = self.deserialize( serialization["parameters"]["key_offset"] )
            self.octave_correction()    # Needed due to possible changes in staff KeySignature without immediate propagation (notice)
        return self

    def __lshift__(self, operand: o.Operand) -> 'Pitch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Octave():       self._octave    = operand % o.Operand()
                    case ou.Key():          self._key       = operand % o.Operand()


                    case int():
                        self._unit = operand % o.Operand()
                    case float() | Fraction():
                        self._unit = int(operand % o.Operand())
                    case ou.Semitone():
                        self._unit = operand % o.Operand() % od.DataSource( int() )
                        self << ou.Degree(1)    # TO BE REMOVED !
                    case ou.KeySignature():
                        self._key_signature = operand % o.Operand()
                    case ou.Sharp():
                        self._sharp << operand % o.Operand()
                    case ou.Flat():
                        self._flat << operand % o.Operand()
                    case ou.Natural():
                        self._natural << operand % o.Operand()
                    case ou.Degree():
                        self._degree << operand % o.Operand()
                    case Scale():
                        self._scale << operand % o.Operand()
                    case str():
                        self._flat << ((operand % o.Operand()).strip().lower().find("b") != -1) * 1
                        self.key_to_int(operand % o.Operand())
                        self._degree << operand % o.Operand()
                    case _:
                        super().__lshift__(operand)

            case Pitch():
                super().__lshift__(operand)
                self._octave    << operand._octave
                self._key       << operand._key
                self._key_offset = operand._key_offset

                self._key_signature << operand._key_signature
                self._key_key._unit = operand._key_key._unit
                self._sharp._unit   = operand._sharp._unit
                self._flat._unit    = operand._flat._unit
                self._natural._unit = operand._natural._unit
                self._degree._unit  = operand._degree._unit
                self._scale         << operand._scale

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Octave():
                self._octave << operand
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | ou.Key() | int() | ou.Unit() | float() | str() | ou.Semitone() \
                | ou.Sharp() | ou.Flat() | ou.Natural() | ou.Degree() | Scale() | ou.Mode() | None:
                self._key << operand


            case int():
                if operand == 0:
                    self._unit      = self._key_signature.get_tonic_key()
                else:
                    self._degree    << operand
            case float() | Fraction() | ou.Semitone():
                                    if isinstance(operand, o.Operand):
                                        self._unit = operand % od.DataSource( int() )
                                    else:
                                        self._unit = int(operand)
                                    if self._major_scale[self._unit % 12] == 0:
                                        if self._key_signature._unit < 0:
                                            self._unit += 1
                                            self._sharp << False
                                            self._flat << True
                                        else:
                                            self._unit -= 1
                                            self._sharp << True
                                            self._flat << False
                                    else:
                                        self._sharp << False
                                        self._flat << False
            case ou.Sharp():
                self._sharp << operand
            case ou.Flat():
                self._flat << operand
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                self._key_signature << operand
                self._unit = self._key_signature.get_tonic_key()   # resets tonic key
            case ou.Natural():
                self._natural   << operand
            case ou.Degree():
                self._degree    << operand
            case Scale() | ou.Mode():
                self._scale     << operand
            case str():
                string: str = operand.strip()
                new_sharp: Sharp = self._sharp.copy(string)
                new_flat: Flat = self._flat.copy(string)
                if new_sharp != self._sharp:
                    self._sharp << new_sharp
                    if new_sharp:
                        self._flat  << False
                elif new_flat != self._flat:
                    if new_flat:
                        self._sharp << False
                    self._flat  << new_flat
                self._degree    << string
                self.key_to_int(string)
                self.stringToNumber(string)


            case tuple():
                for single_operand in operand:
                    self << single_operand

            case _:
                super().__lshift__(operand)

        if not isinstance(operand, tuple):
            self.octave_correction()
        return self

    def reset_sharps_and_flats(self) -> 'Pitch':
        self._sharp << False
        self._flat  << False
        if self._major_scale[self._unit % 12] == 0: # Black key
            if self._key_signature._unit < 0:           # flats
                self._unit += 1
                self._flat << True
            else:                                       # sharps
                self._unit -= 1
                self._sharp << True
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
            case _:
                return super().__add__(operand)




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
            case _:
                return super().__add__(operand)





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




            case _:
                return super().__mul__(operand)
    
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
            



            case _:
                return super().__div__(operand)


    def move_semitones(self, move_keys: int) -> int:
        scale = self._major_scale    # Major scale for the default staff
        if self._scale.hasScale():
            scale = self._scale % list()
        move_semitones: int = 0
        while move_keys > 0:
            move_semitones += 1
            if scale[(self % int() + move_semitones) % 12]:
                move_keys -= 1
        while move_keys < 0:
            move_semitones -= 1
            if scale[(self % int() + move_semitones) % 12]:
                move_keys += 1
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
    
    def stringToNumber(self, string: str):
        string = string.lower().replace("dim", "").replace("aug", "").replace("maj", "")
        for key, value in self._white_keys.items():
            if string.find(key) != -1:
                self._key_key._unit = value
                return

    _keys: list[str]    = ["C",  "C#", "D", "D#", "E",  "F",  "F#", "G", "G#", "A", "A#", "B",
                           "C",  "Db", "D", "Eb", "E",  "F",  "Gb", "G", "Ab", "A", "Bb", "B",
                           "B#", "C#", "D", "D#", "Fb", "E#", "F#", "G", "G#", "A", "A#", "Cb"]

    def key_to_int(self, key: str = "C"):
        for index, value in enumerate(self._keys):
            if value.lower().find(key.strip().lower()) != -1:
                self._key_key._unit = index % 12
                return

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
            case int() | float() | ou.Value() | Fraction():
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
            case int() | float() | ou.Value() | Fraction():
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
        self._scale_list: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major by default
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
            mode_int = self._mode._unit if mode is None else ou.Mode(mode) % int()
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

