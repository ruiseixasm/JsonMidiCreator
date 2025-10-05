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
settings << Tempo(110)

hi_hat = Note(DrumKit("Hi-Hat"), 1/16) * 16 << Even()**Velocity(40)
snare = Note(DrumKit("Snare"), 1/16) * 2 << Foreach(1, 3)**Beat()
drum = Note(DrumKit("Drum"), 1/16) * 4 << Foreach(0, 6, 8, 15)**Step()

# (hi_hat + snare + drum) * 8 >> P

hi_hat += 1/10 * Steps(1)   # shifts by 10%
hi_hat << Length(1.0)

# First clip sets the common parameters (hi-hat)
(hi_hat + snare + drum) * 8 >> Play()

hi_hat += 8/10 * Steps(1)   # shifts by more 80% (total 90%)
hi_hat << Velocity(100) << Odd()**Velocity(40)  # alternates lower velocity
(hi_hat + snare + drum) * 8 >> Play()
