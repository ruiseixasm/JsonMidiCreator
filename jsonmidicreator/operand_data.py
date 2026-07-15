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
import re
# Json Midi Creator Libraries
from . import creator as c
from . import operand as o
from . import operand_label as ol


def _normalize_dsl(dsl: str) -> str:
    """
    Converts a raw DSL string into a strict canonical format:
    - elements separated by ','
    - whitespace removed as structure
    - preserves ':' and '_'

    Literal Syntax instead of Inference Syntax
    DSL stands for Domain-Specific Language
    """

    # 1. Normalize line breaks to spaces
    dsl = dsl.replace("\n", " ")

    # 2a. Remove spaces around commas
    dsl = re.sub(r"\s*,\s*", ",", dsl)

    # 2b. Remove spaces around colons
    dsl = re.sub(r"\s*:\s*", ":", dsl)

    # 2c. Remove spaces around underscores
    dsl = re.sub(r"\s*_\s*", "_", dsl)

    # 3. Convert remaining whitespace between elements into commas
    # (only if not already adjacent to separators)
    dsl = re.sub(r"\s+", ",", dsl)

    # 4. Collapse multiple commas
    dsl = re.sub(r",+", ",", dsl)

    # 5. Remove leading/trailing commas
    dsl = dsl.strip(",")

    return dsl



class Data(o.Operand):
    """`Data`

    Data has a single parameter that keeps Any type of data.

    Parameters
    ----------
    Any(None) : Any type of parameter can be used to be set as data.
    """
    def __init__(self, data = None):
        super().__init__()
        self._data = self.deep_copy(data)

    def __eq__(self, other: o.Operand) -> bool:
        if isinstance(other, Data):
            return self._data == other._data
        if isinstance(other, Conditional):
            return other == self
        return False
    
    def __lt__(self, other: o.Operand) -> bool:
        if isinstance(other, Data):
            return self._data < other._data
        return False
    
    def __gt__(self, other: o.Operand) -> bool:
        if isinstance(other, Data):
            return self._data > other._data
        return False
    
    def __le__(self, other: o.Operand) -> bool:
        return self == other or self < other
    
    def __ge__(self, other: o.Operand) -> bool:
        return self == other or self > other

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, because a Data has
        only one type of Parameters that's a generic type of Parameter
        it should be used in conjugation with Operand() to extract it.

        Examples
        --------
        >>> some_data = Data(Bend(8191))
        >>> some_data % Operand() >> Print(0)
        {'class': 'Bend', 'parameters': {'unit': 8191}}
        """
        match operand:
            case Pipe():
                match operand._data:
                    case Data():                    return self
                    case ol.Null() | None:          return ol.Null()
                    case _:                         return self._data
            case Serialization():           return self.getSerialization()
            case dict():
                serialization: dict = self.getSerialization()
                if len(operand) > 0:
                    return o.get_pair_key_data(operand, serialization)
                return serialization
            case Data():
                return operand.copy(self)
            case _:                         return self.deep_copy(self._data)
            
    def __rmod__(self, operand: any) -> any:
        match operand:
            case dict():
                if isinstance(self._data, str):
                    return o.get_dict_key_data(self._data, operand)
                return {}
            case _:                         return ol.Null()
            
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["data"] = self.serialize(self._data)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Data':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "data" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._data = self.deserialize(serialization["parameters"]["data"])
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case self.__class__():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            case Pipe():
                self._data = operand._data
            # Data doesn't load serialization, just processed data!!
            case Serialization():
                self.loadSerialization(operand % Pipe( dict() ))
            case Data():    # Not exactly the same as `case self.__class__()` above!!
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            case _:
                self._data = self.deep_copy(operand)
        return self


class Pipe(Data):
    """
    Pipe() allows the direct extraction (%) or setting (<<)
    of the given Operand parameters without the normal processing.
    
    Parameters
    ----------
    first : Operand_like
        The Operand intended to be directly extracted or set

    Examples
    --------
    >>> single_note = Note()
    >>> position_source = single_note % Pipe( Position() )
    >>> position_copy = single_note % Position()
    >>> print(id(position_source))
    >>> print(id(position_copy))
    1941569818512
    1941604026545
    """
    def __init__(self, operand: any = None):
        super().__init__()
        self._data: any = operand

    def __mod__(self, operand: o.T) -> o.T:
        return self._data
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Pipe():
                super().__lshift__(operand)
                self._data = operand._data
            case _:
                self._data = operand
        return self
    
class AsIs(Data):
    """`Data -> AsIs`

    `AsIs` lets pass any parameter, including non `Operand` ones, as they are.
    
    Parameters
    ----------
    Any() : Any type of operand.
    """
    pass


class NoteSide(Data):
    """`Data -> NoteSide`

    `NoteSide` sets the side where the Note Duration will result in extension or contraction. The side picked.
    
    Parameters
    ----------
    Duration(0), TimeValue : The amount of duration.
    """
    pass

class Left(Data):
    """`Data -> NoteSide -> Left`

    `Left` sets the side as LEFT where the Note Duration will result in extension or contraction. The left side picked.
    
    Parameters
    ----------
    Duration(0), TimeValue : The amount of duration.
    """
    pass

class Right(Data):
    """`Data -> NoteSide -> Right`

    `Right` sets the side as RIGHT, the default, where the Note Duration will result in extension or contraction. The right side picked.
    
    Parameters
    ----------
    Duration(0), TimeValue : The amount of duration.
    """
    pass


class CompositionConvertible(Data):
    """`Data -> CompositionConvertible`

    Because in a Composition convertibles can be gross or net, this specifies what time amount to be returned.
    
    Parameters
    ----------
    Convertible(0) : The amount of the convertible operand, like, Length or Duration.
    """
    pass

class Gross(CompositionConvertible):
    """`Data -> CompositionConvertible -> Gross`

    This corresponds to the values returned by the respective gross methods, the ones that return the
    entirety of the composition rounded in Measures. This is the **default** return.
    
    Parameters
    ----------
    Convertible(0) : The amount of the convertible operand, like, Length or Duration.
    """
    pass

class Net(CompositionConvertible):
    """`Data -> CompositionConvertible -> Net`

    This corresponds to the values returned by the respective net methods, the ones that return the
    timed amount specific to the Composition contained elements. This means that an empty composition
    will return `None`.
    
    Parameters
    ----------
    Convertible(0) : The amount of the convertible operand, like, Length or Duration.
    """
    pass


class Masking(Data):
    """`Data -> Masking`

    `Masking` is intended to be used with a Container, like a Clip, where the respective
    `Operand` items are set as masked or not masked based on a condition given.
    
    Parameters
    ----------
    Any : Conditions that need to be matched in an And fashion.
    """
    pass

class Select(Masking):
    """`Data -> Masking -> Select`

    `Select` uses a condition as the criteria for the Items NOT to be masked, masking all the others.
    
    Parameters
    ----------
    Any : Conditions that need NOT to be matched in an And fashion in order to an item NOT be masked.
    """
    pass

class Mask(Masking):
    """`Data -> Masking -> Mask`

    `Mask` uses a condition as the criteria for the Items to be masked.
    
    Parameters
    ----------
    Any : Conditions that needs to be matched in an And fashion in order to an item to be masked.
    """
    pass

class Unmask(Masking):
    """`Data -> Masking -> Unmask`

    Unmasks all items in the `Container`.

    Args:
        None
    """
    pass


class Parameter(Data):
    """`Data -> Parameter`

    `Parameter` allows a class to receive items as parameters.
    
    Parameters
    ----------
    Any() : Any type of operand.
    """
    pass

class Remove(Parameter):
    """`Data -> Parameter -> Remove`

    `Remove` allows a given parameter to be removed. The parameter needs to be removable.
    
    Parameters
    ----------
    Any() : Any type of operand.
    """
    pass


class Field(Data):
    """`Data -> Field`

    A `Field` represents the Token components separated with '_', like in `"cl_8:3b:D_-_F_A"`.
    
    Parameters
    ----------
    str("") : Any type of operand.
    """
    def __init__(self, *parameters):
        super().__init__(*parameters)
        if not isinstance(self._data, str): # Makes sure it's a string
            self._data = ""

    def get_parameter(self, index: int) -> str | None:
        token_dsl: str = self._data
        normalized_dsl: str = _normalize_dsl(token_dsl)
        element_fields: list[str] = normalized_dsl.split("_")
        if index < len(element_fields):
            return element_fields[index]
        return None

    def get_parameters(self) -> list[str]:
        line_dsl: str = self._data
        normalized_dsl: str = _normalize_dsl(line_dsl)
        return normalized_dsl.split("_")

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case str():
                if not isinstance(self._data, str):
                    self._data = ""
                return self._data
        return super().__mod__(operand)
    
    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Parameter():
                if isinstance(operand._data, str):
                    if self._data == "":
                        self._data = operand._data
                    elif operand._data != "":
                        self._data += "_" + operand._data
            case str():
                self.__iadd__(Parameter(operand))
        return self # remains as an Inline operand
    
    def __imul__(self, operand: any) -> Self:
        if isinstance(operand, int) and self._data != "":
            if operand > 1:
                new_line = self._data
                for _ in range(operand - 1):
                    new_line += "_" + self._data
                self._data = new_line
            elif operand == 0:
                self._data = ""
        return self # remains as an Inline operand
    

class Token(Data):
    """`Data -> Token`

    `Token` allows an Element to receive multiple parameters in a single string.
    
    The first field(:) for a token(,), has a tag, where where in `"c:3b:F"` is the tag "c", this tag represents the
    `Chord` element, these are the all available tags:

        +------+-----------------+
        | Tag  | Element         |
        +------+-----------------+
        | "r"  | Rest            |
        | "n"  | Note (optional) |
        | "c"  | Chord           |
        | "rt" | Retrigger       |
        | "cl" | Cluster         |
        | "cc" | ControlChange   |
        | "pb" | PitchBend       |
        | "pc" | ProgramChange   |
        | "at" | Aftertouch      |
        +------+-----------------+
        
    Parameters
    ----------
    str("") : A DSL string with multiple parameters, like, "n:1/8:C5#".
    """
    def __init__(self, *parameters):
        super().__init__(*parameters)
        if not isinstance(self._data, str): # Makes sure it's a string
            self._data = ""

    def get_field(self, index: int) -> str | None:
        token_dsl: str = self._data
        normalized_dsl: str = _normalize_dsl(token_dsl)
        element_fields: list[str] = normalized_dsl.split(":")
        if index < len(element_fields):
            return element_fields[index]
        return None

    def get_fields(self) -> list[str]:
        line_dsl: str = self._data
        normalized_dsl: str = _normalize_dsl(line_dsl)
        return normalized_dsl.split(":")
    
    def len(self) -> int:
        return len(self.get_fields())

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case str():
                if not isinstance(self._data, str):
                    self._data = ""
                return self._data
        return super().__mod__(operand)
    
    # CHAINABLE OPERATIONS

    def replace_field(self, index: int, field: str) -> Self:
        fields = self.get_fields()
        # Ensure the index exists
        if index < len(fields):
            # Replace the field
            fields[index] = field
            # Rebuild the token string
            self._data = ":".join(fields)
        return self
    

    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Line():
                if self._data == "":
                    self._data = operand._data
                elif operand._data != "":
                    self._data += ":" + operand._data
            case str():
                self.__iadd__(Line(operand))
        return self # remains as an Inline operand
    
    def __imul__(self, operand: any) -> Self:
        if isinstance(operand, int) and self._data != "":
            if operand > 1:
                new_line = self._data
                for _ in range(operand - 1):
                    new_line += ":" + self._data
                self._data = new_line
            elif operand == 0:
                self._data = ""
        return self # remains as an Inline operand
    
class Line(Data):
    """`Data -> Line`

    A `Line` is a string representing a series of Elements set by multiple tokens and fields.
    The previous `Element` configurations transit to the following ones.

    DSL stands for Domain-Specific Language: `Line[ Token(,)[ Field(:)[ Parameter(_) ] ] ]`

    The first field(:) for each token(,) in a `Line`, like in `"c:3b:F, c_-_4_1:3b"` has a tag that represents the
    respective `Element`, these are the tags:

        +------+-----------------+
        | Tag  | Element         |
        +------+-----------------+
        | "r"  | Rest            |
        | "n"  | Note (optional) |
        | "c"  | Chord           |
        | "rt" | Retrigger       |
        | "cl" | Cluster         |
        | "cc" | ControlChange   |
        | "pb" | PitchBend       |
        | "pc" | ProgramChange   |
        | "at" | Aftertouch      |
        | "a"  | Automation      |
        +------+-----------------+
        
    Parameters
    ----------
    str("") : A DSL string with multiple tokens separated with `,` like `"n:1/8:C5#, n_9:1/8::75"`.
    """
    def __init__(self, *parameters):
        super().__init__(*parameters)
        if not isinstance(self._data, str): # Makes sure it's a string
            self._data = ""

    def get_token(self, index: int) -> str | None:
        line_dsl: str = self._data
        normalized_dsl: str = _normalize_dsl(line_dsl)
        element_tokens: list[str] = normalized_dsl.split(",")
        if index < len(element_tokens):
            return element_tokens[index]
        return None

    def get_tokens(self) -> list[str]:
        line_dsl: str = self._data
        normalized_dsl: str = _normalize_dsl(line_dsl)
        return normalized_dsl.split(",")

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case str():
                if not isinstance(self._data, str):
                    self._data = ""
                return self._data
        return super().__mod__(operand)
    
    # CHAINABLE OPERATIONS

    def __iadd__(self, operand: any) -> Self:
        match operand:
            case Line():
                if self._data == "":
                    self._data = operand._data
                elif operand._data != "":
                    self._data += ", " + operand._data
            case str():
                self.__iadd__(Line(operand))
        return self # remains as an Inline operand
    
    def __imul__(self, operand: any) -> Self:
        if isinstance(operand, int) and self._data != "":
            if operand > 1:
                new_line = self._data
                for _ in range(operand - 1):
                    new_line += ", " + self._data
                self._data = new_line
            elif operand == 0:
                self._data = ""
        return self # remains as an Inline operand
    

class Inline(Data):
    """`Data -> Inline`

    `Inline` disables the `Operand` implicit copy on basic operations like `+` and `>>`.
    
    Parameters
    ----------
    Operand() : Any `Operand` to temporary disable operator implicit copies.
    """
    def __init__(self, operand: any = None):
        super().__init__()
        self._data: any = o.Operand() if operand is None else operand

    def __eq__(self, other: Any) -> bool:
        match other:
            case Inline():
                return self._data == other._data
            case _:
                return self._data == other

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol will extract the data source value.

        Examples
        --------
        >>> dotted_note = Dotted(1/4)
        >>> dotted_note % float() >> Print()
        0.25
        >>> dotted_note % Pipe( float() ) >> Print()
        0.375
        """
        match operand:
            case Pipe():
                return self._data
            case _:
                if isinstance(self._data, o.Operand):
                    return self._data % operand
                return self.deep_copy(operand)
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Inline():
                self._data = self.deep_copy(operand._data)
            case Pipe():
                self._data = self.deep_copy(operand._data)
            case tuple():
                if isinstance(self._data, o.Operand):
                    for single_operand in operand:
                        self._data << single_operand
            case _:
                if isinstance(self._data, o.Operand):
                    self._data << operand
        return self

    def __rshift__(self, operand: any) -> Self:
        self._data.__irshift__(operand)
        return self # remains as an Inline operand
    
    def __add__(self, operand: any) -> Self:
        self._data.__iadd__(operand)
        return self # remains as an Inline operand
    
    def __sub__(self, operand: any) -> Self:
        self._data.__isub__(operand)
        return self # remains as an Inline operand
    
    def __mul__(self, operand: any) -> Self:
        self._data.__imul__(operand)
        return self # remains as an Inline operand
    
    def __truediv__(self, operand: any) -> Self:
        self._data.__itruediv__(operand)
        return self # remains as an Inline operand


class Folder(Data):
    """`Data -> Folder`

    This class sets the Folder path where the files will ba placed whenever just the filename is given.
    Always add the `/` termination char to the given folder path, for example, `improvisation/`, otherwise \
        it will only change the filename by prepending it to the given one.

    Parameters
    ----------
    str("") : Sets the folder path where the files will be placed by Default (filename prefix).
    """
    def __init__(self, path: str = ""):
        if not isinstance(path, str):
            print("Path has to be a string!")
            path = ""
        super().__init__(path)


class Conditional(Data):
    """`Data -> Conditional`

    Operands that represent a Condition to be processed in bulk like And and Or.

    Parameters
    ----------
    Any(None) : A sequence of Any type of items that will be processed in bulk.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

class And(Conditional):
    """`Data -> Conditional -> And`

    A bulk of items that must all be validated as equal to the be considered equal.

    Parameters
    ----------
    Any(None) : A sequence of Any type of items that will be processed in bulk.
    """
    def __eq__(self, other: any) -> bool:
        if isinstance(other, And):
            return self._data == other._data
        for single_condition in self._data:
            if not other == single_condition:
                return False
        return True

class Or(Conditional):
    """`Data -> Conditional -> Or`

    A bulk of items that at least one must be validated as equal to all be considered equal.

    Parameters
    ----------
    Any(None) : A sequence of Any type of items that will be processed in bulk.
    """
    def __eq__(self, other: any) -> bool:
        if isinstance(other, Or):
            return self._data == other._data
        for single_condition in self._data:
            if other == single_condition:
                return True
        if isinstance(self._data, tuple) and len(self._data) > 0:
            return False
        return True


class Names(Data):
    """`Data -> Names`

    Used to return all names of the `Composition` contents.

    Parameters
    ----------
    str(None) : Group of names used in the `Composition` container.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)    # Saves as a tuple


class DataMany(Data):
    """`Data -> DataMany`

    Works like an wrapper of multiple parameters.

    Parameters
    ----------
    Any(None) : Group of data wrapped altogether.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)


class Performers(DataMany):
    def reset(self, *parameters) -> 'Performers':
        super().reset(*parameters)
        if isinstance(self._data, (tuple, list)):
            for single_operand in self._data:
                if isinstance(single_operand, o.Operand):
                    single_operand.reset()
        return self

class Elements(DataMany):
    """`Data -> DataMany -> Elements`

    Works as a wrapper of multiple elements needed to be used by multi element elements.

    Parameters
    ----------
    Element(None) : Group of elements wrapped altogether.
    """
    pass


class To(Data):
    """`Data -> To`

    Sets the destination name Device in a `JsonTalkie` communication.

    Parameters
    ----------
    str("Device") : Name of the targeted Device.
    """
    def __init__(self, to: str = "Device"):    # By default is "Device"
        super().__init__(to)


class TrackName(Data):
    """`Data -> TrackName`

    `Clip` parameter that sets the name of the track for the Midilist exporting.
    Basically works like a tag on a `Clip`, where multiple clips can share the same track name.

    Parameters
    ----------
    str("Track 1") : Name of the `Clip` track.
    """
    def __init__(self, track_name: str = "Track 1"):    # By default is "Track 1"
        super().__init__(track_name)


class Serialization(Data):
    """`Data -> Serialization`

    Serialized data representing all the parameters of a given `Operand`.

    Parameters
    ----------
    dict(None) : A dictionary with all the `Operand` configuration.
    """
    def __init__(self, serialization: dict | o.Operand = None):
        super().__init__()
        match serialization:
            case o.Operand():
                self._data = serialization.copy()
            case dict():
                self._data = self.deserialize(serialization)
            case _:
                self._data = ol.Null()  # Contrary to None, ol.Null allows .copy() of itself

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, for the case a Serialization(),
        those Operands are pass right away to the self Data Operand, with the
        exception of "% Operand()", that returns the self Data operand.

        Examples
        --------
        >>> serialization = Serialization() << Retrigger("D")
        >>> serialization % DataSource( Duration() ) >> Print(False)
        {'class': 'Duration', 'parameters': {'time_unit': {'class': 'NoteValue', 'parameters': {'value': 0.03125}}}}
        >>> serialization = Serialization() << (Retrigger("D") << Division(6))
        >>> serialization % DataSource( Duration() ) >> Print(False)
        {'class': 'Duration', 'parameters': {'time_unit': {'class': 'NoteValue', 'parameters': {'value': 0.08333333333333333}}}}
        """
        if isinstance(self._data, o.Operand):
            match operand:
                case Pipe():
                    return self._data % operand # Already includes the DataSource wrapper
                    # # WHY NOT JUST THIS?
                    # return self._data
                case dict():
                    if isinstance(self._data, o.Operand):
                        return self._data.getSerialization()
                    return dict()
                case _:
                    return self._data % operand
                    # # WHY NOT JUST THIS?
                    # return self._data.copy()
        return super().__mod__(operand)

    def __eq__(self, other: o.Operand | dict) -> bool:
        if self._data is None:
            if isinstance(other, Data) and other._data is None:
                return True # If both have Null data then they are equal
            return False
        if isinstance(self._data, o.Operand):
            match other:
                case dict():
                    return self._data.getSerialization() == other
                case Serialization():
                    return self._data == other._data
                case o.Operand():
                    return self._data.__class__ == other.__class__ and self._data == other  # Just compares the Operand
                case _:
                    return False
        return super().__eq__(other)
    
    if TYPE_CHECKING:
        from operand_rational import Position

    def getPlaylist(self, position_beats: Fraction | None = None) -> list:
        match self._data:
            case o.Operand():
                return self._data.getPlaylist(position_beats)
            case list():
                return self._data
        return []

    def getMidilist(self, midi_track = None, position_beats: Fraction | None = None) -> list:
        match self._data:
            case o.Operand():
                return self._data.getMidilist(midi_track, position_beats)
            case list():
                return self._data
        return []

    def getSerialization(self) -> dict:
        match self._data:
            case o.Operand():
                return self._data.getSerialization()
        return {}

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Serialization':
        self._data = self.deserialize(serialization)
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case Serialization():
                super().__lshift__(operand)
                self._data = operand._data.copy()   # It's and Operand for sure
            case Pipe():
                match operand._data:
                    case o.Operand():
                        self._data = operand._data
                    case dict():
                        self._data = self.deserialize(operand._data)
            case o.Operand():   # DON'T REMOVE THIS STEP !!
                self._data = operand.copy()
            case dict():
                self._data = self.deserialize(operand)
        return self

    def __rrshift__(self, operand: o.T) -> o.T:
        if not isinstance(self._data, ol.Null) and isinstance(operand, o.Operand) and isinstance(self._data, o.Operand):
            return operand >> self._data
        else:
            return super().__rrshift__(operand)

    def __add__(self, operand: 'o.Operand') -> 'o.Operand':
        return self._data + operand

    def __sub__(self, operand: any) -> 'o.Operand':
        return self._data - operand

    def __mul__(self, operand: any) -> 'o.Operand':
        return self._data * operand

    def __truediv__(self, operand: any) -> 'o.Operand':
        return self._data / operand

class Load(Serialization):
    """`Data -> Serialization -> Load`

    This `Operand` allows the loading of a saved file directly in to its respective `Operand` type.

    Parameters
    ----------
    str("json/_Save_jsonMidiCreator.json") : The filename and respective path to load the `Operand` serialization from.
    """
    def __new__(self, filename: str = "json/_Save_jsonMidiCreator.json"):
        if isinstance(filename, str):
            operand_data = self.load_operand_data(filename)
            if operand_data:
                return self.deserialize(operand_data)   # Must convert to an Operand
            return None

    @staticmethod
    def load_operand_data(filename: str) -> dict:
        import operand_generic as og
        file_path: str = filename
        folder: str = og.settings._folder
        if not isinstance(file_path, str):
            file_path = None
        else: # Folder is just a prefix
            file_path = folder + file_path
        return {} if file_path is None else c.loadJsonMidiCreator(file_path)


class Playlist(Data):
    """`Data -> Playlist`

    Operand representing a Playlist that can be played or used as a `Clip` in a `Block`.

    Parameters
    ----------
    list(None) : A list with all the Element dictionaries concerning their midi messages.
    """
    def __init__(self, *parameters):
        super().__init__([])
        self._track_name: str = "Playlist 1"
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter


    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, for the case a Playlist(),
        there is only one data to be extracted, a Play List, the only and always
        the result of the "%" operator.

        Examples
        --------
        >>> play_list = Playlist() << Retrigger("D")
        >>> play_list >> Play()
        <operand_data.Playlist object at 0x0000022EC9967490>
        """
        match operand:
            case Pipe():
                match operand._data:
                    case TrackName():       return operand._data << Pipe(self._track_name)
                    case list():            return self._data
                    case _:                 return super().__mod__(operand)
            case TrackName():       return TrackName(self._track_name)
            case str():             return self._track_name
            case list():            return self.shallow_playlist_list_copy(self._data)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        if self._data is None:
            if other is None:
                return True
            return False
        match other:
            case list():
                return self._data == other
            case Playlist():
                return self._data == other._data
            case o.Operand():
                return self._data == other.getPlaylist()
        return super().__eq__(other)

    def net_start(self) -> float:
        if len(self._data) > 0:
            start_position_ms: float = self._data[0]["time_ms"]
            for self_dict in self._data:
                if "time_ms" in self_dict and self_dict["time_ms"] < start_position_ms:
                    start_position_ms = self_dict["time_ms"]
            return start_position_ms
        return 0.0

    def net_finish(self) -> float:
        if len(self._data) > 0:
            finish_position_ms: float = self._data[0]["time_ms"]
            for self_dict in self._data:
                if "time_ms" in self_dict and self_dict["time_ms"] > finish_position_ms:
                    finish_position_ms = self_dict["time_ms"]
            return finish_position_ms
        return 0.0
  
    def getPlaylist(self, position_beats: Fraction | None = None) -> list[dict]:
        from . import operand_rational as ra
        if isinstance(self._data, list) and len(self._data) > 0:
            # Position generates a dummy list with the position as ms
            operand_playlist_list: list[dict] = ra.Position(position_beats).getPlaylist()
            offset_position_ms: float = operand_playlist_list[0]["time_ms"]
            self_playlist_list_copy: list[dict] = self.deep_copy( self._data )
            for self_dict in self_playlist_list_copy:
                if "time_ms" in self_dict:
                    self_dict["time_ms"] = round(self_dict["time_ms"] + offset_position_ms, 3)
            return self_playlist_list_copy
        return []

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()

        serialization["parameters"]["track_name"]   = self._track_name
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "track_name" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._track_name        = serialization["parameters"]["track_name"]
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_container as oc
        import operand_element as oe
    
        match operand:
            case Playlist():
                self._data          = self.shallow_playlist_list_copy(operand._data)
                self._track_name    = operand._track_name
            case Pipe():
                match operand._data:
                    case TrackName():
                        self._track_name = operand._data._data
                    case list():
                        self._data = operand._data
                    # Don't do this
                    # case _:
                    #     super().__lshift__(operand)
            case oc.Container() | oe.Element() | Playlist():
                self._data = operand.getPlaylist()
            case TrackName():
                self._track_name = operand._data
            case str():
                self._track_name = operand
            case list():
                self._data = self.shallow_playlist_list_copy(operand)
            case tuple():
                for single_operand in operand:
                    self << single_operand
            # Don't do this
            # case _:
            #     super().__lshift__(operand)
        return self
    
    # Pass trough method that always results in a Container (Self)
    def __rshift__(self, operand) -> Self:
        import operand_element as oe
        import operand_container as oc
        match operand:
            case Playlist() | oe.Element() | oc.Container():
                self += operand
                return self
        return super().__rshift__(operand)

    # Pass trough operation as last resort
    def __rrshift__(self, operand: o.T) -> o.T:
        self << operand # Left shifts remaining parameter (Pass Through)
        return operand


    def __iadd__(self, operand: any) -> Self:
        from . import operand_rational as ra
        import operand_element as oe
        import operand_container as oc
        match operand:
            case ra.Position() | ra.TimeUnit():
                # Position generates a dummy list with the position as ms
                operand_playlist_list: list[dict] = operand.getPlaylist()
                offset_position_ms: float = operand_playlist_list[0]["time_ms"]
                for self_dict in self._data:
                    if "time_ms" in self_dict:
                        self_dict["time_ms"] = round(self_dict["time_ms"] + offset_position_ms, 3)
            case list():
                if isinstance(self._data, list):
                    self._data.extend(
                        self.shallow_playlist_list_copy(operand)
                    )
            case Playlist() | oe.Element() | oc.Container():
                if isinstance(self._data, list):
                    self._data.extend(
                        operand.getPlaylist()
                    )
                    
        return self

    def __isub__(self, operand: any) -> Self:
        from . import operand_rational as ra
        match operand:
            case ra.Position() | ra.TimeUnit():
                # Position generates a dummy list with the position as ms
                operand_playlist_list: list[dict] = operand.getPlaylist()
                offset_position_ms: float = operand_playlist_list[0]["time_ms"]
                for self_dict in self._data:
                    if "time_ms" in self_dict:
                        self_dict["time_ms"] = round(self_dict["time_ms"] - offset_position_ms, 3)
                        
        return self

    # Only the "time_ms" data matters to be copied because the rest wont change (faster)
    @staticmethod
    def shallow_playlist_list_copy(playlist: list[dict]) -> list[dict]:
        if isinstance(playlist, list):
            return [
                single_dict.copy() for single_dict in playlist if isinstance(single_dict, dict)
            ]
        return []

class Import(Playlist):
    """`Data -> Playlist -> Import`

    Imports a given `Playlist` from a previously exported file.

    Parameters
    ----------
    str("json/_Export_jsonMidiCreator.json") : The filename and respective path to load the playlist from.
    """
    def __new__(self, filename: str = "json/_Export_jsonMidiCreator.json"):
        if isinstance(filename, str):
            operand_data = self.load_playlist(filename)
            if operand_data:
                if "clock" in operand_data[0]:
                    # Remove "clock" header
                    operand_data.pop(0)
                return Playlist(Pipe( operand_data ))
            return None

    @staticmethod
    def load_playlist(filename: str) -> list[dict]:
        import operand_generic as og
        file_path: str = filename
        folder: str = og.settings._folder
        if not isinstance(file_path, str):
            file_path = None
        else: # Folder is just a prefix
            file_path = folder + file_path
        return [] if file_path is None else c.loadJsonMidiPlay(file_path)


class Device(Data):
    """`Data -> Device`

    Keeps a string as the name of the given midi device it represents.
    It can be a substring and not the full name of the device.

    Parameters
    ----------
    str("Synth") : The device name connected via midi.
    """
    def __init__(self, device: str = "Synth"):
        super().__init__( device if isinstance(device, str) else "Synth" )



