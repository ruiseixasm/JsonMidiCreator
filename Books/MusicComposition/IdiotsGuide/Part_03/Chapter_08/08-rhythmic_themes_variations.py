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

settings << TimeSignature(2, 4) << KeySignature(-3)   # Same as 'bbb'

rhythmic_motif: Clip = Note("G", 1/8, Position(Duration(1/8))) * 4 >> Link()
rhythmic_motif - Match(Measures(1))**2
rhythmic_motif >> Rest() >> Play()

settings << TimeSignature(4, 4) << KeySignature(-2)   # Same as 'bb'

rhythmic_motif_1: Clip = Note("B") * 4 << Foreach(1/8, 1/4, 1/8, 1/2)**Duration() >> Stack()
rhythmic_motif_2: Clip = Note("A") * 6 << Foreach(1/8, 1/4, 1/8, 1/8, 1/4, 1/8)**Duration() >> Stack()

rhythmic_motif_1.copy() + Foreach(0, 1, 0, -1) >> rhythmic_motif_1.copy() + Foreach(-2, -1, -2, -3) \
    >> rhythmic_motif_2.copy() + Foreach(0, 1, 0, -1, -2, -4) >> Note("C", 1/1) >> Rest() >> Play()
