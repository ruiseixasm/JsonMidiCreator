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


ProgramChange("Bright piano", Channel(1)) + ProgramChange("Guitar", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(3, 4) << KeySignature('')


measure_0 = Note(3/8) / [0, 1/8, 1/4, 3/4] / 2
measure_0 << Each(5, 6, 5, 3)**Degree()

measure_4 = Note(3/4) / [1/2, 1/4, 0, 1/2, 1/4, 0]
measure_4 << Each(2, 2, 7, 1, 1, 5)**Degree() << Octave(5)
measure_4 >>= Smooth(4)

measure_8 = (measure_4 * [0]) * (measure_0 * [0, 0, 1])
measure_8 << Each(6, 6, 1, 7, 6, 5, 6, 5, 3)**Degree() << Octave(4)
measure_8 >>= Smooth(4)

measure_12 = (measure_4 * [0]) * (measure_0 * [0, 0, 1])
measure_12 << Each(6, 6, 1, 7, 6, 5, 6, 5, 3)**Degree() << Octave(4)
measure_12 >>= Smooth(4)

measure_16 = (measure_4 * [0]) * (measure_0 * [0, 1, 1])
measure_16 << Each(2, 2, 4, 2, 7, 1, 3)**Degree() << Octave(5)
measure_16 >>= Smooth(4)

measure_20 = (Note(1/4) / 3) * (measure_0 * [0]) * Note(2*3/4)
measure_20 << Each(1, 5, 3, 5, 4, 2, 1)**Degree() << Octave(5)
measure_20 >>= Smooth(4)

melody = \
    measure_0 * measure_4 * measure_8 * \
    measure_12 * measure_16 * measure_20 << Title("Melody")

sorted(melody % [Degree(), int()]) >> Print()


chord_C_4 = Chord("C", Bars(4)) << Channel(2) << Octave(3) << Velocity(80) << Gate(.99)
chord_G_2 = chord_C_4.copy("G", Bars(2))
chord_C_2 = chord_C_4.copy("C", Bars(2))
chord_F_2 = chord_C_4.copy("F", Bars(2))
chord_C_3 = chord_C_4.copy("C", Bars(3))
chord_G_1 = chord_C_4.copy("G", Bars(1))

chords = \
    chord_C_4 * chord_G_2 * chord_C_2 * chord_F_2 * chord_C_2 * \
    chord_F_2 * chord_C_2 * chord_G_2 * chord_C_3 * chord_G_1 * chord_C_2 << Title("Chords")
chords >>= Smooth(4)


silent_night = melody + chords << Title("Silent Night")
melody + chords.copy(Disable()) >> Plot(composition=chords)
