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
    KeySignature(settings) : Follows the Circle of Fifths with the setting of the amount of `Sharps` or `Flats`.
    Tonic(settings), None : The tonic key on which the `Degree` is based on.
    Octave(4) : The octave on the keyboard with the middle C setting on the 4th octave.
    Degree(1), int : Degree sets the position of a note on a `Scale`, with designations like tonic, supertonic and dominant.
    Sharp(0), Flat : `Sharp` and `Flat` sets the respective accidental of a given note.
    Natural(False) : `Natural` disables the effects of `Sharp` and `Flat` and any accidental.
    list([]), Scale(), str, None : Sets the `Scale` to be used, `None` or `[]` uses the staff `KeySignature`.
    bool(True) : Sets if the given scale is processed as transposition (True) or as modulation (False).
    """
    def __init__(self, *parameters):
        self._key_signature: ou.KeySignature \
                                        = settings % ou.KeySignature()
        self._tonic_key: int            = settings % ou.Key() % int()
        self._octave_0: int             = 5     # By default it's the 4th Octave, that's 5 in 0 based!
        self._degree_0: float           = 0.0   # By default it's Degree 1, that's 0 in 0 based
        self._transposition: int        = 0     # By default it's it has no scale transposition
        self._sharp: int                = 0     # By default not a Sharp or Flat
        self._natural: bool             = False
        self._scale: list[int]          = []
        super().__init__(*parameters)


    def sharp(self, unit: bool = True) -> Self:
        return self << ou.Sharp(unit)

    def flat(self, unit: bool = True) -> Self:
        return self << ou.Flat(unit)

    def natural(self, unit: bool = True) -> Self:
        return self << ou.Natural(unit)

    def degree(self, unit: int = 1) -> Self:
        return self << ou.Degree(unit)


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
        Midi octaves start at -1, but octave_0 already has + 1
        """
        return 12 * self._octave_0

    def degree_transposition(self) -> int:
        """
        Based on the Key Signature, this method gives the degree transposition
        """
        if self._degree_0 != 0: # Optimization
            tonic_scale: list[int] = self._key_signature.get_scale_list()
            """
            IN A TRANSPOSITION SCALE ACCIDENTALS **ARE** SUPPOSED TO HAPPEN
            """
            return Scale.transpose_key(round(self._degree_0), tonic_scale)
        return 0

    def scale_transposition(self, degree_transposition: int) -> int:
        """
        Processes the transposition of the Key Signature if no Scale is set.
        """
        if self._transposition != 0:
            if self._scale:
                return Scale.transpose_key(self._transposition, self._scale)
            else:   # For KeySignature the Modulation is treated as a degree_0
                """
                Because in this case the transposition is no more than a degree increase,
                the tonic_offset is 0 for the new calculated degree
                """
                degree_0: float = round(self._degree_0) + self._transposition
                tonic_scale: list[int] = self._key_signature.get_scale_list()
                return Scale.transpose_key(degree_0, tonic_scale) - degree_transposition
        return 0

    def chromatic_transposition(self) -> int:
        degree_int: int = round(self._degree_0)
        semitones: int = round((self._degree_0 - degree_int) * 10)
        if semitones % 2:  # Odd - same direction, same sign
            semitones = (semitones // 2) + (1 if semitones > 0 else -1)
        else:  # Even - inverse sign
            semitones = semitones // (-2)
        return semitones

    def accidentals_transposition(self, key: int) -> int:
        """
        Processes the given set sharps and natural accordingly as final decorators.
        """
        transposition: int = 0
        # Final parameter decorators like Sharp and Natural
        if self._natural:
            if self._major_scale[(key + transposition) % 12] == 0:  # Black key
                accidentals_int: int = self._key_signature._unit
                if accidentals_int < 0:
                    transposition += 1  # Considered a flat
                else:
                    transposition -= 1  # Considered a sharp
        elif self._sharp != 0:
            if self._major_scale[(key + transposition) % 12] == 1:  # White key
                transposition += self._sharp  # applies Pitch self accidentals
        return transposition

    def tonic_int(self) -> int:
        """
        This method simple does a % 12 on the tonic key.
        """
        return self._tonic_key % 12 # It may represent a flat, meaning, may be above 12

    def root_int(self) -> int:
        """
        Gets the root key int from the tonic_key.
        """
        tonic_int: int = self._tonic_key % 12   # It may represent a flat, meaning, may be above 12
        degree_transposition: int = self.degree_transposition()
        return tonic_int + degree_transposition

    def root_key(self) -> int:
        """
        root_key takes into consideration the tonic gross value above 11.
        """
        root_int: int = self.root_int()
        root_key: int = root_int + self._tonic_key // 12 * 12  # key_line * total_keys
        return root_key

    def scale_int(self) -> int:
        """
        The target key int after all processing **excluding** accidentals.
        """
        tonic_int: int = self._tonic_key % 12   # It may represent a flat, meaning, may be above 12
        degree_transposition: int = self.degree_transposition()
        scale_transposition: int = self.scale_transposition(degree_transposition)
        return tonic_int + degree_transposition + scale_transposition

    def chromatic_int(self) -> int:
        """
        The configured Degree chromatic transposition in the float number.
        """
        tonic_int: int = self._tonic_key % 12   # It may represent a flat, meaning, may be above 12
        degree_transposition: int = self.degree_transposition()
        scale_transposition: int = self.scale_transposition(degree_transposition)
        chromatic_transposition: int = self.chromatic_transposition()
        return tonic_int + degree_transposition + scale_transposition + chromatic_transposition

    def pitch_int(self) -> int:
        """
        The final chromatic conversion of the tonic_key into the midi pitch with accidentals.
        """
        chromatic_int: int = self.chromatic_int()

        accidentals_transposition: int = self.accidentals_transposition(chromatic_int)
        octave_transposition: int = self.octave_transposition()
        return chromatic_int + accidentals_transposition + octave_transposition

    """
    Auxiliary methods to get specific data directly
    """

    def increment_tonic(self, keys: int) -> Self:
        """
        Increments the tonic key by preserving the tonic in the Key Signature range
        by changing the octave accordingly.
        """
        gross_tonic_key: int = self._tonic_key % 12 + keys
        self._tonic_key = gross_tonic_key % 12 + self._tonic_key // 12 * 12  # key_line * total_keys
        self._octave_0 += gross_tonic_key // 12
        # There is still the need to match the Octave for the existing transpositions
        return self.match_octave()


    def match_octave(self, move_octave = True) -> Self:
        """
        This method makes sure the Degree and Transposition pitches match the same Octave
        while making degree_key and scale_key being in the same octave as tonic_int.
        """
        # Matches the Degree firstly
        degree_transposition: int = self.degree_transposition()
        if degree_transposition != 0:   # Optimization
            tonic_int: int = self._tonic_key % 12
            # tonic_int is used as octave reference to the root_int octave matching
            degree_key: int = tonic_int + degree_transposition
            octave_offset: int = degree_key // 12
            self._degree_0 -= octave_offset * 7 # Offsets degree to negative
            degree_transposition -= octave_offset * 12  # Offsets transposition too
            if move_octave:
                self._octave_0 += octave_offset     # matches the Octave with the new Degree
        # Matches the Transposition secondly
        scale_transposition: int = self.scale_transposition(degree_transposition)
        if scale_transposition != 0:    # Optimization
            # Because a pitch scale may not be a diatonic scale (7 degrees)!
            if self._scale:
                scale_degrees: int = sum(self._scale)
            else:
                scale_degrees: int = 7  # Diatonic scales
            tonic_int: int = self._tonic_key % 12
            root_int: int = tonic_int + degree_transposition
            # root_int is used as octave reference to the scale_int octave matching
            scale_key: int = root_int + scale_transposition
            octave_offset: int = scale_key // 12
            self._transposition -= octave_offset * scale_degrees    # Offsets degree to negative
            if move_octave:
                self._octave_0 += octave_offset     # matches the Octave with the new Degree
        return self


    def get_key_degree_0(self, root_key: int) -> int:
        degree_0: int = 0
        
        tonic_int: int = self._tonic_key % 12
        keysignature_scale: list[int] = self._key_signature % list()

        # tonic_int goes UP and then DOWN (results in flat or natural)
        while tonic_int < root_key:
            degree_0 += keysignature_scale[ (root_key - tonic_int) % 12 ]
            tonic_int += 1
        while tonic_int > root_key:
            degree_0 -= keysignature_scale[ (root_key - tonic_int) % 12 ]
            tonic_int -= 1

        if keysignature_scale[ (root_key - self._tonic_key % 12) % 12 ] == 0:  # Key NOT on the scale
            if self._tonic_key // 12 == 1:  # Checks the tonic key line
                if self._tonic_key % 12 > root_key:
                    degree_0 -= 1
            else:
                if self._tonic_key % 12 < root_key:
                    degree_0 += 1

        # Sets the Degree as Positive
        degree_0 %= 7   # Diatonic scales

        return degree_0 # Degree base 0 (I)



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
                    case ou.KeySignature(): return self._key_signature
                    case ou.Octave():       return operand._data << od.Pipe(self._octave_0 - 1)
                    case ou.TonicKey():     return operand._data << od.Pipe(self._tonic_key)    # Must come before than Key()
                    case ou.Degree():       return operand._data << od.Pipe(self._degree_0 + 1)
                    case ou.Transposition():
                        return operand._data << od.Pipe(self._transposition)
                    case ou.Sharp():        return operand._data << od.Pipe(max(0, self._sharp))
                    case ou.Flat():         return operand._data << od.Pipe(max(0, self._sharp * -1))
                    case ou.Natural():      return operand._data << od.Pipe(self._natural)
                    case int():             return float(self._tonic_key)
                    case float():           return self._degree_0
                    case Fraction():        return Fraction(self._transposition)
                    case Scale():           return operand._data << od.Pipe(self._scale)
                    case list():            return self._scale
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % operand
            case ou.KeySignature():
                return self._key_signature.copy()
            
            case int():
                return self.pitch_int()
            case float():
                return float((self._degree_0 % 7) + 1)
            case Fraction():
                return Fraction(self._transposition)
            
            case ou.Semitone() | ou.RootKey():
                return operand.copy(self.pitch_int())
            
            case ou.TonicKey():    # Must come before than Key()
                return ou.TonicKey(self._tonic_key)
            case ou.RootKey():
                return ou.RootKey( self.root_key() )
            
            case ou.Octave():
                return ou.Octave(self._octave_0 - 1)
            
            case ou.Degree():
                return ou.Degree((self._degree_0 % 7) + 1)
            case ou.Transposition():
                return operand.copy(self._transposition)
             
            case ou.Sharp():
                target_pitch: int = self.pitch_int()
                if self._major_scale[target_pitch % 12] == 0:    # Black key
                    if self._key_signature._unit >= 0:
                        return ou.Sharp(1)
                return ou.Sharp(0)
            case ou.Flat():
                target_pitch: int = self.pitch_int()
                if self._major_scale[target_pitch % 12] == 0:    # Black key
                    if self._key_signature._unit < 0:
                        return ou.Flat(1)
                return ou.Flat(0)
            case ou.Natural():
                return ou.Natural() << od.Pipe(self._natural)
            
            case Scale():
                return Scale(self._scale)
            case list():
                return self._scale.copy()

            case ou.Quality():
                return self._key_signature % operand
            case ou.Key():
                self_pitch: int = self.pitch_int()
                key_note: int = self_pitch % 12
                key_line: int = self._tonic_key // 12
                if self._key_signature.is_enharmonic(self._tonic_key, key_note):
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
                return self.pitch_int() == other.pitch_int()
            case od.Conditional():
                return other == self
            case _:
                return self % other == other
        return False
    
    def __lt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Pitch():
                return self.pitch_int() < other.pitch_int()
            case int() | float() | ou.Degree() | ou.Octave():
                return self % other < other
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Pitch():
                return self.pitch_int() > other.pitch_int()
            case int() | float() | ou.Degree() | ou.Octave():
                return self % other > other
            case _:
                return super().__gt__(other)
        return False
    
    def getSerialization(self) -> dict:

        serialization = super().getSerialization()
        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
        serialization["parameters"]["tonic_key"]        = self.serialize( self._tonic_key )
        serialization["parameters"]["octave_0"]         = self.serialize( self._octave_0 )
        serialization["parameters"]["degree_0"]         = self.serialize( self._degree_0 )
        serialization["parameters"]["transposition"]    = self.serialize( self._transposition )
        serialization["parameters"]["sharp"]            = self.serialize( self._sharp )
        serialization["parameters"]["natural"]          = self.serialize( self._natural )
        serialization["parameters"]["scale"]            = self.serialize( self._scale )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key_signature" in serialization["parameters"] and "tonic_key" in serialization["parameters"] and "sharp" in serialization["parameters"] and
            "natural" in serialization["parameters"] and "degree_0" in serialization["parameters"] and "octave_0" in serialization["parameters"] and
            "transposition" in serialization["parameters"] and "scale" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._key_signature = self.deserialize( serialization["parameters"]["key_signature"] )
            self._tonic_key     = self.deserialize( serialization["parameters"]["tonic_key"] )
            self._octave_0      = self.deserialize( serialization["parameters"]["octave_0"] )
            self._degree_0      = self.deserialize( serialization["parameters"]["degree_0"] )
            self._transposition = self.deserialize( serialization["parameters"]["transposition"] )
            self._sharp         = self.deserialize( serialization["parameters"]["sharp"] )
            self._natural       = self.deserialize( serialization["parameters"]["natural"] )
            self._scale         = self.deserialize( serialization["parameters"]["scale"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_element as oe
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch():
                super().__lshift__(operand)
                self._key_signature         << operand._key_signature
                self._tonic_key             = operand._tonic_key
                self._octave_0              = operand._octave_0
                self._degree_0              = operand._degree_0
                self._transposition         = operand._transposition
                self._sharp                 = operand._sharp
                self._natural               = operand._natural
                self._scale                 = operand._scale.copy()
            case od.Pipe():
                match operand._data:
                    case ou.KeySignature():
                        self._key_signature = operand._data
                    case ou.TonicKey():    # Must come before than Key()
                        self._tonic_key = operand._data._unit
                    case ou.Octave():
                        self._octave_0 = operand._data._unit + 1    # Based 0 octave
                    case int():
                        self._tonic_key = operand._data
                    case Fraction():
                        self._transposition = int(operand._data)
                    case ou.Semitone():
                        self._tonic_key = operand._data._unit
                    case ou.Sharp():
                        self._sharp = operand._data._unit
                    case ou.Flat():
                        self._sharp = operand._data._unit * -1
                    case ou.Natural():
                        self._natural = operand._data.__mod__(od.Pipe( bool() ))
                    case ou.Transposition():
                        self._transposition = operand._data._unit
                    case Scale():
                        self._scale = operand._data._scale
                    case list():
                        self._scale = operand._data
                    case str():
                        self._sharp = \
                            ((operand._data).strip().lower().find("#") != -1) * 1 + \
                            ((operand._data).strip().lower().find("b") != -1) * -1
                        self._degree_0 = abs((self % od.Pipe( ou.Degree() ) << ou.Degree(operand._data))._unit) - 1 # 0 based
                        self._tonic_key = ou.Key(self._tonic_key, operand._data)._unit
                    case _:
                        super().__lshift__(operand)

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.KeySignature() | ou.Quality():
                self._key_signature << operand

            case int():
                # Starts by resetting non-linear parameters like sharps and flats (needed for simple transposition)
                self._natural = False
                self._sharp = 0
                # Now a basic tonic transposition of the tonic key works because degree and transposition are linear operations
                actual_pitch: int = self.pitch_int()
                pitch_offset: int = operand - actual_pitch
                self.increment_tonic(pitch_offset)

            case ou.Semitone():
                # Starts by resetting non-linear parameters like sharps and flats (needed for simple transposition)
                self._natural = False
                self._sharp = 0
                # Now a basic tonic transposition of the tonic key works because degree and transposition are linear operations
                actual_pitch: int = self.tonic_int()
                tonic_offset: int = operand._unit % 12 - actual_pitch
                self.increment_tonic(tonic_offset)

            case float():
                self << ou.Degree(operand)
            case Fraction():
                self << ou.Transposition(operand)
                    
            case ou.TonicKey():    # Must come before than Key()
                self._tonic_key = operand._unit % 24
            case ou.Octave():
                self._octave_0 = operand._unit + 1

            case ou.Key():
                self._sharp = 0
                self._natural = False
                self._degree_0 = self.get_key_degree_0(operand._unit % 12)

            case ou.Degree():
                # Has to work with increments to keep the same Octave and avoid induced Octave jumps
                previous_degree_0: int = self._degree_0 % 7
                if operand < 0:
                    self._degree_0 = 0  # Resets the degree to I
                    self._degree_0 -= previous_degree_0
                    self._octave_0 = 5  # Based 0 octave, so, 5 means 4th octave
                    self._sharp = 0
                    self._natural = False
                elif operand < 1:
                    # Changes only the chromatic transposition
                    self._degree_0 = round(self._degree_0) + operand % float()
                else:
                    new_degree_0: float = ((operand._unit + operand._semitones) - 1) % 7
                    self._degree_0 += new_degree_0 - previous_degree_0
                # There is still the need to match the Octave for the existing transpositions
                self.match_octave(False)    # Keep actual octave (False)
            
            case None:  # Works as a reset
                self._tonic_key = self._key_signature.get_tonic_key()
                self._degree_0 = 0  # Resets the degree to I
                self._octave_0 = 5  # Based 0 octave, so, 5 means 4th octave
                self._transposition = 0
                self._sharp = 0
                self._natural = False

            case ou.Transposition():
                # Has to work with increments to keep the same Octave and avoid induced Octave jumps
                # Because a pitch scale may not be a diatonic scale (7 degrees)!
                if self._scale:
                    scale_degrees: int = sum(self._scale)
                else:
                    scale_degrees: int = 7  # Diatonic scales
                previous_transposition: int = self._transposition % scale_degrees
                new_transposition: int = operand._unit % scale_degrees
                self._transposition += new_transposition - previous_transposition
                # There is still the need to match the Octave for the existing transpositions
                self.match_octave(False)    # Keep actual octave (False)

            case ou.RootKey():
                # Excludes the effect of purely decorative parameters
                self._natural = False
                self._sharp = 0
                root_offset: int = operand._unit - self.root_int()
                self.increment_tonic(root_offset)

            case dict():
                for octave, value in operand.items():
                    self << value << ou.Octave(octave)

            case ou.DrumKit():
                self._natural = False
                self._sharp = 0
                self << ou.Degree()     # Makes sure no Degree different of Tonic is in use
                self << operand % int() # Sets the key number regardless KeySignature or Scale!
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
                self._degree_0 = abs((self % ou.Degree() << operand)._unit) - 1 # 0 based
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
            case Pitch() | ou.Semitone():
                self += operand % int()
            case ou.Octave():
                self._octave_0 += operand._unit
            case int():
                actual_pitch: int = self.pitch_int()
                self << actual_pitch + operand
            case float():
                self += ou.Degree(operand)
            case Fraction():
                self += ou.Transposition(operand)
            case ou.Degree():
                self._degree_0 += operand._unit
                self.match_octave()
            case ou.Transposition():
                self._transposition += operand._unit
                self.match_octave()
            case ou.Key():
                self.increment_tonic(operand._unit)
            case dict():
                for octave, value in operand.items():
                    self += value
                    self += ou.Octave(octave)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Pitch() | ou.Semitone():
                self -= operand % int()
            case ou.Octave():
                self._octave_0 -= operand._unit
            case int():
                actual_pitch: int = self.pitch_int()
                self << actual_pitch - operand
            case float():
                self -= ou.Degree(operand)
            case Fraction():
                self -= ou.Transposition(operand)
            case ou.Degree():
                self._degree_0 -= operand._unit
                self.match_octave()
            case ou.Transposition():
                self._transposition -= operand._unit
                self.match_octave()
            case ou.Key():
                self.increment_tonic(-operand._unit)
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
                self_pitch: int = self.pitch_int()
                multiplied_int = self_pitch * operand
                new_keynote._tonic_key = multiplied_int % 12
                new_keynote._octave_0 = multiplied_int // 12
                return new_keynote
            case float():
                new_keynote = self.__class__()
                self_degree_0: int = self._degree_0
                multiplied_int = int(self_degree_0 * operand)
                new_keynote._tonic_key = multiplied_int % 12
                new_keynote._octave_0 = multiplied_int // 12
                return new_keynote
            case _:
                return super().__mul__(operand)
    
    def __div__(self, operand) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        if operand != 0:
            match operand:
                case int():
                    new_keynote = self.__class__()
                    self_pitch: int = self.pitch_int()
                    multiplied_int = int(self_pitch / operand)
                    new_keynote._tonic_key = multiplied_int % 12
                    new_keynote._octave_0 = multiplied_int // 12
                    return new_keynote
                case float():
                    new_keynote = self.__class__()
                    self_degree_0: int = self._degree_0
                    multiplied_int = int(self_degree_0 / operand)
                    new_keynote._tonic_key = multiplied_int % 12
                    new_keynote._octave_0 = multiplied_int // 12
                    return new_keynote
        return super().__div__(operand)


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
        scale_list: list[int] = self._key_signature % list()
        self_pitch: int = self.pitch_int()
        pitch_offset: int = 0
        if up:
            pitch_step: int = 1
        else:
            pitch_step: int = -1
        while scale_list[self_pitch + pitch_offset] == 0:
            pitch_offset += pitch_step
        if pitch_offset > 0:
            self += pitch_offset
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
        if len(scale) == 12 and sum(scale) > 0:
            while steps > 0:
                scale_transposition += 1
                steps -= scale[scale_transposition % 12]
            while steps < 0:
                scale_transposition -= 1
                steps += scale[scale_transposition % 12]
        return scale_transposition

    @staticmethod
    def modulate_key(tonic_offset: int = 0, degrees_0: int = 4, scale: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]) -> int:
        # The given scale shall always have a size of 12
        tonic_modulation: int = 0
        if len(scale) == 12 and sum(scale) > 0:
            while degrees_0 > 0:
                tonic_modulation += 1
                degrees_0 -= scale[ (tonic_offset + tonic_modulation) % 12 ]
            while degrees_0 < 0:
                tonic_modulation -= 1
                degrees_0 += scale[ (tonic_offset + tonic_modulation) % 12 ]
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
            case ou.TonicKey():            return ou.TonicKey( Scale.get_tonic_key(self._scale) )
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
        return sum(self._scale)

    def transposition(self, tones: int) -> int:        # Starting in C
        transposition = 0
        if isinstance(self._scale, list) and len(self._scale) == 12:
            modulated_scale: list[int] = self.modulation(None)
            while tones > 0:
                transposition += 1
                tones -= modulated_scale[transposition % 12]
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
                    tones -= self._scale[transposition % 12]
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
                    tones -= self._scale[modulation % 12]
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
    TimeSignature(4, 4) : Represents the typical Time Signature of a staff.
    """
    def __init__(self, *parameters):
        super().__init__()
        # Set Global Staff Settings at the end of this file bottom bellow
        self._time_signature: TimeSignature         = TimeSignature(4, 4)

        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    
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
                    case TimeSignature():       return self._time_signature
                    case ra.BeatsPerMeasure():  return self._time_signature % od.Pipe( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.Pipe( ra.BeatNoteValue() )
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case TimeSignature():       return self._time_signature.copy()
            case ra.Quantization():     return settings % operand
            case ra.BeatsPerMeasure():  return self._time_signature % ra.BeatsPerMeasure()
            case ra.BeatNoteValue():    return self._time_signature % ra.BeatNoteValue()
            case ra.NotesPerMeasure():
                return self._time_signature % ra.NotesPerMeasure()
            case ra.StepsPerNote():
                return ra.StepsPerNote() << 1 / settings._quantization
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
        return  self._time_signature    == other._time_signature


    def getPlaylist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        return [{ "time_ms": o.minutes_to_time_ms( settings.beats_to_minutes(position_beats) ) }]


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["time_signature"]   = self.serialize( self._time_signature )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Staff':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "time_signature" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._time_signature    = self.deserialize( serialization["parameters"]["time_signature"] )
        return self
    
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Staff():
                super().__lshift__(operand)
                self._time_signature << operand._time_signature
            case od.Pipe():
                match operand._data:
                    case TimeSignature():       self._time_signature = operand._data
                    case ra.TimeSignatureParameter():
                                                self._time_signature << od.Pipe( operand._data )
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case TimeSignature() | ra.TimeSignatureParameter():
                                        self._time_signature << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                super().__lshift__(operand)
        return self


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
            arpeggio_end_position: ra.Position = arpeggio_length % ra.Position()
            note_length: ra.Length = ra.Length(note_staff, self._duration_notevalue)
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


class Settings(Generic):
    """`Generic -> Settings`

    The `Settings` operand is declared as the variable `defaults` and is available right away, \
        this variable concentrates the total variables that set the `defaults` of each newly created `Operand`.
    The `defaults` variable parameters can be changes at any time but they only set the newly created operands and these \
        changes have no impact on already created operands.

    Parameters
    ----------
    Tempo(120), int, float : The typical tempo measured in BPM, Beats Per Minute.
    Quantization(1/16) : This sets the Duration of a single `Step`, so, it works like a finer resolution than the `Beat`.
    Staff(), int, float, Fraction, str : It keeps its own global `Staff` that will be used by `Element` and `Clip` at their creation.
    TimeSignature(4, 4) : Represents the typical Time Signature of a staff.
    KeySignature() : Follows the Circle of Fifths with the setting of the amount of `Sharps` or `Flats`.
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
        self._tempo: Fraction                       = Fraction(120)
        self._quantization: Fraction                = Fraction(1/16)
        self._staff: Staff                          = Staff()
        self._time_signature: TimeSignature         = TimeSignature(4, 4)
        self._key_signature: ou.KeySignature        = ou.KeySignature()
        self._duration: Fraction                    = Fraction(1)   # Means 1 beat
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
        actual_bps: Fraction = settings._tempo / 60 # Beats Per Second
        time_seconds: int = 60 * minutes + seconds
        beats_per_measure: int = self._staff._time_signature._top
        total_beats: Fraction = time_seconds * actual_bps
        total_measures: int = int(total_beats / beats_per_measure)
        return total_measures


    def beats_to_minutes(self, beats: Fraction) -> Fraction:
        return beats / self._tempo

    def __mod__(self, operand: o.T) -> o.T:
        import operand_element as oe
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ra.Tempo():            return ra.Tempo(self._tempo)
                    case ra.Quantization():     return operand._data << self._quantization
                    case ra.StepsPerNote():
                        return ra.StepsPerNote() << od.Pipe( 1 / self._quantization )
                    case Staff():               return self._staff
                    case TimeSignature():       return self._time_signature
                    case ra.BeatsPerMeasure():  return self._time_signature % od.Pipe( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.Pipe( ra.BeatNoteValue() )
                    case ou.KeySignature():     return self._key_signature
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
            case ra.Tempo():            return ra.Tempo(self._tempo)
            case ra.Quantization():     return operand.copy(self._quantization)
            case ra.StepsPerNote():
                return ra.StepsPerNote() << 1 / self._quantization
            case ra.StepsPerMeasure():
                return ra.StepsPerMeasure() \
                    << (self % ra.StepsPerNote() % Fraction()) * (self._staff % ra.NotesPerMeasure() % Fraction())
            case Staff():               return self._staff.copy()
            case ra.StaffParameter() | TimeSignature():
                                        return self._staff % operand
            case TimeSignature():       return self._time_signature.copy()
            case ra.BeatsPerMeasure():  return self._time_signature % ra.BeatsPerMeasure()
            case ra.BeatNoteValue():    return self._time_signature % ra.BeatNoteValue()
            case ra.NotesPerMeasure():  return self._time_signature % ra.NotesPerMeasure()
            case ou.KeySignature():     return self._key_signature.copy()
            case ou.Key() | ou.Quality() | int() | float() | Fraction() | str():
                                        return self._key_signature % operand
            # Calculated Values
            case list():
                return self._key_signature.get_scale_list() # Faster this way
            case ou.TonicKey():
                return ou.TonicKey( self._key_signature.get_tonic_key() )
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

    def __eq__(self, other: 'Settings') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        if isinstance(other, od.Conditional):
            return other == self
        return  self._tempo             == other._tempo \
            and self._quantization      == other._quantization \
            and self._staff             == other._staff \
            and self._time_signature    == other._time_signature \
            and self._key_signature     == other._key_signature \
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
        serialization["parameters"]["tempo"]            = self.serialize( self._tempo )
        serialization["parameters"]["quantization"]     = self.serialize( self._quantization )
        serialization["parameters"]["staff"]            = self.serialize( self._staff )
        serialization["parameters"]["time_signature"]   = self.serialize( self._time_signature )
        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
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
            "tempo" in serialization["parameters"] and "quantization" in serialization["parameters"] and "staff" in serialization["parameters"] and
            "time_signature" in serialization["parameters"] and "key_signature" in serialization["parameters"] and "duration" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "velocity" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "devices" in serialization["parameters"] and
            "clocked_devices" in serialization["parameters"] and "clock_ppqn" in serialization["parameters"] and "clock_stop_mode" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempo             = self.deserialize( serialization["parameters"]["tempo"] )
            self._quantization      = self.deserialize( serialization["parameters"]["quantization"] )
            self._staff             = self.deserialize( serialization["parameters"]["staff"] )
            self._time_signature    = self.deserialize( serialization["parameters"]["time_signature"] )
            self._key_signature     = self.deserialize( serialization["parameters"]["key_signature"] )
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
            case Settings():
                super().__lshift__(operand)
                self._tempo             = operand._tempo
                self._quantization      = operand._quantization
                self._staff             << operand._staff
                self._time_signature    << operand._time_signature
                self._key_signature     << operand._key_signature
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
                    case ra.Tempo():            self._tempo = operand._data._rational
                    case ra.Quantization():     self._quantization = operand._data._rational
                    case Staff():               self._staff = operand._data
                    case TimeSignature():       self._time_signature = operand._data
                    case ou.KeySignature():     self._key_signature = operand._data
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
            case ra.Tempo():            self._tempo = operand._rational
            case ra.Quantization():     self._quantization = operand._rational
            case ra.StepsPerNote():
                self._quantization = 1 / (operand % Fraction())
            case ra.StepsPerMeasure():
                self._quantization = self._staff % ra.NotesPerMeasure() / operand % Fraction()
            case Staff() | ra.StaffParameter() | TimeSignature():
                                        self._staff << operand
            case TimeSignature() | ra.TimeSignatureParameter():
                                        self._time_signature << operand
            case ou.KeySignature() | ou.Quality() | int() | float() | Fraction() | str():
                                        self._key_signature << operand
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
                self._tempo += operand._rational
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
                self._tempo -= operand._rational
                return self
        return super().__isub__(operand)


# Instantiate the Global Settings here.
settings: Settings = Settings()


