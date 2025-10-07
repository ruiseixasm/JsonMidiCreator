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

settings << KeySignature(-1)   # Same as 'b'
arch_contour_1: Clip = Note("A") * 6 << Foreach(1/4, 1/8, 1/8, 1/4, 1/8, 1/8) >> Stack()
arch_contour_2: Clip = Note("A") * 4 << Foreach(1/4, 1/8, 1/8, 1/2) >> Stack()

arch_contour: Clip = \
    arch_contour_1.copy() + Foreach(-1, -2, -1, +1, -1, +1) >> \
    arch_contour_2.copy() + Foreach(2, 1, 2, 3) >> \
    arch_contour_1.copy() + Foreach(5, 3, 2, 3, 2, 1) >> \
    arch_contour_2.copy() + Foreach(2, 1, -1, 1)
arch_contour >> Rest() >> Play()

settings << KeySignature("#")
inverted_arch_1: Clip = Note("G") * 4 << Foreach(Dotted(1/4), 1/8, Dotted(1/4), 1/8) >> Stack() \
    << Foreach("C", "A", "B", "G") << Bellow(Pitch("D", 4))**Octave(5) << Above(Pitch("D", 5))**Octave(4)
inverted_arch_2: Clip = inverted_arch_1 >> Copy() \
    << Foreach("A", "F", "G", "E") << Bellow(Pitch("D", 4))**Octave(5) << Above(Pitch("D", 5))**Octave(4)
inverted_arch_3: Clip = Note("G") * 4 << Foreach(Dotted(1/4), 1/8, 1/4, 1/4) >> Stack() \
    << Foreach("D", "E", "F", "G") << Bellow(Pitch("D", 4))**Octave(5) << Above(Pitch("D", 5))**Octave(4)
inverted_arch_4: Clip = Note("A", 1/1) * 1
(inverted_arch_1, inverted_arch_2, inverted_arch_3, inverted_arch_4, Rest()) >> Play()

settings << KeySignature()
ascending_m: Clip = Note() * 4
ascending_1: Clip = ((ascending_m | Nth(1, 2, 3)).copy() << Foreach("F", "G", "A")) >> Link()
ascending_2: Clip = ascending_m.copy() << Foreach("G", "A", "B", "G")
ascending_3: Clip = ascending_m.copy() << Foreach("C", "B", "C", "D")
ascending_4: Clip = (ascending_m | Nth(1)).copy() << "E" << 1/1
(ascending_1, ascending_2, ascending_3, ascending_4, Rest()) >> Smooth() >> Play()

settings << KeySignature(-2)
descending_m: Clip = Note(1/8) * 5 >> Link()
descending_1: Clip = descending_m >> Copy() << Octave(5) << Foreach("D", "C", "B", "A", "B")
descending_2: Clip = descending_1.copy() - 1
descending_3: Clip = descending_2 >> Copy()
(descending_3 | Duration(1/8)) >> Reverse()
descending_3 - Nth(4, 5)**Foreach(2, 1)
descending_4: Clip = Note("F") * 1 >> Link()
descending: Clip = (descending_1, descending_2, descending_3, descending_4, Rest()) >> Smooth() >> Play()
# for note_i in range(descending.len() - 1):
#     descending.copy() - Nth(note_i + 1)**1 >> Play()

settings << KeySignature(2)
stationary_m: Clip = Note() * 4 << Foreach(Dotted(1/4), 1/8, 1/4, 1/4) >> Stack()
stationary_1: Clip = stationary_m >> Copy() << Foreach("A", "G", "A", "B")
stationary_2: Clip = stationary_1.copy() - (stationary_1 | Even()) >> Link() << Foreach("A", "G")
stationary_3: Clip = stationary_m >> Copy() << Foreach("A", "B", "A", "G")
stationary_4: Clip = (stationary_1 | Beats(0)) >> Copy() >> Link()
stationary: Clip = (stationary_1, stationary_2, stationary_3, stationary_4, Rest()) >> Smooth() >> Play()
