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

rest_play = ( Rest(), Play())
settings << Tempo(120)

motif: Clip = Note(1/16) * 12
motif << Nth(6)**Duration(Steps(3)) << Nth(12)**Duration(Steps(2)) >> Stack() << Octave(3)
motif += IsNot(Beat(0))**Step(1)
motif % Length() % float() >> Print()
motif += Foreach(0, 3, 10, 7, 2, -4, -5, -2, 0, 3, 7, -7)**Semitone()
# motif >> P

# The Transposition
transformed_motif: Clip = motif + (Semitone(4), Steps(4))   # Makes just one implicit copy with a tuple

(motif + transformed_motif) % Length() % Steps() % Fraction() >> Print()
(motif + transformed_motif) * 4 >> Play()

