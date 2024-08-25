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
        >>> some_data = Data(Pitch(8191)) % o.Operand()
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
        return self % bool() == other_data % bool()
    
    def __lt__(self, other_data: 'Data') -> bool:
        return self % int() < other_data % int()
    
    def __gt__(self, other_data: 'Data') -> bool:
        return self % int() > other_data % int()
    
    def __le__(self, other_data: 'Data') -> bool:
        return not (self > other_data)
    
    def __ge__(self, other_data: 'Data') -> bool:
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

    def copy(self) -> 'Data':
        return self.__class__() << DataSource( self._data.copy() )

    def __lshift__(self, operand: o.Operand) -> 'Data':
        match operand:
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
            case DataSource():      self._data = operand % o.Operand()
            case o.Operand():
                self._data = self._data.copy()
            case list():
                many_operands: list = []
                for single_operand in self._data:
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
    of the given Operand without the normal processing.
    
    Parameters
    ----------
    first : o.Operand_like
        The Operand intended to be directly extracted or set
    """
    def __init__(self, operand: o.Operand = None):
        super().__init__( o.Operand() if operand is None else operand )

    def __mod__(self, operand: o.Operand):
        return self._data

class ListScale(Data):
    def __init__(self, list_scale: list[int] = None):
        super().__init__( os.global_staff % DataSource( ou.Scale() ) % list() if list_scale is None else list_scale )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, a ListScale has many extraction modes
        one type of extraction is its list() type of Parameter representing a scale
        but it's also possible to extract the same scale on other Tonic() key based on C.

        Examples
        --------
        >>> tonic_a_scale = ListScale([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]) % Tonic("A") % list()
        >>> print(tonic_a_scale)
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        """
        match operand:
            case DataSource():          return super().__mod__(operand)
            case ou.Tonic():
                tonic_note = operand % int()
                transposed_scale = [0] * 12
                self_scale = self._data
                for key_i in range(12):
                    transposed_scale[key_i] = self_scale[(tonic_note + key_i) % 12]
                return ListScale(transposed_scale)
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

class PlayList(Data):
    def __init__(self, play_list: list = None):
        super().__init__( [] if play_list is None else play_list )

    def getPlayList(self):
        return self._data

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand) -> o.Operand:
        return PlayList(operand.getPlayList() + self._data)

    def __add__(self, operand: o.Operand) -> 'PlayList':
        match operand:
            case list():        return PlayList( self._data + operand )
            case _:             return PlayList( self._data + operand.getPlayList() )

class Save(Data):
    def __init__(self, file_name: str = "_jsonMidiCreator.json"):
        super().__init__(file_name)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        c.saveJsonMidiCreator(operand.getSerialization(), self % str())
        return operand

class Load(Data):
    def __init__(self, file_name: str = "_jsonMidiCreator.json"):
        super().__init__(file_name)

class Export(Data):
    def __init__(self, file_name: str = "_jsonMidiPlayer.json"):
        super().__init__(file_name)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        c.saveJsonMidiPlay(operand.getPlayList(), self % str())
        return operand

class Import(Data):
    def __init__(self, file_name: str = "_jsonMidiPlayer.json"):
        loaded_list = c.loadJsonMidiPlay(file_name)
        super().__init__( PlayList(loaded_list) )

    def getPlayList(self):
        return self._data.getPlayList()

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> PlayList:
        return self._data + operand

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
