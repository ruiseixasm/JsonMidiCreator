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


def test_vectors_distance():
    single_pitch = Note() / 4
    different_pitch = ~single_pitch << Iterate(1)**Degree()
    clips_distance = Vectors(different_pitch) - Vectors(single_pitch)
    print(f"Distance: {clips_distance % str()}")
    assert clips_distance > 0
    assert clips_distance == 11
    clips_variations = clips_distance % Variations()
    assert clips_variations == 3    # Only the last 3 notes have the degree changed

# test_vectors_distance()


def test_vectors_keys():
    single_pitch = Note() / 4
    single_vectors = Vectors(single_pitch)
    all_keys = single_vectors % set()
    print(f"Keys: {all_keys}")
    assert all_keys == {'channel', 'duration', 'pitch', 'position', 'velocity'}
    
# test_vectors_keys()


def test_new_key():
    four_notes = Note() / 4
    two_notes = Note() / 2
    # Adding
    added_vectors_1 = Vectors(four_notes) + Vectors(two_notes)
    assert added_vectors_1 % Distance({"new"}) == 2
    added_vectors_2 = Vectors(two_notes) + Vectors(four_notes)
    assert added_vectors_2 % Distance({"new"}) == 2
    # Subtracting
    added_vectors_3 = Vectors(four_notes) - Vectors(two_notes)
    assert added_vectors_3 % Distance({"new"}) == +2
    added_vectors_4 = Vectors(two_notes) - Vectors(four_notes)
    print(f"added_vectors_4 distance: {added_vectors_4 % Distance({"new"}) % int()}")
    assert added_vectors_4 % Distance({"new"}) == +2    # Distance is always positive
    print(f"added_vectors_4 total: {added_vectors_4 % Total({"new"}) % int()}")
    assert added_vectors_4 % Total({"new"}) == -2

# test_new_key()

