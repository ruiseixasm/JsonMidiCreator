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

settings << KeySignature("b")

smooth: Clip = Note("F") * (3*4 + 1) >> Link()
smooth + Foreach(0, -1, 0, 1, 2, 3, 2, 1, 0, 1, 0, -2, -1)
smooth >> Rest() >> Play()

syncopated: Clip = smooth.copy() \
    - Match(Measures(0))**Even()**Position(Duration(1/8)) \
    + Match(Measures(1))**Position(Duration(1/8)) \
    + Match(Measures(2))**DownTo(Beats(2))**Position(Duration(1/8))
(syncopated | Measures(0)) >> Link()
(syncopated | Measures(1)) >> Link()
(syncopated | Measures(2) | Above(Beats(2))) >> Link()
syncopated >> Link()
syncopated >> Rest() >> Play()


settings << KeySignature(3)    # 3 sharps

straight_a: Clip = Note("A", 1/8) * 4 + Foreach(0, 1, 3, 2)
straight_b: Clip = Note("A", 1/8) * 4 - Foreach(0, 1, 2, 3)
straight_c: Clip = Note("B", 1/8) * 4 - Foreach(0, 1, 3, 2)
straight_d: Clip = Note("G", 1/8) * 4 + Foreach(0, 1, 0, -1)
straight_e: Clip = Note("B", 1/2)

straight: Clip = straight_a + straight_e + straight_d + straight_e + straight_a + straight_c + straight_d + straight_e >> Stack()
straight - Match(NoteValue(1/2))**Foreach(0, 5, 2)
straight >> Rest() >> Play()

triple_notes: Clip = Note("A", 1/16) + Note("A", 1/8) + Note("A", 1/16) >> Stack()
single_note: Clip = Note("A", 1/2) * 1
measure_0: Clip = triple_notes * 2 + single_note >> Stack()
measure_1: Clip = measure_0.copy()
measure_2: Clip = triple_notes * 4 >> Stack()
measure_3: Clip = measure_0.copy()

measure_0 + Foreach(0, 1, 3, 3, 2, 1, 1)
measure_1 - Foreach(0, 1, 2, 2, 3, 4, 4)
measure_2 + Foreach(0, 1, 3, 3, 2, 1, 1, 0, -3, -3, -2, -1)
measure_3 + Foreach(-1, 0, -1, -1, -2, -1, -1)

measure_0 >> measure_1 >> measure_2 >> measure_3 >> Rest() >> Tie() >> Play(True)
