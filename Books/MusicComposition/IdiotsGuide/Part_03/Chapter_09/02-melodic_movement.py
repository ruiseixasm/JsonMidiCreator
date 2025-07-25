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

smooth_movement_p1: Clip = Note() * 4
smooth_movement_p2: Clip = Note() * 3 << Foreach(Dotted(1/4), 1/8, 1/2) >> Stack() << Foreach("E", "D", "D")
smooth_movement_1: Clip = smooth_movement_p1.copy() << Foreach("E", "E", "F", "G")
smooth_movement_2: Clip = (smooth_movement_p1.copy() << "G") - Iterate()
smooth_movement_3: Clip = smooth_movement_p1.copy() << Nth(3, 4)**Foreach("D", "E")

(smooth_movement_1, smooth_movement_2, smooth_movement_3, smooth_movement_p2, 
 smooth_movement_1, smooth_movement_2, smooth_movement_3, smooth_movement_p2 - 1, Rest()) >> Play()

settings << KeySignature("b")
whole_notes: Clip = Note(1/1) * 4 << Foreach("F", "B", "E", Pitch("C", 5))
whole_notes >> Rest() >> Play()

melodic_e: Clip = Note(1/8, Position(1/2) - Duration(1/8)) * 5
melodic_1: Clip = (melodic_e.copy() << "E") + Iterate() + Nth(5)**1
melodic_2: Clip = (melodic_e.copy() - (melodic_e | Nth(1)) << "B" << Measures(1)) - Iterate()
melodic_3: Clip = melodic_1.copy() + 1 << Measures(2)
whole_notes + melodic_1 + melodic_2 + melodic_3 >> Link() >> Rest() >> Play(True)

outline: Clip = Note(1/2) * 7 >> Link()
outline << Foreach("F", "A", "G", "F", "E", "D", "E")
outline >> Rest() >> Play()

settings << KeySignature("#")
# Matrix approach instead of a Vectorial one!
mixed = Note() * (2*6 + 2*5)
mixed << Foreach(
    # 1st Measure
    (1/8, Pitch("G", 4)),
    (1/8, Pitch("F", 4)),
    (1/8, Pitch("G", 4)),
    (1/8, Pitch("D", 5)),
    (1/4, Pitch("C", 5)),
    (1/4, Pitch("A", 4)),
    # 2nd Measure
    (1/8, Pitch("G", 4)),
    (1/8, Pitch("F", 4)),
    (1/8, Pitch("G", 4)),
    (1/8, Pitch("C", 5)),
    (1/2, Pitch("B", 4)),
    # 3rd Measure
    (1/8, Pitch("D", 5)),
    (1/8, Pitch("C", 5)),
    (1/8, Pitch("B", 4)),
    (1/8, Pitch("A", 4)),
    (1/4, Pitch("B", 4)),
    (1/4, Pitch("D", 4)),
    # 4th Measure
    (1/8, Pitch("F", 4)),
    (1/8, Pitch("E", 4)),
    (1/8, Pitch("B", 4)),
    (1/8, Pitch("A", 4)),
    (1/2, Pitch("G", 4))
) >> Stack()
(mixed, Rest()) >> Play()
