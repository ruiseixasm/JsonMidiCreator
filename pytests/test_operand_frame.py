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
    
    frame = Increment(2)**Steps()
    single_step << frame << frame
    assert single_step % float() == 2.0
    single_step << frame << frame
    assert single_step % float() == 6.0

def test_foreach_mod():

    frame = Foreach(1, 2, 3, 4, 5)  # ints represent Degrees
    notes = Note() * 7  # default degree 1 relative to the note C

    notes += frame  # Original sequences aren't modified by + operator
    clip = Clip() \
        + (N() << D) + (N() << E) + (N() << F) + (N() << G) + (N() << A) + (N() << D) + (N() << E) \
        >> Stack()
        # +       1            2            3            4            5            1            2
    
    assert notes == clip

# test_foreach_mod()


def test_conditional_note():
    
    note: Note = Note()

    assert note % Octave() == 4
    note -= Equal(Step(0))**Octave(1)
    assert note % Octave() == 3
    note += Equal(Step(0))**Octave(1)
    assert note % Octave() == 4

    four_notes: Clip = Note() * 4
    
    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 4
    four_notes -= NotEqual(Step(0))**Octave(1)
    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 3
    four_notes += NotEqual(Step(0))**Octave(1)
    assert four_notes[0] % Octave() == 4
    assert four_notes[1] % Octave() == 4

    four_notes << 1/1 >> Stack()   # Each note is now one measure long (1 note = 1 measure)
    assert four_notes % Length() == Measures(4)

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

    two_notes = 2 * Note()

    two_notes << Even()**Velocity(40)
    print(two_notes[1] % Velocity() % int())
    assert two_notes[1] % Velocity() == 40
    two_notes << Odd()**Velocity(90)
    print(two_notes[0] % Velocity() % int())
    assert two_notes[0] % Velocity() == 90

    four_notes = 4 * Note()

    assert four_notes.len() == 4
    four_notes |= Even()
    assert four_notes.len() == 2
    four_notes /= Filter(Odd())
    assert four_notes.len() == 1

# test_even_odd()
