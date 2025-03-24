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

device_list = defaults % Devices() % list() >> Print()
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

# https://youtu.be/VJtg7pJO3hQ?si=-cPdOfONCXdw1ID6
defaults << Tempo(135)

open_hats_clip = Clip() >> Stepper("..1..1..", Note(open_hat, 1/16))
open_hats_clip << TrackName("Open Hat")
open_hats_clip += open_hats_clip + Beats(2)

close_hat_4_4_clip = Note(closed_hat, 1/4) * 4 << TrackName("Closed Hat")

tom_clip = Note(tom, 1/16, Step(2)) * 1 << TrackName("Tom")
tom_clip += tom_clip + Beats(2)

snare_clip = Note(snare, 1/16, Step(4)) * 1 << TrackName("Snare")
snare_clip += snare_clip + Beats(2)

kick_clip = Note(kick, 1/4) * 4 << 1/16 << TrackName("Kick") << Velocity(80)


close_hat_4_4_clip * 16 >> P

