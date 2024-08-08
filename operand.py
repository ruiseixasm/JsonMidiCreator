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
        return operand

    def getSerialization(self):
        return { 
            "class": self.__class__.__name__
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        return self
       
    def copy(self): # read only Operand doesn't have to be duplicated, it never changes
        return self
    
    def __lshift__(self, operand: 'Operand') -> 'Operand':
        return self

    def __rshift__(self, operand: 'Operand') -> 'Operand':
        return operand.__rrshift__(self)

    def __rrshift__(self, operand: 'Operand') -> 'Operand':
        return self

    def __add__(self, operand: 'Operand') -> 'Operand':
        return self

    def __sub__(self, operand: 'Operand') -> 'Operand':
        return self

    def __mul__(self, operand: 'Operand') -> 'Operand':
        return self
    
    def __truediv__(self, operand: 'Operand') -> 'Operand':
        return self
    
    def __floordiv__(self, operand: 'Operand') -> 'Operand':
        return self

    def __pow__(self, operand: 'Operand') -> 'Operand':
        return operand.__rpow__(self)
    
    def __rpow__(self, operand: 'Operand') -> 'Operand':
        return self
    
    def __and__(self, operand: 'Operand') -> 'Operand':
        return operand.__rand__(self)

    def __and__(self, operand: 'Operand') -> 'Operand':
        import operand_tag as ot
        return ot.Null()

    def __or__(self, operand: 'Operand') -> 'Operand':
        return operand.__ror__(self)

    def __ror__(self, operand: 'Operand') -> 'Operand':
        import operand_tag as ot
        return ot.Null()
