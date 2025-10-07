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


ProgramChange("tonk piano", Channel(1)) + ProgramChange("English horn", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('b')


melody = Note(1/4) / [
    0, 5, 1/2, 0, 3, 1/2, 1, 0, 11, 1/2, 1
]

melody << Each(
        1, 1, 2, 3, 1, 3, 2,
        1, 1, 2, 3, 1, 7,
        1, 1, 2, 3, 4, 3, 2, 1,
        7, 5, 6, 7, 1, 1
    )**Degree() << Octave(4)


chords = Chord("F", Bars(3)) * Chord("C", Bars(1)) * Chord("F", Bars(1)) * Chord("Bb", Bars(1)) * Chord("C", Bars(1)) * Chord("F", Bars(1)) \
    << Channel(2) << Octave(3) << Velocity(50) >> Smooth(4) << Gate(.99)

yankee_doodle = melody + chords << Title("Yankee Doodle")

yankee_doodle * 2 >> Plot()
