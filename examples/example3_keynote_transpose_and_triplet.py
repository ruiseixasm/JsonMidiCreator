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
staff << Tempo(120) << Measures(1)
single_clock = Clock() * 1 << MidiTrack(0, "Clock Track")

single_note = Note() << (Duration() << Measures(2)) >> Play()
note_transposed = single_note + 5.0 >> Play()

triplets_one = (Note3("E") << Duration(1/16)) * 8
triplets_one + single_clock >> Save("json/_Save_3.1_triple_note3.json") >> Play(True)

triplets_two = (Note3("G") << Duration(1/16)) * 8
triplets_two + single_clock >> Export("json/_Export_3.1_triple_note3.json") >> Play(True)

staff << Measures(2)

# Duration needs to be adjusted because Elements are Stacked based on Duration and not on Duration!
# A 1/16 triplet has a total duration of a 1/8
single_clock >> triplets_one >> triplets_two >> Play(True)

# triplets remain a sequence. Frames don't operate on Songs!!
triplets = (triplets_one >> triplets_two) + Equal(Beats(1))**Semitone(2)
triplets >> single_clock >> Play(True)
