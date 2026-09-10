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

    assert not key_signature is None
    assert not key_signature == None

# test_key_signature()


def test_enharmonic_key():

    sharps = +6
    assert KeySignature.is_enharmonic(5, sharps)
    sharps = +7
    assert KeySignature.is_enharmonic(0, sharps)
    assert KeySignature.is_enharmonic(5, sharps)

    sharps = -6
    assert KeySignature.is_enharmonic(11, sharps)
    sharps = -7
    assert KeySignature.is_enharmonic(4, sharps)
    assert KeySignature.is_enharmonic(11, sharps)

# test_enharmonic_key()


def test_drum_kit():

    assert DrumKit("Drum")      == 35   # White Key
    assert DrumKit("Hi-Hat")    == 42   # Black Key
    assert DrumKit("Clap")      == 39   # Black Key


def test_degree_accidentals():

    natural_degree = Degree()
    assert natural_degree % Natural()   == Natural(True)

    sharped_degree = Degree(Sharp())
    assert sharped_degree % Sharp()     == Sharp(True)
    assert sharped_degree % Natural()   != Natural(True)
    assert sharped_degree % Flat()      != Flat(True)

    flattened_degree = Degree(Flat())
    assert flattened_degree % Flat()    == Flat(True)
    assert flattened_degree % Natural() != Natural(True)
    assert flattened_degree % Sharp()   != Sharp(True)

    print(f"Sharp: {(natural_degree + Sharp(1)) % Sharp() % int()}")
    print(f"Flat: {(natural_degree - Flat(1)) % Sharp() % int()}")
    assert natural_degree + Sharp(1) == natural_degree - Flat(1)

# test_degree_accidentals()


def test_size_set():
    size = Size()
    assert size % int() == 3

    size << "7th"
    assert size % int() == 4

# test_size_set()


def test_degree_multi():
    assert Degree("") == Degree()
    assert Degree("Ab") == Degree()
    assert Degree("A#") == Degree()
    assert Degree("#") == Degree(1.0)
    assert Degree("bb") == Degree(-2.0)
    assert Degree("3bb") == Degree(3, -2.0)

    assert Degree("6") == 6
    assert Degree("9") == 9


def test_key_multi():
    assert Key(4) == 4
    assert Key(14) == 14
    assert Key("A")._unit == 9

# test_key_multi()

