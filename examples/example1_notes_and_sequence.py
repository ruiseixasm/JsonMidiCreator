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
settings << Tempo(110)

# Set the default single Clock for the entire Staff Duration
single_clock = Clock(Length(6)) / 1 << MidiTrack(0, "Clock Track") >> Save("json/_Save_1.1_jsonMidiCreator.json")
# single_clock = Clock(MidiTrack("Clock Track")) >> Save("json/_Save_1.1_jsonMidiCreator.json") >> Print()

# Multiple individual Notes creation and sequentially played
first_note = Note() << (Position() << Steps(3*4 + 2)) >> Save("json/_Save_1.1_first_note.json")
multi_notes = Rest(NoteValue(1/16 * (3*4 + 2))) / ((first_note + Rest()) * 3 >> Stack()) \
    << MidiTrack(1, "Piano") \
    >> Play(0) \
    >> Save("json/_Save_1.2_sequence.json") \
    >> Export("json/_Export_1.1_sequence.json")

first_note << "F" >> Play()
first_note << Load("json/_Save_1.1_first_note.json") >> Play()

Triplet() << (NoteValue() << Duration(1/16)) >> Play() >> Save("json/_Save_1.3_note_triad.json")

# Base Note creation to be used in the Sequencer
base_note = Note() << (NoteValue() << Dotted(1/64))
# base_note >> Play()
# Creation and configuration of a Track of notes
first_sequence = (base_note / 8 << Duration(1/16) >> Stack() << MidiTrack(2, "Drums") << Channel(10)) >> Save("json/_Save_1.4__first_sequence.json")
# first_sequence >> Play()

# Creation and configuration of second Sequencer
second_sequence = first_sequence >> Copy()
second_sequence /= Position(2)
second_sequence /= NoteValue(2)
some_rest = Rest(4/1)
second_sequence = Rest(4/1, Channel(10)) / second_sequence
second_sequence >> Save("json/_Save_1.5_second_sequence.json")
first_sequence = Rest(2/1, Channel(10)) / first_sequence
# second_sequence >> Play()

# Creations, aggregation of both Sequences in a Track element and respective Play
all_elements = Section(first_sequence) + second_sequence >> Save("json/_Save_1.6_all_elements.json") # HAS TO BECOME A SONG !!!
first_note += Beat(2)
all_elements += first_note + single_clock
all_elements >> Play(1) >> Export("json/_Export_1.2_all_elements.json")  # IT'S GONNA BE A SONG SAVE !!
# all_elements >> Print() >> Play(1) >> Export("json/_Export_1.2_all_elements.json")
