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

staff % Duration() >> Print(0)
staff % Measure() >> Print(0)

####### TEST1 ############

# Global Staff setting up
staff << Tempo(110) << Measure(6)

# Set the default single Clock for the entire Staff Length
single_clock = Clock() >> Save("json/testing/_Save_1.1_jsonMidiCreator.json")

# Multiple individual Notes creation and sequentially played
first_note = Note() << (Position() << Step(3*4 + 2)) << (Length() << NoteValue(1/2)) >> Save("json/testing/_Save_1.1_first_note.json")
multi_notes = Rest(NoteValue(Step(3*4 + 2))) >> first_note * 3 << Track("Piano") >> Save("json/testing/_Save_Play_p.1_first_note.json") >> Export("json/testing/_Export_Play_p.1_sequence.json") \
    >> Save("json/testing/_Save_1.2_sequence.json") >> Export("json/testing/_Export_1.1_sequence.json")

first_note << "F" >> Save("json/testing/_Save_Play_p.2_first_note.json") >> Export("json/testing/_Export_Play_p.2_sequence.json")
first_note << Load("json/testing/_Save_1.1_first_note.json") >> Save("json/testing/_Save_Play_p.3_first_note.json") >> Export("json/testing/_Export_Play_p.3_sequence.json")

Note3() << (Duration() << NoteValue(1/16)) >> Save("json/testing/_Save_Play_p.3.1_first_note.json") >> Export("json/testing/_Export_Play_p.3.1_sequence.json") >> Save("json/testing/_Save_1.3_note_triad.json")

# Base Note creation to be used in the Sequencer
base_note = Note() << (Duration() << Dotted(1/64))
# Creation and configuration of a Sequence of notes
first_sequence = (base_note * 8 // Step(1) << Track("Drums") << Channel(10)) >> Save("json/testing/_Save_1.4__first_sequence.json")

# Creation and configuration of second Sequencer
second_sequence = first_sequence >> Copy()
second_sequence /= Position(2)
second_sequence /= Length(2)
some_rest = Rest(4/1)
second_sequence = Rest(4/1) >> second_sequence
second_sequence >> Save("json/testing/_Save_1.5_second_sequence.json")
first_sequence = Rest(2/1) >> first_sequence

# Creations, aggregation of both Sequences in a Sequence element and respective Play
all_elements = Song(first_sequence) + second_sequence
all_elements += (Length() << Beat(2) >> first_note) + single_clock
all_elements >> Save("json/testing/_Save_Play_p.4_first_note.json") >> Export("json/testing/_Export_Play_p.4_sequence.json") >> Export("json/testing/_Export_1.2_all_elements.json")


staff >> Save("json/testing/_Save_Staff_ggg.json")
staff % Duration() >> Print(0)
staff % Measure() >> Print(0)


############### TEST2 #######################

# Process Exported files
first_import = Import("json/testing/_Export_1.1_sequence.json")
second_import = Import("json/testing/_Export_1.2_all_elements.json")    # It has a clock!
first_import >> first_import >> first_import >> first_import >> second_import \
    >> Export("json/testing/_Export_2.1_multiple_imports.json") >> Save("json/testing/_Save_Play_p.5_first_note.json") >> Export("json/testing/_Export_Play_p.5_sequence.json")

# Process Loaded files as Elements
first_load = Load("json/testing/_Save_1.1_first_note.json")
note_0 = Note() << first_load
note_1 = Note() << first_load
note_2 = Note() << first_load
note_3 = Note() << first_load
note_0 >> note_1 >> note_2 >> note_3 >> Save ("json/testing/_Save_2.1_multiple_notes.json") >> Save("json/testing/_Save_Play_p.6_first_note.json") >> Export("json/testing/_Export_Play_p.6_sequence.json")

# Process Loaded files as Serialization
load_0 = first_load >> Copy()
load_1 = first_load >> Copy()
load_2 = first_load >> Copy()
load_3 = first_load >> Copy()
load_0 >> load_1 >> load_2 >> load_3 >> Save ("json/testing/_Save_2.2_sequence_notes.json") >> Save("json/testing/_Save_Play_p.7_first_note.json") >> Export("json/testing/_Export_Play_p.7_sequence.json")


############### TEST3 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(1)
single_clock = Clock()

single_note = Note() << (Duration() << Measure(2)) >> Save("json/testing/_Save_Play_p.7.2_first_note.json") >> Export("json/testing/_Export_Play_p.7.2_sequence.json")
note_transposed = single_note + Semitone(5) >> Save("json/testing/_Save_Play_p.7.3_first_note.json") >> Export("json/testing/_Export_Play_p.7.3_sequence.json")

triplets_one = (Note3("E") << Duration(1/16) << Length(1/16)) * 8 + single_clock \
    >> Save("json/testing/_Save_3.1_triple_note3.json") >> Save("json/testing/_Save_Play_p.8_first_note.json") >> Export("json/testing/_Export_Play_p.8_sequence.json")

triplets_two = (Note3("G") << Duration(1/16) << Length(1/16)) * 8 + single_clock \
    >> Export("json/testing/_Export_3.1_triple_note3.json") >> Save("json/testing/_Save_Play_p.9_first_note.json") >> Export("json/testing/_Export_Play_p.9_sequence.json")

staff << Measure(2)
single_clock = Clock() << Length(0)

# Length needs to be adjusted because Elements are Stacked based on Length and not on Duration!
# A 1/16 triplet has a total length of a 1/8
single_clock >> triplets_one >> triplets_two >> Save("json/testing/_Save_Play_p.10_first_note.json") >> Export("json/testing/_Export_Play_p.10_sequence.json")

(triplets_one >> triplets_two >> single_clock) + Equal(Beat(1))**Semitone(2) >> Save("json/testing/_Save_Play_p.10.1_first_note.json") >> Export("json/testing/_Export_Play_p.10.1_sequence.json")

############### TEST4 #######################

# Global Staff setting up
staff << Tempo(60)

chord = Chord() << NoteValue(2) << Gate(1) >> Save("json/testing/_Save_4.1_control_change.json")
controller = ControlChange("Pan") * (2*16 + 1) << Iterate()**Measure()**NoteValue()**Step()
controller = (Oscillator(Value()) << Offset(64) << Amplitude(50) | controller) >> Save("json/testing/_Save_4.2_control_change.json")
    
chord + controller >> Save("json/testing/_Save_Play_p.10.2_first_note.json") >> Export("json/testing/_Export_Play_p.10.2_sequence.json") >> Export("json/testing/_Export_4.1_control_change.json")


oscillator = Oscillator(Bend()) << Amplitude(8191 / 2)
pitch_bend = (PitchBend() * (2*16 + 1) + Iterate()**Step()) << Extract(Bend())**Wrap(oscillator)**Wrap(PitchBend())**Iterate(4)**Step()

chord + pitch_bend >> Save("json/testing/_Save_Play_p.10.3_first_note.json") >> Export("json/testing/_Export_Play_p.10.3_sequence.json") \
    >> Save("json/testing/_Save_4.2_pitch_bend.json") >> Export("json/testing/_Export_4.2_pitch_bend.json")


############### TEST5 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(7)

(Chord() * 7 << Size("7th")) << Iterate()**Add(1)**Degree() << Increment()**Mode() \
    >> Save("json/testing/_Save_Play_p.11_first_note.json") >> Export("json/testing/_Export_Play_p.11_sequence.json")
(Chord("A") << Scale("minor") << Octave(3)) * 7 << Iterate()**Add()**Degree() << Increment()**Mode() \
    >> Save("json/testing/_Save_Play_p.12_first_note.json") >> Export("json/testing/_Export_Play_p.12_sequence.json") \
        << Inversion(1) >> Save("json/testing/_Save_Play_p.13_first_note.json") >> Export("json/testing/_Export_Play_p.13_sequence.json")

Chord("C") << Size("13th") << Scale("Major") << Degree("Dominant") << Mode("5th") << Octave(3) << NoteValue(8) \
    >> Save("json/testing/_Save_Play_p.13.2_first_note.json") >> Export("json/testing/_Export_Play_p.13.2_sequence.json")
Chord("G") << Size("13th") << Scale("5th") << NoteValue(8) << Octave(3) \
    >> Save("json/testing/_Save_Play_p.13.3_first_note.json") >> Export("json/testing/_Export_Play_p.13.3_sequence.json")


############### TEST6 #######################

# Global Staff setting up
staff << Tempo(120) << Measure(7)

(Chord(1/4) * 7 << Size("7th")) << Even()**Iterate()**Add(2)**Degree() << Even()**Increment()**Mode(2) \
    >> Save("json/testing/_Save_Play_p.14_first_note.json") >> Export("json/testing/_Export_Play_p.14_sequence.json")
(Chord(1/4) * 7 << Size("7th")) << Iterate()**Even()**Add()**Degree() << Increment()**Even()**Mode() \
    >> Save("json/testing/_Save_Play_p.15_first_note.json") >> Export("json/testing/_Export_Play_p.15_sequence.json")

all_chords = (Chord(1/4) * 7 << Size("7th"))
first_chords = all_chords | Beat(0)
first_chords << Degree(5) << Mode(5)
all_chords >> Save("json/testing/_Save_Play_p.15.2_first_note.json") >> Export("json/testing/_Export_Play_p.15.2_sequence.json")

first_chords << Degree() << Mode()
even_chords = all_chords | Even()**Operand()
even_chords << Degree(5) << Mode(5) << Mode(5)
all_chords >> Save("json/testing/_Save_Play_p.15.3_first_note.json") >> Export("json/testing/_Export_Play_p.15.3_sequence.json")

############### TEST7 #######################

# Global Staff setting up
staff << Tempo(120)

(Chord() << Length(1)) * 3 + Iterate()**Inversion() << NoteValue(1) \
    >> Save("json/testing/_Save_Play_p.16_first_note.json") >> Export("json/testing/_Export_Play_p.16_sequence.json")
((Chord() << Length(1)) * 4 << Size("7th")) + Iterate()**Inversion() << NoteValue(1) << Gate(1) >> Export("json/testing/_Export_7.1_chord_inversion.json") \
    >> Save("json/testing/_Save_Play_p.17_first_note.json") >> Export("json/testing/_Export_Play_p.17_sequence.json")


((Chord() << Length(1)) * 4 << Size("7th") << Sus2() << Gate(1)) + Iterate()**Inversion() << NoteValue(1) \
    >> Save("json/testing/_Save_Play_p.18_first_note.json") >> Export("json/testing/_Export_Play_p.18_sequence.json")


############### TEST8 #######################


# Global Staff setting up
staff << Tempo(120) << Measure(7)

(Chord() << Length(1/8)) * 13 + Iterate(1.0)**Key() << NoteValue(1/8) \
    >> Save("json/testing/_Save_Play_p.19_first_note.json") >> Export("json/testing/_Export_Play_p.19_sequence.json") << Even()**Velocity(50) \
        >> Save("json/testing/_Save_Play_p.20_first_note.json") >> Export("json/testing/_Export_Play_p.20_sequence.json")




############### TEST9 #######################


# Global Staff setting up
staff << Tempo(240) << Measure(7)

# All Sharps(#) of the Major Scale on the Circle of Fifths
play_list_1 = Playlist() << ((KeyScale("C") << Scale("Major") << Length(1)) * 8 
    + Iterate(Scale("Major") % Transposition(5 - 1))**Semitone() 
    << NoteValue(1) << Velocity(70) << Octave(4))

# All Fats(b) of the Major Scale on the Circle of Fifths
play_list_2 = Playlist() << ((KeyScale("C") << Scale("Major") << Length(1)) * 8 
    + Iterate(Scale("Major") % Transposition(4 - 1))**Semitone() 
    << NoteValue(1) << Velocity(70) << Octave(4))

# All Sharps(#) of the minor Scale on the Circle of Fifths
play_list_3 = Playlist() << ((KeyScale("A") << Scale("minor") << Length(1)) * 8 
    + Iterate(Scale("minor") % Transposition(5 - 1))**Semitone() 
    << NoteValue(1) << Velocity(70) << Octave(4))

# All Fats(b) of the minor Scale on the Circle of Fifths
play_list_4 = Playlist() << ((KeyScale("A") << Scale("minor") << Length(1)) * 8 
    + Iterate(Scale("minor") % Transposition(4 - 1))**Semitone() 
    << NoteValue(1) << Velocity(70) << Octave(4))

play_list_1 >> play_list_2 >> play_list_3 >> play_list_4 \
    >> Save("json/testing/_Save_Play_p.21_first_note.json") >> Export("json/testing/_Export_Play_p.21_sequence.json")


