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

fx_control_ch   = Channel(9)
auto_channel    = Channel(10)

bank_pattern: dict[str, list[int]] = {
    "A": [0] + list(range(0 * 16, 1 * 16)),
    "B": [0] + list(range(1 * 16, 2 * 16)),
    "C": [0] + list(range(2 * 16, 3 * 16)),
    "D": [0] + list(range(3 * 16, 4 * 16)),
    "E": [0] + list(range(4 * 16, 5 * 16)),
    "F": [0] + list(range(5 * 16, 6 * 16)),
    "G": [0] + list(range(6 * 16, 7 * 16)),
    "H": [0] + list(range(7 * 16, 8 * 16))
}

# https://youtu.be/KQ4UCfROIfk?si=Jcv9g2yZBGFpMsoy
defaults << Tempo(120)


set_pattern_to_2 = ProgramChange(auto_channel, Program("2"))
set_pattern_to_3 = ProgramChange(auto_channel, Program("3"))

set_pattern_to_2 >> P

R(1/1) >> P
set_pattern_to_3 >> P

R(1/1) >> P
set_pattern_to_2 >> P

R(1/1) >> P
set_pattern_to_3 >> P


R(2/1) >> P
set_pattern_to_2 = ProgramChange(auto_channel, "2")
set_pattern_to_3 = ProgramChange(auto_channel, "3")

set_pattern_to_2 >> P

R(1/1) >> P
set_pattern_to_3 >> P

R(1/1) >> P
set_pattern_to_2 >> P

R(1/1) >> P
set_pattern_to_3 >> P


R(2/1) >> P
set_pattern_to_2 = ProgramChange(auto_channel, Program(bank_pattern["A"][2]))
set_pattern_to_3 = ProgramChange(auto_channel, Program(bank_pattern["A"][3]))

set_pattern_to_2 >> P

R(1/1) >> P
set_pattern_to_3 >> P

R(1/1) >> P
set_pattern_to_2 >> P

R(1/1) >> P
set_pattern_to_3 >> P



