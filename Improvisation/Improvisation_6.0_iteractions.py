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

defaults << Tempo(90)

eight_notes = Note(Dotted(1/16)) * 7 << Nth(7)**Dotted(1/4) >> L
eight_notes[6] % Length() % Fraction() >> Print()


# Processing Degrees
chooser = Input(SinX() * 100)
degrees = Choice(1, 3, 5, 6)
pattern = UpDown([0, 1, 1, 1, 1, 1, 1], Degree)

for _ in range(80):
    eight_notes << chooser**degrees
    if eight_notes == pattern:
        eight_notes >> P
        R() >> P



