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

rest_play = (R, P)
staff << "#" << 90
K % str() >> Print()    # Returns the tonic key (I)

motif = N * 6 << Foreach(quarter, eight, eight, dotted_quarter, eight, whole) >> S
motif << Foreach(-3, 1, 2, 3, 2, -3)**Degree()

# Flips three degrees from -3 to +3 up needs to go 5 degrees down (6 less tonic 1)
motif_inversion = motif >> (motif % Copy() << Get(Degree())**Add(3)**Multiply(-1)**Subtract(3))
motif_inversion >> rest_play
