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
src_path = os.path.join(os.path.dirname(__file__), '../../../../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

rest_play = ( Rest(), Play())

# Original Motif to work on its pitches
motif: Clip = Note() * 6 << Foreach(quarter, eight, eight, dotted_quarter, eight, whole) >> Stack()
motif << Foreach(1, 3, 4, 5, 4, 1)**Degree() << KeySignature(1, Minor())
melody: Clip = motif * 2 << MidiTrack("Melody")

chords: Clip = Chord() * 6 << Foreach(half, half, whole, half, half, whole) >> Stack()
chords << Foreach("Em", "Bm", "Em", "Am", "G", "Em") << MidiTrack("Harmony")
chords - Octave()

song: Section = melody + chords
song >> Play()
