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
import time

result_save         = Serialization()
result_export       = Playlist()
results_list        = []

####### TEST1 ############

# Global Staff setting up
staff << Tempo(110) << Measure(6)

# Set the default single Clock for the entire Staff Duration
single_clock = Clock() * 1 << Track("Clock Track") >> Save("json/testing/_Save_1.1_jsonMidiCreator.json")

# Multiple individual Notes creation and sequentially played
original_save       = Load("json/testing/_Save_Play_p.1_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.1_sequence.json")
start_time = time.time()
first_note = Note() << (Position() << Step(3*4 + 2)) >> Save("json/testing/_Save_1.1_first_note.json")
multi_notes = Rest(NoteValue(Step(3*4 + 2))) >> (first_note + Rest()) * 3 << Track("Piano") >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    >> Save("json/testing/_Save_1.2_sequence.json") >> Export("json/testing/_Export_1.1_sequence.json") \
    >> Save("json/testing/_Save_Play_p.1_first_note_compare.json") >> Export("json/testing/_Export_Play_p.1_sequence_compare.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 1.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.2_sequence.json")
start_time = time.time()
first_note << "F" >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    >> Save("json/testing/_Save_Play_p.2_first_note_compare.json") >> Export("json/testing/_Export_Play_p.2_sequence_compare.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 1.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.3_sequence.json")
start_time = time.time()
first_note << Load("json/testing/_Save_1.1_first_note.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 1.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.3.1_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.3.1_sequence.json")
start_time = time.time()
Note3(Track("Piano")) << (Duration() << NoteValue(1/16)) >> od.LeftShift(result_save) >> od.LeftShift(result_export) >> Save("json/testing/_Save_1.3_note_triad.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 1.4",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.4_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.4_sequence.json")
start_time = time.time()
# Base Note creation to be used in the Sequencer
base_note = Note() << (Duration() << Dotted(1/64))
# Creation and configuration of a Sequence of notes
first_sequence = (base_note * 8 // Step(1) << Track("Drums") << Channel(10)) >> Save("json/testing/_Save_1.4__first_sequence.json")

# Creation and configuration of second Sequencer
second_sequence = first_sequence >> Copy()
second_sequence /= Position(2)
second_sequence /= Duration(2)
some_rest = Rest(4/1)
second_sequence = Rest(4/1) >> second_sequence
second_sequence >> Save("json/testing/_Save_1.5_second_sequence.json")
first_sequence = Rest(2/1) >> first_sequence

# Creations, aggregation of both Sequences in a Sequence element and respective Play
all_elements = Song(first_sequence) + second_sequence
all_elements += (Duration() << Beat(2) >> first_note) + single_clock
all_elements >> od.LeftShift(result_save) >> od.LeftShift(result_export) >> Export("json/testing/_Export_1.2_all_elements.json") \
    >> Save("json/testing/_Save_Play_p.4_first_note_compare.json") >> Export("json/testing/_Export_Play_p.4_sequence_compare.json")
original_save >> Save("json/file1.json")
result_save >> Save("json/file2.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 1.5",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


staff >> Save("json/testing/_Save_Staff_process.json")


############### TEST2 #######################

# Process Exported files
original_save       = Load("json/testing/_Save_Play_p.5_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.5_sequence.json")
start_time = time.time()
first_import = Import("json/testing/_Export_1.1_sequence.json")
second_import = Import("json/testing/_Export_1.2_all_elements.json")    # It has a clock!
first_import >> first_import >> first_import >> first_import >> second_import \
    >> Export("json/testing/_Export_2.1_multiple_imports.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    >> Save("json/testing/_Save_Play_p.5_first_note_compare.json") >> Export("json/testing/_Export_Play_p.5_sequence_compare.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 2.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


original_save       = Load("json/testing/_Save_Play_p.6_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.6_sequence.json")
start_time = time.time()

# Process Loaded files as Elements
first_load = Load("json/testing/_Save_1.1_first_note.json")
note_0 = Note() << first_load
note_1 = Note() << first_load
note_2 = Note() << first_load
note_3 = Note() << first_load
note_0 >> note_1 >> note_2 >> note_3 >> Save ("json/testing/_Save_2.1_multiple_notes.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 2.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


original_save       = Load("json/testing/_Save_Play_p.7_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.7_sequence.json")
start_time = time.time()

# Process Loaded files as Serialization
load_0 = first_load >> Copy()
load_1 = first_load >> Copy()
load_2 = first_load >> Copy()
load_3 = first_load >> Copy()
load_0 >> load_1 >> load_2 >> load_3 >> Save ("json/testing/_Save_2.2_sequence_notes.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 2.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST3 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(1)
single_clock = Clock() * 1 << Track("Clock Track")

original_save       = Load("json/testing/_Save_Play_p.7.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.7.2_sequence.json")
start_time = time.time()
single_note = Note() << (Duration() << Measure(2)) >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 3.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.7.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.7.3_sequence.json")
start_time = time.time()
note_transposed = single_note + 5.0 >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 3.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.8_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.8_sequence.json")
start_time = time.time()
triplets_one = (Note3("E") << Duration(1/16)) * 8
triplets_one + single_clock >> Save("json/testing/_Save_3.1_triple_note3.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 3.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.9_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.9_sequence.json")
start_time = time.time()
triplets_two = (Note3("G") << Duration(1/16)) * 8
triplets_two + single_clock >> Export("json/testing/_Export_3.1_triple_note3.json") >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 3.4",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


original_save       = Load("json/testing/_Save_Play_p.10_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.10_sequence.json")
start_time = time.time()

staff << Measure(2)

# Duration needs to be adjusted because Elements are Stacked based on Duration and not on Duration!
# A 1/16 triplet has a total duration of a 1/8
single_clock >> triplets_one >> triplets_two >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    >> Save("json/testing/_Save_Play_p.10_first_note_compare.json") >> Export("json/testing/_Export_Play_p.10_sequence_compare.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 3.5",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.10.1_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.10.1_sequence.json")
start_time = time.time()

# triplets remain a sequence. Frames don't operate on Songs!!
triplets = (triplets_one >> triplets_two) + Equal(Beat(1))**Semitone(2)
triplets >> single_clock >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 3.6",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST4 #######################

original_save       = Load("json/testing/_Save_Play_p.10.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.10.2_sequence.json")
start_time = time.time()
# Global Staff setting up
staff << Tempo(60)

chord = Chord() << NoteValue(2) << Gate(1) >> Save("json/testing/_Save_4.1_control_change.json")
controller = ControlChange("Pan") * (2*16 + 1) << Iterate()**Measure()**NoteValue()**Step()
controller = (Oscillator(Value()) << Offset(64) << Amplitude(50) | controller) >> Save("json/testing/_Save_4.2_control_change.json")

chord + controller >> od.LeftShift(result_save) >> od.LeftShift(result_export) >> Export("json/testing/_Export_4.1_control_change.json") \
    >> Save("json/testing/_Save_Play_p.10.2_first_note_compare.json") >> Export("json/testing/_Export_Play_p.10.2_sequence_compare.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 4.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.10.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.10.3_sequence.json")
start_time = time.time()

oscillator = Oscillator(Bend()) << Amplitude(8191 / 2)
pitch_bend = (PitchBend() * (2*16 + 1) + Iterate()**Step()) << Extract(Bend())**Wrap(oscillator)**Wrap(PitchBend())**Iterate(4)**Step()

chord + pitch_bend >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    >> Save("json/testing/_Save_4.2_pitch_bend.json") >> Export("json/testing/_Export_4.2_pitch_bend.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 4.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST5 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(7)

original_save       = Load("json/testing/_Save_Play_p.11_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.11_sequence.json")
start_time = time.time()
(Chord() * 7 << Size("7th")) << Iterate()**Add(1)**Degree() << Increment()**Mode() \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 5.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.13_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.13_sequence.json")
start_time = time.time()
(Chord("A") << Scale("minor") << Octave(3)) * 7 << Iterate()**Add()**Degree() << Increment()**Mode() \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    << Inversion(1) >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 5.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.13.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.13.2_sequence.json")
start_time = time.time()
Chord("C") << Size("13th") << Scale("Major") << Degree("Dominant") << Mode("5th") << Octave(3) << NoteValue(8) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 5.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.13.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.13.3_sequence.json")
start_time = time.time()
Chord("G") << Size("13th") << Scale("5th") << NoteValue(8) << Octave(3) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 5.4",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST6 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(7)

original_save       = Load("json/testing/_Save_Play_p.14_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.14_sequence.json")
start_time = time.time()
(Chord(1/4) * 7 << Size("7th")) << Even()**Iterate()**Add(2)**Degree() << Even()**Increment()**Mode(2) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 6.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.15_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.15_sequence.json")
start_time = time.time()
(Chord(1/4) * 7 << Size("7th")) << Iterate()**Even()**Add()**Degree() << Increment()**Even()**Mode() \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 6.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.15.2_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.15.2_sequence.json")
start_time = time.time()
all_chords = (Chord(1/4) * 7 << Size("7th"))
first_chords = all_chords | Beat(0)
first_chords << Degree(5) << Mode(5)
all_chords >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 6.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.15.3_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.15.3_sequence.json")
start_time = time.time()
first_chords << Degree() << Mode()
even_chords = all_chords | Even()**Operand()
even_chords << Degree(5) << Mode(5)
all_chords >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 6.4",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST7 #######################

# Global Staff setting up
staff << Tempo(120)

original_save       = Load("json/testing/_Save_Play_p.16_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.16_sequence.json")
start_time = time.time()
(Chord() << Duration(1)) * 3 + Iterate()**Inversion() << NoteValue(1) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 7.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.17_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.17_sequence.json")
start_time = time.time()
((Chord() << Duration(1)) * 4 << Size("7th")) + Iterate()**Inversion() << NoteValue(1) << Gate(1) >> Export("json/testing/_Export_7.1_chord_inversion.json") \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 7.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.18_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.18_sequence.json")
start_time = time.time()
((Chord() << Duration(1)) * 4 << Size("7th") << Sus2() << Gate(1)) + Iterate()**Inversion() << NoteValue(1) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 7.3",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST8 #######################


# Global Staff setting up
staff << Tempo(120) << Measure(7)

original_save       = Load("json/testing/_Save_Play_p.19_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.19_sequence.json")
start_time = time.time()
chord_play = (Chord() << Duration(1/8)) * 13 + Iterate(1.0)**Key() << NoteValue(1/8) \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export) << Even()**Velocity(50)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 8.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

original_save       = Load("json/testing/_Save_Play_p.20_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.20_sequence.json")
start_time = time.time()
chord_play >> od.LeftShift(result_save) >> od.LeftShift(result_export)
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 8.2",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})


############### TEST9 #######################


original_save       = Load("json/testing/_Save_Play_p.21_first_note.json")
original_export     = Import("json/testing/_Export_Play_p.21_sequence.json")
start_time = time.time()
# Global Staff setting up
staff << Tempo(240) << Measure(7)

# All Sharps(#) of the Major Scale on the Circle of Fifths
play_list_1 = Playlist() << ((KeyScale("C") << Scale("Major") << Duration(1)) * 8 
    + Iterate(Scale("Major") % Transposition(5 - 1))**Semitone() 
    << NoteValue(1) << Velocity(70) << Octave(4))

# All Fats(b) of the Major Scale on the Circle of Fifths
play_list_2 = Playlist() << ((KeyScale("C") << Scale("Major") << Duration(1)) * 8 
    + Iterate(Scale("Major") % Transposition(4 - 1))**Semitone() 
    << NoteValue(1) << Velocity(70) << Octave(4))

# All Sharps(#) of the minor Scale on the Circle of Fifths
play_list_3 = Playlist() << ((KeyScale("A") << Scale("minor") << Duration(1)) * 8 
    + Iterate(Scale("minor") % Transposition(5 - 1))**Semitone() 
    << NoteValue(1) << Velocity(70) << Octave(4))

# All Fats(b) of the minor Scale on the Circle of Fifths
play_list_4 = Playlist() << ((KeyScale("A") << Scale("minor") << Duration(1)) * 8 
    + Iterate(Scale("minor") % Transposition(4 - 1))**Semitone() 
    << NoteValue(1) << Velocity(70) << Octave(4))

play_list_1 >> play_list_2 >> play_list_3 >> play_list_4 \
    >> od.LeftShift(result_save) >> od.LeftShift(result_export) \
    >> Save("json/testing/_Save_Play_p.21_first_note_compare.json") >> Export("json/testing/_Export_Play_p.21_sequence_compare.json")
results_list.append({
    "time_ms":  (time.time() - start_time) * 1000,
    "test":     "TEST 9.1",
    "save":     original_save == result_save,
    "export":   original_export == result_export
})

for test in results_list:
    if test['save'] and test['export']:
        print(f"{test['test']}: \t{test['save']} | {test['export']}\t\t{test['time_ms']:.0f} ms")
    else:
        print(f"{test['test']}: \t\t\t{test['save']} | {test['export']}\t\t{test['time_ms']:.0f} ms")
