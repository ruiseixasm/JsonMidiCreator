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
    + ProgramChange(Channel(14), Program("Cello")) >> Play()   # Sets the instruments

chords = Chord(Channel(11), 1/1, Velocity(90)) / 4 << Name("Chords")
chords << Nth(3)**(Minor(), TonicKey("E")) << Foreach("I", "4", "1", "5") << Octave(3)

tones = Note(Channel(14), 1/1, Velocity(60)) / 4 << Name("Tones")
tones << Foreach("I", "1", "7", "7") << Octave(4) << Nth(1, 2)**Octave(5)

skip_wise: Part = Part([chords, tones])
skip_wise * 4 << Name("Common Tones") >> Plot()

