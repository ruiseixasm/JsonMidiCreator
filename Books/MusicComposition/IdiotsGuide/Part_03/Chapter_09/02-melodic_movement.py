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

smooth_movement_p1: Sequence = Note() * 4
smooth_movement_p2: Sequence = Note() * 3 << Foreach(Dotted(1/4), 1/8, 1/2) >> Stack() << Foreach("E", "D", "D")
smooth_movement_1: Sequence = smooth_movement_p1.copy() << Foreach("E", "E", "F", "G")
smooth_movement_2: Sequence = (smooth_movement_p1.copy() << "G") - Iterate()
smooth_movement_3: Sequence = smooth_movement_p1.copy() << Nth(3, 4)**Foreach("D", "E")

# (smooth_movement_1, smooth_movement_2, smooth_movement_3, smooth_movement_p2, 
#  smooth_movement_1, smooth_movement_2, smooth_movement_3, smooth_movement_p2 - 1, Rest()) >> Play()

staff << KeySignature("b")
whole_notes: Sequence = Note(1/1) * 4 << Foreach("F", "B", "E", KeyNote("C", 5))
# whole_notes >> Rest() >> Play()

melodic_e: Sequence = Note(1/8, Position(1/2) - NoteValue(1/8)) * 5
melodic_1: Sequence = (melodic_e.copy() << "E") + Iterate() + Nth(5)**1
melodic_2: Sequence = (melodic_e.copy() - (melodic_e | Nth(1)) << "B" << Measure(1)) - Iterate()
melodic_3: Sequence = melodic_1.copy() + 1 << Measure(2)
whole_notes + melodic_1 + melodic_2 + melodic_3 >> Link(True) >> Rest() >> Play(True)
