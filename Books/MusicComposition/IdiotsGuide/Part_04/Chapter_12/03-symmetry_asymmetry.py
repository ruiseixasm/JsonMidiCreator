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

rest_play = (R, P)
staff << 140
K % str() >> Print()    # Returns the tonic key (I)

phrase_1 = N * 7 >> LJ
phrase_1 % Length() >> Print(0)
phrase_2 = N * 5 >> LJ
phrase_2 % Length() >> Print(0)
symmetrical = \
    (phrase_1 % Copy()  << Foreach(8, 5, 6, 7, 8, 9, 8)**Degree()   >> Slur()) + \
    (phrase_2 % Copy()  << Foreach(7, 8, 7, 6, 7)**Degree()         >> Slur()) + \
    (phrase_1 % Copy()  << Foreach(8, 5, 6, 7, 8, 9, 10)**Degree()  >> Slur()) >> S
symmetrical += symmetrical % Equal(M3, M4) % Copy() + 3
symmetrical >> S
symmetrical % Length() >> Print(0)
symmetrical >> rest_play

phrase_1 = N * 7 >> LJ  >> Slur()
phrase_2 = N * 8        >> Slur()
phrase_3 = N * 5 >> LJ  >> Slur()
asymmetrical = \
    (phrase_1 % Copy()  << Foreach(8, 5, 6, 7, 8, 9, 8)**Degree()) + \
    (phrase_2 % Copy()  << Foreach(7, 8, 7, 6, 7, 5, 6, 7)**Degree()) + \
    (phrase_3 % Copy()  << Foreach(8, 6, 7, 8, 9)**Degree()) + \
    (phrase_1 % Copy()  << Foreach(8, 5, 6, 7, 8, 9, 10)**Degree()) + \
    (phrase_3 % Copy()  << Foreach(10, 11, 10, 9, 10)**Degree()) >> S
asymmetrical % Length() >> Print(0)
asymmetrical >> rest_play