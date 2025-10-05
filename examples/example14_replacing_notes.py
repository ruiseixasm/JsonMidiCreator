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

settings << 160

replacing_notes = \
    (Note() * 3 << Foreach(1/2, 1/4, 1/4)**NoteValue() << Foreach(1, 5, 7)**Degree() << Foreach(None, None, Flat())) + \
    (Note() * 3 << Foreach(1/4, 1/2, 1/4)**NoteValue() << Foreach(8, 7, 5)**Degree() << Foreach(None, Flat(), None)) + \
    (Note() * 3 << Foreach(1/2, 1/4, 1/4)**NoteValue() << Foreach(1, 5, 3)**Degree() << Foreach(None, None, Flat())) + \
    (Note() * 4 << Foreach(1, -2, -4, -2)**Degree() << Foreach(None, Flat(), None, None)) \
    >> Stack()
replacing_notes % NoteValue() >> Print(0)
replacing_notes >> Rest >> Play()

replacing_notes >> Render("Midi/example_song.mid")
