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

device_list = defaults % Device() % list() >> Print()
device_list.insert(0, "Digitakt")
device_list >> Print()
defaults << Device(device_list)

defaults << Tempo(90)


# Processing Degrees
chooser = Input(SinX() * 100)
# Digitakt Channels
kick        = Channel(1)
snare       = Channel(2)
tom         = Channel(3)
clap        = Channel(4)
cowbell     = Channel(5)
closed_hat  = Channel(6)
open_hat    = Channel(7)
cymbal      = Channel(8)

kick_clip = Clip() >> Stepper("1... 1... 1...", Note(kick, 1/16)) << TrackName("Kick")
snare_clip = Note(snare, 1/16) * 1 << TrackName("Snare")
closed_hat_clip = Note(closed_hat, 1/16) * 16 << TrackName("Closed Hat")

# Extend pattern by 4 measures, each clip is 1 measure long
complete_part = Part(kick_clip, snare_clip, closed_hat_clip) * 4

cymbal_ptn = Note(cymbal, 1/2) * 1
cymbal_first = cymbal_ptn + CPar(Position(1.0))
cymbal_second = cymbal_ptn + CPar(Position(3.0))
cymbal_clip = cymbal_first + cymbal_second << TrackName("Cymbal")

complete_part << cymbal_clip


repeated_part = complete_part + Position(4)

complete_part >>= repeated_part

complete_part >> P

R() >> P
complete_part["Kick"] >> P


