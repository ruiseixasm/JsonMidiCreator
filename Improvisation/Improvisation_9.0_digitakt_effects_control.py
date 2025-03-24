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
    # The first column is just for offset purposes
    "A": list(range(0 * 16, 1 * 16 + 1)),   # 1 to 16
    "B": list(range(1 * 16, 2 * 16 + 1)),   # 17 to 32
    "C": list(range(2 * 16, 3 * 16 + 1)),   # 33 to 48
    "D": list(range(3 * 16, 4 * 16 + 1)),   # 49 to 64
    "E": list(range(4 * 16, 5 * 16 + 1)),   # 65 to 80
    "F": list(range(5 * 16, 6 * 16 + 1)),   # 81 to 96
    "G": list(range(6 * 16, 7 * 16 + 1)),   # 97 to 112
    "H": list(range(7 * 16, 8 * 16 + 1))    # 113 to 128
}

midi_cc: dict[str,
            dict[str,
                dict[str, int]
            ]
        ] = {
            # PER TRACK PARAMETERS (CHANNEL 1 TO 8)
            "TRACK": {
                "Mute": {
                    "MSB": 94,
                    "LSB": -1   # Blank, no LSB, 7 bits
                },
                "Level": {
                    "MSB": 95,
                    "LSB": -1   # Blank, no LSB, 7 bits
                }
            }
        }


# https://youtu.be/KQ4UCfROIfk?si=Jcv9g2yZBGFpMsoy
defaults << Tempo(120)


level_cc = ControlChange(kick, MSB(midi_cc["TRACK"]["Level"]["MSB"])) * 16 << Iterate(step=5)

level_cc * 4 >> P

