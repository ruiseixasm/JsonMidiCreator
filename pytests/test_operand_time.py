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



def test_time_mod():

    # Perform the operation
    time = Position(4.5)

    measure_float = time % Measures() % float()
    assert measure_float == 4.0
    measure_float = time % od.DataSource( Measures() ) % float()
    assert measure_float == 4.5

    beat_float = time % Beats() % float()
    assert beat_float == 2.0
    beat_float = time % od.DataSource( Beats() ) % float()
    assert beat_float == 4.5 * 4.0

    step_float = time % Steps() % float()
    assert step_float == 8.0
    step_float = time % od.DataSource( Steps() ) % float()
    assert step_float == 4.5 * 16.0

    note_value_float = time % NoteValue() % float()
    assert note_value_float == 4.5
    note_value_float = time % od.DataSource( NoteValue() ) % float()
    assert note_value_float == 4.5 * 1.0


test_time_mod()



def test_add_beats():

    position = Position()
    measures = Measures(0.5)
    position += Beats(2)
    assert position == measures

    position <<= Measures(1)
    assert position == Position(1.5)

    position += Beats(4)
    assert position == Position(2.5)

    position += Beats(-4)
    assert position == Position(1.5)

def test_add_steps():

    position = Position()
    measures = Measures(0.5)
    position += Steps(2 * 4)
    assert position == measures

    position += Steps(4 * 4)
    assert position == Position(1.5)

    position += Steps(-4 * 4)
    assert position == Position(0.5)

def test_add_note_value():

    position = Position()
    measures = Measures(0.5)
    position += NoteValue(2 / 4)
    assert position == measures

    position += NoteValue(4 / 4)
    assert position == Position(1.5)

    position += NoteValue(-4 / 4)
    assert position == Position(0.5)


def test_sub_beats():

    position = Position(2)
    measures = Measures(1.5)
    position -= Beats(2)
    assert position == measures

    position <<= Measures(2)
    assert position == Position(2.5)

    position -= Beats(4)
    assert position == Position(1.5)

    position -= Beats(-4)
    assert position == Position(2.5)

def test_sub_steps():

    position = Position(2)
    measures = Measures(1.5)
    position -= Steps(2 * 4)
    assert position == measures

    position -= Steps(4 * 4)
    assert position == Position(0.5)

    position -= Steps(-4 * 4)
    assert position == Position(1.5)

def test_sub_note_value():

    position = Position(2)
    measures = Measures(1.5)
    position -= NoteValue(2 / 4)
    assert position == measures

    position -= NoteValue(4 / 4)
    assert position == Position(0.5)

    position -= NoteValue(-4 / 4)
    assert position == Position(1.5)
