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

rest_play = (R(), P)

# Original Motif to work on its pitches
motif: Clip = Note() * 6 << Foreach(quarter, eight, eight, dotted_quarter, eight, whole) >> Stack()
motif << Foreach(1, 3, 4, 5, 4, 1)**Degree() << KeySignature(1, Minor())
melody: Clip = motif * 2 << MidiTrack("Melody")
settings << KeySignature(1, Minor())   # Sets the default Key Note configuration
melody \
    + Note(Position(2 + 1/8), Degree(2)) \
    + Note(Position(2 + 5/8), Degree(6)) \
    + Note(Position(2 + 6/8), Degree(5)) \
    + Note(Position(3 + 3/8), Degree(-2)) \
    + Note(Position(3 + 4/8), Degree(1)) \
        >> Link()
melody >> Play()
