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
from typing import Union
from fractions import Fraction
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_staff as os
import operand_unit as ou
import operand_frame as of
import operand_label as ol
import operand_time as ot


class Data(o.Operand):

    def __init__(self, data = None):
        super().__init__()
        self._data = data
        # self._data = self.deep_copy(data)

    # ERROR ON RECURSIVE COPY DUE TO AMBIGUOUS OPERAND COPY WITH DATA COPY
    # def __init__(self, *parameters):
    #     super().__init__()
    #     self._data = None
    #     if len(parameters) > 0:
    #         self << parameters

    def __mod__(self, operand: any) -> any:
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
                match operand % o.Operand():
                    case of.Frame():                return self % DataSource( operand % o.Operand() )
                    case Data():                    return self
                    case ol.Null() | None:          return ol.Null()
                    case _:                         return self._data
            case of.Frame():                return self % (operand % o.Operand())
            case Data():                    return self.copy()
            case _:                         return self.deep_copy(self._data)
            
    def __eq__(self, other_data: o.Operand) -> bool:
        other_data = self & other_data    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other_data, Data):
            return self._data == other_data._data
        if other_data.__class__ == o.Operand:
            return True
        return False
    
    def __lt__(self, other_data: o.Operand) -> bool:
        other_data = self & other_data    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other_data, Data):
            return self._data < other_data._data
        return False
    
    def __gt__(self, other_data: o.Operand) -> bool:
        other_data = self & other_data    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other_data, Data):
            return self._data > other_data._data
        return False
    
    def __le__(self, other_data: o.Operand) -> bool:
        return self == other_data or self < other_data
    
    def __ge__(self, other_data: o.Operand) -> bool:
        return self == other_data or self > other_data

    def getSerialization(self) -> dict:
        data_serialization = super().getSerialization()
        data_serialization["parameters"]["data"] = self._data
        if isinstance(self._data, o.Operand):
            data_serialization["parameters"]["data"] = self._data.getSerialization()
        return data_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Data':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "data" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._data = serialization["parameters"]["data"]
            if isinstance(self._data, dict) and "class" in self._data and "parameters" in self._data:
                self._data      = o.Operand().loadSerialization(self._data)
        return self

    def __lshift__(self, operand: o.Operand) -> 'Data':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            # Data doesn't load serialization, just processed data!!
            case Serialization():
                self.loadSerialization(operand % DataSource( dict() ))
            case DataSource():
                self._data = operand % o.Operand()
            case Data():
                super().__lshift__(operand)
                self._data = self.deep_copy(operand._data)
            # case tuple():
            #     for single_operand in operand:
            #         self << single_operand
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
    def __init__(self, operand: o.Operand = None):
        super().__init__()
        self._data = o.Operand() if operand is None else operand

    def __mod__(self, operand: o.Operand):
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
        return self._data
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Data':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(operand, tuple) and isinstance(self._data, o.Operand):
            for single_operand in operand:
                self << single_operand
        else:
            super().__lshift__(operand)
        return self

    # def copy(self, *parameters) -> 'DataSource':
    #     ...

    # # STILL NEEDED BECAUSE DataSource is DataSource before Data!!!!
    # # CAN'T USE << SELF!!!
    # # # NEEDS TO REMOVE THIS METHOD
    # def copy(self, *parameters) -> 'DataSource':
    #     self_copy = self.__class__()
    #     self_data = self._data
    #     match self_data:
    #         case o.Operand():
    #             self_copy._data = self_data.copy()
    #         case list():
    #             many_operands: list = []
    #             for single_operand in self_data:
    #                 match single_operand:
    #                     case o.Operand():
    #                         many_operands.append(single_operand.copy())
    #                     case _:
    #                         many_operands.append(single_operand)
    #             self_copy._data = many_operands
    #         case _:
    #             self_copy._data = self_data
    #     # COPY THE SELF OPERANDS RECURSIVELY
    #     if self._next_operand is not None:
    #         self_copy._next_operand = self._next_operand.copy()
    #     return self_copy << parameters

class Parameters(Data):
    def __init__(self, *parameters):    # Allows multiple parameters
        super().__init__()
        # self._data = parameters # Tuple
        self._data = self.deep_copy(parameters) # Tuple

class Reporters(Data):
    def __init__(self, *parameters):    # Allows multiple parameters
        super().__init__()
        # self._data = parameters # Tuple
        self._data = self.deep_copy(parameters) # Tuple

class SideEffects(Data):
    def __init__(self, operand: o.Operand):
        super().__init__(operand)

class LeftShift(SideEffects):
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(self._data, o.Operand):
            self._data << operand
            return operand
        else:
            return super().__rrshift__(operand)

class RightShift(SideEffects):
    # CHAINABLE OPERATIONS
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(self._data, o.Operand):
            operand >> self._data
            return operand
        else:
            return super().__rrshift__(operand)

class Serialization(Data):
    def __init__(self, serialization: dict | o.Operand = None):
        super().__init__()
        if isinstance(serialization, o.Operand):
            self._data = serialization.copy()
        elif isinstance(serialization, dict) and "class" in serialization and "parameters" in serialization:
            self._data = o.Operand().loadSerialization(serialization)
        else:
            self._data = ol.Null()

    def __mod__(self, operand: any) -> any:
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
        match operand:
            case o.Operand():
                return self._data
            case dict():
                if isinstance(self._data, o.Operand):
                    return self._data.getSerialization()
                if isinstance(self._data, dict):
                    return self.deep_copy_dict(self._data)
                return dict()
            case _:
                return self._data % operand

    def __eq__(self, other_operand: any) -> bool:
        other_operand = self & other_operand    # Processes the tailed self operands or the Frame operand if any exists
        if self._data is None:
            if other_operand is None:
                return True
            return False
        match other_operand:
            case dict():
                return self._data.getSerialization() == other_operand
            case o.Operand():
                return self._data.getSerialization() == other_operand.getSerialization()
        return super().__eq__(other_operand)
    
    def getPlaylist(self, position: ot.Position = None) -> dict:
        return self._data.getPlaylist(position)

    def getSerialization(self) -> dict:
        if self._data is None:
            return {}
        return self._data.getSerialization()

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        self._data.loadSerialization(serialization)
        return self
        
    # # NEEDS TO REMOVE THIS METHOD
    # def copy(self, *parameters):
    #     self_copy: Data = self.__class__(self._data.copy()).loadSerialization( self.getSerialization() ) << parameters
    #     # COPY THE SELF OPERANDS RECURSIVELY
    #     if self._next_operand is not None:
    #         self_copy._next_operand = self._next_operand.copy()
    #     return self_copy

    def __lshift__(self, operand: any) -> 'o.Operand':
        if isinstance(operand, o.Operand):
            self._data = operand.copy()
        elif isinstance(operand, dict) and "class" in operand and "parameters" in operand:
            self._data = o.Operand().loadSerialization(operand)
        return self

    def __rrshift__(self, operand: any) -> o.Operand:
        if not isinstance(self._data, ol.Null) and isinstance(operand, o.Operand) and isinstance(self._data, o.Operand):
            return operand >> self._data
        else:
            return super().__rrshift__(operand)

    def __add__(self, operand: 'o.Operand') -> 'o.Operand':
        return self._data + operand

    def __sub__(self, operand: o.Operand) -> 'o.Operand':
        return self._data - operand

    def __mul__(self, operand: o.Operand) -> 'o.Operand':
        return self._data * operand

    def __truediv__(self, operand: o.Operand) -> 'o.Operand':
        return self._data / operand

    def __floordiv__(self, length: ot.Length) -> 'o.Operand':
        return self._data // length

class Playlist(Data):
    def __init__(self, *parameters):
        super().__init__([])
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
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
        return self._data

    def __eq__(self, other_operand: any) -> bool:
        other_operand = self & other_operand    # Processes the tailed self operands or the Frame operand if any exists
        if self._data is None:
            if other_operand is None:
                return True
            return False
        match other_operand:
            case list():
                return self._data == other_operand
            case o.Operand():
                return self._data == other_operand.getPlaylist()
        return super().__eq__(other_operand)
    
    def getPlaylist(self) -> list:
        return Playlist.copy_play_list(self._data)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Playlist':
        import operand_container as oc
        import operand_element as oe
        match operand:
            case oc.Sequence() | oe.Element() | Playlist():
                self._data = operand.getPlaylist()
            case list():
                self._data = Playlist.copy_play_list(operand)
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __rrshift__(self, operand) -> 'Playlist':
        import operand_container as oc
        import operand_element as oe
        if isinstance(self._data, list) and len(self._data) > 0 and isinstance(operand, (oc.Sequence, oe.Element, Playlist, ot.Position, ot.Length)):
            operand_play_list = operand.getPlaylist()
            ending_position_ms = operand_play_list[0]["time_ms"]
            for midi_element in operand_play_list:
                if "time_ms" in midi_element and midi_element["time_ms"] > ending_position_ms:
                    ending_position_ms = midi_element["time_ms"]
            increase_position_ms = ending_position_ms
            if not isinstance(operand, ot.Length):
                starting_position_ms = self._data[0]["time_ms"]
                for midi_element in self._data:
                    if "time_ms" in midi_element and midi_element["time_ms"] < starting_position_ms:
                        starting_position_ms = midi_element["time_ms"]
                increase_position_ms = ending_position_ms - starting_position_ms
            for midi_element in self._data:
                if "time_ms" in midi_element:
                    midi_element["time_ms"] = round(midi_element["time_ms"] + increase_position_ms, 3)
            return self.copy()
        if isinstance(operand, (oc.Sequence, oe.Element, Playlist)):
            return operand + self
        else:
            return super().__rrshift__(operand)

    def __add__(self, operand: o.Operand) -> 'Playlist':
        match operand:
            case ot.Length():
                playlist_copy = Playlist.copy_play_list(self._data)
                increase_position_ms: float = operand.getTime_ms()
                for midi_element in playlist_copy:
                    if "time_ms" in midi_element:
                        midi_element["time_ms"] = round(midi_element["time_ms"] + increase_position_ms, 3)
                return Playlist( playlist_copy )
            case list():        return Playlist( Playlist.copy_play_list(self._data) + Playlist.copy_play_list(operand) )
            case o.Operand():   return Playlist( Playlist.copy_play_list(self._data) + Playlist.copy_play_list(operand.getPlaylist()) )
            case _:             return Playlist( Playlist.copy_play_list(self._data) )

    @staticmethod
    def copy_play_list(play_list: list[dict]) -> list[dict]:
        copy_play_list = []
        for single_dict in play_list:
            copy_play_list.append(single_dict.copy())
        return copy_play_list

class Load(Serialization):
    def __init__(self, file_name: str = None):
        match file_name:
            case str():
                super().__init__( c.loadJsonMidiCreator(file_name) )
            case _:
                super().__init__()

class Import(Playlist):
    def __init__(self, file_name: str = None):
        super().__init__( [] if file_name is None else c.loadJsonMidiPlay(file_name) )

class DataCopy(Data):
    def __init__(self, data: any = None):
        super().__init__()
        self._data = data
        if isinstance(data, (o.Operand, list)):
            self._data = data.copy()

    def __mod__(self, operand: any) -> any:
        match operand:
            case DataSource():
                return super().__mod__(operand)
            case of.Frame():
                return self % (operand % o.Operand())
            case _:
                if isinstance(self._data, (o.Operand, list)):
                    return self._data.copy()
                return self._data

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> 'DataCopy':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case DataSource():
                self._data = operand % o.Operand()
            case DataCopy():
                super().__lshift__(operand)
                if isinstance(operand._data, (o.Operand, list)):
                    self._data = operand._data.copy()
                else:
                    self._data = operand._data
            case Serialization():
                self.loadSerialization(operand % DataSource( dict() ))
            case o.Operand() | list():
                self._data = operand.copy()
            case _:
                self._data = operand
        return self

class Result(DataCopy):
    pass

