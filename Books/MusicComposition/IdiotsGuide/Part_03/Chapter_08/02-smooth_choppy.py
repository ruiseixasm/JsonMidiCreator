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

settings << KeySignature("b")

dotted_note = Dotted(1/2)
note_value = Duration(Dotted(1/2))
print(dotted_note == note_value)

smoothly: Clip = Note("F", 1/8) * 3 << Nth(3)**Duration(Dotted(1/2))
smoothly *= 3
smoothly += Note("F")
smoothly >> Stack() >> Link()
smoothly += Rest(1/8, Position(Measures(3) - Beats(1))) + Note("F", 1/8) >> Stack()
smoothly << Match(Steps(Duration(1/8)))**Gate(1) >> Link()
smoothly + Type(Note())**Foreach("iii", "ii", "ii", "iii", -3, -3, "i", -2, -2, -3, "ii")**Degree()
smoothly >> Rest() >> Play()

choppier = smoothly - (smoothly | Beats(1)) << Gate(0.90) << Match(Measures(3))**NoteValue(1/8) >> Link()
choppier >> Rest() >> Play()
