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

defaults % Devices() % list() >> Print()
defaults += Digitakt.device
defaults % Devices() % list() >> Print()


# Processing Degrees
chooser = Input(SinX() * 100)

# https://youtu.be/KQ4UCfROIfk?si=Jcv9g2yZBGFpMsoy
defaults << Tempo(120)


print("1st LOOP")

level_cc = ControlChange(Digitakt.kick, Digitakt.midi_cc["LFO 1"]["Depth"]) * 16 << Iterate(step=1000)
level_cc * 4 >> P


print("2nd LOOP")

variables_level_cc = ControlChange(
        Digitakt.kick, Digitakt.midi_cc["LFO 1"]["Depth"]
    ) * 16 << Iterate(100, -6)**Multiply(128) >> Reverse()
variables_level_cc * 4 >> P


print("3rd LOOP")

variables_level_nrpn = ControlChange(
        Digitakt.kick, Digitakt.midi_nrpn["LFO 1"]["Depth"]
    ) * 16 << Iterate(100, -6) >> Reverse()
variables_level_nrpn * 4 >> P




defaults -= Digitakt.device
defaults % Devices() % list() >> Print()

