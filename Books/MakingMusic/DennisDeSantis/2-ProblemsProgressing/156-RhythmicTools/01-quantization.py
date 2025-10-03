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

rest_play = (R(), P)
settings << Tempo(90)

original_measure: Clip = Note(1/16, Vel(70), Octave(3)) * 16 << Foreach(2, 3, 4, 6, 9, 7, 8, 7, 6, 5, 3, 2, 1, 2, 3, 4) # Degrees of Major Scale
# original_measure * 4 >> P
quantized_measure: Clip = original_measure + Steps(2) | Less(Beats(4))   # Implicit copy by + operator
quantized_measure << Get(Position())**Get(Beat()) << Duration(1/4)

quantized_measure * 8 >> P

