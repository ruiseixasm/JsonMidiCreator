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
# Json Midi Creator Libraries
import creator as c
from operand import Operand
import operand_staff as os
import operand_unit as ou
import operand_frame as of
import operand_tag as ot


class Data(Operand):
    def __init__(self, data = None):
        self._data = data

    def __mod__(self, operand: Operand):
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case ot.Null() | None:  return ot.Null()
            case _:                 return self._data

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

# Read only class
class Device(Data):
    def __init__(self, device_list: list[str] = None):
        super().__init__(device_list)
        self._data = os.global_staff % self % list() if device_list is None else device_list

class Save(Data):
    def __init__(self, file_name: str = "_jsonMidiCreator.json"):
        super().__init__(file_name)

class Load(Data):
    def __init__(self, file_name: str = "_jsonMidiCreator.json"):
        super().__init__(file_name)

class Export(Data):
    def __init__(self, file_name: str = "_jsonMidiPlayer.json"):
        super().__init__(file_name)

class Import(Data):
    def __init__(self, file_name: str = "_jsonMidiPlayer.json"):
        super().__init__(file_name)
        self._others_playlist: list = []

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case list():        return c.loadJsonMidiPlay(self._data)
            case _:             return super().__mod__(operand)

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "data": self._data
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "data" in serialization):

            self._data = serialization["data"]
        return self
   
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
