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


class Mask(Data):
    pass

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

class TrackName(Data):
    def __init__(self, *parameters):
        super().__init__("Track 1", *parameters)         # By default is "Track 1"


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

class Playlist(Data):
    def __init__(self, *parameters):
        super().__init__([])
        self._midi_track: ou.MidiTrack = ou.MidiTrack("Playlist 1")
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
                    case ou.MidiTrack():    return self._midi_track
                    case list():            return self._data
                    case _:                 return super().__mod__(operand)
            case ou.MidiTrack():    return self._midi_track.copy()
            case list():            return self.shallow_playlist_copy(self._data)
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
            case o.Operand():
                return self._data == other.getPlaylist()
        return super().__eq__(other)
    
    def getPlaylist(self, position = None, staff = None) -> list:
        return self.shallow_playlist_copy(self._data)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_container as oc
        import operand_element as oe
        match operand:
            case Playlist():
                self._data          = self.shallow_playlist_copy(operand._data)
                self._midi_track    << operand._midi_track
            case DataSource():
                match operand._data:
                    case ou.MidiTrack():
                        self._midi_track = operand._data
                    case list():
                        self._data = operand._data
                    case _:
                        super().__lshift__(operand)
            case oc.Part() | oc.Clip() | oe.Element() | Playlist():
                self._data = operand.getPlaylist()
            case ou.MidiTrack():
                self._midi_track    << operand
            case list():
                self._data = self.shallow_playlist_copy(operand)
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __rrshift__(self, operand: any) -> Self:
        import operand_rational as ra
        import operand_element as oe
        import operand_container as oc
        match operand:
            case oc.Clip() | oe.Element() | Playlist(): # TO BE REVIEWED !!
                operand_play_list: list[dict] = operand.getPlaylist()
                self_copy: Playlist = self.copy()
                if len(self_copy._data) > 0 and len(operand_play_list) > 0:
                    ending_position_ms: float = operand_play_list[0]["time_ms"]
                    for operand_dict in operand_play_list:
                        if "time_ms" in operand_dict and operand_dict["time_ms"] > ending_position_ms:
                            ending_position_ms = operand_dict["time_ms"]
                    # Where self_copy _data list is manipulated (pushed forward)
                    increase_position_ms: float = ending_position_ms
                    starting_position_ms = self_copy._data[0]["time_ms"]
                    for self_copy_dict in self_copy._data:
                        if "time_ms" in self_copy_dict and self_copy_dict["time_ms"] < starting_position_ms:
                            starting_position_ms = self_copy_dict["time_ms"]
                    increase_position_ms = ending_position_ms - starting_position_ms
                    for self_copy_dict in self_copy._data:
                        if "time_ms" in self_copy_dict:
                            self_copy_dict["time_ms"] = round(self_copy_dict["time_ms"] + increase_position_ms, 3)
                return self_copy << DataSource( operand_play_list + self_copy._data )

            case ra.Position():
                operand_play_list: list[dict] = operand.getPlaylist()
                new_start_position_ms: float = operand_play_list[0]["time_ms"]
                if len(self._data) > 0:
                    self_start_position_ms: float = self._data[0]["time_ms"]
                    for self_dict in self._data:
                        if "time_ms" in self_dict and self_dict["time_ms"] < self_start_position_ms:
                            self_start_position_ms = self_dict["time_ms"]
                    offset_position_ms: float = new_start_position_ms - self_start_position_ms
                    for self_dict in self._data:
                        if "time_ms" in self_dict:
                            self_dict["time_ms"] = round(self_dict["time_ms"] + offset_position_ms, 3)
                return self

            case ra.Length():
                operand_play_list: list[dict] = operand.getPlaylist()
                offset_position_ms: float = operand_play_list[0]["time_ms"]
                for self_dict in self._data:
                    if "time_ms" in self_dict:
                        self_dict["time_ms"] = round(self_dict["time_ms"] + offset_position_ms, 3)
                return self

            case _:
                return super().__rrshift__(operand)


    def __add__(self, operand: any) -> Self:
        import operand_rational as ra
        match operand:
            case ra.Length():
                playlist_copy = self.shallow_playlist_copy(self._data)
                increase_position_ms: float = operand.getMillis_float() # OUTDATED, NEEDS TO BE REVIEWED WITH LENGTH INSTEAD
                for self_dict in playlist_copy:
                    if "time_ms" in self_dict:
                        self_dict["time_ms"] = round(self_dict["time_ms"] + increase_position_ms, 3)
                return Playlist(self._midi_track) << DataSource( playlist_copy )
            case list():
                return Playlist(self._midi_track) << DataSource( self.shallow_playlist_copy(self._data) + self.shallow_playlist_copy(operand) )
            case o.Operand():
                return Playlist(self._midi_track) << DataSource( self.shallow_playlist_copy(self._data) + operand.getPlaylist() )
            case _:
                return Playlist(self)

    # Only the "time_ms" data matters to be copied because the rest wont change (faster)
    @staticmethod
    def shallow_playlist_copy(playlist: list[dict]) -> list[dict]:
        return [
            single_dict.copy()
                for single_dict in playlist
                if isinstance(single_dict, dict) and "time_ms" in single_dict
        ]


class Load(Serialization):
    def __init__(self, file_name: str = None):
        super().__init__()
        if isinstance(file_name, str):
            # No need to copy (fresh data)
            self._data = {} if file_name is None else c.loadJsonMidiCreator(file_name)
            self._data = o.Operand().loadSerialization(self._data)    # Must convert to an Operand

class Import(Playlist):
    def __init__(self, file_name: str = None):
        super().__init__()
        if isinstance(file_name, str):
            # No need to copy (fresh data)
            self._data = [] if file_name is None else c.loadJsonMidiPlay(file_name)


class Device(Data):
    def __init__(self, device_list: list[str] = None):
        import operand_generic as og
        super().__init__( device_list if isinstance(device_list, list) else [] )

class DataMany(Data):
    def __init__(self, *parameters):    # Allows multiple parameters
        super().__init__(list(parameters))

class Parameters(DataMany):
    pass

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
    pass
    
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
    def __init__(self, file_name: str = "json/_Save_jsonMidiCreator.json"):
        super().__init__(file_name)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            c.saveJsonMidiCreator(operand.getSerialization(), self._data)
            return operand
        return super().__rrshift__(operand)

class Export(Process):
    def __init__(self, file_name: str = "json/_Export_jsonMidiPlayer.json"):
        super().__init__(file_name)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            c.saveJsonMidiPlay(operand.getPlaylist(), self._data)
            return operand
        return super().__rrshift__(operand)

class MidiExport(Process):
    def __init__(self, file_name: str = "song.mid"):
        super().__init__(file_name)

    def __rrshift__(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            c.saveMidiFile(operand.getMidilist(), self._data)
            return operand
        return super().__rrshift__(operand)

if TYPE_CHECKING:
    from operand_generic import Pitch

class Sort(Process):

    # import operand_generic as og
    
    def __init__(self, parameter: type = 'Pitch'):
        super().__init__(parameter)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.sort(self._data)
        return super().__rrshift__(operand)

class Filter(Process):
    def __init__(self, mask: any = None, shallow_copy: bool = True):
        super().__init__((mask, shallow_copy))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.filter(*self._data)
        return super().__rrshift__(operand)

class Operate(Process):
    def __init__(self, operand: any = None, operator: str = "<<"):
        super().__init__((operand, operator))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.operate(*self._data)
        return super().__rrshift__(operand)

if TYPE_CHECKING:
    from operand_element import Note

class Transform(Process):
    def __init__(self, operand_type: type = 'Note'):
        super().__init__(operand_type)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.transform(self._data)
        return super().__rrshift__(operand)

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

class Erase(Process):
    """
    Erase() clears all the Container items and the same ones on the root container.
    """
    def __init__(self, *parameters):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.erase(*self._data)
        return super().__rrshift__(operand)

class Fit(Process):
    
    from operand_rational import Length

    def __init__(self, length: 'Length' = None):
        super().__init__(length)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.fit(self._data)
        return super().__rrshift__(operand)

if TYPE_CHECKING:
    from operand_container import Clip

class Link(Process):
    def __init__(self, non_empty_measures_only: bool = True):
        super().__init__(non_empty_measures_only)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.link(self._data)
        return super().__rrshift__(operand)

class Stack(Process):
    def __init__(self, non_empty_measures_only: bool = True):
        super().__init__(non_empty_measures_only)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.stack(self._data)
        return super().__rrshift__(operand)

class Decompose(Process):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.decompose()
        return super().__rrshift__(operand)

if TYPE_CHECKING:
    from operand_generic import Arpeggio

class Arpeggiate(Process):
    
    def __init__(self, parameters: any = None):
        super().__init__(parameters)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.arpeggiate(self._data)
        return super().__rrshift__(operand)

class Tie(Process):
    def __init__(self, tied: bool = True):
        super().__init__(tied)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.tie(self._data)
        return super().__rrshift__(operand)

class Slur(Process):
    def __init__(self, gate: float = 1.05):
        super().__init__(gate)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.slur(self._data)
        return super().__rrshift__(operand)

class Smooth(Process):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.smooth()
        return super().__rrshift__(operand)

class Play(Process):
    """
    Play() allows to send a given Element to the Player directly without the need of Exporting to the respective .json Player file.
    
    Parameters
    ----------
    first : integer_like
        By default it's configured without any verbose, set to 1 or True to enable verbose
    """
    def __init__(self, verbose: bool = False):
        super().__init__(1 if verbose else 0)

    def __rrshift__(self, operand: o.T) -> o.T:
        match operand:
            case o.Operand():
                c.jsonMidiPlay(operand.getPlaylist(), False if self._data == 0 else True )
                return operand
            case _:
                return super().__rrshift__(operand)

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

if TYPE_CHECKING:
    from operand_chaos import Chaos
    from operand_rational import Probability

class Shuffle(Process):
    
    from operand_rational import Position

    def __init__(self, chaos: 'Chaos' = None, parameter: type = Position):
        super().__init__((chaos, parameter))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.shuffle(*self._data)
        return super().__rrshift__(operand)

class Swap(Process):
    
    from operand_rational import Position

    def __init__(self, probability: 'Probability' = None, chaos: 'Chaos' = None, parameter: type = Position):
        super().__init__((probability, chaos, parameter))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.swap(*self._data)
        return super().__rrshift__(operand)

class Reverse(Process):
    def __init__(self, non_empty_measures_only: bool = True):
        super().__init__(non_empty_measures_only)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.reverse(self._data)
        return super().__rrshift__(operand)

class Recur(Process):
    
    from operand_rational import Duration

    def __init__(self, recursion: Callable = lambda d: d/2, parameter: type = Duration):
        super().__init__((recursion, parameter))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.recur(*self._data)
        return super().__rrshift__(operand)

class Rotate(Process):
    
    from operand_rational import Position

    def __init__(self, offset: int = 1, parameter: type = Position):
        super().__init__((offset, parameter))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.rotate(*self._data)
        return super().__rrshift__(operand)

class Flip(Process):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.flip()
        return super().__rrshift__(operand)

class Snap(Process):
    def __init__(self, up: bool = False):
        super().__init__(up)

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.snap(self._data)
        return super().__rrshift__(operand)

if TYPE_CHECKING:
    from operand_rational import Length

class Extend(Process):
    def __init__(self, length: 'Length' = None):
        super().__init__( length )
        
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.extend(self._data)
        return super().__rrshift__(operand)

class Trim(Process):
    def __init__(self, length: 'Length' = None):
        super().__init__( length )
        
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.trim(self._data)
        return super().__rrshift__(operand)

class Cut(Process):
    from operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__((start, finish))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.cut(*self._data)
        return super().__rrshift__(operand)

class Select(Process):
    from operand_rational import Position

    def __init__(self, start: Position = None, finish: Position = None):
        super().__init__((start, finish))

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.select(*self._data)
        return super().__rrshift__(operand)

class Monofy(Process):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.monofy()
        return super().__rrshift__(operand)

class Fill(Process):
    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        if isinstance(operand, oc.Clip):
            return operand.fill()
        return super().__rrshift__(operand)

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
