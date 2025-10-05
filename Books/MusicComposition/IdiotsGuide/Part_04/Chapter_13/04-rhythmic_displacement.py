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

motif = Note() * 6 << Foreach(quarter, eight, eight, dotted_quarter, eight, whole) >> S
motif << Foreach(-3, 1, 2, 3, 2, -3)**Degree()
# motif >> rest_play

# rest_motif = R + motif % Copy() >> S >> LJ  # up a half-step
# rest_motif >> rest_play

displacing_motif = motif >> Rest + motif % Copy() >> S >> LJ  # up a half-step
displacing_motif % NoteValue() >> Print(0)
displacing_motif >> rest_play >> Render("Midi/displacing_motif.mid")

# Equivalent Staff notational format
displacing_motif = motif \
    >> ((Rest + motif % Copy() >> S) + Note(1/8, Degree(3), Position(M2, B1)) >> LJ >> Tie()) \
    >> S  # up a half-step
displacing_motif % NoteValue() >> Print(0)
displacing_motif >> rest_play
