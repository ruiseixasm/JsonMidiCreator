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
import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '../../../../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

rest_play = ( Rest(), P)
settings << "#" << 120
Key() % str() >> Print()    # Returns the tonic key (I)

# Original Motif to work on its pitches
motif: Clip = Note() * 6 << Foreach(quarter, eight, eight, dotted_quarter, eight, whole) >> S
motif << Foreach(-3, 1, 2, 3, 2, -3)**Degree()

motif_left, motif_right = motif.copy().split(Position(M2))
new_material: Clip = Note() * 6 << Foreach(dotted_quarter, eight, dotted_quarter, eight, half, half) >> S
new_material << Foreach(-3, -2, -3, -2, 1, 2)**Degree() << Tied()

# Where the Variation pitch is generated (Foreach does iteration contrary to Subject)
expanded_rhythm = motif >> motif_left >> new_material >> motif_right
expanded_rhythm >> rest_play
