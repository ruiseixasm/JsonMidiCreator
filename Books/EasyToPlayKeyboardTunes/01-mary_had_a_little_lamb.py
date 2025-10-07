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


ProgramChange("Piano") + ProgramChange("Piccolo", Channel(2)) >> Play()

settings << KeySignature() << Tempo(140)

eight_measures = Note(1/4) / 4 * 8

settings << Quantization(2) # Two beats quantization
eight_measures >>= Match(Measure(1), Step(1))**Merge()
eight_measures >>= Match(Measure(2), Step(1))**Merge()
eight_measures >>= Match(Measure(3), Step(1))**Merge()
eight_measures >>= Match(Measure(7))**Merge()
settings << Quantization(1/4)   # 1/16 note again

eight_measures << Each(
        3, 2, 1, 2,   3, 3, 3,
        2, 2, 2,      3, 5, 5,
        3, 2, 1, 2,   3, 3, 3, 1,
        2, 2, 3, 2,   1
    )**""


chords = Chord("C", 2*1.0) * Chord("G") * Chord("C", 3*1.0) * Chord("G") * Chord("C") << Channel(2) << Octave(3) << Velocity(70) >> Smooth(4)

little_lamb = eight_measures + chords << Title("Little Lamb")

little_lamb * 2 >> Plot()


