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
from jsonmidicreator import *

# https://youtu.be/x-zXfkV90fM?si=URTZ55NqK4Mlz4yX&t=17
settings << Device("loopMIDI")
bach_motif = Clip(
    "n:1/16:A, ::G, ::A, ::G, :1/2d:A"
) << Name("Bach Motif")

ProgramChange("Church Organ") >> Play()
bach_motif >> Plot()
