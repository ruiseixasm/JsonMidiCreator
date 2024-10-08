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

familiar_bar1 = Note("F", 5) * 4 - Iterate()**0
familiar_bar2 = Note("B", Dotted(1/2)) + Note("F", 5)
familiar_bar3 = Note("E", 5) + Note("D", 5) + Note("G") + Note("A")
familiar_bar4 = Note("B", NoteValue(1))

familiar_bar1 + familiar_bar2 + familiar_bar3 + familiar_bar4 >> Stack() >> Play()
