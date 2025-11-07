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
RD_Blofeld.program_change(4, "A") >> Play()
# Devices to sync that also guarantee the total playing up to the end of Measures
# Note that Rest has no impact im prolonging the playing time without the global Clock on
settings << ClockedDevices("Blofeld")

# Configuration input list
iterations: list[int] = [-1, 2, 8]

clip_1 = Note(Channel(1)) * 4
clip_2 = Note(Channel(2)) * 4 + Steps(2)
clip_3 = Note(Channel(3)) * 4 + Steps(3)
part: Section = Section()
chaos: Chaos = Chaos() * 1233
layer: int = 0


clip_1 << Nth(2)**Input(chaos * iterations[layer])**Pick(2, 4, 5)
if iterations[layer] >= 0:
    part += clip_1
layer += 1

clip_2 << Nth(3)**Input(chaos * iterations[layer])**Pick(2, 4, 5)
if iterations[layer] >= 0:
    part += clip_2
layer += 1

clip_3 << Nth(4)**Input(chaos * iterations[layer])**Pick(2, 4, 5)
if iterations[layer] >= 0:
    part += clip_3
layer += 1

part >> Play(True)

settings << ClockedDevices()
RD_Blofeld.program_change(1, "A") + AllNotesOff() >> Play()

