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
import re
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


if TYPE_CHECKING:
    from operand_element import Element, Note
    from operand_chaos import Chaos
    from operand_rational import Length
    from operand_container import Container, Composition, Clip


class Generic(o.Operand):
    """`Generic`

    Generic represents any `Operand` that doesn't fit any particular type of `Operand` in nature or parameters type.

    Parameters
    ----------
    Any(None) : Generic doesn't have any self parameters.
    """
    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case tuple():
                super().__iadd__(operand)
            case _:
                self_operand: any = self % operand
                self_operand += operand
                self << self_operand
        return self

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case tuple():
                super().__isub__(operand)
            case _:
                self_operand: any = self % operand
                self_operand -= operand
                self << self_operand
        return self

    def __imul__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case tuple():
                super().__imul__(operand)
            case _:
                self_operand: any = self % operand
                self_operand *= operand # Generic `self_operand`
                self << self_operand
        return self

    def __itruediv__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        if operand != Fraction(0):
            match operand:
                case tuple():
                    super().__itruediv__(operand)
                case _:
                    self_operand: any = self % operand
                    self_operand /= operand # Generic `self_operand`
                    self << self_operand
        return self

    def __ifloordiv__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        if operand != Fraction(0):
            match operand:
                case tuple():
                    super().__ifloordiv__(operand)
                case _:
                    self_operand: any = self % operand
                    self_operand //= operand # Generic `self_operand`
                    self << self_operand
        return self



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

    def start(self) -> ra.Position:
        return ra.Position(self, self._position_beats)

    def finish(self) -> ra.Position:
        return ra.Position(self, self._position_beats + self._duration_beats)

    def overlap(self, other: 'Locus') -> bool:
        return other._position_beats + other._duration_beats > self._position_beats \
            and other._position_beats < self._position_beats + self._duration_beats

    def trim(self, other: 'Locus') -> Self:
        if self.start() < other.start():
            self._position_beats = other._position_beats
        if self.finish() > other.finish():
            self._duration_beats -= self.finish() % Fraction() - other.finish() % Fraction()
        return self


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


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["position_beats"] = o.serialize(self._position_beats)
        serialization["parameters"]["duration_beats"] = o.serialize(self._duration_beats)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Element':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position_beats" in serialization["parameters"] and "duration_beats" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position_beats    = o.deserialize(serialization["parameters"]["position_beats"])
            self._duration_beats    = o.deserialize(serialization["parameters"]["duration_beats"])
        return self

    def __lshift__(self, operand: any) -> Self:
        from . import operand_element as oe
        from . import operand_container as oc
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        if self._time_signature_reference is None:  # If a self containing TimeSignature is submitted
            match operand:
                case ra.Convertible():
                    self._time_signature_reference = operand._time_signature_reference
                case oe.Element() | oc.Composition():
                    self._time_signature_reference = operand._get_time_signature()
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
            case oe.Element():
                self._position_beats = operand._position_beats
                self._duration_beats = operand._duration_beats
            case ra.Duration() | ra.Length():
                if isinstance(operand, ra.RightDuration):
                    self._position_beats -= operand._rational - self._duration_beats
                self._duration_beats        = operand._rational
            case ra.TimeValue():
                self << ra.Duration(self._time_signature_reference, operand)
            case ra.Position():
                self._position_beats        = operand._rational
            case ra.TimeUnit():
                # The setting of the TimeUnit depends on the Element position
                self._position_beats        = ra.Position(self._time_signature_reference, self._position_beats, operand) % Fraction()

            case str():
                self << ra.Convertible.get_convertible_from_string(operand)
                
            case list():
                if len(operand) < 3:
                    locus_position: ra.Position = ra.Position(self, operand[0])
                    self._position_beats = ra.Beats(locus_position)._rational
                    if len(operand) == 2:
                        locus_duration: ra.Duration = ra.Duration(self, operand[1])
                        self._duration_beats = ra.Beats(locus_duration)._rational

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
            case TimeSignature():
                self._time_signature_reference = operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
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
        serialization["parameters"]["top"]    = o.serialize( self._top )
        serialization["parameters"]["bottom"] = o.serialize( self._bottom )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'TimeSignature':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "top" in serialization["parameters"] and "bottom" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._top           = o.deserialize( serialization["parameters"]["top"] )
            self._bottom        = o.deserialize( serialization["parameters"]["bottom"] )
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
        serialization["parameters"]["value"]    = o.serialize( self._value )
        serialization["parameters"]["position_beats"] = o.serialize( self._position_beats )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "value" in serialization["parameters"] and "position_beats" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._value             = o.deserialize( serialization["parameters"]["value"] )
            self._position_beats    = o.deserialize( serialization["parameters"]["position_beats"] )
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
            case list():                return o.deep_copy(self._dots)
            case Dot():
                for i, dot in enumerate(self._dots):
                    if operand._position_beats == dot._position_beats:
                        return dot.copy()
                return ol.Null()
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["dots"] = o.serialize( self._dots )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "dots" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._dots = o.deserialize( serialization["parameters"]["dots"] )
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
                    self._dots = o.deep_copy(operand)
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
        self._diatonic_mode_0: int      = settings._diatonic_mode_0
        self._tonic_key: int            = settings._tonic_key
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


    def get_diatonic_scale(self) -> tuple[int]:
        scale_mode: int = self._diatonic_mode_0 % 9 + 1
        return Scale._scales[scale_mode]

    def get_sharps(self) -> int:
        diatonic_scale: tuple[int] = self.get_diatonic_scale()
        sharps_or_flats: tuple[int] = Scale.sharps_or_flats_picker(self._tonic_key, diatonic_scale)
        return sum(sharps_or_flats)

    def apply_sharps(self, sharps: int = 0) -> Self:
        self._tonic_key = Scale.sharps_to_tonic(self._diatonic_mode_0, sharps)
        return self

    def apply_key_signature(self, key_signature: ou.KeySignature) -> Self:
        return self.apply_sharps(key_signature % int())

    def reset_tonic_key(self) -> Self:
        self._tonic_key = Scale.sharps_to_tonic(self._diatonic_mode_0)
        return self

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
        signature_scale: tuple[int] = self.get_diatonic_scale()
        degree_0: int = 0
        accidental: int = 0
        tonic_to_root: int = root_key - self._tonic_key % 12
        # For Semitones
        if signature_scale[tonic_to_root % 12] == 0: # Not on the Scale
            # No two consecutive empty notes! (assumption for all scales!!)
            total_sharps: int = self.get_sharps()
            flats: bool = total_sharps < 0
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
            transposition_scale: tuple[int] = tuple(self._scale)
            scale_degrees = sum(self._scale)
            first_key_int: int = self._get_root_key()
        else:
            transposition_scale: tuple[int] = self.get_diatonic_scale()
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
            diatonic_scale: tuple[int] = self.get_diatonic_scale()
            tonic_to_root_key = Scale.transpose_key(self._degree_0, diatonic_scale)
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
            diatonic_scale: tuple[int] = self.get_diatonic_scale()
            tonic_to_target_key: int = Scale.transpose_key(transposition_degree_0, diatonic_scale)
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


    def get_absolute_pitch(self) -> int:
        """
        Returns the final chromatic pitch with a midi value from 0 to 127.
        """
        octave_key: int = self._octave_0 * 12
        target_key: int = self._get_target_key()
        return octave_key + target_key

    def set_absolute_pitch(self, chromatic_pitch: int) -> Self:
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
                return self.get_absolute_pitch() == other.get_absolute_pitch()
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
                return self.get_absolute_pitch() < other.get_absolute_pitch()
            case int() | float() | ou.Degree() | ou.Octave():
                return self % other < other
            case _:
                return super().__lt__(other)
        return False
    
    def __gt__(self, other: any) -> bool:
        match other:
            case Pitch():
                return self.get_absolute_pitch() > other.get_absolute_pitch()
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
                    case ou.Octave():
                        return operand._data << od.Pipe(self._octave_0)
                    case ou.Major():
                        return ou.Major(self._diatonic_mode_0 == 0)
                    case ou.Minor():
                        return ou.Minor(self._diatonic_mode_0 == 5)
                    case ou.Quality() | ou.Mode():
                        return operand._data << self._diatonic_mode_0
                    case ou.TonicKey():
                        return operand._data << od.Pipe(self._tonic_key)    # Must come before than Key()
                    case ou.Degree():   # Returns an absolute degree_0
                        operand._data._unit = self._degree_0
                        operand._data._accidental = self._accidental
                        return operand._data
                    case ou.Accidental() | ou.Natural():
                        return operand._data << self % operand
            
                    case ou.Semitone(): # Returns an absolute pitch_int Semitone
                        return operand._data << self.get_absolute_pitch()
                    case ou.Transposition():
                        return operand._data << od.Pipe(self._transposition)
                    case int():             return self._octave_0
                    case float():           return float(self._degree_0)
                    case Fraction():        return Fraction(self._transposition)
                    case Scale():           return operand._data << od.Pipe(self._scale)
                    case list():            return self._scale
                    case _:                 return super().__mod__(operand)

            case ou.Major():
                return ou.Major(self._diatonic_mode_0 == 0)
            case ou.Minor():
                return ou.Minor(self._diatonic_mode_0 == 5)
            case ou.Quality() | ou.Mode():
                return operand.copy(self._diatonic_mode_0)

            case ou.Flats():
                total_sharps: int = self.get_sharps()
                return ou.Flats(total_sharps * -1)
            case ou.KeySignature() | ou.Accidentals():
                total_sharps: int = self.get_sharps()
                return operand.copy(total_sharps)
            
            case int():
                return self % ou.Octave() % int()
            case float():
                return float(self._degree_0 + 1)
            case Fraction():
                return Fraction(self._transposition)
            
            case ou.AbsolutePitch():
                return ou.AbsolutePitch(self.get_absolute_pitch())
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
                    total_sharps: int = self.get_sharps()
                    key_operand._flattened = total_sharps < 0
                    key_operand._enharmonic = ou.KeySignature.is_enharmonic(key_operand._unit, total_sharps)
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
        serialization["parameters"]["diatonic_mode_0"]  = o.serialize( self._diatonic_mode_0 )
        serialization["parameters"]["tonic_key_0"]      = o.serialize( self._tonic_key )
        serialization["parameters"]["octave_0"]         = o.serialize( self._octave_0 )
        serialization["parameters"]["degree_0"]         = o.serialize( self._degree_0 )
        serialization["parameters"]["accidental"]       = o.serialize( self._accidental )
        if self._transposition:
            serialization["parameters"]["transposition"]    = o.serialize( self._transposition )
        if self._scale:
            serialization["parameters"]["scale"]            = o.serialize( self._scale )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "diatonic_mode_0" in serialization["parameters"] and "tonic_key_0" in serialization["parameters"] and
            "octave_0" in serialization["parameters"] and "degree_0" in serialization["parameters"] and "accidental" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._diatonic_mode_0 = o.deserialize( serialization["parameters"]["diatonic_mode_0"] )
            self._tonic_key     = o.deserialize( serialization["parameters"]["tonic_key_0"] )
            self._octave_0      = o.deserialize( serialization["parameters"]["octave_0"] )
            self._degree_0      = o.deserialize( serialization["parameters"]["degree_0"] )
            self._accidental    = o.deserialize( serialization["parameters"]["accidental"] )
            if "transposition" in serialization["parameters"]:
                self._transposition = o.deserialize( serialization["parameters"]["transposition"] )
            else:
                self._transposition = 0
            if "scale" in serialization["parameters"]:
                self._scale         = o.deserialize( serialization["parameters"]["scale"] )
            else:
                self._scale = []
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Pitch():
                super().__lshift__(operand)
                self._diatonic_mode_0       = operand._diatonic_mode_0
                self._tonic_key             = operand._tonic_key
                self._octave_0              = operand._octave_0
                self._degree_0              = operand._degree_0
                self._accidental            = operand._accidental
                self._transposition         = operand._transposition
                self._scale                 = operand._scale.copy()
            case od.Pipe():
                match operand._data:
                    case ou.KeySignature(): # Preserves the chromatic_pitch
                        self.apply_key_signature(operand._data)

                    case ou.Major():
                        if operand._data: self._diatonic_mode_0 = 0    # Major
                    case ou.Minor():
                        if operand._data: self._diatonic_mode_0 = 5    # minor
                    case ou.Quality():
                        self._diatonic_mode_0 = operand._data._unit
                    case ou.Mode():
                        self._diatonic_mode_0 = operand._data._unit - 1
                    case ou.Flats():
                        self.apply_sharps(operand._data._unit * -1)
                    case ou.Accidentals():
                        self.apply_sharps(operand._data._unit)

                    case ou.TonicKey():    # Must come before than Key()
                        self._octave_0 = operand._data._unit // 12
                        self._tonic_key = operand._data._unit % 12

                    case ou.Semitone(): # Sets the absolute pitch_int Semitone
                        self.set_absolute_pitch(operand._data._unit)
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
                self.apply_key_signature(operand)
                self << original_semitone
            case ou.Major():
                if operand: self._diatonic_mode_0 = 0    # Major
                self.reset_tonic_key()
            case ou.Minor():
                if operand: self._diatonic_mode_0 = 5    # minor
                self.reset_tonic_key()
            case ou.Mode():
                self._diatonic_mode_0 = operand._unit - 1
                self.reset_tonic_key()
            case ou.Flats():
                self.apply_sharps(operand._unit * -1)
            case ou.Accidentals():
                self.apply_sharps(operand._unit)

            case ou.AbsolutePitch():
                self.set_absolute_pitch(operand._unit)
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
                    self.reset_tonic_key()
                    self._degree_0 = 0
                elif operand._unit < 0:
                    self._degree_0 = operand._unit  # Negative remains negative!
                # A Degree with Just an accidental defined can set just that!
            case None:  # Works as a reset
                # Resets the degree to I (tonic)
                self.reset_tonic_key()
                self._degree_0 = 0
                self._accidental = 0
                self._transposition = 0

            # ADJUSTING KEYS DIRECTLY KEEPS THE SAME OCTAVE
            case ou.TonicKey():    # Must come before than Key()
                if operand._unit < 0:
                    self.reset_tonic_key()
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
                self.set_absolute_pitch(ou.Key(operand)._unit) # Sets the key number regardless KeySignature or Scale!

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
                actual_semitone: int = self.get_absolute_pitch()
                added_pitch: int = operand._unit
                new_pitch: int = actual_semitone + added_pitch
                self.set_absolute_pitch(new_pitch)
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
                actual_pitch: int = self.get_absolute_pitch()
                added_pitch: int = operand._unit
                new_pitch: int = actual_pitch - added_pitch
                self.set_absolute_pitch(new_pitch)
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


class Controller(Generic):
    """`Generic -> Controller`

    A `Controller` defines all the parameters concerning a device control that receives a value for its modulation.

    Parameters
    ----------
    Number("Modulation"), MSB, int : The Controller number or MSB number (Most Significant Byte).
    LSB(0) : The Controller number or MSB number (Least Significant Byte).
    NRPN(False) : Sets the controller as an NRPN one.
    High(False), int : Allows the processing of high resolution values up to 16383 (128*128 - 1) instead the usual 127 (128 - 1).
    """
    def __init__(self, *parameters):
        self._number_msb: int   = 1 # Modulation number
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
        serialization["parameters"]["number_msb"]   = o.serialize( self._number_msb )
        serialization["parameters"]["lsb"]          = o.serialize( self._lsb )
        serialization["parameters"]["nrpn"]         = o.serialize( self._nrpn )
        serialization["parameters"]["high"]         = o.serialize( self._high )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "number_msb" in serialization["parameters"] and "lsb" in serialization["parameters"] and
            "nrpn" in serialization["parameters"] and "high" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._number_msb    = o.deserialize( serialization["parameters"]["number_msb"] )
            self._lsb           = o.deserialize( serialization["parameters"]["lsb"] )
            self._nrpn          = o.deserialize( serialization["parameters"]["nrpn"] )
            self._high          = o.deserialize( serialization["parameters"]["high"] )
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
    def sharps_to_tonic(diatonic_mode_0: int = 0, sharps: int = 0) -> int:
        if diatonic_mode_0 % 7 < 7:    # Diatonic scale
            zero_tonic_key: int = Scale.transpose_key(diatonic_mode_0)
            circle_fifths_position: int = sharps
            return (zero_tonic_key + circle_fifths_position * 7) % 12
        return 9    # A key


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
    def sharps_or_flats_picker(tonic_key: int = 0, picker_scale: tuple[int] = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)) -> tuple[int]:
        """
        This method returns all the Sharps or Flats for a given `tonic_key` on a specified `picker_scale`.

        For example, `Scale.sharps_or_flats_picker(2)` will return `(+1, +0, +0, +0, +0, +1, +0, +0, +0, +0, +0, +0)`.

        """
        major_scale: tuple[int] = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)
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
        return tuple(sharps_or_flats)
    

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
        serialization["parameters"]["scale"]   = o.serialize( self._scale )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "scale" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._scale    = o.deserialize( serialization["parameters"]["scale"] )
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
                
            case ou.Major():
                self._scale = self.get_diatonic_scale(1)
            case ou.Minor():
                self._scale = self.get_diatonic_scale(6)
            case ou.Quality():
                self._scale = self.get_diatonic_scale(operand._unit + 1)
            case ou.Mode():
                self._scale = self.get_diatonic_scale(operand._unit)

            case str():
                self_scale = Scale.get_scale(operand)
                if len(self_scale) == 12:
                    self._scale = self_scale
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

    @staticmethod
    def get_diatonic_scale(mode: int = 1) -> list[int]:
        return list(Scale._scales[mode])

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
    def get_scale(scale: int | str | list = 0) -> list[int]:
        if scale != [] and scale != -1 and scale != "":
            scale_number = Scale.get_scale_number(scale)
            if scale_number >= 0:
                return list(Scale._scales[scale_number])
        return []   # Has no scale at all


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
        serialization["parameters"]["sum"] = o.serialize(self._sum)
        serialization["parameters"]["max"] = o.serialize(self._max)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Element':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "sum" in serialization["parameters"] and "max" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._sum = o.deserialize(serialization["parameters"]["sum"])
            self._max = o.deserialize(serialization["parameters"]["max"])
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
        if isinstance(self._chained_operand, NoteEffect):
            return self._chained_operand.apply(notes)
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
        serialization["parameters"]["order"]            = o.serialize( self._order )
        serialization["parameters"]["duration_beats"]         = o.serialize( self._duration_beats )
        serialization["parameters"]["swing"]            = o.serialize( self._swing )
        serialization["parameters"]["chaos"]            = o.serialize( self._chaos )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "order" in serialization["parameters"] and "duration_beats" in serialization["parameters"] and
            "swing" in serialization["parameters"] and "chaos" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._order                 = o.deserialize( serialization["parameters"]["order"] )
            self._duration_beats        = o.deserialize( serialization["parameters"]["duration_beats"] )
            self._swing                 = o.deserialize( serialization["parameters"]["swing"] )
            self._chaos                 = o.deserialize( serialization["parameters"]["chaos"] )
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
        serialization["parameters"]["duration_beats"] = o.serialize( self._duration_beats )
        serialization["parameters"]["swing"]    = o.serialize( self._swing )
        serialization["parameters"]["chaos"]    = o.serialize( self._chaos )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "duration_beats" in serialization["parameters"] and "swing" in serialization["parameters"] and "chaos" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._duration_beats    = o.deserialize( serialization["parameters"]["duration_beats"] )
            self._swing             = o.deserialize( serialization["parameters"]["swing"] )
            self._chaos             = o.deserialize( serialization["parameters"]["chaos"] )
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
            pitch: int = single_note._pitch.get_absolute_pitch()
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
        serialization["parameters"]["notes"] = o.serialize( self._notes )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "notes" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._notes = o.deserialize( serialization["parameters"]["notes"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        from . import operand_element as oe
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Coupler():
                super().__lshift__(operand)
                self._notes = o.deep_copy(operand._notes)
            case od.Pipe():
                match operand._data:
                    case list():
                        if all(isinstance(note, Note) for note in operand._data):
                            self._notes = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                if all(isinstance(note, oe.Note) for note in operand):
                    self._notes = o.deep_copy(operand)
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
        serialization["parameters"]["octaves"] = o.serialize( self._octaves )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "octaves" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._octaves = o.deserialize( serialization["parameters"]["octaves"] )
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
        serialization["parameters"]["segment"] = o.serialize( self._segment )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "segment" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._segment = o.deserialize( serialization["parameters"]["segment"] )
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
    Devices(["VMPK", "FLUID", "MIDI", "Microsoft", "IAC Bus", "Apple"]) : Devices that are used by default in order of trying to connect by the `JsonMidiPlayer`.
    ClockedDevices([]) : By default no devices are set to receive clocking messages.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._tempos: list[ou.Tempo]                = [ou.Tempo()]
        self._quantization: Fraction                = Fraction(1/4) # Quantization is in Beats ratio
        self._time_signature: TimeSignature         = TimeSignature(4, 4)
        self._diatonic_mode_0: int                  = 0
        self._tonic_key: int                        = 0
        self._devices: list[str]                    = ["VMPK", "FLUID", "MIDI", "Microsoft", "IAC Bus", "Apple"]
        self._clocked_devices: list[str]            = []
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter


    def beats_to_minutes(self, beats: Fraction) -> Fraction:
        return beats / self._tempos._unit * 10

    def minutes_to_beats(self, minutes: Fraction) -> Fraction:
        return minutes * self._tempos._unit / 10

    def __mod__(self, operand: o.T) -> o.T:
        from . import operand_element as oe
        from . import operand_container as oc
        match operand:
            case od.Pipe():
                match operand._data:
                    case oc.Tempos():
                        return operand._data << self._tempos
                    case list():                return self._tempos
                    case ra.Quantization():     return operand._data << self._quantization
                    case ra.StepsPerNote():
                        return ra.StepsPerNote() << od.Pipe( 1 / self._quantization )
                    case TimeSignature():       return self._time_signature
                    case ra.BeatsPerMeasure():  return self._time_signature % od.Pipe( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.Pipe( ra.BeatNoteValue() )
                    case ou.Major():
                        return ou.Major(self._diatonic_mode_0 == 0)
                    case ou.Minor():
                        return ou.Minor(self._diatonic_mode_0 == 5)
                    case ou.Quality() | ou.Mode():
                        return operand._data << self._diatonic_mode_0
                    case ou.TonicKey():         return operand._data << self._tonic_key
                    case oc.ClockedDevices():   return oc.ClockedDevices(self._clocked_devices)
                    case oc.Devices():          return oc.Devices(self._devices)
                    case _:                     return super().__mod__(operand)
            case oc.Tempos():           return self._tempos.copy()
            case ou.Tempo():            return oc.Tempos(self._tempos)[0]
            case list():                return o.deep_copy(self._tempos)
            case ra.Quantization():     return operand.copy(self._quantization)
            case ra.StepsPerNote():
                return ra.StepsPerNote() << 1 / self._quantization
            case ra.StepsPerMeasure():
                return ra.StepsPerMeasure(self._time_signature % ra.BeatsPerMeasure() % Fraction() / self._quantization)
            case TimeSignature():       return self._time_signature.copy()
            case ra.BeatsPerMeasure():  return self._time_signature % ra.BeatsPerMeasure()
            case ra.BeatNoteValue():    return self._time_signature % ra.BeatNoteValue()
            case ra.NotesPerMeasure():  return self._time_signature % ra.NotesPerMeasure()
            case ou.Major():
                return ou.Major(self._diatonic_mode_0 == 0)
            case ou.Minor():
                return ou.Minor(self._diatonic_mode_0 == 5)
            case ou.Quality() | ou.Mode():
                return operand.copy(self._diatonic_mode_0)
            case ou.TonicKey():
                return ou.TonicKey(self._tonic_key)
            case ou.KeySignature() | ou.Accidentals():
                scale_mode: int = self._diatonic_mode_0 % 9 + 1
                diatonic_scale: tuple[int] = Scale._scales[scale_mode]
                sharps_or_flats: tuple[int] = Scale.sharps_or_flats_picker(self._tonic_key, diatonic_scale)
                return operand.copy(sum(sharps_or_flats))
            case ou.Key() | ou.Accidentals() | ou.Quality() | int() | float() | Fraction() | str():
                                        return self % ou.KeySignature() % operand
            case oc.ClockedDevices():   return oc.ClockedDevices(self._clocked_devices)
            case oc.Devices():          return oc.Devices(self._devices)
            case Settings():
                return operand.copy(self)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Settings') -> bool:
        if type(self) != type(other):
            return False
        if isinstance(other, od.Conditional):
            return other == self
        return  self._tempos                == other._tempos \
            and self._quantization          == other._quantization \
            and self._time_signature        == other._time_signature \
            and self._diatonic_mode_0       == other._diatonic_mode_0 \
            and self._tonic_key             == other._tonic_key \
            and self._devices               == other._devices \
            and self._clocked_devices       == other._clocked_devices
    

    def getClocking(self, length_beats: Fraction) -> dict[str, list]:
        return {
            "length_beats": [length_beats.numerator, length_beats.denominator],
            "devices": self._clocked_devices,
            "tempos": [
                tempo % dict() for tempo in self._tempos
            ]
        }

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tempos"]               = o.serialize( self._tempos )
        serialization["parameters"]["quantization"]         = o.serialize( self._quantization )
        serialization["parameters"]["time_signature"]       = o.serialize( self._time_signature )
        serialization["parameters"]["diatonic_mode_0"]      = o.serialize( self._diatonic_mode_0 )
        serialization["parameters"]["tonic_key_0"]          = o.serialize( self._tonic_key )
        serialization["parameters"]["devices"]              = o.serialize( self._devices )
        serialization["parameters"]["clocked_devices"]      = o.serialize( self._clocked_devices )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tempos" in serialization["parameters"] and "quantization" in serialization["parameters"] and
            "time_signature" in serialization["parameters"] and "diatonic_mode_0" in serialization["parameters"] and
            "tonic_key_0" in serialization["parameters"] and "devices" in serialization["parameters"] and "clocked_devices" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tempos                = o.deserialize( serialization["parameters"]["tempos"] )
            self._quantization          = o.deserialize( serialization["parameters"]["quantization"] )
            self._time_signature        = o.deserialize( serialization["parameters"]["time_signature"] )
            self._diatonic_mode_0       = o.deserialize( serialization["parameters"]["diatonic_mode_0"] )
            self._tonic_key             = o.deserialize( serialization["parameters"]["tonic_key_0"] )
            self._devices               = o.deserialize( serialization["parameters"]["devices"] )
            self._clocked_devices       = o.deserialize( serialization["parameters"]["clocked_devices"] )
        return self
    
    def __lshift__(self, operand: any) -> Self:
        from . import operand_element as oe
        from . import operand_container as oc
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Settings():
                super().__lshift__(operand)
                self._tempos                = o.deep_copy(operand._tempos)
                self._quantization          = operand._quantization
                self._time_signature        << operand._time_signature
                self._diatonic_mode_0       = operand._diatonic_mode_0
                self._tonic_key             = operand._tonic_key
                self._devices               = operand._devices.copy()
                self._clocked_devices       = operand._clocked_devices.copy()
            case od.Pipe():
                match operand._data:
                    case oc.Tempos():               self._tempos = operand._data._items
                    case list():                    self._tempos = operand._data
                    case ra.Quantization():         self._quantization = operand._data._rational
                    case TimeSignature():           self._time_signature = operand._data
                    case ou.Major():
                        if operand._data: self._diatonic_mode_0 = 0    # Major
                    case ou.Minor():
                        if operand._data: self._diatonic_mode_0 = 5    # minor
                    case ou.Mode():
                        self._diatonic_mode_0 = operand._data._unit - 1
                    case ou.TonicKey():
                        self._tonic_key = operand._data._unit % 12

                    case oc.ClockedDevices():       self._clocked_devices = operand._data % od.Pipe( list() )
                    case oc.Devices():              self._devices = operand._data % od.Pipe( list() )
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case oc.Tempos():           self._tempos = o.deep_copy(operand._items)
            case ou.Tempo():            self._tempos = [operand.copy()]
            case list():                self._tempos = o.deep_copy(operand)
            case ra.Quantization():     self._quantization = operand._rational
            case ra.StepsPerNote():
                self._quantization = 1 / (operand % Fraction())
            case ra.StepsPerMeasure():
                self._quantization = self._time_signature % ra.BeatsPerMeasure() / operand % Fraction()
            case TimeSignature() | ra.TimeSignatureParameter():
                                        self._time_signature << operand
            case ou.Major():
                if operand: self._diatonic_mode_0 = 0    # Major
            case ou.Minor():
                if operand: self._diatonic_mode_0 = 5    # minor
            case ou.Mode():
                self._diatonic_mode_0 = operand._unit - 1
            case ou.KeySignature(): # Preserves the Semitone
                sharps: int = operand % int()
                self._tonic_key = Scale.sharps_to_tonic(self._diatonic_mode_0, sharps)
            case ou.Quality() | ou.Key() | int() | float() | Fraction() | str():
                                        self << ou.KeySignature(operand)
            case oc.ClockedDevices():   self._clocked_devices = operand % list()
            case oc.Devices():          self._devices = operand % list()
            case od.Device():           self._devices = [ operand._data ]
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
            case oc.Tempos() | ou.Tempo():
                tempos = oc.Tempos(od.Pipe(self._tempos))
                tempos += operand
                self._tempos = tempos._items
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
            case oc.Tempos() | ou.Tempo():
                tempos = oc.Tempos(od.Pipe(self._tempos))
                tempos -= operand
                self._tempos = tempos._items
                return self
        return super().__isub__(operand)


# Instantiate the Global Settings here.
settings: Settings = Settings()


