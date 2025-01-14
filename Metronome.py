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
src_path = os.path.join(os.path.dirname(__file__), '', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

rest_play = (R, P)
defaults << Tempo(120)     # Sets the metronome tempo
defaults << Measures(4)    # Sets the length in Measures

measures_long: int = staff // Measures() // int()

measure_bell: Sequence = Nt(DrumKit(34)) * 1 * measures_long
measure_bell >> Play()
beat_tick: Sequence = (Nt(DrumKit(33)) * 3 + Beat(1)) * measures_long << Velocity(50)
beat_tick >> Play()

metronome: Sequence = (measure_bell + beat_tick) * 4
metronome >> Play()


