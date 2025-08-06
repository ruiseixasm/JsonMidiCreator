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
from jsonmidicreator_import import *    # This ensures src is added & JsonMidiCreator is imported

settings % Devices() % list() >> Print()
settings += RD_Blofeld.device
settings % Devices() % list() >> Print()


# Processing Degrees
chooser = Input(SinX() * 100)

# https://youtu.be/KQ4UCfROIfk?si=Jcv9g2yZBGFpMsoy
settings << Tempo(120)

long_note_c = Note(4/1)

print("1st LOOP")

level_cc = ControlChange(RD_Blofeld.midi_cc["EFFECTS"]["Mix 1"]) * 16 << Iterate(step=1000)
level_cc * 4 + long_note_c >> P

print("2nd LOOP")

automation_cc = Clip() >> Automate([95, 50, 20, 50, 90, 100], "1... 1.1. .1.. ..11", RD_Blofeld.midi_cc["EFFECTS"]["Mix 2"])
automation_cc * 4 + long_note_c >> P



settings -= RD_Blofeld.device
settings % Devices() % list() >> Print()

