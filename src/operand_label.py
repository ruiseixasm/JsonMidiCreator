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
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Tuple, Optional, Any, Generic
from typing import Self

from fractions import Fraction
import json

# Json Midi Creator Libraries
import creator as c
import operand as o


class Label(o.Operand):
    """`Label`

    Label is an `Operand` that contains no parameters and it's intended to be processed just based in its name, as label.

    Parameters
    ----------
    None : Labels don't have any parameters.
    """
    def __eq__(self, other: 'Label') -> bool:
        import operand_data as od
        if type(self) == type(other):
            return True
        if isinstance(other, od.Conditional):
            return other == self
        return False
    
    def __bool__(self) -> bool:  # For Python 3
        return True

    def __nonzero__(self) -> bool:  # For Python 2
        return self.__bool__()
    
    def __not__(self) -> bool:
        return False
    
    def __mod__(self, operand: o.T) -> o.T:
        return operand
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        return self
    
    # By default a Label has no copies as it caries no data
    def copy(self, *parameters) -> Self:
        return self


class Null(Label):
    """`Label -> Null`

    A `Null` label is an `Operand` that is processed as no data and as no effect when operated with other `Operands`.
    It is returned by a `Frame` as a no `Operand` return.

    Parameters
    ----------
    None : `Null` has no parameters.
    """
    def __bool__(self) -> bool:  # For Python 3
        return False

    def __not__(self) -> bool:
        return True
    
    def __eq__(self, other: 'Label') -> bool:
        if other is None:
            return True
        if other == False:
            return True
        if other == True:
            return False
        return super().__eq__(other)
    
    def __mod__(self, operand: o.T) -> Self:
        return self


class NonNull(Label):
    """`Label -> NonNull`

    A `NonNull` label is an `Operand` that is processed as existent data and validates any effect when operated with other `Operands`.
    It is returned by a `Frame` as a validates or passed `Operand`.

    Parameters
    ----------
    None : `NonNull` has no parameters.
    """
    pass

    
class Dummy(Label):
    """`Label -> Dummy`

    A `Dummy` label is an `Operand` used just to mimic operations with other `Operands`.

    Parameters
    ----------
    None : `Dummy` has no parameters.
    """
    pass

