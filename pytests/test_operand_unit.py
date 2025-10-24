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

    assert not key_signature is None
    assert not key_signature == None

# test_key_signature()


def test_tonic_key_signature():

    signature: int = -2     # Two flats bb
    key_signature_single: KeySignature = KeySignature(signature)

    print(f"Major Signature: {signature}, returned {key_signature_single % TonicKey() % int() % 12}")
    assert int( key_signature_single % TonicKey() % int() ) % 12 == 10   # Bb is 10

    print("------")
    major_tonic_keys_int: list[int] = [
        11, 6, 1, 8, 3, 10, 5,
        0,
        7, 2, 9, 4, 11, 6, 1
    ]
    for signature in range(len(major_tonic_keys_int)): # Major
        key_signature: KeySignature = KeySignature(signature - 7)
        print(f"Major Signature: {signature - 7}, returned {key_signature % TonicKey() % int() % 12}")
        assert key_signature % TonicKey() % int() % 12 == major_tonic_keys_int[signature]

    print("------")
    minor_tonic_keys_int: list[int] = [
        8, 3, 10, 5, 0, 7, 2,
        9,
        4, 11, 6, 1, 8, 3, 10
    ]
    for signature in range(len(minor_tonic_keys_int)): # minor
        key_signature: KeySignature = KeySignature(signature - 7, Minor())
        print(f"minor Signature: {signature - 7}, returned {key_signature % TonicKey() % int() % 12}")
        assert key_signature % TonicKey() % int() % 12 == minor_tonic_keys_int[signature]

# test_tonic_key_signature()


def test_enharmonic_key():

    key_signature = KeySignature(+6)
    # assert key_signature.is_enharmonic_old(6, 5)
    assert key_signature.is_enharmonic(6, 5)
    # assert key_signature.is_enharmonic_new(6, 5)
    key_signature = KeySignature(+7)
    # assert key_signature.is_enharmonic_old(1, 0)
    # assert key_signature.is_enharmonic_old(1, 5)
    assert key_signature.is_enharmonic(1, 0)
    assert key_signature.is_enharmonic(1, 5)
    # assert key_signature.is_enharmonic_new(1, 0)
    # assert key_signature.is_enharmonic_new(1, 5)

    key_signature = KeySignature(-6)
    # assert key_signature.is_enharmonic_old(6, 11)
    assert key_signature.is_enharmonic(6, 11)
    # assert key_signature.is_enharmonic_new(6, 11)
    key_signature = KeySignature(-7)
    # assert key_signature.is_enharmonic_old(11, 4)
    # assert key_signature.is_enharmonic_old(11, 11)
    assert key_signature.is_enharmonic(11, 4)
    assert key_signature.is_enharmonic(11, 11)
    # assert key_signature.is_enharmonic_new(11, 4)
    # assert key_signature.is_enharmonic_new(11, 11)

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


def test_degree_string():
    degree = Degree()
    assert degree == 1.0
    assert degree == "1"

    degree << "2"
    assert degree == 2.0
    assert degree == "2"

    degree << "2#"
    assert degree == 2.1
    assert degree == "2#"

    degree << "2b"
    assert degree == 2.2
    assert degree == "2b"

# test_degree_string()


def test_add_degree():
    sharp_degree = Degree(2.1)
    flat_degree = Degree(3.2)
    print(f"(sharp_degree + flat_degree) % Degree(): {(sharp_degree + flat_degree) % Degree() % float()}")
    assert sharp_degree + flat_degree == Degree(5.0)    # Flat cancels sharp

    degree_3 = Degree(3)
    degree_5 = Degree(5)
    assert degree_3 + degree_5 == 3 + 5

    degree_0: float = -4.8
    degree_1 = Degree(1)
    print(f"Degree(degree_0) % int(): {Degree(degree_0) % int()}")
    assert Degree(degree_0) % int() == -4
    print(f"Degree(degree_0)._semitones: {Degree(degree_0)._semitones}")
    assert Degree(degree_0)._semitones == 0.8
    print(f"Degree(degree_0) % float(): {Degree(degree_0) % float()}")
    assert Degree(degree_0) % float() == -4.8
    assert Degree(degree_0) == degree_0
    new_degree = Degree(degree_0) + degree_1
    print(f"new_degree % float(): {new_degree % float()}")
    assert new_degree == -3.8   # -4.8 + 1.0

    assert Degree(-1.8) + Degree(1) == 0.8  # It's positive because the degree is 0 and the semitones are always positive

    degree_1 = Degree(1)
    degree_7 = degree_1 + Degree(6)
    degree_7_1 = degree_7 + Degree(0.1)

    assert degree_1 == 1.0
    assert degree_7 == 7.0
    assert degree_7_1 == 7.1

# test_add_degree()


def test_sub_degree():
    sharp_degree = Degree(2.1)  # .1 means Sharp
    flat_degree = Degree(3.2)   # .2 means Flat
    print(f"(sharp_degree - flat_degree) % Degree(): {(sharp_degree - flat_degree) % Degree() % float()}")
    assert sharp_degree - flat_degree == Degree(-1.3)    # Sharp plus sharp = 0.3

    degree_3 = Degree(3)
    degree_5 = Degree(5)
    assert degree_5 - degree_3 == 5 - 3
    assert degree_3 - degree_5 == (5 - 3) * -1

    zero_degree = Degree(0)
    assert sharp_degree - Degree(2.1) == zero_degree
    assert sharp_degree + Degree(-2.2) == zero_degree
    assert sharp_degree + Degree(2.1) * -1 == zero_degree

# test_sub_degree()


def test_mul_degree():
    degree = Degree(2.1)

    assert degree * 2 == Degree(4.3)
    assert degree * 1 == Degree(2.1)
    assert degree * 0 == Degree(0)
    assert degree * -1 == Degree(-2.2)
    assert degree * -2 == Degree(-4.4)


def test_degree_set():
    assert Degree(-0.8) == +0.8
    assert Degree(-0.7) == +0.7 # 0 is always positive!
    assert Degree(-0.1) == +0.1 # 0 is always positive!


def test_size_set():
    size = Size()
    assert size % int() == 3

    size << "7th"
    assert size % int() == 4

# test_size_set()


def test_key_signature_by_key():

    A_minor = KeySignature(Minor())
    print(f"A_minor % str(): {A_minor % str()}")
    assert A_minor == ''
    assert A_minor == Key("A")

    A_minor << Key("D")
    assert A_minor == 'b'
    assert A_minor == Key("D")

