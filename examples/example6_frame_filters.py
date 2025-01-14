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
defaults << Measures(7)

(Chord(1/4) * 7 << Size("7th")) << Even()**Iterate()**Add(2)**Degree() >> Print() >> Play(True)
(Chord(1/4) * 7 << Size("7th")) << Iterate()**Even()**Add()**Degree() >> Print() >> Play(True)

all_chords = (Chord(1/4) * 7 << Size("7th"))
first_chords = all_chords | Beat(0)
first_chords << Degree(5) << Mode(5)
all_chords >> Print() >> Play(True)

first_chords << Degree() << Mode()
even_chords = all_chords | Even()**Operand()
even_chords << Degree(5) << Mode(5)
all_chords >> Print() >> Play(True)
