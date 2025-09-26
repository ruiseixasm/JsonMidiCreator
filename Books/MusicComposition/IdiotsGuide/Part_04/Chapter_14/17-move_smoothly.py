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

violin_1 = Note(Channel(11), 1/1) / 4 << Name("Violin 1") << Nth(2, 3)**(Minor(), Degree(-1)) << Nth(3, 4)**Foreach("D", "G")**TonicKey()
violin_1 << Degree(5)   # Static Voicing

violin_2 = Note(Channel(12), Velocity(80), 1/1) / 4 << Name("Violin 2") << Nth(2, 3)**(Minor(), Degree(-1)) << Nth(3, 4)**Foreach("D", "G")**TonicKey()
violin_2 << Degree(3)   # Static Voicing

viola = Note(Channel(13), 1/1) / 4 << Name("Viola") << Nth(2, 3)**(Minor(), Degree(-1)) << Nth(3, 4)**Foreach("D", "G")**TonicKey()
viola << Degree(1)      # Static Voicing

cello = Note(Channel(14), Octave(3), 1/1, Velocity(70)) / 4 << Name("Cello") << Nth(2, 3)**(Minor(), Degree(-1)) << Nth(3, 4)**Foreach("D", "G")**TonicKey()
cello << Degree(1)      # Static Voicing

# violin_1 + violin_2 + viola + cello >> Plot(block=False)
violin_1 >>= Smooth()
violin_2 >>= Smooth()
viola >>= Smooth()
cello >>= Smooth()

static_voicing: Part = Part([violin_1, violin_2, viola, cello])
static_voicing * 4 << Name("Static Voicing") >> Plot(block=False)

