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



settings += Device("Blofeld")
start_program = RD_Blofeld.program_change(4, "A") >> P
# Devices to sync that also guarantee the total playing up to the end of Measures
# Note that Rest has no impact im prolonging the playing time without the global Clock on
settings << ClockedDevices("Blofeld")

two_notes = Note() / 2 << Iterate(step=2)**Beats()
possibilities = Foreach(1, 2, 3, 4, 5, 6, 7)**Degree()


for degree in range(1, 8):  # 7 degrees in total
    degree >> Pr
    two_notes >> Nth(2) << degree
    try_clip = two_notes * 2 * Rest()
    try_clip >> P
    


reset_program = RD_Blofeld.program_change(1, "B") > P

