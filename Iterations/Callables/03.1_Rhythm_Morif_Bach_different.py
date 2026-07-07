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

# https://youtu.be/x-zXfkV90fM?si=URTZ55NqK4Mlz4yX&t=17
settings << Device("loopMIDI")
bach_motif = Clip(
    "n:1/16:A, ::G, ::A, ::G, :1/2d:A"
) << Name("Bach Motif")

ProgramChange("Church Organ") >> Play()

bach_motif_C = bach_motif - RootKey("G")
bach_motif_crescendo = bach_motif_C * 12 + Get(Measure())**Semitone()
bach_motif_crescendo >> Plot()

