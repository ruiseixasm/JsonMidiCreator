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


ProgramChange("Percussive organ", Channel(1)) + ProgramChange("Bass", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('') << Quantization(1/2)



melody = Note(Beat(3)) / [
    N8("E"), "D",               # 0
    N4("C"), 3,                 # 1
    1/2, R4(), N4("C"),         # 2
    "D", 3,                     # 3
    1/2, R4(), N4("D"),         # 4
    "E", 2, 1/8, 1,             # 5
    N4("F"), 1/8, 1, 1/4, 1/8, 1,   # 6
    N4("E"), "C", "D", 1,       # 7
    N2("C"), R4()               # 8
]

melody << Title("Grand Old Duke of York") << Velocity(85)



chords = Chord(1) / [
    C_2("C"),                   # 1/2
    C_2("G"),                   # 3/4
    C_1("C"), C_1("F"),         # 5/6
    C2("C"), C2("G"), C_1("C")  # 7/8
]

chords << Channel(2) << Octave(3) << Velocity(70) << Gate(.99)
chords >>= Smooth(4)


melody / 2 + chords.copy(Disable()) / 2 >> Plot(composition=chords / 2)


