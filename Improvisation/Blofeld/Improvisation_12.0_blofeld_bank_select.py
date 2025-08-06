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

# The enabled Clock makes everything last at least one Measure!
settings << RD_Blofeld.device << ClockedDevices(RD_Blofeld.device) << Tempo(110)

# Set a sound of a given Bank
RD_Blofeld.program_change(95, "B") + Chord(2/1) >> Pv
AllNotesOff() >> Pv

# Plays a Major chord for each Bank first Sound
for bank in range(8):
    program_change = RD_Blofeld.program_change(1, bank + 1)      # + 1 because programs start at 1 (Programs are 1 based)
    program_change + Chord() >> P
    AllNotesOff() >> P

# Plays a two measures Major chord for all Sounds od the first Bank ("A")
for sound in range(128):
    program_change = RD_Blofeld.program_change(sound + 1, "A")   # + 1 because programs start at 1 (Programs are 1 based)
    program_change + Chord(2/1) >> P
    AllNotesOff() >> P

