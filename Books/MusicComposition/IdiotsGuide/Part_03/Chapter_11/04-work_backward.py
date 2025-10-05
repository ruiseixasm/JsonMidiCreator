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


settings << "b"
Key() % str() >> Print()

single_notes = Note() * 12 << Nth(1, 2, 5, 6, 7, 8, 9, 12)**Foreach(dotted_quarter, eight, dotted_quarter, eight, half, dotted_quarter, eight, whole) >> S
single_notes << Foreach(A, B, A, G, A, B, A, B, D, C, B, A) >> Smooth()
single_notes >> Rest >> P
chords = Chord() * 5 << 1/1 << Nth(3, 4)**(1/2) >> S
chords << Foreach(F, "Dm", "Gm", "C7", F)
chords >> Rest >> P
single_notes + chords >> L >> Rest >> P

