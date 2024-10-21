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

staff << KeySignature(-1)   # Same as 'b'
arch_contour_1: Sequence = Note("A") * 6 << Foreach(1/4, 1/8, 1/8, 1/4, 1/8, 1/8) >> Stack()
arch_contour_2: Sequence = Note("A") * 4 << Foreach(1/4, 1/8, 1/8, 1/2) >> Stack()

arch_contour: Sequence = \
    arch_contour_1.copy() + Foreach(-1, -2, -1, +1, -1, +1) >> \
    arch_contour_2.copy() + Foreach(2, 1, 2, 3) >> \
    arch_contour_1.copy() + Foreach(5, 3, 2, 3, 2, 1) >> \
    arch_contour_2.copy() + Foreach(2, 1, -1, 1)
# arch_contour >> Rest() >> Play()

staff << KeySignature("#")
inverted_arch_1: Sequence = Note("G") * 4 << Foreach(Dotted(1/4), 1/8, Dotted(1/4), 1/8) >> Stack() \
    << Foreach("C", "A", "B", "G") << Less(KeyNote("D", 4))**Octave(5) << Greater(KeyNote("D", 5))**Octave(4)
inverted_arch_2: Sequence = inverted_arch_1 >> Copy() \
    << Foreach("A", "F", "G", "E") << Less(KeyNote("D", 4))**Octave(5) << Greater(KeyNote("D", 5))**Octave(4)
inverted_arch_3: Sequence = Note("G") * 4 << Foreach(Dotted(1/4), 1/8, 1/4, 1/4) >> Stack() \
    << Foreach("D", "E", "F", "G") << Less(KeyNote("D", 4))**Octave(5) << Greater(KeyNote("D", 5))**Octave(4)
inverted_arch_4: Sequence = Note("A", 1/1) * 1
# (inverted_arch_1, inverted_arch_2, inverted_arch_3, inverted_arch_4, Rest()) >> Play()

staff << KeySignature()
ascending_m: Sequence = Note() * 4
ascending_1: Sequence = ((ascending_m | Nth(1, 2, 3)).copy() << Foreach("F", "G", "A")) >> Link(True)
ascending_2: Sequence = ascending_m.copy() << Foreach("G", "A", "B", "G")
ascending_3: Sequence = ascending_m.copy() << Foreach("C", "B", "C", "D")
ascending_4: Sequence = (ascending_m | Nth(1)).copy() << "E" << 1/1
# (ascending_1, ascending_2, ascending_3, ascending_4, Rest()) >> Smooth() >> Play()

staff << KeySignature(-2)
descending_m: Sequence = Note(1/8) * 5 >> Link(True)
descending_1: Sequence = descending_m >> Copy() << Octave(5) << Foreach("D", "C", "B", "A", "B")
descending_2: Sequence = descending_1.copy() - 1
descending_3: Sequence = descending_2 >> Copy()
(descending_3 | NoteValue(1/8)) >> Reverse()
descending_3 - Nth(4, 5)**Foreach(2, 1)
descending_4: Sequence = Note("E") * 1 >> Link(True)
(descending_1, descending_2, descending_3, descending_4, Rest()) >> Smooth() >> Play()



