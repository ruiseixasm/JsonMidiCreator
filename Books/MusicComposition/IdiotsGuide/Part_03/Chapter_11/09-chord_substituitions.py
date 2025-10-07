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


settings << "##"
Key() % str() >> Print()    # Returns the tonic key (I)

notes = Note(half) * 2 + Note() * 4 + Note(half) * 2 + Note(whole) >> Stack()
notes << Foreach(A, (F, 5), E, D, C, A, B, C, B)
notes % Above(Position(0, Beats(0))) >> Smooth()
notes >> Rest >> Play()

substitutions_chords = Chord() * 5 << Nth(3, 4)**half >> Stack()
substitutions_chords << Foreach("F#m", G, "Bm", "Em7", G) << Octave(3)
substitutions_chords = substitutions_chords + Note(A, Chord("Em7", Octave(3)) % Octave() - 1, half, Position(M3, B3)) >> Link()
substitutions_chords >> Rest >> Play()

notes + substitutions_chords >> Link() >> Rest >> Play()
