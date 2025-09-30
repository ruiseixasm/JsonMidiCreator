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


settings += Device("Digitakt")
settings << Tempo(114)

cymbals = Note(1/8, Channel(8), Velocity(90)) / 8
snare_drum = Note(1/4, Channel(2), Velocity(90)) / ".1.1"
bass_drum = Note(1/8, Channel(1), Velocity(90)) / "1...11.." << Nth(1)**(1/4)
drum_set = bass_drum + snare_drum + cymbals << TrackName("Drum set")

drum_set * 4 >> Plot(by_channel=True)

