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

    duration = Duration(NoteValue(Step(3*4 + 2)))
    assert duration == Beat(3.5)
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
