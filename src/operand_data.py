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
import json
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_unit as ou
import operand_frame as of
import operand_label as ol


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
                    case of.Frame():                return self % Pipe( operand._data )
                    case Data():                    return self
                    case ol.Null() | None:          return ol.Null()
                    case _:                         return self._data
            case self.__class__():
                return self.copy()
            case of.Frame():                return self % operand
            case Serialization():           return self.getSerialization()
            case dict():
                serialization: dict = self.getSerialization()
                if len(operand) > 0:
                    return o.get_pair_key_data(operand, serialization)
                return serialization
            case Data():                    return self.copy()
            case _:                         return self.deep_copy(self._data)
            
    def __rmod__(self, operand: any) -> any:
        match operand:
            case dict():
                if isinstance(self._data, str):
                    return o.get_dict_key_data(self._data, operand)
                return {}
            case _:                         return ol.Null()
            
    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if isinstance(other, Data):
            return self._data == other._data
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, Conditional):
            return other == self
        return False
    
    def __lt__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if isinstance(other, Data):
            return self._data < other._data
        return False
    
    def __gt__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        if isinstance(other, Data):
            return self._data > other._data
        return False
    
    def __le__(self, other: o.Operand) -> bool:
        return self == other or self < other
    
    def __ge__(self, other: o.Operand) -> bool:
        return self == other or self > other

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
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            case Pipe():
                self._data = operand._data
            # Data doesn't load serialization, just processed data!!
            case Serialization():
                self.loadSerialization(operand % Pipe( dict() ))
            case Data():
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            case _: self._data = self.deep_copy(operand)
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
        self._data: any = o.Operand() if operand is None else operand

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
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
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

class Previous(Data):
    """`Data -> Previous`

    Data that contains the result of a previous iteration used in the Frame basic selectors.

    Parameters
    ----------
    Any(None) : Any type of data.
    """
    def __init__(self, data = None):
        super().__init__()
        self._data = data


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
        other ^= self    # Processes the Frame operand if any exists
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
        other ^= self    # Processes the Frame operand if any exists
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

class Clips(DataMany):
    pass

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
                self._data = o.Operand().loadSerialization(serialization)
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
                    if type(operand._data) == o.Operand:    # Default DataSource content
                        return self._data
                    return self._data % operand # Already includes the DataSource wrapper
                    # # WHY NOT JUST THIS?
                    # return self._data
                case dict():
                    if isinstance(self._data, o.Operand):
                        return self._data.getSerialization()
                    return dict()
                case _:
                    if type(operand) == o.Operand:    # Default DataSource content
                        return self._data.copy()
                    return self._data % operand
                    # # WHY NOT JUST THIS?
                    # return self._data.copy()
        return super().__mod__(operand)

    def __eq__(self, other: o.Operand | dict) -> bool:
        other ^= self    # Processes the Frame operand if any exists
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

    def getPlaylist(self, position_beats: Fraction = Fraction(0)) -> list:
        match self._data:
            case o.Operand():
                return self._data.getPlaylist(position_beats)
            case list():
                return self._data
        return []

    def getMidilist(self, midi_track = None, position_beats: Fraction = Fraction(0)) -> list:
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
        self._data = o.Operand().loadSerialization(serialization)
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Serialization():
                super().__lshift__(operand)
                self._data = operand._data.copy()   # It's and Operand for sure
            case Pipe():
                match operand._data:
                    case o.Operand():
                        self._data = operand._data
                    case dict():
                        self._data = o.Operand().loadSerialization(operand._data)
            case o.Operand():   # DON'T REMOVE THIS STEP !!
                self._data = operand.copy()
            case dict():
                self._data = o.Operand().loadSerialization(operand)
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
                return o.Operand().loadSerialization(operand_data)    # Must convert to an Operand
            return None

    @staticmethod
    def load_operand_data(filename: str) -> dict:
        return {} if filename is None else c.loadJsonMidiCreator(filename)


if TYPE_CHECKING:
    from operand_rational import Position
    from operand_generic import Staff

class Playlist(Data):
    """`Data -> Playlist`

    Operand representing a Playlist that can be played or used as a `Clip` in a `Part`.

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
        other ^= self    # Processes the Frame operand if any exists
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

    def start(self) -> float:
        if len(self._data) > 0:
            start_position_ms: float = self._data[0]["time_ms"]
            for self_dict in self._data:
                if "time_ms" in self_dict and self_dict["time_ms"] < start_position_ms:
                    start_position_ms = self_dict["time_ms"]
            return start_position_ms
        return 0.0

    def finish(self) -> float:
        if len(self._data) > 0:
            finish_position_ms: float = self._data[0]["time_ms"]
            for self_dict in self._data:
                if "time_ms" in self_dict and self_dict["time_ms"] > finish_position_ms:
                    finish_position_ms = self_dict["time_ms"]
            return finish_position_ms
        return 0.0
  
    def getPlaylist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        import operand_rational as ra
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
        import operand_rational as ra
        import operand_element as oe
        import operand_container as oc
        match operand:
            case ra.Position() | ra.TimeValue() | ra.TimeUnit():
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
        import operand_rational as ra
        match operand:
            case ra.Position() | ra.TimeValue() | ra.TimeUnit():
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
        return [] if filename is None else c.loadJsonMidiPlay(filename)


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


class Process(Data):
    """`Data -> Process`

    A process is no more than a call of a `Container` method, so, in nature a `Process` is a
    read only `Operand` without mutable parameters. Intended to be used in a chained `>>` sequence of operators.

    Parameters
    ----------
    Any(None) : A `Process` has multiple parameters dependent on the specific `Process` sub class.

    Returns:
        Any: All `Process` operands return the original left side `>>` input. Exceptions mentioned.
    """
    def __init__(self, parameters: any = None):
        super().__init__(parameters)

    @staticmethod
    def _clocked_playlist(operand: o.T) -> list[dict]:
        import operand_rational as ra
        import operand_generic as og
        import operand_element as oe
        import operand_container as oc

        playlist: list[dict] = []

        match operand:
            case oc.Composition() | oe.Element():
                # Generates the Clock data regardless, needed for correct JsonMidiPlayer processing
                clock_length: ra.Length = (operand.finish() % ra.Length()).roundMeasures()
                default_clock: oe.Clock = og.settings % oe.Clock()
                default_clock._duration_beats = ra.Duration(clock_length)._rational # The same staff will be given next
                playlist.extend( default_clock.getPlaylist( time_signature = operand._get_time_signature() ) )  # Clock Playlist
                playlist.extend( operand.getPlaylist() )    # Operand Playlist
            case Playlist():

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
                    single_measure_minutes: Fraction = og.settings.beats_to_minutes( single_measure_beats._rational )
                    single_measure_ms: float = o.minutes_to_time_ms( single_measure_minutes )
                    total_measures: int = last_time_ms // single_measure_ms
                    if last_time_ms > int(last_time_ms):
                        total_measures += 1
                    # Generates the Clock data regardless, needed for correct JsonMidiPlayer processing
                    default_clock: oe.Clock = og.settings % oe.Clock() << ra.Length(total_measures)
                    playlist.extend( default_clock.getPlaylist( time_signature = og.settings._time_signature ) )  # Clock Playlist
                    playlist.extend( operand_playlist ) # Operand Playlist

        return playlist


class ReadOnly(Process):
    """`Data -> Process -> ReadOnly`

    A ReadOnly process is one that results in no change of the subject `Operand`.

    Parameters
    ----------
    Any(None) : A `Process` has multiple parameters dependent on the specific `Process` sub class.

    Returns:
        Any: All `Process` operands return the original left side `>>` input. Exceptions mentioned.
    """
    pass


class RightShift(ReadOnly):
    """`Data -> Process -> ReadOnly -> RightShift`

    Applies the `>>` operation if process is `True`.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `>>` by the chained data sequence.
    bool(True) : By default, the the give `Operand` is targeted with `>>`.
    """
    def __init__(self, operand: o.Operand = None, process: bool = True):
        super().__init__()
        self._data = operand    # needs to keep the original reference (no copy)
        self._process: bool = process

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            if self._process:
                return self._data.__rshift__(operand)
            return operand
        return super().__rrshift__(operand)

    
class SideEffect(ReadOnly):
    """`Data -> Process -> ReadOnly -> SideEffect`

    This `Operand` can be inserted in a sequence of `>>` in order to apply as a side effect the chained
    data in the respective self data without changing the respective chained data sequence.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected inside the chained `>>` sequence.
    """
    def __init__(self, operand: o.Operand = None, process: bool = True):
        super().__init__()
        self._data = operand    # needs to keep the original reference (no copy)
        self._process: bool = process

class LeftShift(SideEffect):
    """`Data -> Process -> ReadOnly -> SideEffect -> LeftShift`

    Applies the `<<` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `<<` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            if self._process:
                self._data.__lshift__(operand)
            return operand
        return super().__rrshift__(operand)

class RightShift(SideEffect):
    """`Data -> Process -> ReadOnly -> SideEffect -> RightShift`

    Applies the `>>` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `>>` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            if self._process:
                self._data.__rshift__(operand)
            return operand
        return super().__rrshift__(operand)

class IAdd(SideEffect):    # i stands for "inplace"
    """`Data -> Process -> ReadOnly -> SideEffect -> IAdd`

    Applies the `+=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `+=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            if self._process:
                self._data.__iadd__(operand)
            return operand
        return super().__rrshift__(operand)

class ISub(SideEffect):
    """`Data -> Process -> ReadOnly -> SideEffect -> ISub`

    Applies the `-=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `-=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            if self._process:
                self._data.__isub__(operand)
            return operand
        return super().__rrshift__(operand)

class IMul(SideEffect):
    """`Data -> Process -> ReadOnly -> SideEffect -> IMul`

    Applies the `*=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `*=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            if self._process:
                self._data.__imul__(operand)
            return operand
        return super().__rrshift__(operand)

class IDiv(SideEffect):
    """`Data -> Process -> ReadOnly -> SideEffect -> IDiv`

    Applies the `/=` operation to self data without changing the original chained data or the chain itself.

    Parameters
    ----------
    Any(None) : Typically an `Operand` intended to be affected with `/=` by the chained data sequence.
    """
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            if self._process:
                self._data.__itruediv__(operand)
            return operand
        return super().__rrshift__(operand)


class Save(ReadOnly):
    """`Data -> Process -> ReadOnly -> Save`

    Saves all parameters' `Serialization` of a given `Operand` into a file.

    Parameters
    ----------
    str("json/_Save_jsonMidiCreator.json") : The filename of the Operand's serialization data.
    """
    def __init__(self, filename: str = "json/_Save_jsonMidiCreator.json"):
        super().__init__(filename)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            c.saveJsonMidiCreator(operand.getSerialization(), self._data)
            return operand
        return super().__rrshift__(operand)

class Export(ReadOnly):
    """`Data -> Process -> ReadOnly -> Export`

    Exports a file playable by the `JsonMidiPlayer` program.

    Parameters
    ----------
    str("json/_Export_jsonMidiPlayer.json") : The filename of the JsonMidiPlayer playable file.
    """
    def __init__(self, filename: str = "json/_Export_jsonMidiPlayer.json"):
        super().__init__(filename)

    def __rrshift__(self, operand: o.T) -> o.T:
        match operand:
            case o.Operand():
                playlist: list[dict] = self._clocked_playlist(operand)
                c.saveJsonMidiPlay(playlist, self._data)
                return operand
            case _:
                return super().__rrshift__(operand)

class MidiExport(ReadOnly):
    """`Data -> Process -> ReadOnly -> MidiExport`

    Exports a file playable by a Midi player.

    Parameters
    ----------
    str("midi/_MidiExport_song.mid") : The filename of the Midi playable file.
    """
    def __init__(self, filename: str = "midi/_MidiExport_song.mid"):
        super().__init__(filename)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            c.saveMidiFile(operand.getMidilist(), self._data)
            return operand
        return super().__rrshift__(operand)


class Plot(ReadOnly):
    """`Data -> Process -> ReadOnly -> Plot`

    Plots the `Note`s in a `Clip`, if it has no Notes it plots the existing `Automation` instead.

    Args:
        block (bool): Suspends the program until the chart is closed.
        pause (float): Sets a time in seconds before the chart is closed automatically.
        iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
            this is dependent on a n_button being given.
        n_button (Callable): A function that takes a Clip to be used to generate a new iteration.
        c_button (Callable): A function intended to play the plotted clip among other compositions.
        e_button (Callable): A function to be executed by itself without any output required.
    """
    def __init__(self, block: bool = True, pause: float = 0.0, iterations: int = 0,
                 n_button: Optional[Callable[['Composition'], 'Composition']] = None,
                 c_button: Optional[Callable[['Composition'], 'Composition']] = None,
                 e_button: Optional[Callable[['Composition'], Any]] = None):
        super().__init__((block, pause, iterations, n_button, c_button, e_button))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        import operand_element as oe
        if isinstance(operand, (oc.Composition, oe.Element)):
            return operand.plot(*self._data)
        return operand


class Play(ReadOnly):
    """`Data -> Process -> ReadOnly -> Play`

    Plays an `Element` or a `Composition` straight on into the `JsonMidiPlayer` program.

    Args:
        verbose (bool): Defines the `verbose` mode of the playing.
        plot (bool): Plots a chart before playing it.
        block (bool): Blocks the Plot until is closed and then plays the plotted content.
    """
    def __init__(self, verbose: bool = False, plot: bool = False, block: bool = False):
        super().__init__((verbose, plot, block))

    def __rrshift__(self, operand: o.T) -> o.T:
        import threading
        import operand_container as oc
        import operand_element as oe
        match operand:
            case oc.Composition() | oe.Element() | Playlist():
                if isinstance(operand, oe.Element) or len(operand % Pipe(list())) > 0:
                    playlist: list[dict] = self._clocked_playlist(operand)
                    if self._data[1] and self._data[2]:
                        # Start the function in a new process
                        process = threading.Thread(target=c.jsonMidiPlay, args=(playlist, self._data[0]))
                        process.start()
                        operand >> Plot(self._data[2])
                    else:
                        if self._data[1] and not self._data[2]:
                            operand >> Plot(self._data[2])
                        c.jsonMidiPlay(playlist, self._data[0])
                else:
                    print(f"Warning: Trying to play an **empty** list!")
                return operand
            case _:
                return super().__rrshift__(operand)
    
    @staticmethod
    def play(operand: o.T) -> o.T:
        return Play().__rrshift__(operand)


class Print(ReadOnly):
    """`Data -> Process -> ReadOnly -> Print`

    Prints the Operand's parameters in a JSON alike layout if it's an `Operand` being given,
    otherwise prints directly like the common `print` function.

    Args:
        formatted (bool): If False prints the `Operand` content in a single line.
    """
    def __init__(self, formatted: bool = True):
        super().__init__( 1 if formatted is None else formatted )

    def __rrshift__(self, operand: o.T) -> o.T:
        match operand:
            case o.Operand():
                operand_serialization = operand.getSerialization()
                if self._data:
                    serialized_json_str = json.dumps(operand_serialization)
                    json_object = json.loads(serialized_json_str)
                    json_formatted_str = json.dumps(json_object, indent=4)
                    print(json_formatted_str)
                else:
                    print(operand_serialization)
            # case tuple():
            #     return super().__rrshift__(operand)
            case _: print(operand)
        return operand

class Copy(ReadOnly):
    """`Data -> Process -> ReadOnly -> Copy`

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
            return operand.copy(*self._data)
        return super().__rrshift__(operand)

class Reset(Process):
    """`Data -> Process -> Reset`

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
            return operand.reset(*self._data)
        return super().__rrshift__(operand)

class Clear(Process):
    """`Data -> Process -> Clear`

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
            return operand.clear(*self._data)
        return super().__rrshift__(operand)


if TYPE_CHECKING:
    from operand_generic import Scale

class ScaleProcess(Process):
    """`Data -> Process -> ScaleProcess`
    """
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_generic as og
        if isinstance(operand, og.Scale):
            return self.__irrshift__(operand.copy())
        return super().__rrshift__(operand)

    def __irrshift__(self, operand: o.T) -> o.T:
        import operand_generic as og
        if isinstance(operand, og.Scale):
            return self._process(operand)
        else:
            print(f"Warning: Operand is NOT a `Scale`!")
        return super().__rrshift__(operand)

    def _process(self, operand: o.T) -> o.T:
        return operand

class Modulate(ScaleProcess):    # Modal Modulation
    """`Data -> Process -> ScaleProcess -> Modulate`

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
        return operand.modulate(self._data)

class Transpose(ScaleProcess):    # Chromatic Transposition
    """`Data -> Process -> ScaleProcess -> Transpose`

    Transpose() is used to rotate a scale by semitones.
    
    Parameters
    ----------
    int(7) : Transpose a given Scale by 7 semitones as the default.
    """
    def __init__(self, semitones: int = 7):
        super().__init__(semitones)

    # CHAINABLE OPERATIONS

    def _process(self, operand: 'Scale') -> 'Scale':
        return operand.transpose(self._data)


if TYPE_CHECKING:
    from operand_container import Container

class ContainerProcess(Process):
    """`Data -> Process -> ContainerProcess`

    Processes applicable exclusively to `Container` operands.
    """
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            if operand.is_a_mask(): # Mask retains the original Container
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
    """`Data -> Process -> ContainerProcess -> Sort`

    Sorts the contained items by a given parameter type.

    Args:
        parameter (type): Defines the given parameter type to sort by.
        reverse (bool): Reverses the sorting if `True`.
    """
    from operand_rational import Position

    def __init__(self, parameter: type = Position, reverse: bool = False):
        super().__init__((parameter, reverse))

    def _process(self, operand: 'Container') -> 'Container':
        return operand.sort(*self._data)


class Mask(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Mask`

    Masks the items that meet the conditions (equal to). Masks can't be copied!

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
        return operand.mask(*self._data)

class Filter(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Filter`

    A Filter selects the items that meet the conditions (equal to).
    Filters remain as `Containers` and thus they **can** be copied!

    Args:
        condition (Any): Sets a condition to be compared with `==` operator.
    """
    def __init__(self, *conditions):
        super().__init__(conditions)

    def _process(self, operand: 'Container') -> 'Container':
        return operand.filter(*self._data)


class Drop(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Drop`

    Removes items based on a given probability of such removal happening.

    Args:
        probability (float): The probability of an item being removed.
        chaos (Chaos): The chaotic generation targeted by the probability.
    """
    def __init__(self, probability: float | Fraction = 1/16, chaos: 'Chaos' = None):
        super().__init__((probability, chaos))

    def _process(self, operand: 'Container') -> 'Container':
        return operand.drop(*self._data)

class Operate(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Operate`

    Allows the setting of a specific operator as operation with a str as operator symbol.

    Args:
        operand (Any): `Operand` that is the source of the operation.
        operator (str): The operator `op` that becomes processed as `self op operand`.
    """
    def __init__(self, operand: Any = None, operator: str = "<<"):
        super().__init__((operand, operator))

    def _process(self, operand: 'Container') -> 'Container':
        return operand.operate(*self._data)

if TYPE_CHECKING:
    from operand_element import Note

class Transform(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Transform`

    Transforms each item by wrapping it with the new operand type given.

    Args:
        operand_type (type): The type of `Operand` by which each item will be transformed into.
    """
    def __init__(self, operand_type: type = 'Note'):
        super().__init__(operand_type)

    def _process(self, operand: 'Container') -> 'Container':
        return operand.transform(self._data)

if TYPE_CHECKING:
    from operand_chaos import Chaos
    from operand_rational import Probability

class Shuffle(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Shuffle`

    Reaffects the given parameter type in a chaotic manner.

    Args:
        chaos (Chaos): An Chaos object to be used as sorter.
        parameter (type): The type of parameter being swapped around the items.
    """
    from operand_rational import Position

    def __init__(self, chaos: 'Chaos' = None, parameter: type = Position):
        super().__init__((chaos, parameter))

    def _process(self, operand: 'Container') -> 'Container':
        return operand.shuffle(*self._data)

class Swap(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Swap`

    Reaffects the given parameter type in a chaotic manner accordingly to a probability.

    Args:
        probability (Probability): A given probability of swapping.
        chaos (Chaos): An Chaos object to be used as sorter.
        parameter (type): The type of parameter being swapped around the items.
    """
    from operand_rational import Position

    def __init__(self, probability: 'Probability' = None, chaos: 'Chaos' = None, parameter: type = Position):
        super().__init__((probability, chaos, parameter))

    def _process(self, operand: 'Container') -> 'Container':
        return operand.swap(*self._data)

class Reverse(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Reverse`

    Reverses the self list of items.

    Args:
        None
    """
    def __init__(self, ignore_empty_measures: bool = True):
        super().__init__(ignore_empty_measures)

    def _process(self, operand: 'Container') -> 'Container':
        return operand.reverse(self._data)

class Recur(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Recur`

    Calls the function on the successive items in a Xn+1 = Xn fashion (recursive),
    where n is the previous element and n+1 the next one.

    Args:
        recursion (Callable): recursive function.
        parameter (type): The type of parameter being processed by the recursive function.
    """
    from operand_rational import Duration

    def __init__(self, recursion: Callable = lambda d: d/2, parameter: type = Duration):
        super().__init__((recursion, parameter))

    def _process(self, operand: 'Container') -> 'Container':
        return operand.recur(*self._data)

class Rotate(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Rotate`

    Rotates a given parameter by a given offset, by other words,
    does a displacement for each Element in the Container list of
    a chosen parameter by the offset amount.

    Args:
        a (int): The offset amount of the list index, displacement.
        b (type): The type of parameter being displaced, rotated.
    """
    from operand_rational import Position

    def __init__(self, offset: int = 1, parameter: type = Position):
        super().__init__((offset, parameter))

    def _process(self, operand: 'Container') -> 'Container':
        return operand.rotate(*self._data)

class Erase(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Erase`

    Erases all the given items in the present container and propagates the deletion
    of the same items for the containers above.

    Args:
        *parameters: After deletion, any given parameter will be operated with `<<` in the sequence given.
    """
    def _process(self, operand: 'Container') -> 'Container':
        return operand.erase(*self._data)

class Upper(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> Upper`

    Returns self or the upper container if existent up to the last one if no argument is given, or,
    up to the one above the level given.

    Args:
        level: The level at which the upper container is returned.
    """
    def __init__(self, level: int = None):
        super().__init__(level)

    def _process(self, operand: 'Container') -> 'Container':
        return operand.upper(self._data)


if TYPE_CHECKING:
    from operand_container import Composition
    from operand_container import Clip

TypeComposition = TypeVar('TypeComposition', bound='Composition')  # TypeComposition represents any subclass of Operand

class CompositionProcess(ContainerProcess):
    """`Data -> Process -> ContainerProcess -> CompositionProcess`

    Processes applicable to any `Composition`.
    """
    def _process(self, operand: TypeComposition) -> TypeComposition:
        return operand

class Loop(CompositionProcess):
    """`Data -> Process -> ContainerProcess -> CompositionProcess -> Loop`

    Creates a loop from the Composition from the given `Position` with a given `Length`.

    Args:
        position (Position): The given `Position` where the loop starts at.
        length (Length): The `Length` of the loop.
    """
    def __init__(self, position = 0, length = 4):
        super().__init__((position, length))

    def _process(self, composition: TypeComposition) -> TypeComposition:
        return composition.loop(*self._data)


class ClipProcess(CompositionProcess):
    """`Data -> Process -> ContainerProcess -> CompositionProcess -> ClipProcess`

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

class Fit(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Fit`

    Fits the entire clip in a given length.

    Args:
        length (Length): A length in which the clip must fit.
    """
    from operand_rational import Length

    def __init__(self, length: 'Length' = None):
        super().__init__(length)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.fit(self._data)

class Link(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Link`

    Adjusts the duration/length of each `Element` to connect to the start of the next element.
    For the last element in the clip, this is extended up to the end of the `Measure`.

    Args:
        ignore_empty_measures (bool): Ignores first empty Measures if `True`.
    """
    def __init__(self, ignore_empty_measures: bool = True):
        super().__init__(ignore_empty_measures)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.link(self._data)

class Switch(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Switch`

    `Switch` just switches the given type of parameters with each other elements.

    Args:
        None
    """
    def __init__(self, parameter_type: type = None):
        super().__init__(parameter_type)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.switch(self._data)

class Stack(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Stack`

    Moves each Element to start at the finish position of the previous one.
    If it's the first element then its position becomes 0 or the staring of the first non empty `Measure`.

    Args:
        ignore_empty_measures (bool): Ignores first empty Measures if `True`.
    """
    def __init__(self, ignore_empty_measures: bool = True):
        super().__init__(ignore_empty_measures)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.stack(self._data)

class Quantize(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Quantize`

    Quantizes a `Clip` by a given amount from 0.0 to 1.0.

    Args:
        amount (float): The amount of quantization to apply from 0.0 to 1.0.
    """
    def __init__(self, amount: float = 1.0):
        super().__init__(amount)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.quantize(self._data)


class Decompose(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Decompose`

    Transform each element in its component elements if it's a composed element,
    like a chord that is composed of multiple notes, so, it becomes those multiple notes instead.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.decompose()

if TYPE_CHECKING:
    from operand_generic import Arpeggio
    from operand_element import Element
    
class Arpeggiate(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Arpeggiate`

    Distributes each element accordingly to the configured arpeggio by the parameters given.

    Args:
        parameters: Parameters that will be passed to the `Arpeggio` operand.
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.arpeggiate(self._data)


class Purge(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Purge`

    With time a `Clip` may accumulate redundant Elements, this method removes all those elements.

    Args:
        None.
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.purge()


class Stepper(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Stepper`

    Sets the steps in a Drum Machine for a given `Note`.

    Args:
        pattern (str): A string where the 1s in it set where the triggered steps are.
        note (Any): A note or any respective parameter that sets each note.
    """
    def __init__(self, pattern: str = "1... 1... 1... 1...", note: Any = None):
        super().__init__((pattern, note))

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.stepper(*self._data)

class Automate(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Automate`

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
        super().__init__((values, pattern, automation, interpolate))

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.automate(*self._data)

class Interpolate(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Interpolate`

    Interpolates the multiple values of a given `Automation` element by `Channel`.

    Args:
        None.
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.interpolate()

class Oscillate(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Oscillate`

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
        super().__init__((amplitude, wavelength, offset, phase, parameter))

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.oscillate(*self._data)


class Tie(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Tie`

    Extends the `Note` elements as tied when applicable.
    Works only on Notes, and NOT on its derived elements, as `Chord`,
    do `Decompose` if needed to transform a `Chord` into Notes.

    Args:
        decompose (bool): If `True`, decomposes elements derived from `Note` first.
    """
    def __init__(self, decompose: bool = True):
        super().__init__((decompose,))  # Has to have the ending "," to be considered a tuple

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.tie(*self._data)

class Join(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Join`

    Joins all same type notes with the same `Pitch` as a single `Note`, from left to right.

    Args:
        decompose (bool): If `True`, decomposes elements derived from `Note` first.
    """
    def __init__(self, decompose: bool = True):
        super().__init__((decompose,))  # Has to have the ending "," to be considered a tuple

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.join(*self._data)


class Slur(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Slur`

    Changes the note `Gate` in order to crate a small overlap.

    Args:
        gate (float): Can be given a different gate from 1.05, de default.
    """
    def __init__(self, gate: float = 1.05):
        super().__init__(gate)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.slur(self._data)

class Smooth(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Smooth`

    Adjusts the `Note` octave to have the closest pitch to the previous one.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.smooth()


class Flip(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Flip`

    Flip is similar to reverse but instead of reversing the elements position it reverses the
    Note's respective Pitch, like vertically mirrored.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.flip()

class Invert(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Invert`

    `Invert` is similar to 'Flip' but based in a center defined by the first note on which all notes are vertically mirrored.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.invert()


class Snap(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Snap`

    For `Note` and derived, it snaps the given `Pitch` to the one of the key signature.

    Args:
        up (bool): By default it snaps to the closest bellow pitch, but if set as True, \
            it will snap to the closest above pitch instead.
    """
    def __init__(self, up: bool = False):
        super().__init__(up)

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.snap(self._data)

if TYPE_CHECKING:
    from operand_rational import Length

class Extend(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Extend`

    Extends (stretches) the given clip along a given length.

    Args:
        length (Length): The length along which the clip will be extended (stretched).
    """
    def __init__(self, length: 'Length' = None):
        super().__init__( length )

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.extend(self._data)

class Trim(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Trim`

    Trims the given clip at a given length.

    Args:
        length (Length): The length of the clip that will be trimmed.
    """
    def __init__(self, length: 'Length' = None):
        super().__init__( length )

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.trim(self._data)

class Cut(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Cut`

    Cuts (removes) the section of the clip from the start to the finish positions.

    Args:
        start (Position): Starting position of the section to be cut.
        finish (Position): Finish position of the section to be cut.
    """
    from operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__((start, finish))

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.cut(*self._data)

class Select(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Select`

    Selects the section of the clip that will be preserved.

    Args:
        start (Position): Starting position of the section to be selected.
        finish (Position): Finish position of the section to be selected.
    """
    from operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__((start, finish))

    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.select(*self._data)

class Monofy(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Monofy`

    Cuts out any part of an element Duration that overlaps with the next element.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.monofy()

class Fill(ClipProcess):
    """`Data -> Process -> ContainerProcess -> ClipProcess -> Fill`

    Adds up Rests to empty spaces (lengths) in a staff for each Measure.

    Args:
        None
    """
    def _process(self, operand: 'Clip') -> 'Clip':
        return operand.fill()


class PartProcess(CompositionProcess):
    """`Data -> Process -> ContainerProcess -> CompositionProcess -> PartProcess`

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
    """`Data -> Process -> ContainerProcess -> CompositionProcess -> SongProcess`

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


