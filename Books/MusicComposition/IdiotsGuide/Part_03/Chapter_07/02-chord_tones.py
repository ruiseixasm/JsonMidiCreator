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

settings << KeySignature("b") << Tempo(60)
chords = Chord("F", 1/1) * 8 << Foreach(1, 4, 1, 5, 1, 4, 1, 5)**Degree() \
                             << Foreach(None, None, None, None, "9", "7", "7", "9")**Size() \
                             << Foreach(4, 4, 4, 4, 3, 3, 3, 2)**Octave()
chords >> Play()
settings << Tempo(120)
notes = Note("B", 1/1) * 8 + Foreach(1, 2, -1, -2, -2, -1, -4, -5)
notes >> Play()
notes + chords >> Play()
