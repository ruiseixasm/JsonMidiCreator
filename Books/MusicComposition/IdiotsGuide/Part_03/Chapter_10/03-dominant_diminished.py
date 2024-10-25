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

staff << Tempo(30)
sevenths = Chord(1/2) * 8
sevenths << Foreach(
    (Size("7th"),   Degree("V7")),
    (Size("5th"),   Degree("I"),    Inversion(2)),

    (Size("7th"),   Degree("IV7")),
    (Size("5th"),   Degree("bVII"), Inversion(2),   Octave(3)),

    (Size("7th"),   Degree("I7")),
    (Size("5th"),   Degree("IV"),   Inversion(2),   Octave(3)),

    (Size("7th"),   Degree("II7")),
    (Size("5th"),   Degree("V"),    Inversion(2),   Octave(3))
) >> Stack()
sevenths >> Rest() >> Play()

staff << Tempo(90)
single_notes = Note() * 6
single_notes << Foreach(
    ("G"),
    ("F"),
    ("G"),
    ("C", 5),
    (1/2, "B"),
    (1/2, "A")
) >> Stack()
single_notes >> Rest() >> Play()
chords = Chord() * 3
chords << Foreach(
    (1/1, Size(3), Degree("I")),
    (1/2, Size(3), Degree("V")),
    (1/2, Size("7th"), Degree("II"), Dominant())
) >> Stack()
chords >> Rest() >> Play()
single_notes + chords >> Link() >> Rest() >> Play()

staff << Tempo(30)
fifths = Chord(1/2) * 8
fifths << Foreach(
    (Degree("viiº")),
    (Degree("I"),       Octave(5)),

    (Degree("iiiº")),
    (Degree("IV")),

    (Degree("iiº")),
    (Degree("bIII")),

    (Degree("viº")),
    (Degree("bVII"))
) >> Stack()
fifths >> Rest() >> Play()

staff << Tempo(90)
single_notes = Note() * 7
single_notes << Foreach(
    ("C"),
    ("A"),
    ("G"),
    ("E"),
    ("F"),
    ("G"),
    (1/2, "Ab")
) >> Stack()
single_notes >> Rest() >> Play()
chords = Chord(1/2) * 4
chords << Foreach(
    (Degree("vi"),  Mode("6th")),
    (Degree("iii"), Mode("3rd")),
    (Degree("ii"),  Mode("2nd")),
    (Degree("IIº"), Diminished())
) >> Stack()
chords >> Rest() >> Play()
single_notes + chords >> Link() >> Rest() >> Play()

