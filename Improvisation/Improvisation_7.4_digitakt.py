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

defaults << Tempo(130)

open_hats_clip = Clip() >> Stepper("..1..1..", Note(open_hat, 1/16))
open_hats_clip << TrackName("Open Hat")
open_hats_clip += open_hats_clip + Beats(2)

close_hats_clip = Note(closed_hat, 1/16) * 16 << TrackName("Closed Hat")

tom_clip = Note(tom, 1/16, Step(2)) * 1 << TrackName("Tom")
tom_clip += tom_clip + Beats(2)

snare_clip = Note(snare, 1/16, Step(4)) * 1 << TrackName("Snare")
snare_clip += snare_clip + Beats(2)

kick_clip = Note(kick, 1/4) * 4 << 1/16 << TrackName("Kick")


# Extend pattern by 8 measures, each clip is 1 measure long
complete_part = Part(open_hats_clip, close_hats_clip, tom_clip, snare_clip, kick_clip) * 4

snare_tom_part = Part(tom_clip, snare_clip) * 4



complete_part >> P

R(1/2) >> P
complete_part.filter("Snare")[0] >> P

