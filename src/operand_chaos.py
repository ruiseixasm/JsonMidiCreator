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
import operand_tamer as ot


class Chaos(o.Operand):
    """`Chaos`

    Chaos, contrarily to Randomness, is repeatable and has order in it.
    This class allows trough parametrization the unpredictable return of data
    and processing of other `Operand` in a repeatable way.

    Parameters
    ----------
    Tamer() : The Tamer that adds criteria to the validation of each final result.
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._tamer: ot.Tamer           = ot.Tamer()
        self._max_iterations: int       = 1000
        self._xn: ra.Xn                 = ra.Xn()
        self._x0: ra.X0                 = ra.X0(self._xn)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def number_to_int(self, number: Union['ou.Unit', 'ra.Rational', int, float, Fraction]) -> int:
        match number:
            case ou.Unit() | ra.Rational():
                return number % int()
            case int() | float() | Fraction():
                return int(number)
        return 0

    def tame(self, number: Fraction) -> bool:
        # Makes sure it's a Rational first
        rational: Fraction = ra.Rational(number) % Fraction()
        return self._tamer.tame(rational, True)[1]

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ot.Tamer():            return self._tamer
                    case ra.Xn():               return self._xn
                    case ra.X0():               return self._x0
                    case Fraction():            return self._xn._rational
                    case _:                     return super().__mod__(operand)
            case ot.Tamer():            return self._tamer.copy()
            case ra.Xn():               return self._xn.copy()
            case ra.X0():               return self._x0.copy()
            case int() | float() | Fraction():
                self.__imul__(operand)  # Numbers trigger iterations
                result = ra.Result(self._tamer.tame(self % od.Pipe(Fraction()))[0])
                # result = ra.Result(self % od.Pipe(Fraction()))
                return result % operand
            case list():
                list_out: list = []
                for number in operand:
                    list_out.append(self % number)  # Implicit iterations
                return list_out
            case Chaos():
                return operand.copy(self)
            case o.Operand():   # Operand has to have the triggering value (Fraction)
                return operand.copy(self % (operand % Fraction()))
            case _:
                return super().__mod__(operand)

    def __str__(self) -> str:
        return f'{self._index + 1}: {self._xn % float()}'
    
    def __eq__(self, other: 'Chaos') -> bool:
        if type(self) == type(other):
            return self._xn == other._xn    # Only the actual result matters, NOT the x0
        if isinstance(other, od.Conditional):
            return other == self
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["tamer"] = self.serialize( self._tamer )
        serialization["parameters"]["xn"] = self.serialize( self._xn )
        serialization["parameters"]["x0"] = self.serialize( self._x0 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "tamer" in serialization["parameters"] and "xn" in serialization["parameters"] and "x0" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._tamer = self.deserialize( serialization["parameters"]["tamer"] )
            self._xn = self.deserialize( serialization["parameters"]["xn"] )
            self._x0 = self.deserialize( serialization["parameters"]["x0"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Chaos():
                super().__lshift__(operand)
                self._tamer         = operand._tamer.copy()
                self._xn            << operand._xn
                self._x0            << operand._x0
            case od.Pipe():
                match operand._data:
                    case ot.Tamer():                self._tamer = operand._data
                    case ra.Xn():                   self._xn = operand._data
                    case ra.X0():                   self._x0 = operand._data
                    case int() | float() | Fraction():
                        self._xn << operand._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ot.Tamer():                self._tamer = operand.copy()
            case ra.Xn():                   self._xn << operand
            case ra.X0():                   self._x0 << operand
            case int() | float() | Fraction():
                if isinstance(self._next_operand, Chaos):
                    self._next_operand << operand
                self <<= operand
                self._x0 << self._xn
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __pow__(self, operand: 'o.Operand') -> Self:
        '''
        This operator ** tags another Operand to self that will be the target of the << operation and \
            be passed to self afterwards in a chained fashion.
        '''
        if isinstance(operand, Chaos):
            self << operand % Fraction()    # SETS THE DEFAULT x0 PARAMETER
            self._next_operand = operand
            return self
        return self.__pow__(operand)
    
    def __imul__(self, number: Union['ou.Unit', 'ra.Rational', int, float, Fraction]) -> Self:
        number = self.number_to_int(number)
        return self.iterate(number)
    
    # self is the pusher
    def __rshift__(self, operand: any) -> Self:
        return self.__irshift__(operand)    # Does not Copy !!

    # Pass trough method that always results in a Chaos (Self)
    def __irshift__(self, operand: any) -> Self:
        return self.__imul__(operand)
    
    # Unitary iterations on the operand
    def __irrshift__(self, operand: o.T) -> o.T:
        import operand_container as oc
        match operand:
            case int() | float() | Fraction():
                self.iterate(1) # Does a single iteration
                result: o.TypeNumeral = self._tamer.tame(self % od.Pipe(Fraction()))[0]
                return ra.Result(result) % operand
            case list() | oc.Container():
                for index, item in enumerate(operand):
                    operand[index] = self.__irrshift__(item)    # Recursive call
                return operand
            case Chaos():
                return operand
            case o.Operand():
                self.iterate(1) # Does a single iteration
                result: o.TypeNumeral = self._tamer.tame(self % od.Pipe(Fraction()))[0]
                return operand << result
            case _:
                return super().__irrshift__(operand)


    def iterate(self, times: int = 1) -> Self:
        if times > 0:
            numeral: Fraction = self % od.Pipe(Fraction())
            tamed: bool = True
            if isinstance(self._next_operand, Chaos):   # iterations are done from tail left
                numeral: Fraction = self._next_operand % od.Pipe(Fraction())
                numeral, tamed = self._next_operand.result(numeral, times)
            if tamed:
                self.result(numeral, times)
        return self

    def result(self, numeral: Fraction, iterations: int = 1) -> tuple[Fraction, bool]:
        result: Fraction = numeral
        tamed: bool = False
        count_down: int = self._max_iterations
        increased_index: int = 0
        while not tamed and count_down > 0:
            for _ in range(iterations):
                ####################
                # INSERT CODE HERE #
                ####################
                increased_index += 1
            tamed = self.tame(result)
            count_down -= 1
        if tamed:
            self._xn._rational = result
            self._index += increased_index
            self._initiated = True
        else:
            print(f"Warning: {self.__class__.__name__} Chaos couldn't be tamed!")
        return result, tamed

    def reset(self, *parameters) -> Self:
        self._xn << self._x0
        self._initiated     = False
        self._set           = False
        self._index         = 0
        # RESET THE SELF OPERANDS RECURSIVELY
        if isinstance(self._next_operand, Chaos):
            self << self._next_operand.reset() % Fraction()
        elif isinstance(self._next_operand, o.Operand):
            self << self._next_operand.reset()
        self.reset_tamers()
        return self << parameters

    def reset_tamers(self) -> Self:
        # Reset Tamers recursively
        if isinstance(self._next_operand, Chaos):
            self._next_operand.reset_tamers()
        self._tamer.reset()
        return self


class Cycle(Chaos):
    """`Chaos -> Cycle`

    Increments the `Xn` by each step and its return is the remainder of the given `Modulus`.

    Parameters
    ----------
    Tamer() : The Tamer that adds criteria to the validation of each final result.
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    Modulus(12) : The cyclic value on which the `Xn` modulus % operation is made.
    Steps(1), Step() : The increase amount for each iteration.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._modulus: Fraction = Fraction(12)
        self._steps: Fraction   = Fraction(1)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Modulus():          return operand._data << self._modulus
                    case ra.Steps():            return operand._data << self._steps
                    case _:                     return super().__mod__(operand)
            case ra.Modulus():          return ra.Modulus(self._modulus)
            case ra.Steps():            return ra.Steps(self._steps)
            case ra.Step():             return ra.Step(self._steps)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: Any) -> bool:
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._modulus == other._modulus and self._steps == other._steps
            case _:
                return super().__eq__(other)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["modulus"]  = self.serialize( self._modulus )
        serialization["parameters"]["steps"]    = self.serialize( self._steps )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "modulus" in serialization["parameters"] and "steps" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._modulus   = self.deserialize( serialization["parameters"]["modulus"] )
            self._steps     = self.deserialize( serialization["parameters"]["steps"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Cycle():
                super().__lshift__(operand)
                self._modulus   = operand._modulus
                self._steps     = operand._steps
            case od.Pipe():
                match operand._data:
                    case ra.Modulus():          self._modulus   = operand._data._rational
                    case ra.Steps():            self._steps     = operand._data._rational
                    case _:                     super().__lshift__(operand)
            case ra.Modulus():      self._modulus   = operand._rational
            case ra.Steps() | ra.Step():
                self._steps     = operand._rational
            case _:
                super().__lshift__(operand)
        # Makes sure xn isn't out of the cycle
        self._xn << self._xn % Fraction() % self._modulus
        return self

    def result(self, numeral: Fraction, iterations: int = 1) -> tuple[Fraction, bool]:
        result: Fraction = numeral
        tamed: bool = False
        count_down: int = self._max_iterations
        increased_index: int = 0
        while not tamed and count_down > 0:
            for _ in range(iterations):
                result += self._steps
                result %= self._modulus
                increased_index += 1
            tamed = self.tame(result)
            count_down -= 1
        if tamed:
            self._xn._rational = result
            self._index += increased_index
            self._initiated = True
        else:
            print(f"Warning: {self.__class__.__name__} Chaos couldn't be tamed!")
        return result, tamed

class Counter(Cycle):
    """`Chaos -> Cycle -> Counter`

    The Xn represents the total number of completed cycles.
    Contrary to modulus, the counter returns the amount of completed cycles.

    Parameters
    ----------
    Tamer() : The Tamer that adds criteria to the validation of each final result.
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    Modulus(1) : The modulus value on which the `Xn` modulus % operation is made.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._modulus: Fraction = Fraction(1)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def result(self, numeral: Fraction, iterations: int = 1) -> tuple[Fraction, bool]:
        result: Fraction = numeral
        tamed: bool = False
        count_down: int = self._max_iterations
        increased_index: int = 0
        while not tamed and count_down > 0:
            for _ in range(iterations):
                increased_index += 1
                actual_index: int = self._index + increased_index
                result = actual_index % self._modulus
                increased_index += 1
            tamed = self.tame(result)
            count_down -= 1
        if tamed:
            self._xn._rational = result
            self._index += increased_index
            self._initiated = True
        else:
            print(f"Warning: {self.__class__.__name__} Chaos couldn't be tamed!")
        return result, tamed

class Ripple(Cycle):
    """`Chaos -> Cycle -> Ripple`

    Similar to the ripple effect in water the result alternates positively and negatively `
        increasing each alternation by the step amount.

    Parameters
    ----------
    Tamer() : The Tamer that adds criteria to the validation of each final result.
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    Steps(1), Step() : The increase amount for each iteration.
    """
    def result(self, numeral: Fraction, iterations: int = 1) -> tuple[Fraction, bool]:
        result: Fraction = numeral
        tamed: bool = False
        count_down: int = self._max_iterations
        increased_index: int = 0
        while not tamed and count_down > 0:
            for _ in range(iterations):
                result *= -1    # Always alternates (0 means 0)
                increased_index += 1
                actual_index: int = self._index + increased_index
                if actual_index % 2:    # Odd means up (positive)
                    if result < 0:
                        result -= self._steps
                    else:
                        result += self._steps
            tamed = self.tame(result)
            count_down -= 1
        if tamed:
            self._xn._rational = result
            self._index += increased_index
            self._initiated = True
        else:
            print(f"Warning: {self.__class__.__name__} Chaos couldn't be tamed!")
        return result, tamed

class Spiral(Cycle):
    """`Chaos -> Cycle -> Spiral`

    Similar to a `Ripple` but always move a step for each iteration and not jus the odd ones.

    Parameters
    ----------
    Tamer() : The Tamer that adds criteria to the validation of each final result.
    Xn(0), int, float : The resultant value of each iteration.
    X0(0) : The first value of the multiple iterations where Chaos can be reset to.
    Steps(1), Step() : The increase amount for each iteration.
    """
    def result(self, numeral: Fraction, iterations: int = 1) -> tuple[Fraction, bool]:
        result: Fraction = numeral
        tamed: bool = False
        count_down: int = self._max_iterations
        increased_index: int = 0
        while not tamed and count_down > 0:
            for _ in range(iterations):
                result *= -1    # Always alternates (0 means 0)
                increased_index += 1
                if result < 0:
                    result -= self._steps
                else:
                    result += self._steps
            tamed = self.tame(result)
            count_down -= 1
        if tamed:
            self._xn._rational = result
            self._index += increased_index
            self._initiated = True
        else:
            print(f"Warning: {self.__class__.__name__} Chaos couldn't be tamed!")
        return result, tamed


class Bouncer(Chaos):
    """`Chaos -> Bouncer`

    Bouncer works much alike the moving word in a screen saver.
    So, it is a two dimensional data generator, with a Xn and a Yn.
    The `Bouncer() % int()` and `Bouncer() % float()` returns the hypotenuse.

    Parameters
    ----------
    Tamer() : The Tamer that adds criteria to the validation of each final result.
    Width(16) : Horizontal size of the "screen".
    Height(9) : Vertical size of the "screen".
    dX(0.555) : The incremental value for the horizontal position.
    dY(0.555) : The incremental value for the vertical position.
    Xn(Width(16) / 2), int, float : The resultant horizontal value of each iteration.
    Yn(Height(9) / 2) : The resultant vertical value of each iteration.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._width: ra.Width   = ra.Width(16)
        self._height: ra.Height = ra.Height(9)
        self._dx: ra.dX         = ra.dX(0.555)
        self._dy: ra.dY         = ra.dY(0.555)
        self._xn                = ra.Xn(self._width / 2 % Fraction())
        self._x0                = ra.X0(self._xn)
        self._yn: ra.Yn         = ra.Yn(self._height / 2 % Fraction())
        self._y0: ra.Y0         = ra.Y0(self._yn)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Width():            return self._width
                    case ra.Height():           return self._height
                    case ra.dX():               return self._dx
                    case ra.dY():               return self._dy
                    case ra.Xn():               return self._xn
                    case ra.X0():               return self._x0
                    case ra.Yn():               return self._yn
                    case ra.Y0():               return self._y0
                    case Fraction():            return ra.Result(math.hypot(self._xn % float(), self._yn % float()))._rational
                    case _:                     return super().__mod__(operand)
            case ra.Width():            return self._width.copy()
            case ra.Height():           return self._height.copy()
            case ra.dX():               return self._dx.copy()
            case ra.dY():               return self._dy.copy()
            case ra.Xn():               return self._xn.copy()
            case ra.X0():               return self._x0.copy()
            case ra.Yn():               return self._yn.copy()
            case ra.Y0():               return self._y0.copy()
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: 'Bouncer') -> bool:
        if type(self) != type(other):
            return False
        return  self._xn == other._xn and self._yn == other._yn
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["width"]    = self.serialize( self._width )
        serialization["parameters"]["height"]   = self.serialize( self._height )
        serialization["parameters"]["dx"]       = self.serialize( self._dx )
        serialization["parameters"]["dy"]       = self.serialize( self._dy )
        serialization["parameters"]["xn"]       = self.serialize( self._xn )
        serialization["parameters"]["x0"]       = self.serialize( self._x0 )
        serialization["parameters"]["yn"]       = self.serialize( self._yn )
        serialization["parameters"]["y0"]       = self.serialize( self._y0 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "width" in serialization["parameters"] and "height" in serialization["parameters"] and "dx" in serialization["parameters"] and
            "dy" in serialization["parameters"] and "xn" in serialization["parameters"] and "x0" in serialization["parameters"] and 
            "yn" in serialization["parameters"] and "y0" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._width     = self.deserialize( serialization["parameters"]["width"] )
            self._height    = self.deserialize( serialization["parameters"]["height"] )
            self._dx        = self.deserialize( serialization["parameters"]["dx"] )
            self._dy        = self.deserialize( serialization["parameters"]["dy"] )
            self._xn        = self.deserialize( serialization["parameters"]["xn"] )
            self._x0        = self.deserialize( serialization["parameters"]["x0"] )
            self._yn        = self.deserialize( serialization["parameters"]["yn"] )
            self._y0        = self.deserialize( serialization["parameters"]["y0"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        match operand:
            case Bouncer():
                super().__lshift__(operand)
                self._width     << operand._width
                self._height    << operand._height
                self._dx        << operand._dx
                self._dy        << operand._dy
                self._xn        << operand._xn
                self._x0        << operand._x0
                self._yn        << operand._yn
                self._y0        << operand._y0
            case od.Pipe():
                match operand._data:
                    case ra.Width():    self._width = operand._data
                    case ra.Height():   self._height = operand._data
                    case ra.dX():       self._dx = operand._data
                    case ra.dY():       self._dy = operand._data
                    case ra.Xn():       self._xn = operand._data
                    case ra.X0():       self._x0 = operand._data
                    case ra.Yn():       self._yn = operand._data
                    case ra.Y0():       self._y0 = operand._data
                    case int() | float() | Fraction():
                        operand_rational: Fraction = ra.Numeral(operand)._rational
                        if operand_rational != 0:
                            hypotenuse: Fraction = self % operand_rational
                            ratio: Fraction = hypotenuse / operand_rational
                            self._xn *= ratio
                            self._yn *= ratio
                    case _:             super().__lshift__(operand)
            case ra.Width():    self._width << operand
            case ra.Height():   self._height << operand
            case ra.dX():       self._dx << operand
            case ra.dY():       self._dy << operand
            case ra.Xn():       self._xn << operand
            case ra.X0():       self._x0 << operand
            case ra.Yn():       self._yn << operand
            case ra.Y0():       self._y0 << operand
            case int() | float() | Fraction():
                super().__lshift__(operand)
                self._y0 << self._yn
            case _:
                super().__lshift__(operand)
        # Final needed modulation
        self._xn << (self._xn % float()) % (self._width % float())
        self._yn << (self._yn % float()) % (self._height % float())
        return self

    def result(self, numeral: Fraction, iterations: int = 1) -> tuple[Fraction, bool]:
        result: Fraction = numeral
        tamed: bool = False
        count_down: int = self._max_iterations
        increased_index: int = 0
        position_x: Fraction = self._xn._rational
        position_y: Fraction = self._yn._rational
        while not tamed and count_down > 0:
            for _ in range(iterations):
                for direction_data in [
                            [position_x, self._dx._rational, self._width._rational],
                            [position_y, self._dy._rational, self._height._rational]
                        ]:
                    new_position: Fraction = direction_data[0] + direction_data[1]
                    if new_position < 0:
                        direction_data[1] << direction_data[1] * -1 # flips direction
                        new_position = new_position * -1 % direction_data[2]
                    elif new_position >= direction_data[2]:
                        direction_data[1] << direction_data[1] * -1 # flips direction
                        new_position = direction_data[2] - new_position % direction_data[2]
                    direction_data[0] = new_position
                increased_index += 1
            tamed = self.tame(result)
            count_down -= 1
        if tamed:
            self._xn._rational = position_x
            self._yn._rational = position_y
            self._index += increased_index
            self._initiated = True
        else:
            print(f"Warning: {self.__class__.__name__} Chaos couldn't be tamed!")
        return result, tamed

    def __str__(self) -> str:
        return f'{self._index + 1}: {self % tuple()}'
    
    def reset(self, *parameters) -> Self:
        self._yn << self._y0
        return super().reset(*parameters)

class SinX(Chaos):
    """`Chaos -> SinX`

    Represents a more traditional chaotic formulation with the use of the Sin function.

    Parameters
    ----------
    Tamer() : The Tamer that adds criteria to the validation of each final result.
    Xn(2), int, float : The resultant value of each iteration.
    X0(Xn(2)) : The starting value of all iterations possible to reset to.
    Lambda(77.238537) : Sets the lambda constant of the formula `Xn + Lambda * Sin(Xn)`.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._xn                        << 2
        self._x0                        << self._xn
        self._lambda: ra.Lambda         = ra.Lambda(77.238537) # Can't be an integer in order to be truly chaotic !!
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Lambda():           return self._lambda
                    case _:                     return super().__mod__(operand)
            case ra.Lambda():           return self._lambda.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'SinX') -> bool:
        if super().__eq__(other):
            return  self._lambda == other % od.Pipe( ra.Lambda() )
        return False
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["lambda"] = self.serialize( self._lambda )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "lambda" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._lambda = self.deserialize( serialization["parameters"]["lambda"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        match operand:
            case SinX():
                super().__lshift__(operand)
                self._lambda << operand._lambda
            case od.Pipe():
                match operand._data:
                    case ra.Lambda():               self._lambda = operand._data
                    case _:                         super().__lshift__(operand)
            case ra.Lambda():               self._lambda << operand
            case ra.Xn():                   self._xn << operand
            case ra.X0():                   self._x0 << operand
            case _:
                super().__lshift__(operand)
        return self

    def result(self, numeral: Fraction, iterations: int = 1) -> tuple[Fraction, bool]:
        result: Fraction = numeral
        tamed: bool = False
        count_down: int = self._max_iterations
        increased_index: int = 0
        while not tamed and count_down > 0:
            for _ in range(iterations):
                result = ra.Result(float(result) + float(self._lambda._rational) * math.sin(float(result)))._rational
                increased_index += 1
            tamed = self.tame(result)
            count_down -= 1
        if tamed:
            self._xn._rational = result
            self._index += increased_index
            self._initiated = True
        else:
            print(f"Warning: {self.__class__.__name__} Chaos couldn't be tamed!")
        return result, tamed

