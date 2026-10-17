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
from . import creator as c
from . import operand as o

from . import operand_label as ol
from . import operand_data as od
from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_generic as og
from . import operand_element as oe
from . import operand_container as oc
from . import operand_frame as of
from . import operand_chaos as ch
from . import operand_tamer as ot

if TYPE_CHECKING:
    from operand_element import Element
    from operand_container import Clip


class Action(o.Operand):
    """`Action`

    `Action` is intended to manipulate unmasked `Elements` in a `Clip` based on a given named action.
    The `action` method always returns the exact same inputted `Clip`.
    Contrary to a `Transformation`, an `Action` can be framed because it targets the Clip elements.
    """
    def act(self, clip: 'Clip') -> 'Clip':
        for unmasked_element in clip.elements_unmasked():
            self._single_act(unmasked_element)
        return clip._sort_items()


    def _single_act(self, element: 'Element') -> 'Element':
        return element


    



class Delete(Action):
    """`Action -> Delete`

    Deletes all the unmasked items in the targeted `Container` or elements in it if a `Clip`.

    Args:
        None
    """
    def _single_act(self, element: 'Element') -> 'Element':
        if element.is_owned():
            element._owner_clip._delete_item(element, True)
        return element



class RepeatedAction(Action):
    """`Action -> RepeatedAction`

    `Action` is intended to manipulate unmasked `Elements` in a `Clip` based on a given named action.
    The `action` method always returns the exact same inputted `Clip`.
    Contrary to a `Transformation`, an `Action` can be framed because it targets the Clip elements.
    """
    def __init__(self, *parameters):
        self._amount: int = 1
        super().__init__(*parameters)


    def unit(self, number: int = None) -> Self:
        return self << od.Pipe( number )


    def __neg__(self):
        self._amount *= -1
        return self


    def __mod__(self, operand: o.T) -> o.T:
        from . import operand_rational as ra
        match operand:
            case od.Pipe():
                match operand._data:
                    case bool():            return False if self._amount == 0 else True   # bool is a subclass of int !!
                    case int():             return self._amount           # returns a int()
                    case Fraction():        return Fraction(self._amount)
                    case float():           return float(self._amount)
                    case _:                 return super().__mod__(operand)
            case bool():            return False if self._amount == 0 else True   # bool is a subclass of int !!
            case int():             return self._amount
            case Fraction():        return Fraction(self._amount)
            case float():           return float(self._amount)
            case ra.Rational():     return operand.copy() << od.Pipe( self._amount )
            case ou.Unit():            return operand.copy(self)
            case str():             return str(self._amount)
            case _:                 return super().__mod__(operand)


    def __bool__(self) -> bool:  # For Python 3
        return self._amount != 0

    def __nonzero__(self) -> bool:  # For Python 2
        return self.__bool__()
    
    def __not__(self) -> bool:
        return self._amount == 0
    
    def __eq__(self, other: any) -> bool:
        from . import operand_rational as ra
        match other:
            case RepeatedAction():
                return self._amount == other._amount
            case int() | float() | Fraction():
                return self._amount == other
            case ou.Unit():
                return self._amount == other._unit
            case ra.Rational():
                return self._amount == int( other._rational )
            case od.Conditional():
                return other == self
        return False
    
    def __lt__(self, other: any) -> bool:
        from . import operand_rational as ra
        match other:
            case RepeatedAction():
                return self._amount < other._amount
            case int() | float() | Fraction():
                return self._amount < other
            case ou.Unit():
                return self._amount < other._unit
            case ra.Rational():
                return self._amount < int( other._rational )
        return False
    
    def __gt__(self, other: any) -> bool:
        from . import operand_rational as ra
        match other:
            case RepeatedAction():
                return self._amount > other._amount
            case int() | float() | Fraction():
                return self._amount > other
            case ou.Unit():
                return self._amount > other._unit
            case ra.Rational():
                return self._amount > int( other._rational )
        return False
    
    def __str__(self):
        return f'{self._amount}'


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["amount"] = self._amount
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "amount" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._amount = serialization["parameters"]["amount"]
        return self


    def __lshift__(self, operand: any) -> Self:
        from . import operand_rational as ra
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        match operand:
            case RepeatedAction():
                super().__lshift__(operand)
                self._amount = operand._amount
            case od.Pipe():
                match operand._data:
                    case float() | Fraction() | bool():   # bool is a subclass of int !!
                                                    self._amount = int(operand._data)
                    case int():                     self._amount = operand._data
                    case ou.Unit() | ra.Rational():    self._amount = operand._data % od.Pipe( int() )
            case float() | Fraction() | bool():   # bool is a subclass of int !!
                self._amount = int(operand)
            case int():
                self._amount = operand
            case ra.Rational():
                self._amount = operand % int()
            case str():
                try:
                    self << int(operand)
                except ValueError as e:
                    pass    # No need to print anything
                    # print(f"Error: {e}, '{operand}' is not a number!")
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ol.Null():
                return self
            case o.Operand():
                self << operand % self
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


    def __iadd__(self, number: any) -> Self:
        from . import operand_rational as ra
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case RepeatedAction():
                self._amount += number._amount
            case int() | Fraction() | float():
                self._amount = int( self._amount + number )
            case ou.Unit():
                self._amount += number._unit
            case ra.Rational():
                self._amount = int( self._amount + number._rational )
        return self

    
    def __isub__(self, number: any) -> Self:
        from . import operand_rational as ra
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case RepeatedAction():
                self._amount -= number._amount
            case int() | Fraction() | float():
                self._amount = int( self._amount - number )
            case ou.Unit():
                self._amount -= number._unit
            case ra.Rational():
                self._amount = int( self._amount - number._rational )
        return self

    
    def __imul__(self, number: any) -> Self:
        from . import operand_rational as ra
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case RepeatedAction():
                self._amount *= number._amount
            case int() | Fraction() | float():
                self._amount = int( self._amount * number )
            case ou.Unit():
                self._amount *= number._unit
            case ra.Rational():
                self._amount = int( self._amount * number._rational )
        return self

    
    def __itruediv__(self, number: any) -> Self:
        from . import operand_rational as ra
        number = self._tail_wrap(number)      # Processes the tailed self operands if existent
        match number:
            case RepeatedAction():
                if number._amount != 0:
                    self._amount /= number._amount
            case int() | Fraction() | float():
                if number != 0:
                    self._amount = int( self._amount / number )
            case ou.Unit():
                if number._unit != 0:
                    self._amount = int( self._amount / number._unit )
            case ra.Rational():
                if number._rational != 0:
                    self._amount = int( self._amount / number._rational )
        return self



class Invert(RepeatedAction):
    """`Act -> RepeatedAction -> Invert`

    Invert() inverts the selected elements for each given position.
    
    Parameters
    ----------
    int(1) : Sets the degree of inversion starting by 0 meaning no inversion
    """
    def _single_act(self, element: 'Element') -> 'Element':
        if element.is_owned():
            element_clip: oc.Clip = element.element_clip()
            element_position: ra.Position = element % ra.Position()
            clip_shallow_copy = element_clip.shallow_copy()
            clip_shallow_copy &= of.Equal(element_position)

        return element




