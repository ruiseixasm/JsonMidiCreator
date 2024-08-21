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
import json
# Json Midi Creator Libraries
import creator as c
from operand import Operand
import operand_frame as of


class Label(Operand):
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        return self

class Null(Label):
    def __add__(self, operand: Operand) -> 'Operand':
        match operand:
            case Operand():     return operand.copy()
            case _:             return operand
        
    def __sub__(self, operand: Operand) -> 'Operand':
        return operand * (-1)
    
    def __mul__(self, operand: Operand) -> 'Operand':
        return operand * 0
    
    def __truediv__(self, operand: Operand) -> 'Operand':
        return operand * 0
    
class Dummy(Label):
    pass
