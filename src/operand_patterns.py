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


    def breakbeat(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Breakbeat – A syncopated drum pattern, often sampled from funk and jazz, with offbeat snare hits."""
        pattern: oc.Clip = oe.Note(kick, 1/2) * 2 + ra.Beats(7/4) + oe.Note(kick, 1/2) * 2
        pattern += oe.Note(snare, 1/2) * 2 + ra.Beats(1)
        pattern += oe.Note(hi_hats, 1/16) * 16
        return pattern << ra.Duration(1/16)


    def bossa_nova(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Latin Clave Rhythms – Patterns like Son Clave and Rumba Clave, forming the backbone of Latin music grooves."""
        step: ra.Beats = ra.Beats(1/4)
        pattern: oc.Clip = oe.Note(kick, 0*step) + oe.Note(kick, 10*step) + oe.Note(kick, 24*step)
        pattern += oe.Note(snare, 6*step) + oe.Note(snare, 19*step)
        pattern += oe.Note(hi_hats, 3*step) + oe.Note(hi_hats, 9*step) + oe.Note(hi_hats, 16*step) \
                + oe.Note(hi_hats, 22*step) + oe.Note(hi_hats, 28*step)
        return pattern << ra.Duration(1/16)


    def blast_beat(self,
                kick = ou.DrumKit("Drum", ou.Channel(10)),
                snare = ou.DrumKit("Snare", ou.Channel(10)),
                hi_hats = ou.DrumKit("Hi-Hat", ou.Channel(10))
            ) -> oc.Clip:
        """Blast Beat – Extreme metal drumming technique with rapid, alternating kick and snare hits."""
        pattern: oc.Clip = oe.Note(kick, 1/8) * 8
        pattern += oe.Note(snare, 1/8) * 8 + ra.Beats(1/4)
        pattern += oe.Note(hi_hats, 1/16) * 16
        return pattern << ra.Duration(1/16)



class Melodies(Patterns):

    def sequence(self,
                measures: int = 2
            ) -> oc.Clip:
        """A short melody is repeated at different pitches while maintaining the same interval pattern."""
        pattern: oc.Clip = oe.Cluster([0, 2, 4, 6], 1/1) * measures + of.Iterate() # Increases one Degree on the second Measure
        return pattern << og.Arpeggio("Up", 1/4)


    def arpeggio(self,
                degrees: list[int] = [1, 5]
            ) -> oc.Clip:
        """Notes of a chord are played one at a time instead of simultaneously."""
        pattern: oc.Clip = oc.Clip()
        for degree in degrees:
            pattern += oe.Chord(ou.Degree(degree))
        pattern += of.Iterate()**ra.Measures() # Places the Chords in each Measure
        return pattern << ou.Size(4) << og.Arpeggio("Up", 1/4)


    def passing_tones(self,
                tonic = ou.Tonic("C")
            ) -> oc.Clip:
        """Melodic movement using smooth stepwise motion between strong chord tones."""
        pattern: oc.Clip = oe.Note(tonic) * 8 << of.Iterate(1)
        pattern << of.Nth(6, 7, 8)**of.Propagate(ou.Degree())
        pattern -= of.Nth(7, 8)**of.Iterate(1)
        return pattern


    def pedal_tones(self,
                tonic = ou.Tonic("C")
            ) -> oc.Clip:
        """Melodic movement using smooth stepwise motion between strong chord tones."""
        pattern: oc.Clip = oe.Note(tonic) * 8 << of.Iterate(1) << of.Nth(7, 8)**of.Foreach("G", "F")**ou.Key()
        return pattern

