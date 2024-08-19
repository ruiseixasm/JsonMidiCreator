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

class Operand:
    def __mod__(self, operand: 'Operand') -> 'Operand':
        import operand_tag as ot
        match operand:
            case ot.Null() | None:  return ot.Null()
            case _:                 return self

    def getSerialization(self):
        return { 
            "class": self.__class__.__name__
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        return self
       
    def copy(self):
        return self.__class__() << self
    
    def __lshift__(self, operand: 'Operand') -> 'Operand':
        return self

    # self is the pusher
    def __rshift__(self, operand: 'Operand') -> 'Operand':
        return operand.__rrshift__(self)

    # operand is the pusher
    def __rrshift__(self, operand: 'Operand') -> 'Operand':
        return self

    def __add__(self, operand: 'Operand') -> 'Operand':
        return self.copy()

    def __sub__(self, operand: 'Operand') -> 'Operand':
        return self.copy()

    def __mul__(self, operand: 'Operand') -> 'Operand':
        return self.copy()
    
    def __truediv__(self, operand: 'Operand') -> 'Operand':
        return self.copy()
    
    def __floordiv__(self, operand: 'Operand') -> 'Operand':
        return self.copy()

    def __pow__(self, operand: 'Operand') -> 'Operand':
        return self
    
    def __and__(self, operand: 'Operand') -> 'Operand':
        return self

    def __or__(self, operand: 'Operand') -> 'Operand':
        return self
