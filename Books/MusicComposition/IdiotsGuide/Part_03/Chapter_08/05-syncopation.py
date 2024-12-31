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

staff << KeySignature("b")

smooth: Sequence = Note("F") * (3*4 + 1) >> Link()
smooth + Foreach(0, -1, 0, 1, 2, 3, 2, 1, 0, 1, 0, -2, -1)
smooth >> Rest() >> Play()

syncopated: Sequence = smooth.copy() \
    - Equal(Measures(0))**Even()**OLD_Position(Duration(1/8)) \
    + Equal(Measures(1))**OLD_Position(Duration(1/8)) \
    + Equal(Measures(2))**GreaterEqual(Beats(2))**OLD_Position(Duration(1/8))
(syncopated | Measures(0)) >> Link()
(syncopated | Measures(1)) >> Link()
(syncopated | Measures(2) | Greater(Beats(2))) >> Link()
syncopated >> Link()
syncopated >> Rest() >> Play()


staff << KeySignature(3)    # 3 sharps

straight_a: Sequence = Note("A", 1/8) * 4 + Foreach(0, 1, 3, 2)
straight_b: Sequence = Note("A", 1/8) * 4 - Foreach(0, 1, 2, 3)
straight_c: Sequence = Note("B", 1/8) * 4 - Foreach(0, 1, 3, 2)
straight_d: Sequence = Note("G", 1/8) * 4 + Foreach(0, 1, 0, -1)
straight_e: Sequence = Note("B", 1/2)

straight: Sequence = straight_a + straight_e + straight_d + straight_e + straight_a + straight_c + straight_d + straight_e >> Stack()
straight - Equal(NoteValue(1/2))**Foreach(0, 5, 2)
straight >> Rest() >> Play()

triple_notes: Sequence = Note("A", 1/16) + Note("A", 1/8) + Note("A", 1/16) >> Stack()
single_note: Sequence = Note("A", 1/2) * 1
measure_0: Sequence = triple_notes * 2 + single_note >> Stack()
measure_1: Sequence = measure_0.copy()
measure_2: Sequence = triple_notes * 4 >> Stack()
measure_3: Sequence = measure_0.copy()

measure_0 + Foreach(0, 1, 3, 3, 2, 1, 1)
measure_1 - Foreach(0, 1, 2, 2, 3, 4, 4)
measure_2 + Foreach(0, 1, 3, 3, 2, 1, 1, 0, -3, -3, -2, -1)
measure_3 + Foreach(-1, 0, -1, -1, -2, -1, -1)

measure_0 >> measure_1 >> measure_2 >> measure_3 >> Rest() >> Tie() >> Play(True)
