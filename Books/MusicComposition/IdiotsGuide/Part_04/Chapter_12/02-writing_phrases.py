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


settings << "b" << 140
Key() % str() >> Print()    # Returns the tonic key (I)

phrase_1 = Note() * 6 << whole << Nth(1, 2, 3, 4)**Foreach(dotted_half, quarter, half, half) >> Stack() >> Slur(0.95)
phrase_1 << Foreach("iii", "ii", "iii", "IV", "iii", "I")**Degree() >> Tie()
phrase_2 = phrase_1 % Copy() << Foreach(-3, -2, 1, 2, 3, 3)**Degree()
phrase_4 = phrase_1 % Copy() << Foreach(3, 4, 3, 4, 3, 3)**Degree()
phrase_3 = phrase_1 % Equal(M1, M2) % Copy() \
    + (Note() * 4 << half << Nth(1, 2)**Foreach(dotted_half, quarter) << Foreach(5, 6, 5, 4)**Degree()) >> Stack()
(phrase_1, phrase_2, phrase_3, phrase_4, Rest) >> Play()
