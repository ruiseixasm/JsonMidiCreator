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


staff << 60.0 << ""
Key() % str() >> Print()
chords = Chord(1/1) * 3 << Foreach(("C", Inversion(1)), ("Am", Inversion(2), O3), "F")
chords >> R >> P

staff << 120
original_melody = Note() * 14 << Foreach(
    quarter, quarter, dotted_quarter, eight,
    eight, eight, eight, eight, half,
    quarter, quarter, dotted_quarter, eight,
    whole) >> S # Foreach requires Stacking!
original_melody << Foreach(
    (E, 5), F, E, D,
    C, D, E, D, E,
    D, E, D, C,
    C) >> Smooth()
original_melody >> R >> P

melodic_outline = original_melody % S1 + original_melody % M2 % B3 >> LJ
melodic_outline >> R >> P

structural_tones = original_melody % S1 + original_melody % M2 % B3 + original_melody % M3 % B3 >> LJ
structural_tones >> R >> P

chords = Chord(1/1) * 6
chords % Nth(2, 3, 4, 5) << 1/2
chords >> S << Foreach(C, "Am", "Em", "Dm", G, C)
chords >> R >> P
structural_tones + chords >> L >> R >> P
original_melody + chords >> L >> R >> P
