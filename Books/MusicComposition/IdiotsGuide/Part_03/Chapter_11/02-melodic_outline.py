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


settings << 60.0 << ""
Key() % str() >> Print()
chords = Chord(1/1) * 3 << Foreach(("C", Inversion(1)), ("Am", Inversion(2), Octave(3)), "F")
chords >> Rest >> P

settings << 120
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
original_melody >> Rest >> P

melodic_outline = original_melody % Steps(0) + original_melody % Measures(1) % Beats(2) >> LJ
melodic_outline >> Rest >> P

structural_tones = original_melody % Steps(0) + original_melody % Measures(1) % Beats(2) + original_melody % Measures(2) % Beats(2) >> LJ
structural_tones >> Rest >> P

chords = Chord(1/1) * 6
chords % Nth(2, 3, 4, 5) << 1/2
chords >> S << Foreach(C, "Am", "Em", "Dm", G, C)
chords >> Rest >> P
structural_tones + chords >> L >> Rest >> P
original_melody + chords >> L >> Rest >> P
