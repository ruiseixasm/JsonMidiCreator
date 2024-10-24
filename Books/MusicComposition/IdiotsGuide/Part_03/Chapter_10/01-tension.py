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

two_tones = Note(1/1) * 2 << Foreach(4, 7)**Degree()
# two_tones >> Rest() >> Play()

tension = Note("A") * 4 + Note("A", 1/2) * 2 >> Stack()
tension = tension << Foreach(1, 7, 1, 2, 3, 2)**Degree() >> Smooth()
# tension >> Rest() >> Play()

single_notes = Note() * 5 << Foreach(
    (NoteValue(1/2), Octave(5)),
    "B",
    "A",
    (1/2, "B"),
    (1/2, "A")
) >> Stack()

chords = Chord() * 3 << Foreach(
    (1/1),
    (1/2, Degree(3), Mode(3)),
    (1/2, Degree(4), Mode(4))
) >> Stack()

single_notes + chords >> Link() >> Rest() >> Play()
