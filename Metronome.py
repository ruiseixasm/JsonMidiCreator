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

rest_play = ( Rest(), P)
settings << Tempo(120)     # Sets the metronome tempo
settings << Measures(4)    # Sets the length in Measures

measures_long: int = settings.__mod__(od.Pipe( Measures() )).__mod__(od.Pipe( int() ))

measure_bell: Clip = Note(DrumKit(34)) * 1 * measures_long
# measure_bell >> Play()
beat_tick: Clip = (Note(DrumKit(33)) * 3 + Beat(1)) * measures_long << Velocity(80)
# beat_tick >> Play()

metronome: Clip = measure_bell + beat_tick

for tempo in (89, 90, 91, 92):
    print(f"Tempo: {tempo}")
    metronome << Tempo(tempo)     # Sets the metronome tempo of the Clip
    metronome * 2 >> Play()
    Rest() >> Play()


