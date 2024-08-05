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
from element import *

# Global Staff and Clock setting up
global_staff << Tempo(110) << Measure(6)
single_clock = Clock()
saveJsonMidiCreator(single_clock.getSerialization(), "_Clock_jsonMidiCreator.json")

# Multiple individual Notes creation and sequencially played
first_note = Note() << (Position() << Beat(3) << Step(2)) << (TimeLength() << NoteValue(1/2))
multi_notes = first_note * 3
(Void() >> multi_notes).play()
saveJsonMidiCreator(first_note.getSerialization(), "_Note_jsonMidiCreator.json")

# Base Note creation to be used in the Sequencer
base_note = Note() << (Duration() << NoteValue(1/16))

# Creation and configuration of first Sequencer
first_sequence = Sequence() << (Position() << Measure(1))
first_sequence << base_note * 8 // (TimeLength() << Step(1)) << Channel(10)
saveJsonMidiCreator(first_sequence.getSerialization(), "_Sequence_jsonMidiCreator.json")

# Creation and configuration of second Sequencer
second_sequence = first_sequence.copy()
second_sequence << (Position() << Measure(2))
second_sequence /= Inner()**(Position() << Identity() << Step(2))
second_sequence /= Inner()**(Duration() << Identity() << NoteValue(2))

# Creations, agregation of both Sequences in a MultiElements element and respective Play
all_elements = MultiElements(first_sequence) + MultiElements(second_sequence)
all_elements += (TimeLength() << Beat(2) >> first_note) + single_clock
all_elements.play()

# Saving in a Play file the all_elements play list
saveJsonMidiPlay(all_elements.getPlayList(), "example_play_file.json")
