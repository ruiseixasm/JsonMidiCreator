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
from operand import Operand
import operand_staff as os

class Data(Operand):
    def __init__(self, data = None):
        self._data = data

    def __mod__(self, operand: Operand):
        return self._data

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

class Export(Data):
    def __init__(self, file_name: str = "_jsonMidiPlayer.json"):
        super().__init__(file_name)
