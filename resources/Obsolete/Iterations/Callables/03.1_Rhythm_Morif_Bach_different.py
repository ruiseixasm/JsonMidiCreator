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
bach_motif = Clip(
    "n:1/16:A, ::G, ::A, ::G, :1/2d:A"
) << Name("Bach Motif")

ProgramChange("Church Organ") * 1 << Device("loopMIDI") >> Play()
bach_motif_C = bach_motif - RootKey("G") << Device("loopMIDI")
bach_motif_crescendo = bach_motif_C * 12 + Get(Measure())**Semitone()
bach_motif_crescendo >> Plot()

