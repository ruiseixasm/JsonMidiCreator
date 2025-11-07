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


def test_degrees():

    four_measures = Note() / 4 * 4 << Each(1, 3, 5)**Degree()
    degree_yielder = YieldDegree()
    # four_measures >> Plot(title="Four Measures", block=False)
    # degree_yielder >> Plot(title="Degree Yielder")
    assert degree_yielder == four_measures

# test_degrees()


def test_stretching():

    triad_clip = Note(1/3) / 3 * 4
    stretched_yielder = Yielder()**Yielder(TimeSignature(3))
    # triad_clip >> Plot(title="Triad Clip", block=False)
    # stretched_yielder >> Plot(title="Stretched Yielder")
    assert stretched_yielder == triad_clip


def test_extending():

    four_measures = Note() / 4 << Each(1, 3, 5)**Degree()
    four_measures *= 6
    extended_yielder = Yielder(6)**YieldDegree(1)
    # four_measures >> Plot(title="Four Measures", block=False)
    # extended_yielder >> Plot(title="Extended Yielder")
    assert extended_yielder == four_measures

