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
src_path = os.path.join(os.path.dirname(__file__), '../../', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *


settings << Folder("Books/EasyToPlayKeyboardTunes/")


settings << KeySignature()

four_notes = Note() / 4
three_notes = Note() / 2 / Note(1/2)
two_notes = Note(1/2) * 2
one_notes = Note(1/1) * 1

full_track = four_notes * three_notes.copy().mul(3) * four_notes * three_notes * two_notes * two_notes.copy(Each(1/4, 3/4)).stack()
full_track << Equal(Or(Bar(0), Bar(4)))**Each(3, 4, 3, 2)**""
full_track << Equal(Or(Bar(1), Bar(2), Bar(3), Bar(5)))**Each(1, 2, 3)**""
full_track << Equal(Bar(6))**Each(3, 4, 3, 2)**""
full_track << Equal(Bar(7))**Each(3, 4, 3, 2)**""

