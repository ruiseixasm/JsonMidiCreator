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


def test_clip_rotate():
    three_notes = Note() / 3 << Iterate(1)**Degree() << Last()**Beats(2)
    assert three_notes % Duration() == Beats(4)

    simple_rotation = three_notes >> Rotate(1, False)
    assert three_notes % Duration() == Beats(4)
    # simple_rotation >> Plot()
    assert simple_rotation[1] == Degree(3)
    assert simple_rotation[1] == Beats(1)

    complete_rotation = three_notes >> Rotate(1)
    # complete_rotation >> Plot()
    assert complete_rotation[1] == Degree(3)
    assert complete_rotation[1] == Beats(2)

# test_clip_rotate()


