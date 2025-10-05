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


settings << "#"
Key() % str() >> Print()

single_notes = Note() * 12 << Nth(3, 4, 7, 10, 11, 12)**Foreach(dotted_quarter, eight, half, dotted_quarter, eight, whole) >> S
single_notes << Foreach(B, G, D, G, A, F, D, E, G, E, B, D) >> Smooth()
single_notes >> Rest >> P
chords = Chord() * 4 << 1/1
chords << Foreach(G, D, "Em", D)
chords >> Rest >> P
chords << Foreach(1, 5, 6, 5)**(Degree(), Mode())
chords >> Rest >> P
single_notes + chords >> Link() >> Rest >> P
chords + single_notes >> Link() >> Rest >> P

