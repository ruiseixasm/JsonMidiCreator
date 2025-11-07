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


settings << Tempo(160)

ProgramChange(Channel(11), Program("Violin")) \
    + ProgramChange(Channel(12), Program("Violin")) \
    + ProgramChange(Channel(13), Program("Viola")) \
    + ProgramChange(Channel(14), Program("Cello")) >> Play()   # Sets the instruments

violin_1 = Note(Channel(11), 1/1, Octave(5), Velocity(90)) / 4 << Name("Violin 1")
violin_1 << Foreach("I", "2", "3", "4")

violin_2 = Note(Channel(12), 1/1, Velocity(70)) / 4 << Name("Violin 2")
violin_2 << Foreach("V", "6", "7", "1") << Nth(4)**Octave(5)

viola = Note(Channel(13), 1/1, Velocity(60)) / 4 << Name("Viola")
viola << Foreach("iii", "4", "5", "6")

cello = Note(Channel(14), Octave(3), 1/1, Velocity(60)) / 4 << Name("Cello")
cello << Foreach("I", "2", "3", "4")

viola >>= Smooth()
cello >>= Smooth(3)

skip_wise: Section = Section([violin_1, violin_2, viola, cello])
skip_wise * 4 << Name("Same Direction") >> Plot(block=False)


violin_1    << Octave(5)    << Foreach("5", "4", "5", "4")
violin_2    << Octave(4)    << Foreach("1", "6", "7", "6")          << Nth(1)**Octave(5)
viola       << Octave(4)    << Foreach("3", "4", "3", "1")
cello       << Octave(3)    << Foreach("1", "2", "3", "4")

step_wise: Section = Section([violin_1, violin_2, viola, cello])
step_wise * 4 << Name("Opposite Directions") >> Plot()


