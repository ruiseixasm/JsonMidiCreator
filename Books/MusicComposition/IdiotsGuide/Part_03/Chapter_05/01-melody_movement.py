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

movement = Note() * (3*4 + 1) + Iterate()**Beat()
movement << Equal(Measure(3))**(KeyNote() << Octave(5) << Key("D")) << Equal(Measure(3))**Duration(1) \
         << Equal(Measure(0))**Key("E") << Equal(Measure(1))**Key("G") << Equal(Measure(2))**Key("B")
movement += Equal(Measure(0))**Iterate()**Key()
movement += Equal(Measure(1))**Iterate()**Key()
movement += Equal(Measure(2))**Iterate()**Key()
movement >> Play(True)

Rest(1) >> Play(True)   # Needs to be implemented in JsonMidiPlayer

movement = Note() * 9 << Octave(5)
movement << Container(NoteValue(1/2), None, None, NoteValue(1/2), NoteValue(1/2), NoteValue(1/2), None, None, NoteValue(1))
movement << Container(None, None, None, KeyNote("B") << Octave(4), None, Key("D"), Key("D"), Key("D"), None)
movement >> Stack() >> Play()

movement = Note() * 12
movement << Nth(7)**NoteValue(1/2) << Nth(12)**NoteValue(1)
movement += Container(9, 6, 7, 10, 9, 8, 7, 6, 5, 4, 0, 1)
movement >> Stack() >> Play()

