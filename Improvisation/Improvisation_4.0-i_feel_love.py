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
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

# https://youtu.be/sIBSN1_9Geo?si=_AW-FASDVtHK8irY

# Global Staff setting up
defaults << Tempo(120)
defaults << Minor()

# C - G - A# | A minor with Tonic C
KeyScale(Tonic("C"), 2.0) >> P
first_notes = Note("C", 1/8) * 3 << Foreach("C", "G", "A")**Key() << Duration(1/16)
first_notes[0] % Degree() % int() >> Print()
first_notes[1] % Degree() % int() >> Print()
first_notes[2] % Degree() % int() >> Print()
# first_notes >> P

# Rest() >> P
second_notes = first_notes + Step(1)
# second_notes >> P

# Rest() >> P
patter_notes = first_notes + second_notes + Even()**Octave(1)

final_pattern = patter_notes.filter(Nth(1, 2)) / patter_notes / 2


final_pattern * 8 >> P >> MidiExport("Midi/improvisation_4.0.mid")

