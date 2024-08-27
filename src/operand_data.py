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
import operand_names as on


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

    def getPlayList(self) -> dict:
        import operand_container as oc
        sequence_serialization = {
                "class": "Sequence",
                "parameters": {
                    "operands": [self._data]
                }
            }
        if Serialization.isSequence(self._data):
            sequence_serialization = self._data
        return oc.Sequence().loadSerialization( sequence_serialization ).getPlayList()

    def getSerialization(self) -> dict:
        return Serialization.copySerialization(self._data)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand) -> o.Operand:
        import operand_container as oc
        import operand_element as oe
        match operand:
            case ot.Position():
                start_position = Serialization.getStart(self._data)
                increase_position = operand - start_position
                return Serialization( Serialization.setStart(self._data, increase_position) )
            case Serialization() | oc.Sequence() | oe.Element():
                return Serialization( Serialization.addSequences(operand.getSerialization(), self._data) )
            case _:
                return Serialization.copySerialization(self._data)

    @staticmethod
    def addSequences(left_sequence: dict, right_sequence: dict) -> dict:
        if Serialization.isSequence(left_sequence) and Serialization.isSequence(right_sequence):
            added_sequence = Serialization.copySerialization(left_sequence)
            added_sequence["parameters"]["operands"] += right_sequence["parameters"]["operands"]
            return Serialization.copySerialization(added_sequence)
        if Serialization.isSequence(left_sequence):
            added_sequence = Serialization.copySerialization(left_sequence)
            added_sequence["parameters"]["operands"] += [ right_sequence ]
            return Serialization.copySerialization(added_sequence)
        if Serialization.isSequence(right_sequence):
            added_sequence = Serialization.copySerialization(left_sequence)
            added_sequence["parameters"]["operands"] = [ right_sequence ] + added_sequence["parameters"]["operands"]
            return Serialization.copySerialization(added_sequence)
        added_sequence = {
                "class": "Sequence",
                "parameters": {
                    "operands": [left_sequence, left_sequence]
                }
            }
        return Serialization.copySerialization(added_sequence)

    @staticmethod
    def isSequence(serialization: dict) -> bool:
        if isinstance(serialization, dict) and "class" in serialization and serialization["class"] == "Sequence":
            return True
        return False

    @staticmethod
    def getStart(serialization: any) -> any:
        min_position: ot.Position = None

        if isinstance(serialization, dict):
            for key, value in serialization.items():
                # Recursively copy each value
                if isinstance(value, dict) and "class" in value and "Position" in value["class"]:
                    # {
                    #     "class": "Position",
                    #     "parameters": {
                    #         "measure": 0.0,
                    #         "beat": 0.0,
                    #         "note_value": 0.0,
                    #         "step": 0.0
                    #     }
                    # }
                    value_position = ot.Position().loadSerialization(value) # It's a leaf value (no children, not a node)
                    if min_position is None or value_position < min_position:
                        min_position = value_position
                else:
                    # Recursively check nested structures
                    nested_min = Serialization.getStart(value)
                    if nested_min is not None and (min_position is None or nested_min < min_position):
                        min_position = nested_min

        elif isinstance(serialization, list):
            for element in serialization:
                nested_min = Serialization.getStart(element)
                if nested_min is not None and (min_position is None or nested_min < min_position):
                    min_position = nested_min

        return min_position     # Final exit point

    @staticmethod
    def setStart(serialization: any, increase_position: ot.Length) -> any:
        if isinstance(serialization, dict):
            # Create a new dictionary
            copy_dict = {}
            for key, value in serialization.items():
                # Recursively copy each value
                if isinstance(value, dict) and "class" in value and "Position" in value["class"]:
                    # {
                    #     "class": "Position",
                    #     "parameters": {
                    #         "measure": 0.0,
                    #         "beat": 0.0,
                    #         "note_value": 0.0,
                    #         "step": 0.0
                    #     }
                    # }
                    value_position = ot.Position().loadSerialization(value)
                    new_position = value_position + increase_position
                    new_position_dict = new_position.getSerialization()
                    value["parameters"] = new_position_dict["parameters"]

                copy_dict[key] = Serialization.setStart(value, increase_position)

            return copy_dict    # Final exit point
        
        elif isinstance(serialization, list):
            # Create a new list and recursively copy each element
            return [Serialization.setStart(element, increase_position) for element in serialization]
        else:
            # Base case: return the value directly if it's neither a list nor a dictionary
            return serialization

    @staticmethod
    def copySerialization(serialization: any) -> any:
        if isinstance(serialization, dict):
            # Create a new dictionary
            copy_dict = {}
            for key, value in serialization.items():
                # Recursively copy each value
                copy_dict[key] = Serialization.copySerialization(value)

            return copy_dict    # Final exit point
        
        elif isinstance(serialization, list):
            # Create a new list and recursively copy each element
            return [Serialization.copySerialization(element) for element in serialization]
        else:
            # Base case: return the value directly if it's neither a list nor a dictionary
            return serialization

    @staticmethod
    def deep_copy_dict(data):
        """
        Recursively creates a deep copy of a dictionary that may contain lists and other dictionaries.

        Args:
            data (dict): The dictionary to copy.

        Returns:
            dict: A deep copy of the original dictionary.
        """
        if isinstance(data, dict):
            # Create a new dictionary
            copy_dict = {}
            for key, value in data.items():
                # Recursively copy each value
                copy_dict[key] = Serialization.deep_copy_dict(value)
            return copy_dict
        elif isinstance(data, list):
            # Create a new list and recursively copy each element
            return [Serialization.deep_copy_dict(element) for element in data]
        else:
            # Base case: return the value directly if it's neither a list nor a dictionary
            return data

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

    def getPlayList(self) -> list:
        return PlayList.copyPlayList(self._data)

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
                    playlist_copy = PlayList.copyPlayList(self._data)
                    for midi_element in playlist_copy:
                        if "time_ms" in midi_element:
                            midi_element["time_ms"] = round(midi_element["time_ms"] + increase_position_ms, 3)
                return PlayList( playlist_copy )
            case _:
                return PlayList( operand.getPlayList() + PlayList.copyPlayList(self._data) )

    def __add__(self, operand: o.Operand) -> 'PlayList':
        match operand:
            case list():        return PlayList( PlayList.copyPlayList(self._data) + PlayList.copyPlayList(operand) )
            case o.Operand():   return PlayList( PlayList.copyPlayList(self._data) + PlayList.copyPlayList(operand.getPlayList()) )
            case _:             return PlayList( PlayList.copyPlayList(self._data) )

    @staticmethod
    def copyPlayList(play_list: list):
        copy_play_list = []
        for single_dict in play_list:
            copy_play_list.append(single_dict.copy())
        return copy_play_list

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
