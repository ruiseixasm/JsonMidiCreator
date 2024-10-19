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
import json
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_frame as of


class Label(o.Operand):
    pass

class Null(Label):
    pass
    
class Dummy(Label):
    pass

class MidiValue(Label):
    pass

class MSB(MidiValue):
    """
    MSB() represents the Most Significant Byte.
    """
    pass

class LSB(MidiValue):
    """
    LSB() represents the Least Significant Byte.
    """
    pass

class Copy(Label):
    """
    Copy() does an total duplication of the Operand including its parts.
    """
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(operand, o.Operand):
            return operand.copy()
        return operand

class Len(Label):
    pass

class Reverse(Label):
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.reverse()
        return operand

class Join(Label):
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.join()
        return operand

class Stack(Label):
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.stack()
        return operand

class First(Label):
    pass

class Last(Label):
    pass

class Start(Label):
    pass

class End(Label):
    pass

class Name(Label):
    pass
