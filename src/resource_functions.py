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



class F_Rhythm:
    
    def four_on_the_floor(*parameters, measures: int = 4) -> oc.Clip:
        pattern: oc.Clip = oc.Clip(og.TimeSignature(4, 4), oe.Note(1/16), parameters)
        pattern *= measures       
        return pattern


class F_Pitch:
    pass

