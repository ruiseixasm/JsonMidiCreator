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

from jsonmidicreator import *


# Run the tests with 'pytest tests\python_functions.py' on windows
# Run the tests with 'pytest tests/python_functions.py' on linux

from io import StringIO
import pytest     # pip install pytest
import sys


def test_clip_rotate():
    three_notes = Note() / 3 << Iterate(1)**Degree() << Last()**Beats(2)
    assert three_notes % Duration() == Beats(4)

    simple_rotation = ~three_notes << Rotate(1, False)
    assert three_notes % Duration() == Beats(4)
    # simple_rotation >> Plot()
    assert simple_rotation[1] == Degree(3)
    assert simple_rotation[1] == Beats(1)

    complete_rotation = ~three_notes << Rotate(1)
    # complete_rotation >> Plot()
    assert complete_rotation[1] == Degree(3)
    assert complete_rotation[1] == Beats(2)

# test_clip_rotate()


def test_split_duration():
    many_pitch = Note() / 4 << Iterate(1)**Degree() << Title("ISplitDuration")
    assert many_pitch.len() == 4
    
    split_duration = ISplitDuration(no_repetitions=True)
    # many_pitch >> Plot(transform=split_duration)

    many_pitch << split_duration
    # many_pitch >> Plot()
    assert many_pitch.len() == 8

# test_split_duration()


def test_shuffle_locus():
    many_pitch = Note() / 4 << Iterate(1)**Degree() << Title("IShuffleLocus")
    assert many_pitch.len() == 4
    
    shuffle_locus = IShuffleLocus(no_repetitions=True)
    # many_pitch >> Plot(transform=shuffle_locus)

    many_pitch << shuffle_locus
    # many_pitch >> Plot()
    assert many_pitch.len() == 4

# test_shuffle_locus()


def test_shuffle_durations():
    many_durations = Clip() << Line(":1/4, :1/2, :1/8, :1/8") \
        << Iterate(1)**Degree() << Title("IShuffleDuration")
    assert many_durations.len() == 4
    
    shuffle_durations = IShuffleDuration(no_repetitions=True)
    # many_durations >> Plot(transform=shuffle_durations)

    many_durations << shuffle_durations
    # many_durations >> Plot()
    assert many_durations.len() == 4

# test_shuffle_durations()


def test_choose_durations():
    many_durations = Clip() << Line(":1/4, :1/2, :1/8, :1/8") \
        << Iterate(1)**Degree() << Title("IChooseDuration")
    assert many_durations.len() == 4
    
    choose_durations = IChooseDuration(no_repetitions=True)
    # many_durations >> Plot(transform=choose_durations)

    many_durations << choose_durations
    # many_durations >> Plot()
    assert many_durations.len() == 4

# test_choose_durations()


def test_swap_durations():
    many_durations = Clip() << Line(":1/4, :1/2, :1/8, :1/8") \
        << Iterate(1)**Degree() << Title("ISwapDuration")
    assert many_durations.len() == 4
    
    swap_durations = ISwapDuration(no_repetitions=True)
    many_durations >> Plot(transform=swap_durations)

    many_durations << swap_durations
    # many_durations >> Plot()
    assert many_durations.len() == 4

# test_swap_durations()




