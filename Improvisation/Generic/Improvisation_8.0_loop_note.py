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



defaults += Device("Blofeld")
start_program = ProgramChange(Blofeld.program(4, "A"))
reset_program = ProgramChange(Blofeld.program(1, "B"))
# Devices to sync
# defaults << ClockedDevices("Blofeld")

two_notes = Note() / 2 << Iterate(step=2)**Beats()

full_clip = start_program + two_notes * 2 * Rest() * reset_program
full_clip % Length() % float() >> Pr
full_clip >> Export("json/_Export_8.0_loop_note.json") >> Pv


