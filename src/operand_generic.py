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

# Define ANSI escape codes for colors
RED = "\033[91m"
RESET = "\033[0m"
        
try:
    # pip install matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseEvent
    from matplotlib.widgets import Button
except ImportError:
    print(f"{RED}Error: The 'matplotlib.pyplot' library is not installed.{RESET}")
    print("Please install it by running 'pip install matplotlib'.")
try:
    # pip install numpy
    import numpy as np
except ImportError:
    print(f"{RED}Error: The 'numpy' library is not installed.{RESET}")
    print("Please install it by running 'pip install numpy'.")


class Generic(o.Operand):
    """`Generic`

    Generic represents any `Operand` that doesn't fit any particular type of `Operand` in nature or parameters type.

    Parameters
    ----------
    Any(None) : Generic doesn't have any self parameters.
    """
    pass


class Locus(Generic):
    """`Generic -> Locus`

    A `Locus` is a pair of `Position` and `Duration` of a given `Element`. This allows a clear separation \
        between Element and its positioning and duration. It materializes the following analogy:

        +-------------------+---------+
        | Music             | Biology |
        +-------------------+---------+
        | Clip              | Genome  |
        | Element           | Gene    |
        | Position/Duration | Locus   |
        +-------------------+---------+
        
    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    """
    
    def __init__(self, *parameters):
        super().__init__()
        self._time_signature_reference: TimeSignature = None
        self._position_beats: Fraction      = Fraction(0)   # in Beats
        self._duration_beats: Fraction      = settings._duration
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def _get_time_signature(self, other_time_signature: 'TimeSignature' = None) -> 'TimeSignature':
        if self._time_signature_reference is None:
            if isinstance(other_time_signature, TimeSignature):
                return other_time_signature
            return settings._time_signature
        return self._time_signature_reference

    def position(self, position_measures: float = None) -> Self:
        self._position_beats = ra.Measures(self._time_signature_reference, position_measures) % ra.Position() % Fraction()
        return self

    def duration(self, note_value: float = None) -> Self:
        self._duration_beats = ra.Duration(self._time_signature_reference, note_value)._rational
        return self


    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Duration():
                        return operand._data << ra.Duration(self._time_signature_reference, self._duration_beats)
                    case ra.Position():
                        return operand._data << ra.Position(self._time_signature_reference, self._position_beats)
                    case ra.Length():
                        return operand._data << ra.Length(self._time_signature_reference, self._duration_beats)
                    case Fraction():        return self._duration_beats
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % operand
            case ra.Position():
                return operand.copy(self._time_signature_reference, self._position_beats)
            case ra.TimeUnit():
                # For TimeUnit only the `% operand` does the measure_module of it
                return ra.Position(self._time_signature_reference, self._position_beats) % operand
            case ra.Duration() | ra.Length():
                return operand.copy(self._time_signature_reference, self._duration_beats)
            case ra.NoteValue() | ra.TimeValue():
                return operand.copy(ra.Beats(self._time_signature_reference, self._duration_beats))
            case int():             return self % ra.Measure() % int()
            case Segment():         return operand.copy(self % ra.Position())
            case float():           return self % ra.NoteValue() % float()
            case Fraction():        return self._duration_beats
            case Locus():           return operand.copy(self)
            case _:                 return super().__mod__(operand)


    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return self._position_beats == other._position_beats \
                    and self._duration_beats == other._duration_beats
            case Segment():
                return other == self % ra.Position()
            case od.Conditional():
                return other == self
            case _:
                if other.__class__ == o.Operand:
                    return True
                if type(other) == ol.Null:
                    return False    # Makes sure ol.Null ends up processed as False
                return self % other == other

    def __lt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                if self._position_beats == other._position_beats:
                    return self._duration_beats > other._duration_beats # Longer duration comes first
                return self._position_beats < other._position_beats
            case _:
                return self % other < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                if self._position_beats == other._position_beats:
                    return self._duration_beats < other._duration_beats # Longer duration comes first
                return self._position_beats > other._position_beats
            case _:
                return self % other > other
    
    def start(self) -> ra.Position:
        return ra.Position(self, self._position_beats)

    def finish(self) -> ra.Position:
        return ra.Position(self, self._position_beats + self._duration_beats)

    def overlaps(self, other: 'Locus') -> bool:
        return other._position_beats + other._duration_beats > self._position_beats \
            and other._position_beats < self._position_beats + self._duration_beats


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["position"] = self.serialize(self._position_beats)
        serialization["parameters"]["duration"] = self.serialize(self._duration_beats)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Element':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "duration" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position_beats    = self.deserialize(serialization["parameters"]["position"])
            self._duration_beats    = self.deserialize(serialization["parameters"]["duration"])
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_element as oe
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        if self._time_signature_reference is None:
            match operand:
                case ra.Convertible():
                    self._time_signature_reference = operand._time_signature_reference
                case oe.Element() | oc.Composition():
                    self._time_signature_reference = operand._get_time_signature()
                case TimeSignature():
                    self._time_signature_reference = operand
        match operand:
            case self.__class__():
                super().__lshift__(operand)
                self._position_beats        = operand._position_beats
                self._duration_beats        = operand._duration_beats
            case od.Pipe():
                match operand._data:
                    case ra.Position():     self._position_beats = operand._data._rational
                    case ra.Duration() | ra.Length():
                                            self._duration_beats = operand._data._rational
                    case Fraction():        self._duration_beats = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Duration() | ra.Length():
                self._duration_beats        = operand._rational
            case ra.NoteValue() | ra.TimeValue():
                self << ra.Duration(self._time_signature_reference, operand)
            case ra.Position():
                self._position_beats        = operand._rational
            case ra.TimeUnit():
                # The setting of the TimeUnit depends on the Element position
                self._position_beats        = ra.Position(self._time_signature_reference, self._position_beats, operand) % Fraction()
            case int():
                self._position_beats        = ra.Measure(self._time_signature_reference, operand) % ra.Beats() % Fraction()
            case Segment():
                if operand._segment:
                    self << ra.Measure(operand._segment[0])
                    if len(operand._segment) == 2:
                        self << ra.Beat(operand._segment[1])
                    elif len(operand._segment) > 2:
                        self << ra.Step(operand._segment[2])
            case float():
                self << ra.NoteValue(self._time_signature_reference, operand)
            case Fraction():
                self._duration_beats        = ra.Beats(operand)._rational
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __iadd__(self, operand: any) -> Self:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ra.Position():
                self._position_beats += operand._rational
            case ra.Duration() | ra.Length():
                self._duration_beats += operand._rational
            case _:
                self_operand: any = self % operand
                self_operand += operand
                self << self_operand
        return self

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ra.Position():
                self._position_beats -= operand._rational
            case ra.Duration() | ra.Length():
                self._duration_beats -= operand._rational
            case _:
                self_operand: any = self % operand
                self_operand -= operand
                self << self_operand
        return self

    def __imul__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        self_operand: any = self % operand
        self_operand *= operand # Generic `self_operand`
        self << self_operand
        return self

    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        if operand != Fraction(0):
            self_operand: any = self % operand
            self_operand /= operand # Generic `self_operand`
            self << self_operand
        return self


    def __ifloordiv__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        if operand != Fraction(0):
            self_operand: any = self % operand
            self_operand //= operand # Generic `self_operand`
            self << self_operand
        return self


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
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case TimeSignature():       return self
                    case ra.BeatsPerMeasure():  return ra.BeatsPerMeasure() << self._top
                    case ra.BeatNoteValue():    return ra.BeatNoteValue() << 1 / self._bottom
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            # Direct Values
            case ra.BeatsPerMeasure():  return ra.BeatsPerMeasure() << self._top
            case ra.BeatNoteValue():    return ra.BeatNoteValue() << 1 / self._bottom
            # Calculated Values
            case ra.NotesPerMeasure():  return ra.NotesPerMeasure() << self._top / self._bottom
            case str():                 return f"{self._top}/{self._bottom}"
            case TimeSignature():       return operand.copy(self)
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
        self._tonic_key: int            = settings % ou.Key() % int() % 24
        self._octave_0: int             = 5     # By default it's the 4th Octave, that's 5 in 0 based!
        self._degree_0: float           = 0.0   # By default it's Degree 1, that's 0 in 0 based
        self._transposition: int        = 0     # By default it's it has no scale transposition
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
            + octave_transposition + degree_transposition + scale_transposition + degree_accidentals
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
            signature_scale: list[int] = self._key_signature.get_scale()
            """
            IN A TRANSPOSITION SCALE ACCIDENTALS **ARE** SUPPOSED TO HAPPEN
            """
            return Scale.transpose_key(round(self._degree_0), signature_scale)
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
                signature_scale: list[int] = self._key_signature.get_scale()
                return Scale.transpose_key(degree_0, signature_scale) - degree_transposition
        return 0

    def degree_accidentals(self) -> int:
        degree_int: int = round(self._degree_0)
        semitones: int = round((self._degree_0 - degree_int) * 10)
        if semitones % 2:  # Odd - same direction, same sign
            semitones = (semitones // 2) + (1 if semitones > 0 else -1)
        else:  # Even - inverse sign
            semitones = semitones // (-2)
        return semitones

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

    def chromatic_root_int(self) -> int:
        """
        Gets the root key int from the tonic_key with accidentals.
        """
        tonic_int: int = self._tonic_key % 12   # It may represent a flat, meaning, may be above 12
        degree_accidentals_transposition: int = self.degree_transposition() + self.degree_accidentals()
        return tonic_int + degree_accidentals_transposition

    def chromatic_root_key(self) -> int:
        """
        root_key takes into consideration the tonic gross value above 11 and accidentals.
        """
        chromatic_root_int: int = self.chromatic_root_int()
        chromatic_root_key: int = chromatic_root_int + self._tonic_key // 12 * 12  # key_line * total_keys
        return chromatic_root_key


    def scale_int(self) -> int:
        """
        The target key int after all processing **excluding** accidentals.
        """
        tonic_int: int = self._tonic_key % 12   # It may represent a flat, meaning, may be above 12
        degree_transposition: int = self.degree_transposition()
        scale_transposition: int = self.scale_transposition(degree_transposition)
        return tonic_int + degree_transposition + scale_transposition

    def chromatic_target_int(self) -> int:
        """
        The configured Degree chromatic transposition in the float number.
        """
        tonic_int: int = self._tonic_key % 12   # It may represent a flat, meaning, may be above 12
        degree_transposition: int = self.degree_transposition()
        scale_transposition: int = self.scale_transposition(degree_transposition)
        degree_accidentals: int = self.degree_accidentals()
        return tonic_int + degree_transposition + scale_transposition + degree_accidentals

    def pitch_int(self) -> int:
        """
        The final chromatic conversion of the tonic_key into the midi pitch with sharps, flats and naturals.
        """
        chromatic_int: int = self.chromatic_target_int()
        octave_transposition: int = self.octave_transposition()
        return chromatic_int + octave_transposition

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


    def key_degree_semitone(self, key_int: int) -> tuple[int, int]:
        signature_scale: list[int] = self._key_signature.get_scale()
        degree_0: int = 0
        semitone: int = 0
        tonic_offset: int = key_int - self._tonic_key % 12
        # For Semitones
        if signature_scale[tonic_offset % 12] == 0:
            if tonic_offset < 0:
                semitone = -1   # Needs to go down further
            else:
                semitone = +1   # Needs to go up further
        # For Tones
        while tonic_offset > 0:
            degree_0 += signature_scale[tonic_offset % 12]
            tonic_offset -= 1
        while tonic_offset < 0:
            degree_0 -= signature_scale[tonic_offset % 12]
            tonic_offset += 1
        return degree_0 % 7 + 1, semitone

    def key_transposition_semitone(self, key_int: int) -> tuple[int, int]:
        transposition: int = 0
        semitone: int = 0
        scale_degrees: int = 7  # Diatonic scales
        if self._scale:
            transposition_scale: list[int] = self._scale
            scale_degrees = sum(self._scale)
            first_key_int: int = self.root_int()
        else:
            transposition_scale: list[int] = self._key_signature.get_scale()
            first_key_int: int = self.tonic_int()   # Transposition becomes equivalent to degrees
        first_key_offset: int = key_int - first_key_int
        
        # For Semitones
        if transposition_scale[first_key_offset % 12] == 0:
            if first_key_offset < 0:
                semitone = -1   # Needs to go down further
            else:
                semitone = +1   # Needs to go up further
        # For Tones
        while first_key_offset > 0:
            transposition += transposition_scale[first_key_offset % 12]
            first_key_offset -= 1
        while first_key_offset < 0:
            transposition -= transposition_scale[first_key_offset % 12]
            first_key_offset += 1
        # Finally, transposition needs to be corrected for the usage of the Key Signature scale
        if not self._scale:
            # Partial transposition already done by degrees
            transposition -= self.degree_transposition()
        return transposition % scale_degrees, semitone


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
            case od.Pipe():
                match operand._data:
                    case of.Frame():        return self % od.Pipe( operand._data )
                    case ou.KeySignature(): return self._key_signature
                    case ou.Octave():       return operand._data << od.Pipe(self._octave_0 - 1)
                    case ou.TonicKey():     return operand._data << od.Pipe(self._tonic_key)    # Must come before than Key()
                    case ou.Degree():       return operand._data << od.Pipe(self._degree_0 + 1)
                    case ou.Transposition():
                        return operand._data << od.Pipe(self._transposition)
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
            
            case ou.Semitone():
                return operand.copy(self.pitch_int() % 12)
            
            case ou.TonicKey():    # Must come before than Key()
                return ou.TonicKey(self._tonic_key)
            case ou.RootKey():
                root_pitch: int = self.chromatic_root_int()
                key_note: int = root_pitch % 12
                key_line: int = self._tonic_key // 12
                if self._key_signature.is_enharmonic(self._tonic_key, key_note):
                    key_line += 2    # All Sharps/Flats
                return ou.RootKey( float(key_note + key_line * 12) )
            case ou.TargetKey():
                target_pitch: int = self.chromatic_target_int()
                key_note: int = target_pitch % 12
                key_line: int = self._tonic_key // 12
                if self._key_signature.is_enharmonic(self._tonic_key, key_note):
                    key_line += 2    # All Sharps/Flats
                return ou.TargetKey( float(key_note + key_line * 12) )
            case ou.Key():
                return ou.Key( self % ou.RootKey() )
            
            case ou.Octave():
                return ou.Octave(self._octave_0 - 1)
            
            case ou.Degree():
                return ou.Degree((self._degree_0 % 7) + 1)
            case ou.Transposition():
                return operand.copy(self._transposition)
             
            case ou.Sharp() | ou.Flat() | ou.Natural():
                return self % ou.Degree() % operand
            
            case Scale():
                return Scale(self._scale)
            case list():
                return self._scale.copy()

            case ou.Quality():
                return self._key_signature % operand
            
            case str():
                return self % ou.Key() % str()
            
            case Pitch():
                return operand.copy(self)
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
        serialization["parameters"]["scale"]            = self.serialize( self._scale )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key_signature" in serialization["parameters"] and "tonic_key" in serialization["parameters"] and
            "degree_0" in serialization["parameters"] and "octave_0" in serialization["parameters"] and
            "transposition" in serialization["parameters"] and "scale" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._key_signature = self.deserialize( serialization["parameters"]["key_signature"] )
            self._tonic_key     = self.deserialize( serialization["parameters"]["tonic_key"] )
            self._octave_0      = self.deserialize( serialization["parameters"]["octave_0"] )
            self._degree_0      = self.deserialize( serialization["parameters"]["degree_0"] )
            self._transposition = self.deserialize( serialization["parameters"]["transposition"] )
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
                    case ou.Transposition():
                        self._transposition = operand._data._unit
                    case Scale():
                        self._scale = operand._data._scale
                    case list():
                        self._scale = operand._data
                    case str():
                        # TO BE REVIEWED
                        # self._sharp = \
                        #     ((operand._data).strip().lower().find("#") != -1) * 1 + \
                        #     ((operand._data).strip().lower().find("b") != -1) * -1
                        self._degree_0 = abs((self % od.Pipe( ou.Degree() ) << ou.Degree(operand._data))._unit) - 1 # 0 based
                        self._tonic_key = ou.Key(self._tonic_key, operand._data)._unit
                    case _:
                        super().__lshift__(operand)

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.KeySignature() | ou.Quality():
                self._key_signature << operand

            case int():
                # Now a basic tonic transposition of the tonic key works because degree and transposition are linear operations
                actual_pitch: int = self.pitch_int()
                pitch_offset: int = operand - actual_pitch
                self.increment_tonic(pitch_offset)

            case ou.Semitone():
                # Now a basic tonic transposition of the tonic key works because degree and transposition are linear operations
                actual_pitch: int = self.tonic_int()    # Based on the outputted pitch
                tonic_offset: int = operand._unit % 12 - actual_pitch
                new_tonic: int = (self._tonic_key + tonic_offset) % 12
                tonic_line: int = self._tonic_key // 12
                self._tonic_key = new_tonic + tonic_line * 12
                self.match_octave(False)    # Keep actual octave (False)

            case float():
                self << ou.Degree(operand)
            case Fraction():
                self << ou.Transposition(operand)
                    
            case ou.Octave():
                self._octave_0 = operand._unit + 1

            case ou.TonicKey():    # Must come before than Key()
                if operand._unit < 0:
                    self._tonic_key = self._key_signature % ou.Key() % int()
                    self.match_octave(False)    # Keep actual octave (meaning False)
                else:
                    self._tonic_key = operand._unit % 24
            case ou.RootKey():
                degree, semitone = self.key_degree_semitone(operand._unit % 12)
                # Uses the Degree Accidental system instead of changing the Tonic key
                if semitone > 0:
                    degree += round((semitone * 2 - 1) / 10, 1)
                elif semitone < 0:
                    degree += round((-1) * (semitone * 2) / 10, 1)
                self << ou.Degree(degree)
            case ou.TargetKey():
                degree: float = 0.0 # No linear accidentals
                transposition, semitone = self.key_transposition_semitone(operand._unit % 12)
                # Uses the Degree Accidental system instead of changing the Tonic key
                if semitone > 0:
                    degree += round((semitone * 2 - 1) / 10, 1)
                elif semitone < 0:
                    degree += round((-1) * (semitone * 2) / 10, 1)
                self << ou.Transposition(transposition) << ou.Degree(degree)
            case ou.Key():
                self << ou.RootKey(operand)

            case ou.Degree():
                # Has to work with increments to keep the same Octave and avoid induced Octave jumps
                previous_degree_0: int = self._degree_0 % 7
                if operand < 0:
                    self._tonic_key = self._key_signature % ou.Key() % int()
                    self._degree_0 = 0  # Resets the degree to I
                elif operand < 1:
                    # Changes only the chromatic transposition
                    self._degree_0 = round(self._degree_0) + operand % float()
                else:   # operand >= 1
                    new_degree_0: float = ((operand._unit + operand._semitones) - 1) % 7
                    # previous_degree_0 here cancels any existent self Degree semitones!
                    self._degree_0 += new_degree_0 - previous_degree_0
                # There is still the need to match the Octave for the existing transpositions
                self.match_octave(False)    # Keep actual octave (False)
            
            case None:  # Works as a reset
                self._tonic_key = self._key_signature % ou.Key() % int()
                self._degree_0 = 0  # Resets the degree to I
                self._transposition = 0
                self.match_octave(False)    # Keep actual octave (False)

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

            case dict():
                for octave, value in operand.items():
                    self << value << ou.Octave(octave)

            case ou.DrumKit():
                self << ou.Degree()     # Makes sure no Degree different of Tonic is in use
                self << operand % int() # Sets the key number regardless KeySignature or Scale!

            case ou.Sharp() | ou.Flat() | ou.Natural():
                self << (self % ou.Degree() << operand)
            
            case Scale():
                self._scale = operand % list()
            case list():
                self._scale = operand.copy()
            case None:
                self._scale = []

            case str():
                string: str = operand.strip()
                # TO BE REVIEWED
                # self << ou.Degree(ou.Sharp(max(0, self._sharp)) << string, ou.Flat(max(0, self._sharp * -1)) << string)
                self << (self % ou.Degree() << string) # Safe, doesn't change the octave
                self << (self % ou.Key() << string)    # Need to change this to just Key
                self << Scale(od.Pipe(self._scale), operand)
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
                new_degree: ou.Degree = self % ou.Degree() + operand
                self._degree_0 += operand % float()   # Adds degree
                # self._degree_0 = round(self._degree_0)  # Removes accidentals
                # self._degree_0 += operand % int()   # Adds degree
                # semitones: float = new_degree._semitones
                # if self._degree_0 < 0:
                #     self._degree_0 -= semitones
                # elif self._degree_0 > 0:
                #     self._degree_0 += semitones
                self._degree_0 = round(self._degree_0, 1)
                self.match_octave()
            case ou.Sharp() | ou.Flat():
                self << self % ou.Degree() + operand
            case ou.Transposition() | ou.Tones():
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
                self._degree_0 -= operand % float()
                self._degree_0 = round(self._degree_0, 1)
                self.match_octave()
            case ou.Sharp() | ou.Flat():
                self << self % ou.Degree() - operand
            case ou.Transposition() | ou.Tones():
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
            case Controller():
                return operand.copy(self)
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
    def transpose_key(steps: int = 4, scale: list[int] | tuple[int] = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)) -> int:
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


    @staticmethod
    def plot(block: bool = True, scale: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1], tonic_key: ou.Key = ou.Key(), key_signature: str = None):

        tonic_int: int = tonic_key % int()
        # Enable interactive mode (doesn't block the execution)
        plt.ion()
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.clear()
        ax.set_title(f"Scale {tonic_key % str()} {Scale.get_scale_name(scale)}{f", Key Signature '{key_signature}'" if key_signature is not None else ""}")

        # Horizontal X-Axis, Time related (COMMON)
        ax.margins(x=0)  # Ensures NO extra padding is added on the x-axis

        beats_per_measure: Fraction = Fraction(4)
        quantization_beats: Fraction = Fraction(1) / Fraction(4)

        # By default it's 1 Measure long
        last_position: Fraction = beats_per_measure
        last_position_measures: Fraction = last_position / beats_per_measure
        last_position_measure: int = int(last_position / beats_per_measure)
        if last_position_measure != last_position_measures:
            last_position_measure += 1

        # Vertical Y-Axis, Pitch/Value related (SPECIFIC)
        ax.set_ylabel("Chromatic Keys")
        # Where the corner Coordinates are defined
        ax.format_coord = lambda x, y: (
            f"Pitch = {int(y + 0.5)}"
        )

        # Updates X-Axis data
        last_position = Fraction(1) # Beat 1
        last_position_measures = last_position / beats_per_measure
        last_position_measure = int(last_position_measures) # Trims extra length
        if last_position_measure != last_position_measures: # Includes the trimmed length
            last_position_measure += 1  # Adds only if the end doesn't coincide

        # PITCHES VERTICAL AXIS
        # Get pitch range
        min_pitch: int = 0
        max_pitch: int = 12
        if key_signature is not None:
            max_pitch = 24

        # Shade black keys
        for pitch in range(min_pitch, max_pitch + 1):
            if o.is_black_key(pitch):
                ax.axhspan(pitch - 0.5, pitch + 0.5, color='lightgray', alpha=0.5)

        # Plot notes
        for pitch, scale_key in enumerate(scale):
            if scale_key:
                ax.barh(y = tonic_int + pitch, width = float( 1 if o.is_black_key(tonic_int + pitch) else 2 ), left = float(1), 
                        height=0.5, color='black', edgecolor='black', linewidth=1, linestyle='solid', alpha = 1)

        # Where the VERTICAL axis is defined - Chromatic Keys
        chromatic_keys: list[str] = ["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"]
        # Set MIDI note ticks with Middle C in bold
        ax.set_yticks(range(min_pitch, max_pitch + 1))
        y_labels = [
            chromatic_keys[pitch % 12] + (str(pitch // 12) if pitch % 12 == 0 else "")
            for pitch in range(min_pitch, max_pitch + 1)
        ]  # Bold Middle C
        ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')
        ax.set_ylim(min_pitch - 0.5, max_pitch + 0.5)  # Ensure all notes fit

        # Draw vertical grid lines based on beats and measures
        one_extra_subdivision: float = quantization_beats
        single_measure: int = 1 # It's just for a scale visualization
        step_positions = np.arange(0.0, float(single_measure * beats_per_measure + one_extra_subdivision), float(quantization_beats))
        beat_positions = np.arange(0.0, float(single_measure * beats_per_measure + one_extra_subdivision), 1)
        measure_positions = np.arange(0.0, float(single_measure * beats_per_measure + one_extra_subdivision), float(beats_per_measure))
    
        for measure_pos in measure_positions:
            ax.axvline(measure_pos, color='black', linestyle='-', alpha=1.0, linewidth=0.7)  # Measure lines
        for beat_pos in beat_positions:
            ax.axvline(beat_pos, color='gray', linestyle='-', alpha=0.5, linewidth=0.5)  # Measure lines
        for grid_pos in step_positions:
            ax.axvline(grid_pos, color='gray', linestyle='dotted', alpha=0.25, linewidth=0.5)  # Beat subdivisions

        ax.set_xticks([])
        fig.canvas.draw_idle()

        # Where the padding is set
        plt.tight_layout()
        plt.subplots_adjust(right=0.975)  # 2.5% right padding
        # Avoids too thick hatch lines
        plt.rcParams['hatch.linewidth'] = 0.10

        plt.show(block=block)


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
            case ou.TonicKey():         return ou.TonicKey( Scale.get_tonic_key(self._scale) )
            case ou.Key():              return ou.Key( Scale.get_tonic_key(self._scale) )
            case float():               return float( Scale.get_tonic_key(self._scale) )
            case Scale():
                return operand.copy(self)
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
        self._duration_beats: Fraction = ra.Duration(1/16)._rational
        self._swing: Fraction = ra.Swing(0.5)._rational
        self._chaos: ch.Chaos = ch.SinX()
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ou.Order():            return operand._data << od.Pipe( self._order )
                    case ra.Duration():         return operand._data << od.Pipe( self._duration_beats )
                    case ra.Swing():            return operand._data << od.Pipe( self._swing )
                    case ch.Chaos():            return self._chaos
                    case int():                 return self._order
                    case float():               return float( self._duration_beats )
                    case Fraction():            return self._duration_beats
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case ou.Order():            return ou.Order(self._order)
            case str():                 return ou.Order(self._order) % str()
            case ra.Duration():         return ra.Duration( self._duration_beats )
            case ra.Swing():            return ra.Swing(self._swing)
            case ch.Chaos():            return self._chaos.copy()
            case int():                 return self._order
            case float():               return float( self._duration_beats )
            case Fraction():            return self._duration_beats
            case Arpeggio():
                return operand.copy(self)
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

            time_signature: TimeSignature = notes[0]._get_time_signature()
            note_start_position: ra.Position = notes[0] % od.Pipe( ra.Position() )
            arpeggio_length: ra.Length = notes[0] % od.Pipe( ra.Length() )
            arpeggio_end_position: ra.Position = arpeggio_length % ra.Position()
            note_length: ra.Length = ra.Length(time_signature, self._duration_beats)
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
                and self._duration_beats        == other._duration_beats \
                and self._chaos                 == other._chaos
        if isinstance(other, od.Conditional):
            return other == self
        return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["order"]            = self.serialize( self._order )
        serialization["parameters"]["duration"]         = self.serialize( self._duration_beats )
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
            self._duration_beats        = self.deserialize( serialization["parameters"]["duration"] )
            self._swing                 = self.deserialize( serialization["parameters"]["swing"] )
            self._chaos                 = self.deserialize( serialization["parameters"]["chaos"] )
        return self
    
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Arpeggio():
                super().__lshift__(operand)
                self._order                 = operand._order
                self._duration_beats        = operand._duration_beats
                self._swing                 = operand._swing
                self._chaos                 = operand._chaos.copy()
            case od.Pipe():
                match operand._data:
                    case ou.Order():                self._order = operand._data._unit
                    case ra.Duration():             self._duration_beats = operand._data._rational
                    case ra.Swing():                self._swing = operand._data._rational
                    case ch.Chaos():                self._chaos = operand._data
                    case int():                     self._order = operand._data
                    case float():                   self._duration_beats = ra.Duration(operand._data)._rational
                    case Fraction():                self._duration_beats = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ou.Order():                self._order = operand._unit
            case str():                     self._order = ou.Order(operand)._unit
            case ra.Duration():             self._duration_beats = operand._rational
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ch.Chaos():                self._chaos << operand
            case int():                     self._order = operand
            case float():                   self._duration_beats = ra.Duration(operand)._rational
            case Fraction():                self._duration_beats = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __imul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> Self:
        self._initiated = True
        self._chaos @ number
        self._index += self.convert_to_int(number)    # keeps track of each iteration
        return self


class Segment(Generic):
    """`Generic -> Segment`

    A Segment concerns a single unitary positional section of Time, meaning, a single Measure, a single Beat,
    or a single Step, where the order is set by Measure, Beat, Step.

    Parameters
    ----------
    list([]) : The default is the entire piece, `[]`, for the first Beat use `[0, 0]`, and for the first Step, use, `[0, 0, 0]`.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._segment: list[int] = []
        self._time_signature_reference: TimeSignature = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def _get_time_signature(self, other_time_signature: 'TimeSignature' = None) -> 'TimeSignature':
        if self._time_signature_reference is None:
            if isinstance(other_time_signature, TimeSignature):
                return other_time_signature
            return settings._time_signature
        return self._time_signature_reference


    def len(self) -> int:
        return len(self._segment)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case list():                return self._segment
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case list():                return self._segment.copy()
            case ra.Measure():
                if len(self._segment) < 1:
                    return None
                return operand.copy(self._segment[0])
            case ra.Beat():
                if len(self._segment) < 2:
                    return None
                if len(self._segment) == 2:
                    return operand.copy(self._segment[1])
                steps_per_beat: int = int(1 / settings._quantization)
                return operand.copy(self._segment[2] // steps_per_beat)
            case ra.Step():
                if len(self._segment) < 2:
                    return None
                if len(self._segment) == 2:
                    steps_per_beat: int = int(1 / settings._quantization)
                    return operand.copy(self._segment[1] * steps_per_beat)
                return operand.copy(self._segment[2])
            case int():
                if len(self._segment) < 1:
                    return None
                return self._segment[0]
            case float():
                if len(self._segment) < 1:
                    return None
                if len(self._segment) == 2:
                    return round(self._segment[0] + self._segment[1] / 10, 1)
                if len(self._segment) == 3:
                    return round(self._segment[0] + self._segment[2] / 10, 1)
                return float(self._segment[0])
            case str():
                if len(self._segment) < 1:
                    return ""
                if len(self._segment) == 1:
                    return "Measure"
                if len(self._segment) == 2:
                    return "Measure.Beat"
                return "Measure.Step"
            case Segment():
                return operand.copy(self)
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        match other:
            case Segment():
                if len(self._segment) == 3:
                    return self._segment[0] == other._segment[0] and self._segment[2] == other._segment[2]
                return self._segment == other._segment
            case ra.Measure():
                if len(self._segment) < 1:
                    return True
                return self._segment[0] == other % int()
            case ra.Beat():
                if len(self._segment) < 2:
                    return True
                if len(self._segment) == 2:
                    return self._segment[1] == other % int()
                return False
            case ra.Step():
                if len(self._segment) < 2:
                    return True
                if len(self._segment) == 2:
                    steps_per_beat: int = int(1 / settings._quantization)
                    step_beat: int = other % int() // steps_per_beat
                    return self._segment[1] == step_beat
                if len(self._segment) == 3:
                    return self._segment[2] == other % int()
                return False
            case int():
                if len(self._segment) < 1:
                    return True
                return self._segment[0] == other
            case float():
                if len(self._segment) < 1:
                    return True
                if len(self._segment) == 2:
                    return self._segment[0] == round(other) and self._segment[1] == round((other - round(other)) * 10)
                if len(self._segment) == 3:
                    return self._segment[0] == round(other) and self._segment[2] == round((other - round(other)) * 10)
                return self._segment[0] == round(other)
            case ra.Position():
                if self._segment:
                    position_segment: list[int] = []
                    if len(self._segment) > 0:
                        position_segment.append( other % ra.Measure() % int() )
                        if len(self._segment) == 2:
                            position_segment.append( other % ra.Beat() % int() )
                        elif len(self._segment) == 3:
                            position_segment.append( 0 )    # No Beat defined
                            position_segment.append( other % ra.Step() % int() )
                    return self == Segment(position_segment)
                else:
                    return True
            case od.Conditional():
                return other == self
            case _:
                return self % other == other
        return False
    

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["segment"] = self.serialize( self._segment )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "segment" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._segment = self.deserialize( serialization["parameters"]["segment"] )
        return self
    
    def __lshift__(self, operand: any) -> Self:
        import operand_element as oe
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Segment():
                super().__lshift__(operand)
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand._time_signature_reference
                self._segment = operand._segment.copy()
            case od.Pipe():
                match operand._data:
                    case list():            self._segment = operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case list():
                self._segment = operand.copy()
            case ra.Measure():
                if len(self._segment) > 0:
                    self._segment[0] = operand % int()
                else:
                    self._segment.append(operand % int())
            case ra.Beat():
                if len(self._segment) > 1:
                    self._segment[1] = operand % int()
                elif len(self._segment) == 1:
                    self._segment.append(operand % int())
                elif len(self._segment) == 0:
                    self._segment.append(0) # Default is Measure 0
                    self._segment.append(operand % int())
            case ra.Step():
                if len(self._segment) > 2:
                    self._segment[2] = operand % int()
                elif len(self._segment) == 2:
                    self._segment.append(operand % int())
                elif len(self._segment) == 1:
                    self._segment.append(0) # Default is Beat 0
                    self._segment.append(operand % int())
                elif len(self._segment) == 0:
                    self._segment.append(0) # Default is Measure 0
                    self._segment.append(0) # Default is Beat 0
                    self._segment.append(operand % int())
            case int():
                self << ra.Measure(operand)
            case float():
                self << ra.Measure(round(operand))
                self << ra.Beat(round((operand - round(operand)) * 10))
            case ra.Position():
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand._time_signature_reference
                if self._segment:
                    self._segment[0] = operand % ra.Measure() % int()
                    if len(self._segment) == 2:
                        self._segment[1] = operand % ra.Beat() % int()
                    elif len(self._segment) == 3:
                        self._segment[2] = operand % ra.Step() % int()
            case oe.Element() | oc.Composition():
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand._get_time_signature()
            case TimeSignature():
                if self._time_signature_reference is None:
                    self._time_signature_reference = operand
        return self
    
    def __iadd__(self, operand: any) -> Self:
        match operand:
            case ra.Measure():
                if len(self._segment) > 0:
                    self._segment[0] += operand % int()
            case ra.Beat():
                if len(self._segment) > 1:
                    self._segment[1] += operand % int()
                    beats_per_measure: int = self._get_time_signature()._top
                    self._segment[0] += self._segment[1] // beats_per_measure
                    self._segment[1] %= beats_per_measure
            case ra.Step():
                if len(self._segment) > 2:
                    self._segment[2] += operand % int()
                    steps_per_beat: int = int(1 / settings._quantization)
                    beats_per_measure: int = self._get_time_signature()._top
                    steps_per_measure: int = steps_per_beat * beats_per_measure
                    self._segment[0] += self._segment[2] // steps_per_measure
                    self._segment[2] %= steps_per_measure
            case int():
                if len(self._segment) > 0:
                    self._segment[0] += operand
            case float():
                if len(self._segment) > 0:
                    self += ra.Measure(round(operand))
                    if len(self._segment) == 2:
                        self += ra.Beat(round((operand - round(operand)) * 10))
                    elif len(self._segment) == 3:
                        self += ra.Step(round((operand - round(operand)) * 10))
        return self

    def __isub__(self, operand: any) -> Self:
        match operand:
            case ra.Measure():
                if len(self._segment) > 0:
                    self._segment[0] -= operand % int()
            case ra.Beat():
                if len(self._segment) > 1:
                    self._segment[1] -= operand % int()
                    beats_per_measure: int = self._get_time_signature()._top
                    self._segment[0] -= self._segment[1] // beats_per_measure
                    self._segment[1] %= beats_per_measure
            case ra.Step():
                if len(self._segment) > 2:
                    self._segment[2] -= operand % int()
                    steps_per_beat: int = int(1 / settings._quantization)
                    beats_per_measure: int = self._get_time_signature()._top
                    steps_per_measure: int = steps_per_beat * beats_per_measure
                    self._segment[0] -= self._segment[2] // steps_per_measure
                    self._segment[2] %= steps_per_measure
            case int():
                if len(self._segment) > 0:
                    self._segment[0] -= operand
            case float():
                if len(self._segment) > 0:
                    self -= ra.Measure(round(operand))
                    if len(self._segment) == 2:
                        self -= ra.Beat(round((operand - round(operand)) * 10))
                    elif len(self._segment) == 3:
                        self -= ra.Step(round((operand - round(operand)) * 10))
        return self



if TYPE_CHECKING:
    from operand_element import Element, Note
    from operand_chaos import Chaos
    from operand_rational import Length
    from operand_container import Container, Composition, Clip

class Process(Generic):
    """`Generic -> Process`

    A process is no more than a call of a `Container` method, so, in nature a `Process` is a
    read only `Operand` without mutable parameters. Intended to be used in a chained `>>` sequence of operators.

    Parameters
    ----------
    list([]) : A `Process` has multiple parameters dependent on the specific `Process` sub class.

    Returns:
        Any: All `Process` operands return the original left side `>>` input. Exceptions mentioned.
    """
    def __init__(self, parameters: list = []):
        super().__init__()
        self._parameters: list = self.deep_copy(parameters)
        self._indexes: dict[str, int] = {}

    def __getitem__(self, name: str) -> Any:
        """Get parameter value by name using bracket notation."""
        if name not in self._indexes:
            print(f"Warning: Parameter '{name}' not found. Available: {list(self._indexes.keys())}")
            return ol.Null()
        return self._parameters[self._indexes[name]]
    
    def __setitem__(self, name: str, value: Any) -> Self:
        """Set parameter value by name using bracket notation."""
        if name not in self._indexes:
            print(f"Warning: Parameter '{name}' not found. Available: {list(self._indexes.keys())}")
        else:
            self._parameters[self._indexes[name]] = value
        return self


    @staticmethod
    def _clocked_playlist(operand: o.T) -> list[dict]:
        import operand_element as oe
        import operand_container as oc

        playlist: list[dict] = []

        match operand:
            case oc.Composition() | oe.Element():
                # Generates the Clock data regardless, needed for correct JsonMidiPlayer processing
                clock_length: ra.Length = (operand.finish() % ra.Length()).roundMeasures()
                default_clock: oe.Clock = settings % oe.Clock()
                default_clock._duration_beats = ra.Duration(clock_length)._rational # The same staff will be given next
                playlist.extend( default_clock.getPlaylist( time_signature = operand._get_time_signature() ) )  # Clock Playlist
                if isinstance(operand, oc.Composition):
                    # Makes sure the entire Composition content is used
                    playlist.extend( operand._dev_base_container().getPlaylist() )    # Operand Playlist
                else:
                    playlist.extend( operand.getPlaylist() )    # Operand Playlist
            case od.Playlist():

                operand_playlist = operand.getPlaylist()
                playlist_time_ms: list[dict] = [
                    dict_time_ms for dict_time_ms in operand_playlist
                    if "time_ms" in dict_time_ms
                ]

                if playlist_time_ms:
                    last_time_ms: float = \
                        sorted(playlist_time_ms, key=lambda x: x['time_ms'])[-1]["time_ms"]
                    # By default, time classes use the defaults Staff
                    single_measure_beats: ra.Beats = ra.Measures(1) % ra.Beats()
                    single_measure_minutes: Fraction = settings.beats_to_minutes( single_measure_beats._rational )
                    single_measure_ms: float = o.minutes_to_time_ms( single_measure_minutes )
                    total_measures: int = last_time_ms // single_measure_ms
                    if last_time_ms > int(last_time_ms):
                        total_measures += 1
                    # Generates the Clock data regardless, needed for correct JsonMidiPlayer processing
                    default_clock: oe.Clock = settings % oe.Clock() << ra.Length(total_measures)
                    playlist.extend( default_clock.getPlaylist( time_signature = settings._time_signature ) )  # Clock Playlist
                    playlist.extend( operand_playlist ) # Operand Playlist

        return playlist


class ReadOnly(Process):
    """`Generic -> Process -> ReadOnly`

    A ReadOnly process is one that results in no change of the subject `Operand`.

    Parameters
    ----------
    Any(None) : A `Process` has multiple parameters dependent on the specific `Process` sub class.

    Returns:
        Any: All `Process` operands return the original left side `>>` input. Exceptions mentioned.
    """
    def __irrshift__(self, operand: o.T) -> o.T:
        return self.__rrshift__(operand)


class RightShift(ReadOnly):
    """`Generic -> Process -> ReadOnly -> RightShift`

    Applies the `>>` operation if process is `True`.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `>>` by the chained data sequence.
    bool(True) : By default, the the give `Operand` is targeted with `>>`.
    """
    def __init__(self, operand: o.Operand = None, process: bool = True):
        super().__init__()
        self._parameters = operand    # needs to keep the original reference (no copy)
        self._process: bool = process

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process:
                return self._parameters.__rshift__(operand)
            return operand
        return super().__rrshift__(operand)

    
class SideEffect(ReadOnly):
    """`Generic -> Process -> ReadOnly -> SideEffect`

    This `Operand` can be inserted in a sequence of `>>` in order to apply as a side effect the chained
    data in the respective self data without changing the respective chained data sequence.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected inside the chained `>>` sequence.
    """
    def __init__(self, operand: o.Operand = None, process: bool = True):
        super().__init__()
        self._parameters = operand    # needs to keep the original reference (no copy)
        self._process: bool = process

class LeftShift(SideEffect):
    """`Generic -> Process -> ReadOnly -> SideEffect -> LeftShift`

    Applies the `<<` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `<<` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process:
                self._parameters.__lshift__(operand)
            return operand
        return super().__rrshift__(operand)

class RightShift(SideEffect):
    """`Generic -> Process -> ReadOnly -> SideEffect -> RightShift`

    Applies the `>>` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `>>` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process:
                self._parameters.__rshift__(operand)
            return operand
        return super().__rrshift__(operand)

class IAdd(SideEffect):    # i stands for "inplace"
    """`Generic -> Process -> ReadOnly -> SideEffect -> IAdd`

    Applies the `+=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `+=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process:
                self._parameters.__iadd__(operand)
            return operand
        return super().__rrshift__(operand)

class ISub(SideEffect):
    """`Generic -> Process -> ReadOnly -> SideEffect -> ISub`

    Applies the `-=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `-=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process:
                self._parameters.__isub__(operand)
            return operand
        return super().__rrshift__(operand)

class IMul(SideEffect):
    """`Generic -> Process -> ReadOnly -> SideEffect -> IMul`

    Applies the `*=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `*=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process:
                self._parameters.__imul__(operand)
            return operand
        return super().__rrshift__(operand)

class IDiv(SideEffect):
    """`Generic -> Process -> ReadOnly -> SideEffect -> IDiv`

    Applies the `/=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `/=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process:
                self._parameters.__itruediv__(operand)
            return operand
        return super().__rrshift__(operand)


class Save(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Save`

    Saves all parameters' `Serialization` of a given `Operand` into a file.

    Parameters
    ----------
    None, str() : The filename of the Operand's serialization data.
    """
    def __init__(self, filename: str | None = None):
        super().__init__(filename)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            if not isinstance(self._parameters, str):
                if isinstance(operand, oc.Composition):
                    self._parameters = operand.composition_filename() + "_save.json"
                else:
                    self._parameters = "json/_Save_jsonMidiCreator.json"
            c.saveJsonMidiCreator(operand.getSerialization(), self._parameters)
            return operand
        return super().__rrshift__(operand)

class Export(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Export`

    Exports a file playable by the `JsonMidiPlayer` program.

    Parameters
    ----------
    None, str() : The filename of the JsonMidiPlayer playable file.
    """
    def __init__(self, filename: str | None = None):
        super().__init__(filename)

    def __rrshift__(self, operand: o.T) -> o.T:
        match operand:
            case o.Operand():
                if not isinstance(self._parameters, str):
                    if isinstance(operand, oc.Composition):
                        self._parameters = operand.composition_filename() + "_export.json"
                    else:
                        self._parameters = "json/_Export_jsonMidiPlayer.json"
                playlist: list[dict] = self._clocked_playlist(operand)
                c.saveJsonMidiPlay(playlist, self._parameters)
                return operand
            case _:
                return super().__rrshift__(operand)

class Render(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Render`

    Renders a midi file playable by any Midi player.

    Parameters
    ----------
    None, str() : The filename of the Midi playable file.
    """
    def __init__(self, filename: str | None = None):
        super().__init__(filename)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            if not isinstance(self._parameters, str):
                if isinstance(operand, oc.Composition):
                    self._parameters = operand.composition_filename() + "_render.mid"
                else:
                    self._parameters = "midi/_MidiExport_song.mid"
            c.saveMidiFile(operand.getMidilist(), self._parameters)
            return operand
        return super().__rrshift__(operand)


class Plot(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Plot`

    Plots the `Note`s in a `Clip`, if it has no Notes it plots the existing `Automation` instead.

    Args:
        by_channel: Allows the visualization in a Drum Machine alike instead of by Pitch.
        block (bool): Suspends the program until the chart is closed.
        pause (float): Sets a time in seconds before the chart is closed automatically.
        iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
            this is dependent on a n_button being given.
        n_button (Callable): A function that takes a Composition to be used to generate a new iteration.
        composition (Composition): A composition to be played together with the plotted one.
        title (str): A title to give to the chart in order to identify it.
    """
    def __init__(self, by_channel: bool = False, block: bool = True, pause: float = 0.0, iterations: int = 0,
                 n_button: Optional[Callable[['Composition'], 'Composition']] = None,
                 composition: Optional['Composition'] = None, title: str | None = None):
        super().__init__([by_channel, block, pause, iterations, n_button, composition, title])
        self._indexes = {
            'by_channel': 0, 'block': 1, 'pause': 2, 'iterations': 3, 'n_button': 4, 'composition': 5, 'title': 6
        }

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        import operand_element as oe
        import operand_generic as og
        import operand_unit as ou
        if isinstance(operand, (oc.Composition, oe.Element)):
            return operand.plot(*self._parameters)
        if isinstance(operand, Scale):
            Scale.plot(self._parameters[1], operand % list())
        elif isinstance(operand, ou.KeySignature):
            Scale.plot(self._parameters[1], operand % list(), operand % ou.Key(), operand % str())
        return operand


class Call(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Call`

    `Call` a given callable function passed as `n_button`. This is to be used instead of `Plot` whenever \
        a given iteration was already chosen bypassing this way the process of plotting.

    Args:
        iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
            this is dependent on a n_button being given.
        n_button (Callable): A function that takes a Composition to be used to generate a new iteration.
    """
    def __init__(self, iterations: int = 1, n_button: Optional[Callable[['Composition'], 'Composition']] = None):
        super().__init__([iterations, n_button])
        self._indexes = {
            'iterations': 0, 'n_button': 1
        }

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        import operand_element as oe
        if isinstance(operand, (oc.Composition, oe.Element)):
            return operand.call(*self._parameters)
        return operand


class Play(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Play`

    Plays an `Element` or a `Composition` straight on into the `JsonMidiPlayer` program.

    Args:
        verbose (bool): Defines the `verbose` mode of the playing.
        plot (bool): Plots a chart before playing it.
        block (bool): Blocks the Plot until is closed and then plays the plotted content.
    """
    def __init__(self, verbose: bool = False, plot: bool = False, block: bool = False):
        super().__init__([verbose, plot, block])
        self._indexes = {
            'verbose': 0, 'plot': 1, 'block': 2
        }

    def __rrshift__(self, operand: o.T) -> o.T:
        import threading
        import operand_container as oc
        import operand_element as oe
        match operand:
            case oc.Composition():
                if operand._dev_base_container().len() > 0:
                    playlist: list[dict] = self._clocked_playlist(operand._dev_base_container())
                    if self._parameters[1] and self._parameters[2]:
                        # Start the function in a new process
                        process = threading.Thread(target=c.jsonMidiPlay, args=(playlist, self._parameters[0]))
                        process.start()
                        operand >> Plot(self._parameters[2])
                    else:
                        if self._parameters[1] and not self._parameters[2]:
                            operand >> Plot(self._parameters[2])
                        c.jsonMidiPlay(playlist, self._parameters[0])
                else:
                    print(f"Warning: Trying to play an **empty** list!")
                return operand
            case oe.Element():
                playlist: list[dict] = self._clocked_playlist(operand)
                if self._parameters[1] and self._parameters[2]:
                    # Start the function in a new process
                    process = threading.Thread(target=c.jsonMidiPlay, args=(playlist, self._parameters[0]))
                    process.start()
                    operand >> Plot(self._parameters[2])
                else:
                    if self._parameters[1] and not self._parameters[2]:
                        operand >> Plot(self._parameters[2])
                    c.jsonMidiPlay(playlist, self._parameters[0])
                return operand
            case od.Playlist():
                playlist: list[dict] = self._clocked_playlist(operand)
                c.jsonMidiPlay(playlist, self._parameters[0])
                return operand
            case _:
                return super().__rrshift__(operand)
    
    @staticmethod
    def play(operand: o.T) -> o.T:
        return Play().__rrshift__(operand)


class Print(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Print`

    Prints the Operand's parameters in a JSON alike layout if it's an `Operand` being given,
    otherwise prints directly like the common `print` function.

    Args:
        formatted (bool): If False prints the `Operand` content in a single line.
    """
    def __init__(self, serialization: bool = False):
        super().__init__( False if serialization is None else serialization )

    def __rrshift__(self, operand: o.T) -> o.T:
        import json
        match operand:
            case o.Operand():
                if self._parameters:
                    serialized_json_str = json.dumps(operand.getSerialization())
                    json_object = json.loads(serialized_json_str)
                    json_formatted_str = json.dumps(json_object, indent=4)
                    print(json_formatted_str)
                else:
                    print(operand % str())
            case list():
                for index, value in enumerate(operand):
                    if isinstance(value, o.Operand):
                        operand[index] %= str()
                print(operand)
            case _:
                print(operand)
        return operand

class Copy(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Copy`

    Creates and returns a copy of the left side `>>` operand.

    Parameters
    ----------
    Any(None) : The Parameters to be set on the copied `Operand`.

    Returns:
        Operand: Returns a copy of the left side `>>` operand.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.copy(*self._parameters)
        return super().__rrshift__(operand)

class Reset(Process):
    """`Generic -> Process -> Reset`

    Does a reset of the Operand's original parameters and its volatile ones.

    Parameters
    ----------
    Any(None) : The Parameters to be set on the reset `Operand`.

    Returns:
        Operand: Returns the same reset operand.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.reset(*self._parameters)
        return super().__rrshift__(operand)

class Clear(Process):
    """`Generic -> Process -> Clear`

    Besides doing a reset of the Operand's slate parameters and its volatile ones,
    sets the default parameters associated with an empty Operand (blank slate).

    Parameters
    ----------
    Any(None) : The Parameters to be set on the cleared `Operand`.

    Returns:
        Operand: Returns the same cleared operand.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.clear(*self._parameters)
        return super().__rrshift__(operand)


class ScaleProcess(Process):
    """`Generic -> Process -> ScaleProcess`
    """
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_generic as og
        if isinstance(operand, Scale):
            return self.__irrshift__(operand.copy())
        return super().__rrshift__(operand)

    def __irrshift__(self, operand: o.T) -> o.T:
        import operand_generic as og
        if isinstance(operand, Scale):
            return self._process(operand)
        else:
            print(f"Warning: Operand is NOT a `Scale`!")
        return super().__rrshift__(operand)

    def _process(self, operand: o.T) -> o.T:
        return operand

class Modulate(ScaleProcess):    # Modal Modulation
    """`Generic -> Process -> ScaleProcess -> Modulate`

    Modulate() is used to modulate the self Scale or Scale.
    
    Parameters
    ----------
    int(1) : Modulate a given Scale to 1 ("1st") as the default mode.
    """
    def __init__(self, mode: int | str = 1):
        import operand_unit as ou
        unit = ou.Mode(mode)._unit
        super().__init__(unit)

    # CHAINABLE OPERATIONS

    def _process(self, operand: 'Scale') -> 'Scale':
        return operand.modulate(self._parameters)

class Transpose(ScaleProcess):    # Chromatic Transposition
    """`Generic -> Process -> ScaleProcess -> Transpose`

    Transpose() is used to rotate a scale by semitones.
    
    Parameters
    ----------
    int(7) : Transpose a given Scale by 7 semitones as the default.
    """
    def __init__(self, semitones: int = 7):
        super().__init__(semitones)

    # CHAINABLE OPERATIONS

    def _process(self, operand: 'Scale') -> 'Scale':
        return operand.transpose(self._parameters)


class ContainerProcess(Process):
    """`Generic -> Process -> ContainerProcess`

    Processes applicable exclusively to `Container` operands.
    """
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            if operand.is_masked(): # Mask retains the original Container
                return self.__irrshift__(operand)
            return self.__irrshift__(operand.copy())
        print(f"Warning: Operand is NOT a `Container`!")
        return operand

    def __irrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return self._process(operand)
        else:
            print(f"Warning: Operand is NOT a `Container`!")
        return super().__rrshift__(operand)

    def _process(self, operand: o.T) -> o.T:
        return operand

class Sort(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Sort`

    Sorts the contained items by a given parameter type.

    Args:
        parameter (type): Defines the given parameter type to sort by.
        reverse (bool): Reverses the sorting if `True`.
    """
    from operand_rational import Position

    def __init__(self, parameter: type = Position, reverse: bool = False):
        super().__init__([parameter, reverse])
        self._indexes = {
            'parameter': 0, 'reverse': 1
        }

    def _process(self, operand: 'Container') -> 'Container':
        return operand.sort(*self._parameters)


class Mask(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Mask`

    Masks the items that meet the conditions (equal to). No implicit copies.

    Args:
        condition (Any): Sets a condition to be compared with `==` operator.
    """
    def __init__(self, *conditions):
        super().__init__(conditions)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return self.__irrshift__(operand)   # Special case, NO copy
        print(f"Warning: Operand is NOT a `Container`!")
        return operand
    
    def _process(self, operand: 'Container') -> 'Container':
        return operand.mask(*self._parameters)

class Unmask(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Unmask`

    Returns the base `Container` with the mask disabled.

    Args:
        None
    """
    def __init__(self, *conditions):
        super().__init__()

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return self.__irrshift__(operand)   # Special case, NO copy
        print(f"Warning: Operand is NOT a `Container`!")
        return operand
    
    def _process(self, operand: 'Container') -> 'Container':
        return operand.unmask()


class Filter(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Filter`

    A `Filter` works exactly like a `Mask` with the difference of keeping just \
        the matching items and deleting everything else.

    Args:
        condition (Any): Sets a condition to be compared with `==` operator.
    """
    def __init__(self, *conditions):
        super().__init__(conditions)

    def _process(self, operand: 'Container') -> 'Container':
        return operand.filter(*self._parameters)


class Operate(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Operate`

    Allows the setting of a specific operator as operation with a str as operator symbol.

    Args:
        operand (Any): `Operand` that is the source of the operation.
        operator (str): The operator `op` that becomes processed as `self op operand`.
    """
    def __init__(self, operand: Any = None, operator: str = "<<"):
        super().__init__([operand, operator])
        self._indexes = {
            'operand': 0, 'operator': 1
        }

    def _process(self, operand: 'Container') -> 'Container':
        return operand.operate(*self._parameters)


class Transform(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Transform`

    Transforms each item by wrapping it with the new operand type given.

    Args:
        operand_type (type): The type of `Operand` by which each item will be transformed into.
    """
    def __init__(self, operand_type: type = 'Note'):
        super().__init__(operand_type)

    def _process(self, operand: 'Container') -> 'Container':
        return operand.transform(self._parameters)


class Shuffle(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Shuffle`

    Reaffects the given parameter type in a chaotic manner.

    Args:
        chaos (Chaos): An Chaos object to be used as sorter.
        parameter (type): The type of parameter being swapped around the items.
    """
    from operand_rational import Position

    def __init__(self, chaos: 'Chaos' = None, parameter: type = Position):
        super().__init__([chaos, parameter])
        self._indexes = {
            'chaos': 0, 'parameter': 1
        }

    def _process(self, operand: 'Container') -> 'Container':
        return operand.shuffle(*self._parameters)

class Swap(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Swap`

    This method swaps a given parameter type between two operands.

    Args:
        left (any): The first item or `Segment` data.
        right (any): The second item or `Segment` data.
        what (type): The parameter type that will be swapped between both left and right.
    """
    from operand_rational import Position

    def __init__(self, left: Union[o.Operand, list, int] = 0, right: Union[o.Operand, list, int] = 1, what: type = Position):
        super().__init__([left, right, what])
        self._indexes = {
            'left': 0, 'right': 1, 'what': 2
        }

    def _process(self, operand: 'Container') -> 'Container':
        return operand.swap(*self._parameters)

class Reverse(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Reverse`

    Reverses the self list of items.

    Args:
        None
    """
    def __init__(self, ignore_empty_measures: bool = True):
        super().__init__(ignore_empty_measures)

    def _process(self, operand: 'Container') -> 'Container':
        return operand.reverse(self._parameters)

class Recur(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Recur`

    Calls the function on the successive items in a Xn+1 = Xn fashion (recursive),
    where n is the previous element and n+1 the next one.

    Args:
        recursion (Callable): recursive function.
        parameter (type): The type of parameter being processed by the recursive function.
    """
    from operand_rational import Duration

    def __init__(self, recursion: Callable = lambda d: d/2, parameter: type = Duration):
        super().__init__([recursion, parameter])
        self._indexes = {
            'recursion': 0, 'parameter': 1
        }

    def _process(self, operand: 'Container') -> 'Container':
        return operand.recur(*self._parameters)

class Rotate(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Rotate`

    Rotates a given parameter by a given offset, by other words,
    does a displacement for each Element in the Container list of
    a chosen parameter by the offset amount.

    Args:
        a (int): The offset amount of the list index, displacement.
        b (type): The type of parameter being displaced, rotated.
    """
    from operand_rational import Position

    def __init__(self, offset: int = 1, parameter: type = Position):
        super().__init__([offset, parameter])
        self._indexes = {
            'offset': 0, 'parameter': 1
        }

    def _process(self, operand: 'Container') -> 'Container':
        return operand.rotate(*self._parameters)

class Erase(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Erase`

    Erases all the given items in the present container and propagates the deletion
    of the same items for the containers above.

    Args:
        *parameters: After deletion, any given parameter will be operated with `<<` in the sequence given.
    """
    def _process(self, operand: 'Container') -> 'Container':
        return operand.erase(*self._parameters)


TypeComposition = TypeVar('TypeComposition', bound='Composition')  # TypeComposition represents any subclass of Operand

class CompositionProcess(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess`

    Processes applicable to any `Composition`.
    """
    def _process(self, operand: TypeComposition) -> TypeComposition:
        return operand

class Fit(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> Fit`

    Fits all the `Element` items into the respective Measure doing an optional tie if a `Note`.

    Args:
        tie_splitted_notes (bool): Does a tie of all splitted Notes.
    """
    from operand_rational import Length

    def __init__(self, tie_splitted_notes: bool = True):
        super().__init__(tie_splitted_notes)

    def _process(self, operand: TypeComposition) -> TypeComposition:
        return operand.fit(self._parameters)

class Loop(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> Loop`

    Creates a loop from the Composition from the given `Position` with a given `Length`.

    Args:
        position (Position): The given `Position` where the loop starts at.
        length (Length): The `Length` of the loop.
    """
    def __init__(self, position = 0, length = 4):
        super().__init__([position, length])
        self._indexes = {
            'position': 0, 'length': 1
        }

    def _process(self, composition: TypeComposition) -> TypeComposition:
        return composition.loop(*self._parameters)

class Drop(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> Drop`
    
    Drops from the `Composition` all `Measure`'s given by the numbers as parameters.

    Parameters
    ----------
    int(), list(), tuple(), set() : Accepts a sequence of integers as the Measures to be dropped.
    """
    def __init__(self, *measures):
        super().__init__(measures)

    def _process(self, operand: TypeComposition) -> TypeComposition:
        return operand.drop(*self._parameters)

class Crop(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> Crop`
    
    Crops from the `Composition` all `Measure`'s given by the numbers as parameters.

    Parameters
    ----------
    int(), list(), tuple(), set() : Accepts a sequence of integers as the Measures to be cropped.
    """
    def __init__(self, *measures):
        super().__init__(measures)

    def _process(self, operand: TypeComposition) -> TypeComposition:
        return operand.crop(*self._parameters)


class ClipProcess(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> ClipProcess`

    Processes applicable exclusively to `Clip` operands.
    """
    def __irrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return self._process(operand)
        else:
            print(f"Warning: Operand is NOT a `Clip`!")
        return super().__rrshift__(operand)

    def _process(self, operand: o.T) -> o.T:
        return operand

class Link(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Link`

    Adjusts the duration/length of each `Element` to connect to the start of the next element.
    For the last element in the clip, this is extended up to the end of the `Measure`.

    Args:
        ignore_empty_measures (bool): Ignores first empty Measures if `True`.
    """
    def __init__(self, ignore_empty_measures: bool = True):
        super().__init__(ignore_empty_measures)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.link(self._parameters)

class Stack(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Stack`

    Moves each Element to start at the finish position of the previous one.
    If it's the first element then its position becomes 0 or the staring of the first non empty `Measure`.

    Args:
        ignore_empty_measures (bool): Ignores first empty Measures if `True`.
    """
    def __init__(self, ignore_empty_measures: bool = True):
        super().__init__(ignore_empty_measures)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.stack(self._parameters)

class Quantize(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Quantize`

    Quantizes a `Clip` by a given amount from 0.0 to 1.0.

    Args:
        amount (float): The amount of quantization to apply from 0.0 to 1.0.
    """
    def __init__(self, amount: float = 1.0):
        super().__init__(amount)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.quantize(self._parameters)


class Decompose(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Decompose`

    Transform each element in its component elements if it's a composed element,
    like a chord that is composed of multiple notes, so, it becomes those multiple notes instead.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.decompose()


class Arpeggiate(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Arpeggiate`

    Distributes each element accordingly to the configured arpeggio by the parameters given.

    Args:
        parameters: Parameters that will be passed to the `Arpeggio` operand.
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.arpeggiate(self._parameters)


class Purge(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Purge`

    With time a `Clip` may accumulate redundant Elements, this method removes all those elements.

    Args:
        None.
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.purge()


class Stepper(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Stepper`

    Sets the steps in a Drum Machine for a given `Element`. The default element is `Note()` for None.

    Args:
        pattern (str): A string where the 1s in it set where the triggered steps are.
        element (Element): A element or any respective parameter that sets each element.
    """
    def __init__(self, pattern: str = "1... 1... 1... 1...", element: 'Element' = None):
        super().__init__([pattern, element])
        self._indexes = {
            'pattern': 0, 'element': 1
        }

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.stepper(*self._parameters)

class Automate(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Automate`

    Distributes the values given by the Steps pattern in a way very like the stepper Drum Machine fashion.

    Args:
        values (list[int]): The automation values at the triggered steps.
        pattern (str): A string where the 1s in it are where the triggered midi messages are.
        automation (Any): The type of automation wanted, like, Aftertouch, PitchBend or ControlChange,
        the last one being the default.
        interpolate (bool): Does an interpolation per `Step` between the multiple triggered steps.
    """
    def __init__(self, values: list[int] = [100, 70, 30, 100],
                 pattern: str = "1... 1... 1... 1...", automation: Any = "Pan", interpolate: bool = True):
        super().__init__([values, pattern, automation, interpolate])
        self._indexes = {
            'values': 0, 'pattern': 1, 'automation': 2, 'interpolate': 3
        }

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.automate(*self._parameters)

class Interpolate(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Interpolate`

    Interpolates the multiple values of a given `Automation` element by `Channel`.

    Args:
        None.
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.interpolate()

class Oscillate(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Oscillate`

    Applies for each item element the value at the given position given by the oscillator function at
    that same position.

    Args:
        amplitude (int): Amplitude of the wave.
        wavelength (float): The length of the wave in note value.
        offset (int): Sets the horizontal axis of the wave.
        phase (int): Sets the starting degree of the wave.
        parameter (type): The parameter used as the one being automated by the wave.
    """
    def __init__(self, amplitude: int = 63, wavelength: float = 1/1, offset: int = 0, phase: int = 0,
                 parameter: type = None):
        super().__init__([amplitude, wavelength, offset, phase, parameter])
        self._indexes = {
            'amplitude': 0, 'wavelength': 1, 'offset': 2, 'phase': 3, 'parameter': 4
        }

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.oscillate(*self._parameters)


class Tie(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Tie`

    Adjusts the pitch of successive notes to the previous one and sets all Notes as tied.

    Args:
        None.
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.tie()

class Join(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Join`

    Joins all same type notes with the same `Pitch` as a single `Note`, from left to right.

    Args:
        decompose (bool): If `True`, decomposes elements derived from `Note` first.
    """
    def __init__(self, decompose: bool = True):
        super().__init__([decompose])  # Has to have the ending "," to be considered a tuple
        self._indexes = {
            'decompose': 0
        }

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.join(*self._parameters)


class Slur(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Slur`

    Changes the note `Gate` in order to crate a small overlap.

    Args:
        gate (float): Can be given a different gate from 1.05, de default.
    """
    def __init__(self, gate: float = 1.05):
        super().__init__(gate)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.slur(self._parameters)

class Smooth(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Smooth`

    Adjusts the `Note` octave to have the closest pitch to the previous one.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.smooth()


class Flip(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Flip`

    `Flip` works like `Reverse` but it's agnostic about the Measure keeping the elements positional range.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.flip()

class Mirror(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Mirror`

    Mirror is similar to reverse but instead of reversing the elements position it reverses the
    Note's respective Pitch, like vertically mirrored.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.mirror()

class Invert(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Invert`

    `Invert` is similar to 'Mirror' but based in a center defined by the first note on which all notes are vertically mirrored.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.invert()


class Snap(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Snap`

    For `Note` and derived, it snaps the given `Pitch` to the one of the key signature.

    Args:
        up (bool): By default it snaps to the closest bellow pitch, but if set as True, \
            it will snap to the closest above pitch instead.
    """
    def __init__(self, up: bool = False):
        super().__init__(up)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.snap(self._parameters)

class Extend(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Extend`

    Extends (stretches) the given clip along a given length.

    Args:
        length (Length): The length along which the clip will be extended (stretched).
    """
    def __init__(self, length: 'Length' = None):
        super().__init__( length )

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.extend(self._parameters)

class Trim(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Trim`

    Trims the given clip at a given length.

    Args:
        length (Length): The length of the clip that will be trimmed.
    """
    def __init__(self, length: 'Length' = None):
        super().__init__( length )

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.trim(self._parameters)

class Cut(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Cut`

    Cuts (removes) the section of the clip from the start to the finish positions.

    Args:
        start (Position): Starting position of the section to be cut.
        finish (Position): Finish position of the section to be cut.
    """
    from operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__([start, finish])
        self._indexes = {
            'start': 0, 'finish': 1
        }

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.cut(*self._parameters)

class Select(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Select`

    Selects the section of the clip that will be preserved.

    Args:
        start (Position): Starting position of the section to be selected.
        finish (Position): Finish position of the section to be selected.
    """
    from operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__([start, finish])
        self._indexes = {
            'start': 0, 'finish': 1
        }

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.select(*self._parameters)

class Monofy(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Monofy`

    Cuts out any part of an element Duration that overlaps with the next element.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.monofy()

class Fill(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Fill`

    Adds up Rests to empty spaces (lengths) in a staff for each Measure.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.fill()


class PartProcess(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> PartProcess`

    Processes applicable exclusively to `Part` operands.
    """
    def __irrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Part):
            return self._process(operand)
        else:
            print(f"Warning: Operand is NOT a `Part`!")
        return super().__rrshift__(operand)

    def _process(self, operand: o.T) -> o.T:
        return operand

class SongProcess(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> SongProcess`

    Processes applicable exclusively to `Song` operands.
    """
    def __irrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Song):
            return self._process(operand)
        else:
            print(f"Warning: Operand is NOT a `Song`!")
        return super().__rrshift__(operand)

    def _process(self, operand: o.T) -> o.T:
        return operand
    


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
        self._quantization: Fraction                = Fraction(1/4) # Quantization is in Beats ratio
        self._time_signature: TimeSignature         = TimeSignature(4, 4)
        self._key_signature: ou.KeySignature        = ou.KeySignature()
        self._duration: Fraction                    = Fraction(1)   # Means 1 beat
        self._octave: int                           = 4
        self._velocity: int                         = 100
        self._controller: Controller                = Controller("Pan")
        self._channel_0: int                        = 0 # Default is channel 1 base 1 same as 0 base 0
        self._devices: list[str]                    = ["Microsoft", "FLUID", "Apple"]
        self._clocked_devices: list[str]            = []
        self._clock_ppqn: int                       = 24
        self._clock_stop_mode: int                  = 0
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

        # Volatile variable not intended to be user defined
        # (position_on, pitch_channel_0)
        self._notes_on: set[tuple[Fraction, int]] = set()
        # (position_on, pitch_channel_0, note_on)
        self._notes_off: dict[tuple[Fraction, int], dict] = {}


    def _add_note_on(self, position_on: Fraction, pitch_channel_0: int) -> bool:
        if (position_on, pitch_channel_0) in self._notes_on:
            return False
        self._notes_on.add((position_on, pitch_channel_0))
        return True

    def reset_notes_on(self) -> Self:
        self._notes_on = set()
        return self
    

    def _add_note_off(self, position_on: Fraction, position_off: Fraction, pitch_channel_0: int, note_off: dict) -> dict | None:
        tied_to: dict | None = None
        if (position_on, pitch_channel_0) in self._notes_off:
            note_off = tied_to = self._notes_off[(position_on, pitch_channel_0)]
        self._notes_off[(position_off, pitch_channel_0)] = note_off
        return tied_to
    
    def reset_notes_off(self) -> Self:
        self._notes_off = {}
        return self
    

    def reset(self, *parameters) -> Self:
        super().reset()
        self.reset_notes_on()
        self.reset_notes_off()
        return self << parameters
    
    
    def convert_time_to_measures(self, minutes: int = 0, seconds: int = 0) -> int:
        actual_bps: Fraction = settings._tempo / 60 # Beats Per Second
        time_seconds: int = 60 * minutes + seconds
        beats_per_measure: int = self._time_signature._top
        total_beats: Fraction = time_seconds * actual_bps
        total_measures: int = int(total_beats / beats_per_measure)
        return total_measures


    def beats_to_minutes(self, beats: Fraction) -> Fraction:
        return beats / self._tempo

    def __mod__(self, operand: o.T) -> o.T:
        import operand_element as oe
        match operand:
            case od.Pipe():
                match operand._data:
                    case of.Frame():            return self % od.Pipe( operand._data )
                    case ra.Tempo():            return ra.Tempo(self._tempo)
                    case ra.Quantization():     return operand._data << self._quantization
                    case ra.StepsPerNote():
                        return ra.StepsPerNote() << od.Pipe( 1 / self._quantization )
                    case TimeSignature():       return self._time_signature
                    case ra.BeatsPerMeasure():  return self._time_signature % od.Pipe( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.Pipe( ra.BeatNoteValue() )
                    case ou.KeySignature():     return self._key_signature
                    case ra.Duration():         return operand << self._duration
                    case ou.Octave():           return ou.Octave(self._octave)
                    case ou.Velocity():         return ou.Velocity(self._velocity)
                    case Controller():          return self._controller
                    case ou.Channel():          return ou.Channel(self._channel_0)
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
                return ra.StepsPerMeasure(self._time_signature % ra.BeatsPerMeasure() % Fraction() / self._quantization)
            case TimeSignature():       return self._time_signature.copy()
            case ra.BeatsPerMeasure():  return self._time_signature % ra.BeatsPerMeasure()
            case ra.BeatNoteValue():    return self._time_signature % ra.BeatNoteValue()
            case ra.NotesPerMeasure():  return self._time_signature % ra.NotesPerMeasure()
            case ou.KeySignature():     return self._key_signature.copy()
            case ou.Key() | ou.Quality() | int() | float() | Fraction() | str():
                                        return self._key_signature % operand
            # Calculated Values
            case list():
                return self._key_signature.get_scale() # Faster this way
            case ou.TonicKey():
                return ou.TonicKey( self._key_signature.get_tonic_key() )
            case ra.Duration():         return operand.copy() << self._duration
            case ou.Octave():           return ou.Octave(self._octave)
            case ou.Velocity():         return ou.Velocity(self._velocity)
            case Controller():          return self._controller.copy()
            case ou.Number():           return self._controller % ou.Number()
            case ou.Value():            return ou.Number.getDefaultValue(self % ou.Number() % int())
            case ou.Channel():          return ou.Channel(self._channel_0)
            case oc.ClockedDevices():   return oc.ClockedDevices(self._clocked_devices)
            case oc.Devices():          return oc.Devices(self._devices)
            case ou.PPQN():             return ou.PPQN(self._clock_ppqn)
            case ou.ClockStopModes():   return ou.ClockStopModes(self._clock_stop_mode)
            case oe.Clock():            return oe.Clock(self % oc.ClockedDevices(), self % ou.PPQN(), self % ou.ClockStopModes())
            case Settings():
                return operand.copy(self)
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
            and self._time_signature    == other._time_signature \
            and self._key_signature     == other._key_signature \
            and self._duration          == other._duration \
            and self._octave            == other._octave \
            and self._velocity          == other._velocity \
            and self._controller        == other._controller \
            and self._channel_0           == other._channel_0 \
            and self._devices           == other._devices \
            and self._clocked_devices   == other._clocked_devices \
            and self._clock_ppqn        == other._clock_ppqn \
            and self._clock_stop_mode   == other._clock_stop_mode
    

    def getPlaylist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        return [{ "time_ms": o.minutes_to_time_ms( self.beats_to_minutes(position_beats) ) }]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tempo"]            = self.serialize( self._tempo )
        serialization["parameters"]["quantization"]     = self.serialize( self._quantization )
        serialization["parameters"]["time_signature"]   = self.serialize( self._time_signature )
        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
        serialization["parameters"]["duration"]         = self.serialize( self._duration )
        serialization["parameters"]["octave"]           = self.serialize( self._octave )
        serialization["parameters"]["velocity"]         = self.serialize( self._velocity )
        serialization["parameters"]["controller"]       = self.serialize( self._controller )
        serialization["parameters"]["channel_0"]        = self.serialize( self._channel_0 )
        serialization["parameters"]["devices"]          = self.serialize( self._devices )
        serialization["parameters"]["clocked_devices"]  = self.serialize( self._clocked_devices )
        serialization["parameters"]["clock_ppqn"]       = self.serialize( self._clock_ppqn )
        serialization["parameters"]["clock_stop_mode"]  = self.serialize( self._clock_stop_mode )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tempo" in serialization["parameters"] and "quantization" in serialization["parameters"] and
            "time_signature" in serialization["parameters"] and "key_signature" in serialization["parameters"] and "duration" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "velocity" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "channel_0" in serialization["parameters"] and "devices" in serialization["parameters"] and
            "clocked_devices" in serialization["parameters"] and "clock_ppqn" in serialization["parameters"] and "clock_stop_mode" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempo             = self.deserialize( serialization["parameters"]["tempo"] )
            self._quantization      = self.deserialize( serialization["parameters"]["quantization"] )
            self._time_signature    = self.deserialize( serialization["parameters"]["time_signature"] )
            self._key_signature     = self.deserialize( serialization["parameters"]["key_signature"] )
            self._duration          = self.deserialize( serialization["parameters"]["duration"] )
            self._octave            = self.deserialize( serialization["parameters"]["octave"] )
            self._velocity          = self.deserialize( serialization["parameters"]["velocity"] )
            self._controller        = self.deserialize( serialization["parameters"]["controller"] )
            self._channel_0         = self.deserialize( serialization["parameters"]["channel_0"] )
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
                self._time_signature    << operand._time_signature
                self._key_signature     << operand._key_signature
                self._duration          = operand._duration
                self._octave            = operand._octave
                self._velocity          = operand._velocity
                self._controller        << operand._controller
                self._channel_0           = operand._channel_0
                self._devices           = operand._devices.copy()
                self._clocked_devices   = operand._clocked_devices.copy()
                self._clock_ppqn        = operand._clock_ppqn
                self._clock_stop_mode   = operand._clock_stop_mode
            case od.Pipe():
                match operand._data:
                    case ra.Tempo():            self._tempo = operand._data._rational
                    case ra.Quantization():     self._quantization = operand._data._rational
                    case TimeSignature():       self._time_signature = operand._data
                    case ou.KeySignature():     self._key_signature = operand._data
                    case ra.Duration():         self._duration = operand._data._rational
                    case ou.Octave():           self._octave = operand._data._unit
                    case ou.Velocity():         self._velocity = operand._data._unit
                    case Controller():          self._controller = operand._data
                    case ou.Channel():          self._channel_0 = operand._data._unit
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
                self._quantization = self._time_signature % ra.BeatsPerMeasure() / operand % Fraction()
            case TimeSignature() | ra.TimeSignatureParameter():
                                        self._time_signature << operand
            case ou.KeySignature() | ou.Key() | ou.Quality() | int() | float() | Fraction() | str():
                                        self._key_signature << operand
            case ra.Duration():         self._duration = operand._rational
            case ou.Octave():           self._octave = operand._unit
            case ou.Velocity():         self._velocity = operand._unit
            case Controller() | ou.Number():
                                        self._controller << operand
            case ou.Channel():          self._channel_0 = operand._unit
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


