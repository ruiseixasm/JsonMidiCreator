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

motion = Foreach(0, 2, 1, 4)**Degree()
parallel_1 = Note(1/1, Degree(6)) / 4 << TrackName("Parallel Motion")
parallel_1 += motion
parallel_2 = Note(1/1, Degree(4)) / 4
parallel_2 += motion

parallel_1 + parallel_2 >> Plot(block=False)


similar_1 = Note(1/1, Octave(5), Degree(1)) / 4 << TrackName("Similar Motion")
similar_1 += Foreach(0, 1, 3, 2)**Degree()
similar_2 = Note(1/1, Degree(3)) / 4
similar_2 += Foreach(0, 4, 5, 2)**Degree()

similar_1 + similar_2 >> Plot(block=False)


motion = Foreach(0, -2, -1, 0)**Degree()
oblique_1 = Note(1/1, Degree(5)) / 4 << TrackName("Oblique Motion")
oblique_1 += motion
oblique_2 = Note(1/1, Degree(1)) / 4

oblique_1 + oblique_2 >> Plot(block=False)


motion = Foreach(0, 1, 2, 1)**Degree()
contrary_1 = Note(1/1, Degree(5)) / 4 << TrackName("Contrary Motion")
contrary_1 += motion
contrary_2 = Note(1/1, Degree(1)) / 4
contrary_2 -= motion

contrary_1 + contrary_2 >> Plot(block=True)



