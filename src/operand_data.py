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
            case DataSource():
                match operand._data:
                    case of.Frame():                return self % DataSource( operand._data )
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
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, Data):
            return self._data == other._data
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, Conditional):
            return other == self
        return False
    
    def __lt__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, Data):
            return self._data < other._data
        return False
    
    def __gt__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
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
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            case DataSource():
                self._data = operand._data
            # Data doesn't load serialization, just processed data!!
            case Serialization():
                self.loadSerialization(operand % DataSource( dict() ))
            case Data():
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            case _: self._data = self.deep_copy(operand)
        return self

class DataSource(Data):
    """
    DataSource() allows the direct extraction (%) or setting (<<)
    of the given Operand parameters without the normal processing.
    
    Parameters
    ----------
    first : Operand_like
        The Operand intended to be directly extracted or set

    Examples
    --------
    >>> single_note = Note()
    >>> position_source = single_note % DataSource( Position() )
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
        >>> dotted_note % DataSource( float() ) >> Print()
        0.375
        """
        match operand:
            case DataSource():
                return self._data
            case _:
                if isinstance(self._data, o.Operand):
                    return self._data % operand
                return self.deep_copy(operand)
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case DataSource():
                self._data = self.deep_copy(operand._data)
            case tuple():
                if isinstance(self._data, o.Operand):
                    for single_operand in operand:
                        self._data << single_operand
            case _:
                if isinstance(self._data, o.Operand):
                    self._data << operand
        return self


class Next(Data):
    def __init__(self, data = None):
        super().__init__()
        self._data = data

class Previous(Data):
    def __init__(self, data = None):
        super().__init__()
        self._data = data


class Conditional(Data):
    def __init__(self, *parameters):
        super().__init__(parameters)

class And(Conditional):
    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, And):
            return self._data == other._data
        for single_condition in self._data:
            if not other == single_condition:
                return False
        return True

class Or(Conditional):
    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other, Or):
            return self._data == other._data
        for single_condition in self._data:
            if other == single_condition:
                return True
        if isinstance(self._data, tuple) and len(self._data) > 0:
            return False
        return True


class ClipParameter(Data):   # Just a data wrapper
    def __init__(self, operand: any = None):
        super().__init__()
        self._data = operand

class PartParameter(Data):   # Just a data wrapper
    def __init__(self, operand: any = None):
        super().__init__()
        self._data = operand

class PlaylistParameter(Data):   # Just a data wrapper
    def __init__(self, operand: any = None):
        super().__init__()
        self._data = operand

class TrackName(Data):
    def __init__(self, track_name: str = "Track 1"):    # By default is "Track 1"
        super().__init__(track_name)



class Serialization(Data):
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
                case DataSource():
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
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
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

    def getPlaylist(self, position: 'Position' = None) -> list:
        match self._data:
            case o.Operand():
                return self._data.getPlaylist(position)
            case list():
                return self._data
        return []

    def getMidilist(self, midi_track = None, position = None) -> list:
        match self._data:
            case o.Operand():
                return self._data.getMidilist(midi_track, position)
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
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Serialization():
                super().__lshift__(operand)
                self._data = operand._data.copy()   # It's and Operand for sure
            case DataSource():
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

if TYPE_CHECKING:
    from operand_rational import Position
    from operand_generic import Staff

class Playlist(Data):
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
            case DataSource():
                match operand._data:
                    case TrackName():       return operand._data << DataSource(self._track_name)
                    case list():            return self._data
                    case _:                 return super().__mod__(operand)
            case TrackName():       return TrackName(self._track_name)
            case str():             return self._track_name
            case list():            return self.shallow_playlist_list_copy(self._data)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
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
  
    def getPlaylist(self, position: 'Position' = None) -> list[dict]:
        import operand_rational as ra
        if isinstance(self._data, list) and len(self._data) > 0:
            if not isinstance(position, ra.Position):
                position: ra.Position = ra.Position(0)
            # Position generates a dummy list with the position as ms
            operand_playlist_list: list[dict] = position.getPlaylist()
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
        
        if isinstance(operand, Parameters):
            for single_parameter in operand._data:
                self << single_parameter

        else:

            if isinstance(operand, PlaylistParameter):
                operand = operand._data

            match operand:
                case Playlist():
                    self._data          = self.shallow_playlist_list_copy(operand._data)
                    self._track_name    = operand._track_name
                case DataSource():
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
            case ra.Position() | ra.TimeValue() | ou.TimeUnit():
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
            case PlaylistParameter():
                self += operand._data
            case Parameters():
                for single_parameter in operand._data:
                    self += single_parameter

        return self

    def __isub__(self, operand: any) -> Self:
        import operand_rational as ra
        match operand:
            case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                # Position generates a dummy list with the position as ms
                operand_playlist_list: list[dict] = operand.getPlaylist()
                offset_position_ms: float = operand_playlist_list[0]["time_ms"]
                for self_dict in self._data:
                    if "time_ms" in self_dict:
                        self_dict["time_ms"] = round(self_dict["time_ms"] - offset_position_ms, 3)
            case PlaylistParameter():
                self -= operand._data
            case Parameters():
                for single_parameter in operand._data:
                    self -= single_parameter

        return self

    # Only the "time_ms" data matters to be copied because the rest wont change (faster)
    @staticmethod
    def shallow_playlist_list_copy(playlist: list[dict]) -> list[dict]:
        if isinstance(playlist, list):
            return [
                single_dict.copy() for single_dict in playlist if isinstance(single_dict, dict)
            ]
        return []


class Load(Serialization):
    def __new__(self, filename: str = "json/_Save_jsonMidiCreator.json"):
        if isinstance(filename, str):
            operand_data = self.load_operand_data(filename)
            if operand_data:
                return o.Operand().loadSerialization(operand_data)    # Must convert to an Operand
            return None

    @staticmethod
    def load_operand_data(filename: str) -> dict:
        return {} if filename is None else c.loadJsonMidiCreator(filename)
    


class Import(Playlist):
    def __init__(self, filename: str = None):
        super().__init__()
        if isinstance(filename, str):
            self._data = [] if filename is None else c.loadJsonMidiPlay(filename)
            if self._data and "clock" in self._data[0]:
                # Remove "clock" header
                self._data.pop(0)


class Device(Data):
    def __init__(self, device: str = None):
        super().__init__( device if isinstance(device, str) else "Synth" )

class DataMany(Data):
    def __init__(self, *parameters):
        super().__init__(parameters)

class Parameters(DataMany):
    def __init__(self, *parameters):    # Allows multiple parameters
        super().__init__()
        self._data = parameters

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

class Result(Data):
    pass

class Chain(Data):
    def __init__(self, *parameters):
        super().__init__()
        self << parameters

    def __rrshift__(self, operand: o.T) -> o.T:
        for process in self._data:
            operand >>= process
        return operand

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "data" in serialization["parameters"]):

            super().loadSerialization(serialization)
            data_list: list = self.deserialize(serialization["parameters"]["data"])
            self._data = tuple(data_list)
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Chain():
                self._data = self.deep_copy(operand._data)
            case DataSource():
                match operand._data:
                    case tuple():
                        self._data = operand._data
                    case _:
                        super().__lshift__(operand)
            case tuple():
                # self._data = operand
                self._data = self.deep_copy(operand)
            case _:
                self._data = tuple(self.deep_copy(operand))
        return self


class Process(Data):
    
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
                default_clock: oe.Clock = og.defaults % oe.Clock()
                clock_length: ra.Length = operand.finish().transformToLength().roundMeasures()
                default_clock.set_staff_reference(operand.get_staff_reference()) << clock_length    # Element converts Length to Duration
                playlist.extend( default_clock.getPlaylist(devices_header=False) )  # Clock Playlist
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
                    single_measure_ms: float = o.minutes_to_time_ms( ra.Measures(1).getMinutes() )
                    total_measures: int = last_time_ms // single_measure_ms
                    if last_time_ms > int(last_time_ms):
                        total_measures += 1
                    # Generates the Clock data regardless, needed for correct JsonMidiPlayer processing
                    default_clock: oe.Clock = og.defaults % oe.Clock() << ra.Length(total_measures)
                    playlist.extend( default_clock.getPlaylist(devices_header=False) )  # Clock Playlist
                    playlist.extend( operand_playlist ) # Operand Playlist

        return playlist

    
class SideEffects(Process):
    def __init__(self, operand: o.Operand = None):
        super().__init__()
        self._data = operand    # needs to keep the original reference (no copy)

class LeftShift(SideEffects):
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            self._data << operand
            return operand
        return super().__rrshift__(operand)

class RightShift(SideEffects):
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(self._data, o.Operand):
            operand >> self._data
            return operand
        return super().__rrshift__(operand)

class Save(Process):
    def __init__(self, filename: str = "json/_Save_jsonMidiCreator.json"):
        super().__init__(filename)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            c.saveJsonMidiCreator(operand.getSerialization(), self._data)
            return operand
        return super().__rrshift__(operand)

class Export(Process):
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

class MidiExport(Process):
    def __init__(self, filename: str = "song.mid"):
        super().__init__(filename)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            c.saveMidiFile(operand.getMidilist(), self._data)
            return operand
        return super().__rrshift__(operand)

class Play(Process):
    """
    Play() allows to send a given Element to the Player directly without the need of Exporting to the respective .json Player file.
    
    Parameters
    ----------
    first : integer_like
        By default it's configured without any verbose, set to 1 or True to enable verbose
    """
    def __init__(self, verbose: bool = False, plot: bool = False, block: bool = False):
        super().__init__((verbose, plot, block))

    def __rrshift__(self, operand: o.T) -> o.T:
        import threading
        match operand:
            case o.Operand():
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
                return operand
            case _:
                return super().__rrshift__(operand)
    
    @staticmethod
    def play(operand: o.T) -> o.T:
        return Play().__rrshift__(operand)


class Print(Process):
    """
    Print() allows to get on the console the configuration of the source Operand in a JSON layout.
    
    Parameters
    ----------
    first : integer_like
        Sets the indent of the JSON print layout with the default as 4
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

class Copy(Process):
    """
    Copy() does an total duplication of the Operand including its parts.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.copy(*self._data)
        return super().__rrshift__(operand)

class Reset(Process):
    """
    Reset() does an total reset of the Operand including its non accessible parameters.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.reset(*self._data)
        return super().__rrshift__(operand)

class Clear(Process):
    """
    Clear() does an total clean up of all parameters including a reset.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.clear(*self._data)
        return super().__rrshift__(operand)


if TYPE_CHECKING:
    from operand_container import Container

class ContainerProcess(Process):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return self.process(operand)
        return super().__rrshift__(operand)

    def process(self, operand: o.T) -> o.T:
        return operand

class Sort(ContainerProcess):
    from operand_rational import Position

    def __init__(self, parameter: type = Position, reverse: bool = True):
        super().__init__((parameter, reverse))

    def process(self, operand: 'Container') -> 'Container':
        return operand.sort(*self._data)

class Filter(ContainerProcess):
    def __init__(self, condition: any = None, shallow_copy: bool = True):
        super().__init__((condition, shallow_copy))

    def process(self, operand: 'Container') -> 'Container':
        return operand.filter(*self._data)

class Dropper(ContainerProcess):
    def __init__(self, probability: float | Fraction = 1/16, chaos: 'Chaos' = None):
        super().__init__((probability, chaos))

    def process(self, operand: 'Container') -> 'Container':
        return operand.dropper(*self._data)

class Operate(ContainerProcess):
    def __init__(self, operand: any = None, operator: str = "<<"):
        super().__init__((operand, operator))

    def process(self, operand: 'Container') -> 'Container':
        return operand.operate(*self._data)

if TYPE_CHECKING:
    from operand_element import Note

class Transform(ContainerProcess):
    def __init__(self, operand_type: type = 'Note'):
        super().__init__(operand_type)

    def process(self, operand: 'Container') -> 'Container':
        return operand.transform(self._data)

if TYPE_CHECKING:
    from operand_chaos import Chaos
    from operand_rational import Probability

class Shuffle(ContainerProcess):
    from operand_rational import Position

    def __init__(self, chaos: 'Chaos' = None, parameter: type = Position):
        super().__init__((chaos, parameter))

    def process(self, operand: 'Container') -> 'Container':
        return operand.shuffle(*self._data)

class Swap(ContainerProcess):
    from operand_rational import Position

    def __init__(self, probability: 'Probability' = None, chaos: 'Chaos' = None, parameter: type = Position):
        super().__init__((probability, chaos, parameter))

    def process(self, operand: 'Container') -> 'Container':
        return operand.swap(*self._data)

class Reverse(ContainerProcess):
    def __init__(self, non_empty_measures_only: bool = True):
        super().__init__(non_empty_measures_only)

    def process(self, operand: 'Container') -> 'Container':
        return operand.reverse(self._data)

class Recur(ContainerProcess):
    from operand_rational import Duration

    def __init__(self, recursion: Callable = lambda d: d/2, parameter: type = Duration):
        super().__init__((recursion, parameter))

    def process(self, operand: 'Container') -> 'Container':
        return operand.recur(*self._data)

class Rotate(ContainerProcess):
    from operand_rational import Position

    def __init__(self, offset: int = 1, parameter: type = Position):
        super().__init__((offset, parameter))

    def process(self, operand: 'Container') -> 'Container':
        return operand.rotate(*self._data)

class Erase(ContainerProcess):
    """
    Erase() clears all the Container items and the same ones on the root container.
    """
    def process(self, operand: 'Container') -> 'Container':
        return operand.erase(*self._data)

class Upper(ContainerProcess):
    def __init__(self, level: int = None):
        super().__init__(level)

    def process(self, operand: 'Container') -> 'Container':
        return operand.upper(self._data)


if TYPE_CHECKING:
    from operand_container import Composition
    from operand_container import Clip

class ClipProcess(Process):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return self.process(operand)
        return super().__rrshift__(operand)

    def process(self, operand: o.T) -> o.T:
        return operand

class Fit(ClipProcess):
    from operand_rational import Length

    def __init__(self, length: 'Length' = None):
        super().__init__(length)

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.fit(self._data)

class Link(ClipProcess):
    def __init__(self, non_empty_measures_only: bool = True):
        super().__init__(non_empty_measures_only)

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.link(self._data)

class Stack(ClipProcess):
    def __init__(self, non_empty_measures_only: bool = True):
        super().__init__(non_empty_measures_only)

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.stack(self._data)

class Decompose(ClipProcess):
    def process(self, operand: 'Clip') -> 'Clip':
        return operand.decompose()

if TYPE_CHECKING:
    from operand_generic import Arpeggio
    from operand_element import Element
    
class Arpeggiate(ClipProcess):
    def process(self, operand: 'Clip') -> 'Clip':
        return operand.arpeggiate(self._data)

class Stepper(ClipProcess):

    def __init__(self, pattern: str = "1... 1... 1... 1...", note: Any = None):
        super().__init__((pattern, note))

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.stepper(*self._data)

class Automate(ClipProcess):

    def __init__(self, values: list[int] = [100, 70, 30, 100],
                 pattern: str = "1... 1... 1... 1...", automation: Any = "Pan", interpolate: bool = True):
        super().__init__((values, pattern, automation, interpolate))

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.automate(*self._data)

class Interpolate(ClipProcess):
    def process(self, operand: 'Clip') -> 'Clip':
        return operand.interpolate()

class Tie(ClipProcess):
    def __init__(self, tied: bool = True):
        super().__init__(tied)

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.tie(self._data)

class Slur(ClipProcess):
    def __init__(self, gate: float = 1.05):
        super().__init__(gate)

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.slur(self._data)

class Smooth(ClipProcess):
    def process(self, operand: 'Clip') -> 'Clip':
        return operand.smooth()

class Flip(ClipProcess):
    def process(self, operand: 'Clip') -> 'Clip':
        return operand.flip()

class Snap(ClipProcess):
    def __init__(self, up: bool = False):
        super().__init__(up)

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.snap(self._data)

if TYPE_CHECKING:
    from operand_rational import Length

class Extend(ClipProcess):
    def __init__(self, length: 'Length' = None):
        super().__init__( length )

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.extend(self._data)

class Trim(ClipProcess):
    def __init__(self, length: 'Length' = None):
        super().__init__( length )

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.trim(self._data)

class Cut(ClipProcess):
    from operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__((start, finish))

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.cut(*self._data)

class Select(ClipProcess):
    from operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__((start, finish))

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.select(*self._data)

class Monofy(ClipProcess):
    def process(self, operand: 'Clip') -> 'Clip':
        return operand.monofy()

class Fill(ClipProcess):
    def process(self, operand: 'Clip') -> 'Clip':
        return operand.fill()

class Plot(ClipProcess):
    def __init__(self, block: bool = True, pause: float = 0.0, iterations: int = 0,
                 n_button: Optional[Callable[['Clip'], 'Clip']] = None,
                 c_button: Optional[Callable[['Clip'], 'Composition']] = None,
                 e_button: Optional[Callable[['Clip'], Any]] = None):
        super().__init__((block, pause, iterations, n_button, c_button, e_button))

    def process(self, operand: 'Clip') -> 'Clip':
        return operand.plot(*self._data)




class Getter(Data):
    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case str():
                return self._data == other
            case _:
                return super().__eq__(other)

class Len(Getter):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.len()
        return ol.Null()

class Start(Getter):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.start()
        return ol.Null()

class End(Getter):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.finish()
        return ol.Null()

class Name(Getter):
    def __rrshift__(self, operand: any) -> str:
        if isinstance(operand, o.Operand):
            return operand.__class__.__name__
        return ol.Null()
