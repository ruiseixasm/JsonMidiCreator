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
import pytest
import sys


def test_container_mod():

    keys_container: Container = Container(Pitch(), Pitch(), Pitch(), Pitch(), Pitch(), Pitch(), Pitch())
    assert keys_container.len() == 7
    for single_item in keys_container:
        assert single_item == "C"
    
    keys_container << Iterate()**Add(1)**Degree()
    keys: list = ["C", "D", "E", "F", "G", "A", "B"]
    for degree in range(7):
        keys_container[degree] % str() >> Print()
        assert keys_container[degree] == keys[degree]

# test_container_mod()


def test_sequence_mod():

    # Perform the operation
    sequence_1 = Sequence(Note("A"), Note("B"))
    sequence_2 = Note("A") + Note("B")

    sequence_1 % Position() % Fraction() >> Print() # 0
    assert sequence_1 == Position(0.0)
    assert sequence_1 % Position() == Position(0.0)
    assert sequence_1 % Position() % Fraction() == 0

    assert sequence_1 == sequence_2

    sequence_1 >> Stack()
    sequence_2 >> Stack()

    assert sequence_1 == sequence_2
    

    chords_sequence: Sequence = Sequence(Chord(), Chord(), Chord(), Chord(), Chord(), Chord(), Chord())
    assert chords_sequence.len() == 7
    for single_item in chords_sequence:
        assert single_item == "C"
    
    chords_sequence << Iterate()**Add(1)**Degree()
    keys: list = ["C", "D", "E", "F", "G", "A", "B"]
    for degree in range(7):
        chords_sequence[degree] % str() >> Print()
        assert chords_sequence[degree] == keys[degree]

    print("------")
    keys_float: list = [60.0, 62.0, 64.0, 65.0, 67.0, 69.0, 71.0]
    for degree in range(7):
        chords_sequence[degree] % Pitch() % float() >> Print()
        assert chords_sequence[degree] % Pitch() % float() == keys_float[degree]



def test_rrshift_sequence():

    two_notes: Sequence = Note() * 2
    assert two_notes.len() == 2
    # Checks each note position
    two_notes % Position() % Fraction() >> Print()      # 0
    assert two_notes == Position(0)

    print("------")
    measure_length: Length = Length(1)
    moved_two_notes: Sequence = measure_length >> two_notes.copy()
    moved_two_notes % Position() % Fraction() >> Print()    # 1
    assert moved_two_notes == Position(1)
    moved_two_notes[0] % Position() % Fraction() >> Print() # 0
    assert moved_two_notes[0] == Position(0)

    print("------")
    two_notes_original = two_notes.copy()
    four_notes = two_notes >> two_notes     # moves the second pair of notes to the next measure (1)!
    assert two_notes == two_notes_original  # Original two_notes is not changed!
    assert four_notes.len() == 4
    # Last two notes change position, but the sequence position remains the same, Element Stacking!
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

# test_rrshift_sequence()


def test_milliseconds_duration():

    duration = NoteValue(1/16 * (3*4 + 2))
    duration >> Print()
    rest_sequence = Rest(duration) * 1
    sequence_playlist = rest_sequence.getPlaylist()
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    sequence_start = sequence_playlist[0]
    sequence_stop = sequence_playlist[1]
    assert sequence_start["time_ms"] == 0.0
    assert sequence_stop["time_ms"] == 1750.0

    rest_sequence_copy = rest_sequence.copy()
    sequence_playlist = rest_sequence_copy.getPlaylist()
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    sequence_start = sequence_playlist[0]
    sequence_stop = sequence_playlist[1]
    assert sequence_start["time_ms"] == 0.0
    assert sequence_stop["time_ms"] == 1750.0

    rest_default_sequence = Rest() * 1
    sequence_playlist = rest_default_sequence.getPlaylist()
    # 1.0 beat / 120 bpm * 60 * 1000 = 500.0 ms
    sequence_start = sequence_playlist[0]
    sequence_stop = sequence_playlist[1]
    assert sequence_start["time_ms"] == 0.0
    assert sequence_stop["time_ms"] == 500.0


def test_add_sequence():

    two_notes: Sequence = Note() * 2
    four_notes: Sequence = Note() * 4

    assert two_notes + two_notes >> Stack() == four_notes
    assert two_notes != four_notes

    three_notes: Sequence = Note() * 3
    three_notes_2 = two_notes + Note() >> Stack()   # two_notes is NOT changed and thus remains of size 2
    assert three_notes == three_notes_2
    assert two_notes != three_notes_2               # two_notes remains unchanged, size 2!

    assert two_notes[0] % Octave() == 4
    two_notes -= Octave()
    assert two_notes[0] % Octave() == 3
    two_notes += Octave()
    assert two_notes[0] % Octave() == 4


def test_sub_sequence():

    single_note: Element = Note()
    four_notes: Sequence = Note() * 4
    notes_to_remove: Sequence = four_notes % Nth(1, 3)
    remaining_notes: Sequence = four_notes % Nth(2, 4)

    assert notes_to_remove.len() < four_notes.len()
    assert notes_to_remove.len() == remaining_notes.len()

    assert (four_notes - single_note).len() == four_notes.len() - 1
    assert (four_notes - notes_to_remove).len() == four_notes.len() - 2
    assert four_notes - notes_to_remove == remaining_notes


def test_mul_sequence():

    two_notes: Sequence = Note() * 2
    four_notes: Sequence = Note() * 4

    assert two_notes * 2 >> Stack() == four_notes
    assert two_notes != four_notes

    two_notes << Track("Two Notes")
    assert (two_notes * 4).len() == 8

    eight_notes_1 = two_notes * 4
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
    assert two_notes * 2.0 % Length() == Beats(4)
    assert two_notes * Beat(6) % Length() == Beats(2)
    assert two_notes * Beats(6) % Length() == Beats(6)
    
# test_mul_sequence()


def test_element_stacking():

    two_notes: Sequence = Note() * 2
    assert two_notes % Last() % Beats() == Beats(1)

    two_notes << 1/8    # Stacking is NOT included!
    assert two_notes % Last() % Beats() == Beats(1)
    two_notes >> Stack()
    assert two_notes % Last() % Beats() == Beats(1/2)
    
# test_element_stacking()


def test_sequence_filter():

    four_notes: Sequence = Note() * 4
    assert four_notes.len() == 4
    single_note: Sequence = four_notes | Beat(2)
    assert single_note.len() == 1

    eight_notes: Sequence = Note() * 8
    assert eight_notes.len() == 8
    single_note: Sequence = eight_notes | Beat(2)
    assert single_note.len() == 2

# test_sequence_filter()


def test_sequence_map():

    four_notes: Sequence = Note() * 4
    four_notes += All()**Beat(1)
    assert four_notes[0] % Beat() == 1
    assert four_notes[0] % Beats() == 1
    assert four_notes[1] % Beat() == 2
    assert four_notes[1] % Beats() == 2
    assert four_notes[2] % Beat() == 3
    assert four_notes[2] % Beats() == 3
    assert four_notes[3] % Beat() == 0
    assert four_notes[3] % Beats() == 4


def test_sequence_selectors():

    four_notes: Sequence = Note() * 4
    four_notes += All()**Beat(1)
    assert four_notes % First() % Beats() == 1
    assert four_notes % Middle(3) % Beats() == 3    # Middle uses nth, so, 3 means the 3rd element
    assert four_notes % Last() % Beats() == 4

    # Test for bad input
    empty_sequence: Sequence = Sequence()
    assert empty_sequence % First() == Null()
    assert empty_sequence % Middle(3) == Null()
    assert empty_sequence % Last() == Null()

# test_sequence_selectors()


def test_position_shift():

    four_notes_1: Sequence = Note() * 4 << NoteValue(1/8)
    four_notes_2: Sequence = Note() * 4

    print(four_notes_2 % First() % Beats() % int())
    assert four_notes_2 % First() % Beats() == 0

    eight_notes = four_notes_1 >> four_notes_2  # Moves to the next Measure
    print(eight_notes % First() % Beats() % int())
    assert eight_notes % First() % Beats() == 0
    print(eight_notes % Middle(5) % Beats() % int())
    assert eight_notes % Middle(5) % Beats() == 4

    print(four_notes_2 % First() % Beats() % int())
    assert four_notes_2 % First() % Beats() == 0

    assert four_notes_1 % Length() == 3 * Beats(1) + Beats(1/2)
    assert (Measures(1) >> four_notes_1) % Position() == Beats(4)

# test_position_shift()


def test_sequence_operations():

    straight_sequence: Sequence = Note() * 4 << Foreach(eight, quarter, dotted_quarter, dotted_eight) >> Stack()
    reversed_sequence: Sequence = Note() * 4 << Foreach(dotted_eight, dotted_quarter, quarter, eight) >> Stack()

    # 1/8 + 1/4 + 1/4 * 3/2 + 1/8 * 3/2 = 15/16 NoteValue = 4 * 15/16 = 15/4 = 3.75 Beats
    # 1/8 * 3/2 + 1/4 * 3/2 + 1/4 + 1/8 = 15/16 NoteValue = 4 * 15/16 = 15/4 = 3.75 Beats
    duration: float = 0.9375    # 15/16 Note

    sequence_duration: Duration = straight_sequence % Duration()
    print(sequence_duration % float())
    assert sequence_duration == duration

    straight_length: Length = straight_sequence % Length()
    straight_length % Name() >> Print()
    assert straight_length % Name() == "Length"
    
    straight_serialization: dict = straight_length.getSerialization()
    straight_serialization % Data("float") >> Print()   # 3.75 Beats
    assert straight_serialization % Data("float") == 3.75

    reversed_length: Length = reversed_sequence % Length()
    reversed_length % Name() >> Print()
    assert reversed_length % Name() == "Length"
    
    reversed_serialization: dict = reversed_length.getSerialization()
    reversed_serialization % Data("float") >> Print()   # 3.75 Beats
    assert reversed_serialization % Data("float") == 3.75

    assert straight_sequence != reversed_sequence
    assert straight_sequence.copy().reverse()[0] == reversed_sequence[0] + Beats(0.25)
    assert straight_sequence.copy().reverse()[1] == reversed_sequence[1] + Beats(0.25)
    assert straight_sequence.copy().reverse()[2] == reversed_sequence[2] + Beats(0.25)
    assert straight_sequence.copy().reverse()[3] == reversed_sequence[3] + Beats(0.25)
    assert straight_sequence.reverse() == reversed_sequence + All()**Beats(0.25)

# test_sequence_operations()


def test_sequence_content():

    sequence_elements: Sequence = Note() * 4

    for item in sequence_elements:
        assert isinstance(item, Element)

    sequence_items: Sequence = Sequence(Note(), Channel(1), Velocity(100), Rest())
    assert sequence_items.len() == 2
    for item in sequence_items:
        assert isinstance(item, Element)

    sequence_items = sequence_items + Channel() + Velocity() + Clock()  # Only Elements are added, in this case Clock
    assert sequence_items.len() == 3
    for item in sequence_items:
        assert isinstance(item, Element)

