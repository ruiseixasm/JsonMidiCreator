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
from typing import Union, TYPE_CHECKING, Type, Callable, List, Tuple, Optional, Any, Generic
try:
    from typing import Self
except ImportError:
    from typing import TypeVar
    Self = TypeVar('Self', bound='Label')  # Define Self manually

from fractions import Fraction
import json

# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_frame as of


class Label(o.Operand):
    # By default a Label has no copies as it caries no data
    def copy(self, *parameters) -> Self:
        return self

    def __eq__(self, other: 'Label') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if type(self) == type(other) or type(other) == o.Operand or not other:
            return True
        return False
    
    def __bool__(self) -> bool:  # For Python 3
        return False

    def __nonzero__(self) -> bool:  # For Python 2
        return self.__bool__()
    
    def __not__(self) -> bool:
        return True
    
    def __add__(self, operand: any) -> 'Label':
        return self
    
    def __sub__(self, operand: any) -> 'Label':
        return self
    
    def __mul__(self, operand: any) -> 'Label':
        return self
    
    def __div__(self, operand: any) -> 'Label':
        return self
    
class Null(Label):
    pass
    
class Dummy(Label):
    pass

class MidiValue(Label):
    pass

