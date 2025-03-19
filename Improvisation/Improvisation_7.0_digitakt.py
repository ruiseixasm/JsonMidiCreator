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

kick_ptn = Note(kick) * 3
kick_ptn /= Duration(2)
snare_ptn = Note(snare) * 1

full_ptn = kick_ptn + snare_ptn << Duration(1/16)

# full_ptn * 4 >> P
R() >> P

closed_hat_ptn = Note(closed_hat, 1/16) * 16

full_ptn += closed_hat_ptn

# full_ptn * 4 >> P

# Extend pattern by 16 measures
full_ptn *= 4
complete_part = Part(full_ptn)

cymbal_ptn = Note(cymbal, 1/1) * 1
cymbal_first = cymbal_ptn + CPar(Position(2.0))
cymbal_second = cymbal_ptn + CPar(Position(6.0))

complete_part << cymbal_first
complete_part << cymbal_second


repeated_part = complete_part + Position(4)

complete_part >>= repeated_part

complete_part >> P



