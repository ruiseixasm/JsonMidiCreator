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
import enum
import math
# Json Midi Creator Libraries
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_frame as of


class Tamer(o.Operand):
    """`Tamer`

    Because `Chaos` returns numbers that fit no specific criteria, `Tamer` makes sure a criteria is
    met with validation or manipulation dependant of the tamer.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._next_operand: Tamer = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, number: int | float | Fraction) -> tuple[int | float | Fraction, bool]:
        if self._next_operand is not None:
            number, validation = self._next_operand.tame(number)
            if not validation:
                return number, False    # Breaks the chain
        return number, True

    # CHAINABLE OPERATIONS

    def __pow__(self, tamer: 'Tamer') -> Self:
        match tamer:
            case Tamer():       self._next_operand = tamer
            case _:             self._next_operand = None
        return self

class Validator(Tamer):
    """`Tamer -> Validator`

    A `Validator` is a read-only `Tamer` that just verifies that the submitted number conforms.
    """
    pass

class Stepwise(Validator):
    """`Tamer -> Validator -> Stepwise`

    This `Validator` checks if the successive numbers have a distance less or equal to 0 to the previous one.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._last_number: int | float | Fraction = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def tame(self, number: int | float | Fraction) -> tuple[int | float | Fraction, bool]:
        number, validation = super().tame(number)
        if validation:
            if self._last_number is None:
                self._last_number = number
            else:
                if abs(number - self._last_number) > 1:
                    return number, False    # Breaks the chain
        return number, validation


class Manipulator(Tamer):
    """`Tamer -> Manipulator`

    A `Manipulator` is a read-write `Tamer` that beside verifying a submitted number it's also
    able to manipulate that number in order to conform.
    """
    pass
