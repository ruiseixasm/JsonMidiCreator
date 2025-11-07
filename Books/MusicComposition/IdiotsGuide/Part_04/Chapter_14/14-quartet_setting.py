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

settings << KeySignature('#')

ProgramChange(Channel(11), Program("Violin")) \
    + ProgramChange(Channel(12), Program("Violin")) \
    + ProgramChange(Channel(13), Program("Viola")) \
    + ProgramChange(Channel(14), Program("Cello")) >> Play()   # Sets the instruments

violin_1 = Note(Channel(11)) / [1/4, 1/8, 0, 1/4, 0, 1/8, 0, 1/4, 1/2, 1/4, 1/8, 0, 1/4, 0, 1/2, 0] << Name("Violin 1")
violin_1 >>= Match(1/4, Beat(0))**Rest()
violin_1 += InputType(Note)**Foreach(2, 3, 2, 1, 0, -1, 0, 1, 0, 1, 2, 4, 2, 1)**Degree()
# violin_1 >> Plot(block=False)

violin_2 = Note(Channel(12), Velocity(80)) / [1/1, 1/2, 0, 1/1, 1/2, 0] << Name("Violin 2")
violin_2 += Foreach(-3, -2, -1, -3, -5, -3)**Degree()
# violin_2 >> Plot(block=False)

viola = Note(Channel(13)) / [1/1, 1/2] << Name("Viola")
viola[1] /= 6
viola << Previous(Pipe(Degree()), first_null=False)**Add(-5, 1, 1, -2, 4, 1, 1)**Pipe()   # Pipe does an Absolute setting of Degree
# viola += Foreach(-5, -4, -3, -5, -1, 0, 1)**Degree()
# viola >> Plot(block=False)

cello = Note(Channel(14), Octave(3), 1/2, Velocity(70)) / 8 << Name("Cello")
cello += Foreach(0, -3, 1, 4, 0, 2, -2, -3)**Degree()
# cello >> Plot(block=False)


quartet: Section = Section([violin_1, violin_2, viola, cello])
quartet * 4 << Name("Quartet") >> Plot()
