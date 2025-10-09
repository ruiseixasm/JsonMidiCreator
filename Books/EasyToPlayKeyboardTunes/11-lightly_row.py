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


ProgramChange("Trumpet", Channel(1)) + ProgramChange("Mandolin", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('') << Quantization(1/2)

four_notes = N4() / 4
three_notes = N4()**2 / N2()
whole_note = N1()**1


melody = \
    three_notes**Each("5", "3", "3") >> Plot()
melody << Title("Melody") << Velocity(85) >> Plot(block=False)



chords = \
    R_1(1)**2 / R2() / \
    C2("D") / C_3("G") / C2("C") / C2("D") / \
    C_4("G") / C_1("D") / C_2("G") / C2("C") / C2("D") / C_1("G")

chords << Channel(2) << Octave(3) << Velocity(90) << Gate(.99)
chords >>= Smooth(4)


melody / 2 + chords.copy(Disable()) / 2 >> Plot(composition=chords / 2, title="O Little Town of Bethlehem")


