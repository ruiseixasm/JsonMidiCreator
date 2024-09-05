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
staff << Tempo(110) << Measure(6)

# Set the default single Clock for the entire Staff Length
single_clock = Clock() >> Save("json/_Save_1.1_jsonMidiCreator.json") >> Print()

# Multiple individual Notes creation and sequentially played
first_note = Note() << (Position() << Step(3*4 + 2)) << (Length() << NoteValue(1/2)) >> Save("json/_Save_1.1_first_note.json")
multi_notes = Null() >> first_note * 3 >> Play(0) >> Save("json/_Save_1.2_sequence.json") >> Export("json/_Export_1.1_sequence.json")

# first_note << Key("F") >> Play()
# first_note << Load("json/_Save_1.1_first_note.json") >> Play()

# Note3() << (Duration() << NoteValue(1/16)) >> Play(1) >> Save("json/_Save_1.3_note_triad.json")

# # Base Note creation to be used in the Sequencer
# base_note = Note() << (Duration() << Dotted(1/64))
# # Creation and configuration of a Sequence of notes
# first_sequence = base_note * 8 // Step(1) << Measure(2) << Channel(10) >> Save("json/_Save_1.4__first_sequence.json")

# # Creation and configuration of second Sequencer
# second_sequence = first_sequence >> Copy()
# second_sequence << Measure(4)
# second_sequence /= Position() << Identity() << Step(2)
# second_sequence /= Duration() << Identity() << NoteValue(2)
# second_sequence >> Save("json/_Save_1.5_second_sequence.json")

# # Creations, aggregation of both Sequences in a Sequence element and respective Play
# all_elements = Sequence(first_sequence) + Sequence(second_sequence)
# all_elements += (Length() << Beat(2) >> first_note) + single_clock
# all_elements >> Print() >> Play(1) >> Export("json/_Export_1.2_all_elements.json")
