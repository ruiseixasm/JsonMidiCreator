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

staff << "#"
K % str() >> Print()
notes_B     = Note("B") * 3 << Foreach((0), (0, Beat(2)), (1, Beat(1)))**Position()
notes_A     = Note("A") * 2 << Foreach(Position(0, Beat(1)), Position(1, Beat(2)))
notes_C5    = Note("C", 5) * 2 << Foreach(Position(0, Beat(3)), Position(2))
notes_D5    = Note("D", 5) * 3 << Foreach(Position(1), Position(1, Beat(3)), Position(2, Beat(2)))
notes_E     = Note("E") * 1 << Position(2, Beat(1))
notes_F5    = Note("F", 5) * 1 << Position(2, Beat(3))
notes_G     = Note("G") * 1 << Position(3)
notes_G5    = Note("G", 5) * 1 << Position(3, Beat(1))
notes_E5    = Note("E", 5) * 1 << Position(3, Beat(2))
notes = notes_B + notes_A + notes_C5 + notes_D5 + notes_E + notes_F5 + notes_G + notes_G5 + notes_E5 >> Link(True)

# notes >> Rest() >> Play()

staff << ""
K % str() >> Print()
rising = Note() * 13 << Foreach(A, G, A, B, C, B, C, D, E, D, E, F, G) >> Link(True) >> Smooth()
# rising >> Rest() >> Play()

staff << "b"
K % str() >> Print()
slower = N * 6 << half >> Stack() << Nth(5, 6)**M4 << Foreach(A, D, G, C, G, (C, 5)) >> Link()
faster = N * 10 << M3 << sixteenth << Nth(2, 3, 4)**eight << Nth(1)**quarter >> S << Foreach(F, B, A, G, A, B, A, G, A, F)
# slower + faster >> L >> R >> P

staff << ""
K % str() >> Print()
syncopation = N * 16 << Greater(M1)**Foreach(quarter, eight, eight, dotted_quarter, eight, eight, quarter, eight, eight, quarter, eight, whole) >> S
syncopation << Foreach(G, A, G, B, C, B, A, B, G, A, G, F, G, C, E, D) >> Smooth()
# syncopation >> R >> P

staff << "#"
K % str() >> Print()
volume = N * 7 << half << Foreach(60, 70, 80, 90, 100, 110, 120)**Velocity() >> S >> LJ << Foreach(D, A, B, F, G, C, B)
volume >> R >> P

