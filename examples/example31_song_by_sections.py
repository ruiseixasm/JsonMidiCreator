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
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')

if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

settings << Tempo(160) << Folder("examples/")


kick = Note(1/2, Channel(1)) / 2 * 4 << Steps(1)
snare = Note(1/4, Channel(2)) / 4 * 4 << Steps(1) << Velocity(80)

part_A = Part([kick, snare])

kick += Beat(1)
snare += IsNot(Step(0))**Step(1)
snare << Velocity(60) << DownBeat()**Channel(3)
part_B = Part([kick, snare])

song_AB = part_A + part_B
song_sections = song_AB * ['a', 'a', 'b', 'a']

song_sections >> Plot(by_channel=True)

