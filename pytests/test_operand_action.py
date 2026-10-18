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


def test_delete():
    sixteen_triggers = Trigger() * 16
    assert sixteen_triggers % int() == 16
    sixteen_triggers << Delete()
    assert sixteen_triggers % int() == 0


def test_invert():
    c_major = Clip(":, :|:3n, :|:5n,")
    assert c_major.len() == 3
    c_major += c_major + Beat(1)
    assert c_major[Beat(0)] % Octave() == c_major[Beat(1)] % Octave()
    c_major << Equal(Beat(1))**Invert()
    # c_major >> Plot()
    # c_major[Beat(0)] + c_major[Beat(1)] >> Plot()
    assert c_major[Beat(0)] % Degree() + 2 == c_major[Beat(1)] % Degree()

# test_invert()


def test_effect():
    c_major = Clip(":, :|:3n, :|:5n,")
    for single_note in c_major:
        single_note % Position() == Position(0)
    c_major << ApplyEffect(Arpeggio())
    # c_major >> Plot()
    actual_position = Position(0)
    for single_note in c_major:
        single_note % Position() == actual_position
        actual_position += single_note % Length()
    total_notes: int = c_major % int()
    total_notes >> Print()
    assert total_notes == 4

# test_effect()


def test_framed_action():
    c_major = Clip(":, :|:3n, :|:5n,") * 2
    # c_major >> Plot()
    c_major << Equal(Measure(1))**ApplyEffect(Arpeggio())
    # c_major >> Plot()
    for single_note in c_major & Measure(0):
        single_note % Position() == Position(0)
    actual_position = Position(1)
    for single_note in c_major & Measure(1):
        single_note % Position() == actual_position
        actual_position += single_note % Length()
    total_notes: int = (c_major & Measure(1)) % int()
    total_notes >> Print()
    assert total_notes == 4

# test_framed_action()

