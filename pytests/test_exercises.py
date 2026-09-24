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


def test_cutting_note():

    settings << None    # Reset settings

    simple_cuts = Note(1/1) * 1
    # Main splits (Positional)
    simple_cuts //= Beat(1)
    simple_cuts //= Position(1) - Steps(1)
    # Secondary splits (Durational)
    # Shallow clip splitting
    simple_cuts[Beat(0)] //= Steps(1)
    simple_cuts *= Rest(1/1)    # Add a simple rest
    # simple_cuts[4] % Duration() >> Print()
    # simple_cuts >> Plot()
    assert simple_cuts[4] % Duration() == Beats(3) - Steps(1)

# test_cutting_note()


def test_transform_note():

    settings << None    # Reset settings

    simple_cuts = Note(1/1) * 1
    # Main splits (Positional)
    split_1 = Operate(lambda clip: clip // Beat(1))
    split_2 = Operate(lambda clip: clip // (Position(1) - Steps(1)))
    split_3 = Operate(lambda clip: clip // Equal(Beat(0))**Steps(1))
    add_rest = Operate(lambda clip: clip * Rest(1/1))
    # Chaining all the transformations
    global_transform = split_1**split_2**split_3**add_rest
    # simple_cuts >> Plot(transform=global_transform)

    simple_cuts << global_transform
    simple_cuts[4] % Duration() >> Print()
    # simple_cuts >> Plot()

    assert simple_cuts[4] % Duration() == Beats(3) - Steps(1)

# test_transform_note()


