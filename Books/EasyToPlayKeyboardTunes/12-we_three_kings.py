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


ProgramChange("Electric grand piano", Channel(1)) + ProgramChange("Synth voice", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(6, 8) << KeySignature('') << Quantization(1/2)


# / has precedence over +

melody =     C_1(0, "A") + \
                N4(0, "E", o5) / N8("D", o5) / N4("C", o5) / N8("A") \
            + CD8(1, "G") / C_1(Bars(1.5), "A") + \
                N8(1)**["B", "C", "B"] / ND4("A") \
            + N4(2, "E") / N8("D") / N4("C") / N8("A") \
            + CD8(3, "G") / C_1("A") / C2("G") + \
                N8(3)**["B", "C", "B"] / ND4("A") / N4("C") / N8("C") / N4("D") / N8("D")


melody << Title("Melody") << Velocity(85) >> Plot(block=False)



chords = \
    C_1()**["C", "G", "C", "G", "C", "G"] / \
    C2("C") / C2("G") / C_1("C") / \
    C_2("G") / C_3("C") / \
    C_1("G") / \
    C2("C") / C2("G") / C_1("C")

chords << Channel(2) << Octave(3) << Velocity(60) << Gate(.99)
chords >>= Smooth(4)


melody / 2 + chords.copy(Disable()) / 2 >> Plot(composition=chords / 2, title="Lightly Row")


