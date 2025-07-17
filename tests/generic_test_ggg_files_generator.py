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

# Global Staff setting up
settings << Tempo(110)

# Set the default single Clock for the entire Staff Duration
single_clock = Clock(Length(6)) / 1 << MidiTrack(0, "Clock Track") >> Save("json/testing/_Save_1.1_jsonMidiCreator.json")

# Multiple individual Notes creation and sequentially played
first_note = Note(Steps(3*4 + 2)) >> Save("json/testing/_Save_1.1_first_note.json")
multi_notes = Rest(NoteValue(1/16 * (3*4 + 2))) / ((first_note + Rest()) * 3 >> Stack()) << MidiTrack(1, "Piano") >> Save("json/testing/_Save_Play_p.1_first_note.json") >> Export("json/testing/_Export_Play_p.1_sequence.json") \
    >> Save("json/testing/_Save_1.2_sequence.json") >> Export("json/testing/_Export_1.1_sequence.json")

first_note << "F" >> Save("json/testing/_Save_Play_p.2_first_note.json") >> Export("json/testing/_Export_Play_p.2_sequence.json")
first_note << Load("json/testing/_Save_1.1_first_note.json") >> Save("json/testing/_Save_Play_p.3_first_note.json") >> Export("json/testing/_Export_Play_p.3_sequence.json")

Triplet() << (NoteValue() << Duration(1/16)) >> Save("json/testing/_Save_Play_p.3.1_first_note.json") >> Export("json/testing/_Export_Play_p.3.1_sequence.json") >> Save("json/testing/_Save_1.3_note_triad.json")

# Base Note creation to be used in the Sequencer
base_note = Note() << (NoteValue() << Dotted(1/64))
# Creation and configuration of a Track of notes
first_sequence = (base_note / 8 << Duration(1/16) >> Stack() << MidiTrack(2, "Drums") << Channel(10)) >> Save("json/testing/_Save_1.4__first_sequence.json")

# Creation and configuration of second Sequencer
second_sequence = first_sequence >> Copy()
second_sequence /= Position(2)
second_sequence /= NoteValue(2)
some_rest = Rest(4/1)
second_sequence = Rest(4/1, Channel(10)) / second_sequence
second_sequence >> Save("json/testing/_Save_1.5_second_sequence.json")
first_sequence = Rest(2/1, Channel(10)) / first_sequence

# Creations, aggregation of both Sequences in a Track element and respective Play
all_elements = Part(first_sequence) + second_sequence
first_note += Beats(2)
all_elements += first_note + single_clock
all_elements >> Save("json/testing/_Save_Play_p.4_first_note.json") >> Export("json/testing/_Export_Play_p.4_sequence.json") >> Export("json/testing/_Export_1.2_all_elements.json")


settings % TimeSignature() >> Save("json/testing/_Save_TimeSignature_ggg.json")


############### TEST2 #######################

# Process Exported files
first_import = Import("json/testing/_Export_1.1_sequence.json")
second_import = Import("json/testing/_Export_1.2_all_elements.json")    # It has a clock!
first_import + Measures(0) >> first_import + Measures(2) >> first_import + Measures(4) >> first_import + Measures(6) \
    >> second_import + Measures(8) \
    >> Export("json/testing/_Export_2.1_multiple_imports.json") >> Save("json/testing/_Save_Play_p.5_first_note.json") >> Export("json/testing/_Export_Play_p.5_sequence.json")

# Process Loaded files as Elements
note = Note(Load("json/testing/_Save_1.1_first_note.json"))
note / 4 >> Save ("json/testing/_Save_2.1_multiple_notes.json") >> Save("json/testing/_Save_Play_p.6_first_note.json") >> Export("json/testing/_Export_Play_p.6_sequence.json")

# Process Loaded files as Serialization
load = Note(Load("json/testing/_Save_1.1_first_note.json").copy())
load / 4 >> Save ("json/testing/_Save_2.2_sequence_notes.json") >> Save("json/testing/_Save_Play_p.7_first_note.json") >> Export("json/testing/_Export_Play_p.7_sequence.json")


############### TEST3 #######################

# Global Staff setting up
settings << Tempo(120)
single_clock = Clock(Length(1)) / 1 << MidiTrack(0, "Clock Track")
composition: Part = Part(single_clock)

single_note = Note() << (NoteValue() << Measures(2)) >> Save("json/testing/_Save_Play_p.7.2_first_note.json") >> Export("json/testing/_Export_Play_p.7.2_sequence.json")
note_transposed = single_note + Semitone(5) >> Save("json/testing/_Save_Play_p.7.3_first_note.json") >> Export("json/testing/_Export_Play_p.7.3_sequence.json")

triplets_one = (Triplet("E") << NoteValue(1/16)) / 8
triplets_one + single_clock >> Save("json/testing/_Save_3.1_triple_note3.json") >> Save("json/testing/_Save_Play_p.8_first_note.json") >> Export("json/testing/_Export_Play_p.8_sequence.json")

triplets_two = (Triplet("G") << NoteValue(1/16)) / 8
triplets_two + single_clock >> Export("json/testing/_Export_3.1_triple_note3.json") >> Save("json/testing/_Save_Play_p.9_first_note.json") >> Export("json/testing/_Export_Play_p.9_sequence.json")

# Duration needs to be adjusted because Elements are Stacked based on Duration and not on Duration!
# A 1/16 triplet has a total duration of a 1/8
composition + triplets_one * triplets_two \
    >> Save("json/testing/_Save_Play_p.10_first_note.json") >> Export("json/testing/_Export_Play_p.10_sequence.json")

# triplets remain a clip. Frames don't operate on Songs!!
triplets = triplets_one * triplets_two + Equal(Beat(1))**Semitone(2)
composition + triplets \
    >> Save("json/testing/_Save_Play_p.10.1_first_note.json") >> Export("json/testing/_Export_Play_p.10.1_sequence.json")

############### TEST4 #######################

# Global Staff setting up
settings << Tempo(60)

chord = Chord() << Duration(2.0) << Gate(1) >> Save("json/testing/_Save_4.1_control_change.json")
oscillate: Oscillate = Oscillate(50, offset=64)
controller = ControlChange("Pan") / (2*16 + 1) << Iterate()**Steps()
controller >>= oscillate
controller >> Save("json/testing/_Save_4.2_control_change.json")
    
chord + controller >> Save("json/testing/_Save_Play_p.10.2_first_note.json") >> Export("json/testing/_Export_Play_p.10.2_sequence.json") >> Export("json/testing/_Export_4.1_control_change.json")


oscillate: Oscillate = Oscillate(int(128*128 / 2 - 1), 1/4)
pitch_bend = PitchBend() / (2*16 + 1) << Iterate()**Steps()
pitch_bend >>= oscillate

chord + pitch_bend >> Save("json/testing/_Save_Play_p.10.3_first_note.json") >> Export("json/testing/_Export_Play_p.10.3_sequence.json") \
    >> Save("json/testing/_Save_4.2_pitch_bend.json") >> Export("json/testing/_Export_4.2_pitch_bend.json")


############### TEST5 #######################

# Global Staff setting up
settings << Tempo(120)

(Chord() / 7 << Size("7th") << Scale([])) + Iterate()**Degree() \
    >> Save("json/testing/_Save_Play_p.11_first_note.json") >> Export("json/testing/_Export_Play_p.11_sequence.json")
settings << Minor()
(Chord("A") << Octave(3) << Scale([])) / 7 + Iterate()**Degree() \
    >> Save("json/testing/_Save_Play_p.12_first_note.json") >> Export("json/testing/_Export_Play_p.12_sequence.json") \
        << Inversion(1) >> Save("json/testing/_Save_Play_p.13_first_note.json") >> Export("json/testing/_Export_Play_p.13_sequence.json")

settings << Major()
Chord("C") << Size("13th") << Scale("Major").modulate("5th") << Degree("Dominant") << Octave(3) << Duration(8.0) \
    >> Save("json/testing/_Save_Play_p.13.2_first_note.json") >> Export("json/testing/_Export_Play_p.13.2_sequence.json")
Chord("G") << Size("13th") << Scale("5th") << Duration(8.0) << Octave(3) \
    >> Save("json/testing/_Save_Play_p.13.3_first_note.json") >> Export("json/testing/_Export_Play_p.13.3_sequence.json")


############### TEST6 #######################

# Global Staff setting up
settings << Tempo(120)

(Chord(1/4) / 7 << Size("7th") << Scale([])) << Even()**Iterate()**Add(2)**Degree() \
    >> Save("json/testing/_Save_Play_p.14_first_note.json") >> Export("json/testing/_Export_Play_p.14_sequence.json")
(Chord(1/4) / 7 << Size("7th") << Scale([])) << Iterate()**Even()**Add()**Degree() \
    >> Save("json/testing/_Save_Play_p.15_first_note.json") >> Export("json/testing/_Export_Play_p.15_sequence.json")

all_chords = (Chord(1/4) / 7 << Size("7th"))
first_chords = all_chords >> Beat(0)
first_chords << Degree(5) << Mode(5)
all_chords >> Save("json/testing/_Save_Play_p.15.2_first_note.json") >> Export("json/testing/_Export_Play_p.15.2_sequence.json")

first_chords << Degree() << Mode()
even_chords = all_chords >> Even()**Operand()
even_chords << Degree(5) << Mode(5) << Mode(5)
all_chords >> Save("json/testing/_Save_Play_p.15.3_first_note.json") >> Export("json/testing/_Export_Play_p.15.3_sequence.json")

############### TEST7 #######################

# Global Staff setting up
settings << Tempo(120)

(Chord() << NoteValue(1)) / 3 + Iterate()**Inversion() << Duration(1/1) \
    >> Save("json/testing/_Save_Play_p.16_first_note.json") >> Export("json/testing/_Export_Play_p.16_sequence.json")
((Chord() << NoteValue(1)) / 4 << Size("7th")) + Iterate()**Inversion() << Duration(1/1) << Gate(1) >> Export("json/testing/_Export_7.1_chord_inversion.json") \
    >> Save("json/testing/_Save_Play_p.17_first_note.json") >> Export("json/testing/_Export_Play_p.17_sequence.json")


((Chord("Major") << NoteValue(1)) / 4 << Size("7th") << Sus2() << Gate(1)) + Iterate()**Inversion() << Duration(1/1) \
    >> Save("json/testing/_Save_Play_p.18_first_note.json") >> Export("json/testing/_Export_Play_p.18_sequence.json")


############### TEST8 #######################


# Global Staff setting up
settings << Tempo(120)

(Chord("Major") << NoteValue(1/8)) / 13 + Iterate()**Semitone() << Duration(1/8) \
    >> Save("json/testing/_Save_Play_p.19_first_note.json") >> Export("json/testing/_Export_Play_p.19_sequence.json") << Even()**Velocity(50) \
        >> Save("json/testing/_Save_Play_p.20_first_note.json") >> Export("json/testing/_Export_Play_p.20_sequence.json")




############### TEST9 #######################


# Global Staff setting up
settings << Tempo(240)

# All Sharps(#) of the Major Scale on the Circle of Fifths
play_list_1 = Playlist() << ((KeyScale("C") << Scale("Major") << NoteValue(1)) / 8 
    + Iterate(step=7)**Semitone() 
    << Duration(1/1) << Velocity(70) << Octave(4))

# All Fats(b) of the Major Scale on the Circle of Fifths
play_list_2 = Playlist() << ((KeyScale("C") << Scale("Major") << NoteValue(1)) / 8 
    + Iterate(step=5)**Semitone() 
    << Duration(1/1) << Velocity(70) << Octave(4))

# All Sharps(#) of the minor Scale on the Circle of Fifths
play_list_3 = Playlist() << ((KeyScale("A") << Scale("minor") << NoteValue(1)) / 8 
    + Iterate(step=7)**Semitone() 
    << Duration(1/1) << Velocity(70) << Octave(4))

# All Fats(b) of the minor Scale on the Circle of Fifths
play_list_4 = Playlist() << ((KeyScale("A") << Scale("minor") << NoteValue(1)) / 8 
    + Iterate(step=5)**Semitone() 
    << Duration(1/1) << Velocity(70) << Octave(4))

play_list_1 + Measures(0 * 8) \
    >> play_list_2 + Measures(1 * 8) \
    >> play_list_3 + Measures(2 * 8) \
    >> play_list_4 + Measures(3 * 8) \
    >> Save("json/testing/_Save_Play_p.21_first_note.json") >> Export("json/testing/_Export_Play_p.21_sequence.json")


