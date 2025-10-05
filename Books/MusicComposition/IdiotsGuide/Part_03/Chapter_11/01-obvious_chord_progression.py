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


settings << "##"
Key() % str() >> Print()
single_notes = Note() * 14 << Foreach(quarter, eight, eight, quarter, quarter, dotted_quarter, sixteenth, half,
                                 quarter, eight, eight, quarter, quarter, whole)
single_notes << Foreach("I", "ii", "I", "viiº", "V", "vi", "viiº", "vi", "IV", "V", "IV", "iii", "IV", "V") << Octave(5)) >> Smooth()
single_notes >> Rest >> P
chords = Chord(1/1) * 4
chords << Foreach("I", "vi", "IV", "V7")
settings << 60.0
chords >> Rest >> P
settings << 100.0
single_notes + chords >> L >> Rest >> P
