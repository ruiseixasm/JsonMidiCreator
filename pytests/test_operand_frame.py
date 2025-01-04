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
    sequence = Sequence() \
        + (N << D) + (N << E) + (N << F) + (N << G) + (N << A) + (N << D) + (N << E) \
        >> Stack()
        # +     1          2          3          4          5          1          2
    
    assert notes == sequence

# test_foreach_mod()
