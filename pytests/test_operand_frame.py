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



def test_frame_mod():

    # Perform the operation
    single_step = Steps()
    assert single_step % float() == 0.0
    
    frame = Iterate(step=2)**Steps()
    single_step << frame << frame
    assert single_step % float() == 2.0
    single_step << frame << frame
    assert single_step % float() == 6.0

def test_foreach_mod():

    frame = Foreach(1, 2, 3, 4, 5)**Degree()   # ints represent Degrees
    notes = Note() / 7  # default degree 1 relative to the note C

    notes += frame  # Increases the Degree for each **stacked** element
    clip = Clip() / N(D) / N(E) / N(F) / N(G) / N(A) / N(D) / N(E)  # Makes sure the notes are **staked**
              #       1      2      3      4      5      1      2
              # +     1      1      1      1      1      1      1
              # =     2      3      4      5      6      2      3
    
    assert notes.len() == clip.len()
    clip[0] % Pitch() % Degree() % int() >> Print()
    clip[1] % Pitch() % Degree() % int() >> Print()
    clip[2] % Pitch() % Degree() % int() >> Print()
    clip[3] % Pitch() % Degree() % int() >> Print()
    clip[4] % Pitch() % Degree() % int() >> Print()
    clip[5] % Pitch() % Degree() % int() >> Print()
    clip[6] % Pitch() % Degree() % int() >> Print()
    assert notes[0] == clip[0]
    assert notes[1] == clip[1]
    assert notes[2] == clip[2]
    assert notes[3] == clip[3]
    assert notes[4] == clip[4]
    assert notes[5] == clip[5]
    assert notes[6] == clip[6]
    assert notes == clip

    # Beats are for Duration while Beat is for Position, so, it should be used Beat
    four_notes = Note() / 4
    assert four_notes[0] == Beat(0)
    assert four_notes[1] == Beat(1)
    assert four_notes[2] == Beat(2)
    assert four_notes[3] == Beat(3)

    # Steps are for Duration while Step is for Position, so, it should be used Step
    four_notes << Foreach(0, 1, 2, 3)**Step()
    assert four_notes[0] == Step(0)
    assert four_notes[1] == Step(1)
    assert four_notes[2] == Step(2)
    assert four_notes[3] == Step(3)

    four_notes << Foreach(Beat(0), Beat(1), Beat(2), Beat(3))
    assert four_notes[0] == Beat(0)
    assert four_notes[1] == Beat(1)
    assert four_notes[2] == Beat(2)
    assert four_notes[3] == Beat(3)
    
    assert four_notes[0] == quarter
    assert four_notes[1] == quarter
    assert four_notes[2] == quarter
    assert four_notes[3] == quarter

    four_notes << Foreach(whole, half, quarter, eight)
    assert four_notes[0] == whole
    assert four_notes[1] == half
    assert four_notes[2] == quarter
    assert four_notes[3] == eight

    # Test Stacking
    four_notes >>= Stack()
    assert four_notes[0] == Position(Beats(0))
    assert four_notes[1] == Position(Beats(4))
    assert four_notes[2] == Position(Beats(6))
    assert four_notes[3] == Position(Beats(7))

    four_notes << Nth(1, 4)**Foreach(quarter)
    assert four_notes[0] == quarter
    assert four_notes[1] == half
    assert four_notes[2] == quarter
    assert four_notes[3] == quarter

    four_notes << Foreach(range(2,6))**Beat()
    print(f"Position: {four_notes[0] % Position() % Fraction()}")
    assert four_notes[0] == Position(Beats(2))
    print(f"Position: {four_notes[1] % Position() % Fraction()}")
    assert four_notes[1] == Position(Beats(3))
    assert four_notes[2] == Position(Beats(4))
    assert four_notes[3] == Position(Beats(5))

# test_foreach_mod()


def test_each():

    many_notes = Note() / 9

    for single_note in many_notes:
        assert single_note % Duration() == 1/4
    
    many_notes << Every(3)**Duration(1/8)
    for i, value in enumerate(many_notes):
        if (i + 1) in {3, 6, 9}:
            assert value % Duration() == 1/8
        else:
            assert value % Duration() == 1/4

# test_each()


def test_conditional_note():
    
    note: Note = Note()

    assert note % Octave() == 4
    note -= Equal(Step(0))**Octave(1)
    assert note % Octave() == 3
    note += Equal(Step(0))**Octave(1)
    assert note % Octave() == 4

    four_notes: Clip = Note() / 4
    
    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 4
    four_notes -= NotEqual(Step(0))**Octave(1)
    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 3
    four_notes += NotEqual(Step(0))**Octave(1)
    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 4

    four_notes << 1/1   # Each note is now one measure long (1 note = 1 measure)
    four_notes >>= Stack()
    assert four_notes % Duration() == Measures(4)

    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 4
    four_notes -= NotEqual(Measure(0))**Octave(1)
    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 3
    four_notes += NotEqual(Measure(0))**Octave(1)
    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 4

# test_conditional_note()

def test_even_odd():

    two_notes = 2 / Note()

    two_notes << Even()**Velocity(40)
    print(two_notes[1] % Velocity() % int())
    assert two_notes[1] % Velocity() == 40
    two_notes << Odd()**Velocity(90)
    print(two_notes[0] % Velocity() % int())
    assert two_notes[0] % Velocity() == 90

    four_notes = 4 / Note()

    assert four_notes.len() == 4
    four_notes >>= Even()
    assert four_notes.len() == 2
    four_notes >>= Mask(Odd())
    assert four_notes.len() == 1

# test_even_odd()


def test_input_clip():

    clip = Note() / 4
    clip_G = Note("G") / 4

    for note in clip:
        assert note == "C"
    
    for note in clip_G:
        assert note == "G"
    
    clip << Input(clip_G)**Get(Pitch())

    for note in clip:
        assert note == "G"
    
# test_input_clip()

