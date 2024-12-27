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



def test_rational_mod():

    # Perform the operation
    rational_1 = FloatR(12)
    rational_2 = FloatR(10)

    assert rational_1 + rational_2 == 12 + 10
    assert rational_1 - rational_2 == 12 - 10
    assert rational_1 * rational_2 == 12 * 10
    assert rational_1 / rational_2 == 12 / 10


def test_dotted_mod():

    dotted = Dotted(1/4)
    assert dotted % NoteValue() % Fraction() == Fraction(3, 8)
    assert dotted % Dotted() % Fraction() == Fraction(1, 4)
    assert dotted % DataSource( Fraction() ) == Fraction(3, 8)


def test_beats_and_steps_default():

    position_measures = Position(1.5)
    assert position_measures % Beats() % DataSource( Fraction() ) == 6
    assert position_measures % Steps() % DataSource( Fraction() ) == 16 + 16/2
    assert position_measures % Beat() == Beats(2)
    assert position_measures % Step() == Steps(1/2 * 16)

    position_beats = Position(Beats(6))
    assert position_beats % Beats() % DataSource( Fraction() ) == 6
    assert position_beats % Steps() % DataSource( Fraction() ) == 16 + 16/2
    assert position_beats % Beat() == Beats(2)
    assert position_beats % Step() == Steps(1/2 * 16)

    position_steps = Position(Steps(16 + 16/2))
    assert position_steps % Beats() % DataSource( Fraction() ) == 6
    assert position_steps % Steps() % DataSource( Fraction() ) == 16 + 16/2
    assert position_steps % Beat() == Beats(2)
    assert position_steps % Step() == Steps(1/2 * 16)

    duration = Duration(1.5)
    assert duration % Beats() % DataSource( Fraction() ) == 6
    assert duration % Steps() % DataSource( Fraction() ) == 16 + 16/2
    assert duration % Beat() == Beats(2)
    assert duration % Step() == Steps(1/2 * 16)

# test_beats_and_steps_default()

def test_beats_and_steps_specific():

    position_measures = Position(1.5) << TimeSignature(3, 8) << Quantization(1/32)
    print(position_measures % Beats() % DataSource( Fraction() ))
    assert position_measures % Beats() % DataSource( Fraction() ) == 3 + 3/2
    # assert position_measures.getSteps() % DataSource( Fraction() ) == 32 + 32/2
    # assert position_measures.getBeat() == Beat(3/2)
    # assert position_measures.getStep() == Step(1/2 * 32)

    # beats = Beat(6) << TimeSignature(3, 8) << Quantization(1/32)
    # assert beats.getBeats() % DataSource( Fraction() ) == 6
    # assert beats.getSteps() % DataSource( Fraction() ) == 16 + 16/2
    # assert beats.getBeat() == Beat(2)
    # assert beats.getStep() == Step(1/2 * 16)

    # steps = Step(16 + 16/2) << TimeSignature(3, 8) << Quantization(1/32)
    # assert steps.getBeats() % DataSource( Fraction() ) == 6
    # assert steps.getSteps() % DataSource( Fraction() ) == 16 + 16/2
    # assert steps.getBeat() == Beat(2)
    # assert steps.getStep() == Step(1/2 * 16)

    # notes = NoteValue(1.5) << TimeSignature(3, 8) << Quantization(1/32)
    # assert notes.getBeats() % DataSource( Fraction() ) == 6
    # assert notes.getSteps() % DataSource( Fraction() ) == 16 + 16/2
    # assert notes.getBeat() == Beat(2)
    # assert notes.getStep() == Step(1/2 * 16)



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


# test_time_mod()



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

# test_sub_note_value()
