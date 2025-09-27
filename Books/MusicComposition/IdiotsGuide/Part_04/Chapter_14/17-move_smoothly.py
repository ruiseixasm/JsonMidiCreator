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


ProgramChange(Channel(11), Program("Violin")) \
    + ProgramChange(Channel(12), Program("Violin")) \
    + ProgramChange(Channel(13), Program("Viola")) \
    + ProgramChange(Channel(14), Program("Cello")) >> Play()   # Sets the instruments

violin_1 = Note(Channel(11), 1/1, Octave(5)) / 4 << Name("Violin 1")
violin_1 << Foreach("1", "3", "6", "1")

violin_2 = Note(Channel(12), Velocity(80), 1/1) / 4 << Name("Violin 2")
violin_2 << Foreach("V", "vii", "iii", "vi")

viola = Note(Channel(13), 1/1) / 4 << Name("Viola")
viola << Foreach("3", "7", "1", "4")

cello = Note(Channel(14), Octave(3), 1/1, Velocity(70)) / 4 << Name("Cello")
cello << Foreach("I", "iii", "vi", "iv")

violin_2 >>= Smooth()
viola >>= Smooth()
cello >>= Smooth(3)

static_voicing: Part = Part([violin_1, violin_2, viola, cello])
static_voicing * 4 << Name("Skip Wise Motion") >> Plot()

