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


# Run the tests with 'pytest tests\python_functions.py' on windows
# Run the tests with 'pytest tests/python_functions.py' on linux

from io import StringIO
import pytest     # pip install pytest
import sys


def test_staff_parameters():

    four_notes = Note() * 4
    assert four_notes % Tempo() == 120.0
    four_notes << Tempo(145)
    assert four_notes % Tempo() == 145.0

    assert four_notes % KeySignature() == 0
    four_notes << KeySignature(2)
    assert four_notes % KeySignature() == 2

# test_staff_parameters()


def test_container_mod():

    keys_container: Container = Container([Pitch(), Pitch(), Pitch(), Pitch(), Pitch(), Pitch(), Pitch()])
    assert keys_container.len() == 7
    for single_item in keys_container:
        assert single_item == "C"
    
    keys_container += Iterate()**Degree()
    keys: list = ["C", "D", "E", "F", "G", "A", "B"]
    for degree in range(7):
        keys_container[degree] % str() >> Print()
        assert keys_container[degree] == keys[degree]

# test_container_mod()


def test_clip_mod():

    # Perform the operation
    clip_1 = Clip([Note("A"), Note("B")])
    clip_2 = Note("A") + Note("B")

    clip_1 % Position() % Fraction() >> Print() # 0
    assert clip_1 == Position(0.0)
    assert clip_1 % Position() == Position(0.0)
    assert clip_1 % Position() % Fraction() == 0

    assert clip_1 == clip_2

    clip_1 >> Stack()
    clip_2 >> Stack()

    assert clip_1 == clip_2
    

    chords_clip: Clip = Clip([Chord(), Chord(), Chord(), Chord(), Chord(), Chord(), Chord()])
    assert chords_clip.len() == 7
    for single_item in chords_clip:
        assert single_item == "C"
    
    chords_clip += Iterate()**Degree()
    keys: list = ["C", "D", "E", "F", "G", "A", "B"]
    for degree in range(7):
        chords_clip[degree] % str() >> Print()
        assert chords_clip[degree] == keys[degree]

    print("------")
    keys_float: list = [60.0, 62.0, 64.0, 65.0, 67.0, 69.0, 71.0]
    for degree in range(7):
        chords_clip[degree] % Pitch() % float() >> Print()
        assert chords_clip[degree] % Pitch() % float() == keys_float[degree]

# test_clip_mod()


def test_staff_reference():

    clip_add: Clip = Note() + Note()
    assert clip_add.test_staff_reference()

    clip_mul: Clip = Note() * 1
    assert clip_mul.test_staff_reference()

    assert (clip_add + Note()).test_staff_reference()
    assert (Note() + clip_add).test_staff_reference()
    assert (clip_add + clip_mul).test_staff_reference()
    assert (clip_add * clip_mul).test_staff_reference()

# test_staff_reference()


def test_time_signature():

    four_notes: Note = Note() * 4
    print(four_notes[2] % Position() % float())
    assert four_notes[2] % Position() == 0.5    # Measures
    four_notes << TimeSignature(2, 4)
    print(four_notes[2] % Position() % float())
    assert four_notes[2] % Position() == 1.0    # Measures

# test_time_signature()


def test_or_clip():

    # A Clip with a Measure of only 2 Beats
    four_notes: Clip = Note(1/8) * 4 << TimeSignature(2, 4)

    assert four_notes.len() == 4
    four_notes |= Equal(Step(2), Step(4))
    print(four_notes.len())
    assert four_notes.len() == 2

# test_or_clip()


def test_rrshift_clip():

    two_notes: Clip = Note() * 2
    assert two_notes.len() == 2
    # Checks each note position
    two_notes % Position() % Fraction() >> Print()      # 0
    assert two_notes == Position(0)

    print("------")
    measure_length: Length = Length(1)
    moved_two_notes = two_notes.copy()
    measure_length >> moved_two_notes
    moved_two_notes % Position() % Fraction() >> Print()    # 1
    assert moved_two_notes == Position(1)
    moved_two_notes[0] % Position() % Fraction() >> Print() # 0
    assert moved_two_notes[0] == Position(0)

    print("------")
    two_notes_original = two_notes.copy()
    four_notes = two_notes * two_notes     # moves the second pair of notes to the next measure (1)!
    assert two_notes == two_notes_original  # Original two_notes is not changed!
    assert four_notes.len() == 4
    # Last two notes change position, but the clip position remains the same, Element Stacking!
    four_notes % Position() % Fraction() >> Print()     # 0
    assert four_notes == Position(0)
    four_notes[0] % Position() % Fraction() >> Print()  # 0
    assert four_notes[0] == Position(0)
    four_notes[1] % Position() % Fraction() >> Print()  # 1/4
    assert four_notes[1] == Position(1/4)
    four_notes[2] % Position() % Fraction() >> Print()  # 1
    assert four_notes[2] == Position(1)
    four_notes[3] % Position() % Fraction() >> Print()  # 5/4
    assert four_notes[3] == Position(1 + 1/4)

    print("------")
    note_clip = Note() * 1
    note: Note = Note()
    assert note_clip % Position() == 0.0 # Measures
    assert note_clip.len() == 1
    two_notes = note_clip >> note
    assert two_notes.len() == 2
    print(f"Position: {two_notes % Position() % float()}")
    assert two_notes % Position() == 0.0 # Measures
    print(f"Position: {two_notes[0] % Position() % float()}")
    assert two_notes[0] % Position() == 0.0 # Measures
    print(f"Position: {two_notes[1] % Position() % float()}")
    assert two_notes[1] % Position() == 0.25 # Measures

# test_rrshift_clip()


def test_milliseconds_duration():

    duration = NoteValue(1/16 * (3*4 + 2))
    duration >> Print()
    rest_clip = Rest(duration) * 1
    clip_playlist = rest_clip.getPlaylist()
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    clip_start = clip_playlist[0]
    clip_stop = clip_playlist[1]
    assert clip_start["time_ms"] == 0.0
    assert clip_stop["time_ms"] == 1750.0

    rest_clip_copy = rest_clip.copy()
    clip_playlist = rest_clip_copy.getPlaylist()
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    clip_start = clip_playlist[0]
    clip_stop = clip_playlist[1]
    assert clip_start["time_ms"] == 0.0
    assert clip_stop["time_ms"] == 1750.0

    rest_default_clip = Rest() * 1
    clip_playlist = rest_default_clip.getPlaylist()
    # 1.0 beat / 120 bpm * 60 * 1000 = 500.0 ms
    clip_start = clip_playlist[0]
    clip_stop = clip_playlist[1]
    assert clip_start["time_ms"] == 0.0
    assert clip_stop["time_ms"] == 500.0


def test_playlists():

    two_notes = Note() * 2
    playlist = two_notes.getPlaylist()
    midi_pitch_1 = playlist[0]["midi_message"]["data_byte_1"]
    midi_pitch_2 = playlist[3]["midi_message"]["data_byte_1"]
    assert midi_pitch_1 == midi_pitch_2

    assert two_notes[0] % Pitch() == two_notes[1] % Pitch()
    two_notes << Nth(1)**Sharp()
    assert two_notes[0] % Pitch() != two_notes[1] % Pitch()
    playlist = two_notes.getPlaylist()
    midi_pitch_1 = playlist[0]["midi_message"]["data_byte_1"]
    midi_pitch_2 = playlist[3]["midi_message"]["data_byte_1"]
    assert midi_pitch_1 == midi_pitch_2

    two_notes.reverse()
    assert two_notes[0] % Pitch() != two_notes[1] % Pitch()
    playlist = two_notes.getPlaylist()
    midi_pitch_1 = playlist[0]["midi_message"]["data_byte_1"]
    midi_pitch_2 = playlist[3]["midi_message"]["data_byte_1"]
    assert midi_pitch_1 != midi_pitch_2


def test_add_clip():

    two_notes: Clip = Note() * 2
    four_notes: Clip = Note() * 4

    assert two_notes + two_notes >> Stack() == four_notes
    assert two_notes != four_notes

    three_notes: Clip = Note() * 3
    three_notes_2 = two_notes + Note() >> Stack()   # two_notes is NOT changed and thus remains of size 2
    assert three_notes == three_notes_2
    assert two_notes != three_notes_2               # two_notes remains unchanged, size 2!

    assert two_notes[0] % Octave() == 4
    two_notes -= Octave()
    assert two_notes[0] % Octave() == 3
    two_notes += Octave()
    assert two_notes[0] % Octave() == 4

    assert two_notes % Length() == Beats(2)
    # assert two_notes >> Length() == Beats(2)
    assert (two_notes + two_notes) % Length() == Beats(2)
    four_measures: Clip = two_notes * 4
    assert four_measures % Length() == Beats(3 * 4 + 2)
    assert (four_measures + four_measures) % Length() == Beats(3 * 4 + 2)

# test_add_clip()


def test_sub_clip():

    single_note: Element = Note()
    four_notes: Clip = Note() * 4
    notes_to_remove: Clip = four_notes | Nth(1, 3)
    remaining_notes: Clip = four_notes | Nth(2, 4)

    assert notes_to_remove.len() < four_notes.len()
    assert notes_to_remove.len() == remaining_notes.len()

    assert (four_notes - single_note).len() == four_notes.len() - 1
    assert (four_notes - notes_to_remove).len() == four_notes.len() - 2
    assert four_notes - notes_to_remove == remaining_notes


def test_mul_clip():

    two_notes: Clip = Note() * 2
    four_notes: Clip = Note() * 4

    assert two_notes * 2 >> Stack() == four_notes
    assert two_notes != four_notes

    two_notes << MidiTrack("Two Notes")
    eight_notes: Clip = two_notes * 4
    print(f"Len: {eight_notes.len()}")
    assert eight_notes.len() == 8

    eight_notes_1: Clip = two_notes * 4
    assert eight_notes_1.len() == 8
    first_note = eight_notes_1[0]
    third_note = eight_notes_1[2]
    fifth_note = eight_notes_1[4]
    first_note % Measures() % Fraction() >> Print()
    assert first_note % Measures() == 0.0   # in measures
    third_note % Measures() % Fraction() >> Print()
    assert third_note % Measures() == 1.0   # in measures
    fifth_note % Measures() % Fraction() >> Print()
    assert fifth_note % Measures() == 2.0   # in measures
    
    eight_notes_2 = four_notes * 2
    assert eight_notes_2.len() == 8
    first_note = eight_notes_2[0]
    third_note = eight_notes_2[2]
    fifth_note = eight_notes_2[4]
    first_note % Measures() % Fraction() >> Print()
    assert first_note % Measures() == 0.0   # in measures
    third_note % Measures() % Fraction() >> Print()
    assert third_note % Measures() == 0.5   # in measures
    fifth_note % Measures() % Fraction() >> Print()
    assert fifth_note % Measures() == 1.0   # in measures

    assert eight_notes_1 != eight_notes_2

    assert two_notes % Length() == Beats(2)
    assert two_notes * 2 % Length() == Beats(6)
    assert two_notes / 2 % Length() == Beats(4)
    assert two_notes * Beat(6) % Length() == Beats(2)
    assert two_notes / Beat(6) % Length() == Beats(6)

    assert (two_notes * two_notes).len() == 4
    assert two_notes * two_notes % Length() == 1.5 # Measures

    hi_hat: Clip = Note(DrumKit("Hi-Hat"), 1/16) * 4 << Iterate(None, 2)**Steps() << TimeSignature(2, 4)
    assert hi_hat.len() == 4
    assert hi_hat.test_staff_reference()
    hi_hat |= Nth(2, 4)
    assert hi_hat.len() == 2
    assert hi_hat.test_staff_reference()
    hi_hat *= 2
    assert hi_hat.len() == 4
    assert hi_hat.test_staff_reference()
    hi_hat[0] % Position() % Steps() % float() >> Print()
    assert hi_hat[0] % Position() % Steps() == 2.0
    hi_hat[1] % Position() % Steps() % float() >> Print()
    assert hi_hat[1] % Position() % Steps() == 6.0
    hi_hat[2] % Position() % Steps() % float() >> Print()
    assert hi_hat[2] % Position() % Steps() == 10.0
    hi_hat[3] % Position() % Steps() % float() >> Print()
    assert hi_hat[3] % Position() % Steps() == 14.0

    # Test empty Clip
    empty_clip = hi_hat * 0
    assert empty_clip.len() == 0
    unchanged_hi_hat = empty_clip * hi_hat
    assert unchanged_hi_hat == hi_hat
    
    print("------")
    six_notes = 6 * Note()
    print(f"Length: {six_notes % Length() % float()}")
    assert six_notes % Length() == 1.5  # Measures
    six_notes << CParameter(Length(1.0))
    print(f"Length: {six_notes % Length() % float()}")
    assert six_notes % Length() == 1.0  # Measures

    single_note = Note() * 1
    two_notes = single_note * single_note
    assert two_notes[0] % Position() == 0.0
    assert two_notes[1] % Position() == 1.0

    timed_rest = Rest(NoteValue(1/16 * (3*4 + 2)))  # 7/8 = 0.875
    timed_clip = Note(Steps(3*4 + 2)) + Rest()      # Steps(14) = 0.875 = 7/8

    assert type(timed_clip[0]) == type(Rest())
    assert type(timed_clip[1]) == type(Note())
    
    timed_clip *= 3

    assert type(timed_clip[0]) == type(Rest())
    assert type(timed_clip[1]) == type(Note())
    assert type(timed_clip[2]) == type(Rest())
    assert type(timed_clip[3]) == type(Note())
    assert type(timed_clip[4]) == type(Rest())
    assert type(timed_clip[5]) == type(Note())

    timed_rest_clip = timed_rest * timed_clip   # 7/8 + 0/1 + 7/8
                                                # Rest
                                                #       Rest
                                                #             Note
                                                # Rest + Rest + Note

    assert timed_rest_clip.len() == 1 + 2*3
    assert type(timed_rest_clip[0]) == type(Rest())
    assert timed_rest_clip[0] % Position() == 0/1
    assert type(timed_rest_clip[1]) == type(Rest())
    assert timed_rest_clip[1] % Position() == 7/8
    assert type(timed_rest_clip[2]) == type(Note())
    assert timed_rest_clip[2] % Position() == 7/8 * 2

# test_mul_clip()


def test_clip_composition():

    measure_bell: Clip = Nt(DrumKit(34)) * 1 * 4
    print(f"Length: {measure_bell % Length() % float()}")
    assert measure_bell % Length() == Measures(3.25)
    print(f"Length: {measure_bell % Length() % float()}")
    assert measure_bell % Length() == Measure(4)
    print(f"Position: {measure_bell % Position() % float()}")
    assert measure_bell % Position() == 0.0

    print("------")
    beat_tick: Clip = (Nt(DrumKit(35)) * 3 + Beat(1)) * 4   # Position basic operations work on elements
    print(f"Measures: {beat_tick % Length() % Measures() % float()}")
    # assert beat_tick % Finish() == Measures(4.0)
    assert beat_tick % Length() == Measures(3.75)
    print(f"Measure: {beat_tick % Length() % Measure() % int()}")
    assert beat_tick % Length() == Measure(4)
    print(f"Position: {beat_tick % Position() % Measures() % float()}")
    assert beat_tick % Position() == 0.0    # Position basic operations work on elements

    print("------")
    metronome: Clip = measure_bell + beat_tick
    print(f"Measure: {metronome % Length() % Measure() % int()}")
    assert metronome % Length() == Measure(4)
    print(f"Measures: {metronome % Length() % Measures() % float()}")
    assert metronome % Length() == Measures(4.0)
    print(f"Position: {metronome % Position() % Measures() % float()}")
    assert metronome % Position() == 0.0

    print("---------------------")
    # correct version working with frame All()
    beat_tick = (Nt(DrumKit(35)) * 3 + All()**Beat(1)) * 4
    print(f"Measure: {beat_tick % Length() % Measure() % int()}")
    assert beat_tick % Length() == Measure(4)
    print(f"Measures: {beat_tick % Length() % Measures() % float()}")
    assert beat_tick % Length() == Measures(3.75)
    print(f"Position: {beat_tick % Position() % Measures() % float()}")
    assert beat_tick % Position() == 0.0

    print("------")
    metronome: Clip = measure_bell + beat_tick
    print(f"Measure: {metronome % Length() % Measure() % int()}")
    assert metronome % Length() == Measure(4)
    print(f"Measures: {metronome % Length() % Measures() % float()}")
    assert metronome % Length() == Measures(4.0)
    print(f"Position: {metronome % Position() % Measures() % float()}")
    assert metronome % Position() == 0.0

# test_clip_composition()


def test_element_stacking():

    two_notes: Clip = Note() * 2
    assert two_notes[-1] == Beats(1)

    two_notes << 1/8    # Stacking is NOT included!
    assert two_notes[-1] == Beats(1)
    two_notes >> Stack()
    assert two_notes[-1] == Beats(1/2)
    
# test_element_stacking()


def test_lshift_clip():

    base_line: Clip = Nt(dotted_eight) * Measures(4)
    print(f"Length: {base_line % Length() % float()}")
    assert base_line % Length() == 3/16 * 21 # 3.9375 measures
    base_line += Step(1)
    print(f"Length: {base_line % Length() % float()}")
    assert base_line % Length() == 3/16 * 21 # 3.9375 measures
    base_line -= Step(1)
    print(f"Length: {base_line % Length() % float()}")
    assert base_line % Length() == 3/16 * 21 # 3.9375 measures
    base_line << 1/16
    print(f"Length: {base_line % Length() % float()}")
    assert base_line % Length() == 3/16 * 21 - 1/8 # 3.8125 measures

    two_measures: Clip = Note() * 8
    two_measures << All()**Beat(0)
    assert two_measures.len() == 8
    one_measure: Clip = two_measures | Less(Measures(1))
    assert one_measure.len() == 4

    assert two_measures[0] % Pitch() == 60.0
    two_measures << Semitone(30)
    assert two_measures[0] % Pitch() == 30.0
    two_measures << Pitch()
    assert two_measures[0] % Pitch() == 60.0


    eight_notes = Note() * 8

    filtered_notes = eight_notes >> Measure(1)

    assert filtered_notes.len() == 4
    assert filtered_notes[0] % Position() == 1.0
    assert filtered_notes[1] % Position() == 1.25
    assert filtered_notes[2] % Position() == 1.50
    assert filtered_notes[3] % Position() == 1.75

    filtered_notes << Measure(0)

    assert filtered_notes.len() == 4
    assert filtered_notes[0] % Position() == 0.0
    assert filtered_notes[1] % Position() == 0.25
    assert filtered_notes[2] % Position() == 0.50
    assert filtered_notes[3] % Position() == 0.75

# test_lshift_clip()


def test_clip_filter():

    four_notes: Clip = Note() * 4
    assert four_notes.len() == 4
    single_note: Clip = four_notes | Beat(2)
    assert single_note.len() == 1

    eight_notes: Clip = Note() * 8
    assert eight_notes.len() == 8
    single_note: Clip = eight_notes | Beat(2)
    assert single_note.len() == 2

# test_clip_filter()


def test_clip_fitting():

    six_notes: Clip = Note() * 6
    assert six_notes % Length() == Beats(6)

    six_notes.fit(Measures(2))
    assert six_notes % Length() == Beats(8)

# test_clip_fitting()


def test_clip_map():

    four_notes: Clip = Note() * 4
    four_notes += All()**Beat(1)
    assert four_notes[0] % Beat() == 1
    assert four_notes[0] % Beats() == 1
    assert four_notes[1] % Beat() == 2
    assert four_notes[1] % Beats() == 2
    assert four_notes[2] % Beat() == 3
    assert four_notes[2] % Beats() == 3
    assert four_notes[3] % Beat() == 0
    assert four_notes[3] % Beats() == 4


def test_clip_selectors():

    four_notes: Clip = Note() * 4
    four_notes += All()**Beat(1)
    assert four_notes[0] % Beats() == 1
    assert four_notes[2] % Beats() == 3    # Middle uses nth, so, 2 means the 3rd element
    assert four_notes[-1] % Beats() == 4

    # Test for bad input
    empty_clip: Clip = Clip()
    if empty_clip % int() >= 2:
        assert empty_clip[0] == Null()
        assert empty_clip[2] == Null()
        assert empty_clip[-1] == Null()

# test_clip_selectors()


def test_position_shift():

    chords: Clip = Chord() * 4 << Loop(1, 5, 6, 4)

    assert chords % Position() == 0.0
    Steps(3) >> chords
    assert chords % Position() == 0.0   # Clip has no Position on its own

    Steps(-3) >> chords
    fifth_measure_chords = chords.copy()
    Measures(4) >> fifth_measure_chords
    print(f"Length: {chords % Length() % float()}")
    assert chords % Length() == 4.0
    assert chords % Position() == 0.0   # Clip has no Position on its own
    assert fifth_measure_chords % Length() == 4.0
    assert fifth_measure_chords % Position() == 0.0   # Clip has no Position on its own

    # __add__ is clip position agnostic!
    aggregated_chords: Clip = chords + fifth_measure_chords
    print(f"Length: {aggregated_chords % Length() % float()}")
    assert aggregated_chords % Length() == 4.0


    four_notes_1: Clip = Note() * 4 << NoteValue(1/8)
    four_notes_2: Clip = Note() * 4

    Beats(2) >> four_notes_1
    assert four_notes_1 % Position() == Beats(0)    # Clip has no Position on its own
    Beats(-2) >> four_notes_1
    assert four_notes_1 % Position() == Beats(0)

    print(four_notes_2[0] % Beats() % int())
    assert four_notes_2[0] % Beats() == 0

    eight_notes = four_notes_1 * four_notes_2  # * Moves four_notes_2 to the next Measure
    print(eight_notes[0] % Beats() % int())
    assert eight_notes[0] % Beats() == 0
    print(eight_notes[4] % Beats() % int())
    assert eight_notes[4] % Beats() == 4

    print(four_notes_2[0] % Beats() % int())
    assert four_notes_2[0] % Beats() == 0

    assert four_notes_1 % Length() == 3 * Beats(1) + Beats(1/2)
    assert (Measures(1) >> four_notes_1) % Position() == Beats(4)

# test_position_shift()


def test_clip_operations():

    straight_clip: Clip = Note() * 4 << Loop(eight, quarter, dotted_quarter, dotted_eight) >> Stack()
    reversed_clip: Clip = Note() * 4 << Loop(dotted_eight, dotted_quarter, quarter, eight) >> Stack()

    # 1/8 + 1/4 + 1/4 * 3/2 + 1/8 * 3/2 = 15/16 NoteValue = 4 * 15/16 = 15/4 = 3.75 Beats
    # 1/8 * 3/2 + 1/4 * 3/2 + 1/4 + 1/8 = 15/16 NoteValue = 4 * 15/16 = 15/4 = 3.75 Beats
    duration: float = 0.9375    # 15/16 Note

    clip_duration: Duration = straight_clip % Duration()
    print(clip_duration % float())
    assert clip_duration == duration

    straight_length: Length = straight_clip % Length()
    straight_length % Name() >> Print()
    assert straight_length % Name() == "Length"
    
    straight_serialization: dict = straight_length.getSerialization()
    straight_serialization % Data("float") >> Print()   # 3.75 Beats
    assert straight_serialization % Data("float") == 3.75

    reversed_length: Length = reversed_clip % Length()
    reversed_length % Name() >> Print()
    assert reversed_length % Name() == "Length"
    
    reversed_serialization: dict = reversed_length.getSerialization()
    reversed_serialization % Data("float") >> Print()   # 3.75 Beats
    assert reversed_serialization % Data("float") == 3.75

    assert straight_clip != reversed_clip
    assert straight_clip.copy().reverse()[0] == reversed_clip[0] + Beats(0.25)
    assert straight_clip.copy().reverse()[1] == reversed_clip[1] + Beats(0.25)
    assert straight_clip.copy().reverse()[2] == reversed_clip[2] + Beats(0.25)
    assert straight_clip.copy().reverse()[3] == reversed_clip[3] + Beats(0.25)
    assert straight_clip.reverse() == reversed_clip + All()**Beats(0.25)


    three_notes = Note(1/4) + Note(1/2) + Note(1/2) >> Stack()
    three_notes += Measure(1)

    assert three_notes % Length() == 1.25
    assert three_notes[0] % Position() == 1.0

    three_notes.reverse()
    assert three_notes % Length() == 1.25
    print(three_notes[0] % Position() % float())
    assert three_notes[0] % Position() == 1.75



# test_clip_operations()


def test_flip_operation():

    four_notes: Clip = Note() * 4
    four_notes << Iterate(60, 2)**Semitone()

    actual_pitch: float = 60.0
    for single_note in four_notes:
        single_note // Pitch() % float() >> Print()
        assert single_note // Pitch() == actual_pitch
        actual_pitch += 2.0
    
    four_notes.flip()

    print("------")
    for single_note in four_notes:
        actual_pitch -= 2.0
        single_note // Pitch() % float() >> Print()
        assert single_note // Pitch() == actual_pitch

# test_flip_operation()


def test_clip_content():

    clip_elements: Clip = Note() * 4

    for item in clip_elements:
        assert isinstance(item, Element)

    clip_items: Clip = Clip([Note(), Channel(1), Velocity(100), Rest()])
    assert clip_items.len() == 2
    for item in clip_items:
        assert isinstance(item, Element)

    clip_items = clip_items + Channel() + Velocity() + Clock()  # Only Elements are added, in this case Clock
    assert clip_items.len() == 3
    for item in clip_items:
        assert isinstance(item, Element)


def test_tied_notes():

    notes = Note() * 2
    playlist = notes.getPlaylist()
    note_length = playlist[1]["time_ms"] - playlist[0]["time_ms"]
    assert len(playlist) == 4
        
    tied_notes = Note(Tied()) * 2
    playlist = tied_notes.getPlaylist()
    tied_notes_length = playlist[1]["time_ms"] - playlist[0]["time_ms"]
    assert len(playlist) == 2

    assert tied_notes_length == 2 * note_length

# test_tied_notes()


def test_song_operations():

    clip_1: Clip = Clip([Clock()])
    clip_2: Clip = Clip([Note()])

    song_1: Part = Part([clip_1, clip_2])
    song_2: Part = Part([clip_2, clip_1])

    assert song_1.len() == 2
    assert song_2.len() == 2

    assert (song_1 + clip_2).len() == 3
    assert (song_1 - clip_2).len() == 1
    assert (song_1 + song_2).len() == 4

    assert (song_1 >> clip_2).len() == 3
    assert (song_1 >> song_2).len() == 4

# test_song_operations()


def test_clip_length():

    two_notes = Note() * 2
    assert two_notes % Length() == Beats(2)
    two_notes << ClipParameter(Length(1.0))
    assert two_notes % Length() == Beats(4)

    assert two_notes * 2 % Length() == Beats(4 * 2)
    assert two_notes * two_notes % Length() == Beats(4 * 2)
    assert two_notes * 3 % Length() == Beats(4 * 3)
    assert two_notes * two_notes * two_notes % Length() == Beats(4 * 3)

# test_clip_length()
