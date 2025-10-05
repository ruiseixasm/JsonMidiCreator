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


settings << 40
Key() % str() >> Print()

chords_F = Chord(1/1) * 7
chords_F << Foreach("Bdim", ("Dm", Inversion(2)), (F, Inversion(1)), "G7", "Em9", "CM11", ("Am13", Octave(3), Inversion(1)))
chords_F >> Rest >> P

staff_chords_F = Chord(1/1, []) * 7
staff_chords_F << Foreach("vii", "ii", "IV", "V", "iii", "I", "vi")**Degree()   # Sets the root notes
staff_chords_F << Foreach(3, 3, 3, 4, 5, 6, 7)**Size()
staff_chords_F << Nth(2, 3, 7)**Foreach(Inversion(2), Inversion(1), (Octave(3), Inversion(1)))
staff_chords_F >> Rest >> P
