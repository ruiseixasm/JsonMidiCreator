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
AllNotesOff() + Blofeld.program_change(4, "A") >> P
# Devices to sync that also guarantee the total playing up to the end of Measures
# Note that Rest has no impact im prolonging the playing time without the global Clock on
defaults << ClockedDevices("Blofeld")

# Configuration input list
iterations: list[int] = [-1, 2, 8]

chaotic_calls: dict["str", dict] = {
        "position": { "chaos": Chaos(150), "loops": 13 },
        "duration": { "chaos": Chaos(300), "loops": 4 },
        "degree":   { "chaos": Chaos(477), "loops": 9 },
    }

seed: Clip = Note() * 4 << Duration(1/8)

for key, call in chaotic_calls.items():
    if call["loops"] >= 0:
        call["chaos"] *= call["loops"]
        pick: int = call["chaos"] % int()
        match key:
            case "position":
                seed << Nth(3)**Input(pick % 4)**Pick(7, 8, 9, 10)**Step()
            case "duration":
                seed << Nth(2, 4)**Input(pick % 8)**Pick(1/16, 1/8, 1/4, 1/2)**Duration()
            case "degree":
                seed << Nth(2, 4)**Input(pick % 8)**Pick(1, 4, 5, 6)**Degree()

seed * 4 >> Pv

defaults << ClockedDevices()
AllNotesOff() + Blofeld.program_change(1, "A") >> P

