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
# note_group >> Rest() >> Play()
melody = Note() + Note() + note_group + Note() + Note() + Note(half) + Note() + Note() + note_group + Note(whole) >> Stack()
melody << Nth(1, 2, 7, 8, 9, 10, 11, 16)**Foreach("V", "I", "I", "ii", "iii", "IV", "I", "I")
melody >> Rest() >> Play()
chords = Chord() * 4 << Foreach("Bb", "Gm", "Eb", "Bb") << Octave(3)
# chords >> Rest() >> Play()
melody + chords >> Link() >> Rest() >> Play()

chords_2 = Chord(1/2) * 6 + Chord() >> Stack() << Foreach("Bb", "Gm", "Eb", "Dm", "Eb", "F", "Bb") << Octave(3)
melody + chords_2 >> Link() >> Rest() >> Play()

