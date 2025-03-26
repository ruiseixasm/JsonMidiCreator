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

defaults % Devices() % list() >> Print()
defaults += Digitakt.device
defaults % Devices() % list() >> Print()


# Processing Degrees
chooser = Input(SinX() * 100)

# https://youtu.be/KQ4UCfROIfk?si=Jcv9g2yZBGFpMsoy
defaults << Tempo(120)


print("1st LOOP")

level_cc = ControlChange(Digitakt.kick, Digitakt.midi_cc["TRACK"]["Level"]) * 16 << Iterate(step=1000)
# level_cc * 4 >> P

print("2nd LOOP")

automation_cc = Clip() >> Automate([100, 50, 20, 50, 100], "1... 1.1. .1.. ..1.", Digitakt.midi_cc["TRACK"]["Level"]) << Digitakt.kick
automation_cc * 4 >> P

print("3rd LOOP")

automation_cc = Clip() >> Automate([100, 50, 20, 50, 100], "1... 1.1. .1.. ..1.", Digitakt.midi_cc["TRACK"]["Level"], False) << Digitakt.kick
automation_cc * 4 >> P



defaults -= Digitakt.device
defaults % Devices() % list() >> Print()

