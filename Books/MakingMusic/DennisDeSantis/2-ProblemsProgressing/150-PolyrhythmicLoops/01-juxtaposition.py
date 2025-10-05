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

rest_play = ( Rest(), Play())
settings << Tempo(90)

basic_loop: Clip = Note(1/16) * 4 << Foreach(2, 4, 6, 4) << Octave(3) << Velocity(65)
out_sync_loop: Clip = Note(1/16) * Rest()

# Multiply by elements instead of Measures (by float instead of by int)
out_sync_loop *= 4.0
basic_loop *= 5.0

juxtaposition: Clip = basic_loop + out_sync_loop
juxtaposition * 8.0 >> Play()

