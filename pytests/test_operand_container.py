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



def test_sequence_mod():

    # Perform the operation
    sequence_1 = Sequence(Note("A"), Note("B"))
    sequence_2 = Note("A") + Note("B")

    assert sequence_1 == sequence_2

    sequence_1 >> Stack()
    sequence_2 >> Stack()

    assert sequence_1 == sequence_2
    

def test_milliseconds_duration():

    duration = Duration(Steps(3*4 + 2))
    # duration >> Print()
    assert duration == Beats(3.5)
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
    three_notes_2 = two_notes + Note() >> Stack()
    assert three_notes == three_notes_2
    assert two_notes == three_notes_2   # Changes the original sequence!

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

def test_floordiv_sequence():

    two_notes: Sequence = Note() * 2
    two_notes // Steps(1)

    for single_note in two_notes:
        assert single_note % Duration() % Steps() == Steps(1)
        

def test_sequence_filter():

    four_notes: Sequence = Note() * 4
    assert four_notes.len() == 4
    single_note: Sequence = four_notes | Beat(2)
    assert single_note.len() == 1

    eight_notes: Sequence = Note() * 8
    assert eight_notes.len() == 8
    single_note: Sequence = eight_notes | Beat(2)
    assert single_note.len() == 2

test_sequence_filter()
