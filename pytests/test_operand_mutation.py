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



def test_mutation_mod():

    four_notes = Note() * 4 << Cycle(1, 3, 4, 5)**Pitch()
    # Perform the operation
    mutation = Exchange() * 100 # Position parameter by default
    # four_notes remains the same, just like mutation
    clip_100_1 = four_notes * mutation
    assert clip_100_1 != four_notes # Different positions
    mutation.reset()    # Resets the Chaos and sets Clip to None
    mutation *= 100     # Configured to the same value as in the start of mutation
    assert four_notes * mutation == clip_100_1
    clip_100_2 = four_notes * (mutation * 100) 
    # Shuffled Note positions
    assert clip_100_1 != clip_100_2

# test_mutation_mod()


def test_translocation():

    eight_notes = Note() * 8
    two_notes = Note() * 2

    translocation = Translocation()
    assert eight_notes.len() == 8
    eight_notes <<= translocation
    assert eight_notes.len() + translocation.len() ==  2 * 8
    two_notes <<= translocation

    assert eight_notes.len() != 8
    assert two_notes.len() != 2
    eight_notes_len = eight_notes.len()
    two_notes_len = two_notes.len()
    assert eight_notes_len + two_notes_len + translocation.len() == 10 + 8

# test_translocation()
