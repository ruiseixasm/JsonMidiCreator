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
import re
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_data as od

import operand_frame as of
import operand_label as ol


# Units have never None values and are also const, with no setters
class Unit(o.Operand):
    """`Unit`

    This type of Operand is associated to an Integer.
    This class is intended to represent parameters that are whole numbers like midi messages from 0 to 127

    Parameters
    ----------
    first : integer_like
        An Integer described as a Unit
    """
    def __init__(self, *parameters):
        self._unit: int = 0
        super().__init__(*parameters)

    def unit(self, number: int = None) -> Self:
        return self << od.DataSource( number )

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract the Unit, because a Unit is an Integer
        it should be used in conjugation with int(). If used with a float() it
        will return the respective unit formatted as a float.

        Examples
        --------
        >>> channel_int = Channel(12) % int()
        >>> print(channel_int)
        12
        """
        import operand_rational as ra
        match operand:
            case od.DataSource():
                match operand._data:
                    case int():             return self._unit           # returns a int()
                    case bool():            return False if self._unit == 0 else True
                    case Fraction():        return Fraction(self._unit)
                    case float():           return float(self._unit)
                    case of.Frame():        return self % od.DataSource( operand._data )
                    case Unit() | ra.Rational():
                                            return operand.__class__() << od.DataSource( self._unit )
                    case _:                 return super().__mod__(operand)
            case int():             return self._unit
            case bool():            return False if self._unit == 0 else True
            case Fraction():        return Fraction(self._unit)
            case float():           return float(self._unit)
            case of.Frame():        return self % operand
            case Unit() | ra.Rational():
                                    return operand.__class__() << od.DataSource( self._unit )
            case _:                 return super().__mod__(operand)

    def __bool__(self) -> bool:  # For Python 3
        return self._unit != 0

    def __nonzero__(self) -> bool:  # For Python 2
        return self.__bool__()
    
    def __not__(self) -> bool:
        return self._unit == 0
    
    def __eq__(self, other: any) -> bool:
        import operand_rational as ra
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case int() | float() | Fraction():
                return self._unit == other
            case Unit():
                return self._unit == other._unit
            case ra.Rational():
                return self._unit == int( other._rational )
            case od.Conditional():
                return other == self
            case _:
                if other.__class__ == o.Operand:
                    return True
        return False
    
    def __lt__(self, other: any) -> bool:
        import operand_rational as ra
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case int() | float() | Fraction():
                return self._unit < other
            case Unit():
                return self._unit < other._unit
            case ra.Rational():
                return self._unit < int( other._rational )
        return False
    
    def __gt__(self, other: any) -> bool:
        import operand_rational as ra
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case int() | float() | Fraction():
                return self._unit > other
            case Unit():
                return self._unit > other._unit
            case ra.Rational():
                return self._unit > int( other._rational )
        return False
    
    def __str__(self):
        return f'{self._unit}'
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["unit"] = self._unit
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Unit':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "unit" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._unit = serialization["parameters"]["unit"]
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Unit():
                super().__lshift__(operand)
                self._unit = operand._unit
            case od.DataSource():
                match operand._data:
                    case int():                     self._unit = operand._data
                    case float() | Fraction() | bool():
                                                    self._unit = int(operand._data)
                    case Unit() | ra.Rational():    self._unit = operand._data % od.DataSource( int() )
            case int():
                self._unit = operand
            case float() | Fraction() | bool():
                self._unit = int(operand)
            case ra.Rational():
                self._unit = operand % int()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __iadd__(self, number: any) -> Self:
        import operand_rational as ra
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case int() | Fraction() | float():
                self._unit = int( self._unit + number )
            case Unit():
                self._unit += number._unit
            case ra.Rational():
                self._unit = int( self._unit + number._rational )
        return self
    
    def __isub__(self, number: any) -> Self:
        import operand_rational as ra
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case int() | Fraction() | float():
                self._unit = int( self._unit - number )
            case Unit():
                self._unit -= number._unit
            case ra.Rational():
                self._unit = int( self._unit - number._rational )
        return self
    
    def __imul__(self, number: any) -> Self:
        import operand_rational as ra
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case int() | Fraction() | float():
                self._unit = int( self._unit * number )
            case Unit():
                self._unit *= number._unit
            case ra.Rational():
                self._unit = int( self._unit * number._rational )
        return self
    
    def __itruediv__(self, number: any) -> Self:
        import operand_rational as ra
        number = self & number      # Processes the tailed self operands or the Frame operand if any exists
        match number:
            case int() | Fraction() | float():
                if number != 0:
                    self._unit = int( self._unit / number )
            case Unit():
                if number._unit != 0:
                    self._unit = int( self._unit / number._unit )
            case ra.Rational():
                if number._rational != 0:
                    self._unit = int( self._unit / number._rational )
        return self

class Next(Unit):
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

class Previous(Unit):
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

class Total(Unit):
    pass

class TimeUnit(Unit):
    def __init__(self, *parameters):
        import operand_generic as og
        self._staff_reference: og.Staff     = og.defaults._staff
        super().__init__(*parameters)

    if TYPE_CHECKING:
        from operand_generic import Staff

    def set_staff_reference(self, staff_reference: 'Staff' = None) -> 'TimeUnit':
        import operand_generic as og
        if isinstance(staff_reference, og.Staff):
            self._staff_reference = staff_reference
        return self

    def get_staff_reference(self) -> 'Staff':
        return self._staff_reference

    def reset_staff_reference(self) -> 'TimeUnit':
        import operand_generic as og
        self._staff_reference = og.defaults._staff
        return self

    #######################################################################
    # Conversion (Simple, One-way) | Only destination Staff is considered #
    #######################################################################

    if TYPE_CHECKING:
        from operand_rational import Convertible, Position, Length, Duration, Measures, Beats, Steps

    def convertToBeats(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Beats':
        match time:
            case None:
                return self._staff_reference.convertToBeats(self)
            case _:
                return self._staff_reference.convertToBeats(time)

    def convertToMeasures(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Measures':
        match time:
            case None:
                return self._staff_reference.convertToMeasures(self)
            case _:
                return self._staff_reference.convertToMeasures(time)
        
    def convertToSteps(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Steps':
        match time:
            case None:
                return self._staff_reference.convertToSteps(self)
            case _:
                return self._staff_reference.convertToSteps(time)

    def convertToDuration(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Duration':
        match time:
            case None:
                return self._staff_reference.convertToDuration(self)
            case _:
                return self._staff_reference.convertToDuration(time)

    def convertToMeasure(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Measure':
        match time:
            case None:
                return self._staff_reference.convertToMeasure(self)
            case _:
                return self._staff_reference.convertToMeasure(time)

    def convertToBeat(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Beat':
        match time:
            case None:
                return self._staff_reference.convertToBeat(self)
            case _:
                return self._staff_reference.convertToBeat(time)

    def convertToStep(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Step':
        match time:
            case None:
                return self._staff_reference.convertToStep(self)
            case _:
                return self._staff_reference.convertToStep(time)

    def convertToPosition(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Position':
        match time:
            case None:
                return self._staff_reference.convertToPosition(self)
            case _:
                return self._staff_reference.convertToPosition(time)

    def convertToLength(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Length':
        match time:
            case None:
                return self._staff_reference.convertToLength(self)
            case _:
                return self._staff_reference.convertToLength(time)

    ################################################################################################################
    # Transformation (Two-way, Context-Dependent) | Both Staffs are considered, the source and the destination one #
    ################################################################################################################

    def transformBeats(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Beats':
        match time:
            case None:
                return self._staff_reference.transformBeats(self)
            case _:
                return self._staff_reference.transformBeats(time)

    def transformMeasures(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Measures':
        match time:
            case None:
                return self._staff_reference.transformMeasures(self)
            case _:
                return self._staff_reference.transformMeasures(time)

    def transformSteps(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Steps':
        match time:
            case None:
                return self._staff_reference.transformSteps(self)
            case _:
                return self._staff_reference.transformSteps(time)

    def transformDuration(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Duration':
        match time:
            case None:
                return self._staff_reference.transformDuration(self)
            case _:
                return self._staff_reference.transformDuration(time)

    def transformMeasure(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Measure':
        match time:
            case None:
                return self._staff_reference.transformMeasure(self)
            case _:
                return self._staff_reference.transformMeasure(time)

    def transformBeat(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Beat':
        match time:
            case None:
                return self._staff_reference.transformBeat(self)
            case _:
                return self._staff_reference.transformBeat(time)

    def transformStep(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Step':
        match time:
            case None:
                return self._staff_reference.transformStep(self)
            case _:
                return self._staff_reference.transformStep(time)

    def transformPosition(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Position':
        match time:
            case None:
                return self._staff_reference.transformPosition(self)
            case _:
                return self._staff_reference.transformPosition(time)

    def transformLength(self, time: Union['Convertible', 'TimeUnit'] = None) -> 'Length':
        match time:
            case None:
                return self._staff_reference.transformLength(self)
            case _:
                return self._staff_reference.transformLength(time)


    def getMillis_rational(self, time: Union['Convertible', 'TimeUnit'] = None) -> Fraction:
        match time:
            case None:
                return self._staff_reference.getMinutes(self)
            case _:
                return self._staff_reference.getMinutes(time)

    def getPlaylist(self, position: 'Position' = None) -> list:
        match position:
            case None:
                return self._staff_reference.getPlaylist(self)
            case _:
                return self._staff_reference.getPlaylist(position)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
                self._staff_reference = operand._staff_reference
            case _:
                super().__lshift__(operand)
        return self


class Measure(TimeUnit):
    """`Unit -> TimeUnit -> Measure`

    A Measure() represents the basic unit of a Staff division by witch Clips are multiplied,
    and is set as an integer without decimal places.
    Its return from Length and Position objects represents their rounded value accordingly.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like, Convertible_like, or TimeUnit_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 0 Measures.
    
    Examples
    --------
    Creating a Measure with a single value:
    >>> measure = Measure(1.5)
    
    Creating a Measure with multiple values (the last will determine the amount of Measures):
    >>> measure = Measure(1, 0.5, Fraction(1, 4))

    Default Measure (0):
    >>> measure = Measure()
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case TimeUnit() | ra.Convertible():
                self._unit = self._staff_reference.convertToMeasure(operand)._unit
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'Measure':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__iadd__(self._staff_reference.convertToMeasure(operand)._unit)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Measure':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__isub__(self._staff_reference.convertToMeasure(operand)._unit)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Measure':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__imul__(self._staff_reference.convertToMeasure(operand)._unit)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Measure':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__itruediv__(self._staff_reference.convertToMeasure(operand)._unit)
            case _:
                super().__itruediv__(operand)
        return self


class Beat(TimeUnit):
    """`Unit -> TimeUnit -> Beat`

    A Beat() represents the basic unit of a TimeSignature in relation to Measures (Ex 4 per Measure),
    and is set as an integer without decimal places.
    Its return from Length and Position objects represents their rounded value accordingly.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like, Convertible_like, or TimeUnit_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 0 Beats.
    
    Examples
    --------
    Creating a Beat with a single value:
    >>> beat = Beat(1.5)
    
    Creating a Beat with multiple values (the last will determine the amount of Beats):
    >>> beat = Beat(1, 0.5, Fraction(1, 4))

    Default Beat (0):
    >>> beat = Beat()
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case TimeUnit() | ra.Convertible():
                self._unit = self._staff_reference.convertToBeat(operand)._unit
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'Beat':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__iadd__(self._staff_reference.convertToBeat(operand)._unit)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Beat':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__isub__(self._staff_reference.convertToBeat(operand)._unit)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Beat':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__imul__(self._staff_reference.convertToBeat(operand)._unit)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Beat':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__itruediv__(self._staff_reference.convertToBeat(operand)._unit)
            case _:
                super().__itruediv__(operand)
        return self


class Step(TimeUnit):
    """`Unit -> TimeUnit -> Step`

    A Step() represents an unit of Quantization (Ex 1/16) as an integer without decimal places.
    Its return from Length and Position objects represents their rounded value accordingly.

    Parameters
    ----------
    *args : integer_like, float_like, Fraction_like, Convertible_like, or TimeUnit_like
        The last passed argument is the one being considered. If no parameters are provided,
        the default is 0 Steps.
    
    Examples
    --------
    Creating a Step with a single value:
    >>> step = Step(1.5)
    
    Creating a Step with multiple values (the last will determine the amount of Steps):
    >>> step = Step(1, 0.5, Fraction(1, 4))

    Default Step (0):
    >>> step = Step()
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():
                super().__lshift__(operand)
            case TimeUnit() | ra.Convertible():
                self._unit = self._staff_reference.convertToStep(operand)._unit
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'Step':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__iadd__(self._staff_reference.convertToStep(operand)._unit)
            case _:
                super().__iadd__(operand)
        return self
    
    def __isub__(self, operand: any) -> 'Step':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__isub__(self._staff_reference.convertToStep(operand)._unit)
            case _:
                super().__isub__(operand)
        return self
    
    def __imul__(self, operand: any) -> 'Step':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__imul__(self._staff_reference.convertToStep(operand)._unit)
            case _:
                super().__imul__(operand)
        return self
    
    def __itruediv__(self, operand: any) -> 'Step':
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case TimeUnit() | ra.Convertible():
                super().__itruediv__(self._staff_reference.convertToStep(operand)._unit)
            case _:
                super().__itruediv__(operand)
        return self

class Accidentals(Unit):
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

class Sharps(Accidentals):  # Sharps (###)
    """`Unit -> Accidentals -> Sharps`

    Sharps() is intended to be used with KeySignature to set its amount of Sharps.
    
    Parameters
    ----------
    first : integer_like or string_like
        A number from 0 to 7 or a string like "###" with the default as 1 ("#").
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_sharps = len(re.findall(r"#", operand))
                    if total_sharps > 0:
                        self._unit = total_sharps
            case _:
                super().__lshift__(operand)
        return self

class Flats(Accidentals):   # Flats (bbb)
    """`Unit -> Accidentals -> Flats`

    Flats() is intended to be used with KeySignature to set its amount of Flats.
    
    Parameters
    ----------
    first : integer_like or string_like
        A number from 0 to 7 or a string like "bbb" with the default as 1 ("b").
    """
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_flats = len(re.findall(r"b", operand))
                    if total_flats > 0:
                        self._unit = total_flats
            case _:
                super().__lshift__(operand)
        return self


class KeySignature(Unit):       # Sharps (+) and Flats (-)
    """`Unit -> KeySignature`

    A KeySignature() consists in an integer from -7 to 7 describing the amount
    of Sharps for positive values and the amount of Flats for negative values.
    
    Parameters
    ----------
    first : integer_like or string_like
        A number from -7 to 7 or a string like "bbb" with the default as 0 ("").
    """
    def __init__(self, *parameters):
        self._major: bool = True
        super().__init__(*parameters)
    
    _major_scale = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)    # Major scale for the default staff

    def get_tonic_key(self) -> int:
        circle_fifths_position: int = self._unit
        zero_key_int: int = 0  # C (Major)
        if not self._major:
            zero_key_int = 9   # A (minor)
        return (zero_key_int + circle_fifths_position * 7) % 12

    def get_scale_list(self) -> list[int]:
        if self._major: #                      A
            return [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major scale
                #                              |
        else:   #   ----------------------------
                #   |
            return [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]  # minor scale
                #   A

    def get_modulated_scale_list(self) -> list[int]:
        key_signature_scale: list[int] = [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]  # Major scale
        if not(self._unit == 0 and self._major):
            key_signature = KeySignature._key_signatures[(self._unit + 7) % 15]
            for key_i in range(11, -1, -1): # range(12) results in a bug
                if key_signature[key_i] != 0:
                    key_signature_scale[key_i] = 0
                    key_signature_scale[(key_i + key_signature[key_i]) % 12] = 1
            if not self._major: # Needs to rotate scale to start on the key of A (9th key)
                original_scale: list[int] = key_signature_scale.copy()
                for key_i in range(12):
                    key_signature_scale[key_i] = original_scale[(key_i + 9) % 12]
                
        return key_signature_scale
    
    def is_enharmonic(self, tonic_key: int, key: int) -> bool:
        # if self._major_scale[tonic_key % 12] != 1:
        #     return True
        self_key_signature: list[int] = self._key_signatures[(self._unit + 7) % 15]
        return self_key_signature[key % 12] != 0


    def __mod__(self, operand: o.T) -> o.T:
        import operand_generic as og
        match operand:
            case od.DataSource():
                match operand._data:
                    case of.Frame():            return self % od.DataSource( operand._data )
                    case KeySignature():        return self
                    case list():                return self % list()
                    case Major():               return Major() << od.DataSource(self._major)
                    case _:                     return super().__mod__(operand)
            case of.Frame():            return self % operand
            case KeySignature():        return self.copy()
            case int():                 return self._unit
            case float():
                return self % Key() % float()
            
            case Key():
                tonic_key: int = self.get_tonic_key()
                key_line: int = 0
                if self._unit < 0:
                    key_line = 1
                # It happens only for 7 Flats (-7) (Cb)
                if self.is_enharmonic(tonic_key, tonic_key):
                    key_line += 2    # All Sharps/Flats
                return Key( float(tonic_key + key_line * 12) )
            
            case Major():               return Major() << od.DataSource(self._major)
            case Minor():               return Minor() << od.DataSource(not self._major)
            case Sharps():
                if self._unit > 0:
                    return Sharps(self._unit)
                return Sharps(0)
            case Flats():
                if self._unit < 0:
                    return Flats(self._unit * -1)
                return Flats(0)
            case og.Scale():            return og.Scale(self % list())
            case list():                return self.get_scale_list()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: any) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if isinstance(other, KeySignature):
            return self._unit == other._unit and self._major == other._major
        if isinstance(other, od.Conditional):
            return other == self
        return self % other == other
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["major"]            = self.serialize( self._major )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeySignature':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "major" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._major         = self.deserialize( serialization["parameters"]["major"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeySignature():
                super().__lshift__(operand)
                self._major         = operand._major
            case od.DataSource():
                match operand._data:
                    case int():     self._unit      = operand._data
                    case Major():   self._major     = operand._data // bool()
            case int():     self._unit   = operand
            case Major():   self._major  = operand // bool()
            case Minor():   self._major  = not (operand // bool())
            case Sharps() | Flats():
                self._unit = operand._unit
                if isinstance(operand, Flats):
                    self._unit *= -1
            case Key():
                if self._major:
                    self._unit = self._major_keys_accidentals[ operand % int() ]
                else:
                    self._unit = self._minor_keys_accidentals[ operand % int() ]
            case str(): # Processes series of "#" and "b"
                if len(operand) == 0:
                    self._unit = 0
                else:
                    sharps = re.findall(r"#+", operand)
                    if len(sharps) > 0:
                        self._unit = len(sharps[0])
                    else:
                        flats = re.findall(r"b+", operand)
                        if len(flats) > 0:
                            self._unit = -len(flats[0])
            case _: 
                super().__lshift__(operand)
        return self

    _key_signatures: list[list] = [
    #     C      D      E   F      G      A      B
        [-1, 0, -1, 0, -1, -1, 0, -1, 0, -1, 0, -1],    # -7
        [-1, 0, -1, 0, -1, -0, 0, -1, 0, -1, 0, -1],    # -6
        [-0, 0, -1, 0, -1, -0, 0, -1, 0, -1, 0, -1],    # -5
        [-0, 0, -1, 0, -1, -0, 0, -0, 0, -1, 0, -1],    # -4
        [-0, 0, -0, 0, -1, -0, 0, -0, 0, -1, 0, -1],    # -3
        [-0, 0, -0, 0, -1, -0, 0, -0, 0, -0, 0, -1],    # -2
        [-0, 0, -0, 0, -0, -0, 0, -0, 0, -0, 0, -1],    # -1
    #     C      D      E   F      G      A      B
        [+0, 0, +0, 0, +0, +0, 0, +0, 0, +0, 0, +0],    # +0
    #     C      D      E   F      G      A      B
        [+0, 0, +0, 0, +0, +1, 0, +0, 0, +0, 0, +0],    # +1
        [+1, 0, +0, 0, +0, +1, 0, +0, 0, +0, 0, +0],    # +2
        [+1, 0, +0, 0, +0, +1, 0, +1, 0, +0, 0, +0],    # +3
        [+1, 0, +1, 0, +0, +1, 0, +1, 0, +0, 0, +0],    # +4
        [+1, 0, +1, 0, +0, +1, 0, +1, 0, +1, 0, +0],    # +5
        [+1, 0, +1, 0, +1, +1, 0, +1, 0, +1, 0, +0],    # +6
        [+1, 0, +1, 0, +1, +1, 0, +1, 0, +1, 0, +1]     # +7
    ]

    _major_keys_accidentals: dict[int, int] = {
        23:     -7,     # Cb (11 + 12 = 23)

        18:     -6,     # Gb
        10:     -6,     # A#

        13:     -5,     # Db

        20:     -4,     # Ab
        8:      -4,     # G#

        15:     -3,     # Eb
        3:      -3,     # D#

        22:     -2,     # Bb
        5:      -1,     # F
        0:      +0,     # C
        7:      +1,     # G
        2:      +2,     # D
        9:      +3,     # A
        4:      +4,     # E
        11:     +5,     # B
        6:      +6,     # F#
        1:      +7      # C#
    }

    _minor_keys_accidentals: dict[int, int] = {
        20:     -7,     # Ab (8 + 12 = 20)
        3:      -6,     # Eb
        22:     -5,     # Bb
        5:      -4,     # F
        0:      -3,     # C
        7:      -2,     # G
        2:      -1,     # D
        9:      +0,     # A
        4:      +1,     # E
        11:     +2,     # B
        6:      +3,     # F#

        1:      +4,     # C#
        13:     +4,     # Db

        8:      +5,     # G#

        3:      +6,     # D#
        15:     +6,     # Eb

        10:     +7,     # A#
        18:     +7      # Gb
    }


class PitchParameter(Unit):
    pass

class Tone(PitchParameter):
    """`Unit -> PitchParameter -> Tone`

    A Tone() represents a Key change in a given KeySignature or Scale, AKA whole-step.
    The default is 0.
    
    Parameters
    ----------
    first : integer_like
        An Integer representing the amount of whole-steps, from 0 to higher.
    """
    pass

class Semitone(PitchParameter):
    """`Unit -> PitchParameter -> Semitone`

    A Semitone() represents a pitch in a Chromatic scale, AKA half-step.
    The default is 0.
    
    Parameters
    ----------
    first : integer_like
        An Integer representing the amount of Chromatic steps, from 0 to 127.
    """
    pass

class Key(PitchParameter):
    """`Unit -> PitchParameter -> Key`

    A Key() is an integer from 0 to 11 (12 to 23 for flats) that describes
    the 12 keys of an octave.
    
    Parameters
    ----------
    first : integer_like or string_like
        A number from 0 to 11 with 0 as default or the equivalent string key "C"
    """
    def key_signature(self, key_signature: 'KeySignature' = None) -> Self:
        self._key_signature = key_signature
        return self

    def sharp(self, unit: int = None) -> Self:
        return self << od.DataSource( Sharp(unit) )

    def flat(self, unit: int = None) -> Self:
        return self << od.DataSource( Flat(unit) )

    def natural(self, unit: int = None) -> Self:
        return self << od.DataSource( Natural(unit) )

    def degree(self, unit: int = None) -> Self:
        return self << od.DataSource( Degree(unit) )

    def scale(self, scale: list[int] | str = None) -> Self:
        import operand_generic as og
        return self << od.DataSource( og.Scale(scale) )

    def __mod__(self, operand: o.T) -> o.T:
        import operand_generic as og
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():
                        return Key._keys[self._unit % 48]
                    case _:
                        return super().__mod__(operand)

            case int():
                return self._unit % 24

            case float():
                return float(self._unit % 48)

            case str():
                return Key._keys[self._unit % 48]

            case Sharp():
                line: int = self._unit // 12
                if line % 2 == 0:   # Even line
                    return Sharp(self._accidentals[self._unit % 48])
                return Sharp(0)
            case Flat():
                line: int = self._unit // 12
                if line % 2 == 1:   # Odd line
                    return Flat(self._accidentals[self._unit % 48] * -1)
                return Flat(0)

            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        import operand_generic as og
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return self % int() == other % int()    # This get's in consideration the just final key pressed
            case str():
                return self % str() == other
            case _:
                return super().__eq__(other)
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        import operand_generic as og
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand._data:
                    case int():
                        self._unit = operand._data
                    case float() | Fraction():
                        self._unit = int(operand._data)
                    case Semitone():
                        self._unit = operand._data % od.DataSource( int() )
                        self << Degree(1)

                    case str():
                        self._unit = self.getStringToNumber(operand._data) % 48
                    case _:
                        super().__lshift__(operand)
          

            case int():
                self._unit = operand % 24
            case float():
                self._unit = int(operand) % 48

            case str():
                self_unit: int = self.getStringToNumber(operand)
                if self_unit != -1:
                    self._unit = self_unit

            case _:
                super().__lshift__(operand)
        return self

    _keys: list[str] = [
        "C",   "C#", "D",   "D#", "E",   "F",   "F#", "G",   "G#", "A",   "A#", "B",    # Black Sharps
        "C",   "Db", "D",   "Eb", "E",   "F",   "Gb", "G",   "Ab", "A",   "Bb", "B",    # Black Flats
        "B#",  "C#", "C##", "D#", "D##", "E#",  "F#", "F##", "G#", "G##", "A#", "A##",  # All Sharps
        "Dbb", "Db", "Ebb", "Eb", "Fb",  "Gbb", "Gb", "Abb", "Ab", "Bbb", "Bb", "Cb"    # All Flats
    ]

    _accidentals: list[int] = [
         0,    +1,    0,    +1,    0,     0,    +1,    0,    +1,    0,    +1,    0,     # Black Sharps
         0,    -1,    0,    -1,    0,     0,    -1,    0,    -1,    0,    -1,    0,     # Black Flats
        +1,    +1,   +2,    +1,   +2,    +1,    +1,   +2,    +1,   +2,    +1,   +2,     # All Sharps
        -2,    -1,   -2,    -1,   -1,    -2,    -1,   -2,    -1,   -2,    -1,   -1      # All Flats
    ]
    
    def getStringToNumber(self, key: str = "C") -> int:
        key_to_find: str = key.strip().lower()
        for index, value in enumerate(Key._keys):
            if value.lower().find(key_to_find) != -1:
                return index
        return -1

class Tonic(Key):
    """`Unit -> PitchParameter -> Key -> Tonic`

    An Tonic() represents the root note of a given pitch, with same pitch to a Degree of 1.
    The default value is the Tonic key is 0 representing the key of C.
    
    Parameters
    ----------
    first : integer_like
        An Integer representing the key offset relative to the key of C.
    """
    pass

class Root(Key):
    pass

class Home(Key):
    pass


class Octave(PitchParameter):
    """`Unit -> PitchParameter -> Octave`

    An Octave() represents the full midi keyboard, varying from -1 to 9 (11 octaves).
    The default value is 1 octave.
    
    Parameters
    ----------
    first : integer_like
        An Integer representing the full midi keyboard octave varying from -1 to 9
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters) # By default it's 1 to be used in basic operations like + and -

class Degree(PitchParameter):
    """`Unit -> PitchParameter -> Degree`

    A Degree() represents its relation with a Tonic key on a scale
    and respective Progressions.
    
    Parameters
    ----------
    first : integer_like
        Accepts a numeral (5) or the string (V) with 1 as the default
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters) # By default the degree it's 1 (I, Tonic)

    _degree = ("I", "ii", "iii", "IV", "V", "vi", "viiº")

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case str():
                adjusted_degree: int = self._unit
                if adjusted_degree > 0:
                    adjusted_degree -= 1
                return __class__._degree[adjusted_degree % 7]
            case _:
                return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():
                        self.stringSetDegree(operand._data)
                    case _:
                        super().__lshift__(operand)
            case str():
                self.stringSetDegree(operand)
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, number: any) -> 'Degree':
        super().__iadd__(number)
        if self._unit == 0 or self._unit == -1:
            self._unit = 1      # Always jumps to 1
        return self
    
    def __isub__(self, number: any) -> 'Degree':
        super().__isub__(number)
        if self._unit == 0 or self._unit == -1:
            self._unit = 1      # Always jumps to 1
        return self
    
    def __imul__(self, number: any) -> 'Degree':
        super().__imul__(number)
        if self._unit == 0 or self._unit == -1:
            self._unit = 1      # Always jumps to 1
        return self
    
    def __itruediv__(self, number: any) -> 'Degree':
        super().__itruediv__(number)
        if self._unit == 0 or self._unit == -1:
            self._unit = 1      # Always jumps to 1
        return self
    
    def stringSetDegree(self, string: str) -> None:
        string = string.strip()
        match re.sub(r'[^a-z]', '', string.lower()):    # also removes "º" (base 0)
            case "i"   | "tonic":                   self._unit = 1
            case "ii"  | "supertonic":              self._unit = 2
            case "iii" | "mediant":                 self._unit = 3
            case "iv"  | "subdominant":             self._unit = 4
            case "v"   | "dominant":                self._unit = 5
            case "vi"  | "submediant":              self._unit = 6
            case "vii" | "leading tone":            self._unit = 7

class Sharp(PitchParameter):  # Sharp (#)
    """`Unit -> PitchParameter -> Sharp`

    A Sharp() sets a given Pitch as Sharped or not.
    
    Parameters
    ----------
    first : integer_like
        Accepts a boolean or a numeral (0 or 1) to set Sharp as true or false
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_sharps = len(re.findall(r"#", operand))
                    if total_sharps > 0:
                        self._unit = 1
            case _:
                super().__lshift__(operand)
        return self


class Flat(PitchParameter):   # Flat (b)
    """`Unit -> PitchParameter -> Flat`

    A Flat() sets a given Pitch as Flatten or not.
    
    Parameters
    ----------
    first : integer_like
        Accepts a boolean or a numeral (0 or 1) to set Flat as true or false
    """
    def __init__(self, *parameters):
        super().__init__(1)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                else:
                    total_flats = len(re.findall(r"b", operand))
                    if total_flats > 0:
                        self._unit = 1
            case _:
                super().__lshift__(operand)
        return self

class Order(Unit):

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     return Order.numberToName(self._unit)
                    case _:                         return super().__mod__(operand)
            case str():                 return Order.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     self.nameToNumber(operand._data)
                    case _:                         super().__lshift__(operand)
            case str():             self.nameToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _name_order: dict = {
        "None":         0,
        "Up":           1,
        "Down":         2,
        "UpDown":      3,
        "DownUp":      4,
        "Chaotic":      5
    }

    _order_name: dict = {
        0:              "None",
        1:              "Up",
        2:              "Down",
        3:              "UpDown",
        4:              "DownUp",
        5:              "Chaotic"
    }

    def nameToNumber(self, order: str = "Up"):
        # Convert input words to lowercase
        order_split = order.lower().split()
        # Iterate over the instruments list
        for key, value in Order._name_order.items():
            # Check if all input words are present in the order string
            if all(word in key.lower() for word in order_split):
                self._unit = value
                return

    @staticmethod
    def numberToName(number: int) -> str:
        if 0 <= number < len(Order._order_name):
            return Order._order_name[number]
        return "Unknown Order!"



class DrumKit(Unit):
    """`Unit -> DrumKit`

    Auxiliary object that represents the standard Midi Drum Kit.
    
    Parameters
    ----------
    first : integer_like or string_like
        Accepts a numeral (35 to 82) or a String like "Drum"
    """
    def __init__(self, *parameters):
        self._channel: int = 10
        super().__init__(35, *parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     return DrumKit.numberToName(self._unit)
                    case Channel():                 return operand._data << self._channel
                    case _:                         return super().__mod__(operand)
            case str():                 return DrumKit.numberToName(self._unit)
            case Channel():             return Channel(self._channel)
            case float():               return float(self._channel)
            case _:                     return super().__mod__(operand)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["channel"] = self.serialize(self._channel)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "channel" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._channel = self.deserialize(serialization["parameters"]["channel"])
        return self
        
    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     self.nameToNumber(operand._data)
                    case Channel():                 self._channel = operand._data._unit
                    case _:                         super().__lshift__(operand)
            case str():             self.nameToNumber(operand)
            case Channel():         self._channel = operand._unit
            case float():           self._channel = int(operand)
            case _:                 super().__lshift__(operand)
        return self

    _drum_kit: dict = {
        "Acoustic Bass Drum":       35,
        "Bass Drum 1":              36,
        "Side Stick":               37,
        "Acoustic Snare":           38,
        "Hand Clap":                39,
        "Electric Snare":           40,
        "Low Floor Tom":            41,
        "Closed Hi-Hat":            42,
        "High Floor Tom":           43,
        "Pedal Hi-Hat":             44,
        "Low Tom":                  45,
        "Open Hi-Hat":              46,
        "Low-Mid Tom":              47,
        "Hi-Mid Tom":               48,
        "Crash Cymbal 1":           49,
        "High Tom":                 50,
        "Ride Cymbal 1":            51,
        "Chinese Cymbal":           52,
        "Ride Bell":                53,
        "Tambourine":               54,
        "Splash Cymbal":            55,
        "Cowbell":                  56,
        "Crash Symbol 2":           57,
        "Vibraslap":                58,
        "Ride Cymbal 2":            59,
        "Hi Bongo":                 60,
        "Low Bongo":                61,
        "Mute Hi Conga":            62,
        "Open Hi Conga":            63,
        "Low Conga":                64,
        "High Timbale":             65,
        "Low Timbale":              66,
        "High Agogo":               67,
        "Low Agogo":                68,
        "Cabasa":                   69,
        "Maracas":                  70,
        "Short Whistle":            71,
        "Long Whistle":             72,
        "Short Guiro":              73,
        "Long Guiro":               74,
        "Calves":                   75,
        "Hi Wood Block":            76,
        "Low Wood Block":           77,
        "Mute Cuica":               78,
        "Open Cuica":               79,
        "Mute Triangle":            80,
        "Open Triangle":            81,
        "Shaker":                   82
    }

    def nameToNumber(self, name: str = "Snare"):
        # Convert input words to lowercase
        name_split = name.lower().split()
        # Iterate over the instruments list
        for key, value in DrumKit._drum_kit.items():
            # Check if all input words are present in the name string
            if all(word in key.lower() for word in name_split):
                self._unit = value
                return

    @staticmethod
    def numberToName(number: int) -> str:
        for key, value in DrumKit._drum_kit.items():
            if value == number:
                return key
        return "Unknown Drum Kit!"


class Boolean(Unit):
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

    # def __or__(self, operand: any) -> 'Boolean':
    #     operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
    #     match operand:
    #         case bool():
    #             return self._unit != 0 or operand
    #         case Boolean():
    #             return self._unit != 0 or operand._unit != 0
    #     return False

class Default(Boolean):
    pass

class Enable(Boolean):
    pass

class Disable(Boolean):
    pass

class Tied(Boolean):
    """`Unit -> Boolean -> Tied`

    Sets the respective Notes or descendent Elements as Tied.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set Tied as true or false
    """
    pass

class Quality(Boolean):
    pass

class Major(Quality):
    """`Unit -> Boolean -> Quality -> Major`

    Sets the respective Key Signature as Major, the default.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set as Major the Key Signature
    """
    pass

class Minor(Quality):
    """`Unit -> Boolean -> Quality -> Minor`

    Sets the respective Key Signature as minor.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set as minor the Key Signature
    """
    pass

class Natural(Boolean):     # Natural (n)
    """`Unit -> Boolean -> Natural`

    Sets the respective Pitch as Natural, in which case sharps and flats aren't applied.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set as Natural the Pitch
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                if len(operand) == 0:
                    self._unit = 0
                elif len(re.findall(r"n", operand)) > 0:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Dominant(Boolean):    # Flats the seventh
    """`Unit -> Boolean -> Dominant`

    Sets the respective Chord configuration by flatting the seventh key.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set as Dominant the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                operand = operand.replace("#", "").replace("b", "").lower()
                if operand.find("º") == -1 and len(re.findall(r"\d+", operand)) > 0 \
                    and re.sub(r'[^a-z]', '', operand) in {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'}:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Diminished(Boolean):  # Flats the third and the fifth
    """`Unit -> Boolean -> Diminished`

    Sets the respective Chord configuration by flatting the third and the fifth key.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set as Diminished the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.find("º") != -1 or operand.lower().find("dim") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Augmented(Boolean):   # Sharps the fifth
    """`Unit -> Boolean -> Augmented`

    Sets the respective Chord configuration by sharping the fifth key.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set as Augmented the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("aug") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Sus2(Boolean):        # Second instead of the third
    """`Unit -> Boolean -> Sus2`

    Sets the respective Chord configuration by replacing the third with the second degree.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set as Sus2 the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("sus2") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Sus4(Boolean):        # Fourth instead of the third
    """`Unit -> Boolean -> Sus4`

    Sets the respective Chord configuration by replacing the third with the fourth degree.
    
    Parameters
    ----------
    first : bool_like, integer_like
        Accepts a boolean or a numeral (0 or 1) to set as Sus4 the Chord
    """
    # CHAINABLE OPERATIONS
    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case str():
                self._unit = 0
                if operand.lower().find("sus4") != -1:
                    self._unit = 1
            case _: super().__lshift__(operand)
        return self

class Mode(Unit):
    """`Unit -> Mode`

    Mode() represents the different scales (e.g., Ionian, Dorian, Phrygian)
    derived from the degrees of the major scale.
    
    Parameters
    ----------
    first : integer_like or string_like
        A Mode Number varies from 1 to 7 with 1 being normally the default
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)         # By default the mode is 1 (1st)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     self.stringToNumber(operand._data)
                    case _:                         super().__lshift__(operand)
            case str():             self.stringToNumber(operand)
            case _:                 super().__lshift__(operand)
        self._unit = max(1, self._unit)
        return self

        # 1 - First, 2 - Second, 3 - Third, 4 - Fourth, 5 - Fifth, 6 - Sixth, 7 - Seventh,
        # 8 - Eighth, 9 - Ninth, 10 - Tenth, 11 - Eleventh, 12 - Twelfth, 13 - Thirteenth,
        # 14 - Fourteenth, 15 - Fifteenth, 16 - Sixteenth, 17 - Seventeenth, 18 - Eighteenth,
        # 19 - Nineteenth, 20 - Twentieth.

    _modes_str = ["None" , "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]

    def stringToNumber(self, string: str):
        match string.strip().lower():
            case '1'  | "1st":              self._unit = 1
            case '2'  | "2nd":              self._unit = 2
            case '3'  | "3rd":              self._unit = 3
            case '4'  | "4th":              self._unit = 4
            case '5'  | "5th":              self._unit = 5
            case '6'  | "6th":              self._unit = 6
            case '7'  | "7th":              self._unit = 7
            case '8'  | "8th":              self._unit = 8

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._modes_str[number % len(__class__._modes_str)]

class Size(Unit):
    """`Unit -> Size`

    Size() represents the size of the Chord, like "7th", "9th", etc, or
    as the total number of keys, like integer 3, representing a triad, the default.
    
    Parameters
    ----------
    first : integer_like or string_like
        A Size Number varies from "1st" to "13th" with "3rd" being the triad default
    """
    def __init__(self, *parameters):
        super().__init__(3, *parameters)         # Default Size is 3
            
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case str():         return __class__.numberToString(self._unit)
            case _:             return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     self.stringToNumber(operand._data)
                    case _:                         super().__lshift__(operand)
            case str():             self.stringToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _types_str = ["None" , "1st", "3rd", "5th", "7th", "9th", "11th", "13th"]

    def stringToNumber(self, string: str):
        size = re.findall(r"\d+", string)
        if len(size) > 0:
            match size[0].lower():
                case '1'  | "1st":              self._unit = 1
                case '3'  | "3rd":              self._unit = 2
                case '5'  | "5th":              self._unit = 3
                case '7'  | "7th":              self._unit = 4
                case '9'  | "9th":              self._unit = 5
                case '11' | "11th":             self._unit = 6
                case '13' | "13th":             self._unit = 7

    @staticmethod
    def numberToString(number: int) -> str:
        return __class__._types_str[number % len(__class__._types_str)]

class Divisions(Unit):
    """`Unit -> Divisions`

    A Divisions() is used in conjugation with a Tuplet as not the usual 3 of the Triplet.
    
    Parameters
    ----------
    first : integer_like
        The amount of notes grouped together with the default of 3 (Triplet)
    """
    def __init__(self, *parameters):
        super().__init__(3, *parameters)

class ScaleOperation(Unit):
    pass

class Transposition(ScaleOperation):
    """`Unit -> ScaleOperation -> Transposition`

    A Transposition() is used to do a modal Transposition along a given Scale.
    
    Parameters
    ----------
    first : integer_like
        Transposition along the given Scale with 1 ("1st") as the default mode
    """
    def __init__(self, tones: int = 5):
        super().__init__(tones)

class Modulation(ScaleOperation):    # Modal Modulation
    """`Unit -> ScaleOperation -> Modulation`

    A Modulation() is used to return a modulated Scale from a given Scale or Scale.
    
    Parameters
    ----------
    first : integer_like
        Modulation of a given Scale with 1 ("1st") as the default mode
    """
    def __init__(self, mode: int | str = None):
        unit = Mode(mode)._unit
        super().__init__(unit)

class Modulate(ScaleOperation):    # Modal Modulation
    """`Unit -> ScaleOperation -> Modulate`

    Modulate() is used to modulate the self Scale or Scale.
    
    Parameters
    ----------
    first : integer_like
        Modulate a given Scale to 1 ("1st") as the default mode
    """
    def __init__(self, mode: int | str = None):
        unit = Mode(mode)._unit
        super().__init__(unit)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.T) -> o.T:
        import operand_generic as og
        if isinstance(operand, og.Scale):
            operand = operand.copy().modulate(self._unit)
            return operand
        else:
            return super().__rrshift__(operand)

class Progression(ScaleOperation):
    """`Unit -> ScaleOperation -> Progression`

    A Progression() is used to do a Progression along a given Scale.
    
    Parameters
    ----------
    first : integer_like
        Accepts a numeral equivalent to the the Roman numerals,
        1 instead of I, 4 instead of IV and 5 instead of V
    """
    def __init__(self, unit: int = None):
        super().__init__(unit)

class Inversion(ScaleOperation):
    """`Unit -> ScaleOperation -> Inversion`

    Inversion() sets the degree of inversion of a given chord.
    
    Parameters
    ----------
    first : integer_like
        Inversion sets the degree of chords inversion starting by 0 meaning no inversion
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)

class Midi(Unit):
    """`Unit -> Midi`

    """
    pass

class PPQN(Midi):
    """`Unit -> Midi -> PPQN`

    PPQN() represent Pulses Per Quarter Note for Midi clock.
    
    Parameters
    ----------
    first : integer_like
        The typical and the default value is 24, but it can be set multiples of 24
    """
    def __init__(self, *parameters):
        super().__init__(24, *parameters)

class MidiTrack(Midi):
    """`Unit -> Midi -> MidiTrack`

    A MidiTrack() is how arrangements are split in multiple compositions in Midi files.
    
    Parameters
    ----------
    first : integer_like
        For a given track concerning a composition, there default is 1.
    second : string_like
        The name of the Track, there default is "Track 1".
    """
    def __init__(self, *parameters):
        self._name: str = "Track 1"
        super().__init__(1, *parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case TrackNumber():         return operand._data << od.DataSource(self._unit)
                    case od.TrackName():        return operand._data << od.DataSource(self._name)
                    case str():                 return self._name
                    case _:                     return super().__mod__(operand)
            case TrackNumber():         return TrackNumber(self._unit)
            case od.TrackName():        return od.TrackName(self._name)
            case str():                 return self._name
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        import operand_generic as og
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) and self._name == other._name
            case TrackNumber():
                return self._unit == other._unit
            case od.TrackName():
                return self._unit == other._data
            case str():
                return self._name == other
            case _:
                return super().__eq__(other)    # Compares the _unit integer value
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["name"] = self._name        # It's a string already
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "name" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._name = serialization["parameters"]["name"]    # It's a string already
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case MidiTrack():
                super().__lshift__(operand)
                self._name = operand._name
            case od.DataSource():
                match operand._data:
                    case TrackNumber():         self._unit = operand._data._unit
                    case od.TrackName():        self._name = operand._data._data
                    case str():                 self._name = operand._data
                    case _:                     super().__lshift__(operand)
            case TrackNumber():         self._unit = operand._unit
            case od.TrackName():        self._name = operand._data
            case str():                 self._name = operand
            case _:                     super().__lshift__(operand)
        return self

class TrackNumber(Midi):
    def __init__(self, *parameters):
        super().__init__(1, *parameters)         # By default is Track number 1

class Channel(Midi):
    """`Unit -> Midi -> Channel`

    A Channel() is an identifier normally associated to an instrument in a given midi device.
    
    Parameters
    ----------
    first : integer_like
        For a given device, there are 16 channels ranging from 1 to 16
    """
    def __init__(self, *parameters):
        super().__init__(1, *parameters)         # By default is channel 1

class Velocity(Midi):
    """`Unit -> Midi -> Velocity`

    Velocity() represents the velocity or strength by which a key is pressed.
    
    Parameters
    ----------
    first : integer_like
        A key velocity varies from 0 to 127
    """
    def __init__(self, *parameters):
        super().__init__(100, *parameters)         # By default is velocity 100

class Pressure(Midi):
    """`Unit -> Midi -> Pressure`

    Pressure() represents the intensity with which a key is pressed after being down.
    
    Parameters
    ----------
    first : integer_like
        A key pressure varies from 0 to 127
    """
    pass

class Bend(Midi):
    """`Unit -> Midi -> Bend`

    Bend() sets the bending of the pitch to be associated to the PitchBend() Element.
    
    Parameters
    ----------
    first : integer_like
        Pitch bending where 0 is no bending and other values from -8192 to 8191 are the intended bending,
        this bending is 2 semi-tones bellow or above respectively
    """
    pass

class Program(Midi):
    """`Unit -> Midi -> Program`

    Program() represents the Program Number associated to a given Instrument.
    
    Parameters
    ----------
    first : integer_like or string_like
        A Program Number varies from 0 to 127 or it's known name like "Piano"
    """
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     return Program.numberToName(self._unit)
                    case _:                         return super().__mod__(operand)
            case str():                 return Program.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     self.nameToNumber(operand._data)
                    case _:                         super().__lshift__(operand)
            case str():             self.nameToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _instruments = [
                                                                            # Piano
        {   "midi_instrument": 0,   "names": ["Acoustic grand piano", "Piano"]    },
        {   "midi_instrument": 1,   "names": ["Bright acoustic piano"]    },
        {   "midi_instrument": 2,   "names": ["Electric grand piano"]    },
        {   "midi_instrument": 3,   "names": ["Honky tonk piano"]    },
        {   "midi_instrument": 4,   "names": ["Electric piano 1"]    },
        {   "midi_instrument": 5,   "names": ["Electric piano 2"]    },
        {   "midi_instrument": 6,   "names": ["Harpsicord"]    },
        {   "midi_instrument": 7,   "names": ["Clavinet"]    },
                                                                            # Chromatic percussion
        {   "midi_instrument": 8,   "names": ["Celesta", "Chromatic percussion"]    },
        {   "midi_instrument": 9,   "names": ["Glockenspiel"]    },
        {   "midi_instrument": 10,  "names": ["Music box"]    },
        {   "midi_instrument": 11,  "names": ["Vibraphone"]    },
        {   "midi_instrument": 12,  "names": ["Marimba"]    },
        {   "midi_instrument": 13,  "names": ["Xylophone"]    },
        {   "midi_instrument": 14,  "names": ["Tubular bell"]    },
        {   "midi_instrument": 15,  "names": ["Dulcimer"]    },
                                                                            # Organ
        {   "midi_instrument": 16,  "names": ["Hammond", "Drawbar organ", "Organ"]    },
        {   "midi_instrument": 17,  "names": ["Percussive organ"]    },
        {   "midi_instrument": 18,  "names": ["Rock organ"]    },
        {   "midi_instrument": 19,  "names": ["Church organ"]    },
        {   "midi_instrument": 20,  "names": ["Reed organ"]    },
        {   "midi_instrument": 21,  "names": ["Accordion"]    },
        {   "midi_instrument": 22,  "names": ["Harmonica"]    },
        {   "midi_instrument": 23,  "names": ["Tango accordion"]    },
                                                                            # Guitar
        {   "midi_instrument": 24,  "names": ["Nylon string acoustic guitar", "Guitar"]    },
        {   "midi_instrument": 25,  "names": ["Steel string acoustic guitar"]    },
        {   "midi_instrument": 26,  "names": ["Jazz electric guitar"]    },
        {   "midi_instrument": 27,  "names": ["Clean electric guitar"]    },
        {   "midi_instrument": 28,  "names": ["Muted electric guitar"]    },
        {   "midi_instrument": 29,  "names": ["Overdriven guitar"]    },
        {   "midi_instrument": 30,  "names": ["Distortion guitar"]    },
        {   "midi_instrument": 31,  "names": ["Guitar harmonics"]    },
                                                                            # Bass
        {   "midi_instrument": 32,  "names": ["Acoustic bass", "Bass"]    },
        {   "midi_instrument": 33,  "names": ["Fingered electric bass"]    },
        {   "midi_instrument": 34,  "names": ["Picked electric bass"]    },
        {   "midi_instrument": 35,  "names": ["Fretless bass"]    },
        {   "midi_instrument": 36,  "names": ["Slap bass 1"]    },
        {   "midi_instrument": 37,  "names": ["Slap bass 2"]    },
        {   "midi_instrument": 38,  "names": ["Synth bass 1"]    },
        {   "midi_instrument": 39,  "names": ["Synth bass 2"]    },
                                                                            # Strings
        {   "midi_instrument": 40,  "names": ["Violin", "Strings"]    },
        {   "midi_instrument": 41,  "names": ["Viola"]    },
        {   "midi_instrument": 42,  "names": ["Cello"]    },
        {   "midi_instrument": 43,  "names": ["Contrabass"]    },
        {   "midi_instrument": 44,  "names": ["Tremolo strings"]    },
        {   "midi_instrument": 45,  "names": ["Pizzicato strings"]    },
        {   "midi_instrument": 46,  "names": ["Orchestral strings", "Harp"]    },
        {   "midi_instrument": 47,  "names": ["Timpani"]    },
                                                                            # Ensemble
        {   "midi_instrument": 48,  "names": ["String ensemble 1", "Ensemble"]    },
        {   "midi_instrument": 49,  "names": ["String ensemble 2", "Slow strings"]    },
        {   "midi_instrument": 50,  "names": ["Synth strings 1"]    },
        {   "midi_instrument": 51,  "names": ["Synth strings 2"]    },
        {   "midi_instrument": 52,  "names": ["Choir aahs"]    },
        {   "midi_instrument": 53,  "names": ["Voice oohs"]    },
        {   "midi_instrument": 54,  "names": ["Synth choir", "Voice"]    },
        {   "midi_instrument": 55,  "names": ["Orchestra hit"]    },
                                                                            # Brass
        {   "midi_instrument": 56,  "names": ["Trumpet", "Brass"]    },
        {   "midi_instrument": 57,  "names": ["Trombone"]    },
        {   "midi_instrument": 58,  "names": ["Tuba"]    },
        {   "midi_instrument": 59,  "names": ["Muted trumpet"]    },
        {   "midi_instrument": 60,  "names": ["French horn"]    },
        {   "midi_instrument": 61,  "names": ["Brass ensemble"]    },
        {   "midi_instrument": 62,  "names": ["Synth brass 1"]    },
        {   "midi_instrument": 63,  "names": ["Synth brass 2"]    },
                                                                            # Reed
        {   "midi_instrument": 64,  "names": ["Soprano sax", "Reed"]    },
        {   "midi_instrument": 65,  "names": ["Alto sax"]    },
        {   "midi_instrument": 66,  "names": ["Tenor sax"]    },
        {   "midi_instrument": 67,  "names": ["Baritone sax"]    },
        {   "midi_instrument": 68,  "names": ["Oboe"]    },
        {   "midi_instrument": 69,  "names": ["English horn"]    },
        {   "midi_instrument": 70,  "names": ["Bassoon"]    },
        {   "midi_instrument": 71,  "names": ["Clarinet"]    },
                                                                            # Pipe
        {   "midi_instrument": 72,  "names": ["Piccolo", "Pipe"]    },
        {   "midi_instrument": 73,  "names": ["Flute"]    },
        {   "midi_instrument": 74,  "names": ["Recorder"]    },
        {   "midi_instrument": 75,  "names": ["Pan flute"]    },
        {   "midi_instrument": 76,  "names": ["Bottle blow", "Blown bottle"]    },
        {   "midi_instrument": 77,  "names": ["Shakuhachi"]    },
        {   "midi_instrument": 78,  "names": ["Whistle"]    },
        {   "midi_instrument": 79,  "names": ["Ocarina"]    },
                                                                            # Synth lead
        {   "midi_instrument": 80,  "names": ["Synth square wave", "Synth lead"]    },
        {   "midi_instrument": 81,  "names": ["Synth saw wave"]    },
        {   "midi_instrument": 82,  "names": ["Synth calliope"]    },
        {   "midi_instrument": 83,  "names": ["Synth chiff"]    },
        {   "midi_instrument": 84,  "names": ["Synth charang"]    },
        {   "midi_instrument": 85,  "names": ["Synth voice"]    },
        {   "midi_instrument": 86,  "names": ["Synth fifths saw"]    },
        {   "midi_instrument": 87,  "names": ["Synth brass and lead"]    },
                                                                            # Synth pad
        {   "midi_instrument": 88,  "names": ["Fantasia", "New age", "Synth pad"]    },
        {   "midi_instrument": 89,  "names": ["Warm pad"]    },
        {   "midi_instrument": 90,  "names": ["Polysynth"]    },
        {   "midi_instrument": 91,  "names": ["Space vox", "Choir"]    },
        {   "midi_instrument": 92,  "names": ["Bowed glass"]    },
        {   "midi_instrument": 93,  "names": ["Metal pad"]    },
        {   "midi_instrument": 94,  "names": ["Halo pad"]    },
        {   "midi_instrument": 95,  "names": ["Sweep pad"]    },
                                                                            # Synth effects
        {   "midi_instrument": 96,  "names": ["Ice rain", "Synth effects"]    },
        {   "midi_instrument": 97,  "names": ["Soundtrack"]    },
        {   "midi_instrument": 98,  "names": ["Crystal"]    },
        {   "midi_instrument": 99,  "names": ["Atmosphere"]    },
        {   "midi_instrument": 100, "names": ["Brightness"]    },
        {   "midi_instrument": 101, "names": ["Goblins"]    },
        {   "midi_instrument": 102, "names": ["Echo drops", "Echoes"]    },
        {   "midi_instrument": 103, "names": ["Sci fi"]    },
                                                                            # Ethnic
        {   "midi_instrument": 104, "names": ["Sitar", "Ethnic"]    },
        {   "midi_instrument": 105, "names": ["Banjo"]    },
        {   "midi_instrument": 106, "names": ["Shamisen"]    },
        {   "midi_instrument": 107, "names": ["Koto"]    },
        {   "midi_instrument": 108, "names": ["Kalimba"]    },
        {   "midi_instrument": 109, "names": ["Bag pipe"]    },
        {   "midi_instrument": 110, "names": ["Fiddle"]    },
        {   "midi_instrument": 111, "names": ["Shanai"]    },
                                                                            # Percussive
        {   "midi_instrument": 112, "names": ["Tinkle bell", "Percussive"]    },
        {   "midi_instrument": 113, "names": ["Agogo"]    },
        {   "midi_instrument": 114, "names": ["Steel drums"]    },
        {   "midi_instrument": 115, "names": ["Woodblock"]    },
        {   "midi_instrument": 116, "names": ["Taiko drum"]    },
        {   "midi_instrument": 117, "names": ["Melodic tom"]    },
        {   "midi_instrument": 118, "names": ["Synth drum"]    },
        {   "midi_instrument": 119, "names": ["Reverse cymbal"]    },
                                                                            # Sound effects
        {   "midi_instrument": 120, "names": ["Guitar fret noise", "Sound effects"]    },
        {   "midi_instrument": 121, "names": ["Breath noise"]    },
        {   "midi_instrument": 122, "names": ["Seashore"]    },
        {   "midi_instrument": 123, "names": ["Bird tweet"]    },
        {   "midi_instrument": 124, "names": ["Telephone ring"]    },
        {   "midi_instrument": 125, "names": ["Helicopter"]    },
        {   "midi_instrument": 126, "names": ["Applause"]    },
        {   "midi_instrument": 127, "names": ["Gunshot"]    }
    ]

    def nameToNumber(self, name: str = "Piano"):
        # Convert input words to lowercase
        name_split = name.lower().split()
        # Iterate over the instruments list
        for instrument in Program._instruments:
            for instrument_name in instrument["names"]:
                # Check if all input words are present in the name string
                if all(word in instrument_name.lower() for word in name_split):
                    self._unit = instrument["midi_instrument"]
                    return

    @staticmethod
    def numberToName(number: int) -> str:
        for instrument in Program._instruments:
            if instrument["midi_instrument"] == number:
                return instrument["names"][0]
        return "Unknown instrument!"

# For example, if the pitch bend range is set to ±2 half-tones (which is common), then:
#     8192 (center value) means no pitch change.
#     0 means maximum downward bend (−2 half-tones).
#     16383 means maximum upward bend (+2 half-tones).

#        bend down    center      bend up
#     0 |<----------- |8192| ----------->| 16383
# -8192                   0                 8191
# 14 bits resolution (MSB, LSB). Value = 128 * MSB + LSB
# min : The maximum negative swing is achieved with data byte values of 00, 00. Value = 0
# center: The center (no effect) position is achieved with data byte values of 00, 64 (00H, 40H). Value = 8192
# max : The maximum positive swing is achieved with data byte values of 127, 127 (7FH, 7FH). Value = 16384

class Value(Midi):
    """`Unit -> Midi -> Value`

    Value() represents the Control Change value that is sent via Midi
    
    Parameters
    ----------
    first : integer_like
        The Value shall be set from 0 to 127 accordingly to the range of CC Midi values
    """
    pass

class Number(Midi):
    """`Unit -> Midi -> Number`

    Number() represents the number of the Control to be manipulated with the Value values.
    
    Parameters
    ----------
    first : integer_like and string_like
        Allows the direct set with a number or in alternative with a name relative to the Controller
    """
    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():       return super().__mod__(operand)
            case str():                 return Number.numberToName(self._unit)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        import operand_rational as ra
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand._data:
                    case str():                     self.nameToNumber(operand._data)
                    case _:                         super().__lshift__(operand)
            case str():             self.nameToNumber(operand)
            case _:                 super().__lshift__(operand)
        return self

    _controllers = [
        {   "midi_number": 0,   "default_value": 0,     "names": ["Bank Select"]    },
        {   "midi_number": 1,   "default_value": 0,     "names": ["Modulation Wheel", "Modulation"]    },
        {   "midi_number": 2,   "default_value": 0,     "names": ["Breath Controller"]    },
        
        {   "midi_number": 4,   "default_value": 0,     "names": ["Foot Controller", "Foot Pedal"]    },
        {   "midi_number": 5,   "default_value": 0,     "names": ["Portamento Time"]    },
        {   "midi_number": 6,   "default_value": 0,     "names": ["Data Entry MSB"]    },
        {   "midi_number": 7,   "default_value": 100,   "names": ["Main Volume"]    },
        {   "midi_number": 8,   "default_value": 64,    "names": ["Balance"]    },
        
        {   "midi_number": 10,  "default_value": 64,    "names": ["Pan"]    },
        {   "midi_number": 11,  "default_value": 0,     "names": ["Expression"]    },
        {   "midi_number": 12,  "default_value": 0,     "names": ["Effect Control 1"]    },
        {   "midi_number": 13,  "default_value": 0,     "names": ["Effect Control 2"]    },
        
        {   "midi_number": 64,  "default_value": 0,     "names": ["Sustain", "Damper Pedal"]    },
        {   "midi_number": 65,  "default_value": 0,     "names": ["Portamento"]    },
        {   "midi_number": 66,  "default_value": 0,     "names": ["Sostenuto"]    },
        {   "midi_number": 67,  "default_value": 0,     "names": ["Soft Pedal"]    },
        {   "midi_number": 68,  "default_value": 0,     "names": ["Legato Footswitch"]    },
        {   "midi_number": 69,  "default_value": 0,     "names": ["Hold 2"]    },
        {   "midi_number": 70,  "default_value": 0,     "names": ["Sound Variation"]    },
        {   "midi_number": 71,  "default_value": 0,     "names": ["Timbre", "Harmonic Content", "Resonance"]    },
        {   "midi_number": 72,  "default_value": 64,    "names": ["Release Time"]    },
        {   "midi_number": 73,  "default_value": 64,    "names": ["Attack Time"]    },
        {   "midi_number": 74,  "default_value": 64,    "names": ["Brightness", "Frequency Cutoff"]    },

        {   "midi_number": 84,  "default_value": 0,     "names": ["Portamento Control"]    },

        {   "midi_number": 91,  "default_value": 0,     "names": ["Reverb"]    },
        {   "midi_number": 92,  "default_value": 0,     "names": ["Tremolo"]    },
        {   "midi_number": 93,  "default_value": 0,     "names": ["Chorus"]    },
        {   "midi_number": 94,  "default_value": 0,     "names": ["Detune"]    },
        {   "midi_number": 95,  "default_value": 0,     "names": ["Phaser"]    },
        {   "midi_number": 96,  "default_value": 0,     "names": ["Data Increment"]    },
        {   "midi_number": 97,  "default_value": 0,     "names": ["Data Decrement"]    },

        {   "midi_number": 120, "default_value": 0,     "names": ["All Sounds Off"]    },
        {   "midi_number": 121, "default_value": 0,     "names": ["Reset All Controllers"]    },
        {   "midi_number": 122, "default_value": 127,   "names": ["Local Control", "Local Keyboard"]    },
        {   "midi_number": 123, "default_value": 0,     "names": ["All Notes Off"]    },
        {   "midi_number": 124, "default_value": 0,     "names": ["Omni Off"]    },
        {   "midi_number": 125, "default_value": 0,     "names": ["Omni On"]    },
        {   "midi_number": 126, "default_value": 0,     "names": ["Mono On", "Monophonic"]    },
        {   "midi_number": 127, "default_value": 0,     "names": ["Poly On", "Polyphonic"]    }
    ]

    @staticmethod
    def getDefault(number: int) -> int:
        for controller in Number._controllers:
            if controller["midi_number"] == number:
                return controller["default_value"]
        return 0

    def nameToNumber(self, name: str = "Pan"):
        for controller in Number._controllers:
            for controller_name in controller["names"]:
                if controller_name.lower().find(name.strip().lower()) != -1:
                    self._unit = controller["midi_number"]
                    return

    @staticmethod
    def numberToName(number: int) -> str:
        for controller in Number._controllers:
            if controller["midi_number"] == number:
                return controller["names"][0]
        return "Unknown controller!"
