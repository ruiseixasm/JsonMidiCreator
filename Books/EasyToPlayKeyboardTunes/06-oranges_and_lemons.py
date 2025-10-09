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


ProgramChange("Electric piano 1", Channel(1)) + ProgramChange("Cello", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(3, 4) << KeySignature('') << Quantization(1/2)


melody = Note() / 3 * 8 << Title("Melody")
melody //= First(2)**Step(1)
melody //= Either(Bar(1), Bar(5))**Match(Beat(2))**Beats(1/2)
melody >>= Last(2)**Merge()
melody << Each(5, 5, 3, 5, 3, 1, 2, 3, 4, 2, 5, 3, 1, 5, 5, 3, 5, 3, 1, 2, 3, 4, 2, 5, 3, 1)**Degree()

chords = \
    Chord("C", Bars(2)) * Chord("G", Bars(1)) * Chord("C", Bars(3)) * \
    Chord("G", Bars(1)) * Chord("C", Bars(1)) \
        << Title("Chords") << Channel(2) << Octave(3) << Velocity(60) << Gate(.99)
chords >>= Smooth(4)


silent_night = melody + chords << Title("Oranges and Lemons")
(melody + chords.copy(Disable())) * 2 >> Plot(composition=chords * 2)


