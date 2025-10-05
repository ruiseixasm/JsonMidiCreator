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

rest_play = ( Rest(), P)
settings << Tempo(110)

# Direct programming
hi_hat = Note(DrumKit("Hi-Hat"), 1/16) * 3 << Foreach(2, 8, 14)**Step()
snare = Note(DrumKit("Snare"), 1/16) * 2 << Foreach(4, 10)**Step()
drum = Note(DrumKit("Drum"), 1/16) * 3 << Foreach(0, 6, 12)**Step()

(hi_hat + snare + drum) * 8 >> P

print("Delay for 0.5 seconds")
time.sleep(0.5)

# 2+2+2 pattern programming
pattern = Note(1/16) * 3 << Iterate(2)**Step() << Foreach(DrumKit("Drum"), DrumKit("Hi-Hat"), DrumKit("Snare"))
pattern << Length(Steps(pattern, 2+2+2))
pattern *= 3
pattern >> Trim()

pattern * 8 >> P


