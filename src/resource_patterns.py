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

import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_label as ol
import operand_generic as og
import operand_element as oe
import operand_frame as of
import operand_container as oc
import operand_chaos as ch



class RP_Patterns:
    
    @staticmethod
    def four_on_the_floor(*parameters, measures: int = 4) -> 'oc.Clip':
        pattern: oc.Clip = oc.Clip(od.TrackName("Four on the Floor"), og.TimeSignature(4, 4), oe.Note(1/16), parameters)
        pattern *= measures       
        return pattern

    @staticmethod
    def west_side(*parameters, measures: int = 4) -> 'oc.Clip':
        pattern = oc.Clip(od.TrackName("West Side"), og.TimeSignature(3, 4))
        pattern += oe.Note(pattern, 1/8) / 6
        pattern /= oe.Note(pattern, 1/4) / 3
        pattern << of.Nth(1, 2, 3)**ou.Key("G")
        pattern << of.Nth(4, 5, 6)**(ou.Octave(5), ou.Key("C"))
        pattern << of.Nth(7, 8, 9)**of.Foreach("A", "F", "C")**ou.Key()
        return pattern * (measures // 2)


class RP_Mutation(RP_Patterns):
    pass

