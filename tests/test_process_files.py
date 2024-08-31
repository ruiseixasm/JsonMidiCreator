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

####### TEST1 ############

reference_save_p1       = Load("json/testing/_Save_Play_p.1_first_note.json")
reference_export_p1     = Import("json/testing/_Export_Play_p.1_sequence.json")
result_save_p1          = Serialization()
result_export_p1        = PlayList()

# Global Staff setting up
staff << Tempo(110) << Measure(6)

# Set the default single Clock for the entire Staff Length
single_clock = Clock() >> Save("json/testing/_Save_1.1_jsonMidiCreator.json")

# Multiple individual Notes creation and sequentially played
first_note = Note() << (Position() << Beat(3) << Step(2)) << (Length() << NoteValue(1/2)) >> Save("json/testing/_Save_1.1_first_note.json")
multi_notes = Null() >> first_note * 3 >> od.LeftShift(result_save_p1) >> od.LeftShift(result_export_p1) \
    >> Save("json/testing/_Save_1.2_sequence.json") >> Export("json/testing/_Export_1.1_sequence.json")

print(reference_save_p1 == result_save_p1)

first_note << Key("F") >> Save("json/testing/_Save_Play_p.2_first_note.json") >> Export("json/testing/_Export_Play_p.2_sequence.json")
first_note << Load("json/testing/_Save_1.1_first_note.json") >> Save("json/testing/_Save_Play_p.3_first_note.json") >> Export("json/testing/_Export_Play_p.3_sequence.json")

Note3() << (Duration() << NoteValue(1/16)) >> Save("json/testing/_Save_Play_p.3_first_note.json") >> Export("json/testing/_Export_Play_p.3_sequence.json") >> Save("json/testing/_Save_1.3_note_triad.json")

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
all_elements >> Save("json/testing/_Save_Play_p.4_first_note.json") >> Export("json/testing/_Export_Play_p.4_sequence.json") >> Export("json/testing/_Export_1.2_all_elements.json")

############### TEST2 #######################

# Process Exported files
first_import = Import("json/testing/_Export_1.1_sequence.json")
second_import = Import("json/testing/_Export_1.2_all_elements.json")    # It has a clock!
(Position(0) >> first_import) + (Position(1) >> first_import) + (Position(2) >> first_import) + (Position(3) >> first_import) + (Position(4) >> second_import) \
    >> Export("json/testing/_Export_2.1_multiple_imports.json") >> Save("json/testing/_Save_Play_p.5_first_note.json") >> Export("json/testing/_Export_Play_p.5_sequence.json")

# Process Loaded files as Elements
first_load = Load("json/testing/_Save_1.1_first_note.json")
note_0 = Note() << (Position(0) >> first_load)
note_1 = Note() << (Position(1) >> first_load)
note_2 = Note() << (Position(2) >> first_load)
note_3 = Note() << (Position(3) >> first_load)
note_0 + note_1 + note_2 + note_3 >> Save ("json/testing/_Save_2.1_multiple_notes.json") >> Save("json/testing/_Save_Play_p.6_first_note.json") >> Export("json/testing/_Export_Play_p.6_sequence.json")

# Process Loaded files as Serialization
load_0 = Position(0) >> first_load >> Copy()
load_1 = Position(1) >> first_load >> Copy()
load_2 = Position(2) >> first_load >> Copy()
load_3 = Position(3) >> first_load >> Copy()
load_0 + load_1 + load_2 + load_3 >> Save ("json/testing/_Save_2.2_sequence_notes.json") >> Save("json/testing/_Save_Play_p.7_first_note.json") >> Export("json/testing/_Export_Play_p.7_sequence.json")


############### TEST3 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(1)
single_clock = Clock()

single_note = Note() << (Duration() << Measure(2)) >> Save("json/testing/_Save_Play_p.7.2_first_note.json") >> Export("json/testing/_Export_Play_p.7.2_sequence.json")
note_transposed = single_note + Key(5) >> Save("json/testing/_Save_Play_p.7.3_first_note.json") >> Export("json/testing/_Export_Play_p.7.3_sequence.json")

triplets_one = (Note3() << Key("E") << NoteValue(1/16)) * 8 + Iterate(1/2)**Beat() + single_clock \
    >> Save("json/testing/_Save_3.1_triple_note3.json") >> Save("json/testing/_Save_Play_p.8_first_note.json") >> Export("json/testing/_Export_Play_p.8_sequence.json")

triplets_two = (Note3() << Key("G") << NoteValue(1/16)) * 8 + Wrapper(Position())**Iterate(1/2)**Beat() + single_clock \
    >> Export("json/testing/_Export_3.1_triple_note3.json") >> Save("json/testing/_Save_Play_p.9_first_note.json") >> Export("json/testing/_Export_Play_p.9_sequence.json")

staff << Measure(2)
single_clock = Clock()

# Length needs to be adjusted because Elements are Stacked based on Length and not on Duration!
# A 1/16 triplet has a total length of a 1/8
triplets_two = triplets_one << Length(1/8) >> triplets_two
triplets_one + triplets_two + single_clock >> Save("json/testing/_Save_Play_p.10_first_note.json") >> Export("json/testing/_Export_Play_p.10_sequence.json")


############### TEST4 #######################

# Global Staff setting up
staff << Tempo(60)

chord = Chord() << NoteValue(2) << Gate(1) >> Save("json/testing/_Save_4.1_control_change.json")
controller = (Oscillator(ControlValue()) << Offset(64) << Amplitude(50) | ControlChange("Pan") * (2*16 + 1) << Iterate()**Step()) >> Save("json/testing/_Save_4.2_control_change.json")
    
chord + controller >> Save("json/testing/_Save_Play_p.10.2_first_note.json") >> Export("json/testing/_Export_Play_p.10.2_sequence.json") >> Export("json/testing/_Export_4.1_control_change.json")


oscillator = Oscillator(Pitch()) << Amplitude(8191 / 2)
pitch_bend = PitchBend() * (2*16 + 1) + Iterate()**Step() << Extractor(Pitch())**Wrapper(oscillator)**Wrapper(PitchBend())**Iterate(4)**Step()

chord + pitch_bend >> Save("json/testing/_Save_Play_p.10.3_first_note.json") >> Export("json/testing/_Export_Play_p.10.3_sequence.json") \
    >> Save("json/testing/_Save_4.2_pitch_bend.json") >> Export("json/testing/_Export_4.2_pitch_bend.json")


############### TEST5 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(7)

(Chord() * 7 << Type("7th")) + Increment()**Beat() + Increment()**Degree(0) \
    >> Save("json/testing/_Save_Play_p.11_first_note.json") >> Export("json/testing/_Export_Play_p.11_sequence.json")
(Chord("A") << Scale("minor") << Octave(3)) * 7 + Increment()**Beat() + Increment()**Degree(0) \
    >> Save("json/testing/_Save_Play_p.12_first_note.json") >> Export("json/testing/_Export_Play_p.12_sequence.json") \
        << Inversion(1) >> Save("json/testing/_Save_Play_p.13_first_note.json") >> Export("json/testing/_Export_Play_p.13_sequence.json")

Chord("C") << Type("13th") << Scale("Major") << Degree("Dominant") << Octave(3) << NoteValue(8) \
    >> Save("json/testing/_Save_Play_p.13.2_first_note.json") >> Export("json/testing/_Export_Play_p.13.2_sequence.json")
Chord("G") << Type("13th") << Scale("5th") << NoteValue(8) << Octave(3) \
    >> Save("json/testing/_Save_Play_p.13.2_first_note.json") >> Export("json/testing/_Export_Play_p.13.2_sequence.json")


############### TEST6 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(7)

(Chord() * 7 << Type("7th")) + Increment()**Beat() + Increment()**Even()**Degree(0) \
    >> Save("json/testing/_Save_Play_p.14_first_note.json") >> Export("json/testing/_Export_Play_p.14_sequence.json")
(Chord() * 7 << Type("7th")) + Increment()**Beat() + Iterate()**Even()**Degree(0) \
    >> Save("json/testing/_Save_Play_p.15_first_note.json") >> Export("json/testing/_Export_Play_p.15_sequence.json")


############### TEST7 #######################

# Global Staff setting up
staff << Tempo(120)

Chord() * 3 + Iterate()**Measure() + Iterate()**Inversion() << NoteValue(1) \
    >> Save("json/testing/_Save_Play_p.16_first_note.json") >> Export("json/testing/_Export_Play_p.16_sequence.json")
(Chord() * 4 << Type("7th")) + Iterate()**Measure() + Iterate()**Inversion() << NoteValue(1) << Gate(1) >> Export("json/testing/_Export_7.1_chord_inversion.json") \
    >> Save("json/testing/_Save_Play_p.17_first_note.json") >> Export("json/testing/_Export_Play_p.17_sequence.json")


(Chord() * 4 << Type("7th") << Sus("sus2") << Gate(1)) + Iterate()**Measure() + Iterate()**Inversion() << NoteValue(1) \
    >> Save("json/testing/_Save_Play_p.18_first_note.json") >> Export("json/testing/_Export_Play_p.18_sequence.json")


############### TEST8 #######################


# Global Staff setting up
staff << Tempo(120) << Measure(7)

Chord() * 13 + Iterate(1/2)**Beat() + Iterate()**KeyNote() << NoteValue(1/8) \
    >> Save("json/testing/_Save_Play_p.19_first_note.json") >> Export("json/testing/_Export_Play_p.19_sequence.json") << Even()**Velocity(50) \
        >> Save("json/testing/_Save_Play_p.20_first_note.json") >> Export("json/testing/_Export_Play_p.20_sequence.json")




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

play_list_1 + play_list_2 + play_list_3 + play_list_4 \
    >> Save("json/testing/_Save_Play_p.21_first_note.json") >> Export("json/testing/_Export_Play_p.21_sequence.json")


