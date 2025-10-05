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


settings << "#"
Key() % str() >> Print()    # Returns the tonic key (I)

slow_melody = Note() * 5 << 1/1 << Nth(2, 3)**half >> Stack()
slow_melody << Foreach((G, Gate(1)), G, A, B, G)
slow_melody >> Rest >> Play()

chords = Chord(1/2) * 6 + Chord() >> Stack()
chords << Foreach("Em", G, C, "Am", "Em", "Bm", G) << Octave(3)
chords + slow_melody >> Link() >> Rest >> Play()

settings << "b"
Key() % str() >> Print()    # Returns the tonic key (I)

fast_melody = \
    (Note() * 9 << eight << Nth(1, 2)**sixteenth << Foreach(1, 2, 3, 3, 3, 2, 1, 2, 3)**Degree()) + \
    (Note() * 7 << eight << Nth(5)**quarter      << Foreach(1, -2, 1, 2, 3, -4, 2)**Degree()) + \
    (Note() * 9 << eight << Nth(1, 2)**sixteenth << Foreach(1, 2, 3, 3, 5, 3, 2, 1)**Degree()) + \
    (Note() * 5 << eight << Nth(5)**half         << Foreach(2, 2, 2, 3, 2)**Degree()) << Gate(0.7) >> Stack()
fast_melody >> Rest >> Play()

chords = Chord(3/1) + Chord() >> Stack()
chords << Foreach((Gate(0.99), F), "Gm") << Octave(3)
# chords >> L >> R >> P
chords + fast_melody >> Link() >> Rest >> Play()
