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

step_wise = Note("F") * (4*4 - 3) + Nth(2, 3, 4, 7, 8, 9, 10)**Iterate()**0 << Match(Measures(3))**Duration(1/1)
(step_wise | Nth(1, 5, 6, 11, 12, 13)) + Foreach(1, 3, 2, 5, 4, 3)
step_wise >> Play()

skip_wise: Clip = Note() * 4 + Foreach(4, 8, 7, 4)
skip_wise >> skip_wise - 1 >> skip_wise - 1 >> (skip_wise - 1 - (skip_wise | Nth(2, 3, 4)) << Duration(1/1)) >> Play()
