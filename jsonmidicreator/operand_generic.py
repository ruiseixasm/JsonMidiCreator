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
from . import creator as c
from . import operand as o

from . import operand_label as ol
from . import operand_data as od
from . import operand_unit as ou
from . import operand_rational as ra

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
    Duration(Beats(1)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    """
    
    def __init__(self, *parameters):
        super().__init__()
        self._time_signature_reference: TimeSignature = None
        self._position_beats: Fraction      = Fraction(0)   # in Beats
        self._duration_beats: Fraction      = Fraction(1)   # in Beats
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
            case ra.Position():
                return operand.copy(self._time_signature_reference, self._position_beats)
            case ra.TimeUnit():
                # For TimeUnit only the `% operand` does the measure_module of it
                return ra.Position(self._time_signature_reference, self._position_beats) % operand
            case ra.Duration() | ra.Length():
                return operand.copy(self._time_signature_reference, self._duration_beats)
            case ra.TimeValue():
                return operand.copy(ra.Beats(self._time_signature_reference, self._duration_beats))
            case list():            return [self._position_beats, self._duration_beats]
            case int():             return self % ra.Measure() % int()
            case Segment():         return operand.copy(self % ra.Position())
            case float():           return self % ra.NoteValue() % float()
            case Fraction():        return self._duration_beats
            case Locus():           return operand.copy(self)
            case _:                 return super().__mod__(operand)


    def __eq__(self, other: o.Operand) -> bool:
        match other:
            case self.__class__():
                return self._position_beats == other._position_beats \
                    and self._duration_beats == other._duration_beats
            case Segment():
                return other == self % ra.Position()
            case od.Conditional():
                return other == self
            case ol.Null():
                return False    # Makes sure ol.Null ends up processed as False
        return self % other == other

    def __lt__(self, other: 'o.Operand') -> bool:
        match other:
            case self.__class__():
                if self._position_beats == other._position_beats:
                    return self._duration_beats > other._duration_beats # Longer duration comes first
                return self._position_beats < other._position_beats
            case _:
                return self % other < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        match other:
            case self.__class__():
                if self._position_beats == other._position_beats:
                    return self._duration_beats < other._duration_beats # Longer duration comes first
                return self._position_beats > other._position_beats
            case _:
                return self % other > other
    
    def net_start(self) -> ra.Position:
        return ra.Position(self, self._position_beats)

    def net_finish(self) -> ra.Position:
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
        from . import operand_element as oe
        from . import operand_container as oc
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        if self._time_signature_reference is None:
            match operand:
                case ra.Convertible():
                    self._time_signature_reference = operand._time_signature_reference
                case oe.Element() | oc.Composition():
                    self._time_signature_reference = operand._get_time_signature()
                case TimeSignature():
                    self._time_signature_reference = operand
        match operand:
            case Locus():
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
            case ra.TimeValue():
                self << ra.Duration(self._time_signature_reference, operand)
            case ra.Position():
                self._position_beats        = operand._rational
            case ra.TimeUnit():
                # The setting of the TimeUnit depends on the Element position
                self._position_beats        = ra.Position(self._time_signature_reference, self._position_beats, operand) % Fraction()
            case list():
                if operand:
                    self._position_beats = ra.Beats(self._time_signature_reference, operand[0])._rational
                    if len(operand) > 1:
                        duration_beats: Fraction = ra.Beats(self._time_signature_reference, operand[1])._rational
                        if duration_beats > 0:
                            self._duration_beats = duration_beats
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
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
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
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
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
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Fraction():
                self._position_beats = ra.Position(self._position_beats) * operand % Fraction()
                self._duration_beats = ra.Duration(self._duration_beats) * operand % Fraction()
            case int():
                self._position_beats = ra.Position(self._position_beats) * operand % Fraction()
            case float():
                self._duration_beats = ra.Duration(self._duration_beats) * operand % Fraction()
            case _:
                self_operand: any = self % operand
                self_operand *= operand # Generic `self_operand`
                self << self_operand
        return self

    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        if operand != Fraction(0):
            match operand:
                case Fraction():
                    self._position_beats = ra.Position(self._position_beats) / operand % Fraction()
                    self._duration_beats = ra.Duration(self._duration_beats) / operand % Fraction()
                case int():
                    self._position_beats = ra.Position(self._position_beats) / operand % Fraction()
                case float():
                    self._duration_beats = ra.Duration(self._duration_beats) / operand % Fraction()
                case _:
                    self_operand: any = self % operand
                    self_operand /= operand # Generic `self_operand`
                    self << self_operand
        return self

    def __ifloordiv__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        if operand != Fraction(0):
            match operand:
                case Fraction():
                    self._position_beats = ra.Position(self._position_beats) // operand % Fraction()
                    self._duration_beats = ra.Duration(self._duration_beats) // operand % Fraction()
                case int():
                    self._position_beats = ra.Position(self._position_beats) // operand % Fraction()
                case float():
                    self._duration_beats = ra.Duration(self._duration_beats) // operand % Fraction()
                case _:
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
                    case TimeSignature():       return self
                    case ra.BeatsPerMeasure():  return ra.BeatsPerMeasure() << self._top
                    case ra.BeatNoteValue():    return ra.BeatNoteValue() << 1 / self._bottom
                    case _:                     return super().__mod__(operand)
            # Direct Values
            case ra.BeatsPerMeasure():  return ra.BeatsPerMeasure() << self._top
            case ra.BeatNoteValue():    return ra.BeatNoteValue() << 1 / self._bottom
            # Calculated Values
            case ra.NotesPerMeasure():  return ra.NotesPerMeasure() << self._top / self._bottom
            case str():                 return f"{self._top}/{self._bottom}"
            case TimeSignature():       return operand.copy(self)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_signature: 'TimeSignature') -> bool:
        other_signature = self._tail_wrap(other_signature)    # Processes the tailed self operands if existent
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
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
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


class Dot(Generic):
    """`Generic -> Dot`

    A `Dot` is a pair of a `Value` (0 - 127) and a `Position` to be used with the element `Automation`.

    Args:
        position (any): The position relative to each value.
        value (int): The value for the automated operand from 0 to 127.
    """
    def __init__(self, position: any = 0, value: int = 0):
        self._position_beats: Fraction = ra.Position(position)._rational
        self._value: int = 0
        if isinstance(value, int):
            self._value = value
        super().__init__()

    def __eq__(self, other: 'Dot') -> bool:
        if isinstance(other, Dot):
            return self._value == other._value \
                and self._position_beats == other._position_beats
        return False
    
    def __lt__(self, other: 'Dot') -> bool:
        if isinstance(other, Dot):
            return self._position_beats < other._position_beats
        return False
    
    def __gt__(self, other: 'Dot') -> bool:
        if isinstance(other, Dot):
            return self._position_beats > other._position_beats
        return False
    
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case int():                 return self._value
                    case Fraction():            return self._position_beats
                    case _:                     return super().__mod__(operand)
            case int():                 return self._value
            case float() | Fraction() | ra.Convertible():
                return ra.Position(self._position_beats) % operand
            case _:                     return super().__mod__(operand)
            

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["value"]    = self.serialize( self._value )
        serialization["parameters"]["position"] = self.serialize( self._position_beats )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "value" in serialization["parameters"] and "position" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._value             = self.deserialize( serialization["parameters"]["value"] )
            self._position_beats    = self.deserialize( serialization["parameters"]["position"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Dot():
                super().__lshift__(operand)
                self._value = operand._value
                self._position_beats = operand._position_beats
            case od.Pipe():
                match operand._data:
                    case int():
                        self.value = operand._data
                    case Fraction():
                        self._position_beats = operand._data
                    case _:
                        super().__lshift__(operand)
            case int():
                self.value = operand
            case float() | Fraction() | ra.Convertible():
                self._position_beats = ra.Position(operand)._rational
            case list():
                if len(operand) == 2:
                    if isinstance(operand[0], int):
                        self._position_beats = ra.Position(operand[1])._rational
                        self._value = operand[0]
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, number: any) -> Self:
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case int():
                self._value += number
            case float() | Fraction() | ra.Convertible():
                self._position_beats += ra.Position(number)._rational
            case _:
                self.__iadd__(number)
        return self
    
    def __isub__(self, number: any) -> Self:
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case int():
                self._value -= number
            case float() | Fraction() | ra.Convertible():
                self._position_beats -= ra.Position(number)._rational
            case _:
                self.__isub__(number)
        return self


class Dots(Generic):
    """`Generic -> Dots`

    A series of `Dot` operands to be used in automation of `ControlChange`, `Aftertouch` and `PitchBend` elements.

    This is a constant operand intended to be used as a wrapper of information for the automation only.

    Args:
        list['Dot']([]): The Dot elements in a list to be set at once.
    """
    def __init__(self, *parameters):
        self._dots: list['Dot'] = []
        super().__init__(*parameters)

    def len(self) -> int:
        return len(self._dots)

    def __eq__(self, other: 'Dots') -> bool:
        if isinstance(other, Dots):
            self._dots.sort()
            other._dots.sort()
            return self._dots == other._dots
        return False
    
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():                return self._dots
                    case _:                     return super().__mod__(operand)
            case list():                return o.Operand.deep_copy(self._dots)
            case Dot():
                for i, dot in enumerate(self._dots):
                    if operand._position_beats == dot._position_beats:
                        return dot.copy()
                return ol.Null()
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["dots"] = self.serialize( self._dots )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "dots" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._dots = self.deserialize( serialization["parameters"]["dots"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Dots():
                super().__lshift__(operand)
                self._dots = operand._dots.copy() # Dots are constant, no need for deep copy
            case od.Pipe():
                match operand._data:
                    case list():
                        if all(isinstance(d, Dot) for d in operand._data):
                            self._dots = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                if all(isinstance(d, Dot) for d in operand):
                    self._dots = o.Operand.deep_copy(operand)
                elif all(isinstance(dl, list) for dl in operand) and all(len(dl) == 2 for dl in operand):
                    self._dots = []
                    for dot_l in operand:
                        self._dots.append(Dot(dot_l))
            case Dot():
                for dot in enumerate(self._dots):
                    if operand._position_beats == dot._position_beats:
                        dot._value = operand._value
                        return self
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, number: any) -> Self:
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case Dot():
                if number._position_beats < 0:  # Affects all Dots
                    self._dots = [
                        dot + number._value for dot in self._dots
                    ]
                else:
                    for dot in enumerate(self._dots):
                        if number._position_beats == dot._position_beats:
                            dot._value += number._value
                            return self
                    self._dots.append(number.copy())
            case list():    # Needs list comprehension
                if all(isinstance(d, Dot) for d in number):
                    self._dots = [
                        dot for dot in self._dots if dot not in number
                    ]
                    self._dots.extend(number)
            case _:
                super().__iadd__(number)
        return self
    
    def __isub__(self, number: any) -> Self:
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case Dot():
                if number._position_beats < 0:  # Affects all Dots
                    self._dots = [
                        dot - number._value for dot in self._dots
                    ]
                else:
                    for dot in enumerate(self._dots):
                        if number._position_beats == dot._position_beats:
                            dot._value -= number._value
                            return self
            case list():    # Needs list comprehension
                if all(isinstance(d, Dot) for d in number):
                    self._dots = [
                        dot for dot in self._dots if dot not in number
                    ]
            case _:
                super().__isub__(number)
        return self


class Pitch(Generic):
    """`Generic -> Pitch`

    A `Pitch` comes down the the absolute key in a full midi keyboard of 128 keys. To do so, processes and keeps many related \
    parameters like `Octave` and `Degree`.

    Parameters
    ----------
    KeySignature(settings) : Follows the Circle of Fifths with the setting of the amount of `Sharps` or `Flats`.
    Tonic(settings), None : The tonic key on which the `Degree` is based on.
    Octave(4), int : The octave on the keyboard with the middle C setting on the 4th octave.
    Degree(1), float : Degree sets the position of a note on a `Scale`, with designations like tonic, supertonic and dominant.
    Sharp(0), Flat : `Sharp` and `Flat` sets the respective accidental of a given note.
    Natural(False) : `Natural` disables the effects of `Sharp` and `Flat` and any accidental.
    list([]), Scale(), str, None : Sets the `Scale` to be used, `None` or `[]` uses the staff `KeySignature`.
    bool(True) : Sets if the given scale is processed as transposition (True) or as modulation (False).
    """
    def __init__(self, *parameters):
        self._key_signature: ou.KeySignature \
                                        = settings % ou.KeySignature()
        self._tonic_key: int            = self._key_signature.get_tonic_key()
        self._octave_0: int             = 5     # By default it's the 4th Octave, that's 5 in 0 based!
        self._degree_0: int             = 0     # By default it's Degree 1, that's 0 in 0 based
        self._accidental: int           = 0     # By default it has no accidental
        self._transposition: int        = 0     # By default it's it has no scale transposition
        self._scale: list[int]          = []
        super().__init__(*parameters)


    """
    PITCH CLASS PRINCIPLES FOR SETTING ITS KEYS
        * `Key()` manipulates `self._root_key` ONLY
        * `self._tonic_key` is CENTRAL, self._octave relates exclusively to it
        * `Transposition()`, MUST result in a `self._target_key()` at the same
            Octave than the `self._tonic_key` by manipulating ONLY the `self._root_key`
        * `self._root_key` when set DIRECTLY with `<<`, is set as is relative to the `self._tonic_key`
        * `<< Pipe(TonicKey())` does a `% 12` and a `// 2` for the `self._octave_0` but doesn't touch
            on the the `self._root_key`
        * `<< Pipe(RootKey())` neither does a `% 12` or a `// 2`, it's set straight away with its given value
        * `<< Pipe(Key())` doesn't exist, it does nothing at all
        * Setting with `<< Pipe()` the `KeySignature`, `Quality`, `Accidentals` or `Mode`, don't update any Key
        * Setting Keys or Semitones ONLY adjust the Degree and not the Octave, avoiding repeated offsets on repeated setting
    """


    def sharp(self, unit: bool = True) -> Self:
        return self << ou.Sharp(unit)

    def flat(self, unit: bool = True) -> Self:
        return self << ou.Flat(unit)

    def natural(self, unit: bool = True) -> Self:
        return self << ou.Natural(unit)

    def degree(self, unit: int = 1) -> Self:
        return self << ou.Degree(unit)


    """
    Auxiliary methods concerning the Degree
    """

    def _absolute_degree_0(self) -> 'ou.Degree':
        """
        Degrees are returned relative to the Tonic key in a Octave, this function returns the \
            absolute Degree rooted in the Octave 0.
        """
        return ou.Degree(self._degree_0, float(self._accidental)) + self._octave_0 * 7   # 7 degrees per octave


    def _tone_and_semitone(self, root_key: int) -> tuple[int, int]:
        signature_scale: list[int] = self._key_signature.get_scale()
        degree_0: int = 0
        accidental: int = 0
        tonic_to_root: int = root_key - self._tonic_key % 12
        # For Semitones
        if signature_scale[tonic_to_root % 12] == 0: # Not on the Scale
            # No two consecutive empty notes! (assumption for all scales!!)
            flats: bool = self._key_signature._unit < 0
            if flats:
                tonic_to_root += 1
                accidental = -1
            else:
                tonic_to_root -= 1
                accidental = 1
        # For Tones
        while tonic_to_root > 0:
            degree_0 += signature_scale[tonic_to_root % 12]
            tonic_to_root -= 1
        while tonic_to_root < 0:
            degree_0 -= signature_scale[tonic_to_root % 12]
            tonic_to_root += 1
        return degree_0, accidental

    def _transposition_tone_semitone(self, target_key: int) -> tuple[int, int]:
        degree_0: int = 0
        accidental: int = 0
        scale_degrees: int = 7  # Diatonic scales
        if self._scale:
            transposition_scale: list[int] = self._scale
            scale_degrees = sum(self._scale)
            first_key_int: int = self._get_root_key()
        else:
            transposition_scale: list[int] = self._key_signature.get_scale()
            first_key_int: int = self._tonic_key % 12   # Transposition becomes equivalent to degrees
        first_key_offset: int = target_key - first_key_int
        
        # For Semitones
        if transposition_scale[first_key_offset % 12] == 0:
            if first_key_offset < 0:
                accidental = -1   # Needs to go down further
            else:
                accidental = +1   # Needs to go up further
        # For Tones
        while first_key_offset > 0:
            degree_0 += transposition_scale[first_key_offset % 12]
            first_key_offset -= 1
        while first_key_offset < 0:
            degree_0 -= transposition_scale[first_key_offset % 12]
            first_key_offset += 1
        return degree_0 % scale_degrees, accidental

    """
    Elementary methods that represent variables alike
    """

    def _get_root_key(self) -> int:
        """Emulates the existing member variable `self._root_key`
        """
        tonic_to_root_key: int = 0
        if self._degree_0 != 0: # Optimization
            signature_scale: list[int] = self._key_signature.get_scale()
            tonic_to_root_key = Scale.transpose_key(self._degree_0, signature_scale)
        tonic_to_root_key += self._accidental
        return self._tonic_key % 12 + tonic_to_root_key

    def _set_root_key(self, root_key: int) -> Self:
        """Emulates the existing member variable `self._root_key`
        """
        # Can result in negative degrees, the `self._octave_0` remains the same
        degree_0, accidental = self._tone_and_semitone(root_key)
        self._degree_0 = degree_0
        self._accidental = accidental
        return self


    def _get_target_key(self) -> int:
        """Emulates the existing of the member variable `self._target_key`
        """
        target_key: int = 0
        if self._transposition == 0:
            target_key = self._get_root_key()
        elif self._scale:
            target_key = self._get_root_key() + Scale.transpose_key(self._transposition, self._scale)
        else:   # For KeySignature the Modulation is treated as a degree_0
            """
            Because in this case the transposition is no more than a degree increase,
            the tonic_offset is 0 for the new calculated degree
            """
            transposition_degree_0: float = self._degree_0 + self._transposition
            signature_scale: list[int] = self._key_signature.get_scale()
            tonic_to_target_key: int = Scale.transpose_key(transposition_degree_0, signature_scale)
            target_key = self._tonic_key % 12 + tonic_to_target_key + self._accidental
        return target_key

    def _set_target_key(self, target_key: int) -> Self:
        """Emulates the member variable `self._target_key` setting
        """
        if self._transposition:
            root_key: int = self._get_root_key()
            root_to_target_key: int = self._get_target_key() - root_key
            new_root_key: int = target_key - root_to_target_key
            self._set_root_key(new_root_key)    # Adjusts the Degree only
        else:
            self._set_root_key(target_key)  # target_key the same as root_key, no transposition
        return self


    def _get_octave_0(self) -> int:
        """
        Returns the Octave of the Target Key.
        """
        target_key: int = self._get_target_key()
        return self._octave_0 + target_key // 12

    def _set_octave_0(self, octave_0: int) -> Self:
        """
        Sets the Octave for the Target Key.
        """
        target_key: int = self._get_target_key()
        self._octave_0 = octave_0
        self._octave_0 -= target_key // 12
        return self


    def _get_chromatic_pitch(self) -> int:
        """
        Returns the final chromatic pitch with a midi value from 0 to 127.
        """
        octave_key: int = self._octave_0 * 12
        target_key: int = self._get_target_key()
        return octave_key + target_key

    def _set_chromatic_pitch(self, chromatic_pitch: int) -> Self:
        """
        Sets the final chromatic pitch with a midi value from 0 to 127.
        """
        self._octave_0 = chromatic_pitch // 12
        new_target_key: int = chromatic_pitch % 12
        self._set_target_key(new_target_key)
        return self


    def __eq__(self, other: any) -> bool:
        match other:
            case Pitch():
                return self._get_chromatic_pitch() == other._get_chromatic_pitch()
            case str():
                try:
                    string_degree = ou.Degree(int(other))
                    return self == string_degree
                except ValueError:
                    return self % other == other
            case od.Conditional():
                return other == self
            case _:
                return self % other == other
        return False
    
    def __lt__(self, other: any) -> bool:
        match other:
            case Pitch():
                return self._get_chromatic_pitch() < other._get_chromatic_pitch()
            case int() | float() | ou.Degree() | ou.Octave():
                return self % other < other
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        match other:
            case Pitch():
                return self._get_chromatic_pitch() > other._get_chromatic_pitch()
            case int() | float() | ou.Degree() | ou.Octave():
                return self % other > other
            case _:
                return super().__gt__(other)
        return False
    

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
                    case ou.KeySignature(): return self._key_signature
                    case ou.Octave():
                        return operand._data << od.Pipe(self._octave_0)
                    case ou.TonicKey():
                        return operand._data << od.Pipe(self._tonic_key)    # Must come before than Key()
                    case ou.Degree():   # Returns an absolute degree_0
                        operand._data._unit = self._degree_0
                        operand._data._accidental = self._accidental
                        return operand._data
                    case ou.Accidental() | ou.Natural():
                        return operand._data << self % operand
            
                    case ou.Semitone(): # Returns an absolute pitch_int Semitone
                        return operand._data << self % int()
                    case ou.Transposition():
                        return operand._data << od.Pipe(self._transposition)
                    case int():             return self._octave_0
                    case float():           return float(self._degree_0)
                    case Fraction():        return Fraction(self._transposition)
                    case Scale():           return operand._data << od.Pipe(self._scale)
                    case list():            return self._scale
                    case _:                 return super().__mod__(operand)
            case ou.KeySignature():
                return self._key_signature.copy()
            case ou.Quality() | ou.Mode() | ou.Accidentals():
                return self._key_signature % operand
            
            case int():
                return self % ou.Octave() % int()
            case float():
                return float(self._degree_0 + 1)
            case Fraction():
                return Fraction(self._transposition)
            
            case ou.Semitone():
                self_key = self % ou.Key()
                return operand.copy(self_key._unit)
            
            case ou.TonicKey():    # Must come before than Key()
                return ou.TonicKey(self._tonic_key)
            case ou.Key():
                key_operand = operand.copy()
                if isinstance(operand, ou.RootKey):
                    root_key: int = self._get_root_key()
                    key_operand << root_key
                else:
                    target_key: int = self._get_target_key()
                    key_operand << target_key
                if self._accidental:
                    key_operand._flattened = self._accidental < 0
                    key_operand._enharmonic = True
                else:
                    key_operand._flattened = self._key_signature._unit < 0
                    key_operand._enharmonic = self._key_signature.is_enharmonic(key_operand._unit)
                return key_operand
            
            case ou.Octave():
                return ou.Octave(self._get_octave_0() - 1)  # Formal octave starts at -1 Octave
            case ou.Degree():
                if self._degree_0 < 0:
                    return ou.Degree(self._degree_0, float(self._accidental))
                return ou.Degree(self._degree_0 + 1, float(self._accidental))
            case ou.Accidental() | ou.Natural():
                return self % ou.Degree() % operand
            
            case ou.Transposition():
                return operand.copy(self._transposition)
            case Scale():
                return Scale(self._scale)
            case list():
                return self._scale.copy()
            case str():
                key: str = self % ou.Key() % str()
                octave: str = str(self % ou.Octave() % int())
                return key + octave
            
            case Pitch():
                return operand.copy(self)
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:

        serialization = super().getSerialization()
        serialization["parameters"]["key_signature"]    = self.serialize( self._key_signature )
        serialization["parameters"]["tonic_key"]        = self.serialize( self._tonic_key )
        serialization["parameters"]["octave_0"]         = self.serialize( self._octave_0 )
        serialization["parameters"]["degree_0"]         = self.serialize( self._degree_0 )
        serialization["parameters"]["accidental"]       = self.serialize( self._accidental )
        serialization["parameters"]["transposition"]    = self.serialize( self._transposition )
        serialization["parameters"]["scale"]            = self.serialize( self._scale )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key_signature" in serialization["parameters"] and "tonic_key" in serialization["parameters"] and
            "octave_0" in serialization["parameters"] and "degree_0" in serialization["parameters"] and "accidental" in serialization["parameters"] and
            "transposition" in serialization["parameters"] and "scale" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._key_signature = self.deserialize( serialization["parameters"]["key_signature"] )
            self._tonic_key     = self.deserialize( serialization["parameters"]["tonic_key"] )
            self._octave_0      = self.deserialize( serialization["parameters"]["octave_0"] )
            self._degree_0      = self.deserialize( serialization["parameters"]["degree_0"] )
            self._accidental    = self.deserialize( serialization["parameters"]["accidental"] )
            self._transposition = self.deserialize( serialization["parameters"]["transposition"] )
            self._scale         = self.deserialize( serialization["parameters"]["scale"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Pitch():
                super().__lshift__(operand)
                self._key_signature         << operand._key_signature
                self._tonic_key             = operand._tonic_key
                self._octave_0              = operand._octave_0
                self._degree_0              = operand._degree_0
                self._accidental            = operand._accidental
                self._transposition         = operand._transposition
                self._scale                 = operand._scale.copy()
            case od.Pipe():
                match operand._data:
                    case ou.KeySignature(): # Preserves the chromatic_pitch
                        self._key_signature = operand._data

                    case ou.TonicKey():    # Must come before than Key()
                        self._octave_0 = operand._data._unit // 12
                        self._tonic_key = operand._data._unit % 12

                    case ou.Degree():   # Sets an absolute degree_0
                        self._degree_0 = operand._data._unit
                        self._accidental = operand._data._accidental
                    case ou.Accidental() | ou.Natural():
                        self._accidental = ou.Degree(operand._data)._accidental
            
                    case ou.Octave():
                        self._octave_0 = operand._data._unit    # Based 0 octave
                    case int():
                        self._octave_0 = operand
                    case float():
                        self._degree_0 = int(operand)
                    case Fraction():
                        self._transposition = int(operand._data)
                    case ou.Semitone(): # Sets an absolute pitch
                        self << od.Pipe(ou.Key(operand._data._unit))
                    case ou.Transposition():
                        self._transposition = operand._data._unit
                    case Scale():
                        self._scale = operand._data._scale
                    case list():
                        self._scale = operand._data
                    case str():
                        self._degree_0 = abs((self % od.Pipe( ou.Degree() ) << ou.Degree(operand._data))._unit) - 1 # 0 based
                        self._tonic_key = ou.Key(self._tonic_key, operand._data)._unit
                    case _:
                        super().__lshift__(operand)

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            # Setting of the KeySignature and respective parameters
            case ou.KeySignature(): # Preserves the Semitone
                original_semitone = self % ou.Semitone()
                self._key_signature << operand
                self._tonic_key = self._key_signature.get_tonic_key()   # Setting a Key Signature adjusts the Tonic Key accordingly
                self << original_semitone
            case ou.Quality() | ou.Mode() | ou.Accidentals():
                self._key_signature << operand
                self._tonic_key = self._key_signature.get_tonic_key()   # Setting a Key Signature adjusts the Tonic Key accordingly

            case ou.Semitone():
                self << ou.Key(operand._unit)

            case int():
                self << ou.Octave(operand)
            case float():
                if operand == 0.0:
                    self._degree_0 = 0
                    self._accidental = 0
                else:
                    # Sets just the degree, NOT the accidental!
                    self << ou.Degree(int(operand), float(self._accidental))
            case Fraction():
                self << ou.Transposition(operand)
                    
            case ou.Octave():
                self._set_octave_0(operand._unit + 1)   # Formal octave starts at -1 Octave
            case ou.Degree():
                self._accidental = operand._accidental
                if operand._unit > 0:
                    # No implicit Octave offset (Repeated sets with `<<` don't change Octave)
                    self._degree_0 = operand._unit - 1
                elif operand == ou.Degree(0):
                    # Resets the degree to I (tonic)
                    self._tonic_key = self._key_signature % ou.Key() % int()
                    self._degree_0 = 0
                elif operand._unit < 0:
                    self._degree_0 = operand._unit  # Negative remains negative!
                # A Degree with Just an accidental defined can set just that!
            case None:  # Works as a reset
                self._tonic_key = self._key_signature % ou.Key() % int()
                # Resets the degree to I
                self._degree_0 = 0
                self._accidental = 0
                self._transposition = 0

            # ADJUSTING KEYS DIRECTLY KEEPS THE SAME OCTAVE
            case ou.TonicKey():    # Must come before than Key()
                if operand._unit < 0:
                    self._tonic_key = self._key_signature % ou.Key() % int()
                else:
                    self._tonic_key = operand._unit % 12
            case ou.RootKey():
                self._set_root_key(operand._unit)
            case ou.Key():
                self._set_target_key(operand._unit)

            case ou.Transposition():
                self._transposition = operand._unit

            case dict():
                for octave, value in operand.items():
                    self << value << ou.Octave(octave)

            case ou.DrumKit():
                self << ou.Degree()     # Makes sure no Degree different of Tonic is in use
                self._set_chromatic_pitch(ou.Key(operand)._unit) # Sets the key number regardless KeySignature or Scale!

            case ou.Accidental() | ou.Natural():
                self._accidental = ou.Degree(operand)._accidental
            
            case Scale():
                self._scale = operand % list()
            case list():
                self._scale = operand.copy()

            case str():
                string: str = operand.strip()
                if string == "#":
                    self << ou.Sharp()
                elif string == "b":
                    self << ou.Flat()
                elif string == "n":
                    self << ou.Natural()
                else:
                    self << ou.Degree(string) # Safe, doesn't change the octave
                    target_key: int = self._get_target_key()
                    new_key_operand = ou.Key(target_key, string)
                    if new_key_operand != target_key:
                        self << new_key_operand
                    if len(operand) > 1:    # Single value shouldn't set the Octave
                        self << (self % ou.Octave() << string)
                    self << Scale(od.Pipe(self._scale), operand)
            case tuple():
                for single_operand in operand:
                    self << single_operand
            case _:
                super().__lshift__(operand)
        return self


    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Pitch():
                actual_semitone: int = self._get_chromatic_pitch()
                added_pitch: int = operand._unit
                new_pitch: int = actual_semitone + added_pitch
                self._set_chromatic_pitch(new_pitch)
            case ou.Semitone():
                actual_semitone = self % ou.Semitone()
                new_semitone = actual_semitone + operand
                self << new_semitone
            case ou.Octave():
                self._octave_0 += operand._unit
            case ou.Degree():
                self._degree_0 += operand._unit
                self._accidental += operand._accidental
                # Normalize degree
                offset_octave = self._degree_0 // 7
                if offset_octave:
                    self._degree_0 %= 7
                    self._octave_0 += offset_octave
            case ou.Accidental():
                self << self % ou.Degree() + operand
            case int():
                self.__iadd__(ou.Octave(operand))
            case float():
                self += ou.Degree(int(operand))
            case str():
                self += ou.Degree(operand)
            case Fraction():
                self += ou.Transposition(operand)
            case ou.Transposition() | ou.Tones():
                self._transposition += operand._unit

            case ou.TonicKey():
                self._tonic_key += operand._unit
                self._octave_0 += self._tonic_key // 12
                self._tonic_key %= 12   # The Tonic Key is always a % 12 (principles)
            case ou.RootKey():
                actual_root_key = self % ou.RootKey()
                new_root_key = actual_root_key + operand
                self << new_root_key
            case ou.Key():
                actual_key = self % ou.Key()
                new_root_key = actual_key + operand
                self << new_root_key

            case dict():
                for octave, value in operand.items():
                    self += value
                    self += ou.Octave(octave)
        return self
    
    def __isub__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Pitch():
                actual_pitch: int = self._get_chromatic_pitch()
                added_pitch: int = operand._unit
                new_pitch: int = actual_pitch - added_pitch
                self._set_chromatic_pitch(new_pitch)
            case ou.Semitone():
                actual_semitone = self % ou.Semitone()
                new_semitone = actual_semitone - operand
                self << new_semitone
            case ou.Octave():
                self._octave_0 -= operand._unit
            case ou.Degree():
                self._degree_0 -= operand._unit
                self._accidental -= operand._accidental
                # Normalize degree
                offset_octave = self._degree_0 // 7
                if offset_octave:
                    self._degree_0 %= 7
                    self._octave_0 += offset_octave
            case ou.Accidental():
                self << self % ou.Degree() - operand
            case int():
                self.__isub__(ou.Octave(operand))
            case float():
                self -= ou.Degree(int(operand))
            case str():
                self -= ou.Degree(operand)
            case Fraction():
                self -= ou.Transposition(operand)
            case ou.Transposition() | ou.Tones():
                self._transposition -= operand._unit

            case ou.TonicKey():
                self._tonic_key -= operand._unit
                self._octave_0 += self._tonic_key // 12
                self._tonic_key %= 12   # The Tonic Key is always a % 12 (principles)
            case ou.RootKey():
                actual_root_key = self % ou.RootKey()
                new_root_key = actual_root_key - operand
                self << new_root_key
            case ou.Key():
                actual_key = self % ou.Key()
                new_root_key = actual_key - operand
                self << new_root_key

            case dict():
                for octave, value in operand.items():
                    self -= value
                    self -= ou.Octave(octave)
        return self


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
        self_pitch: int = self._get_chromatic_pitch()
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
            case Controller():
                return operand.copy(self)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
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
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
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
    def root_key_degree_0(tonic_key: int, root_key: int, flats: bool = False,
                        scale: list[int] | tuple[int] = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)) -> ou.Degree:
        degree = ou.Degree()
        if len(scale) == 12 and sum(scale) > 0:
            tonic_key %= 12
            accidental: int = 0
            while scale[(root_key + accidental - tonic_key) % 12] == 0:
                if flats:
                    accidental -= 1
                else:
                    accidental += 1
            degree._accidental = accidental
            root_key -= accidental
            steps: int = 0
            while root_key > tonic_key:
                root_key -= 1
                steps += scale[(root_key - tonic_key) % 12]
            while root_key < tonic_key:
                root_key += 1
                steps -= scale[(root_key - tonic_key) % 12]
            degree._unit = steps
        return degree

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
    def sharps_or_flats_picker(tonic_key: int = 0, picker_scale: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]) -> list[int]:
        """
        This method returns all the Sharps or Flats for a given `tonic_key` on a specified `picker_scale`.

        For example, `Scale.sharps_or_flats_picker(2)` will return `[+1, +0, +0, +0, +0, +1, +0, +0, +0, +0, +0, +0]`.

        """
        major_scale: tuple[int] = ou.KeySignature._major_scale
        sharps_or_flats: list[int] = [0] * 12
        major_key: int = 0
        for picker_key in range(12):
            if picker_scale[picker_key] == 1:
                # There is always a white key after a black one (diatonic scales)
                major_key += 1 ^ major_scale[(tonic_key + major_key) % 12]
                sharps_or_flats[(tonic_key + major_key) % 12] = picker_key - major_key
                major_key += 1 # Moves to the next key to be available
        total_accidentals: int = sum(sharps_or_flats)
        if major_scale[tonic_key % 12] == 0 and total_accidentals < -6:
            sharps: list[int] = [0] * 12
            major_key = -1  # Starts by assuming a sharp (it's the case)
            for picker_key in range(12):
                if picker_scale[picker_key] == 1:
                    # There is always a white key after a black one (diatonic scales)
                    major_key += 1 ^ major_scale[(tonic_key + major_key) % 12]
                    sharps[(tonic_key + major_key) % 12] = picker_key - major_key
                    major_key += 1 # Moves to the next key to be available
            return sharps
        return sharps_or_flats
    

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

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
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
                self_scale = Scale.get_scale(operand)
                if len(self_scale) == 12:
                    self._scale = list(self_scale)
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
    

    _names: tuple[tuple[str]] = (
        ("Chromatic", "chromatic"),
        #                                                               START OF 7 KEYS/DEGREES SCALES
        # Diatonic Scales
        ("Major", "Maj", "maj", "M", "Ionian", "ionian"),
        ("Dorian", "dorian"),
        ("Phrygian", "phrygian"),
        ("Lydian", "lydian"),
        ("Mixolydian", "mixolydian"),
        ("minor", "min", "m", "Aeolian", "aeolian"),
        ("Locrian", "locrian"),
        # Other Scales
        ("Harmonic", "harmonic"),
        ("Melodic", "melodic"),
        #                                                               END OF 7 KEYS/DEGREES SCALES
        ("octatonic_hw"),
        ("octatonic_wh"),
        ("pentatonic_maj", "Pentatonic"),
        ("pentatonic_min", "pentatonic"),
        ("Diminished", "diminished"),
        ("Augmented", "augmented"),
        ("Blues", "blues"),
        ("Whole-tone", "Whole tone", "Whole", "whole")
    )

    _scales: tuple[tuple[int]] = (
    #       Db    Eb       Gb    Ab    Bb
    #       C#    D#       F#    G#    A#
    #    C     D     E  F     G     A     B
        (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        #                                                               START OF 7 KEYS/DEGREES SCALES
        # Diatonic Scales
        (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1),   # Major
        (1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0),   # Dorian
        (1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0),   # Phrygian
        (1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1),   # Lydian
        (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0),   # Mixolydian
        (1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0),   # minor (Aeolian)
        (1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0),   # Locrian
        # Other Scales
        (1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1),   # Harmonic
        (1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1),   # Melodic
        #                                                               END OF 7 KEYS/DEGREES SCALES
        (1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0),   # Octatonic HW
        (1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1),   # Octatonic WH
        (1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0),   # Pentatonic Major
        (1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0),   # Pentatonic minor
        (1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0),   # Diminished
        (1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1),   # Augmented
        (1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0),   # Blues
        (1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0)    # Whole-tone
    )

    _tonics: tuple[int] = (
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
    )

    @staticmethod
    def get_tonic_key(scale: list[int]) -> int:
        return Scale._tonics[ max(0, Scale.get_scale_number( scale )) ]

    def get_diatonic_scale(mode: int = 1) -> list[int]:
        return Scale._scales[mode]

    @staticmethod
    def get_scale_number(scale: int | str | list = 0) -> int:
        match scale:
            case int():
                total_scales = len(Scale._scales)
                if scale >= 0 and scale < total_scales:
                    return scale
            case str():
                scale_name = scale.strip()
                for index, names in enumerate(Scale._names):
                    for name in names:
                        if name == scale_name:
                            return index
            case list():
                if len(scale) == 12:
                    scale_tuple: tuple = tuple(scale)
                    for index, scale_mode in enumerate(Scale._scales):
                        if scale_tuple == scale_mode:
                            return index
        return -1

    @staticmethod
    def get_scale_name(scale: int | str | list = 0) -> str:
        scale_number = Scale.get_scale_number(scale)
        if scale_number < 0:
            return "Unknown Scale!"
        else:
            return Scale._names[scale_number][0]

    @staticmethod
    def get_scale(scale: int | str | list = 0) -> tuple[int]:
        if scale != [] and scale != -1 and scale != "":
            scale_number = Scale.get_scale_number(scale)
            if scale_number >= 0:
                return Scale._scales[scale_number]
        return tuple([])    # Has no scale at all


class PitchTransitions(Generic):
    """`Generic -> PitchTransitions`

    This `Operand` is an extracted of information concerning a `Composition`, mainly for Chords.

    Parameters
    ----------
    Sum(0) : The total amount of transitions from one pitch to a different one.
    Max(0) : The maximum difference in pitch change of all transitions.
    """
    def __init__(self, *parameters):
        self._sum: int = 0
        self._max: int = 0
        super().__init__(*parameters)


    def __eq__(self, other: any) -> bool:
        if isinstance(other, PitchTransitions):
            return self._sum == other._sum and self._max == other._max
        return False
    
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case ra.Sum():
                return ra.Sum(self._sum)
            case ra.Max():
                return ra.Max(self._max)
            case _:
                return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["sum"] = self.serialize(self._sum)
        serialization["parameters"]["max"] = self.serialize(self._max)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Element':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "sum" in serialization["parameters"] and "max" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._sum = self.deserialize(serialization["parameters"]["sum"])
            self._max = self.deserialize(serialization["parameters"]["max"])
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case PitchTransitions():
                super().__lshift__(operand)
                self._sum = operand._sum
                self._max = operand._max
            case ra.Sum():
                self._sum = operand % int()
            case ra.Max():
                self._max = operand % int()
            case _:
                return super().__mod__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case PitchTransitions():
                self._sum += operand._sum
                if operand._max > self._max:
                    self._max = operand._max
            case _:
                super().__iadd__(operand)
        return self


if TYPE_CHECKING:
    from operand_element import Note


class NoteEffect(Generic):
    """`Generic -> NoteEffect`

    A `NoteEffect` represents a manipulation of simultaneously played notes, like and Arpeggio.
    `NoteEffect` concern time changing behavior of notes, concerning their Position or Duration manipulation.

    Effects can be chained, their never set each other because they don't share common parameters, once chained,
    with the operator `**`, they are read from left to right.
    """
    
    def apply(self, notes: list['Note']) -> list['Note']:
        # Makes sure the next effect takes a sorted list of notes
        notes.sort()
        if isinstance(self._next_operand, NoteEffect):
            return self._next_operand.apply(notes)
        # Finally removes all notes are cleaned from any possible existing `NoteEffect`
        for single_note in notes:
            single_note._note_effect = None
        return notes


class Arpeggio(NoteEffect):
    """`Generic -> NoteEffect -> Arpeggio`

    An `Arpeggio` lets a group of simultaneously played notes to be played in sequence accordingly to the Arpeggio configuration.

    Parameters
    ----------
    Order(1), int : The notes changing order, with 1 being the "Up" order.
    Duration(1/16), float : The duration after which the next note is played following the set `Order`.
    Swing(0.5) : Sets the amount of time the note is effectively pressed relatively to its total duration.
    Chaos(SinX()) : For the `Order` 5, "Chaotic", it uses the set Chaotic `Operand`.
    """
    def __init__(self, *parameters):
        from . import operand_chaos as ch
        self._order: int = 1    # "Up" by default
        self._duration_beats: Fraction = Fraction(1, 4) # duration in beats, NOT note value
        self._swing: Fraction = Fraction(1, 2)
        self._chaos: ch.Chaos = ch.SinX()
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        from . import operand_chaos as ch
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Order():            return operand._data << od.Pipe( self._order )
                    case ra.Duration():         return operand._data << od.Pipe( self._duration_beats )
                    case ra.Swing():            return operand._data << od.Pipe( self._swing )
                    case ch.Chaos():            return self._chaos
                    case int():                 return self._order
                    case float():               return float( self._duration_beats )
                    case Fraction():            return self._duration_beats
                    case _:                     return super().__mod__(operand)
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

    def apply(self, notes: list['Note']) -> list['Note']:
        arpeggiated_notes: list['Note'] = []
        if self._order > 0 and len(notes) > 0:

            time_signature: TimeSignature = notes[0]._get_time_signature()
            note_start_position: ra.Position = notes[0] % od.Pipe( ra.Position() )
            arpeggio_length: ra.Length = notes[0] % od.Pipe( ra.Length() )
            arpeggio_end_position: ra.Position = arpeggio_length % ra.Position()
            note_length: ra.Length = ra.Length(time_signature, self._duration_beats)
            odd_length: ra.Length = note_length * 2 * self._swing
            even_length: ra.Length = note_length * 2 - odd_length
            
            sequenced_notes: list['Note'] = self._generate_sequence(notes)
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
        return super().apply(arpeggiated_notes)


    def arpeggiate_source(self, notes: list['Note'], start_position: ra.Position, arpeggio_length: ra.Length) -> list['Note']:
        if self._order > 0 and len(notes) > 0:

            note_start_position: ra.Position = start_position
            total_notes: int = len(notes)
            note_length: ra.Length = arpeggio_length / total_notes
            odd_length: ra.Length = note_length * 2 * self._swing
            even_length: ra.Length = note_length * 2 - odd_length
            
            sequenced_notes: list['Note'] = self._generate_sequence(notes)
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
        from . import operand_chaos as ch
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
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
        self._chaos *= number
        self._index += self.convert_to_int(number)    # keeps track of each iteration
        return self

class Repeat(NoteEffect):
    """`Generic -> NoteEffect -> Repeat`

    A `Repeat` repeats the note being pressed accordingly to a given Duration.

    Parameters
    ----------
    Duration(1/16), int, float : int for steps and float for note value.
    Swing(0.5) : Sets the amount of time the note is effectively pressed relatively to its total duration.
    Chaos(SinX()) : For the `Order` 5, "Chaotic", it uses the set Chaotic `Operand`.
    """
    def __init__(self, *parameters):
        from . import operand_chaos as ch
        self._duration_beats: Fraction  = Fraction(1, 4)    # duration in beats, NOT note value
        self._swing: Fraction           = Fraction(1, 2)
        self._chaos: ch.Chaos           = ch.SinX()
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Duration():     return operand._data << od.Pipe(self._count)
                    case ra.Swing():        return operand._data << od.Pipe(self._swing)
                    case _:                 return super().__mod__(operand)
            case ra.Duration():        return ra.Duration() << od.Pipe(self._count)
            case ra.Swing():        return ra.Swing() << od.Pipe(self._swing)
            # Returns the SYMBOLIC value of each note
            case ra.Duration():
                return operand.copy(self._duration_beats)
            case ra.TimeValue():
                return operand.copy(ra.Duration(self._duration_beats))
            case float():           return self % ra.NoteValue() % float()
            case int():             return self % ra.Steps() % int()
            case _:                 return super().__mod__(operand)


    def _repeat_note(self, single_note: 'Note') -> list['Note']:
        repeated_note: list[Note] = []
        single_note_position: Fraction = single_note._position_beats
        single_note_finish: Fraction = single_note_position + single_note._duration_beats
        repeat_duration: Fraction = self._duration_beats
        total_repeats: int = int(single_note._duration_beats / repeat_duration)
        self._swing = max(Fraction(0), self._swing, min(Fraction(1), self._swing))
        for repeat_i in range(total_repeats + 1):
            new_note = single_note.copy()
            repeated_note.append(new_note)
            if repeat_i % 2 == 0:
                new_note._duration_beats = repeat_duration * 2 * self._swing
                new_note._position_beats = single_note_position + repeat_duration * repeat_i
            else:
                new_note._duration_beats = repeat_duration * 2 * (1 - self._swing)
                new_note._position_beats = single_note_position + repeat_duration * (repeat_i + 1)
                new_note._position_beats -= new_note._duration_beats
            # Trim exceeding duration
            new_note_finish: Fraction = new_note._position_beats + new_note._duration_beats
            if new_note_finish >= single_note_finish:
                new_note._duration_beats -= new_note_finish - single_note_finish
                break
        return repeated_note

    def apply(self, notes: list['Note']) -> list['Note']:
        repeated_notes: list['Note'] = []
        for single_note in notes:
            repeated_notes.extend(self._repeat_note(single_note))
        return super().apply(repeated_notes)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["duration"] = self.serialize( self._duration_beats )
        serialization["parameters"]["swing"]    = self.serialize( self._swing )
        serialization["parameters"]["chaos"]    = self.serialize( self._chaos )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "duration" in serialization["parameters"] and "swing" in serialization["parameters"] and "chaos" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._duration_beats    = self.deserialize( serialization["parameters"]["duration"] )
            self._swing             = self.deserialize( serialization["parameters"]["swing"] )
            self._chaos             = self.deserialize( serialization["parameters"]["chaos"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Repeat():
                super().__lshift__(operand)
                self._duration_beats    = operand._duration_beats
                self._swing             = operand._swing
            case od.Pipe():
                match operand._data:
                    case ra.Duration():             self._duration_beats = operand._data._rational
                    case ra.Swing():                self._swing = operand._data._rational
                    case _:                         super().__lshift__(operand)
            case ra.Duration():
                if operand > 0:
                    self._duration = operand._rational
            case ra.TimeValue():
                if operand > 0:
                    self << ra.Duration(operand)
            case float():
                if operand > 0:
                    self << ra.NoteValue(operand)
            case int():
                if operand > 0:
                    self << ra.Steps(operand)
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case _:
                super().__lshift__(operand)
        return self

    def __imul__(self, number: int | float | Fraction | ou.Unit | ra.Rational) -> Self:
        self._initiated = True
        self._chaos *= number
        self._index += self.convert_to_int(number)    # keeps track of each iteration
        return self


class Overhang(NoteEffect):
    """`Generic -> NoteEffect -> Overhang`

    An `Overhang` extends the duration of all notes like if the sustain pedal was pressed all the time.
    It keeps retriggering the though, meaning, they are released only when they are retriggered.

    Parameters
    ----------
    Any(None) : The `Operand` to be used as input.
    """

    @staticmethod
    def _hanged_notes(notes: list['Note']) -> dict[int, list['Note']]:
        global_finish = Fraction(0)
        overhang_channel_pitch_notes: dict[int, list[Note]] = {} # channel_pitch based
        # Add the hanged notes and respective sustain duration
        for single_note in notes:
            note_finish: Fraction = single_note % ra.Finish() % Fraction()
            global_finish = max(global_finish, note_finish)
            channel_0: int = single_note._channel_0
            pitch: int = single_note._pitch._get_chromatic_pitch()
            channel_pitch: int = channel_0 << 7 | pitch # (4 bits, 7 bits)
            if channel_pitch in overhang_channel_pitch_notes:
                channel_pitch_notes: list[Note] = overhang_channel_pitch_notes[channel_pitch]
                channel_pitch_notes[-1] << ra.Finish(single_note % ra.Start())
                channel_pitch_notes.append(single_note.copy())
            else:
                overhang_channel_pitch_notes[channel_pitch] = [single_note.copy()]
        # Extend all notes to the global finish
        for channel_pitch_notes in overhang_channel_pitch_notes.items():
            channel_pitch_notes[-1] << ra.Finish(global_finish)
        return overhang_channel_pitch_notes


    @staticmethod
    def apply(notes: list['Note']) -> list['Note']:
        overhang_notes: list['Note'] = []
        overhang_channel_pitch_notes: dict[int, list[Note]] = Overhang._hanged_notes(notes)
        for channel_pitch_notes in overhang_channel_pitch_notes.items():
            for single_note in channel_pitch_notes:
                overhang_notes.append(single_note)
        return super().apply(overhang_notes)


class Coupler(NoteEffect):
    """`Generic -> NoteEffect -> Coupler`

    A `Coupler` couples each note with the respective notes set in a list by keeping all its parameters
    but `Pitch`, `Position` and `Duration`.

    Parameters
    ----------
    list([Note]) : Sets the notes to be coupled with.
    """
    def __init__(self, *parameters):
        self._notes: list['Note'] = []
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():            return self._notes
                    case _:                 return super().__mod__(operand)
            case list():            return self._notes
            case _:                 return super().__mod__(operand)


    def apply(self, notes: list['Note']) -> list['Note']:
        coupled_notes: list['Note'] = []
        for single_note in notes:
            note_pitch: Pitch = single_note._pitch
            note_locus: Locus = single_note % Locus()
            for coupling_note in self._notes:
                coupled_note = coupling_note.copy(note_pitch, note_locus)
                coupled_notes.append( coupled_note )
        coupled_notes.extend(notes)
        return super().apply(coupled_notes)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["notes"] = self.serialize( self._notes )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "notes" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._notes = self.deserialize( serialization["parameters"]["notes"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        from . import operand_element as oe
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Coupler():
                super().__lshift__(operand)
                self._notes = o.Operand.deep_copy(operand._notes)
            case od.Pipe():
                match operand._data:
                    case list():
                        if all(isinstance(note, Note) for note in operand._data):
                            self._notes = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                if all(isinstance(note, oe.Note) for note in operand):
                    self._notes = o.Operand.deep_copy(operand)
            case _:
                super().__lshift__(operand)
        return self


class OctaveExpansion(NoteEffect):
    """`Generic -> NoteEffect -> OctaveExpansion`

    An `OctaveExpansion` repeats the note being pressed on one or two octaves above or bellow.

    Parameters
    ----------
    int(1) : Sets the octaves above or bellow for positive or negative amount respectively.
    """
    def __init__(self, *parameters):
        self._octaves: int = 1
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case int():             return self._octaves
                    case _:                 return super().__mod__(operand)
            case int():             return self._octaves
            case _:                 return super().__mod__(operand)


    def apply(self, notes: list['Note']) -> list['Note']:
        octaves_notes: list['Note'] = []
        for single_note in notes:
            note_octave: ou.Octave = single_note % ou.Octave() + self._octaves
            octaves_notes.append( single_note.copy(note_octave) )
        octaves_notes.extend(notes)
        return super().apply(octaves_notes)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["octaves"] = self.serialize( self._octaves )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "octaves" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._octaves = self.deserialize( serialization["parameters"]["octaves"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case OctaveExpansion():
                super().__lshift__(operand)
                self._octaves = operand._octaves
            case od.Pipe():
                match operand._data:
                    case int():                     self._octaves = operand._data
                    case _:                         super().__lshift__(operand)
            case int():
                self._octaves = operand
            case _:
                super().__lshift__(operand)
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
                    case list():                return self._segment
                    case _:                     return super().__mod__(operand)
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
        from . import operand_element as oe
        from . import operand_container as oc
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
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
    
    def _direct_process(self, operand: o.T) -> o.T:
        return operand  # No copy

    def __rrshift__(self, operand: o.T) -> o.T:
        return self._direct_process( o.Operand.deep_copy(operand) )


    @staticmethod
    def _clocked_playlist(operand: o.T) -> list[dict]:
        from . import operand_element as oe
        from . import operand_container as oc

        playlist: list[dict] = []

        match operand:
            case oc.Composition() | oe.Element():
                if isinstance(operand, oc.Composition) and not operand._has_elements():
                    return playlist # exists with nothing right away
                # Generates the Clock data regardless, needed for correct JsonMidiPlayer processing
                clock_length: ra.Length = (operand.net_finish() % ra.Length()).roundMeasures()
                default_clock: oe.Clock = settings % oe.Clock()
                default_clock._duration_beats = ra.Duration(clock_length)._rational # The same staff will be given next
                playlist.extend( default_clock.getPlaylist( time_signature = operand._get_time_signature() ) )  # Clock Playlist
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


class SideEffect(Process):
    """`Generic -> Process -> SideEffect`

    This `Operand` can be inserted in a sequence of `>>` in order to apply as a side effect the chained
    data in the respective self data without changing the respective chained data sequence.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected inside the chained `>>` sequence.
    """
    def __init__(self, operand: o.Operand = None, process_it: bool = True):
        super().__init__()
        self._parameters = operand    # needs to keep the original reference (no copy)
        self._process_it: bool = process_it
    
    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.T) -> o.T:
        return self._direct_process(operand)

class LeftShift(SideEffect):
    """`Generic -> Process -> SideEffect -> LeftShift`

    Applies the `<<` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `<<` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def _direct_process(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process_it:
                self._parameters.__lshift__(operand)
            return operand
        return super().__rrshift__(operand)

class RightShift(SideEffect):
    """`Generic -> Process -> SideEffect -> RightShift`

    Applies the `>>` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `>>` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def _direct_process(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process_it:
                self._parameters.__rshift__(operand)
            return operand
        return super().__rrshift__(operand)

class IAdd(SideEffect):    # i stands for "inplace"
    """`Generic -> Process -> SideEffect -> IAdd`

    Applies the `+=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `+=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def _direct_process(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process_it:
                self._parameters.__iadd__(operand)
            return operand
        return super().__rrshift__(operand)

class ISub(SideEffect):
    """`Generic -> Process -> SideEffect -> ISub`

    Applies the `-=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `-=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def _direct_process(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process_it:
                self._parameters.__isub__(operand)
            return operand
        return super().__rrshift__(operand)

class IMul(SideEffect):
    """`Generic -> Process -> SideEffect -> IMul`

    Applies the `*=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `*=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def _direct_process(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process_it:
                self._parameters.__imul__(operand)
            return operand
        return super().__rrshift__(operand)

class IDiv(SideEffect):
    """`Generic -> Process -> SideEffect -> IDiv`

    Applies the `/=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `/=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def _direct_process(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process_it:
                self._parameters.__itruediv__(operand)
            return operand
        return super().__rrshift__(operand)


class ReadOnly(Process):
    """`Generic -> Process -> ReadOnly`

    A ReadOnly process is one that results in no change of the subject `Operand`.

    Parameters
    ----------
    Any(None) : A `Process` has multiple parameters dependent on the specific `Process` sub class.

    Returns:
        Any: All `Process` operands return the original left side `>>` input. Exceptions mentioned.
    """
    def __rrshift__(self, operand: o.T) -> o.T:
        return self._direct_process(operand)


class RightShift(ReadOnly):
    """`Generic -> Process -> ReadOnly -> RightShift`

    Applies the `>>` operation if process is `True`.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `>>` by the chained data sequence.
    bool(True) : By default, the the give `Operand` is targeted with `>>`.
    """
    def __init__(self, operand: o.Operand = None, process_it: bool = True):
        super().__init__()
        self._parameters = operand    # needs to keep the original reference (no copy)
        self._process_it: bool = process_it

    # CHAINABLE OPERATIONS

    def _direct_process(self, operand: o.T) -> o.T:
        if isinstance(self._parameters, o.Operand):
            if self._process_it:
                return self._parameters.__rshift__(operand)
            return operand
        return super().__rshift__(operand)


class Save(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Save`

    Saves all parameters' `Serialization` of a given `Operand` into a file.

    Parameters
    ----------
    None, str() : The filename of the Operand's serialization data.
    """
    def __init__(self, filename: str | None = None):
        super().__init__(filename)

    def _direct_process(self, operand: o.T) -> o.T:
        from . import operand_container as oc
        if isinstance(operand, o.Operand):
            file_path: str = self._parameters
            folder: str = settings._folder
            if not isinstance(file_path, str):
                if isinstance(operand, oc.Composition):
                    file_path = folder + operand.composition_filename() + "_save.json"
                else:
                    file_path = folder + "json/_Save_jsonMidiCreator.json"
            else: # Folder is just a prefix
                file_path = folder + file_path
            c.saveJsonMidiCreator(operand.getSerialization(), file_path)
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

    def _direct_process(self, operand: o.T) -> o.T:
        from . import operand_container as oc
        match operand:
            case o.Operand():
                file_path: str = self._parameters
                folder: str = settings._folder
                if not isinstance(file_path, str):
                    if isinstance(operand, oc.Composition):
                        file_path = folder + operand.composition_filename() + "_export.json"
                    else:
                        file_path = folder + "json/_Export_jsonMidiPlayer.json"
                else: # Folder is just a prefix
                    file_path = folder + file_path
                playlist: list[dict] = self._clocked_playlist(operand)
                c.saveJsonMidiPlay(playlist, file_path)
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

    def _direct_process(self, operand: o.T) -> o.T:
        from . import operand_element as oe
        from . import operand_container as oc
        # filepath and filename
        file_path: str = self._parameters
        folder: str = settings._folder
        if not isinstance(file_path, str):
            if isinstance(operand, oc.Composition):
                file_path = folder + operand.composition_filename() + "_render.mid"
            else:
                file_path = folder + "midi/_MidiExport_song.mid"
        else: # Folder is just a prefix
            file_path = folder + file_path
        # Rendering of the midi file
        match operand:
            case oc.Composition() | oe.Element():
                c.saveMidiFile(operand.getMidilist(), file_path)
                return operand
            case od.Line():
                line_clip = oc.Clip(operand)
                self.__rrshift__(line_clip)
            case str():
                line = od.Line(operand)
                self.__rrshift__(line)
        return super().__rrshift__(operand)



# Define ANSI escape codes for colors
RED = "\033[91m"
RESET = "\033[0m"
        
try:
    # pip install matplotlib
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseEvent
    from matplotlib.widgets import Button
    import matplotlib.patheffects as patheffects
except ImportError:
    print(f"{RED}Error: The 'matplotlib.pyplot' library is not installed.{RESET}")
    print("Please install it by running 'pip install matplotlib'.")
try:
    # pip install numpy
    import numpy as np
except ImportError:
    print(f"{RED}Error: The 'numpy' library is not installed.{RESET}")
    print("Please install it by running 'pip install numpy'.")



class Plot(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Plot`

    Plots the `Composition` content, Notes or the `Automation` if existent.

    Notes
    -----
    - The plotted `T` marks the Tonic Key of the Key Signature with the respective Sharps(#) or Flats(b)
    on the Y-axis, and they concern the immediate following Measures;
    - The Notes' Sharps and Flats plotted concern the Key Signature being used and NOT necessarily
    the Major Scale, in other words, they concern the `Degree` and NOT the `Key`.
        
    Args
    ----
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
                 composition: Optional['Composition'] = None, title: str | None = None):
        super().__init__([by_channel, block, pause, iterations, composition, title])
        self._indexes = {
            'by_channel': 0, 'block': 1, 'pause': 2, 'iterations': 3, 'composition': 5, 'title': 6
        }
        self._compositions: list[Composition] = []
        self._plot_lists: list[list] = []
        self._plot_checksums: list[str] = []
        self._by_channel: bool = by_channel
        self._iteration_index: int = 0
        self._composition = composition
        self._title: str = title
        self._block: bool = block
        self._pause: bool = pause
        self._iterations: int = iterations
        self._n_function: Callable[[int], 'Clip'] = None

    def __rrshift__(self, operand: o.T) -> 'Composition':
        from . import operand_unit as ou
        from . import operand_element as oe
        from . import operand_container as oc
        from . import operand_iterations as oi
        match operand:
            case oc.Composition():
                return self.plot_composition(operand)
            case oe.Element():
                element_clip = oc.Clip(operand)
                return self.__rrshift__(element_clip)
            case od.Line():
                line_clip = oc.Clip(operand)
                return self.__rrshift__(line_clip)
            case str():
                line = od.Line(operand)
                self.__rrshift__(line)
            case Scale():
                Scale.plot(self._parameters[1], operand % list())
            case ou.KeySignature():
                Scale.plot(self._parameters[1], operand % list(), operand % ou.Key(), operand % str())
            case oi.Iterations():
                if not isinstance(self._title, str):
                    self._title = operand.__class__.__name__
                self._n_function = operand.n_function
                return self.plot_iterations()
            case _:
                if isinstance(operand, Callable):
                    self._n_function = operand
                    return self.plot_iterations()
        return operand


    _channel_colors = [
        "#4CAF50",  # Green (starting point)    01
        "#2196F3",  # Blue                      02
        "#FF5722",  # Orange                    03
        "#9C27B0",  # Purple                    04
        "#FFEB3B",  # Bright Yellow             05
        "#FF9800",  # Amber                     06
        "#E91E63",  # Pink                      07
        "#00BCD4",  # Cyan                      08
        "#C7E99B",  # Light Green               09
        "#FFC107",  # Gold                      10
        "#4A5ED3",  # Indigo                    11
        "#FF5252",  # Light Red                 12
        "#2B184D",  # Deep Purple               13
        "#CDDC39",  # Lime                      14
        "#03A9F4",  # Light Blue                15
        "#FF4081",  # Hot Pink                  16
    ]

    _white_key_heigh: float = 1.0
    _black_key_heigh: float = 1.0
    _b3_key_heigh: float = 1.0
    _c4_key_heigh: float = 1.0
    _octave_heigh: float = 7 * _white_key_heigh + 5 * _black_key_heigh
    _white_above_black_heigh: float = _white_key_heigh - _black_key_heigh
    _previous_black_keys: tuple[int] = (0, 0, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5)

    @staticmethod
    def _pitch_to_y(pitch: float) -> float:
        y: float = 0.0
        pitch_int: int = int(pitch)
        octaves: int = pitch_int // 12
        y += octaves * Composition._octave_heigh
        if pitch_int > 59:
            y += Composition._b3_key_heigh - Composition._white_key_heigh
            if pitch_int > 60:
                y += Composition._c4_key_heigh - Composition._white_key_heigh
        pitch_octave: int = pitch_int % 12
        y += pitch_octave * Composition._white_key_heigh
        y -= Composition._previous_black_keys[pitch_octave] * Composition._white_above_black_heigh
        key_float: float = pitch - pitch_int
        key_heigh: float = Composition._white_key_heigh
        if pitch_int == 59:
            key_heigh = Composition._b3_key_heigh
        elif pitch_int == 60:
            key_heigh = Composition._c4_key_heigh
        elif o.is_black_key(pitch_int):
            key_heigh = Composition._black_key_heigh
        y += key_heigh * key_float
        return y

    @staticmethod
    def _y_to_pitch(y: float) -> float:
        pitch: float = 0.0
    
        return pitch


    def _plot_elements(self):
        """
        The method that does the heavy work of plotting
        """
        from . import operand_element as oe
        from . import operand_container as oc
        # The plotting is managed by the single and original Composition.
        plotlist: list[dict] = self._plot_lists[self._iteration_index]
        time_signature = self._compositions[self._iteration_index]._time_signature
        checksum_str: str = self._plot_checksums[self._iteration_index]

        self._ax.clear()

        beats_per_measure: Fraction = time_signature % ra.BeatsPerMeasure() % Fraction()
        quantization_beats: Fraction = settings._quantization    # Quantization is a Beats value already
        steps_per_measure: Fraction = beats_per_measure / quantization_beats

        chart_title: str = f"{self._title + " - " if self._title != "" else ""}" \
                        + f"{self._compositions[self._iteration_index].__class__.__name__}"
        # Chart title (TITLE)
        if isinstance(self, oc.Block):
            measure_position: int = int(self._position_beats / beats_per_measure)
            chart_title += f"({measure_position}) - "
        else:
            chart_title += " - "
        chart_title += f"{"Masked - " if self._compositions[self._iteration_index].is_masked() else ""}"
        if self._n_function is not None:
            chart_title += f"Iteration {self._iteration_index} of {len(self._compositions) - 1} - "
        chart_title += f"({checksum_str})"
        self._ax.set_title(chart_title)

        # Horizontal X-Axis, Time related (COMMON)

        composition_tempo: float = float(plotlist[0]["tempo"])
        # # 1. Disable autoscaling and force limits
        # self._ax.set_autoscalex_on(False)
        # current_min, current_max = self._ax.get_xlim()
        # self._ax.set_xlim(current_min, current_max * 1.03)
        self._ax.margins(x=0)  # Ensures NO extra padding is added on the x-axis

        # # By default it's 1 Measure long
        # last_position: Fraction = beats_per_measure
        # last_position_measures: Fraction = last_position / beats_per_measure
        # last_position_measure: int = int(last_position / beats_per_measure)
        # if last_position_measure != last_position_measures:
        #     last_position_measure += 1

        # No content assumed
        last_position: Fraction = Fraction(0)   # No content assumed
        last_position_measures: Fraction = last_position
        last_position_measure: int = 0


        # Vertical Y-Axis, Pitch/Value related (SPECIFIC)
        plot_channels: list[dict] = [ channel_dict["channels"] for channel_dict in plotlist if "channels" in channel_dict ]

        note_channels: list[int] = []
        automation_channels: list[int] = []

        for element_channel in plot_channels:
            for note_channel in element_channel["note"]:
                if note_channel not in note_channels:
                    note_channels.append(note_channel)
            for automation_channel in element_channel["automation"]:
                if automation_channel not in automation_channels:
                    automation_channels.append(automation_channel)

                    
        # Plot Notes
        if note_channels or not automation_channels:

            # As Channels (Drums)
            if self._by_channel:
                self._ax.set_ylabel("Channels")

                # Set MIDI channel ticks with Middle C in bold
                self._ax.set_yticks(range(17))  # Needs to accommodate all labels, so, it's 17
                self._ax.tick_params(axis='y', which='both', length=0)
                y_labels = ['R'] + [
                    channel_0 + 1 for channel_0 in range(16)
                ]
                self._ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')
                self._ax.set_ylim(0 - 0.5, 16 + 0.5)  # Ensure all channels fit

                # Where the corner Coordinates are defined
                self._ax.format_coord = lambda x, y: (
                    f"Time = {int(x / composition_tempo * 60 // 60)}'"
                    f"{int(x / composition_tempo * 60 % 60)}''"
                    f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
                    f"Measure = {int(x / beats_per_measure)}, "
                    f"Beat = {int(x % beats_per_measure)}, "
                    f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                    f"Channel = {round(y)}"
                )

                # Shade Odd Channels (1 based) VERTICAL AXIS
                for channel_0 in range(16):
                    if channel_0 % 2 == 1:
                        self._ax.axhspan(channel_0 - 0.5, channel_0 + 0.5, color='lightgray', alpha=0.5)

                note_plotlist: list[dict] = [ element_dict["note"] for element_dict in plotlist if "note" in element_dict ]

                if note_plotlist:

                    # Updates X-Axis data
                    last_position = max(note["position_off"] for note in note_plotlist)
                    last_position_measures = last_position / beats_per_measure
                    last_position_measure = int(last_position_measures) # Trims extra length
                    if last_position_measure != last_position_measures: # Includes the trimmed length
                        last_position_measure += 1  # Adds only if the end doesn't coincide

                    # Plot notes
                    for channel_0 in note_channels:
                        channel_color = Composition._channel_colors[channel_0]
                        channel_plotlist = [
                            channel_note for channel_note in note_plotlist
                            if channel_note["channel"] == channel_0
                        ]

                        for note in channel_plotlist:
                            if type(note["self"]) is oe.Rest:
                                # Available hatch patterns: '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'
                                color_alpha: float = 1.0
                                if note["masked"]:
                                    color_alpha = 0.2
                                self._ax.barh(y = 0.0, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]),
                                    height=0.30, color='none', hatch='', edgecolor='black', linewidth=1.0, linestyle='solid', alpha = color_alpha)
                            else:
                                bar_hatch: str = ''
                                line_style: str = 'solid'
                                if isinstance(note["self"], oe.KeyScale):
                                    line_style = 'dashed'
                                elif isinstance(note["self"], (oe.Rhythm, oe.Tuplet)):
                                    line_style = 'dotted'
                                edge_color: str = 'black'
                                if not note["enabled"]:
                                    edge_color = 'white'

                                color_alpha: float = round(0.3 + 0.7 * (note["velocity"] / 127), 2)

                                if note["velocity"] > 127:
                                    edge_color = 'red'
                                    color_alpha = 1.0
                                elif note["velocity"] < 0:
                                    edge_color = 'blue'
                                    color_alpha = 1.0

                                if note["masked"]:
                                    color_alpha = 0.2
                                    
                                self._ax.barh(y = note["channel"] + 1, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                        height=0.3, color=channel_color, hatch=bar_hatch, edgecolor=edge_color, linewidth=1.0, linestyle=line_style, alpha=color_alpha)

                                info: str = ""
                                if note["self"]._tied:
                                    info += " Tied"
                                if isinstance(note["self"]._note_effect, NoteEffect):
                                    info += " FX"
                                self._ax.text(float(note["position_on"]), note["pitch"] + 0.3, info, ha='left', va='bottom', fontsize=4,
                                    color='black',  # Outline color
                                    path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                                    alpha=color_alpha)
                        
                                if "middle_pitch" in note:
                                    self._ax.hlines(y=note["channel"] + 1, xmin=float(note["position_on"]), xmax=float(note["position_off"]), 
                                                    color='black', linewidth=0.5, alpha=color_alpha)
                                    
                else:  # Empty watermark
                    # Add watermark text in the center of the plot
                    self._ax.text(0.5, 0.5, 'EMPTY', 
                                transform=self._ax.transAxes,
                                fontsize=20,
                                color='gray',
                                alpha=0.5,
                                ha='center',
                                va='center',
                                fontweight='bold',
                                fontstyle='italic')
                    
                    # Optional: Add a subtle rectangle watermark
                    self._ax.axhspan(-0.5, 16.5, color='lightgray', alpha=0.1)
                
            # As Chromatic keys (Notes)
            else:

                self._ax.set_ylabel("Chromatic Keys")
                # Where the corner Coordinates are defined
                self._ax.format_coord = lambda x, y: (
                    f"Time = {int(x / composition_tempo * 60 // 60)}'"
                    f"{int(x / composition_tempo * 60 % 60)}''"
                    f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
                    f"Measure = {int(x / beats_per_measure)}, "
                    f"Beat = {int(x % beats_per_measure)}, "
                    f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                    f"Pitch = {int(y + 0.5)}"
                )

                # Solid line at y = 60 the Middle C
                self._ax.axhline(y=60 - 0.5, color='gray', linestyle='-', linewidth=1.0)

                note_plotlist: list[dict] = [ element_dict["note"] for element_dict in plotlist if "note" in element_dict ]

                if note_plotlist:

                    # Updates X-Axis data
                    last_position = max(note["position_off"] for note in note_plotlist)
                    last_position_measures = last_position / beats_per_measure
                    last_position_measure = int(last_position_measures) # Trims extra length
                    if last_position_measure != last_position_measures: # Includes the trimmed length
                        last_position_measure += 1  # Adds only if the end doesn't coincide

                    # PITCHES VERTICAL AXIS

                    # Get pitch range
                    min_pitch: int = int(min(note["pitch"] for note in note_plotlist) // 12 * 12)
                    max_pitch: int = int(max(note["pitch"] for note in note_plotlist) // 12 * 12 + 12)

                else:  # Empty watermark

                    # Updates X-Axis data
                    last_position_measures = last_position / beats_per_measure
                    last_position_measure = int(last_position_measures) # Trims extra length
                    if last_position_measure != last_position_measures: # Includes the trimmed length
                        last_position_measure += 1  # Adds only if the end doesn't coincide

                    # PITCHES VERTICAL AXIS

                    # Get pitch range
                    min_pitch: int = 60
                    max_pitch: int = 60

                    # Add watermark text in the center of the plot
                    self._ax.text(0.5, 0.5, 'EMPTY', 
                                transform=self._ax.transAxes,
                                fontsize=20,
                                color='gray',
                                alpha=0.5,
                                ha='center',
                                va='center',
                                fontweight='bold',
                                fontstyle='italic')
                    
                    # Optional: Add a subtle rectangle watermark
                    self._ax.axhspan(-0.5, 16.5, color='lightgray', alpha=0.1)


                pitch_range: int = max_pitch - min_pitch
                if pitch_range // 12 < 4:   # less than 4 octaves
                    middle_c_reference: int = 60    # middle C pitch
                    extra_octaves_range: int = 4 - pitch_range // 12
                    for _ in range(extra_octaves_range):
                        raised_top: int = max_pitch + 12
                        lowered_bottom: int = min_pitch - 12
                        if abs(raised_top - middle_c_reference) < abs(lowered_bottom - middle_c_reference):
                            max_pitch += 12
                        else:
                            min_pitch -= 12

                # Set MIDI note ticks with Middle C in bold
                self._ax.set_yticks(range(min_pitch, max_pitch + 1))
                self._ax.tick_params(axis='y', which='both', color='white')

                # # Only show tick marks for octaves (pitch % 12 == 0)
                # for tick in self._ax.yaxis.get_major_ticks():
                #     if tick.get_loc() % 12 != 0:  # If not an octave
                #         tick.tick1line.set_visible(False)  # Hide left tick
                #         tick.tick2line.set_visible(False)  # Hide right tick

                # Where the VERTICAL axis is defined - Chromatic Keys
                chromatic_keys: list[str] = ["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"]
                
                y_labels = [
                    chromatic_keys[pitch % 12] + (str(pitch // 12 - 1) if pitch % 12 == 0 else "")
                    for pitch in range(min_pitch, max_pitch + 1)
                ]  # Bold Middle C
                self._ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')

                # # Adjust alignment and shift
                # for label in self._ax.get_yticklabels():
                #     label.set_horizontalalignment("right")  # right-align text
                #     label.set_x(-0.005)                     # shift a bit left (tweak as needed)

                self._ax.set_ylim(min_pitch - 0.5, max_pitch + 0.5)  # Ensure all notes fit

                # Shade and shorten black keys and enlarge B3 and C4 keys
                for pitch in range(min_pitch, max_pitch + 1):
                    if o.is_black_key(pitch):   # Make it less taller, 0.6 instead of 1.0
                        self._ax.axhspan(pitch - 0.3, pitch + 0.3, color='lightgray', alpha=0.5)

                staff_modes: dict[int, int] = {}
                staff_tonic_keys: dict[int, int] = {}
                staff_sharps_or_flats: dict[int, list[int]] = {}

                # Plot notes per Channel
                for channel_0 in note_channels:
                    printed_channel_number: bool = False
                    channel_color = Plot._channel_colors[channel_0]
                    channel_plotlist = [
                        channel_note for channel_note in note_plotlist
                        if channel_note["channel"] == channel_0
                    ]
                    last_mode_measure: int = -1         # Tracker
                    last_tonic_key_measure: int = -1
                    last_sharps_or_flats_measure: int = -1

                    for note in channel_plotlist:
                        if isinstance(note["self"], oe.Rest):
                            # Available hatch patterns: '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'
                            color_alpha: float = 1.0
                            if note["masked"]:
                                color_alpha = 0.2
                            self._ax.barh(y = note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]),
                                height=0.40, color='none', hatch='', edgecolor='black', linewidth=1.0, linestyle='solid', alpha = color_alpha)
                        else:
                            if o.is_black_key(round(note["pitch"])):
                                bar_height: float = 0.25
                            else:
                                bar_height: float = 0.40
                            bar_hatch: str = ''
                            line_style: str = 'solid'
                            if isinstance(note["self"], oe.KeyScale):
                                line_style = 'dashed'
                            elif isinstance(note["self"], oe.Tuplet):
                                line_style = 'dotted'
                            edge_color: str = 'black'
                            if not note["enabled"]:
                                edge_color = 'white'

                            color_alpha: float = round(0.3 + 0.7 * (note["velocity"] / 127), 2)
                            if note["velocity"] > 127:
                                edge_color = 'red'
                                color_alpha = 1.0
                            elif note["velocity"] < 0:
                                edge_color = 'blue'
                                color_alpha = 1.0
                            
                            if note["masked"]:
                                color_alpha = 0.2

                            self._ax.barh(y=note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                    height=bar_height, color=channel_color, hatch=bar_hatch, edgecolor=edge_color, linewidth=1.0, linestyle=line_style, alpha=color_alpha)

                            info: str = ""
                            if note["self"]._tied:
                                info += " Tied"
                            if isinstance(note["self"]._note_effect, NoteEffect):
                                info += " FX"
                            self._ax.text(float(note["position_on"]), note["pitch"] + 0.3, info, ha='left', va='bottom', fontsize=4,
                                color='black',  # Outline color
                                path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                                alpha=color_alpha)
                        
                            if "middle_pitch" in note:
                                self._ax.hlines(y=note["middle_pitch"], xmin=float(note["position_on"]), xmax=float(note["position_off"]), 
                                                color='black', linewidth=0.5, alpha=color_alpha)

                            # note Measures to keep track of
                            note_measure: int = int(note["position_on"] // beats_per_measure)
                            flag_update_key_signature: bool = False

                            # Sets the Measure KeySignature if not yet set
                            if note_measure not in staff_modes: # Major, minor, Locrian, etc...

                                # Updates the last_mode_measure (Keeps track of the last measure staff data)
                                changed_last_mode_measure: int = last_mode_measure
                                while changed_last_mode_measure < note_measure and changed_last_mode_measure not in staff_modes:
                                    changed_last_mode_measure += 1
                                if changed_last_mode_measure < note_measure:
                                    last_mode_measure = changed_last_mode_measure
                            
                                mode_0: int = note["mode"]  # Mode here is the same as Major, minor, Locrian, etc...
                                if last_mode_measure < 0 or staff_modes[last_mode_measure] != mode_0:
                                    staff_modes[note_measure] = mode_0  # It's the Note KeySignature that is Plotted
                                    scale_mode: int = mode_0 % 9 + 1
                                    mode_marker: str = Scale._names[scale_mode][0]
                                    base_pitch: int = max_pitch - 12
                                    self._ax.text(float(note_measure * beats_per_measure) + 0.05, base_pitch + 12, mode_marker, ha='left', va='center', fontsize=6, color='black')
                                    flag_update_key_signature = True
                                    last_mode_measure = note_measure
                            else:
                                last_mode_measure = note_measure

                            if note_measure not in staff_tonic_keys:    # The T marking the Tonic
                                
                                # Updates the last_tonic_key_measure
                                changed_last_tonic_key_measure: int = last_tonic_key_measure
                                while changed_last_tonic_key_measure < note_measure and changed_last_tonic_key_measure not in staff_tonic_keys:
                                    changed_last_tonic_key_measure += 1
                                if changed_last_tonic_key_measure < note_measure:
                                    last_tonic_key_measure = changed_last_tonic_key_measure
                            
                                tonic_key: int = note["tonic_key"]
                                if last_tonic_key_measure < 0 or staff_tonic_keys[last_tonic_key_measure] != tonic_key:
                                    staff_tonic_keys[note_measure] = tonic_key
                                    base_pitch: int = max_pitch - 12
                                    self._ax.text(float(note_measure * beats_per_measure) + 0.05, base_pitch + tonic_key, 'T', ha='left', va='center', fontsize=5, color='black')
                                    flag_update_key_signature = True
                                    last_tonic_key_measure = note_measure
                            else:
                                last_tonic_key_measure = note_measure

                            if note_measure not in staff_sharps_or_flats: # Concerning the KeySignature, sharps, > 0 or flats, < 0, from -7 to +7
                                if flag_update_key_signature:
                                    diatonic_mode_0: int = staff_modes[last_mode_measure]
                                    diatonic_scale: list[int] = Scale.get_diatonic_scale(diatonic_mode_0 + 1)
                                    tonic_key: int = staff_tonic_keys[last_tonic_key_measure]
                                    scale_accidentals: list[int] = Scale.sharps_or_flats_picker(tonic_key, diatonic_scale)
                                    if last_sharps_or_flats_measure < 0 or staff_sharps_or_flats[last_sharps_or_flats_measure] != scale_accidentals:
                                        staff_sharps_or_flats[note_measure] = scale_accidentals
                                        
                                        for accidental_key, accidental in enumerate(scale_accidentals):
                                            chromatic_pitch: int = base_pitch
                                            if accidental > 0:
                                                accidental_key += 1
                                                chromatic_pitch += accidental_key % 12
                                                self._ax.text(float(note_measure * beats_per_measure) - 0.05, chromatic_pitch, '♯', ha='right', va='center', fontsize=10, fontweight='bold', color='black')
                                            elif accidental < 0:
                                                accidental_key -= 1
                                                chromatic_pitch += accidental_key % 12
                                                self._ax.text(float(note_measure * beats_per_measure) - 0.05, chromatic_pitch, '♭', ha='right', va='center', fontsize=10, fontweight='bold', color='black')

                                        last_sharps_or_flats_measure = note_measure
                            else:
                                last_sharps_or_flats_measure = note_measure


                            # Where the bar accidentals are plotted individually for each Note on the left side of them
                            if note["accidentals"]:
                                symbol: str = ''
                                if note["accidentals"] > 0: # Sharped
                                    symbol = '♯' * note["accidentals"]
                                else:                       # Flattened
                                    symbol = '♭' * (note["accidentals"] * -1)
                                y_pos: int = note["pitch"]
                                x_pos = float(note["position_on"]) - 0.15
                                self._ax.text(x_pos, y_pos, symbol, ha='center', va='center', fontsize=8, fontweight='bold',
                                    color='black',  # Outline color
                                    path_effects=[patheffects.withStroke(linewidth=1.4, foreground=channel_color)],
                                    alpha=color_alpha)

                            if not printed_channel_number:
                                y_pos: int = note["pitch"] + 0.2
                                x_pos = (float(note["position_on"]) + float(note["position_off"])) / 2
                                self._ax.text(x_pos, y_pos, channel_0 + 1, ha='center', va='bottom', fontsize=8,
                                    color='black',  # Outline color
                                    path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                                    alpha=color_alpha)
                                printed_channel_number = True
                                 
        # Plot Automations
        else:

            self._ax.set_ylabel("Automation Values (MSB)")
            # Where the corner Coordinates are defined
            self._ax.format_coord = lambda x, y: (
                f"Time = {int(x / composition_tempo * 60 // 60)}'"
                f"{int(x / composition_tempo * 60 % 60)}''"
                f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
                f"Measure = {int(x / beats_per_measure)}, "
                f"Beat = {int(x % beats_per_measure)}, "
                f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                f"Value = {int(y + 0.5)}"
            )

            automation_plotlist: list[dict] = [
                    element_dict["automation"] for element_dict in plotlist
                    if "automation" in element_dict and isinstance(element_dict["automation"]["self"], oe.Automatable)
                ]

            if automation_plotlist:

                # Updates X-Axis data
                last_position = max(automation["position"] for automation in automation_plotlist)
                last_position_measures = last_position / beats_per_measure
                last_position_measure = int(last_position_measures)
                if last_position_measure != last_position_measures:
                    last_position_measure += 1

                # Axis limits
                self._ax.set_ylim(-1, 128)
                # Ticks
                self._ax.set_yticks(range(0, 129, 8))

                # Dashed horizontal lines at multiples of 16 (except 64)
                for i in range(0, 129, 16):
                    if i != 64:
                        self._ax.axhline(y=i, color='gray', linestyle='--', linewidth=1)
                # Dashed line at y = 127
                self._ax.axhline(y=127, color='gray', linestyle='--', linewidth=1)
                # Solid line at y = 64
                self._ax.axhline(y=64, color='gray', linestyle='-', linewidth=1.5)

                # Plot automations
                for channel_0 in automation_channels:
                    channel_color = Composition._channel_colors[channel_0]
                    channel_plotlist = [
                        channel_automation for channel_automation in automation_plotlist
                        if channel_automation["channel"] == channel_0
                    ]

                    if channel_plotlist:

                        channel_plotlist.sort(key=lambda a: a['position'])

                        # Plotting point lists
                        x: list[float]  = []
                        y: list[int]    = []
                        for automation in channel_plotlist:
                            x.append( float(automation["position"]) )
                            y.append( automation["value"] )

                        # Stepped line connecting the points
                        self._ax.plot(x, y, linestyle='-', drawstyle='steps-post', color=channel_color, linewidth=0.5)
                        
                        if automation["masked"]:
                            color_alpha = 0.2
                        else:
                            color_alpha = 1.0

                        edge_color: str = 'black'
                        if not automation["enabled"]:
                            edge_color = 'white'
                        
                        # Actual data points
                        marker: str = 'o'
                        info: str = str(channel_0 + 1)
                        match automation["self"]:
                            case oe.ControlChange():
                                info += f".{automation["self"]._controller._number_msb}"
                            case oe.Aftertouch():
                                marker = 'v'
                            case _: # PitchBend
                                marker = 'P'

                        self._ax.plot(x, y, marker=marker, linestyle='None', color=channel_color,
                                    markeredgecolor=edge_color, markeredgewidth=1, markersize=6, alpha = color_alpha)

                        # Add the tailed line up to the end of the chart
                        x = [
                            float(channel_plotlist[-1]["position"]),
                            float(last_position_measure * beats_per_measure)
                        ]
                        y = [
                            channel_plotlist[-1]["value"],
                            channel_plotlist[-1]["value"]
                        ]

                        # Stepped line connecting the points
                        self._ax.plot(x, y, linestyle='-', drawstyle='steps-post', color=channel_color, linewidth=0.5)
                        # Actual data points
                        self._ax.plot(x, y, marker='None', linestyle='None', color=channel_color, markersize=6)

                        y_pos: int = automation["value"] + 2
                        x_pos = automation["position"]
                        self._ax.text(x_pos, y_pos, info, ha='center', va='bottom', fontsize=8,
                            color='black',  # Outline color
                            path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                            alpha=color_alpha)
                                        

        # Draw vertical grid lines based on beats and measures
        one_extra_subdivision: float = quantization_beats
        four_measures_multiple: int = max(4, (last_position_measure - 1) // 4 * 4 + 4)
        step_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), float(quantization_beats))
        beat_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), 1)
        measure_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), float(beats_per_measure))
    
        for measure_pos in measure_positions:
            self._ax.axvline(measure_pos, color='black', linestyle='-', alpha=1.0, linewidth=0.7)   # Measure lines
        for beat_pos in beat_positions:
            self._ax.axvline(beat_pos, color='gray', linestyle='-', alpha=0.5, linewidth=0.5)       # Beat lines
        for grid_pos in step_positions:
            self._ax.axvline(grid_pos, color='gray', linestyle='dotted', alpha=0.25, linewidth=0.5) # Step subdivisions

        # Set x-axis labels in 'Measure.Beat' format
        measure_labels = [
            f"{int(pos // float(beats_per_measure))}" for pos in measure_positions
        ]
        
        self._ax.set_xlabel(
            f"Measures played at {round(composition_tempo, 1)}bpm for "
            f"{int(last_position / composition_tempo * 60 // 60)}'"
            f"{int(last_position / composition_tempo * 60 % 60)}''"
            f"{int(last_position / composition_tempo * 60_000 % 1000)}ms "
            f"with a Time Signature of {time_signature._top}/{time_signature._bottom} "
            f"and a Quantization of {quantization_beats} Beat"
        )

        self._ax.set_xticks(measure_positions)  # Only show measure & beat labels
        if four_measures_multiple > 100:
            self._ax.set_xticklabels(measure_labels, fontsize=6, rotation=45)
        else:
            self._ax.set_xticklabels(measure_labels, rotation=0)
        self._fig.canvas.draw_idle()

        return None


    def _run_play(self, even = None, times: int = 1) -> Self:
        import threading
        iteration_self: Composition = self._compositions[self._iteration_index] * times
        threading.Thread(target=Play.play, args=(iteration_self,)).start()
        return self

    def _run_composition(self, even = None, times: int = 1) -> Self:
        import threading
        if isinstance(self._composition, Composition):
            iteration_self: Composition = self._compositions[self._iteration_index]
            iteration_composition: Composition = self._composition + iteration_self
            threading.Thread(target=Play.play, args=(iteration_composition * times,)).start()
        return self

    def _plot_filename(self, composition: 'Composition') -> str:
        # Process title separately (replace whitespace with underscores)
        processed_title = str(self._title).replace(" ", "_").replace("\t", "_").replace("\n", "_").replace("__", "_")
        composition_designations: list[str] = [
            processed_title,
            type(composition).__name__,
            f"{self._iteration_index}",
            f"{len(self._compositions) - 1}",
            o.checksum_to_string(composition.checksum())
        ]
        # 1. Filter empty strings and convert all parts to lowercase
        filtered_strings = [
            designation.strip().lower() 
            for designation in composition_designations 
            if designation
        ]
        # 2. Join with single underscore (no leading/trailing/double underscores)
        return "_".join(filtered_strings)

    def _run_save(self, even = None) -> Self:
        composition = self._compositions[self._iteration_index]
        file_name: str = self._plot_filename(composition) + "_save.json"
        composition >> Save(file_name)
        return self

    def _run_export(self, even = None) -> Self:
        composition = self._compositions[self._iteration_index]
        file_name: str = self._plot_filename(composition) + "_export.json"
        composition >> Export(file_name)
        return self

    def _run_render(self, even = None) -> Self:
        composition = self._compositions[self._iteration_index]
        file_name: str = self._plot_filename(composition) + "_render.mid"
        composition >> Render(file_name)
        return self

    @staticmethod
    def _disable_button(button: Button) -> Button:
        # Set disabled style
        button.label.set_color('lightgray')         # Light text
        button.ax.set_facecolor('none')             # No fill color
        button.hovercolor = 'none'
        for spine in button.ax.spines.values():
            spine.set_color('lightgray')
        return button

    @staticmethod
    def _enable_button(button: Button) -> Button:
        # Set enabled style
        button.ax.set_facecolor('white')
        button.hovercolor = 'gray'
        button.label.set_color('black')
        for spine in button.ax.spines.values():
            spine.set_color('black')
        return button

    def _on_move(self, event: MouseEvent) -> Self:
        if event.inaxes == self._ax:
            print(f"x = {event.xdata}, y = {event.ydata}")
        return self

    def _on_key(self, event: MouseEvent) -> Self:
        match event.key:
            case 'ctrl+p' | 'ctrl+enter':
                self._run_play(event, 4)
            case 'p' | 'enter':
                self._run_play(event)
            case 'ctrl+c' | 'ctrl+space' | 'ctrl+ ':
                self._run_composition(event, 4)
            case 'c' | ' ':
                self._run_composition(event)
            case 'S':
                self._run_save(event)
            case 'E':
                self._run_export(event)
            case 'R':
                self._run_render(event)
            case 'n':
                self._run_new(event)
            case ',':
                self._run_previous(event)
            case '.':
                self._run_next(event)
            case 'm':
                self._run_first(event)
            case '/' | "-" | ";":
                self._run_last(event)
        return self
    
    def _onclick(self, event: MouseEvent) -> Self:
        import threading
        from . import operand_element as oe
        from . import operand_container as oc
        if event.button == 3 and event.xdata is not None and event.ydata is not None:   # 1=left, 2=middle, 3=right
            composition = self._compositions[self._iteration_index]
            at_position_elements: list[oe.Element] = composition.at_position_elements(ra.Position(ra.Beats(event.xdata)))
            at_position_notes: list[oe.Note] = [
                single_note.copy() for single_note in at_position_elements
                if isinstance(single_note, oe.Note)
            ]
            if at_position_notes:
                if self._by_channel:
                    if 0 <= round(event.ydata - 1) < 16:
                        # Sort by Position in reverse instead
                        at_position_notes.sort(key=lambda note:note._position_beats * -1)
                        at_position_notes = [ at_position_notes[0] ]    # Just a single note is played
                        at_position_notes[0]._channel_0 = round(event.ydata - 1)
                        at_position_notes[0]._position_beats = Fraction(0)
                    else:
                        return self
                else:
                    # Sort by Pitch instead
                    at_position_notes.sort(key=lambda note:note._pitch._get_chromatic_pitch())
                    minimum_position: Fraction = None
                    plotting_pitch: int = int(event.ydata + 0.5)
                    for single_note in at_position_notes:
                        if minimum_position is None:
                            minimum_position = single_note._position_beats
                            root_pitch: int = single_note._pitch._get_chromatic_pitch()
                            single_note._pitch << plotting_pitch
                            plotting_pitch -= root_pitch
                        else:
                            if single_note._position_beats < minimum_position:
                                minimum_position = single_note._position_beats
                            single_note._pitch += plotting_pitch
                    for single_note in at_position_notes:
                        single_note._position_beats -= minimum_position
                    
                threading.Thread(target=Play.play, args=(Clip( od.Pipe(at_position_notes) ),)).start()
        return self


    def plot_composition(self, composition: 'Composition') -> Self:
        """
        Plots the `Note`s in a `Composition`, if it has no Notes it plots the existing `Automation` instead.

        Args:
            composition (Composition): A composition to be played together with the plotted one.

        Returns:
            Composition: Returns the presently plotted composition.
        """
        from . import operand_element as oe
        from . import operand_container as oc
        # First composition and its plotting (i = 0) it's always the self copy
        self._compositions      = [ composition.copy() ]   # Works with a forced copy (Read Only)
        self._plot_lists        = [ composition.getPlotlist() ]
        self._plot_checksums    = [ o.checksum_to_string(composition.checksum()) ]
        if not isinstance(self._title, str):
            self._title: str = composition % str()

        # Enable interactive mode (doesn't block the execution)
        plt.ion()

        # Where the window title is set too
        self._fig, self._ax = plt.subplots(num=self._title, figsize=(12, 6))
        # Replace handler
        try:
            # self._fig.canvas.mpl_disconnect(self._fig.canvas.manager.key_press_handler_id)
            # mpl.rcParams['keymap.back'].remove('left')
            # mpl.rcParams['keymap.forward'].remove('right')

            # Get the current keymap
            current_keymap: list = plt.rcParams['keymap.all_axes']
            # Remove the 'p' key binding
            current_keymap.remove('p')
            current_keymap.remove('s')
            # Update the rcParams
            plt.rcParams['keymap.all_axes'] = current_keymap
        except Exception as e:
            pass    # No need to print anything
            # print(f"Unable to disable default keys!")
        self._fig.canvas.mpl_connect('key_press_event', lambda event: self._on_key(event))
        self._fig.canvas.mpl_connect('button_press_event', lambda event: self._onclick(event))

        # Plot the Composition
        self._plot_elements()

        # Where the padding is set
        plt.tight_layout()

        plt.subplots_adjust(right=0.975)  # 2.5% right padding
        # Avoids too thick hatch lines
        plt.rcParams['hatch.linewidth'] = 3.00  # Where the HATCH thickness is set

        # Play Button Widget
        ax_button = plt.axes([0.979, 0.888, 0.015, 0.05])
        play_button = Button(ax_button, 'P', color='white', hovercolor='grey')
        play_button.on_clicked(self._run_play)

        # Composition Button Widget
        ax_button = plt.axes([0.979, 0.828, 0.015, 0.05])
        composition_button = Button(ax_button, 'C', color='white', hovercolor='grey')
        composition_button.on_clicked(self._run_composition)

        # Buttons are vertically spaced by 0.060

        # Save Button Widget
        ax_button = plt.axes([0.979, 0.528, 0.015, 0.05])
        save_button = Button(ax_button, 'S', color='white', hovercolor='grey')
        save_button.on_clicked(self._run_save)

        # Execution Button Widget
        ax_button = plt.axes([0.979, 0.468, 0.015, 0.05])
        export_button = Button(ax_button, 'E', color='white', hovercolor='grey')
        export_button.on_clicked(self._run_export)

        # Render Button Widget
        ax_button = plt.axes([0.979, 0.408, 0.015, 0.05])
        render_button = Button(ax_button, 'R', color='white', hovercolor='grey')
        render_button.on_clicked(self._run_render)

        if not isinstance(self._composition, oc.Composition):
            # Composition Button Widget
            self._disable_button(composition_button)

        if self._block and self._pause == 0:
            plt.show(block=True)
        elif self._pause > 0:
            plt.draw()
            plt.pause(self._pause)
        else:
            plt.show(block=False)

        return composition
    


    def _run_first(self, even = None) -> Self:
        if self._iteration_index > 0:
            self._iteration_index = 0
            self._plot_elements()
            self._enable_button(self._next_button)
            if self._iteration_index == 0:
                self._disable_button(self._previous_button)
        return self

    def _run_previous(self, even = None) -> Self:
        if self._iteration_index > 0:
            self._iteration_index -= 1
            self._plot_elements()
            self._enable_button(self._next_button)
            if self._iteration_index == 0:
                self._disable_button(self._previous_button)
        return self

    def _run_next(self, even = None) -> Self:
        if self._iteration_index < len(self._plot_lists) - 1:
            self._iteration_index += 1
            self._plot_elements()
            self._enable_button(self._previous_button)
            if self._iteration_index == len(self._plot_lists) - 1:
                self._disable_button(self._next_button)
        return self

    def _run_last(self, even = None) -> Self:
        if self._iteration_index < len(self._plot_lists) - 1:
            self._iteration_index = len(self._plot_lists) - 1
            self._plot_elements()
            self._enable_button(self._previous_button)
            if self._iteration_index == len(self._plot_lists) - 1:
                self._disable_button(self._next_button)
        return self


    def _run_new(self, even = None) -> Self:
        from . import operand_container as oc
        if callable(self._n_function):
            # Keeps iterating the root/seed composition
            new_iteration: oc.Composition = self._n_function(self._iteration_index + 1)
            if isinstance(new_iteration, oc.Composition):
                self._iteration_index = len(self._compositions)
                plotlist: list[dict] = new_iteration.getPlotlist()
                new_checksum_str: str = o.checksum_to_string(new_iteration.checksum())
                self._compositions.append(new_iteration)
                self._plot_lists.append(plotlist)
                self._plot_checksums.append(new_checksum_str)
                self._plot_elements()
                self._enable_button(self._previous_button)
                self._disable_button(self._next_button)
        return self


    def plot_iterations(self) -> Self:
        """
        Plots the `Note`s in a `Composition`, if it has no Notes it plots the existing `Automation` instead.

        Args:
            by_channel: Allows the visualization in a Drum Machine alike instead of by Pitch.
            block (bool): Suspends the program until the chart is closed.
            pause (float): Sets a time in seconds before the chart is closed automatically.
            iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
                this is dependent on a n_button being given.
            n_button (Callable): A function that takes a Composition to be used to generate a new iteration.
            composition (Composition): A composition to be played together with the plotted one.
            title (str): A title to give to the chart in order to identify it.

        Returns:
            Composition: Returns the presently plotted composition.
        """
        from . import operand_element as oe
        from . import operand_container as oc
        # First composition and its plotting (i = 0) it's always the self copy
        iteration_0: oc.Composition = self._n_function(0)
        self._compositions      = [ iteration_0 ]   # Works with a forced copy (Read Only)
        self._plot_lists        = [ iteration_0.getPlotlist() ]
        self._plot_checksums    = [ o.checksum_to_string(iteration_0.checksum()) ]
        if not isinstance(self._title, str):
            self._title: str = iteration_0 % str()

        if callable(self._n_function) and isinstance(self._iterations, int) and self._iterations > 1:
            for i in range(self._iterations):
                new_composition: Composition = self._n_function(i)
                new_plotlist: list[dict] = new_composition.getPlotlist()
                new_checksum_str: str = o.checksum_to_string(new_composition.checksum())
                self._compositions.append(new_composition)
                self._plot_lists.append(new_plotlist)
                self._plot_checksums.append(new_checksum_str)
                self._iteration_index += 1

        # Enable interactive mode (doesn't block the execution)
        plt.ion()

        # Where the window title is set too
        self._fig, self._ax = plt.subplots(num=self._title, figsize=(12, 6))
        # Replace handler
        try:
            # self._fig.canvas.mpl_disconnect(self._fig.canvas.manager.key_press_handler_id)
            # mpl.rcParams['keymap.back'].remove('left')
            # mpl.rcParams['keymap.forward'].remove('right')

            # Get the current keymap
            current_keymap: list = plt.rcParams['keymap.all_axes']
            # Remove the 'p' key binding
            current_keymap.remove('p')
            current_keymap.remove('s')
            # Update the rcParams
            plt.rcParams['keymap.all_axes'] = current_keymap
        except Exception as e:
            pass    # No need to print anything
            # print(f"Unable to disable default keys!")
        self._fig.canvas.mpl_connect('key_press_event', lambda event: self._on_key(event))
        self._fig.canvas.mpl_connect('button_press_event', lambda event: self._onclick(event))

        # Plot the Composition
        self._plot_elements()

        # Where the padding is set
        plt.tight_layout()

        plt.subplots_adjust(right=0.975)  # 2.5% right padding
        # Avoids too thick hatch lines
        plt.rcParams['hatch.linewidth'] = 3.00  # Where the HATCH thickness is set

        # Play Button Widget
        ax_button = plt.axes([0.979, 0.888, 0.015, 0.05])
        play_button = Button(ax_button, 'P', color='white', hovercolor='grey')
        play_button.on_clicked(self._run_play)

        # Composition Button Widget
        ax_button = plt.axes([0.979, 0.828, 0.015, 0.05])
        composition_button = Button(ax_button, 'C', color='white', hovercolor='grey')
        composition_button.on_clicked(self._run_composition)

        # Previous Button Widget
        ax_button = plt.axes([0.979, 0.768, 0.015, 0.05])
        self._previous_button = Button(ax_button, '<', color='white', hovercolor='grey')
        self._previous_button.on_clicked(self._run_previous)

        # Next Button Widget
        ax_button = plt.axes([0.979, 0.708, 0.015, 0.05])
        self._next_button = Button(ax_button, '>', color='white', hovercolor='grey')
        self._next_button.on_clicked(self._run_next)

        # New Button Widget
        ax_button = plt.axes([0.979, 0.648, 0.015, 0.05])
        new_button = Button(ax_button, 'N', color='white', hovercolor='grey')
        new_button.on_clicked(self._run_new)

        # Buttons are vertically spaced by 0.060

        # Save Button Widget
        ax_button = plt.axes([0.979, 0.528, 0.015, 0.05])
        save_button = Button(ax_button, 'S', color='white', hovercolor='grey')
        save_button.on_clicked(self._run_save)

        # Execution Button Widget
        ax_button = plt.axes([0.979, 0.468, 0.015, 0.05])
        export_button = Button(ax_button, 'E', color='white', hovercolor='grey')
        export_button.on_clicked(self._run_export)

        # Render Button Widget
        ax_button = plt.axes([0.979, 0.408, 0.015, 0.05])
        render_button = Button(ax_button, 'R', color='white', hovercolor='grey')
        render_button.on_clicked(self._run_render)

        # Previous Button Widget
        if self._iteration_index == 0:
            self._disable_button(self._previous_button)
        # Next Button Widget
        self._disable_button(self._next_button)

        if not callable(self._n_function):
            # New Button Widget
            self._disable_button(new_button)

        if not isinstance(self._composition, oc.Composition):
            # Composition Button Widget
            self._disable_button(composition_button)

        if self._block and self._pause == 0:
            plt.show(block=True)
        elif self._pause > 0:
            plt.draw()
            plt.pause(self._pause)
        else:
            plt.show(block=False)

        return self._compositions[self._iteration_index]


    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Plot():
                super().__lshift__(operand)
                self._parameters = operand._parameters.copy()
            case _:
                super().__lshift__(operand)
        return self

    def __imul__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        if isinstance(operand, int):
            self._parameters[self._indexes['iterations']] = operand
        return self



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
        from . import operand_element as oe
        from . import operand_container as oc
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
    def __init__(self, verbose: bool = False, plot: bool = False, block: bool = False, talkie_delay_ms: int = 500):
        super().__init__([verbose, plot, block, talkie_delay_ms])
        self._indexes = {
            'verbose': 0, 'plot': 1, 'block': 2, 'talkie_delay_ms': 3
        }

    def __rrshift__(self, operand: o.T) -> o.T:
        import threading
        from . import operand_element as oe
        from . import operand_container as oc
        match operand:
            case oc.Composition():
                if operand._items:
                    playlist: list[dict] = self._clocked_playlist(operand)  # Where the heavy lifting method is called
                    if self._parameters[1] and self._parameters[2]:
                        # Start the function in a new process
                        process = threading.Thread(target=c.jsonMidiPlay, args=(playlist, self._parameters[0], self._parameters[3]))
                        process.start()
                        operand >> Plot(self._parameters[2])
                    else:
                        if self._parameters[1] and not self._parameters[2]:
                            operand >> Plot(self._parameters[2])
                        c.jsonMidiPlay(playlist, self._parameters[0], self._parameters[3])
                else:
                    print(f"Warning: Trying to play an **empty** list!")
                return operand
            case oe.Element():
                playlist: list[dict] = self._clocked_playlist(operand)  # Where the heavy lifting method is called
                if self._parameters[1] and self._parameters[2]:
                    # Start the function in a new process
                    process = threading.Thread(target=c.jsonMidiPlay, args=(playlist, self._parameters[0], self._parameters[3]))
                    process.start()
                    operand >> Plot(self._parameters[2])
                else:
                    if self._parameters[1] and not self._parameters[2]:
                        operand >> Plot(self._parameters[2])
                    c.jsonMidiPlay(playlist, self._parameters[0], self._parameters[3])
                return operand
            case od.Line():
                line_clip = oc.Clip(operand)
                self.__rrshift__(line_clip)
            case str():
                line = od.Line(operand)
                self.__rrshift__(line)
            case od.Playlist():
                playlist: list[dict] = self._clocked_playlist(operand)  # Where the heavy lifting method is called
                c.jsonMidiPlay(playlist, self._parameters[0], self._parameters[3])
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

class Proxy(ReadOnly):
    """`Generic -> Process -> ReadOnly -> Proxy`

    Creates and returns a shallow copy of the left side `>>` Container.

    Parameters
    ----------
    Any(None) : The Parameters to be set on the shallow copied `Container`.

    Returns:
        Container: Returns a shallow copy of the left side `>>` operand.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        from . import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.shallow_copy(*self._parameters)
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

class Read(Process):
    """`Generic -> Process -> Read`

    Reads the keyboard input. Press and release SHIFT for each Element. Press ENTER to stop.

    Args:
        None
    """
    def __rrshift__(self, operand: o.T) -> o.T:
        from . import operand_element as oe
        if isinstance(operand, (oe.Element, ra.Tempo)):
            return self._direct_process(operand.copy())
        else:
            print(f"Warning: Operand is NOT an `Element` os a `Tempo`!")
        return operand

    def _direct_process(self, operand: o.T) -> o.T:
        from . import operand_element as oe
        if isinstance(operand, (oe.Element, ra.Tempo)):
            return self._direct_process(operand)
        else:
            print(f"Warning: Operand is NOT an `Element` os a `Tempo`!")
        return super().__rrshift__(operand)

    def _direct_process(self, operand: Union['Element', 'ra.Tempo']) -> Union['Clip', 'ra.Tempo']:
        return operand.read()


class ScaleProcess(Process):
    """`Generic -> Process -> ScaleProcess`
    """
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, Scale):
            return self._direct_process(operand.copy())
        return super().__rrshift__(operand)

    def _direct_process(self, operand: o.T) -> o.T:
        if isinstance(operand, Scale):
            return self._direct_process(operand)
        else:
            print(f"Warning: Operand is NOT a `Scale`!")
        return super().__rrshift__(operand)

    def _direct_process(self, operand: o.T) -> o.T:
        return operand

class Modulate(ScaleProcess):    # Modal Modulation
    """`Generic -> Process -> ScaleProcess -> Modulate`

    Modulate() is used to modulate the self Scale or Scale.
    
    Parameters
    ----------
    int(1) : Modulate a given Scale to 1 ("1st") as the default mode.
    """
    def __init__(self, mode: int | str = 1):
        from . import operand_unit as ou
        unit = ou.Mode(mode)._unit
        super().__init__(unit)

    # CHAINABLE OPERATIONS

    def _direct_process(self, operand: 'Scale') -> 'Scale':
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

    def _direct_process(self, operand: 'Scale') -> 'Scale':
        return operand.transpose(self._parameters)


class ContainerProcess(Process):
    """`Generic -> Process -> ContainerProcess`

    Processes applicable exclusively to `Container` operands.
    """
    def __init__(self, parameters: list = []):
        super().__init__(parameters)
        self._previous_item: Any = None
        
    def __rrshift__(self, operand: o.T) -> o.T:
        from . import operand_container as oc
        if isinstance(operand, oc.Container):
            return self._direct_process(operand.copy())
        print(f"Warning: Operand is NOT a `Container`!")
        return operand

    def _direct_process(self, operand: o.T) -> o.T:
        from . import operand_container as oc
        if isinstance(operand, oc.Container):
            return self._direct_process(operand)
        else:
            print(f"Warning: Operand is NOT a `Container`!")
        return super().__rrshift__(operand)

    def _direct_process(self, operand: o.T) -> o.T:
        return operand

class Sort(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Sort`

    Sorts the contained items by a given parameter type.

    Args:
        parameter (type): Defines the given parameter type to sort by.
        reverse (bool): Reverses the sorting if `True`.
    """
    from .operand_rational import Position

    def __init__(self, parameter: type = Position, reverse: bool = False):
        super().__init__([parameter, reverse])
        self._indexes = {
            'parameter': 0, 'reverse': 1
        }

    def _direct_process(self, operand: 'Container') -> 'Container':
        return operand.sort(*self._parameters)


class Filter(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Filter`

    A `Filter` works exactly like a `Mask` with the difference of keeping just \
        the matching items and deleting everything else.

    Args:
        condition (Any): Sets a condition to be compared with `==` operator.
    """
    def __init__(self, *conditions):
        super().__init__(conditions)

    def _direct_process(self, operand: 'Container') -> 'Container':
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

    def _direct_process(self, operand: 'Container') -> 'Container':
        return operand.operate(*self._parameters)


class Transform(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Transform`

    Transforms each item by wrapping it with the new operand type given.

    Args:
        operand_type (type): The type of `Operand` by which each item will be transformed into.
    """
    def __init__(self, operand_type: type = 'Note'):
        super().__init__(operand_type)

    def _direct_process(self, operand: 'Container') -> 'Container':
        return operand.transform(self._parameters)


class Swap(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Swap`

    This method swaps a given parameter type between two operands.

    Args:
        left (any): The first item or `Segment` data.
        right (any): The second item or `Segment` data.
        what (type): The parameter type that will be swapped between both left and right.
    """
    from .operand_rational import Position

    def __init__(self, left: Union[o.Operand, list, int] = 0, right: Union[o.Operand, list, int] = 1, what: type = Position):
        super().__init__([left, right, what])
        self._indexes = {
            'left': 0, 'right': 1, 'what': 2
        }

    def _direct_process(self, operand: 'Container') -> 'Container':
        return operand.swap(*self._parameters)

class Reverse(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Reverse`

    Reverses the self list of items.

    Args:
        None
    """
    def _direct_process(self, operand: 'Container') -> 'Container':
        return operand.reverse()

class Recur(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Recur`

    Calls the function on the successive items in a Xn+1 = Xn fashion (recursive),
    where n is the previous element and n+1 the next one.

    Args:
        recursion (Callable): recursive function.
        parameter (type): The type of parameter being processed by the recursive function.
    """
    from .operand_rational import Duration

    def __init__(self, recursion: Callable = lambda d: d/2, parameter: type = Duration):
        super().__init__([recursion, parameter])
        self._indexes = {
            'recursion': 0, 'parameter': 1
        }

    def _direct_process(self, operand: 'Container') -> 'Container':
        return operand.recur(*self._parameters)

class Rotate(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Rotate`

    Rotates a given parameter by a given right amount, by other words,
    does a displacement for each Element in the Container list of
    a chosen parameter by the given right amount. Clockwise.

    Args:
        right (int): The right amount of the list index, displacement.
        parameter (type): The type of parameter being displaced, rotated.
    """
    from .operand_rational import Position

    def __init__(self, right: int = 1, parameter: type = ra.Position):
        super().__init__([right, parameter])
        self._indexes = {
            'left': 0, 'parameter': 1
        }

    def _direct_process(self, operand: 'Container') -> 'Container':
        return operand.rotate(*self._parameters)

class Erase(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> Erase`

    Erases all the given items in the present container and propagates the deletion
    of the same items for the containers above.

    Args:
        *parameters: After deletion, any given parameter will be operated with `<<` in the sequence given.
    """
    def _direct_process(self, operand: 'Container') -> 'Container':
        return operand.erase(*self._parameters)


TypeComposition = TypeVar('TypeComposition', bound='Composition')  # TypeComposition represents any subclass of Operand

class CompositionProcess(ContainerProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess`

    Processes applicable to any `Composition`.
    """
    def _direct_process(self, operand: TypeComposition) -> TypeComposition:
        return operand


class Fit(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> Fit`

    Moves the `Position` of the following Elements to match the finish of the previous
    `Element` by keeping its finish Position, meaaning, by changing its `Duration`.

    Args:
        None
    """
    def _direct_process(self, operand: TypeComposition) -> TypeComposition:
        return operand.fit()


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

    def _direct_process(self, composition: TypeComposition) -> TypeComposition:
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

    def _direct_process(self, operand: TypeComposition) -> TypeComposition:
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

    def _direct_process(self, operand: TypeComposition) -> TypeComposition:
        return operand.crop(*self._parameters)


class ClipProcess(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> ClipProcess`

    Processes applicable exclusively to `Clip` operands.
    """
    def __init__(self, parameters: list = []):
        from . import operand_element as oe
        super().__init__(parameters)
        self._previous_item: oe.Element | None = None

    def _direct_process(self, operand: o.T) -> o.T:
        from . import operand_container as oc
        if isinstance(operand, oc.Clip):
            return self._direct_process(operand)
        else:
            print(f"Warning: Operand is NOT a `Clip`!")
        return super().__rrshift__(operand)

    def _direct_process(self, operand: o.T) -> o.T:
        return operand

class Link(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Link`

    Adjusts the `Duration` of each element to link its finish with the start of the next element.

    Args:
        None.
    """
    def __init__(self):
        super().__init__()

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.link()

class Stack(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Stack`

    Moves each Element to start at the finish `Position` of the previous one.

    Args:
        None.
    """
    def __init__(self):
        super().__init__()

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.stack()

class Close(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Close`
    
    Sets the finish `Position` of the last `Element` to match the end if its occupying `Measure`.

    Args:
        None.
    """
    def __init__(self):
        super().__init__()

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.close()

class Quantize(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Quantize`

    Quantizes a `Clip` by a given amount from 0.0 to 1.0.

    Args:
        amount (float): The amount of quantization to apply from 0.0 to 1.0.
        quantize_duration (bool): Includes the quantization of the `Duration` too.
    """
    def __init__(self, amount: float = 1.0, quantize_duration: bool = False):
        super().__init__((amount, quantize_duration))

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.quantize(*self._parameters)


class Decompose(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Decompose`

    Transform each element in its component elements if it's a composed element,
    like a chord that is composed of multiple notes, so, it becomes those multiple notes instead.

    Args:
        None
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.decompose()


class Arpeggiate(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Arpeggiate`

    Distributes each element accordingly to the configured arpeggio by the parameters given.

    Args:
        parameters: Parameters that will be passed to the `Arpeggio` operand.
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.arpeggiate(self._parameters)


class Purge(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Purge`

    With time a `Clip` may accumulate redundant Elements, this method removes all those elements.

    Args:
        None.
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
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

    def _direct_process(self, operand: 'Clip') -> 'Clip':
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

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.automate(*self._parameters)

class Interpolate(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Interpolate`

    Interpolates the multiple values of a given `Automation` element by `Channel`.

    Args:
        None.
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
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

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.oscillate(*self._parameters)


class Merge(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Merge`

    Adjusts the pitch of successive notes to the previous one and sets all Notes as tied.

    Args:
        None.
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.merge()

class Tie(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Tie`

    Adjusts the pitch of successive notes to the previous one and sets all Notes as tied.

    Args:
        None.
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
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

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.join(*self._parameters)


class Slur(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Slur`

    Changes the note `Gate` in order to crate a small overlap.

    Args:
        gate (float): Can be given a different gate from 1.05, de default.
    """
    def __init__(self, gate: float = 1.05):
        super().__init__(gate)

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.slur(self._parameters)

class Smooth(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Smooth`

    Adjusts each `Note` octave to have the closest pitch to the first, previous one or both.

    Args:
        algorithm_type (int): Sets the type of algorithm to be used accordingly to the next table:
            +------+---------------------------------------------------------------------------+
            | Type | Description                                                               |
            +------+---------------------------------------------------------------------------+
            | 1    | Considers both pitch distances, from the first note and the previous one. |
            | 2    | Considers only the previous note pitch distance.                          |
            | 3    | Considers only the first note pitch distance.                             |
            | 4    | Considers the middle_pitch in relation to the previous one.               |
            | 5    | Considers the middle_pitch in relation to the first note. (default)       |
            +------+---------------------------------------------------------------------------+
    """
    def __init__(self, algorithm_type: int = 5):
        super().__init__(algorithm_type)

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.smooth(self._parameters)


class Shift(ClipProcess):
    """`Generic -> Process -> ClipProcess -> Shift`

    Does a `Position` shift in a rotative fashion by doing a positional displacement of each `Element`
    in the `Clip` list by the given amount. Clockwise. It does the module of positions by `Length` Measures.

    Args:
        right (1): The right `Position` amount for the displacement. Numbers are equivalent to:        
            +----------+-------------+
            | Type     | Equivalency |
            +----------+-------------+
            | int      | Measure     |
            | float    | Step        |
            | Fraction | Beat        |
            +----------+-------------+
    """
    from .operand_rational import Position

    def __init__(self, right: Union['ra.Position', 'ra.TimeUnit', int, float, Fraction] = 1):
        super().__init__([right])
        self._indexes = {
            'right': 0
        }

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.shift(*self._parameters)


class Flip(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Flip`

    `Flip` works like `Reverse` but it's agnostic about the Measure keeping the elements positional range.

    Args:
        None
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.flip()

class Mirror(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Mirror`

    Mirror is similar to reverse but instead of reversing the elements position it reverses the
    Note's respective Pitch, like vertically mirrored.

    Args:
        by_degree (bool): If `True` a mirror by Degree accordingly to the Key Signature, similar to the typical Staff, if False, \
            does a chromatic mirror by pitch like in a piano roll. The default is `True`.
    """
    def __init__(self, by_degree: bool = True):
        super().__init__(by_degree)

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.mirror(self._parameters)

class Invert(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Invert`

    `invert` is similar to `Mirror` but based in a center defined by the first note on which all notes are vertically mirrored.

    Args:
        by_degree (bool): If `True` an inversion by Degree accordingly to the Key Signature, similar to the typical Staff, if False, \
            does a chromatic inversion by pitch like in a piano roll. The default is `True`.
    """
    def __init__(self, by_degree: bool = True):
        super().__init__(by_degree)

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.invert(self._parameters)


class Snap(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Snap`

    For `Note` and derived, it snaps the given `Pitch` to the one of the key signature.

    Args:
        up (bool): By default it snaps to the closest bellow pitch, but if set as True, \
            it will snap to the closest above pitch instead.
    """
    def __init__(self, up: bool = False):
        super().__init__(up)

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.snap(self._parameters)

class Extend(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Extend`

    Extends (stretches) the given clip along a given length.

    Args:
        length (Length): The length along which the clip will be extended (stretched).
    """
    def __init__(self, length: 'Length' = None):
        super().__init__( length )

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.extend(self._parameters)

class Trim(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Trim`

    Trims the given clip at a given length.

    Args:
        length (Length): The length of the clip that will be trimmed.
    """
    def __init__(self, length: 'Length' = None):
        super().__init__( length )

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.trim(self._parameters)

class Cut(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Cut`

    Cuts (removes) the section of the clip from the start to the finish positions.

    Args:
        start (Position): Starting position of the section to be cut.
        finish (Position): Finish position of the section to be cut.
    """
    from .operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__([start, finish])
        self._indexes = {
            'start': 0, 'finish': 1
        }

    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.cut(*self._parameters)


class Monofy(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Monofy`

    Cuts out any part of an element Duration that overlaps with the next element.

    Args:
        None
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.monofy()

class Fill(ClipProcess):
    """`Generic -> Process -> ContainerProcess -> ClipProcess -> Fill`

    Adds up Rests to empty spaces (lengths) in a staff for each Measure.

    Args:
        None
    """
    def _direct_process(self, operand: 'Clip') -> 'Clip':
        return operand.fill()


class BlockProcess(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> BlockProcess`

    Processes applicable exclusively to `Block` operands.
    """
    def _direct_process(self, operand: o.T) -> o.T:
        from . import operand_container as oc
        if isinstance(operand, oc.Block):
            return self._direct_process(operand)
        else:
            print(f"Warning: Operand is NOT a `Block`!")
        return super().__rrshift__(operand)

    def _direct_process(self, operand: o.T) -> o.T:
        return operand

class PartProcess(CompositionProcess):
    """`Generic -> Process -> ContainerProcess -> CompositionProcess -> PartProcess`

    Processes applicable exclusively to `Part` operands.
    """

    def _direct_process(self, operand: o.T) -> o.T:
        from . import operand_container as oc
        if isinstance(operand, oc.Part):
            return self._direct_process(operand.copy())
        else:
            print(f"Warning: Operand is NOT a `Part`!")
        return super().__rrshift__(operand)

    def _direct_process(self, operand: o.T) -> o.T:
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
    Devices(["VMPK", "FLUID", "loopMIDI", "Microsoft", "IAC Bus", "Apple"]) : Devices that are used by default in order of trying to connect by the `JsonMidiPlayer`.
    ClockedDevices([]) : By default no devices are set to receive clocking messages.
    ControlledDevices([]) : By default no devices are set to receive controlling messages (for DAWs).
    PPQN(24) : The default for clocking midi messages is 24 Pulses Per Quarter Note.
    ClockMMCMode(False) : The default clock stop mode is the one that sends a song position signal back to 0.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._tempo: Fraction                       = Fraction(120)
        self._quantization: Fraction                = Fraction(1/4) # Quantization is in Beats ratio
        self._time_signature: TimeSignature         = TimeSignature(4, 4)
        self._key_signature: ou.KeySignature        = ou.KeySignature()
        self._controller: Controller                = Controller("Pan")
        self._devices: list[str]                    = ["VMPK", "FLUID", "loopMIDI", "Microsoft", "IAC Bus", "Apple"]
        self._clocked_devices: list[str]            = []
        self._controlled_devices: list[str]         = []
        self._clock_ppqn: int                       = 24
        self._folder: str                           = ""
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter


    def convert_time_to_measures(self, minutes: int = 0, seconds: int = 0) -> int:
        actual_bps: Fraction = settings._tempo / 60 # Beats Per Second
        time_seconds: int = 60 * minutes + seconds
        beats_per_measure: int = self._time_signature._top
        total_beats: Fraction = time_seconds * actual_bps
        total_measures: int = int(total_beats / beats_per_measure)
        return total_measures


    def beats_to_minutes(self, beats: Fraction) -> Fraction:
        return beats / self._tempo

    def minutes_to_beats(self, minutes: Fraction) -> Fraction:
        return minutes * self._tempo


    def __mod__(self, operand: o.T) -> o.T:
        from . import operand_element as oe
        from . import operand_container as oc
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Tempo():            return ra.Tempo(self._tempo)
                    case ra.Quantization():     return operand._data << self._quantization
                    case ra.StepsPerNote():
                        return ra.StepsPerNote() << od.Pipe( 1 / self._quantization )
                    case TimeSignature():       return self._time_signature
                    case ra.BeatsPerMeasure():  return self._time_signature % od.Pipe( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.Pipe( ra.BeatNoteValue() )
                    case ou.KeySignature():     return self._key_signature
                    case Controller():          return self._controller
                    case oc.ClockedDevices():   return oc.ClockedDevices(self._clocked_devices)
                    case oc.ControlledDevices():
                                                return oc.ControlledDevices(self._controlled_devices)
                    case oc.Devices():          return oc.Devices(self._devices)
                    case ou.PPQN():             return ou.PPQN(self._clock_ppqn)
                    case od.Folder():           return od.Folder(self._folder)
                    case _:                     return super().__mod__(operand)
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
            case Controller():          return self._controller.copy()
            case ou.Number():           return self._controller % ou.Number()
            case ou.Value():            return ou.Number.getDefaultValue(self % ou.Number() % int())
            case oc.ClockedDevices():   return oc.ClockedDevices(self._clocked_devices)
            case oc.ControlledDevices():
                                        return oc.ControlledDevices(self._controlled_devices)
            case oc.Devices():          return oc.Devices(self._devices)
            case ou.PPQN():             return ou.PPQN(self._clock_ppqn)
            case od.Folder():           return od.Folder(self._folder)
            case oe.Clock():            return oe.Clock(self % oc.ClockedDevices(), self % oc.ControlledDevices(), self % ou.PPQN())
            case Settings():
                return operand.copy(self)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Settings') -> bool:
        if type(self) != type(other):
            return False
        if isinstance(other, od.Conditional):
            return other == self
        return  self._tempo                 == other._tempo \
            and self._quantization          == other._quantization \
            and self._time_signature        == other._time_signature \
            and self._key_signature         == other._key_signature \
            and self._controller            == other._controller \
            and self._devices               == other._devices \
            and self._clocked_devices       == other._clocked_devices \
            and self._controlled_devices    == other._controlled_devices \
            and self._clock_ppqn            == other._clock_ppqn \
            and self._folder                == other._folder
    

    def getPlaylist(self, position_beats: Fraction | None = None) -> list[dict]:
        if isinstance(position_beats, Fraction):
            return [{ "time_ms": o.minutes_to_time_ms( self.beats_to_minutes(position_beats) ) }]
        return [{ "time_ms": 0.0 }]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tempo"]                = self.serialize( self._tempo )
        serialization["parameters"]["quantization"]         = self.serialize( self._quantization )
        serialization["parameters"]["time_signature"]       = self.serialize( self._time_signature )
        serialization["parameters"]["key_signature"]        = self.serialize( self._key_signature )
        serialization["parameters"]["controller"]           = self.serialize( self._controller )
        serialization["parameters"]["devices"]              = self.serialize( self._devices )
        serialization["parameters"]["clocked_devices"]      = self.serialize( self._clocked_devices )
        serialization["parameters"]["controlled_devices"]   = self.serialize( self._controlled_devices )
        serialization["parameters"]["clock_ppqn"]           = self.serialize( self._clock_ppqn )
        serialization["parameters"]["folder"]               = self.serialize( self._folder )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tempo" in serialization["parameters"] and "quantization" in serialization["parameters"] and
            "time_signature" in serialization["parameters"] and "key_signature" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "devices" in serialization["parameters"] and "clocked_devices" in serialization["parameters"] and  "controlled_devices" in serialization["parameters"] and 
            "clock_ppqn" in serialization["parameters"] and "folder" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempo                 = self.deserialize( serialization["parameters"]["tempo"] )
            self._quantization          = self.deserialize( serialization["parameters"]["quantization"] )
            self._time_signature        = self.deserialize( serialization["parameters"]["time_signature"] )
            self._key_signature         = self.deserialize( serialization["parameters"]["key_signature"] )
            self._controller            = self.deserialize( serialization["parameters"]["controller"] )
            self._devices               = self.deserialize( serialization["parameters"]["devices"] )
            self._clocked_devices       = self.deserialize( serialization["parameters"]["clocked_devices"] )
            self._controlled_devices    = self.deserialize( serialization["parameters"]["controlled_devices"] )
            self._clock_ppqn            = self.deserialize( serialization["parameters"]["clock_ppqn"] )
            self._folder                = self.deserialize( serialization["parameters"]["folder"] )
        return self
    
    def __lshift__(self, operand: any) -> Self:
        from . import operand_element as oe
        from . import operand_container as oc
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Settings():
                super().__lshift__(operand)
                self._tempo                 = operand._tempo
                self._quantization          = operand._quantization
                self._time_signature        << operand._time_signature
                self._key_signature         << operand._key_signature
                self._controller            << operand._controller
                self._devices               = operand._devices.copy()
                self._clocked_devices       = operand._clocked_devices.copy()
                self._controlled_devices    = operand._controlled_devices.copy()
                self._clock_ppqn            = operand._clock_ppqn
                self._folder                = operand._folder
            case od.Pipe():
                match operand._data:
                    case ra.Tempo():                self._tempo = operand._data._rational
                    case ra.Quantization():         self._quantization = operand._data._rational
                    case TimeSignature():           self._time_signature = operand._data
                    case ou.KeySignature():         self._key_signature = operand._data
                    case Controller():              self._controller = operand._data
                    case oc.ClockedDevices():       self._clocked_devices = operand._data % od.Pipe( list() )
                    case oc.ControlledDevices():    self._controlled_devices = operand._data % od.Pipe( list() )
                    case oc.Devices():              self._devices = operand._data % od.Pipe( list() )
                    case ou.PPQN():                 self._clock_ppqn = operand._data._unit
                    case od.Folder():               self._folder = operand._data._data
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
            case Controller() | ou.Number():
                                        self._controller << operand
            case oc.ClockedDevices():   self._clocked_devices = operand % list()
            case oc.ControlledDevices():
                                        self._controlled_devices = operand % list()
            case oc.Devices():          self._devices = operand % list()
            case od.Device():           self._devices = [ operand._data ]
            case ou.PPQN():             self._clock_ppqn = operand._unit
            case od.Folder():           self._folder = operand._data
            case oe.Clock():
                self << ( operand % oc.ClockedDevices(), operand % oc.ControlledDevices(), operand % ou.PPQN() )
            case None:  # Does a Reset!
                self << Settings()
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    
    def __iadd__(self, operand: any) -> Self:
        from . import operand_container as oc
        match operand:
            case od.Device():
                if isinstance(operand._data, str):
                    self_devices: oc.Devices = self % od.Pipe( oc.Devices() )
                    self_devices += operand
                    self._devices = self_devices % od.Pipe( list() )
                return self
            case ra.Tempo():
                self._tempo += operand._rational
                return self
        return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        from . import operand_container as oc
        match operand:
            case od.Device():
                self_devices: oc.Devices = self % od.Pipe( oc.Devices() )
                self_devices -= operand
                self._devices = self_devices % od.Pipe( list() )
                return self
            case ra.Tempo():
                self._tempo -= operand._rational
                return self
        return super().__isub__(operand)


# Instantiate the Global Settings here.
settings: Settings = Settings()


