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

    four_notes = Note() / 4
    # Tempo is centralized in defaults
    assert settings % Tempo() == 120.0
    settings << Tempo(145)
    assert settings % Tempo() == 145.0
    settings << Tempo(120)  # resets to the default

    # KeySignature is an Element parameter, NOT a Clip one
    assert four_notes[0] % KeySignature() == 0
    four_notes << KeySignature(2)
    assert four_notes[0] % KeySignature() == 2

# test_staff_parameters()

def test_container_content():

    container = Container(["String"])
    assert container.len() == 1
    assert isinstance(container[0], str)

    clip = Clip(Chord())
    assert clip.len() == 1
    assert isinstance(clip[0], Element)

    part = Part(clip)
    assert part.len() == 1
    assert isinstance(part[0], Clip)

    song = Song(part)
    assert song.len() == 1
    assert isinstance(song[0], Part)

# test_container_content()


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
    keys: list[str] = ["C", "D", "E", "F", "G", "A", "B"]
    for degree in range(7):
        chords_clip[degree] % str() >> Print()
        assert chords_clip[degree] == keys[degree]

    print("------")
    keys_float: list[int] = [60, 62, 64, 65, 67, 69, 71]
    for degree in range(7):
        chords_clip[degree] % Pitch() % int() >> Print()
        assert chords_clip[degree] % Pitch() % int() == keys_float[degree]

    single_note = Note()
    note_clip = Clip(single_note)

    assert note_clip.len() == 1

# test_clip_mod()


def test_owner_clip():

    clip_add: Clip = Note() + Note()
    assert clip_add._test_owner_clip()

    clip_mul: Clip = Note() / 1
    assert clip_mul._test_owner_clip()

    assert (clip_add + Note())._test_owner_clip()
    assert (Note() + clip_add)._test_owner_clip()
    assert (clip_add + clip_mul)._test_owner_clip()
    assert (clip_add * clip_mul)._test_owner_clip()

# test_owner_clip()


def test_time_signature():

    four_notes: Note = Note() / 4
    print(four_notes[2] % Position() % float())
    assert four_notes[2] % Position() == 0.5    # Measures
    four_notes << TimeSignature(2, 4)
    print(four_notes[2] % Position() % float())
    assert four_notes[2] % Position() == 1.0    # Measures

# test_time_signature()


def test_measurements_composition():

    clip_2_4 = Clip() << TimeSignature(2, 4)

    # Here the measurements still use the default staff 4/4
    assert Measures(1) == Beats(4)
    assert Measure(1) == Beats(4)
    assert Measure(1) == Beat(4)

    # Here the measurements are being set as clip_2_4 measurements
    assert Measures(clip_2_4, 1) == Beats(2)
    assert Measure(clip_2_4, 1) == Beats(2)
    assert Measure(clip_2_4, 1) == Beat(2)

# test_measurements_composition()


def test_or_clip():

    # A Clip with a Measure of only 2 Beats
    four_notes: Clip = Note(1/8) / 4 << TimeSignature(2, 4)

    assert four_notes.len() == 4
    four_notes >>= Mask(Equal(Or(Step(2), Step(4))))
    print(four_notes.len())
    assert four_notes.len() == 2

# test_or_clip()


def test_copy_container():

    clip = Clip(Note())
    assert clip.len() == 1
    assert clip.copy() == clip

    part = Part(clip)
    assert part.len() == 1
    assert part.copy() == part

    song = Part(part)
    assert song.len() == 1
    assert song.copy() == song

    clip << TimeSignature(3, 4)
    assert clip.copy() == clip



def test_add_container():

    clip = Clip() + Note()
    assert type(clip) is Clip
    assert clip.len() == 1

    part = Part() + clip
    assert type(part) is Part
    assert part.len() == 1
    part = Part() + Note()
    assert type(part) is Part
    assert part.len() == 1

    song = Song() + part
    assert type(song) is Song
    assert song.len() == 1
    song = Song() + clip
    assert type(song) is Song
    assert song.len() == 1
    song = Song() + Note()
    assert type(song) is Song
    assert song.len() == 1

# test_add_container()


def test_new_container():

    clip = Clip(Note())
    assert clip.len() == 1

    part = Part(clip)
    assert part.len() == 1
    part = Part(Note())
    assert part.len() == 1

    song = Song(part)
    assert song.len() == 1
    song = Song(clip)
    assert song.len() == 1
    song = Song(Note())
    assert song.len() == 1

# test_new_container()


def test_rshift_container():

    # Clip testing ###################################################
    note_clip = Clip(Note())
    assert note_clip[0] % Position() == 0.0

    note_clip *= Note("E")
    assert note_clip[0] != "E"
    assert note_clip[1] == "E"
    assert note_clip[1] % Position() == Measures(1)

    new_clip = Clip() >> note_clip >> note_clip
    assert new_clip.len() == 4


    # Part testing ###################################################
    # Beat sets Position while Beats set Duration
    note_clip = Clip(Note(), Note("E")) << Iterate()**Beat() # A single Measure clip long!
    note_clip % Length() % float() >> Pr
    clip_part = Part(note_clip)
    assert clip_part % Position() == Beats(0)

    clip_part *= note_clip  # Moves to the next Measure
    assert clip_part.len() == 2

    # Occupies two Measures
    assert clip_part[0][0] % Position() == Measures(0) + Beats(0)
    assert clip_part[0][1] % Position() == Measures(0) + Beats(1)
    assert clip_part[1][0] % Position() == Measures(1) + Beats(0)
    assert clip_part[1][1] % Position() == Measures(1) + Beats(1)

    new_song = clip_part * clip_part
    assert new_song.len() == 2
    print(f"new_song[1][0] % Position(): {new_song[1] % Position() % str()}")
    assert new_song[0] % Position() == Measures(0) + Beats(0)
    assert new_song[1] % Position() == Measures(2) + Beats(0)

    elements_part = Part(Note(), Note("A"))
    assert elements_part.len() == 2
    assert elements_part[0][0] == "C"
    assert elements_part[1][0] == "A"
    # Part stacks by Measure
    assert elements_part[0][0] % Position() == Measures(0) + Beats(0)
    assert elements_part[1][0] % Position() == Measures(0) + Beats(0)


    # Song testing ###################################################
    part_song = Song(clip_part)
    assert part_song.len() == 1
    assert part_song[0] % Position() == Measures(0) + Beats(0)
    assert part_song._test_owner_song()

    print(f"Has Part Length: {part_song.__mod__(od.Pipe( Length() )) is not None}")
    print(f"Length['part_song']: {part_song % Length() % float()}")
    part_song *= clip_part
    assert part_song.len() == 2
    
    print(f"Length[0]: {part_song[0] % Length() % float()}")
    print(f"Length[1]: {part_song[1] % Length() % float()}")
    print(f"Length: {part_song % Length() % float()}")
    # It's a Song and NOT a Part, thus, it's the Part position that is being returned
    print(f"Position[0]: {part_song[0] % Position() % float()}")
    assert part_song[0] % Position() == Measures(0) + Beats(0)
    # The second clip_part occupies two Measures, so, the next Part Measure sets at Position 2 (3rd one)
    print(f"Position[1]: {part_song[1] % Position() % float()}")
    assert part_song[1] % Position() == Measures(2) + Beats(0)
    assert part_song._test_owner_song()

    part_song *= part_song
    assert part_song.len() == 4
    assert part_song[0] % Position() == Measures(0) + Beats(0)
    # clip_part occupies two Measures, so, the next Part Measure Position is the 2 (3rd one)
    assert part_song[1] % Position() == Measures(2) + Beats(0)
    # The two first parts are repeated at the Measure 4 and 6 respectively
    assert part_song[2] % Position() == Measures(4) + Beats(0)
    assert part_song[3] % Position() == Measures(6) + Beats(0)
    assert part_song._test_owner_song()


    all_chords = Chord(1/4) / 7 << Size("7th")
    assert not all_chords.is_masked()
    assert all_chords[0].access(Pitch()).pitch_int() == 60
    first_chords = all_chords >> Beat(0)
    # assert not first_chords.is_masked()
    assert all_chords._test_owner_clip()
    assert first_chords._test_owner_clip()
    assert first_chords is not all_chords
    assert first_chords[0].access(Pitch()).pitch_int() == 60
    first_chords << Degree(5) << Mode(5)
    assert first_chords is not all_chords
    assert all_chords._test_owner_clip()
    assert first_chords._test_owner_clip()
    # assert first_chords[0] is not all_chords[0]
    assert first_chords[0].access(Pitch()).pitch_int() == 67
    # assert all_chords[0].access(Pitch()).pitch_int() == 60

# test_rshift_container()


def test_rrshift_clip():

    two_notes: Clip = Note() / 2
    assert two_notes.len() == 2
    # Checks each note position
    two_notes % Position() % Fraction() >> Print()      # 0
    assert two_notes == Position(0)

    print("------")
    moved_two_notes = two_notes.copy()
    moved_two_notes += Measure(1)   # Measure is for Position while Measures is for Duration
    moved_two_notes % Position() % Fraction() >> Print()    # 0
    assert moved_two_notes == Position(0)
    moved_two_notes[0] % Position() % Fraction() >> Print() # 1
    assert moved_two_notes[0] == Position(1)
    moved_two_notes[1] % Position() % Fraction() >> Print() # 1 + 1/4 = 5/4
    assert moved_two_notes[1] == Position(5/4)

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
    note_clip = Note() / 1
    note: Note = Note()
    assert note_clip % Position() == 0.0 # Measures
    assert note_clip.len() == 1
    two_notes = note_clip / note
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
    note_clip = Note(duration) / 1
    clip_playlist = playlist_time_ms( note_clip.getPlaylist() )
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    clip_start = clip_playlist[0]
    clip_stop = clip_playlist[1]
    assert clip_start["time_ms"] == 0.0
    assert clip_stop["time_ms"] == 1750.0

    note_clip_copy = note_clip.copy()
    clip_playlist = playlist_time_ms( note_clip_copy.getPlaylist() )
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    clip_start = clip_playlist[0]
    clip_stop = clip_playlist[1]
    assert clip_start["time_ms"] == 0.0
    assert clip_stop["time_ms"] == 1750.0

    rest_default_clip = Note() / 1
    clip_playlist = playlist_time_ms( rest_default_clip.getPlaylist() )
    # 1.0 beat / 120 bpm * 60 * 1000 = 500.0 ms
    clip_start = clip_playlist[0]
    clip_stop = clip_playlist[1]
    assert clip_start["time_ms"] == 0.0
    assert clip_stop["time_ms"] == 500.0

# test_milliseconds_duration()


def test_playlists():

    two_notes: Clip = Note() / 2
    playlist = playlist_time_ms( two_notes.getPlaylist() )
    midi_pitch_1 = playlist[0]["midi_message"]["data_byte_1"]   # Note 1 On     [0]
    midi_pitch_2 = playlist[3]["midi_message"]["data_byte_1"]   # Note 2 Off    [3]
    assert midi_pitch_1 == midi_pitch_2

    assert two_notes[0] % Pitch() == two_notes[1] % Pitch()     # Both are 60
    two_notes << Nth(1)**Sharp()    # Only the first note is sharpened
    assert two_notes[0] % Pitch() != two_notes[1] % Pitch() # Checked in isolation!
    playlist = playlist_time_ms( two_notes.getPlaylist() )
    midi_pitch_1 = playlist[0]["midi_message"]["data_byte_1"]
    midi_pitch_2 = playlist[3]["midi_message"]["data_byte_1"]
    print(f"First Pitch: {midi_pitch_1}")
    print(f"Second Pitch: {midi_pitch_2}")
    # assert midi_pitch_1 == midi_pitch_2    # Because both notes are in the same Measure, the sharp propagates (61)
    assert midi_pitch_1 != midi_pitch_2    # Abandoned the sharp propagation on same Measure (61)

    two_notes.reverse()
    assert two_notes[0] % Pitch() != two_notes[1] % Pitch()
    playlist = playlist_time_ms( two_notes.getPlaylist() )
    midi_pitch_1 = playlist[0]["midi_message"]["data_byte_1"]
    midi_pitch_2 = playlist[3]["midi_message"]["data_byte_1"]
    assert midi_pitch_1 != midi_pitch_2

# test_playlists()


def test_add_clip():

    two_notes: Clip = Note() / 2
    four_notes: Clip = Note() / 4

    assert two_notes + two_notes >> Stack() == four_notes
    assert two_notes != four_notes

    three_notes: Clip = Note() / 3
    three_notes_2 = two_notes + Note() >> Stack()   # two_notes is NOT changed and thus remains of size 2
    assert three_notes == three_notes_2
    assert two_notes != three_notes_2               # two_notes remains unchanged, size 2!

    assert two_notes[0] % Octave() == 4
    two_notes -= Octave()
    assert two_notes[0] % Octave() == 3
    two_notes += Octave()
    assert two_notes[0] % Octave() == 4

    assert two_notes % Duration() == Beats(2)
    # assert two_notes >> Duration() == Beats(2)
    assert (two_notes + two_notes) % Duration() == Beats(2)
    four_measures: Clip = two_notes * 4
    assert four_measures % Duration() == Beats(3 * 4 + 2)
    assert (four_measures + four_measures) % Duration() == Beats(3 * 4 + 2)

# test_add_clip()


def test_sub_clip():

    four_notes: Clip = Note() / 4
    single_note: Element = four_notes[0]
    notes_to_remove: Clip = four_notes >> Mask(Nth(1, 3))
    remaining_notes: Clip = four_notes >> Filter(Nth(2, 4))

    assert notes_to_remove.len() < four_notes.len()
    assert notes_to_remove.len() == remaining_notes.len()

    assert (four_notes - single_note).len() == four_notes.len() - 1
    assert (four_notes - notes_to_remove).len() == four_notes.len() - 2
    assert four_notes - notes_to_remove == remaining_notes

# test_sub_clip()


def test_mul_clip():

    two_notes: Clip = Note() / 2
    four_notes: Clip = Note() / 4

    # Checks if it's a mask
    # assert not two_notes % bool()
    # assert not four_notes % bool()
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
    # For Position MEasure shall be used instead of Measures
    first_note % Measure() % Fraction() >> Print()
    assert first_note % Measure() == 0.0   # in measures
    third_note % Measure() % Fraction() >> Print()
    assert third_note % Measure() == 1.0   # in measures
    fifth_note % Measure() % Fraction() >> Print()
    assert fifth_note % Measure() == 2.0   # in measures
    
    eight_notes_2 = four_notes * 2
    assert eight_notes_2.len() == 8
    first_note = eight_notes_2[0]
    third_note = eight_notes_2[2]
    fifth_note = eight_notes_2[4]
    # For Position MEasure shall be used instead of Measures
    first_note % Measure() % Fraction() >> Print()
    assert first_note % Measure() == 0.0   # in measures
    third_note % Position() % Measures() % Fraction() >> Print()
    assert third_note % Position() % Measures() == 0.5   # in measures
    fifth_note % Measure() % Fraction() >> Print()
    assert fifth_note % Measure() == 1.0   # in measures

    assert eight_notes_1 != eight_notes_2

    assert two_notes % Duration() == Beats(2)
    assert two_notes * 2 % Duration() == Beats(6)
    assert two_notes / 2 % Duration() == Beats(4)
    assert two_notes * Beat(6) % Duration() == Beats(2)
    print(f"Duration_/: {two_notes / Beat(6) % Duration() % Beats() % float()}")
    assert two_notes / Beat(6) % Duration() == Beats(6)

    assert (two_notes * two_notes).len() == 4
    assert two_notes * two_notes % Duration() == Measures(1.5) # Measures

    hi_hat: Clip = Note(DrumKit("Hi-Hat"), 1/16) / 4 << Iterate(step=2)**Step() << TimeSignature(2, 4)
    assert hi_hat.len() == 4
    assert hi_hat._test_owner_clip()
    hi_hat >>= Mask(Nth(2, 4))
    assert hi_hat.len() == 2
    assert hi_hat._test_owner_clip()
    hi_hat *= 2
    assert hi_hat.len() == 4
    assert hi_hat._test_owner_clip()
    hi_hat[0] % Position() % Steps() % float() >> Print()
    assert hi_hat[0] % Position() % Steps() == 2.0
    hi_hat[1] % Position() % Steps() % float() >> Print()
    assert hi_hat[1] % Position() % Steps() == 6.0
    hi_hat[2] % Position() % Steps() % float() >> Print()
    assert hi_hat[2] % Position() % Steps() == 10.0
    hi_hat[3] % Position() % Steps() % float() >> Print()
    assert hi_hat[3] % Position() % Steps() == 14.0

    # Test empty Clip
    empty_clip = hi_hat * 0 << TimeSignature(2, 4)
    assert empty_clip.len() == 0
    equally_hi_hat: Clip = empty_clip * hi_hat
    assert hi_hat.len() == 4
    assert equally_hi_hat.len() == 4
    assert equally_hi_hat == hi_hat
    
    print("------")
    six_notes = 6 / Note()
    print(f"Length: {six_notes % Length() % float()}")
    assert six_notes % Duration() == Measures(1.5)  # Measures
    six_notes << Length(six_notes, 1.0)
    print(f"Length: {six_notes % Length() % float()}")
    assert six_notes.__mod__(od.Pipe( Length() )) == 1.0  # Measures

    single_note = Note() / 1
    two_notes = single_note * single_note
    assert two_notes[0] % Position() == 0.0
    assert two_notes[1] % Position() == 1.0

    timed_rest = Rest(NoteValue(1/16 * (3*4 + 2)))  # 7/8 = 0.875
    # Step and NOT Steps is the one that set the Position
    timed_clip = Note(Step(3*4 + 2)) + Rest()       # Step(14) = 0.875 = 7/8

    assert type(timed_clip[0]) == type(Rest())
    assert type(timed_clip[1]) == type(Note())
    
    timed_clip /= 3

    assert type(timed_clip[0]) == type(Rest())
    assert type(timed_clip[1]) == type(Note())
    assert type(timed_clip[2]) == type(Rest())
    assert type(timed_clip[3]) == type(Note())
    assert type(timed_clip[4]) == type(Rest())
    assert type(timed_clip[5]) == type(Note())

    timed_rest_clip = timed_rest / timed_clip   # 7/8 + 0/1 + 7/8
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

    measure_bell: Clip = Nt(DrumKit(34)) / 1 * 4
    print(f"Duration: {measure_bell % Duration() % float()}")
    assert measure_bell % Duration() == Measures(3.25)
    print(f"Length: {measure_bell % Length() % float()}")
    assert measure_bell % Length() == Measures(4)
    assert measure_bell % Length() == Measure(4)    # Measure rounds the Length!!
    print(f"Position: {measure_bell % Position() % float()}")
    assert measure_bell % Position() == 0.0

    print("------")
    beat_tick: Clip = (Nt(DrumKit(35)) / 3 + Beat(1)) * 4   # Position basic operations work on elements
    print(f"Net Measures: {beat_tick.net_duration() % Measures() % float()}")
    print(f"Measures: {beat_tick % Duration() % Measures() % float()}")
    assert beat_tick.net_duration() == Measures(3.75)
    assert beat_tick % Duration() == Measures(4.0)
    print(f"Measure: {beat_tick % Duration() % Measure() % int()}")
    assert beat_tick % Duration() == Measure(4)
    print(f"Position: {beat_tick % Position() % Measures() % float()}")
    assert beat_tick % Position() == 0.0    # Position basic operations work on elements

    print("------")
    metronome: Clip = measure_bell + beat_tick
    print(f"Measure: {metronome % Duration() % Measure() % int()}")
    assert metronome % Duration() == Measure(4)
    print(f"Measures: {metronome % Duration() % Measures() % float()}")
    assert metronome % Duration() == Measures(4.0)
    print(f"Position: {metronome % Position() % Measures() % float()}")
    assert metronome % Position() == 0.0

    print("---------------------")
    # correct version working with frame All()
    beat_tick = (Nt(DrumKit(35)) / 3 + All()**Beat(1)) * 4
    print(f"Measure: {beat_tick % Duration() % Measure() % int()}")
    assert beat_tick % Duration() == Measure(4)
    print(f"Measures: {beat_tick % Duration() % Measures() % float()}")
    assert beat_tick.net_duration() == Measures(3.75)
    assert beat_tick % Duration() == Measures(4.0)
    print(f"Position: {beat_tick % Position() % Measures() % float()}")
    assert beat_tick % Position() == 0.0

    print("------")
    metronome: Clip = measure_bell + beat_tick
    print(f"Measure: {metronome % Duration() % Measure() % int()}")
    assert metronome % Duration() == Measure(4)
    print(f"Measures: {metronome % Duration() % Measures() % float()}")
    assert metronome % Duration() == Measures(4.0)
    print(f"Position: {metronome % Position() % Measures() % float()}")
    assert metronome % Position() == 0.0

# test_clip_composition()


def test_element_stacking():

    two_notes: Clip = Note() / 2
    assert two_notes[-1] == Beat(1)

    two_notes << 1/8    # Stacking is NOT included!
    assert two_notes[-1] == Beat(1)
    two_notes >>= Stack()
    assert two_notes[-1] == Step(2) # 2 Steps == 1/2 Beats

    single_note: Note = Note(Measure(1))
    print(f"Position: {single_note % Position() % Fraction()}")
    assert single_note % Position() == Beats(4)
    four_notes: Clip = single_note / 4
    print(f"Position: {four_notes[0] % Position() % Fraction()}")
    assert four_notes[0] % Position() == Beats(4)

# test_element_stacking()


def test_lshift_clip():

    base_line: Clip = Nt(dotted_eight) / Measure(4)
    print(f"Duration: {base_line % Duration() % float()}")
    assert base_line % Duration() == Measures(3/16 * 21) # 3.9375 measures
    base_line += Step(1)
    print(f"Duration: {base_line % Duration() % float()}")
    assert base_line % Duration() == Measures(3/16 * 21) + Step(1) # 4.0 measures
    base_line -= Step(1)
    print(f"Duration: {base_line % Duration() % float()}")
    assert base_line % Duration() == Measures(3/16 * 21) # 3.9375 measures
    base_line << 1/16
    print(f"Duration: {base_line % Duration() % float()}")
    assert base_line % Duration() == Measures(3/16 * 21 - 1/8) # 3.8125 measures

    two_measures: Clip = Note() / 8
    two_measures << All()**Beat(0)
    assert two_measures.len() == 8
    one_measure: Clip = two_measures >> Mask(Less(Measure(1)))
    assert one_measure.len() == 4

    assert two_measures[0] % Pitch() == 60
    two_measures << Pitch(30)
    assert two_measures[0] % Pitch() == 30
    two_measures << Pitch()
    assert two_measures[0] % Pitch() == 60


    eight_notes = Note() / 8

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

    four_notes: Clip = Note() / 4
    assert four_notes.len() == 4
    single_note: Clip = four_notes >> Beat(2)
    assert single_note.len() == 1

    eight_notes: Clip = Note() / 8
    assert eight_notes.len() == 8
    single_note: Clip = eight_notes >> Beat(2)
    assert single_note.len() == 2

    original_note: Clip = Note() / 1
    assert original_note.len() == 1
    derived_note: Clip = original_note >> Nth(1)
    assert derived_note.len() == 1
    derived_note += Note()
    assert derived_note.len() == 2
    # Needs to be replicated upwards!
    # assert original_note.len() == 2

    # Stacks to make Elements (Notes) different
    derived_note >>= Stack()
    second_note: Note = derived_note[1]
    derived_note -= second_note
    # Shall remove just one Element and become size 1, remove by id and not by data
    assert derived_note.len() == 1
    # Needs to be replicated upwards!
    assert original_note.len() == 1

    original_note: Clip = Note() / 1
    assert original_note.len() == 1
    derived_note: Clip = original_note >> Nth(1)
    assert derived_note.len() == 1
    derived_note /= 2   # Here "/" results in a multiplication by 2 but stacked directly by Element
    assert derived_note.len() == 2
    # Needs to be replicated upwards!
    # assert original_note.len() == 2

# test_clip_filter()


def test_clip_fitting():

    long_notes: Clip = Note(2/1) / Note(2.5)    # Last note equal to 2.0 + 2.5 Measures !!!
    assert long_notes.len() == 2
    assert long_notes % Duration() == 2.0 + 2.5

    print(f"long_notes % Length() % float() {long_notes % Length() % float()}")
    assert long_notes % Length() == Measures(2.0 + 2.0)
    long_notes.fit()
    assert long_notes.len() == 2
    assert long_notes % Duration() == 2.0 + 2.0 # trimmed to the end of last Measure, 4.0 !!

# test_clip_fitting()


def test_clip_map():

    four_notes: Clip = Note() / 4
    four_notes += All()**Beat(1)    # Changes Position
    assert four_notes[0] % Beat() == 1
    assert four_notes[0] % Position() == Beats(1)
    assert four_notes[0] % Beats() == 1
    assert four_notes[1] % Beat() == 2
    assert four_notes[1] % Position() == Beats(2)
    assert four_notes[2] % Beat() == 3
    assert four_notes[2] % Position() == Beats(3)
    assert four_notes[3] % Beat() == 0
    assert four_notes[3] % Position() == Beats(4)


def test_clip_selectors():

    four_notes: Clip = Note() / 4
    four_notes += Beat(1)
    assert four_notes[0] % Beat() == 1
    assert four_notes[2] % Beat() == 3    # Middle uses nth, so, 2 means the 3rd element
    assert four_notes[-1] % Beat() == 0
    assert four_notes[-1] % Position() == Beats(4)

    # Test for bad input
    empty_clip: Clip = Clip()
    if empty_clip.len() >= 2:
        assert empty_clip[0] == Null()
        assert empty_clip[2] == Null()
        assert empty_clip[-1] == Null()

# test_clip_selectors()


def test_position_shift():

    # Integers set the Pitch
    chords: Clip = Chord() / 4 << Foreach(1, 5, 6, 4)

    assert chords % Position() == 0.0
    print(f"Position first [0]: {chords[0] % Position() % float()}")
    # To set ALL Chords into the SAME position, Steps need to be wrapped with Position
    Position(Steps(3)) >> chords   # Step and NOT Steps is what changes Position
    print(f"Position first [0]: {chords[0] % Position() % float()}")
    assert chords % Position() == 0.0   # Clip has no Position on its own

    # To set ALL Chords into the SAME position, Steps need to be wrapped with Position
    Position(Steps(-3)) >> chords # SETS, doesn't Move!! # All Element positions set at Step -3 (Measure -1)
    print(f"Position first [0]: {chords[0] % Position() % float()}")
    assert chords[0] % Position() == Steps(-3)
    fifth_measure_chords = chords.copy()
    # To set ALL Chords into the SAME position, Measures need to be wrapped with Position
    Position(Measures(4)) >> fifth_measure_chords # SETS, doesn't Move, all at Position 4 measure !!
    print(f"Chords Length: {chords % Length() % float()}")
    assert chords % Position() == 0.0   # Clip has no Position on its own
    # chords has ALL notes at negative Measure, so, Length ends up being 0.0 !!
    assert chords % Length() == 0.0 # All Elements became at the same NEGATIVE position, -1.0 position each one
    print(f"Fifth Length: {fifth_measure_chords % Length() % float()}")
    print(f"Duration: {fifth_measure_chords % Duration() % float()}")
    assert fifth_measure_chords % Position() == 0.0   # Clip has no Position on its own
    assert fifth_measure_chords % Length() == 5.0   # All Elements became at the same position, 1.0 length each one
    assert fifth_measure_chords % Duration() == 5.0   # All Elements became at the same position, 1.0 length each one

    # __add__ is clip position agnostic!
    aggregated_chords: Clip = chords + fifth_measure_chords
    print(f"Length: {aggregated_chords % Length() % float()}")
    print(f"Length ADD: {(Steps(3) + Measures(4) + Measures(1)) % Length() % float()}")
    print(f"Duration: {aggregated_chords % Duration() % float()}")
    assert aggregated_chords % Duration() == 5.0

# test_position_shift()


def test_clip_duration():

    four_notes_1: Clip = Note() / 4 << NoteValue(1/8)
    four_notes_2: Clip = Note() / 4

    Beat(2) >> four_notes_1 # SETS common Position!!
    assert four_notes_1 % Position() == Beat(0)    # Clip has no Position on its own
    Beat(-2) >> four_notes_1 # SETS common Position (NEGATIVE)!!
    assert four_notes_1 % Position() == Beat(0)    # Always is 0!

    print(four_notes_2[0] % Beat() % int())
    assert four_notes_2[0] % Beat() == 0

    eight_notes = four_notes_1 * four_notes_2  # * Moves four_notes_2 to the next Measure (THAT IS 0)
    print(eight_notes[0] % Position() % Beats() % int())
    assert eight_notes[0] % Position() == Beats(-2)
    print(eight_notes[4] % Position() % Beats() % int())
    assert eight_notes[4] % Position() == Beats(0)  # four_notes_1 is at Measure -1

    print(four_notes_2[0] % Beat() % int())
    assert four_notes_2[0] % Beat() == 0

    print(f"Duration_0: {four_notes_1 % Duration() % float()}")
    assert four_notes_1.len() == 4    # Total of 4 notes
    # Measures has to be wrapped with Position because by itself set the Duration!
    assert Position(Measures(1)) >> four_notes_1 == Beats(4)  # Operator >> is a pass trough operator, sets all notes Position
    # All Notes are now at position Measure 1
    print(f"Duration_1: {four_notes_1 % Duration() % float()}")
    assert four_notes_1.len() == 4    # Total of 4 notes
    assert four_notes_1.net_duration() == Beats(1/2)    # All Elements became at the same position, NoteValue(1/8) length each one
    print(f"Total Duration: {four_notes_1 % Duration() % float()}")
    assert four_notes_1 % Duration() == Measures(1) + Beats(1/2)    # All Elements became at the same position, NoteValue(1/8) length each one

    single_beat_note = Clip(Note(Beats(1)))
    print(f"single_beat_note Length: {single_beat_note % Length() % float()}")
    assert single_beat_note % Length() == 1.0

# test_clip_duration()


def test_clip_operations():

    straight_clip: Clip = Note() / 4 << Foreach(eight, quarter, dotted_quarter, dotted_eight) >> Stack()
    reversed_clip: Clip = Note() / 4 << Foreach(dotted_eight, dotted_quarter, quarter, eight) >> Stack()

    # 1/8 + 1/4 + 1/4 * 3/2 + 1/8 * 3/2 = 15/16 NoteValue = 4 * 15/16 = 15/4 = 3.75 Beats
    # 1/8 * 3/2 + 1/4 * 3/2 + 1/4 + 1/8 = 15/16 NoteValue = 4 * 15/16 = 15/4 = 3.75 Beats
    duration: float = 0.9375    # 15/16 Note

    # Starts at Position 0.0, so length == net_duration
    clip_duration: Duration = straight_clip % Duration()
    print(clip_duration % float())
    assert clip_duration == duration

    # Starts at Position 0.0, so length == net_duration
    straight_net_length: Length = Length( straight_clip % Duration() )
    type(straight_net_length) >> Print()
    assert type(straight_net_length) == Length
    
    straight_serialization: dict = straight_net_length.getSerialization()
    straight_serialization % Data("float") >> Print()   # 3.75 Beats
    assert straight_serialization % Data("float") == 3.75

    # Starts at Position 0.0, so length == net_duration
    reversed_net_length: Length = Length( reversed_clip % Duration() )
    type(reversed_net_length) >> Print()
    assert type(reversed_net_length) == Length
    
    reversed_serialization: dict = reversed_net_length.getSerialization()
    reversed_serialization % Data("float") >> Print()   # 3.75 Beats
    assert reversed_serialization % Data("float") == 3.75

    assert straight_clip != reversed_clip
    assert straight_clip.copy().reverse()[0] == reversed_clip[0] + Step(1)  # 1 Step == 1/4 Beats
    assert straight_clip.copy().reverse()[1] == reversed_clip[1] + Step(1)
    assert straight_clip.copy().reverse()[2] == reversed_clip[2] + Step(1)
    assert straight_clip.copy().reverse()[3] == reversed_clip[3] + Step(1)
    assert straight_clip.reverse() == reversed_clip + All()**Step(1)


    three_notes = Note(1/4) + Note(1/2) + Note(1/2) >> Stack()
    three_notes += Measure(1)

    # NOT at Position 0.0, so length != net_duration
    three_notes_net_length: Length = Length( three_notes.finish() - three_notes.start() )
    assert three_notes_net_length == 1.25
    assert three_notes[0] % Position() == 1.0

    three_notes.reverse()
    reversed_notes_net_length: Length = Length( three_notes.finish() - three_notes.start() )
    assert reversed_notes_net_length == 1.25
    print(three_notes[0] % Position() % float())
    assert three_notes[0] % Position() == 1.75



# test_clip_operations()


def test_flip_operation():

    four_notes: Clip = Note() / 4
    four_notes << Iterate(60, 2)**Pitch()

    actual_pitch: int = 60
    for single_note in four_notes:
        single_note % od.Pipe( Pitch() ) % int() >> Print()
        assert single_note % od.Pipe( Pitch() ) == actual_pitch
        actual_pitch += 2
    
    four_notes.mirror()

    print("------")
    for single_note in four_notes:
        actual_pitch -= 2
        single_note % od.Pipe( Pitch() ) % int() >> Print()
        assert single_note % od.Pipe( Pitch() ) == actual_pitch

# test_flip_operation()


def test_clip_content():

    clip_elements: Clip = Note() / 4

    for item in clip_elements:
        assert isinstance(item, Element)

    clip_items: Clip = Clip([Note(), Channel(1), Velocity(100), Rest()])
    assert clip_items.len() == 0    # All elements shall be of Element type
    for item in clip_items:
        assert isinstance(item, Element)

    clip_items = clip_items + Channel() + Velocity() + Clock()  # Only Elements are added, in this case Clock
    assert clip_items.len() == 1
    for item in clip_items:
        assert isinstance(item, Element)


def test_tied_notes():

    notes = Note() / 2
    playlist = playlist_time_ms( notes.getPlaylist() )
    note_length = playlist[1]["time_ms"] - playlist[0]["time_ms"]
    assert len(playlist) == 4
        
    tied_notes = Note() / 2 << Tied()
    playlist = playlist_time_ms( tied_notes.getPlaylist() )
    tied_notes_length = playlist[1]["time_ms"] - playlist[0]["time_ms"]
    assert len(playlist) == 2

    assert tied_notes_length == 2 * note_length

# test_tied_notes()


def test_part_operations():

    clip_1: Clip = Clip([Clock()])
    clip_2: Clip = Clip([Note()])

    part_1: Part = Part(clip_1, clip_2)
    part_2: Part = Part(clip_2, clip_1)

    assert part_1.len() == 2
    assert part_2.len() == 2

    assert (part_1 + clip_2).len() == 3
    assert (part_1 - part_1[1]).len() == 1
    assert (part_1 + part_2).len() == 2 # Becomes a Song!

    # Becomes a Part of two Clips due to * operator
    assert (part_1 * clip_2).len() == 3
    part_1 *= clip_2
    assert part_1.len() == 3

# test_part_operations()


def test_clip_length():

    two_notes = Note() / 2
    assert two_notes % Duration() == Beats(2)
    two_notes << Length(1.0)    # Imposed Length
    assert two_notes % Length() == Beats(4)

    assert two_notes * 2 % Length() == Beats(4) * 2
    assert two_notes * two_notes % Length() == Beats(4) * 2
    assert two_notes * 3 % Length() == Beats(4) * 3
    assert two_notes * two_notes * two_notes % Length() == Beats(4) * 3

# test_clip_length()


def test_part_position():

    note_clip_120 = Note() / 1
    note_clip_60 = note_clip_120 / 1 * Duration(2.0)  # Twice the duration

    part_120 = Part(note_clip_120) << Measures(2)
    part_60 = Part(note_clip_60)

    assert part_120 % Position() != part_60 % Position()
    part_60 << Measures(2)
    assert part_120 % Position() == part_60 % Position()
    print(f"Part Duration: {part_120 % Duration() % Fraction()}")
    assert part_120 % Duration() == 1/4
    assert part_120 % Duration() == part_60 % Duration() * 1/2

# test_part_position()


def test_pitch_shifting():

    two_notes: Clip = Note() / 2
    
    # Asserts if it's in transpose mode, by default it is
    print(f"transpose bool True = {two_notes[0] % Pitch() % bool()}")
    assert two_notes[0] % Pitch() % bool()


# test_pitch_shifting()


def test_split_note():

    note_clip: Clip = Note(1/1) * 1
    assert note_clip.len() == 1

    # NoteValue split
    assert (note_clip // NoteValue(1/4)).len() == 4

    # Frame split
    assert (note_clip // NoteValue(1/4) // All()**NoteValue(1/8)).len() == 8

# test_split_note()


def test_process_mask():
    native_clip: Clip = Note() // 4
    copy_clip: Clip = native_clip >> Stack()
    assert copy_clip != native_clip
    masked_native_clip: Clip = native_clip.mask(All())
    assert masked_native_clip.is_masked()
    assert native_clip.is_masked()
    # masked_native_clip is native_clip
    assert masked_native_clip is native_clip
    # A >> from a Mask shall also result in a copy!
    same_mask: Clip = masked_native_clip >> Stack()
    assert masked_native_clip is native_clip
    assert same_mask is not native_clip
    # Now by using the mask the native_copy was stacked changed
    assert same_mask == copy_clip
    
    long_clip: Clip = Note() / 16
    print(f"long_clip.len: {long_clip.len()}")
    assert long_clip.len() == 16
    # long_mask is still long_clip
    long_mask: Clip = long_clip.mask(Last())
    print(f"long_mask.len: {long_mask.len()}")
    assert long_mask.len() == 1

# test_process_mask()


def test_segment_swap():
    two_notes = Note() / 2
    assert two_notes[0] % Pitch() == two_notes[1] % Pitch()
    two_notes << Foreach(1, 5)**Degree()
    assert two_notes[0] % Pitch() != two_notes[1] % Pitch()
    assert two_notes[0] % Pitch() < two_notes[1] % Pitch()

    two_notes.swap([0, 0], [0, 1], Segment)
    assert two_notes[0] % Pitch() > two_notes[1] % Pitch()

# test_segment_swap()


def test_segment_operations():
    four_notes = Note() / 4 << Foreach(0, 2, 4, 6)**Semitone()
    assert four_notes == Foreach(0, 2, 4, 6)**Semitone()

    eight_notes = four_notes / [0.0, 0.0, 0.2, 0.1, 0.0, 0.0, 0.2, 0.3]
    assert eight_notes.len() == 8
    assert eight_notes == Foreach(0, 0, 4, 2, 0, 0, 4, 6)**Semitone()
    assert eight_notes != Foreach(0, 0, 4, 2, 0, 0, 4, 4)**Semitone()

    eight_notes = four_notes * [0, 0]   # Repeated the first Measure twice
    assert eight_notes.len() == 8
    assert eight_notes == Foreach(0, 2, 4, 6)**Semitone()

    eight_notes = four_notes // [0, 0]   # Repeated the first Measure twice
    assert eight_notes.len() == 8
    assert eight_notes == Foreach(0, 0, 2, 2, 4, 4, 6, 6)**Semitone()

# test_segment_operations()


def test_checksum():
    four_notes = Note() / 4
    assert four_notes.checksum() == "8904"

    part_notes = Part(four_notes)
    assert part_notes.checksum() == "8905"

    song_notes = Song(part_notes)
    assert song_notes.checksum() == "8906"


def test_mul_list():
    long_clip = Note(Velocity(100)) / 4 * 8 # 4 * 8 = 32
    assert long_clip.len() == 4 * 8
    long_clip -= Iterate()**Velocity()
    assert long_clip[32 - 1] % Velocity() == 100 - 32 + 1
    assert long_clip[2*4 - 1] % Velocity() == 100 - 2*4 + 1
    
    new_clip = long_clip * [1, 0]   # Picks by Measure, where 0 is the first Measure
    print(f'new_clip[4 - 1] % Velocity(): {new_clip[4 - 1] % Velocity() % int()}')
    print(f'new_clip[8 - 1] % Velocity(): {new_clip[8 - 1] % Velocity() % int()}')
    assert new_clip[4 - 1] % Velocity() % int() == 100 - 8 + 1
    assert new_clip[8 - 1] % Velocity() % int() == 100 - 4 + 1

    same_as_long_clip = long_clip.mask(Beat(3))
    assert same_as_long_clip.len() == 1 * 8
    new_clip = same_as_long_clip * [1, 0]   # Picks by Measure, where 0 is the first Measure
    print(f'new_clip[0] % Velocity(): {new_clip[0] % Velocity() % int()}')
    print(f'new_clip[1] % Velocity(): {new_clip[1] % Velocity() % int()}')
    assert new_clip[0] % Velocity() % int() == 100 - 8 + 1
    assert new_clip[1] % Velocity() % int() == 100 - 4 + 1
    same_as_new_clip = new_clip.unmask()
    assert same_as_new_clip.len() == 4 * 2

# test_floor_div()


def test_floordiv_clip():
    just_notes = Note() / 4
    just_rests = Rest() / 4
    assert just_notes != just_rests

    just_rests //= Note()
    assert just_notes == just_rests

    just_rests = Rest(1/2) / 2
    assert just_notes != just_rests
    assert just_notes[0] == Note()
    assert just_rests[0] == Rest(1/2)

    just_rests //= just_notes
    assert just_rests[0] == Note(1/2)

    just_rests = Rest(1/2) / 2
    just_rests_mask = Rest(1/2) / 2 >> Beat(2)  # 3rd beat masked, meaning, 2nd Rest
    assert just_rests_mask == just_rests
    assert just_rests.len() == 2
    assert just_rests_mask.len() == 1

    just_rests_mask //= just_notes
    assert just_rests_mask[0] == Note(Beat(2), 1/2)
    just_rests = just_rests_mask.unmask()
    assert just_rests[0] == Rest(1/2)
    assert just_rests[1] == Note(Beat(2), 1/2)

    eight_notes = Note() / [1/8, 0, 0, 0, 0, 0, 0, 0]
    assert eight_notes.len() == 8
    assert eight_notes[0] == Position(0)
    assert eight_notes % Duration() == 1.0  # 1 Measures

    eight_notes = Note(Position(1/8)) / [1/8, 0, 0, 0, 0, 0, 0, 0]
    assert eight_notes.len() == 8
    print(f"eight_notes[0] % Position(): {eight_notes[0] % Position() % float()}")
    assert eight_notes[0] == Position(1/8)
    print(f"eight_notes % Length(): {eight_notes % Length() % float()}")
    assert eight_notes % Duration() == 1.0 + 1/8    # Duration in Measures

# test_floordiv_clip()


def test_clip_proxy():
    four_notes = Note() / 4

    notes_proxy = four_notes >> Proxy()
    assert notes_proxy is not four_notes

    inline_notes = notes_proxy >> Inline()
    assert inline_notes % Pipe() is notes_proxy

    inline_mask = inline_notes >> Mask(Nth(1, 2))
    assert inline_mask % Pipe() is inline_notes % Pipe()
    assert inline_notes % Pipe() % bool()   # True means masked

    joined_mask = inline_mask >> Join()
    assert joined_mask % Pipe() is inline_notes % Pipe()

# test_clip_proxy()

