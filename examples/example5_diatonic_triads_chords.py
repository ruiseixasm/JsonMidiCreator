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
staff << Tempo(30) << Measure(7)

(Chord() * 7 << Type("7th")) << Increment()**Degree() >> Play(True)
(Chord("A") << Scale("minor") << Octave(3)) * 7 << Increment()**Degree() \
    >> Play(True) >> Print() << Inversion(1) >> Play(True)

Chord("C") << Type("13th") << Scale("Major") << Degree("Dominant") << Octave(3) << NoteValue(8) >> Print() >> Play()
Chord("G") << Type("13th") << Scale("5th") << NoteValue(8) << Octave(3) >> Print() >> Play()

