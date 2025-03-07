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

suspended = Chord(1/1) * 2 << Loop(
    (Sus4()),
    ("C")
)
suspended >> Rest() >> Play()

suspended = Chord(1/2) * 8 << Loop(
    ("D", Scale("minor")),
    ("G"),
    ("E", Scale("minor")),
    ("A", Scale("minor")),
    ("F"),
    (1/4, "G", Sus4()),
    (1/4, "G"),
    (1/1)
) >> Stack()
suspended >> Rest() >> Play()
single_notes = Note(1/2) * 8 << Loop(
    ("A"),
    ("G"),
    ("B"),
    ("A"),
    (5),
    (1/4, 5),
    (1/4, "B"),
    (1/1, 5)
) >> Stack()
single_notes >> Rest() >> Play()
suspended + single_notes >> Link() >> Rest() >> Play()
