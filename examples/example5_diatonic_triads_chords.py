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


# Global Staff setting up
staff << Measures(7) << 240

(Chord() * 7 << Size("7th")) << Iterate()**Add(1)**Degree() >> Play(True)
(Chord("A") << Scale("minor") << Octave(3)) * 7 << Iterate()**Add()**Degree() \
    >> Play(True) >> Print() << Inversion(1) >> Play(True)

Chord("C") << Size("13th") << Scale("Major") << Degree("Dominant") << Mode("5th") << Octave(3) << NoteValue(2) >> Print() >> Play()
Chord("G") << Size("13th") << Scale("5th") << NoteValue(2) << Octave(3) >> Print() >> Play()

