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

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('#') << Quantization(1/2)


pickup_bar = \
    N4(Beat(3)) / 1
main_phrase = \
    N4("G")**3 / N4("A") / N8("B") / N8("A") / N8("B") / N8("C") / N4("D") / N4("B")
variant_phrase = \
    N4() / N8()**2 / N4()**2 / ND2() / N4() << Foreach("C", "B", "G", "A", "A", "G", "D")
central_period = \
    ND4("D") / N8("E")**5 / N8()**["G", "A", "B", "C"] / N4("D")**2 \
        << Match(0, "E")**Previous(Pipe(Degree()))**Subtract(1)**Pipe() \
        << Match(1, Beat(3))**Octave(4)

melody = pickup_bar * main_phrase * variant_phrase * central_period
melody << Title("O Little Town of Bethlehem") << Velocity(85)



chords = \
    C2("D", 3, Beat(2)) / C_3("G") / C2()**["C", "D"] / \
    C_4("G") / C1("D") / C_2("G") / C2()**["C", "D"] / C1("G")

chords << Channel(2) << Octave(3) << Velocity(70) << Gate(.99)
chords >>= Smooth(4)


melody / 2 + chords.copy(Disable()) / 2 >> Plot(composition=chords / 2)


