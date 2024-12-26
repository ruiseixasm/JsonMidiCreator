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

structural_tones: Sequence = Note("E", NoteValue(1)) * 4 + Foreach(0, 2, 2, 4)
chromatic_tones = Note("F#", Position(Beat(3))) + Note("Ab", Position(Measures(1), Beat(3))) + Note("A#", Position(Measures(2), Beat(3)))
structural_tones + chromatic_tones >> Link() << Get(Duration())**Duration() >> Rest() >> Play()

structural_tones = \
    Note("C", 5, Dotted(1/4)) + \
    Note("C", 5, Dotted(1/4), Position(Beat(2))) + \
    Note("G", 1/2, Position(Measures(1))) + \
    Note("F", Position(Measures(1), Beat(2))) + \
    Note("F", Dotted(1/2), Position(Measures(2))) + \
    Note("G", 1/1, Position(Measures(3))) >> Link()
blues_scale = \
    Note("C", 1/8, Position(Dotted(1/4))) + \
    Note("C", 1/8, Position(Dotted(2 * 1/4) + NoteValue(1/8))) + \
    Note("C", 1/4, Position(Measures(1) + NoteValue(1/2 + 1/4))) + \
    Note("C", 1/4, Position(Measures(2) + Dotted(1/2))) >> Link() << Scale("Blues")
blues_scale + Foreach(5, 3, 1, 3)
structural_tones + blues_scale >> Link() >> Rest() >> Play()

all_notes: Sequence = Note() * (3*3 + 1)
all_notes << Nth(1, 4, 7)**NoteValue(1/2) << Nth(10)**NoteValue(1) >> Stack()
all_notes << Greater(Beat(0))**Scale("Pentatonic")
all_notes + Foreach(Octave(1), 3, 4, Degree(5), 0, 1, Degree(3), 3, 4, Degree(5)) >> Rest() >> Play()
