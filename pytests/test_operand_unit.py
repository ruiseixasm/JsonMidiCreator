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



def test_unit_set():
    unit_1 = Unit(7)
    unit_2 = Unit()
    unit_2.unit(7)
    assert unit_2 == unit_1


def test_unit_mod():

    # Perform the operation
    integer_1 = Unit(12)
    integer_2 = Unit(10)

    assert integer_1 + integer_2 == 12 + 10
    assert integer_1 - integer_2 == 12 - 10
    assert integer_1 * integer_2 == 12 * 10
    assert integer_1 / integer_2 == int(12 / 10)


def test_key_signature():

    key_signature: KeySignature = KeySignature()
    assert key_signature % list() == [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]   # Major scale
    key_signature << Minor()
    assert key_signature % list() == [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]   # minor scale


def test_tonic_key_signature():

    signature: int = -2     # Two flats bb
    key_signature_single: KeySignature = KeySignature(signature)

    print(f"Major Signature: {signature}, returned {int( key_signature_single % float() ) % 12}")
    assert int( key_signature_single % float() ) % 12 == 10   # Bb is 10

    print("------")
    major_tonic_keys_int: list[int] = [
        11, 6, 1, 8, 3, 10, 5,
        0,
        7, 2, 9, 4, 11, 6, 1
    ]
    for signature in range(len(major_tonic_keys_int)): # Major
        key_signature: KeySignature = KeySignature(signature - 7)
        print(f"Major Signature: {signature - 7}, returned {int( key_signature % float() ) % 12}")
        assert int( key_signature % float() ) % 12 == major_tonic_keys_int[signature]

    print("------")
    minor_tonic_keys_int: list[int] = [
        8, 3, 10, 5, 0, 7, 2,
        9,
        4, 11, 6, 1, 8, 3, 10
    ]
    for signature in range(len(minor_tonic_keys_int)): # minor
        key_signature: KeySignature = KeySignature(signature - 7, Minor())
        print(f"minor Signature: {signature - 7}, returned {int( key_signature % float() ) % 12}")
        assert int( key_signature % float() ) % 12 == minor_tonic_keys_int[signature]

# test_tonic_key_signature()


def test_drum_kit():

    assert DrumKit("Drum")      == 35   # White Key
    assert DrumKit("Hi-Hat")    == 42   # Black Key
    assert DrumKit("Clap")      == 39   # Black Key

