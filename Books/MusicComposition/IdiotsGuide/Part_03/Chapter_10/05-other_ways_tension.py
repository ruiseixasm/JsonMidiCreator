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
Key() % str() >> Print()
notes_B     = Note("B") * 3 << Foreach((0), (0, Beats(2)), (1, Beats(1)))**Position()
notes_A     = Note("A") * 2 << Foreach(Position(0, Beats(1)), Position(1, Beats(2)))
notes_C5    = Note("C", 5) * 2 << Foreach(Position(0, Beats(3)), Position(2))
notes_D5    = Note("D", 5) * 3 << Foreach(Position(1), Position(1, Beats(3)), Position(2, Beats(2)))
notes_E     = Note("E") * 1 << Position(2, Beats(1))
notes_F5    = Note("F", 5) * 1 << Position(2, Beats(3))
notes_G     = Note("G") * 1 << Position(3)
notes_G5    = Note("G", 5) * 1 << Position(3, Beats(1))
notes_E5    = Note("E", 5) * 1 << Position(3, Beats(2))
notes = notes_B + notes_A + notes_C5 + notes_D5 + notes_E + notes_F5 + notes_G + notes_G5 + notes_E5 >> Link()

notes >> Rest() >> Play()

staff << ""
Key() % str() >> Print()    # Prints the Tonic for the given Key Signature
rising = Note() * 13 << Foreach(A, G, A, B, C, B, C, D, E, D, E, F, G) >> Link() >> Smooth()
rising >> Rest() >> Play()

staff << "b"
Key() % str() >> Print()    # Prints the Tonic for the given Key Signature
slower = Note() * 6 << half >> Stack() << Nth(5, 6)**M4 << Foreach(A, D, G, C, G, (C, 5)) >> Link()
faster = Note() * 10 << M3 << sixteenth << Nth(2, 3, 4)**eight << Nth(1)**quarter >> S << Foreach(F, B, A, G, A, B, A, G, A, F)
slower + faster >> L >> R >> P

staff << ""
Key() % str() >> Print()    # Prints the Tonic for the given Key Signature
syncopation = Note() * 16 << Greater(M1)**Foreach(quarter, eight, eight, dotted_quarter, eight, eight, quarter, eight, eight, quarter, eight, whole) >> S
syncopation << Foreach(G, A, G, B, C, B, A, B, G, A, G, F, G, C, E, D) >> Smooth()
syncopation >> R >> P

staff << "#"
Key() % str() >> Print()    # Prints the Tonic for the given Key Signature
volume = Note() * 7 << half << Increment(12)**Velocity(30) >> S >> LJ << Foreach(D, A, B, F, G, C, B)
volume >> R >> P

staff << ""
Key() % str() >> Print()    # Prints the Tonic for the given Key Signature
sixteenth_group = Note() * 4 << sixteenth
dotted_rhythm = Note() * 3 << Foreach(sixteenth, sixteenth, eight)
duplet = Note() * 2 << eight
dotted_rhythm >> N >> dotted_rhythm >> N >> Print()
melodic_line = \
    dotted_rhythm >> N >> dotted_rhythm >> N >> \
    dotted_rhythm >> sixteenth_group >> dotted_rhythm >> sixteenth_group >> \
    duplet >> dotted_rhythm % Reverse() >> sixteenth_group >> dotted_rhythm >> \
    sixteenth_group * 2 >> (N << half)
melodic_line % M1 << Foreach(B, C, B, A)
melodic_line % M2 % B1 << Foreach(G, A, G)
melodic_line % M2 % B2 << Increment()**F
melodic_line % M2 % B3 << Increment(-1)**C
melodic_line % M2 % B4 << Increment()**G
melodic_line % M3 % B1 << Foreach((D, 5), G)
melodic_line % M3 % B2 << Increment()**A
melodic_line % M3 % B3 << Foreach(D, F, E, C)
melodic_line % M3 % B4 << Foreach(D, C, D)
melodic_line % M4 << Foreach((G, 5), E, C, G, B, G, E, B, A)

melodic_line % M1 >> Smooth()
melodic_line % M2 >> Smooth()
melodic_line % M3 % Greater(B1) >> Smooth()
melodic_line % M4 >> Smooth()

melodic_line % M1 % Len() >> Print()
melodic_line % M2 % Len() >> Print()
melodic_line % M3 % Len() >> Print()
melodic_line % M4 % Len() >> Print()
melodic_line % M5 % Len() >> Print()
melodic_line % Len() >> Print()
melodic_line >> R >> P


