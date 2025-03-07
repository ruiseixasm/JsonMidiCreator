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



def test_selection():

    four_notes = Note() * 4
    six_notes = Note()  * 6

    selection = Condition(Or(4, 6))
    assert four_notes == selection
    assert six_notes == selection
    
    selection << And(4)
    assert four_notes == selection
    assert six_notes != selection

# test_selection()


def test_comparison():

    four_notes = Note() * 4 << Loop(1/1, 1/2, 1/4, 1/8)

    comparison = Matching()
    assert four_notes != comparison

    comparison = Ascending()
    assert four_notes != comparison

    comparison = Descending()
    assert four_notes == comparison

# test_comparison()

