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
    assert dotted % Beat() % Fraction() == Fraction(3, 2)


