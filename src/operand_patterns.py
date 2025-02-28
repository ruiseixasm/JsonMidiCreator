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
from types import FunctionType
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
import operand_mutation as om
import operand_selection as os


class Patterns(o.Operand):
    pass


class Drums(Patterns):

    def four_on_the_floor(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Four on the Floor – A steady kick drum on every beat (1-2-3-4), common in house, disco, and techno."""
        pattern: oc.Clip = oe.Note(kick) * 4
        pattern += oe.Note(snare, ra.Duration(1/2)) * 2 + ra.Beats(1)
        pattern += oe.Note(hi_hats) * 4 + ra.Beats(1/2)
        return pattern << ra.Duration(1/16)


    def boom_bap(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Boom Bap – A classic hip-hop groove with a strong snare hit on beats 2 and 4, and syncopated kick patterns."""
        pattern: oc.Clip = oe.Note(kick, 1/2) * 2
        pattern += oe.Note(snare, ra.Duration(1/2)) * 2 + ra.Beats(1) << ou.Velocity(110)
        swung: oc.Clip = (oe.Note(hi_hats, 1/8) * 8) * (oe.Note(hi_hats, 1/16) * 16)
        return pattern * 2 + swung << ra.Duration(1/16)


    def backbeat(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Backbeat – A rock and pop staple with the snare drum emphasizing beats 2 and 4, while the kick supports the rhythm."""
        pattern: oc.Clip = oe.Note(kick, 1/2) * 2
        pattern += oe.Note(snare, ra.Duration(1/2)) * 2 + ra.Beats(1) << ou.Velocity(120)
        pattern += oe.Note(hi_hats, 1/16) * 16
        return pattern << ra.Duration(1/16)


    def half_time_groove(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Half-Time Groove – Slower-feeling pattern with snare on beat 3, often used in hip-hop, trap, and metal breakdowns."""
        pattern: oc.Clip = oe.Note(kick, 1/16) * 1
        pattern += oe.Note(snare, 1/16) * 1 + ra.Beats(2)
        pattern += oe.Note3(hi_hats, 1/8) * 4   # Note3 triplets means that for 1/8 it takes 1/4 total length
        return pattern


    def d_beat(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """D-Beat – A fast punk/hardcore beat with alternating kick and snare hits, driving an aggressive rhythm."""
        pattern: oc.Clip = oe.Note(kick, 1/8) * 8 << ou.Velocity(75)
        pattern += oe.Note(snare, 1/8) * 8 + ra.Beats(1/4)  # Alternates one Step only, 1/4 of a Beat
        pattern += oe.Note(hi_hats, 1/16) * 16
        return pattern << ra.Duration(1/16)


    def reggae_one_drop(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                rimshot = ou.DrumKit("Electric Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Reggae One Drop – Snare (or rimshot) and kick on beat 3, with hi-hat or guitar skank filling the space."""
        pattern: oc.Clip = oe.Note(kick, 1/16) * 1 << ou.Beat(2)    # Beat starts on 0
        pattern += oe.Note(rimshot, 1/16) * 1 << ou.Beat(2)    # Beat starts on 0
        pattern += oe.Note(hi_hats) * 4 + ra.Beats(1/2)
        return pattern << ra.Duration(1/16)


    def funk_shuffle(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Funk Shuffle – A swung groove with syncopated hi-hat and ghost snare notes, adding a "rolling" feel."""
        pattern: oc.Clip = oe.Note(kick, 1/2) * 2 + ra.Beats(1) << ra.Duration(1/16)
        pattern += oe.Note(snare, 1/2) * 2 + ra.Beats(1) << ra.Duration(1/16)
        pattern += oe.Note3(hi_hats, 1/8) * 4 + ra.Beats(1/2)   # Note3 triplets means that for 1/8 it takes 1/4 total length
        return pattern



