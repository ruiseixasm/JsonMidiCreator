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
import operand_container as oc


class Generic(o.Operand):
    """`Generic`

    Generic represents any `Operand` that doesn't fit any particular type of `Operand` in nature or parameters type.

    Parameters
    ----------
    Any(None) : Generic doesn't have any self parameters.
    """
    pass


class TimeSignature(Generic):
    """`Generic -> TimeSignature`

    A time signature indicates the number of `Beats` in each `Measure` and the note value that receives one `Beat`.

    Args:
        top (int): The top value of a time signature, like, the 2 in a 2/4 time signature.
        bottom (int): The bottom value of a time signature, like, the 4 in a 2/4 time signature.
    """
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
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
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
        other_signature = self._tail_lshift(other_signature)    # Processes the tailed self operands or the Frame operand if any exists
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
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeSignature():
                super().__lshift__(operand)
                self._top               = operand._top
                self._bottom            = operand._bottom
            case od.Pipe():
                match operand._data:
                    case ra.BeatsPerMeasure():
                        self._top           = operand._data % od.Pipe( int() )
                    case ra.BeatNoteValue():
                        if operand._data % od.Pipe( int() ) > 0:
                            # This formula is just to make sure it's a power of 2, it doesn't change the input value if it is already a power of 2
                            self._bottom    = int(math.pow(2, int(max(0, math.log2(1 / (  operand._data % od.Pipe( int() )  ))))))
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.BeatsPerMeasure():
                self._top               = int(max(1, operand % int()))
            case ra.BeatNoteValue():
                if operand % int() > 0:
                    # This formula is just to make sure it's a power of 2, it doesn't change the input value if it is already a power of 2
                    self._bottom        = int(math.pow(2, int(max(0, math.log2(1 / (  operand % int()  ))))))
        return self


if TYPE_CHECKING:
    from operand_element import Element

class Pitch(Generic):
    """`Generic -> Pitch`

    A `Pitch` comes down the the absolute key in a full midi keyboard of 128 keys. To do so, processes and keeps many related \
    parameters like `Octave` and `Degree`.

    Parameters
    ----------
    Tonic(defaults), None : The tonic key on which the `Degree` is based on.
    Octave(4) : The octave on the keyboard with the middle C setting on the 4th octave.
    Degree(1), int : Degree sets the position of a note on a `Scale`, with designations like tonic, supertonic and dominant.
    Sharp(0), Flat : `Sharp` and `Flat` sets the respective accidental of a given note.
    Natural(False) : `Natural` disables the effects of `Sharp` and `Flat` and any accidental.
    list([]), Scale(), str, None : Sets the `Scale` to be used, `None` or `[]` uses the staff `KeySignature`.
    bool(True) : Sets if the given scale is processed as transposition (True) or as modulation (False).
    """
    def __init__(self, *parameters):
        import operand_element as oe
        self._tonic_key: int            = defaults._staff % ou.Key() % int()
        self._octave: int               = 4     # By default it's the 4th Octave!
        self._degree: int               = 1     # By default it's Degree 1
        self._shifting: int             = 0     # By default it's it has no shifting (transposition/modulation)
        self._sharp: int                = 0     # By default not a Sharp or Flat
        self._natural: bool             = False
        self._scale: list[int]          = []
        self._transpose: bool           = True  # Sets the process as Transposition instead of Modulation

        self._owner_element: oe.Element = None
        super().__init__(*parameters)


    def _set_owner_element(self, owner_element: 'Element') -> Self:
        import operand_element as oe
        if isinstance(owner_element, oe.Element):
            self._owner_element = owner_element
        return self

    def _get_staff(self) -> 'Staff':
        if self._owner_element is None:
            return defaults._staff
        return self._owner_element._get_staff()

    """
    Methods used to calculate the final chromatic pitch as `pitch_int` by following
    the formula:
        pitch_int = 
            tonic_key
            + octave_transposition + degree_transposition + scale_transposition
            + accidentals_transposition
    """

    def octave_transposition(self) -> int:
        """
        Because Midi octaves start at -1, +12 needs to be added
        """
        return 12 * self._octave + 12

    def degree_transposition(self) -> int:
        """
        Based on the Key Signature, this method gives the degree transposition
        """
        key_signature: ou.KeySignature = self._get_staff()._key_signature
        tonic_scale: list[int] = key_signature.get_scale_list()
        degree_0 = (self._degree - 1) % 7   # Key Signatures always have 7 keys (diatonic scales)
        """
        IN A TRANSPOSITION SCALE ACCIDENTALS **ARE** SUPPOSED TO HAPPEN
        """
        return Scale.transpose_key(degree_0, tonic_scale)

    def scale_transposition(self, root_key: int) -> int:
        """
        For a non zero shifting, the respective transposition or modulation of the given degree_transposition is returned.
        """
        transposition: int = 0
        if self._shifting != 0:
            if self._scale:
                modulated_scale: list[int] = self._scale
                if self._transpose: # Transposition is only applicable to a Scale, not a Key Signature
                    """
                    IN A TRANSPOSITION SCALE ACCIDENTALS **ARE** SUPPOSED TO HAPPEN
                    """
                    transposition = Scale.transpose_key(self._shifting, modulated_scale)
                else:
                    """
                    Scale modulation is set by the Scale itself
                    """
                    scale_tonic: int = Scale.get_tonic_key(modulated_scale)
                    tonic_offset: int = root_key - scale_tonic
                    """
                    IN A MODULATION SCALE ACCIDENTALS **ARE NOT** SUPPOSED TO HAPPEN
                    """
                    transposition = Scale.modulate_key(tonic_offset, self._shifting, modulated_scale)

            else:   # For KeySignature the Modulation is treated as a degree_0
                key_signature: ou.KeySignature = self._get_staff()._key_signature
                tonic_scale: list[int] = key_signature.get_scale_list()
                """
                KeySignature modulation is set by the Tonic key instead
                """
                tonic_offset: int = root_key - self._tonic_key
                """
                IN A MODULATION SCALE ACCIDENTALS **ARE NOT** SUPPOSED TO HAPPEN
                """
                transposition = Scale.modulate_key(tonic_offset, self._shifting, tonic_scale)
        return transposition

    def accidentals_transposition(self, scale_key: int) -> int:
        """
        Processes the given set sharps and natural accordingly as final decorators.
        """
        transposition: int = 0
        # Final parameter decorators like Sharp and Natural
        if self._natural:
            if self._major_scale[(scale_key + transposition) % 12] == 0:  # Black key
                accidentals_int: int = self._get_staff()._key_signature._unit
                if accidentals_int < 0:
                    transposition += 1  # Considered a flat
                else:
                    transposition -= 1  # Considered a sharp
        elif self._sharp != 0:
            if self._major_scale[(scale_key + transposition) % 12] == 1:  # White key
                transposition += self._sharp  # applies Pitch self accidentals
        return transposition

    def pitch_int(self) -> int:
        """
        The final chromatic conversion of the tonic_key into the midi pitch.
        """
        tonic_key: int = self._tonic_key % 12   # It may represent a flat, meaning, may be above 12
        octave_transposition: int = self.octave_transposition()
        degree_transposition: int = self.degree_transposition()
        root_key: int = tonic_key + degree_transposition
        scale_transposition: int = self.scale_transposition(root_key)
        scale_key: int = root_key + scale_transposition
        accidentals_transposition: int = self.accidentals_transposition(scale_key)
        return tonic_key \
            + octave_transposition + degree_transposition + scale_transposition \
            + accidentals_transposition

    """
    Auxiliary methods to get specific data directly
    """

    def root_key(self) -> int:
        tonic_key: int = self._tonic_key % 12   # It may represent a flat, meaning, may be above 12
        degree_transposition: int = self.degree_transposition()
        return tonic_key + degree_transposition



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


    def get_key_degree(self, root_key: int) -> int:
        tonic_key: int = self._tonic_key % 12
        staff_scale: list[int] = self._get_staff() % list()
        total_keys: int = sum(1 for key in staff_scale if key != 0)

        degree_0: int = 0
        
        # tonic_key goes UP and then DOWN (results in flat or natural)
        while tonic_key < root_key:
            if staff_scale[ (root_key - tonic_key) % 12 ] == 1:  # Scale key
                degree_0 += 1
            tonic_key += 1
        while tonic_key > root_key:
            if staff_scale[ (root_key - tonic_key) % 12 ] == 1:  # Scale key
                degree_0 -= 1
            tonic_key -= 1

        if staff_scale[ (root_key - self._tonic_key % 12) % 12 ] == 0:  # Key NOT on the scale
            if self._tonic_key // 12 == 1:  # Checks the tonic key line
                if self._tonic_key % 12 > root_key:
                    degree_0 -= 1
            else:
                if self._tonic_key % 12 < root_key:
                    degree_0 += 1

        # Sets the Degree as Positive
        degree_0 %= total_keys

        return degree_0 + 1 # Degree base 1 (I)


    # measure input lets the preservation of a given accidental to be preserved along the entire Measure
    def get_key_with_accidentals(self, root_key: int) -> int:
        key_int: int = root_key

        # Final parameter decorators like Sharp and Natural
        if self._natural:
            if self._major_scale[key_int % 12] == 0:  # Black key
                accidentals_int: int = self._get_staff()._key_signature._unit
                if accidentals_int < 0:
                    key_int += 1
                else:
                    key_int -= 1
        elif self._sharp != 0:
            if self._major_scale[key_int % 12] == 1:  # White key
                key_int += self._sharp  # applies Pitch self accidentals
        return key_int


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
    
    def set_chromatic_pitch(self, pitch: int) -> Self:
        
        # Reset purely decorative parameters
        self._natural = False
        self._sharp = 0

        # Excludes the effect of purely decorative parameters
        key_offset: int = pitch - self.pitch_int()
        return self.apply_key_offset(key_offset)


    def octave_degree_offset(self, degree_offset: int) -> tuple[int, int]:
        
        self_degree_0: int = 0
        if self._degree > 0:
            self_degree_0 = self._degree - 1
        elif self._degree < 0:
            self_degree_0 = self._degree + 1

        staff_scale: list[int] = self._get_staff() % list()
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
            case od.Pipe():
                match operand._data:
                    case of.Frame():        return self % od.Pipe( operand._data )
                    case ou.Octave():       return operand._data << od.Pipe(self._octave)
                    case ou.Tonic():        return operand._data << od.Pipe(self._tonic_key)    # Must come before than Key()
                    case ou.Degree():       return operand._data << od.Pipe(self._degree)
                    case ou.Shifting():     return operand._data << od.Pipe(self._shifting)
                    case ou.Sharp():        return operand._data << od.Pipe(max(0, self._sharp))
                    case ou.Flat():         return operand._data << od.Pipe(max(0, self._sharp * -1))
                    case ou.Natural():      return operand._data << od.Pipe(self._natural)
                    # bool is an int, so, it must come before an int to be processed as a bool!
                    case bool():            return self._transpose
                    case int():             return self._degree
                    case float():           return float(self._tonic_key)
                    case Fraction():        return Fraction(self._shifting)
                    case Scale():           return operand._data << od.Pipe(self._scale)
                    case list():            return self._scale
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % operand

            case bool():    # bool is an int, so, it must come before an int to be processed as a bool!
                return self._transpose
            
            case int():
                self_degree_0: int = 0
                if self._degree > 0:
                    self_degree_0 = self._degree - 1
                elif self._degree < 0:
                    self_degree_0 = self._degree + 1
                staff_scale: list[int] = self._get_staff() % list()
                total_degrees: int = sum(1 for key in staff_scale if key != 0)

                return self_degree_0 % total_degrees + 1
             
            case Fraction():
                return Fraction(self._shifting)
            
            case float():
                return float( self.pitch_int() )
            
            case ou.Semitone():
                return ou.Semitone(self.pitch_int())
            
            case ou.Tonic():    # Must come before than Key()
                return ou.Tonic(self._tonic_key)
            case ou.Root():
                root_key: int = self.root_key() % 12
                root_key += self._tonic_key // 12 * 12  # key_line * total_keys
                return ou.Root(root_key)
            
            case ou.Octave():
                target_pitch: int = self.pitch_int()
                return ou.Octave( target_pitch // 12 - 1 )
            
            case ou.Degree():
                return ou.Degree(self % int())
            case ou.Shifting():
                return ou.Shifting(self._shifting)
             
            case ou.Sharp():
                target_pitch: int = self.pitch_int()
                if self._major_scale[target_pitch % 12] == 0:    # Black key
                    if self._get_staff()._key_signature._unit >= 0:
                        return ou.Sharp(1)
                return ou.Sharp(0)
            case ou.Flat():
                target_pitch: int = self.pitch_int()
                if self._major_scale[target_pitch % 12] == 0:    # Black key
                    if self._get_staff()._key_signature._unit < 0:
                        return ou.Flat(1)
                return ou.Flat(0)
            case ou.Natural():
                return ou.Natural() << od.Pipe(self._natural)
            
            case Scale():
                return Scale(self._scale)
            case list():
                return self._scale.copy()

            case ou.KeySignature():
                return self._get_staff()._key_signature.copy()
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                return self._get_staff()._key_signature % operand
            case ou.Key():
                self_pitch: int = self.pitch_int()
                key_note: int = self_pitch % 12
                key_line: int = self._tonic_key // 12
                self_staff: Staff = self._get_staff()   # Optimization
                if self_staff._key_signature.is_enharmonic(self._tonic_key, key_note):
                    key_line += 2    # All Sharps/Flats
                return ou.Key( float(key_note + key_line * 12) )
            
            case str():
                return self % ou.Key() % str()
            
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        match other:
            case Pitch():
                # return self.pitch_int() == other.pitch_int()
                return self.pitch_int() == other.pitch_int()
            case ou.Octave():
                return self % od.Pipe( ou.Octave() ) == other
            case int() | float() | str() | ou.Key() | Scale():
                return self % other == other
            case od.Conditional():
                return other == self
            case _:
                return super().__eq__(other)
        return False
    
    def __lt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Pitch():
                return self.pitch_int() < other.pitch_int()
            case ou.Octave():
                return self % od.Pipe( ou.Octave() ) < other
            case int() | float():
                return self % other < other
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Pitch():
                return self.pitch_int() > other.pitch_int()
            case ou.Octave():
                return self % od.Pipe( ou.Octave() ) > other
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
        serialization["parameters"]["shifting"]         = self.serialize( self._shifting )
        serialization["parameters"]["sharp"]            = self.serialize( self._sharp )
        serialization["parameters"]["natural"]          = self.serialize( self._natural )
        serialization["parameters"]["scale"]            = self.serialize( self._scale )
        serialization["parameters"]["transpose"]        = self.serialize( self._transpose )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tonic_key" in serialization["parameters"] and "sharp" in serialization["parameters"] and "natural" in serialization["parameters"] and
            "degree" in serialization["parameters"] and "octave" in serialization["parameters"] and "shifting" in serialization["parameters"] and 
            "scale" in serialization["parameters"] and "transpose" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tonic_key     = self.deserialize( serialization["parameters"]["tonic_key"] )
            self._octave        = self.deserialize( serialization["parameters"]["octave"] )
            self._degree        = self.deserialize( serialization["parameters"]["degree"] )
            self._shifting      = self.deserialize( serialization["parameters"]["shifting"] )
            self._sharp         = self.deserialize( serialization["parameters"]["sharp"] )
            self._natural       = self.deserialize( serialization["parameters"]["natural"] )
            self._scale         = self.deserialize( serialization["parameters"]["scale"] )
            self._transpose     = self.deserialize( serialization["parameters"]["transpose"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_element as oe
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                super().__lshift__(operand)
                self._tonic_key             = operand._tonic_key
                self._octave                = operand._octave
                self._degree                = operand._degree
                self._shifting              = operand._shifting
                self._sharp                 = operand._sharp
                self._natural               = operand._natural
                self._scale                 = operand._scale.copy()
                self._transpose             = operand._transpose
                # Because a Pitch is also defined by the Owner Element, this also needs to be copied!
                if self._owner_element is None: # << and copy operation doesn't override ownership
                    self._owner_element     = operand._owner_element
            case od.Pipe():
                match operand._data:
                    case ou.Tonic():    # Must come before than Key()
                        self._tonic_key = operand._data._unit
                    case ou.Octave():
                        self._octave    = operand._data._unit
                    case bool():    # bool is an int, so, it must come before an int to be processed as a bool!
                        self._transpose = operand._data
                    case int():
                        self._degree = operand._data
                    case float():
                        self._tonic_key = int(operand._data)
                    case Fraction():
                        self._shifting = int(operand._data)
                    case ou.Semitone():
                        self._tonic_key = operand._data._unit
                    case ou.Sharp():
                        self._sharp = operand._data._unit
                    case ou.Flat():
                        self._sharp = operand._data._unit * -1
                    case ou.Natural():
                        self._natural = operand._data.__mod__(od.Pipe( bool() ))
                    case ou.Degree():
                        self._degree = operand._data._unit
                    case ou.Shifting():
                        self._shifting = operand._data._unit
                    case Scale():
                        self._scale = operand._data._scale
                    case list():
                        self._scale = operand._data
                    case str():
                        self._sharp     = \
                            ((operand._data).strip().lower().find("#") != -1) * 1 + \
                            ((operand._data).strip().lower().find("b") != -1) * -1
                        self._degree    = (self % od.Pipe( ou.Degree() ) << ou.Degree(operand._data))._unit
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

            case bool():    # bool is an int, so, it must come before an int to be processed as a bool!
                self._transpose = operand
            case int():
                if operand > 0:
                    staff_scale: list[int] = self._get_staff()._key_signature % list()
                    total_degrees: int = sum(1 for key in staff_scale if key != 0)
                    self._degree = (operand - 1) % total_degrees + 1
                elif operand == 0:
                    self._tonic_key = self._get_staff()._key_signature.get_tonic_key()
                else:
                    self << 0   # Resets the Tonic key
                    self << 1   # Resets the degree to I
                    self._octave = 4
                    self._sharp = 0
                    self._natural = False
            case ou.Degree():
                self << operand._unit   # Sets as int like above
            case ou.Transposition():
                self._shifting = operand._unit
                self._transpose = True
            case ou.Modulation():
                self._shifting = operand._unit
                self._transpose = False
            case ou.Shifting():
                self._shifting = operand._unit
            case Fraction():
                self._shifting = int(operand)

            case float():
                self.set_chromatic_pitch(int(operand))
            case ou.Semitone():
                self.set_chromatic_pitch(operand._unit)
            case ou.Tone():
                self._tonic_key = operand._unit % 12
                self._octave = operand._unit // 12 - 1

            case dict():
                for octave, value in operand.items():
                    self << value << ou.Octave(octave)

            case ou.DrumKit():
                self._natural = False
                self._sharp = 0
                self << ou.Degree()         # Makes sure no Degree different of Tonic is in use
                self << operand % od.Pipe( float() )  # Sets the key number regardless KeySignature or Scale!
            case ou.Sharp():
                if max(0, self._sharp) != operand._unit:
                    self._sharp = operand._unit % 3
            case ou.Flat():
                if max(0, self._sharp * -1) != operand._unit:
                    self._sharp = operand._unit % 3 * -1
            case ou.Natural():
                self._natural = operand.__mod__(od.Pipe( bool() ))
                
            case Scale():
                self._scale = operand % list()
            case list():
                self._scale = operand.copy()
            case None:
                self._scale = []

            case str():
                string: str = operand.strip()
                self._sharp = \
                    (ou.Sharp(max(0, self._sharp)) << string)._unit + \
                    (ou.Flat(max(0, self._sharp * -1)) << string)._unit
                self._degree    = (self % ou.Degree() << operand)._unit
                self._tonic_key = (self % ou.Key() << string)._unit
                self._scale = Scale(od.Pipe(self._scale), operand) % od.Pipe(list())
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                super().__lshift__(operand)

        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                self += operand % float()
            case ou.Octave():
                self._octave += operand._unit
            case int():
                self.apply_degree_offset(operand)
            case ou.Degree():
                self.apply_degree_offset(operand._unit)
            case ou.Transposition():
                self._shifting += operand._unit
                self._transpose = True
            case ou.Modulation():
                self._shifting += operand._unit
                self._transpose = False
            case ou.Shifting():
                self._shifting += operand._unit
            case ou.Tone() | ou.Root():
                new_pitch: int = self.pitch_int() + self.move_semitones(operand % int())
                self.set_chromatic_pitch(new_pitch)
            case ou.Tonic():
                self._tonic_key += operand._unit
            case float():
                new_pitch: int = self.pitch_int() + int(operand)
                self.set_chromatic_pitch(new_pitch)
            case Fraction():
                self._shifting += int(operand)
            case ra.Rational() | ou.Key() | ou.Semitone():
                new_pitch: int = self.pitch_int() + operand % int()
                self.set_chromatic_pitch(new_pitch)
            case dict():
                for octave, value in operand.items():
                    self += value
                    self += ou.Octave(octave)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                self -= operand % float()
            case ou.Octave():
                self._octave -= operand._unit
            case int():
                self.apply_degree_offset(-operand)
            case ou.Degree():
                self.apply_degree_offset(-operand._unit)
            case ou.Transposition():
                self._shifting -= operand._unit
                self._transpose = True
            case ou.Modulation():
                self._shifting -= operand._unit
                self._transpose = False
            case ou.Shifting():
                self._shifting -= operand._unit
            case ou.Tone() | ou.Root():
                new_pitch: int = self.pitch_int() - self.move_semitones(operand % int())
                self.set_chromatic_pitch(new_pitch)
            case ou.Tonic():
                self._tonic_key -= operand._unit
            case float():
                new_pitch: int = self.pitch_int() - int(operand)
                self.set_chromatic_pitch(new_pitch)
            case Fraction():
                self._shifting -= int(operand)
            case ra.Rational() | ou.Key() | ou.Semitone():
                new_pitch: int = self.pitch_int() - operand % int()
                self.set_chromatic_pitch(new_pitch)
            case dict():
                for octave, value in operand.items():
                    self -= value
                    self -= ou.Octave(octave)
        return self

    def __mul__(self, operand) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                new_keynote = self.__class__()
                self_degree: int = self % int()
                multiplied_int = self_degree * operand
                new_keynote._tonic_key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case float():
                new_keynote = self.__class__()
                self_pitch: int = self.pitch_int()
                multiplied_int = int(self_pitch * operand)
                new_keynote._tonic_key = multiplied_int % 12
                new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                return new_keynote
            case _:
                return super().__mul__(operand)
    
    def __div__(self, operand) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        if operand != 0:
            match operand:
                case int():
                    new_keynote = self.__class__()
                    self_degree: int = self % int()
                    multiplied_int = int(self_degree / operand)
                    new_keynote._tonic_key = multiplied_int % 12
                    new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                    return new_keynote
                case float():
                    new_keynote = self.__class__()
                    self_pitch: int = self.pitch_int()
                    multiplied_int = int(self_pitch / operand)
                    new_keynote._tonic_key = multiplied_int % 12
                    new_keynote._octave = multiplied_int // 12 - 1 # rooted on -1 octave
                    return new_keynote
        return super().__div__(operand)


    def move_semitones(self, move_tones: int) -> int:
        scale = self._major_scale    # Major scale for the default staff
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
        scale_list: list[int] = self._get_staff() % list()
        self_pitch: int = self.pitch_int()
        pitch_offset: int = 0
        if up:
            pitch_step: int = 1
        else:
            pitch_step: int = -1
        while scale_list[self_pitch + pitch_offset] == 0:
            pitch_offset += float(pitch_step)
        if pitch_offset > 0:
            self += float(pitch_offset)
        return self


class Controller(Generic):
    """`Generic -> Controller`

    A `Controller` defines all the parameters concerning a device control that receives a value for its modulation.

    Parameters
    ----------
    Number("Pan"), MSB, int : The Controller number or MSB number (Most Significant Byte).
    LSB(0) : The Controller number or MSB number (Least Significant Byte).
    NRPN(False) : Sets the controller as an NRPN one.
    High(False), int : Allows the processing of high resolution values up to 16383 (128*128 - 1) instead the usual 127 (128 - 1).
    """
    def __init__(self, *parameters):
        self._number_msb: int   = ou.Number("Pan")._unit
        self._lsb: int          = 0 # lsb for 14 bits messages
        self._nrpn: bool        = False
        self._high: bool        = False
        super().__init__(*parameters)


    def _midi_msb_lsb_values(self, value: int) -> tuple[int]:
            
        msb_value: int  = (value >> 7) & 127
        lsb_value: int  = value & 127

        if not self._high:
            msb_value: int  = value & 127

        return msb_value, lsb_value


    def _midi_nrpn_values(self, value: int) -> tuple[int]:

        cc_99_msb: int  = self._number_msb
        cc_98_lsb: int  = self._lsb
        cc_6_msb: int   = (value >> 7) & 127
        cc_38_lsb: int  = value & 127

        if not self._high:
            cc_6_msb    = value & 127

        return cc_99_msb, cc_98_lsb, cc_6_msb, cc_38_lsb


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
            case od.Pipe():
                match operand._data:
                    case ou.Number():           return operand._data << od.Pipe(self._number_msb)
                    case ou.LSB():              return operand._data << od.Pipe(self._lsb)
                    case ou.NRPN():             return operand._data << od.Pipe(self._nrpn)
                    case ou.HighResolution():   return operand._data << od.Pipe(self._high)
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case bool():                return self._high
                    case _:                     return super().__mod__(operand)
            case ou.Number():           return operand.copy() << od.Pipe(self._number_msb)
            case ou.LSB():              return operand.copy() << od.Pipe(self._lsb)
            case ou.NRPN():             return operand.copy() << od.Pipe(self._nrpn)
            case ou.HighResolution():   return operand.copy() << od.Pipe(self._high)
            case bool():                return self._high
            case dict():
                controller_dict: dict[str, int] = {
                    "MSB": self._number_msb,
                    "LSB": self._lsb,
                    "NRPN": self._nrpn,
                    "HIGH": self._high
                }
                return controller_dict
            case of.Frame():            return self % operand
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, Controller):
            return self._number_msb == other._number_msb and self._lsb == other._lsb \
                and self._nrpn == other._nrpn and self._high == other._high
        if isinstance(other, od.Conditional):
            return other == self
        return self % other == other
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["number_msb"]   = self.serialize( self._number_msb )
        serialization["parameters"]["lsb"]          = self.serialize( self._lsb )
        serialization["parameters"]["nrpn"]         = self.serialize( self._nrpn )
        serialization["parameters"]["high"]         = self.serialize( self._high )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "number_msb" in serialization["parameters"] and "lsb" in serialization["parameters"] and
            "nrpn" in serialization["parameters"] and "high" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._number_msb    = self.deserialize( serialization["parameters"]["number_msb"] )
            self._lsb           = self.deserialize( serialization["parameters"]["lsb"] )
            self._nrpn          = self.deserialize( serialization["parameters"]["nrpn"] )
            self._high          = self.deserialize( serialization["parameters"]["high"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Controller():
                super().__lshift__(operand)
                self._number_msb    = operand._number_msb
                self._lsb           = operand._lsb
                self._nrpn          = operand._nrpn
                self._high          = operand._high
            case od.Pipe():
                match operand._data:
                    case ou.Number():           self._number_msb = operand._data._unit
                    case ou.LSB():              self._lsb = operand._data._unit
                    case ou.NRPN():             self._nrpn = bool(operand._data._unit)
                    case ou.HighResolution():   self._high = bool(operand._data._unit)
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.MSB():      # Must be check before the Number class
                self._number_msb = operand._unit
            case bool():   # bool is a subclass of int !!
                self._high = operand
            case int():         # Includes ou.MSB() as a subclass of Number
                self._number_msb = operand
                # Number has implicit 7 bytes CC
                self._nrpn = False
                self._high = False
            case ou.Number():   # Includes ou.MSB() as a subclass of Number
                self << operand._unit
            case str():
                self._number_msb = ou.Number(self._number_msb, operand)._unit
            case ou.LSB():
                self._lsb = operand._unit
            case ou.NRPN():
                self._nrpn = bool(operand._unit)
            case ou.HighResolution():
                self._high = bool(operand._unit)
            case dict():
                if "NUMBER" in operand and isinstance(operand["NUMBER"], int):
                    self._number_msb = operand["NUMBER"]
                    # Number has implicit 7 bytes CC
                    self._nrpn = False
                    self._high = False
                else:
                    if "MSB" in operand and isinstance(operand["MSB"], int):
                        self._number_msb = operand["MSB"]
                    if "NRPN" in operand and isinstance(operand["NRPN"], int):   # bool is a subclass of int !!
                        self._nrpn = bool(operand["NRPN"])
                    if "HIGH" in operand and isinstance(operand["HIGH"], int):   # bool is a subclass of int !!
                        self._high = bool(operand["HIGH"])
                    if "LSB" in operand and isinstance(operand["LSB"], int):
                        self._lsb = operand["LSB"]
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


class Scale(Generic):
    """`Generic -> Scale`

    A `Scale` is a series of notes ordered by pitch and separated by intervals of whole and half steps.

    Parameters
    ----------
    list([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]), str : Sets the scale type where default scale is the Major scale.
    """
    def __init__(self, *parameters):
        self._scale: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major by default
        super().__init__(*parameters)


    @staticmethod
    def transpose_key(steps: int = 4, scale: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]) -> int:
        # The given scale shall always have a size of 12
        scale_transposition: int = 0
        if len(scale) == 12 and sum(1 for key in scale if key != 0) > 0:
            while steps > 0:
                scale_transposition += 1
                if scale[scale_transposition % 12]:
                    steps -= 1
            while steps < 0:
                scale_transposition -= 1
                if scale[scale_transposition % 12]:
                    steps += 1
        return scale_transposition

    @staticmethod
    def modulate_key(tonic_offset: int = 0, degrees_0: int = 4, scale: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]) -> int:
        # The given scale shall always have a size of 12
        tonic_modulation: int = 0
        if len(scale) == 12 and sum(1 for key in scale if key == 1) > 0:
            while degrees_0 > 0:
                tonic_modulation += 1
                if scale[ (tonic_offset + tonic_modulation) % 12 ] == 1:  # Scale key
                    degrees_0 -= 1
            while degrees_0 < 0:
                tonic_modulation -= 1
                if scale[ (tonic_offset + tonic_modulation) % 12 ] == 1:  # Scale key
                    degrees_0 += 1
        return tonic_modulation


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
            case od.Pipe():
                match operand._data:
                    case list():                return self._scale
                    case str():                 return self.get_scale_name(self._scale)
                    case int():                 return self.get_scale_number(self._scale)
                    case ou.Key():              return ou.Key(self._tonics[ max(0, self.get_scale_number(self._scale)) ])
                    case _:                     return super().__mod__(operand)
            case list():                return self._scale.copy()
            case str():                 return self.get_scale_name(self.modulation(None))
            case int():                 return self.get_scale_number(self.modulation(None))
            case ou.Tonic():            return ou.Tonic( Scale.get_tonic_key(self._scale) )
            case ou.Key():              return ou.Key( Scale.get_tonic_key(self._scale) )
            case float():               return float( Scale.get_tonic_key(self._scale) )
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Scale') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        if isinstance(other, od.Conditional):
            return other == self
        return  self._scale == other._scale
    
    def hasScale(self) -> bool:
        if self._scale == [] or self._scale == -1 or self._scale == "":
            return False
        return True

    def keys(self) -> int:
        return sum(1 for key in self._scale if key != 0)

    def transposition(self, tones: int) -> int:        # Starting in C
        transposition = 0
        if isinstance(self._scale, list) and len(self._scale) == 12:
            modulated_scale: list[int] = self.modulation(None)
            while tones > 0:
                transposition += 1
                if modulated_scale[transposition % 12]:
                    tones -= 1
        return transposition

    def modulation(self, mode: int | str = "5th") -> list[int]: # AKA as remode (remoding)
        self_scale = self._scale.copy()
        if isinstance(self._scale, list) and len(self._scale) == 12:
            mode_int = 1 if mode is None else ou.Mode(mode) % int()
            tones = max(1, mode_int) - 1    # Modes start on 1, so, mode - 1 = tones
            transposition = 0
            if isinstance(self._scale, list) and len(self._scale) == 12:
                while tones > 0:
                    transposition += 1
                    if self._scale[transposition % 12]:
                        tones -= 1
            if transposition != 0:
                for key_i in range(12):
                    self_scale[key_i] = self._scale[(key_i + transposition) % 12]
        return self_scale

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["scale"]   = self.serialize( self._scale )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "scale" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._scale    = self.deserialize( serialization["parameters"]["scale"] )
        return self


    def modulate(self, mode: int | str = "5th") -> Self: # AKA as remode (remoding)
        modulated_scale: list[int] = self._scale.copy()
        if isinstance(self._scale, list) and len(self._scale) == 12:
            mode_int = 1 if mode is None else ou.Mode(mode) % int()
            tones = max(1, mode_int) - 1    # Modes start on 1, so, mode - 1 = tones
            modulation = 0
            if isinstance(self._scale, list) and len(self._scale) == 12:
                while tones > 0:
                    modulation += 1
                    if self._scale[modulation % 12]:
                        tones -= 1
            if modulation != 0:
                for key_i in range(12):
                    modulated_scale[key_i] = self._scale[(key_i + modulation) % 12]
        self._scale = modulated_scale
        return self
    
    def transpose(self, semitones: int = 7) -> Self:
        if isinstance(self._scale, list) and len(self._scale) == 12:
            transposed_scale: list[int] = self._scale.copy()
            for key_i in range(12):
                transposed_scale[(key_i + semitones) % 12] = self._scale[key_i]
            self._scale = transposed_scale
        return self
    

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Scale():
                super().__lshift__(operand)
                self._scale = operand._scale.copy()
            case od.Pipe():
                match operand._data:
                    case list():            self._scale = operand._data
                    case _:                 super().__lshift__(operand)
            case od.Serialization():
                self.loadSerialization(operand % od.Pipe( dict() ))
            case str():
                self_scale = __class__.get_scale(operand)
                if len(self_scale) == 12:
                    self._scale = self_scale.copy()
            case list():
                if len(operand) == 12 and all(x in {0, 1} for x in operand) and any(x == 1 for x in operand):
                    self._scale = operand.copy()
                elif operand == []:
                    self._scale = []
            case None:
                self._scale = []
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

    @staticmethod
    def get_tonic_key(scale: list[int]) -> int:
        return Scale._tonics[ max(0, Scale.get_scale_number( scale )) ]

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
    """`Generic -> Staff`

    A `Staff` is one of the most important `Operands` it works as the root for tempo and time values configurations for \
        `Composition` operands like `Clip` and `Song`.

    Parameters
    ----------
    Tempo(120), int, float : The typical tempo measured in BPM, Beats Per Minute.
    TimeSignature(4, 4) : Represents the typical Time Signature of a staff.
    Quantization(1/16) : This sets the Duration of a single `Step`, so, it works like a finer resolution than the `Beat`.
    KeySignature() : Follows the Circle of Fifths with the setting of the amount of `Sharps` or `Flats`.
    Scale(None) : Sets the `Scale` of the `Staff`, by default it has no scale and thus it uses the `KeySignature` instead.
    """
    def __init__(self, *parameters):
        super().__init__()
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._tempo: Fraction                       = Fraction(120)
        self._time_signature: TimeSignature         = TimeSignature(4, 4)
        self._quantization: Fraction                = Fraction(1/16)
        # Key Signature is an alias of Sharps and Flats of a Scale
        self._key_signature: ou.KeySignature        = ou.KeySignature()

        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

        # Volatile variable not intended to be user defined
        # channel_pitch, position_off, note_off
        self._tied_notes: dict[int, dict[str, any]] = {}
        self._stacked_notes: dict[float | Fraction, # note on time
                                  dict[int,             # status byte
                                       set[int]             # set of pitches
                                  ]
                            ] = {}

    # For Playlist Notes list
    def _reset_tied_notes(self) -> Self:
        self._tied_notes = {}
        return self

    def _tie_note(self, channel_pitch: int,
                  position_on: Fraction, position_off: Fraction, note_off: dict,
                  extend_note: Callable[[dict, Fraction, Fraction], None]) -> bool:
        
        if channel_pitch in self._tied_notes:
            if self._tied_notes[channel_pitch]["position_off"] == position_on:
                # The Note is already in the sequence to be tied (extended)
                self._tied_notes[channel_pitch]["position_off"] = position_off
                extend_note(
                    self._tied_notes[channel_pitch]["note_off"],
                    self._tied_notes[channel_pitch]["position_on"],
                    position_off
                )
                return True # It was Tied
        # Any previous note becomes history
        self._tied_notes[channel_pitch] = {
            "position_on": position_on,
            "position_off": position_off,
            "note_off": note_off
        }
        return False


    # Checks for stacked notes
    def _stack_note(self, note_on: float | Fraction, channel_byte: int, pitch: int) -> bool:
        if self is not defaults._staff: # defaults's staff remains clean
            if note_on not in self._stacked_notes:
                self._stacked_notes[note_on] = {
                    channel_byte: {
                        pitch: set( [pitch] )
                    }
                }
            elif channel_byte not in self._stacked_notes[note_on]:
                self._stacked_notes[note_on][channel_byte] = {
                    pitch: set( [pitch] )
                }
            elif pitch not in self._stacked_notes[note_on][channel_byte]:
                self._stacked_notes[note_on][channel_byte][pitch] = set( [pitch] )
            elif pitch not in self._stacked_notes[note_on][channel_byte][pitch]:
                self._stacked_notes[note_on][channel_byte][pitch].add( pitch )
            else:   # It's an Overlapping note
                return False
        return True

    def _reset_stacked_notes(self) -> Self:
        self._stacked_notes = {}
        return self

    def reset(self, *parameters) -> Self:
        super().reset()
        
        # Needs to be reset because shallow_copy doesn't result in different
        # staff references for each element
        self._reset_tied_notes()
        self._reset_stacked_notes()

        return self << parameters
    
    
    def convert_time_to_measures(self, minutes: int = 0, seconds: int = 0) -> int:
        actual_bps: Fraction = self._tempo / 60 # Beats Per Second
        time_seconds: int = 60 * minutes + seconds
        beats_per_measure: int = self._time_signature._top
        total_beats: Fraction = time_seconds * actual_bps
        total_measures: int = int(total_beats / beats_per_measure)
        return total_measures


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
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ra.Tempo():            return ra.Tempo(self._tempo)
                    case TimeSignature():       return self._time_signature
                    case ra.Quantization():     return ra.Quantization(self._quantization)
                    case ou.KeySignature():     return self._key_signature
                    case ra.BeatsPerMeasure():  return self._time_signature % od.Pipe( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.Pipe( ra.BeatNoteValue() )
                    # Calculated Values
                    case ra.NotesPerMeasure():
                        return self._time_signature % od.Pipe( ra.NotesPerMeasure() )
                    case ra.StepsPerNote():
                        return ra.StepsPerNote() << od.Pipe( 1 / self._quantization )
                    case ra.StepsPerMeasure():
                        return ra.StepsPerMeasure() \
                            << od.Pipe( self % od.Pipe( ra.StepsPerNote() ) % od.Pipe( Fraction() ) \
                                * (self % od.Pipe( ra.NotesPerMeasure() ) % od.Pipe( Fraction() )))
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            # Direct Values
            case of.Frame():            return self % od.Pipe( operand._data )
            case ra.Tempo():            return ra.Tempo(self._tempo)
            case TimeSignature():       return self._time_signature.copy()
            case ra.Quantization():     return ra.Quantization(self._quantization)
            case ou.KeySignature():     return self._key_signature.copy()
            case ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats():
                                        return self._key_signature % operand
            case ra.BeatsPerMeasure():  return self._time_signature % ra.BeatsPerMeasure()
            case ra.BeatNoteValue():    return self._time_signature % ra.BeatNoteValue()
            # Calculated Values
            case ou.Tonic():
                return ou.Tonic( self._key_signature.get_tonic_key() )
            case ou.Key():
                return self._key_signature % ou.Key()
            case list():
                return self._key_signature.get_scale_list() # Faster this way
            case float():
                return self._key_signature % float()
            case str():
                return self._key_signature % str()
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
        other ^= self    # Processes the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        if isinstance(other, od.Conditional):
            return other == self
        return  self._tempo             == other._tempo \
            and self._time_signature    == other._time_signature \
            and self._quantization      == other._quantization \
            and self._key_signature     == other._key_signature

    def convertToBeats(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ra.Beats':
        match time:
            case ra.Beats() | ra.Measurement():
                time_staff: Staff = time._get_staff(self)
                # By default Time values have no Staff reference,
                # so, they aren't transformed, just converted !!
                if time_staff._tempo == self._tempo:
                    return ra.Beats(time._rational)._set_staff_reference(self)
                # beats_b / tempo_b = beats_a / tempo_a => beats_b = beats_a * tempo_b / tempo_a
                beats_a: Fraction = time._rational
                tempo_a: Fraction = time._staff_reference._tempo
                tempo_b: Fraction = self._tempo
                beats_b: Fraction = beats_a * tempo_b / tempo_a
                return ra.Beats(beats_b)._set_staff_reference(self)
            case ra.Duration(): # The most internally called option
                time_staff: Staff = time._get_staff(self)
                beats_per_note: int = time_staff._time_signature._bottom
                beats: Fraction = time._rational * beats_per_note
                return ra.Beats(beats)._set_staff_reference(self)
            case ra.Measures():
                time_staff: Staff = time._get_staff(self)
                beats_per_measure: int = time_staff._time_signature._top
                beats: Fraction = time._rational * beats_per_measure
                return ra.Beats(beats)._set_staff_reference(self)
            case ra.Steps():
                time_staff: Staff = time._get_staff(self)
                beats_per_note: int = time_staff._time_signature._bottom
                notes_per_step: Fraction = time_staff._quantization
                beats_per_step: Fraction = beats_per_note * notes_per_step
                beats: Fraction = time._rational * beats_per_step
                return ra.Beats(beats)._set_staff_reference(self)
            case ou.Measure():
                time_staff: Staff = time._get_staff(self)
                return self.convertToBeats(
                    ra.Measures(time._unit)._set_staff_reference(time_staff)
                )
            case ou.Beat():
                time_staff: Staff = time._get_staff(self)
                return self.convertToBeats(
                    ra.Beats(time._unit)._set_staff_reference(time_staff)
                )
            case ou.Step():
                time_staff: Staff = time._get_staff(self)
                return self.convertToBeats(
                    ra.Steps(time._unit)._set_staff_reference(time_staff)
                )
            case float() | int() | Fraction():
                return self.convertToBeats(ra.Measures(time))
        return ra.Beats()._set_staff_reference(self)

    def convertToMeasures(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ra.Measures':
        time_beats: ra.Beats = self.convertToBeats(time)
        beats_per_measure: int = self._time_signature._top
        measures: Fraction = time_beats._rational / beats_per_measure
        return ra.Measures(measures)._set_staff_reference(self)


    def convertToSteps(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ra.Steps':
        time_beats: ra.Beats = self.convertToBeats(time)
        beats_per_note: int = self._time_signature._bottom
        notes_per_step: Fraction = self._quantization
        beats_per_step: Fraction = beats_per_note * notes_per_step
        steps: Fraction = time_beats._rational / beats_per_step
        return ra.Steps(steps)._set_staff_reference(self)

    def convertToDuration(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ra.Duration':
        time_beats: ra.Beats = self.convertToBeats(time)
        beats_per_note: int = self._time_signature._bottom
        duration: Fraction = time_beats._rational / beats_per_note
        return ra.Duration(duration)._set_staff_reference(self)

    def convertToMeasure(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ou.Measure':
        if isinstance(time, ra.Measurement):
            time = time.roundMeasures()
        return ou.Measure( self.convertToMeasures(time)._rational )._set_staff_reference(self)

    def convertToBeat(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ou.Beat':
        if isinstance(time, ra.Measurement):
            time = time.roundBeats()
        absolute_beat: int = self.convertToBeats(time) % int()
        beats_per_measure: int = self._time_signature._top
        relative_beat: int = absolute_beat % beats_per_measure
        return ou.Beat(relative_beat)._set_staff_reference(self)

    def convertToStep(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ou.Step':
        if isinstance(time, ra.Measurement):
            time = time.roundSteps()
        absolute_step: int = self.convertToSteps(time) % int()
        beats_per_measure: int = self._time_signature._top
        beats_per_note: int = self._time_signature._bottom
        notes_per_step: Fraction = self._quantization
        beats_per_step: Fraction = beats_per_note * notes_per_step
        steps_per_measure: int = int(beats_per_measure / beats_per_step)
        relative_step: int = absolute_step % steps_per_measure
        return ou.Step(relative_step)._set_staff_reference(self)

    def convertToPosition(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ra.Position':
        time_beats: ra.Beats = self.convertToBeats(time)
        return ra.Position(time_beats)._set_staff_reference(self)

    def convertToLength(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> 'ra.Length':
        time_beats: ra.Beats = self.convertToBeats(time)
        return ra.Length(time_beats)._set_staff_reference(self)


    def getMinutes(self, time: Union['ra.Convertible', 'ou.TimeUnit', float, int, Fraction] = None) -> Fraction:
        time_beats: ra.Beats = self.convertToBeats(time)
        return time_beats._rational / self._tempo

    def getPlaylist(self, position: 'ra.Position' = None) -> list[dict]:
        if position is None:
            return [{ "time_ms": 0.0 }]
        return [{ "time_ms": o.minutes_to_time_ms(self.getMinutes(position)) }]


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tempo"]            = self.serialize( self._tempo )
        serialization["parameters"]["time_signature"]   = self.serialize( self._time_signature )
        serialization["parameters"]["quantization"]     = self.serialize( self._quantization )
        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Staff':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tempo" in serialization["parameters"] and "time_signature" in serialization["parameters"] and
            "key_signature" in serialization["parameters"] and "quantization" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempo             = self.deserialize( serialization["parameters"]["tempo"] )
            self._time_signature    = self.deserialize( serialization["parameters"]["time_signature"] )
            self._quantization      = self.deserialize( serialization["parameters"]["quantization"] )
            self._key_signature     = self.deserialize( serialization["parameters"]["key_signature"] )
        return self
    
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Staff():
                super().__lshift__(operand)
                self._tempo             = operand._tempo
                self._time_signature    << operand._time_signature
                self._quantization      = operand._quantization
                self._key_signature     << operand._key_signature
            case od.Pipe():
                match operand._data:
                    case ra.Tempo():            self._tempo = operand._data._rational
                    case TimeSignature():       self._time_signature = operand._data
                    case ra.Quantization():     self._quantization = operand._data._rational
                    case ou.KeySignature():     self._key_signature = operand._data
                    case ra.TimeSignatureParameter():
                                                self._time_signature << od.Pipe( operand._data )
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Tempo():            self._tempo = operand._rational
            case TimeSignature() | ra.TimeSignatureParameter():
                                        self._time_signature << operand
            case ra.Quantization():     self._quantization = operand._rational
            # case Scale():               self._scale << operand
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

    def __iadd__(self, operand: any) -> Self:
        match operand:
            case ra.Tempo():
                self._tempo += operand._rational
                return self
        return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        match operand:
            case ra.Tempo():
                self._tempo -= operand._rational
                return self
        return super().__isub__(operand)


class Arpeggio(Generic):
    """`Generic -> Arpeggio`

    An `Arpeggio` lets a group of simultaneously played notes to be played in sequence accordingly to the Arpeggio configuration.

    Parameters
    ----------
    Order(1), int : The notes changing order, with 1 being the "Up" order.
    Duration(1/16), float : The duration after which the next note is played following the set `Order`.
    Swing(0.5) : Sets the amount of time the note is effectively pressed relatively to its total duration.
    Chaos(SinX()) : For the `Order` 5, "Chaotic", it uses the set Chaotic `Operand`.
    """
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
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ou.Order():            return operand._data << od.Pipe( self._order )
                    case ra.Duration():         return operand._data << od.Pipe( self._duration_notevalue )
                    case ra.Swing():            return operand._data << od.Pipe( self._swing )
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
            target_picks.append(source_picks.pop(self._chaos @ 1 % int() % len(source_picks)))

        shuffled_list = []
        for pick in target_picks:
            shuffled_list.append(list[pick])

        return shuffled_list

    if TYPE_CHECKING:
        from operand_element import Note

    def _generate_sequence(self, notes: list['Note']) -> list['Note']:
        """Generates the sequence of the arpeggio order."""
        match ou.Order.numberToName( self._order ):
            case "Up":
                return notes
            case "Down":
                return notes[::-1]
            case "UpDown":
                return notes + notes[-2:0:-1]  # Ascend then descend
            case "DownUp":
                return notes[::-1] + notes[1:-1]  # Descend then ascend
            case "Chaotic":
                return self._shuffle_list(notes)
            case _:
                return notes  # Default to "Up"

    def arpeggiate(self, notes: list['Note']) -> list['Note']:
        from operand_element import Note

        if self._order > 0 and len(notes) > 0:

            note_staff: Staff = notes[0]._get_staff()
            note_start_position: ra.Position = notes[0] % od.Pipe( ra.Position() )
            arpeggio_length: ra.Length = notes[0] % od.Pipe( ra.Length() )
            arpeggio_end_position: ra.Position = arpeggio_length.convertToPosition()
            note_length: ra.Length = note_staff.convertToLength(ra.Duration(self._duration_notevalue))
            odd_length: ra.Length = note_length * 2 * self._swing
            even_length: ra.Length = note_length * 2 - odd_length
            
            sequenced_notes: list[Note] = self._generate_sequence(notes)
            arpeggiated_notes: list[Note] = []
            nth_note: int = 1
            while note_start_position < arpeggio_end_position:
                for source_note in sequenced_notes:
                    new_note: Note = source_note.copy()
                    arpeggiated_notes.append(new_note)
                    new_note << note_start_position
                    if nth_note % 2 == 1:   # Odd note
                        new_note << odd_length
                    else:
                        new_note << even_length
                    note_end_position: ra.Position = note_start_position + new_note % od.Pipe( ra.Length() )
                    if note_end_position > arpeggio_end_position:
                        length_deficit: ra.Length = arpeggio_length - arpeggio_end_position
                        new_note += length_deficit
                        break
                    note_start_position = note_end_position
                    nth_note += 1
            return arpeggiated_notes

        return notes

    def arpeggiate_source(self, notes: list['Note'], start_position: ra.Position, arpeggio_length: ra.Length) -> list['Note']:
        from operand_element import Note

        if self._order > 0 and len(notes) > 0:

            note_start_position: ra.Position = start_position
            total_notes: int = len(notes)
            note_length: ra.Length = arpeggio_length / total_notes
            odd_length: ra.Length = note_length * 2 * self._swing
            even_length: ra.Length = note_length * 2 - odd_length
            
            sequenced_notes: list[Note] = self._generate_sequence(notes)
            nth_note: int = 1
            for note_i in range(total_notes):
                notes[note_i] = sequenced_notes[note_i]
                notes[note_i] << note_start_position
                if nth_note % 2 == 1:   # Odd note
                    notes[note_i] << odd_length
                else:
                    notes[note_i] << even_length
                note_start_position += notes[note_i] % od.Pipe( ra.Length() )
                nth_note += 1

        return notes

    def __eq__(self, other: 'Arpeggio') -> bool:
        other ^= self    # Processes the Frame operand if any exists
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
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Arpeggio():
                super().__lshift__(operand)
                self._order                 = operand._order
                self._duration_notevalue    = operand._duration_notevalue
                self._swing                 = operand._swing
                self._chaos                 << operand._chaos
            case od.Pipe():
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
        self._chaos @ number
        self._index += self.convert_to_int(number)    # keeps track of each iteration
        return self


class Defaults(Generic):
    """`Generic -> Defaults`

    The `Defaults` operand is declared as the variable `defaults` and is available right away, \
        this variable concentrates the total variables that set the `defaults` of each newly created `Operand`.
    The `defaults` variable parameters can be changes at any time but they only set the newly created operands and these \
        changes have no impact on already created operands.

    Parameters
    ----------
    Staff(), int, float, Fraction, str : It keeps its own global `Staff` that will be used by `Element` and `Clip` at their creation.
    Duration(1/4) : The default note `Element` duration is 1/4 note.
    Octave(4) : The default `Octave` is the 4th relative to the middle C.
    Velocity(100) : Sets the default velocity of a `Note` as 100.
    Controller("Pan") : The default controller being controlled by CC midi messages is the "Pan", CC number 10.
    Channel(1) : The default `Channel is the midi channel 1.
    Devices(["Microsoft", "FLUID", "Apple"]) : Devices that are used by default in order of trying to connect by the `JsonMidiPlayer`.
    ClockedDevices([]) : By default no devices are set to receive clocking messages.
    PPQN(24) : The default for clocking midi messages is 24 Pulses Per Quarter Note.
    ClockStopModes(0) : The default clock stop mode is the one that sends a song position signal back to 0.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._staff: Staff                          = Staff()
        self._duration: Fraction                    = Fraction(1/4)
        self._octave: int                           = 4
        self._velocity: int                         = 100
        self._controller: Controller                = Controller("Pan")
        self._channel: int                          = 1
        self._devices: list[str]                    = ["Microsoft", "FLUID", "Apple"]
        self._clocked_devices: list[str]            = []
        self._clock_ppqn: int                       = 24
        self._clock_stop_mode: int                  = 0
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        import operand_element as oe
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case Staff():               return self._staff
                    case ra.StaffParameter() | ou.KeySignature() | TimeSignature() \
                        | Scale() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                        | int() | float() | Fraction() | str():
                                                return self._staff % od.Pipe( operand._data )
                    case ra.Duration():         return operand << self._duration
                    case ou.Octave():           return ou.Octave(self._octave)
                    case ou.Velocity():         return ou.Velocity(self._velocity)
                    case Controller():          return self._controller
                    case ou.Channel():          return ou.Channel(self._channel)
                    case oc.ClockedDevices():   return oc.ClockedDevices(self._clocked_devices)
                    case oc.Devices():          return oc.Devices(self._devices)
                    case ou.PPQN():             return ou.PPQN(self._clock_ppqn)
                    case ou.ClockStopModes():   return ou.ClockStopModes(self._clock_stop_mode)
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case Staff():               return self._staff.copy()
            case ra.StaffParameter() | ou.KeySignature() | TimeSignature() \
                | Scale() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | int() | float() | Fraction() | str():
                                        return self._staff % operand
            case ra.Duration():         return operand.copy() << self._duration
            case ou.Octave():           return ou.Octave(self._octave)
            case ou.Velocity():         return ou.Velocity(self._velocity)
            case Controller():          return self._controller.copy()
            case ou.Number():           return self._controller % ou.Number()
            case ou.Value():            return ou.Number.getDefaultValue(self % ou.Number() % int())
            case ou.Channel():          return ou.Channel(self._channel)
            case oc.ClockedDevices():   return oc.ClockedDevices(self._clocked_devices)
            case oc.Devices():          return oc.Devices(self._devices)
            case ou.PPQN():             return ou.PPQN(self._clock_ppqn)
            case ou.ClockStopModes():   return ou.ClockStopModes(self._clock_stop_mode)
            case oe.Clock():            return oe.Clock(self % oc.ClockedDevices(), self % ou.PPQN(), self % ou.ClockStopModes())
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Defaults') -> bool:
        other ^= self    # Processes the Frame operand if any exists
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
            and self._devices           == other._devices \
            and self._clocked_devices   == other._clocked_devices \
            and self._clock_ppqn        == other._clock_ppqn \
            and self._clock_stop_mode   == other._clock_stop_mode
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["staff"]            = self.serialize( self._staff )
        serialization["parameters"]["duration"]         = self.serialize( self._duration )
        serialization["parameters"]["octave"]           = self.serialize( self._octave )
        serialization["parameters"]["velocity"]         = self.serialize( self._velocity )
        serialization["parameters"]["controller"]       = self.serialize( self._controller )
        serialization["parameters"]["channel"]          = self.serialize( self._channel )
        serialization["parameters"]["devices"]          = self.serialize( self._devices )
        serialization["parameters"]["clocked_devices"]  = self.serialize( self._clocked_devices )
        serialization["parameters"]["clock_ppqn"]       = self.serialize( self._clock_ppqn )
        serialization["parameters"]["clock_stop_mode"]  = self.serialize( self._clock_stop_mode )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "staff" in serialization["parameters"] and "duration" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "velocity" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "devices" in serialization["parameters"] and
            "clocked_devices" in serialization["parameters"] and "clock_ppqn" in serialization["parameters"] and "clock_stop_mode" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._staff             = self.deserialize( serialization["parameters"]["staff"] )
            self._duration          = self.deserialize( serialization["parameters"]["duration"] )
            self._octave            = self.deserialize( serialization["parameters"]["octave"] )
            self._velocity          = self.deserialize( serialization["parameters"]["velocity"] )
            self._controller        = self.deserialize( serialization["parameters"]["controller"] )
            self._channel           = self.deserialize( serialization["parameters"]["channel"] )
            self._devices           = self.deserialize( serialization["parameters"]["devices"] )
            self._clocked_devices   = self.deserialize( serialization["parameters"]["clocked_devices"] )
            self._clock_ppqn        = self.deserialize( serialization["parameters"]["clock_ppqn"] )
            self._clock_stop_mode   = self.deserialize( serialization["parameters"]["clock_stop_mode"] )
        return self
    
    def __lshift__(self, operand: any) -> Self:
        import operand_element as oe
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Defaults():
                super().__lshift__(operand)
                self._staff             << operand._staff
                self._duration          = operand._duration
                self._octave            = operand._octave
                self._velocity          = operand._velocity
                self._controller        << operand._controller
                self._channel           = operand._channel
                self._devices           = operand._devices.copy()
                self._clocked_devices   = operand._clocked_devices.copy()
                self._clock_ppqn        = operand._clock_ppqn
                self._clock_stop_mode   = operand._clock_stop_mode
            case od.Pipe():
                match operand._data:
                    case Staff():               self._staff = operand._data
                    case ra.Duration():         self._duration = operand._data._rational
                    case ou.Octave():           self._octave = operand._data._unit
                    case ou.Velocity():         self._velocity = operand._data._unit
                    case Controller():          self._controller = operand._data
                    case ou.Channel():          self._channel = operand._data._unit
                    case oc.ClockedDevices():   self._clocked_devices = operand._data % od.Pipe( list() )
                    case oc.Devices():          self._devices = operand._data % od.Pipe( list() )
                    case ou.PPQN():             self._clock_ppqn = operand._data._unit
                    case ou.ClockStopModes():   self._clock_stop_mode = operand._data._unit
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.StaffParameter() | ou.KeySignature() | TimeSignature() \
                | Scale() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | int() | float() | Fraction() | str():
                                        self._staff << operand
            case ra.Duration():         self._duration = operand._rational
            case ou.Octave():           self._octave = operand._unit
            case ou.Velocity():         self._velocity = operand._unit
            case Controller() | ou.Number():
                                        self._controller << operand
            case ou.Channel():          self._channel = operand._unit
            case oc.ClockedDevices():   self._clocked_devices = operand % list()
            case oc.Devices():          self._devices = operand % list()
            case od.Device():           self._devices = oc.Devices(self._devices, operand) % od.Pipe( list() )
            case ou.PPQN():             self._clock_ppqn = operand._unit
            case ou.ClockStopModes():   self._clock_stop_mode = operand._unit
            case oe.Clock():
                self << ( operand % oc.ClockedDevices(), operand % ou.PPQN(), operand % ou.ClockStopModes() )
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    
    def __iadd__(self, operand: any) -> Self:
        match operand:
            case od.Device():
                if isinstance(operand._data, str):
                    self_devices = self % od.Pipe( oc.Devices() )
                    self_devices += operand
                    self._devices = self_devices % od.Pipe( list() )
                return self
            case ra.Tempo():
                self._staff += operand
                return self
        return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        match operand:
            case od.Device():
                self_devices = self % od.Pipe( oc.Devices() )
                self_devices -= operand
                self._devices = self_devices % od.Pipe( list() )
                return self
            case ra.Tempo():
                self._staff -= operand
                return self
        return super().__isub__(operand)


# Instantiate the Global Defaults here.
defaults: Defaults = Defaults()


