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

stable = Note("C", 1/1) * 3 - 1 + Foreach(1, 5, 3)
rest = Rest(1/1)
unstable = Note("C", 1/1) * 4 - 1 + Foreach(6, 2, 4, 7)

# stable >> rest >> unstable >> Play()


harmonies = Note(Measures(0), Duration(1/2)) + Note(Beats(2), Duration(1/2)) + Note(Measures(1)) * 4 + Note(Measures(2), NoteValue(1/2)) * 2 + Note(Measures(3), NoteValue(1/1)) >> Link()
harmonies - 1 + Foreach(8, 1, 2, 3, 4, 5, 6, 5, 8)
harmonies >> Play()
