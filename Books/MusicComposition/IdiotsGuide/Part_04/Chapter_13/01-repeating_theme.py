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
staff << "bbb"
K % str() >> Print()    # Returns the tonic key (I)

motif = N * 5 << eight >> LJ << Foreach(9, 6, 8, 9, 9)**Degree() >> Tie()
# motif >> rest_play
measure_2 = N * 3 << Equal(B1)**half >> S << Foreach(9, 8, 7)**Degree()
measure_4 = N * 2 << half << Foreach(8, 7)**Degree()
# motif >> measure_2 >> motif >> measure_4 >> rest_play

clarinet = \
    (R << whole) + \
    motif + \
    (N * 3 << Nth(1)**half << Foreach(9, 11, 10)**Degree()) + \
    motif \
    >> S >> Tie() << Channel(1) << Track(1, "Clarinet")
clarinet % M1 % Length() >> Print(0)
clarinet >> rest_play >> MidiExport("Midi/clarinet.mid")
# trumpet = \
#     motif + \
#     (N * 2 << half << Foreach(5, 7)**Degree()) + \
#     motif + \
#     (N * 2 << half << Foreach(7, 6)**Degree()) \
#     >> S << Channel(2) << Track(2, "Trumpet")
# trumpet >> rest_play
# clarinet + trumpet >> L >> rest_play
