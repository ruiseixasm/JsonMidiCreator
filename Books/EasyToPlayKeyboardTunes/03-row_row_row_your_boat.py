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


ProgramChange("Harpsichord", Channel(1)) + ProgramChange("Bassoon", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(3, 4) << KeySignature()


melody = Note(3/4) * 16 << Velocity(120) << Equal(Bar(8))**Octave(5)
melody //= Position(Bar(2), Beat(2))
melody //= Position(Bar(4), Beat(2))
melody //= Position(Bar(5), Beat(2))
melody //= Position(Bar(12), Beat(2))
melody //= Position(Bar(13), Beat(2))
melody //= Greater(Bar(7))**Less(Bar(12))**Beats(1)

melody >>= Equal(Or(Bar(6), Bar(7)))**Merge()
melody >>= Equal(Or(Bar(14), Bar(15)))**Merge()

melody << Each(
        C, C, C, D,   E, E, D,
        E, F, G,      C, C, C,
        G, G, G,      E, E, E,    C, C, C,
        G,    F,      E, D,       C
    )**RootKey()

chords = Chord("C", Bars(8)) * Chord("C", Bars(4)) * Chord("G", Bars(2)) * Chord("C", Bars(2)) \
    << Channel(2) << Octave(3) << Velocity(50) >> Smooth(4) << Gate(.99)

london_bridge = melody + chords << Title("Row Row Row your Boat")

london_bridge * 2 >> Plot()
