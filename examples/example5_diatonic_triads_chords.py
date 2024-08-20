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
global_staff << Tempo(120) << Measure(7)

Chord("7th") * 7 + Increment()**Beat() + Increment()**Degree(0) >> Play(True)
(Chord() << Key("A") << Scale("minor") << Octave(3)) * 7 + Increment()**Beat() + Increment()**Degree(0) \
    >> Play(True) >> Print(8) << Inversion(1) >> Play(True)

Chord("13th") << Key("C") << Scale("Major") << Degree("Dominant") << Octave(3) << NoteValue(8) >> Print(8) >> Play()
Chord("13th") << Key("G") << Scale("5th") << NoteValue(8) << Octave(3) >> Print(8) >> Play()



