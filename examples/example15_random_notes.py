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
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

rest_play = (R, P)
staff << 120
Key() % str() >> Print()    # Returns the tonic key (I)

some_notes = N * Foreach(Modulus(20))**Pick(3, 4, 5, 6, 7)
some_notes << Foreach(Bouncer() * 10.15)**Get(int())**Pick(eight, quarter, dotted_eight, dotted_quarter) >> S
some_notes + Foreach(Flipper())**Get(int())**Formula(lambda n: (n * 5 + 4) % 3)**Multiply(2)
some_notes >> rest_play

some_notes = N * Foreach(Modulus(20))**Pick(3, 4, 5, 6, 7)
some_notes << Foreach(SinX() * 4.11)**Frequency(1, 4, 2, 1)**Pick(eight, quarter, dotted_eight, dotted_quarter) >> S
some_notes << Foreach(SinX() * 100)**Until(5, 1, 5)**Pick(O3, O4, O5) << Foreach(SinX())**Pick(C, D, E, F, G, A, B)
some_notes >> rest_play

