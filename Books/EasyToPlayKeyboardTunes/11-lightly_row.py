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

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('') << Quantization(1/2)

four_notes = Note() / 4
three_notes = Note()**2 / Note(1/2, )
whole_note = Note(1/1)**1


melody = \
    three_notes**Each("5", "3", "3") / three_notes**Each("4", "2", "2") / \
    four_notes**Each("1", "2", "3", "4") / three_notes**"5" / \
    three_notes**Each("5", "3", "3") / three_notes**Each("4", "2", "2") / \
    four_notes**Each("1", "3", "5", "5") / whole_note**"3" / \
    four_notes**"2" / three_notes**Each("2", "3", "4") / \
    four_notes**"3" / three_notes**Each("3", "4", "5") / \
    three_notes**Each("5", "3", "3") / three_notes**Each("4", "2", "2") / \
    four_notes**Each("1", "3", "5", "5") / whole_note
melody << Title("Melody") << Velocity(85) >> Plot(block=False)



chords = \
    Chord(1., )**["C", "G", "C", "G", "C", "G"] / \
    Chord(1/2, "C") / Chord(1/2, "G") / Chord(1., "C") / \
    Chord(2., "G") / Chord(3., "C") / \
    Chord(1., "G") / \
    Chord(1/2, "C") / Chord(1/2, "G") / Chord(1., "C")

chords << Channel(2) << Octave(3) << Velocity(60) << Gate(.99)
chords >>= Smooth(4)


melody / 2 + chords.copy(Disable()) / 2 >> Plot(composition=chords / 2, title="Lightly Row")


