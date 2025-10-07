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

settings << KeySignature("#")
Scale(settings % KeySignature() % list()) % str() >> Print(0)

embellishing: Clip = Note("B") * 10 << Nth(3, 4, 5, 7, 8, 9, 10)**Foreach(1/2, 1/2, 1/2, Dotted(1/8), 1/16, 1/2, 1/1) >> Stack()
embellishing - Nth(4, 5, 10)**Foreach(Degree(4), Degree(2), Degree(5))  # Interpretation is like the ii degree below
embellishing >> Rest() >> Play()

embellishing = Note("G") * 9 << Nth(3, 4, 5, 8, 9)**Foreach(1/2, 1/2, 1/2, 1/2, 1/1)**Duration() >> Stack()
embellishing + Foreach(+3, +4, +3, -2, +2, +3, +2, +3, -3)**Degree()
embellishing >> Rest() >> Play()

embellishing -= embellishing | Bellow(Beats(2))**Match(Measures(0), Measures(2))
embellishing += Note("B", 1/8) * 4 + Foreach(0, 1, 0, 1)
embellishing += Note("B", 1/8, Position(2)) * 4 - Foreach(0, 1, 0, 1)
embellishing >> Link() >> Rest() >> Play()

embellishing -= embellishing | Match(Beats(1), Steps(2))
embellishing += Note("A", 1/8, Position(0, Beats(1))) * 2 + Foreach(0, 2)
embellishing += Note("A", 1/8, Position(2, Beats(1))) * 2 + Foreach(2, 0)
embellishing >> Link() << Get(NoteValue())**NoteValue() >> Rest() >> Play()

embellishing -= embellishing | Match(Measures(0), Measures(2))**Above(Beats(0))
embellishing += Note("E", 1/8, Position(0, Beats(3))) * 2 + Foreach(2, 0)
embellishing += Note("D", 1/8, Position(2, Beats(3))) * 2 + Foreach(2, 0)
embellishing >> Link() >> Rest() >> Play(True)
