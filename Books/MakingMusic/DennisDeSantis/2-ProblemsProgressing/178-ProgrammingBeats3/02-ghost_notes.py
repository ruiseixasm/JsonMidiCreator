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


hi_hat = Note(DrumKit("Hi-Hat"), 1/16) * 8 << Iterate(2)**Steps()
snare = Note(DrumKit("Snare"), 1/16) * 2 << Iterate(2)**Add(1)**Beat()
drum = Note(DrumKit("Drum"), 1/16) * 3 << Iterate()**Beats()
drum += Nth(2)**Steps(3)

ghost_notes = Note(DrumKit("Snare"), 1/16) * 2 + Step(1) << Velocity(30)
ghost_notes << Length(ghost_notes, 0.5)
ghost_notes *= 2

backbeats = hi_hat + snare + drum + ghost_notes
backbeats * 8 >> P

print("Delay for 0.5 seconds")
time.sleep(0.5)

ghost_notes << Velocity(60)
anticipation = Note(DrumKit("Snare"), 1/32) * 2 + Steps(15) << Velocity(30)

backbeats = hi_hat + snare + drum + ghost_notes + anticipation
backbeats * 8 >> Play(1)

print("Delay for 0.5 seconds")
time.sleep(0.5)

anticipation << Quantization(1/8)   # Quantization is in Beats ratio
anticipation += Steps(1/2)
anticipation << Duration(0.40 * 1/32)

backbeats = hi_hat + snare + drum + ghost_notes + anticipation
backbeats * 8 >> Play(1)

