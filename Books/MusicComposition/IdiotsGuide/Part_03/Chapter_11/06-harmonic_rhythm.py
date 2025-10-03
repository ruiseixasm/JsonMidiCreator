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


settings << "bb"
Key() % str() >> Print()    # Returns the tonic key (I)

note_group = (Note() * 4 << 1/8 << "iii") - Iterate()
# note_group >> R >> P
melody = N + N + note_group + N + N + Note(half) + N + N + note_group + Note(whole) >> S
melody << Nth(1, 2, 7, 8, 9, 10, 11, 16)**Foreach("V", "I", "I", "ii", "iii", "IV", "I", "I")
melody >> R >> P
chords = Chord() * 4 << Foreach("Bb", "Gm", "Eb", "Bb") << Octave(3)
# chords >> R >> P
melody + chords >> L >> R >> P

chords_2 = Chord(1/2) * 6 + Chord() >> S << Foreach("Bb", "Gm", "Eb", "Dm", "Eb", F, "Bb") << Octave(3)
melody + chords_2 >> L >> R >> P

