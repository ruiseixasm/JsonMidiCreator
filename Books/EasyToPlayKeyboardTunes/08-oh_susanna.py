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


ProgramChange("Electric piano 2", Channel(1)) + ProgramChange("Contrabass", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('#') << Quantization(1/4)



melody = Note(Beat(3)) / [
    #   0    1
        1/8, "2",
    #   2           3    4    5             6           7    8           9
        (1/4, "3"), "5", 3/8, (1/8, "6"),
                                            (1/4, "5"), "3", (3/8, "G"), (1/8, "2"),
    #   10          11 12   13              14          15      16         17
        (1/4, "3"), 1, "2", "1",
                                            (1/2, "2"), Rest(), {-3: 1/8}, "2",
        (1/4, "3"), "5", 3/8, (1/8, "6"),
                                            (1/4, "5"), "3", (3/8, "1"), (1/8, "2"),
        (1/4, "3"), 1, "2", 1,
                                            (1/1, "1"),
        (1/2, "4"), 1,
                                            (1/4, "6"), 1/2, 1/4,
        (1/4, "5"), 1, "3", "1",
                                            (1/2, "2"), Rest(), {0: Nul}, "2",
        {2: Nul}, {3: Nul}, {4: Nul}, {5: Nul},
                                            {6: Nul}, {7: Nul}, {8: Nul}, {9: Nul},
        {10: Nul}, {11: Nul}, {12: Nul}, {13: Nul},
                                            (3/4, "1")

]
melody << Title("Melody") << Velocity(85)



chords = \
    Chord("F", Bars(1)) * Chord("C", Bars(2)) * Chord("F", Bars(2)) * Chord("C", Bars(2)) * Chord("F", Bars(1)) \
        << Title("Chords") << Channel(2) << Octave(2) << Velocity(40) << Gate(.99)
chords >>= Smooth(4)


silent_night = melody + chords << Title("Oh Susanna")
(melody + chords.copy(Disable())) * 2 >> Plot(composition=chords * 2)


