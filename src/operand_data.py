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
        self._data = data

    def __mod__(self, operand: o.Operand):
        """
        The % symbol is used to extract a Parameter, because a Data has
        only one type of Parameters that's a generic type of Parameter
        it should be used in conjugation with Operand() to extract it.

        Examples
        --------
        >>> some_data = Data(Pitch(8191)) % Operand()
        >>> print(some_data)
        <operand_unit.Pitch object at 0x00000135E6437290>
        """
        match operand:
            case DataSource():              return self._data
            case of.Frame():                return self % (operand % o.Operand())
            case ol.Null() | None:          return ol.Null()
            case _:
                match self._data:
                    case o.Operand():
                        return self._data.copy()
                    case list():
                        many_operands: list = []
                        for single_operand in self._data:
                            match single_operand:
                                case o.Operand():
                                    many_operands.append(single_operand.copy())
                                case _:
                                    many_operands.append(single_operand)
                        return many_operands
                    case _: return self._data

    def __eq__(self, other_data: 'Data') -> bool:
        if type(self._data) == type(other_data % DataSource()):
            return self._data == other_data % DataSource()
        return False
    
    def __lt__(self, other_data: 'Data') -> bool:
        if type(self._data) != type(other_data % DataSource()):
            return False
        return self._data < other_data % DataSource()
    
    def __gt__(self, other_data: 'Data') -> bool:
        if type(self._data) != type(other_data % DataSource()):
            return False
        return self._data > other_data % DataSource()
    
    def __le__(self, other_data: 'Data') -> bool:
        if type(self._data) != type(other_data % DataSource()):
            return False
        return not (self > other_data)
    
    def __ge__(self, other_data: 'Data') -> bool:
        if type(self._data) != type(other_data % DataSource()):
            return False
        return not (self < other_data)

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "data": self._data
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "data" in serialization["parameters"]):

            self._data = serialization["parameters"]["data"]
        return self

    def __lshift__(self, operand: o.Operand) -> 'Data':
        match operand:
            case DataSource():      self._data = operand % o.Operand()
            case Data():
                operand_data = operand % DataSource( o.Operand() )
                match operand_data:
                    case o.Operand():
                        self._data = operand_data.copy()
                    case list():
                        many_operands: list = []
                        for single_operand in operand_data:
                            match single_operand:
                                case o.Operand():
                                    many_operands.append(single_operand.copy())
                                case _:
                                    many_operands.append(single_operand)
                        self._data = many_operands
                    case _:
                        self._data = operand_data
            case of.Frame():        self << (operand & self)
            case Load():
                self.loadSerialization(operand % DataSource())
            case o.Operand():
                self._data = self._data.copy()
            case list():
                many_operands: list = []
                for single_operand in operand:
                    match single_operand:
                        case o.Operand():
                            many_operands.append(single_operand.copy())
                        case _:
                            many_operands.append(single_operand)
                self._data = many_operands
            case _: self._data = operand
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
        super().__init__( o.Operand() if operand is None else operand )

    def __mod__(self, operand: o.Operand):
        """
        The % symbol will extract the data source value.

        Examples
        --------
        >>> data_source = DataSource( Position() )
        >>> print(data_source % Operand())
        <operand_time.Position object at 0x000001C4109E4F10>
        """
        return self._data

class DataScale(Data):
    def __init__(self, list_scale: list[int] = None):
        super().__init__( [] )  # By default there is no scale set

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, a DataScale has many extraction modes
        one type of extraction is its list() type of Parameter representing a scale
        but it's also possible to extract the same scale on other Tonic() key based on C.

        Examples
        --------
        >>> tonic_a_scale = DataScale([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]) % Tonic("A") % list()
        >>> print(tonic_a_scale)
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        """
        match operand:
            case DataSource():          return super().__mod__(operand)
            case bool():
                if isinstance(self._data, list) and len(self._data) == 12:
                    return True
                return False
            case list():
                if self % bool():       return self._data.copy()
                return []
            case str():                 return "Data"
            case ou.Tonic():
                transposed_scale = []
                if self % bool():
                    tonic_note = operand % int()
                    transposed_scale = [0] * 12
                    self_scale = self._data
                    for key_i in range(12):
                        transposed_scale[key_i] = self_scale[(tonic_note + key_i) % 12]
                return DataScale(transposed_scale)
            case ou.Mode():             return ou.Key("C") + self.transpose(operand % int() - 1)
            case ou.Transposition():    return ou.Key("C") + self.transpose(operand % int())
            case _:                     return super().__mod__(operand)

    def len(self) -> int:
        scale_len = 0
        self_scale = self._data
        for key in self_scale:
            scale_len += key
        return scale_len

    def transpose(self, interval: int = 1) -> int:
        self_scale = self._data
        chromatic_transposition = 0
        if interval > 0:
            while interval != 0:
                chromatic_transposition += 1
                if self_scale[chromatic_transposition % 12] == 1:
                    interval -= 1
        elif interval < 0:
            while interval != 0:
                chromatic_transposition -= 1
                if self_scale[chromatic_transposition % 12] == 1:
                    interval += 1
        return chromatic_transposition

class Device(Data):
    def __init__(self, device_list: list[str] = None):
        super().__init__( os.global_staff % DataSource( self ) % list() if device_list is None else device_list )

class Save(Data):
    def __init__(self, file_name: str = "json/_Save_jsonMidiCreator.json"):
        super().__init__(file_name)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        c.saveJsonMidiCreator(operand.getSerialization(), self % str())
        return operand

class Serialization(Data):
    def __init__(self, serialization: list = None):
        super().__init__( { } if serialization is None else serialization )

    def getStart(self, start: ot.Position = None, dictionary = None):
        if dictionary == None: dictionary = self._data
        if "parameters" in dictionary:
            if "position" in dictionary["parameters"]:
                if start is None or start > ot.Position().loadSerialization(dictionary["parameters"]["position"]):
                    return ot.Position().loadSerialization(dictionary["parameters"]["position"])
                return start
            if "operands" in dictionary["parameters"]:
                for operand_dictionary in dictionary["parameters"]["operands"]:
                    start = self.getStart(start, operand_dictionary)
        return start

    def setStart(self, increase_position: ot.Length, dictionary = None):
        if dictionary == None: dictionary = self._data
        if "parameters" in dictionary:
            if "position" in dictionary["parameters"]:
                operand_position = ot.Position().loadSerialization(dictionary["parameters"]["position"])
                new_operand_position = operand_position + increase_position
                return new_operand_position.getSerialization()
            if "operands" in dictionary["parameters"]:
                for operand_dictionary in dictionary["parameters"]["operands"]:
                    operand_dictionary["position"] = self.setStart(increase_position, operand_dictionary)
        return self

    def getSerialization(self):
        return self._data

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand) -> o.Operand:
        match operand:
            case ot.Position():
                start_position = self.getStart()
                increase_position = operand - start_position
                return self.setStart(increase_position)
            case _:
                self._data = operand.getSerialization()
                return self

class Load(Serialization):
    def __init__(self, file_name: str = "json/_Save_jsonMidiCreator.json"):
        super().__init__( c.loadJsonMidiCreator(file_name) )

class Export(Data):
    def __init__(self, file_name: str = "json/_Export_jsonMidiPlayer.json"):
        super().__init__(file_name)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        c.saveJsonMidiPlay(operand.getPlayList(), self % str())
        return operand

class PlayList(Data):
    def __init__(self, play_list: list = None):
        super().__init__( [] if play_list is None else play_list )

    def getPlayList(self):
        return self._data.copy()

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand) -> o.Operand:
        match operand:
            case ot.Position():
                if len(self._data) > 0:
                    input_position_ms: float = operand.getTime_ms()
                    starting_position_ms = self._data[0]["time_ms"]
                    for midi_element in self._data:
                        if "time_ms" in midi_element and midi_element["time_ms"] < starting_position_ms:
                            starting_position_ms = midi_element["time_ms"]
                    increase_position_ms = input_position_ms - starting_position_ms
                    for midi_element in self._data:
                        if "time_ms" in midi_element:
                            midi_element["time_ms"] = round(midi_element["time_ms"] + increase_position_ms, 3)
                return self
            case _:
                return PlayList( operand.getPlayList() + self._data.copy() )

    def __add__(self, operand: o.Operand) -> 'PlayList':
        match operand:
            case list():        return PlayList( self._data.copy() + operand )
            case o.Operand():   return PlayList( self._data.copy() + operand.getPlayList() )
            case _:             return PlayList( self._data.copy() )

class Import(PlayList):
    def __init__(self, file_name: str = "json/_Export_jsonMidiPlayer.json"):
        super().__init__( c.loadJsonMidiPlay(file_name) )

class Function(Data):
    pass

class Copy(Function):
    """
    Copy() does an total duplication of the Operand including its parts.
    """
    def __init__(self):
        super().__init__(None)

class Len(Function):
    def __init__(self):
        super().__init__(None)

class Sort(Function):
    def __init__(self, compare: o.Operand = None):
        super().__init__(compare)

class Reverse(Function):
    def __init__(self):
        super().__init__(None)

class First(Function):
    def __init__(self):
        super().__init__(None)

class Last(Function):
    def __init__(self):
        super().__init__(None)

class Start(Function):
    def __init__(self):
        super().__init__(None)

class End(Function):
    def __init__(self):
        super().__init__(None)
