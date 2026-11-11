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
from . import creator as c
from . import operand as o

from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_data as od
from . import operand_label as ol
from . import operand_generic as og
from . import operand_element as oe
from . import operand_frame as of
from . import operand_container as oc
from . import operand_chaos as ch
from . import operand_tamer as ot
from . import operand_process as op
from . import operand_action as oa
from . import operand_transformation as tr



root_clip = oc.Clip()
root_axes = [0] * 4

def four_measures_durations_and_degrees(clip: 'oc.Clip', axes: list[int]) -> 'oc.Clip':
    """
    Starts by setting the durations [1 / 2, 1 / 4, 1 / 8, 1 / 16] on each of the 4 Measures, and then sets the Degrees for each MEasure too.
    

    Axes
    ----
    Odd axes : Durations per Measure
    Even axes : Degrees per Measure
    """
    global root_clip, root_axes

    # Root stage for durations
    changed: bool = False
    for measure_i in range(4):
        if all(axis == 0 for axis in axes) or axes[measure_i * 2] != root_axes[measure_i]:
            setting_durations = tr.IChooseDuration(no_repeats=True)
            for _ in range(axes[measure_i * 2]):
                clip << of.Equal(ra.Measure(measure_i))**setting_durations
            root_axes[measure_i] = axes[measure_i * 2]
            root_clip << of.Equal(ra.Measure(measure_i))**(clip & ra.Measure(measure_i))
        else:
            clip << of.Equal(ra.Measure(measure_i))**(root_clip & ra.Measure(measure_i))

    # 2nd stage for degrees
    for measure_i in range(4):
        if axes[measure_i * 2 + 1] > 0:
            degrees = [ou.Degree()] * 10
            untamed = ot.Modulo() * (10 * axes[measure_i * 2 + 1])
            setting_degrees = untamed % degrees
            clip << of.Equal(ra.Measure(measure_i))**setting_degrees
    return clip


