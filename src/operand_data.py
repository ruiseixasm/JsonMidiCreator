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
from operand import Operand
import operand_staff as os
import operand_unit as ou
import operand_frame as of
import operand_label as ol
import operand_time as ot


class Data(Operand):
    def __init__(self, data = None):
        self._data = data

    def __mod__(self, operand: Operand):
        match operand:
            case of.Frame():                return self % (operand % Operand())
            case ol.Null() | None:          return ol.Null()
            case _:                         return self._data

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
        return self.__class__(self._data)

    def __lshift__(self, operand: Operand) -> 'Data':
        match operand:
            case Data():            self._data = operand % Operand()
            case _:                 self._data = operand
        return self

class OperandData(Data):
    def __init__(self, operand: Operand = None):
        super().__init__(operand)

class ListScale(Data):
    def __init__(self, list_scale: list[int] = None):
        super().__init__( os.global_staff % ou.Scale() % list() if list_scale is None else list_scale )

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ou.Tonic():
                tonic_note = operand % int()
                transposed_scale = [0] * 12
                self_scale = self._data
                for key_i in range(12):
                    transposed_scale[(tonic_note + key_i) % 12] = self_scale[key_i]
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
        super().__init__( os.global_staff % self % list() if device_list is None else device_list )

class PlayList(Data):
    def __init__(self):
        super().__init__([])

    def getPlayList(self):
        return self._data

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand) -> Operand:
        import operand_container as oc
        import operand_element as oe
        match operand:
            case oc.Sequence() | oe.Element():
                self._data.extend(operand.getPlayList())
        return self

class Save(Data):
    def __init__(self, file_name: str = "_jsonMidiCreator.json"):
        super().__init__(file_name)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: Operand) -> Operand:
        c.saveJsonMidiCreator(operand.getSerialization(), self % str())
        return operand

class Load(Data):
    def __init__(self, file_name: str = "_jsonMidiCreator.json"):
        super().__init__(file_name)

class Export(Data):
    def __init__(self, file_name: str = "_jsonMidiPlayer.json"):
        super().__init__(file_name)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: Operand) -> Operand:
        c.saveJsonMidiPlay(operand.getPlayList(), self % str())
        return operand

class Import(Data):
    def __init__(self, file_name: str = "_jsonMidiPlayer.json"):
        super().__init__(file_name)
        self._others_playlist: list = []

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case list():        return c.loadJsonMidiPlay(self._data)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __rshift__(self, operand: Operand) -> 'Operand':
        match operand:
            case ou.Play():
                play_list = c.loadJsonMidiPlay(self._data)
                c.jsonMidiPlay(self._others_playlist + play_list, operand % int())
                return self
            case _: return operand.__rrshift__(self)

    def __rrshift__(self, operand: Operand) -> Operand:
        match operand:
            case Import():
                self._others_playlist.extend(operand % list())
                return self
        return self

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
    def __init__(self, compare: Operand = None):
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
