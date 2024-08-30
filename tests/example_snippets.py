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


# Global Staff setting up
staff << Tempo(90) << Measure(7)

# entire_scale = KeyScale("A")
# entire_scale << Mode("5th")
# print(entire_scale % list())
# print(entire_scale % str())

# single_chord = Chord("A") << Scale("minor") << Type("7th") << NoteValue(1/2)
# single_chord >> Play()

# single_triplet = Triplet(Note("B"), Note("F"), Note("G")) << Gate(0.75)
# single_triplet >> Play(True)

# single_triplet = Triplet(Note("C"), Note("G"), Note("F")) << Gate(0.75)
# single_triplet >> Play(True)

# tuplet = Tuplet( Note("C"), Note("F"), Note("G"), Note("C") )
# tuplet % Division() % int() >> Print()

retrigger = Retrigger("G") << Gate(.9)
retrigger << NoteValue(1) >> Play(True) >> Export("json/_Export_s.1_snippets_retirgger.json")
retrigger << Swing(.75) >> Play(True) >> Export("json/_Export_s.2_snippets_retirgger.json")

retrigger << Division(5) >> Play(True) >> Export("json/_Export_s.3_snippets_retirgger.json")

