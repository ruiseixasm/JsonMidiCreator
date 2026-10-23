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


def test_arpeggio_action():
    c_major = Clip(":, :|:3n, :|:5n,")
    for single_note in c_major:
        single_note % Position() == Position(0)
    c_major << Arpeggiate()
    # c_major >> Plot()
    actual_position = Position(0)
    for single_note in c_major:
        single_note % Position() == actual_position
        actual_position += single_note % Length()
    total_notes: int = c_major % int()
    total_notes >> Print()
    assert total_notes == 4

# test_arpeggio_action()


def test_framed_action():
    c_major = Clip(":, :|:3n, :|:5n,") * 2
    # c_major >> Plot()
    c_major << Equal(Measure(1))**Arpeggiate()
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


def test_sustain_action():
    c_major = Clip(":, :|:3n, :|:5n,")
    for single_note in c_major:
        single_note % Position() == Position(0)
    c_major << Arpeggiate() << Sustain()
    # c_major >> Plot()
    assert c_major[Degree(5)] % Finish() == Beats(1)

# test_sustain_action()


def test_retrigger_notes():
    four_notes = Note(1/1) * 4 << Iterate(1)**Degree()
    four_notes << Retrigger(Swing(2/3))
    # four_notes >> Plot()
    assert four_notes % int() == 16 * 4

# test_retrigger_notes()


def test_complementary_notes():
    sixteen_triggers = Trigger() * 16
    odd_notes = ~sixteen_triggers << Even()**Delete()
    even_notes = ~sixteen_triggers << Even()**Keep()
    assert odd_notes != even_notes
    assert odd_notes != sixteen_triggers
    assert even_notes != sixteen_triggers
    assert odd_notes + even_notes == sixteen_triggers


def test_clip_rotate():
    three_notes = Note() * 3 << Iterate(1)**Degree() << Last()**Beats(2)
    assert three_notes % Duration() == Beats(4)

    # three_notes >> Plot(title="Three Notes", block=False)
    simple_rotation = ~three_notes << Rotate()  # Default is 1 rotation by one Measure
    # simple_rotation >> Plot(title="Simple Rotation", block=False)
    assert three_notes % Duration() == Beats(4)
    assert simple_rotation[1] == Degree(3)
    assert simple_rotation[1] == Beats(2)

    complete_rotation = ~three_notes << Rotate(2)
    # complete_rotation >> Plot(title="Complete Rotation")
    assert complete_rotation[1] == Degree(1)
    assert complete_rotation[1] == Beats(1)

# test_clip_rotate()


def test_rotate_steps():
    onbeat_steps = Trigger(1/4) * 4 << 1/16 << DrumKit("808") << Channel(10)
    onbeat_steps >> Plot(title="Original Pattern", block=False)
    assert onbeat_steps.len() == 4
    assert onbeat_steps[3] == OperandType(Trigger)
    assert onbeat_steps[3] % Steps() == 1
    assert onbeat_steps[3] % Step() == 12
    onbeat_steps << RotateSteps()
    onbeat_steps >> Plot(title="Rotated Pattern")
    assert onbeat_steps.len() == 4
    assert onbeat_steps[3] % Steps() == 1
    # assert onbeat_steps[3] % Step() == 15

# test_rotate_steps()


