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

result_save         = Serialization()
result_export       = PlayList()
results_list        = []

####### TEST1 ############

# Global Staff setting up
staff << Tempo(110) << Measure(6)

# Set the default single Clock for the entire Staff Length
single_clock = Clock() >> Save("json/testing/_Save_1.1_jsonMidiCreator.json")

# Multiple individual Notes creation and sequentially played
original_save       = Load("json/testing/_Save_Play_p.1_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.1_sequence.json")
first_note = Note() << (Position() << Beat(3) << Step(2)) << (Length() << NoteValue(1/2)) >> Save("json/testing/_Save_1.1_first_note.json")
multi_notes = Null() >> first_note * 3 >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    >> Save("json/testing/_Save_1.2_sequence.json") >> Export("json/testing/_Export_1.1_sequence.json")
results_list.append({
    "test":     "TEST 1.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.2_sequence.json")
first_note << Key("F") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 1.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.3_sequence.json")
first_note << Load("json/testing/_Save_1.1_first_note.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 1.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.3.1_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.3.1_sequence.json")
Note3() << (Duration() << NoteValue(1/16)) >> od.LeftShift(result_save) >> od.LeftShift(result_export) >> Save("json/testing/_Save_1.3_note_triad.json")
results_list.append({
    "test":     "TEST 1.4",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

# Base Note creation to be used in the Sequencer
base_note = Note() << (Duration() << Dotted(1/64))
# Creation and configuration of a Sequence of notes
first_sequence = base_note * 8 // Step(1) << Measure(2) << Channel(10) >> Save("json/testing/_Save_1.4__first_sequence.json")

# Creation and configuration of second Sequencer
second_sequence = first_sequence >> Copy()
second_sequence << Measure(4)
second_sequence /= Position() << Identity() << Step(2)
second_sequence /= Duration() << Identity() << NoteValue(2)
second_sequence >> Save("json/testing/_Save_1.5_second_sequence.json")

# Creations, aggregation of both Sequences in a Sequence element and respective Play
all_elements = Sequence(first_sequence) + Sequence(second_sequence)
all_elements += (Length() << Beat(2) >> first_note) + single_clock
original_save       = Load("json/testing/_Save_Play_p.4_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.4_sequence.json")
all_elements >> od.LeftShift(result_save) >> od.LeftShift(result_export) >> Export("json/testing/_Export_1.2_all_elements.json")
results_list.append({
    "test":     "TEST 1.5",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

############### TEST2 #######################

# Process Exported files
first_import = Import("json/testing/_Export_1.1_sequence.json")
second_import = Import("json/testing/_Export_1.2_all_elements.json")    # It has a clock!
original_save       = Load("json/testing/_Save_Play_p.5_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.5_sequence.json")
(Position(0) >> first_import) + (Position(1) >> first_import) + (Position(2) >> first_import) + (Position(3) >> first_import) + (Position(4) >> second_import) \
    >> Export("json/testing/_Export_2.1_multiple_imports.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 2.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

# Process Loaded files as Elements
first_load = Load("json/testing/_Save_1.1_first_note.json")
note_0 = Note() << (Position(0) >> first_load)
note_1 = Note() << (Position(1) >> first_load)
note_2 = Note() << (Position(2) >> first_load)
note_3 = Note() << (Position(3) >> first_load)
original_save       = Load("json/testing/_Save_Play_p.6_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.6_sequence.json")
note_0 + note_1 + note_2 + note_3 >> Save ("json/testing/_Save_2.1_multiple_notes.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 2.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

# Process Loaded files as Serialization
load_0 = Position(0) >> first_load >> Copy()
load_1 = Position(1) >> first_load >> Copy()
load_2 = Position(2) >> first_load >> Copy()
load_3 = Position(3) >> first_load >> Copy()
original_save       = Load("json/testing/_Save_Play_p.7_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.7_sequence.json")
load_0 + load_1 + load_2 + load_3 >> Save ("json/testing/_Save_2.2_sequence_notes.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 2.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST3 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(1)
single_clock = Clock()

original_save       = Load("json/testing/_Save_Play_p.7.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.7.2_sequence.json")
single_note = Note() << (Duration() << Measure(2)) >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 3.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.7.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.7.3_sequence.json")
note_transposed = single_note + Key(5) >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 3.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.8_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.8_sequence.json")
triplets_one = (Note3() << Key("E") << NoteValue(1/16)) * 8 + Iterate(1/2)**Beat() + single_clock \
    >> Save("json/testing/_Save_3.1_triple_note3.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 3.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.9_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.9_sequence.json")
triplets_two = (Note3() << Key("G") << NoteValue(1/16)) * 8 + Wrapper(Position())**Iterate(1/2)**Beat() + single_clock \
    >> Export("json/testing/_Export_3.1_triple_note3.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 3.4",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

staff << Measure(2)
single_clock = Clock()

# Length needs to be adjusted because Elements are Stacked based on Length and not on Duration!
# A 1/16 triplet has a total length of a 1/8
triplets_two = triplets_one << Length(1/8) >> triplets_two
original_save       = Load("json/testing/_Save_Play_p.10_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.10_sequence.json")
triplets_one + triplets_two + single_clock >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 3.5",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST4 #######################

# Global Staff setting up
staff << Tempo(60)

chord = Chord() << NoteValue(2) << Gate(1) >> Save("json/testing/_Save_4.1_control_change.json")
controller = (Oscillator(ControlValue()) << Offset(64) << Amplitude(50) | ControlChange("Pan") * (2*16 + 1) << Iterate()**Step()) >> Save("json/testing/_Save_4.2_control_change.json")

original_save       = Load("json/testing/_Save_Play_p.10.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.10.2_sequence.json")
chord + controller >> od.LeftShift(result_save) >> od.LeftShift(result_export) >> Export("json/testing/_Export_4.1_control_change.json")
results_list.append({
    "test":     "TEST 4.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


oscillator = Oscillator(Pitch()) << Amplitude(8191 / 2)
pitch_bend = PitchBend() * (2*16 + 1) + Iterate()**Step() << Extractor(Pitch())**Wrapper(oscillator)**Wrapper(PitchBend())**Iterate(4)**Step()

original_save       = Load("json/testing/_Save_Play_p.10.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.10.3_sequence.json")
chord + pitch_bend >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    >> Save("json/testing/_Save_4.2_pitch_bend.json") >> Export("json/testing/_Export_4.2_pitch_bend.json")
results_list.append({
    "test":     "TEST 4.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST5 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(7)

original_save       = Load("json/testing/_Save_Play_p.11_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.11_sequence.json")
(Chord() * 7 << Type("7th")) + Increment()**Beat() + Increment()**Degree(0) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 5.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.13_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.13_sequence.json")
(Chord("A") << Scale("minor") << Octave(3)) * 7 + Increment()**Beat() + Increment()**Degree(0) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    << Inversion(1) >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 5.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.13.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.13.2_sequence.json")
Chord("C") << Type("13th") << Scale("Major") << Degree("Dominant") << Octave(3) << NoteValue(8) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 5.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.13.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.13.3_sequence.json")
Chord("G") << Type("13th") << Scale("5th") << NoteValue(8) << Octave(3) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 5.4",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST6 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(7)

original_save       = Load("json/testing/_Save_Play_p.14_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.14_sequence.json")
(Chord() * 7 << Type("7th")) + Increment()**Beat() + Increment()**Even()**Degree(0) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 6.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.15_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.15_sequence.json")
(Chord() * 7 << Type("7th")) + Increment()**Beat() + Iterate()**Even()**Degree(0) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 6.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST7 #######################

# Global Staff setting up
staff << Tempo(120)

original_save       = Load("json/testing/_Save_Play_p.16_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.16_sequence.json")
Chord() * 3 + Iterate()**Measure() + Iterate()**Inversion() << NoteValue(1) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 7.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.17_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.17_sequence.json")
(Chord() * 4 << Type("7th")) + Iterate()**Measure() + Iterate()**Inversion() << NoteValue(1) << Gate(1) >> Export("json/testing/_Export_7.1_chord_inversion.json") \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 7.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.18_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.18_sequence.json")
(Chord() * 4 << Type("7th") << Sus("sus2") << Gate(1)) + Iterate()**Measure() + Iterate()**Inversion() << NoteValue(1) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 7.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST8 #######################


# Global Staff setting up
staff << Tempo(120) << Measure(7)

original_save       = Load("json/testing/_Save_Play_p.19_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.19_sequence.json")
chord_play = Chord() * 13 + Iterate(1/2)**Beat() + Iterate()**KeyNote() << NoteValue(1/8) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export) << Even()**Velocity(50)
results_list.append({
    "test":     "TEST 8.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.20_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.20_sequence.json")
chord_play >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 8.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST9 #######################


# Global Staff setting up
staff << Tempo(240) << Measure(7)

# All Sharps(#) of the Major Scale on the Circle of Fifths
play_list_1 = PlayList() << (Position(0) >> (KeyScale("C") << Scale("Major")) * 8 
    + Iterate(Scale("Major") % Transposition("5th"))**Key() + Iterate()**Measure() 
    << NoteValue(1) << Velocity(70))

# All Fats(b) of the Major Scale on the Circle of Fifths
play_list_2 = PlayList() << (Position(8) >> (KeyScale("C") << Scale("Major")) * 8 
    + Iterate(Scale("Major") % Transposition("4th"))**Key() + Iterate()**Measure() 
    << NoteValue(1) << Velocity(70))

# All Sharps(#) of the minor Scale on the Circle of Fifths
play_list_3 = PlayList() << (Position(16) >> (KeyScale("A") << Scale("minor")) * 8 
    + Iterate(Scale("minor") % Transposition("5th"))**Key() + Iterate()**Measure() 
    << NoteValue(1) << Velocity(70))

# All Fats(b) of the minor Scale on the Circle of Fifths
play_list_4 = PlayList() << (Position(24) >> (KeyScale("A") << Scale("minor")) * 8 
    + Iterate(Scale("minor") % Transposition("4th"))**Key() + Iterate()**Measure() 
    << NoteValue(1) << Velocity(70))

original_save       = Load("json/testing/_Save_Play_p.21_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.21_sequence.json")
play_list_1 + play_list_2 + play_list_3 + play_list_4 \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "test":     "TEST 9.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

for test in results_list:
    if test['save'] and test['export']:
        print(f"{test['test']}: \t{test['save']} | {test['export']}")
    else:
        print(f"{test['test']}: \t\t\t{test['save']} | {test['export']}")

