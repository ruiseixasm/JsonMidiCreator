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
import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '../../', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *


settings << Folder("Books/EasyToPlayKeyboardTunes/")


ProgramChange("Organ", Channel(1)) + ProgramChange("Flute", Channel(2)) >> Play()

settings << KeySignature() << Tempo(140)


melody = Note() / [
        Nul,  -5,                    1/2,
        Nul, Nul,  1/2,    Nul, Nul, 1/2,
        Nul,  -5,                    1/2,
        1/2, 1/2,          Nul, 3/4
    ]


melody << Each(
        G, A, G, F,   E, F, G,
        D, E, F,      E, F, G,
        G, A, G, F,   E, F, G,
        D,    G,      E, C
    )**RootKey()

chords = Chord("C", 2*1.0) * Chord("G") * Chord("C") * Chord("C", 2.0) * Chord("G") * Chord("C") << Channel(2) << Octave(3) << Velocity(70) >> Smooth(4)

london_bridge = melody + chords << Title("London Bridge")

london_bridge * 2 >> Plot()
