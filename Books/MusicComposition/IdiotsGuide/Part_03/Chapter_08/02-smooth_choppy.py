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

staff << KeySignature("b")

dotted_note = Dotted(1/2)
note_value = NoteValue(dotted_note)

smoothly: Sequence = Note("F", 1/8) * 3 << Nth(3)**NoteValue(Dotted(1/2))
smoothly *= 3
smoothly >> Print()
smoothly += Note("F")
smoothly >> Stack() >> Link(True)
smoothly += Rest(1/8, Position(Measure(3) - Beat(1))) + Note("F", 1/8) >> Stack()
smoothly >> Link(True)
smoothly >> Rest() >> Play()
