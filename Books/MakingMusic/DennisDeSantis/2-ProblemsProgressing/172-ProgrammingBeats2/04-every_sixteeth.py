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


# Linear Drum pattern programming
linear_drum_pattern = Note(1/16) * 32 << \
    Foreach(0, 1, 2, 0, 1, 2, 2, 1, 0, 2, 0, 0, 2, 0, 1, 1, 2, 1, 0, 2, 1, 0, 2, 1, 0, 1, 2, 0, 1, 2, 1, 0)**\
        Choice(DrumKit("Drum"), DrumKit("Snare"), DrumKit("Hi-Hat"))
linear_drum_pattern << Equal(DrumKit("Hi-Hat"))**Velocity(60)
linear_drum_pattern << Equal(DrumKit("Snare"))**Foreach(60, 110, 65, 70, 60, 65, 105, 70, 70, 110, 75)**Velocity()
linear_drum_pattern * 8 >> P

print("Delay for 0.5 seconds")
time.sleep(0.5)

# Chaotic Drum pattern programming
chaotic_drum_pattern = Note(1/16) * 32 << \
    Input(SinX() * 25)**Choice(DrumKit("Drum"), DrumKit("Snare"), DrumKit("Hi-Hat"))
chaotic_drum_pattern << Equal(DrumKit("Hi-Hat"))**Velocity(60)
chaotic_drum_pattern << Equal(DrumKit("Snare"))**Foreach(60, 110, 65, 70, 60, 65, 105)**Velocity()
chaotic_drum_pattern * 8 >> P

