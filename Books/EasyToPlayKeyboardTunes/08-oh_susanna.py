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


ProgramChange("Harmonica", Channel(1)) + ProgramChange("Accordion", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('#') << Quantization(1/4)



upbeat = Note(1/8, Beat(3)) / 2
phrase_1 = Note() / [
        "3", "5", 3/8, N8("6"),
        N4("5"), "3", D4("1"), N8("2"),
        N4("3"), 1, "2", "1"
    ]
phrase_2 = Note() / [
        N2("2"), Rest(), {0: N4("1")}, "2",
        N4("3"), "5", 3/8, N8("6"),
        N4("5"), "3", D4("1"), N8("2"),
        N4("3"), 1, "2", 1
    ]
phrase_3 = Note() / [
        N1(),
        N2("4"), 1,
        N4("6"), 1/2, 1/4,
        "5", 1, "3", "1"
    ]
phrase_4 = Note(3/4) / [
        1
    ]

melody = upbeat * phrase_1 * phrase_2 * phrase_3 * phrase_2 * phrase_4
melody << Title("Melody") << Velocity(85)



chords = Chord(1, "G", Bars(3)) / [
        0,
        (1/1, "D"),
        (2/1, "G"),
        (1/1, "D"), "G",
        (2/1, "C"),
        (1/1, "G"), (1/1, "D"),
        (2/1, "G"),
        (1/1, "D"), "G"
    ]

chords << Title("Chords") << Channel(2) << Octave(3) << Velocity(50) << Gate(.99)
chords >>= Smooth(4)


silent_night = melody + chords << Title("Oh Susanna")
(melody + chords.copy(Disable())) * 2 >> Plot(composition=chords * 2)


