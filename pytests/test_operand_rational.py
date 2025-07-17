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



def test_rational_mod():

    # Perform the operation
    rational_1 = Rational(12)
    rational_2 = Rational(10)

    assert rational_1 + rational_2 == 12 + 10
    assert rational_1 - rational_2 == 12 - 10
    assert rational_1 * rational_2 == 12 * 10
    assert rational_1 / rational_2 == 12 / 10


def test_dotted_mod():

    dotted = Dotted(1/4)    # Multiply by 3/2 (1.5) (1/4 * 3/2 = 3/8)
    print(dotted % Fraction())
    assert dotted % Fraction() == 1/4 * 3/2
    print(dotted % Dotted() % float())
    assert dotted % Dotted() % float() == 1/4
    print(dotted % NoteValue() % Fraction())
    assert dotted % NoteValue() % Fraction() == Fraction(3, 8)
    print(dotted % Duration() % Fraction())
    assert dotted % Duration() % Fraction() == Fraction(3, 8) * 4
    assert dotted % Pipe( Fraction() ) == Fraction(3, 8)

    undotted = NoteValue(dotted)
    assert dotted == 1/4
    assert undotted == 3/8

# test_dotted_mod()


def test_position_lshift():

    # Quantization is in Beats ratio, meaning, 1/4 by default
    print(f"Quantization: {settings % Quantization() % Fraction()}")
    # Time signature Top decides the Beats per Measure (Must be 4)
    print(f"Top: {settings % TimeSignature() % BeatsPerMeasure() % Fraction()}")
    assert settings % TimeSignature() % BeatsPerMeasure() % Fraction() == 4

    position: Position = Position()

    assert position == 0.0
    position += Measures(1)
    assert position == 1.0
    position += Beats(2)
    print(f"Measures: {position % Measures() % float()}")
    assert position == 1.5
    position << Beat(0)
    assert position == 1.0

# test_position_lshift()


def test_position_default():

    # Time signature Top decides the Beats per Measure (Must be 4)
    print(f"Top: {settings % TimeSignature() % BeatsPerMeasure() % Fraction()}")
    assert settings % TimeSignature() % BeatsPerMeasure() % Fraction() == 4

    position_measures = Position(1.5)
    position_measures % float() >> Print()   # 3/2
    assert position_measures % float() == 3/2
    assert position_measures % Beats() % Fraction() == 6
    assert position_measures % Steps() % Fraction() == 16 + 16/2
    assert position_measures % Beat() == Beats(2)
    assert position_measures % Step() == Steps(1/2 * 16)

    position_beats = Position(Beats(6))
    assert position_beats % Beats() % Fraction() == 6
    assert position_beats % Steps() % Fraction() == 16 + 16/2
    assert position_beats % Beat() == Beats(2)
    assert position_beats % Step() == Steps(1/2 * 16)

    position_steps = Position(Steps(16 + 16/2))
    assert position_steps % Beats() % Fraction() == 6
    assert position_steps % Steps() % Fraction() == 16 + 16/2
    assert position_steps % Beat() == Beats(2)
    assert position_steps % Step() == Steps(1/2 * 16)

# test_position_default()


def test_position_specific():

    settings << TimeSignature(3, 8) << Quantization(1/8)   # Quantization is in Beats ratio

    position: Position = Position(1.5)  # 1.5 Measures
    # Same as a 3/8 time signature
    beats_per_measure: int = 3
    steps_per_beat: int = 8
    # Quantization of 1/32 (note value)
    steps_per_measure: int = steps_per_beat * beats_per_measure

    print(position % Beats() % Pipe( Fraction() ))
    assert position % Beats() == 1.5 * beats_per_measure
    print(position % Steps() % Pipe( Fraction() ))
    print(1.5 * beats_per_measure * steps_per_beat)
    assert position % Steps() == 1.5 * beats_per_measure * steps_per_beat
    print(int(1.5 * beats_per_measure) % beats_per_measure)
    assert position % Beat() == int(1.5 * beats_per_measure) % beats_per_measure
    print(int(1.5 * steps_per_measure) % steps_per_measure)
    assert position % Step() == int(1.5 * steps_per_measure) % steps_per_measure

    settings << TimeSignature(4, 4) << Quantization(1/4)   # Quantization is in Beats ratio

# test_position_specific()


def test_position_unit():

    settings << TimeSignature(4, 4) << Quantization(1/4)   # Quantization is in Beats ratio

    position: Position = Position()
    assert position % Measure() == 0
    # Test if position as Position was round down
    assert position + Steps(1/2) == 0             # 0 Measure (int)
    assert position + Steps(1/2) == Measure(0)    # 0 Measure
    assert position + Steps(1/2) == Beat(0)       # 0 Beat
    assert position + Steps(1/2) == Step(0)       # 0 Beat

# test_position_unit()

def test_length_unit():

    length: Length = Length()
    assert length % Measure() == 0

    assert length + Steps(1/2) == 1/32          # Measures
    assert length + Steps(1/2) == Measure(0)    # Measure
    assert length + Steps(1/2) == Beat(0)       # Beat
    assert length + Steps(1/2) == Step(0)       # Step

    # Test if length as Length was round up
    assert (length + Steps(1/2)).roundMeasures() == 1           # 1 Measure (int)
    assert (length + Steps(1/2)).roundMeasures() == Measure(1)  # 1 Measure
    assert (length + Steps(1/2)).roundBeats() == Beat(1)        # 1 Beat
    assert (length + Steps(1/2)).roundSteps() == Step(1)        # 1 Step

# test_length_unit()


def test_position_round():

    # Position round type: [...)
    position: Position = Position()
    assert position.roundMeasures() == 0.0  # Common behavior
    position += Beat(1)
    assert position.roundMeasures() == 0.0
    position += 1.0 # Measure
    assert position.roundMeasures() == 1.0
    position -= Beat(1)
    assert position.roundMeasures() == 1.0  # Common behavior

def test_length_round():

    # Length round type: (...]
    length: Length = Length()
    assert length.roundMeasures() == 0.0    # Common behavior
    length += Beat(1)
    assert length.roundMeasures() == 1.0
    length += 1.0 # Measure
    assert length.roundMeasures() == 2.0
    length -= Beat(1)
    assert length.roundMeasures() == 1.0    # Common behavior


def test_duration_eq():

    duration: Duration = Duration(0)

    print(duration % float())
    assert duration == 0.0  # Notes
    duration += 1/4
    print(duration % float())
    assert duration == 0.25 # Notes


def test_time_mod():

    # Perform the operation
    time = Position(4.5)

    measure_float = time % Measure() % float()
    assert measure_float == 4.0
    measure_float = time % Measures() % float()
    assert measure_float == 4.5

    beat_float = time % Beat() % float()
    assert beat_float == 2.0
    beat_float = time % Beats() % float()
    assert beat_float == 4.5 * 4.0

    step_float = time % Step() % float()
    assert step_float == 8.0
    step_float = time % Steps() % float()
    assert step_float == 4.5 * 16.0

    note_value_float = time % Duration() % float()
    assert note_value_float == 4.5
    note_value_float = time % Duration() % float()
    assert note_value_float == 4.5 * 1.0


# test_time_mod()



def test_add_beats():

    position = Position()
    measures = Measures(0.5)
    position += Beats(2)
    assert position == measures

    position << Measure(1)
    assert position == Position(1.5)

    position += Beats(4)
    assert position == Position(2.5)

    position += Beats(-4)
    assert position == Position(1.5)

# test_add_beats()


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
    position += Duration(2 / 4)
    assert position == measures

    position += Duration(4 / 4)
    assert position == Position(1.5)

    position += Duration(-4 / 4)
    assert position == Position(0.5)


def test_sub_beats():

    position = Position(2)
    measures = Measures(1.5)
    position -= Beats(2)
    assert position == measures

    position << Measure(2)
    assert position == Position(2.5)

    position -= Beats(4)
    assert position == Position(1.5)

    position -= Beats(-4)
    assert position == Position(2.5)

# test_sub_beats()


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
    position -= Duration(2 / 4)
    assert position == measures

    position -= Duration(4 / 4)
    assert position == Position(0.5)

    position -= Duration(-4 / 4)
    assert position == Position(1.5)

# test_sub_note_value()

def test_div_time_values():

    position = Position(5)
    position /= Measures(2)
    print(f"Measures(5) / Measures(2) == {position % Measures() % Fraction()}")
    assert position == Measures(2.5)    # Direct, same as / 2

    position = Position(5)
    position /= Beats(2)    # Same as Measures(2 / 4) = Measures(1/2)
    print(f"Measures(5) / Measures(1/2) == {position % Measures() % Fraction()}")
    assert position == Measures(10)     # Same as * 2

    position = Position(5)
    position /= Steps(2)    # Same as Measures(2 / 16) = Measures(1/8)
    print(f"Measures(5) / Measures(1/8) == {position % Measures() % Fraction()}")
    assert position == Measures(40)     # Same as * 8

    position = Position(5)
    position /= Duration(2.0) # Same as Measures(2 / 1) = Measures(2)
    print(f"Measures(5) / Measures(2/1) == {position % Measures() % Fraction()}")
    assert position == Measures(2.5)     # Same as / 2

# test_div_time_values()


def test_div_time():

    position = Position(5)
    measures = Measures(2.5)
    position /= Position(2)
    assert position == measures

    position = Position(5)      # Position is in Measures
    measures = Measures(2.5)
    position /= Length(2)   # Length is in Measures
    # position /= Length(2 * 4)   # Length is in Beats
    assert position == measures

    position = Position(5)
    measures = Measures(2.5)
    position /= NoteValue(2)     # Duration is in NoteValue
    assert position == measures

    position = Position(1/4)
    length = Length(1/1)
    assert position / length % float() == 1/4   # Measures


# test_div_time()


def test_basic_conversions():

    position = Position(10.5)

    assert position % Measures() % Fraction() == 10.5
    assert position % Measure() % Fraction() == 10
    assert position % Beats() % Fraction() == 10.5 * 4
    assert position % Beat() % Fraction() == 2      # Second beat in the Measure 10
    assert position % Steps() % Fraction() == 10.5 * 4 * 4
    assert position % Step() % Fraction() == 2 * 4  # Eight step in the Measure 10
    print(f"NoteValue: {position % NoteValue() % Fraction()} vs. {10 * (1/1) + 2 * (1/4)}")
    assert position % NoteValue() % Fraction() == 10 * (1/1) + 2 * (1/4)
    print(f"NoteValue: {position % Duration() % Fraction()} vs. {(10 * (1/1) + 2 * (1/4)) * 4}")
    assert position % Duration() % Fraction() == (10 * (1/1) + 2 * (1/4)) * 4 # Because one note value is 4 beats !

    quantization: Quantization = Quantization(1/4)  # Quantization is in Beats ratio
    assert quantization % Fraction() == 1/4         # Quantization is in Beats ratio
    duration: Duration = Duration()
    assert duration % Fraction() == 0
    duration << quantization
    assert duration % Steps() == 1
    assert duration % Fraction() == 1/4 # A quarter of a beat
    assert duration % float() == 1/16

    assert Beats(2) % Measures() == Measures(1/2)

# test_basic_conversions()


def test_full_conversions():

    position = Position()
    position_staff = position._get_time_signature()

    for time_value in (Measures(10.5), Beats(10.5 * 4),
                       Steps(10.5 * 4 * 4), Duration(10 * (1/1) + 2 * (1/4))):
        assert time_value % Measures(position_staff) == 10.5
        assert time_value % Measure(position_staff) == 10
        assert time_value % Beats(position_staff) == 10.5 * 4
        assert time_value % Beat(position_staff) == 2
        assert time_value % Steps(position_staff) == 10.5 * 4 * 4
        assert time_value % Step(position_staff) == 2 * 4
        assert time_value % Duration(position_staff) == 10 * (1/1) + 2 * (1/4)

    for time_unit in (Measure(10), Beat(10 * 4), Step(10 * 4 * 4)):
        assert time_unit % Measures(position_staff) == 10
        assert time_unit % Measure(position_staff) == 10
        assert time_unit % Beats(position_staff) == 10 * 4
        assert time_unit % Beat(position_staff) == 0
        assert time_unit % Steps(position_staff) == 10 * 4 * 4
        assert time_unit % Step(position_staff) == 0 * 4
        assert time_unit % Duration(position_staff) == 10 * (1/1)

# test_full_conversions()


def test_equality():

    rational = Rational(1.5)
    unit = Unit(1)
    assert rational == unit

    measures = Measures(1.5)
    measure = Measure(1)
    assert measures == measure

    beats = Beats(6)
    beat = Beat(2)
    assert measures == beats
    assert measures == beat

    assert Beats(6.5) == Beat(2)

# test_equality()


def test_multi_testing():

    position = Position(10.5)
    print(position % Measures() % Fraction())
    print(position % Measure() % int())
    assert position % Measure() == 10
    assert position % Measure() + 1 == 11
    print(ra.Measures(position % ra.Measure() + 1) % float())
    assert ra.Measures(11) == 11.0
    assert ra.Measures(ra.Measure(11)) == 11.0
    position << ra.Measures(position % ra.Measure() + 1) # Rounded up Duration to Measures
    print(position % Measures() % Fraction())
    assert position == Position(11)

# test_multi_testing()

