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

staff << Tempo(30)
sevenths = Chord(1/2) * 8
sevenths << Foreach(
    (Size("7th"),   Degree("V"),    Dominant()),
    (Size("5th"),   Degree("I"),    Inversion(2)),

    (Size("7th"),   Degree("IV"),   Dominant()),
    (Size("5th"),   Degree("VII"),  Flat(),         Inversion(2)),

    (Size("7th"),   Degree("I"),    Dominant()),
    (Size("5th"),   Degree("IV"),   Inversion(2),   Octave(3)),

    (Size("7th"),   Degree("II"),   Dominant()),
    (Size("5th"),   Degree("V"),    Inversion(2),   Octave(3))
) >> Stack()
sevenths >> Rest() >> Play()


