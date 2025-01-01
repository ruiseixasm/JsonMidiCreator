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



def test_unit_set():
    unit_1 = Unit(7)
    unit_2 = Unit()
    unit_2.unit(7)
    assert unit_2 == unit_1

    key_1 = Key(Sharp(), Degree(2), Scale("minor"))
    key_2 = Key()
    key_2.sharp().degree(2).scale("minor")
    assert key_1 == key_2

def test_unit_mod():

    # Perform the operation
    integer_1 = Unit(12)
    integer_2 = Unit(10)

    assert integer_1 + integer_2 == 12 + 10
    assert integer_1 - integer_2 == 12 - 10
    assert integer_1 * integer_2 == 12 * 10
    assert integer_1 / integer_2 == int(12 / 10)

def test_key_signature_mod():

    major_keys_signatures: list[int] = [
        "B", "Gb", "Db", "Ab", "Eb", "Bb", "F",
        "C",
        "G", "D", "A", "E", "B", "F#", "C#"
    ]
    # major_keys_signatures: dict = {
    #     "B": -7, "Gb": -6, "Db": -5, "Ab": -4, "Eb": -3, "Bb": -2, "F": -1,
    #     "C": 0,
    #     "G": +1, "D": +2, "A": +3, "E": +4, "B": +5, "F#": +6, "C#": +7
    # }
    tonic_key = Key()
    for signature in range(len(major_keys_signatures)):
        tonic_key << KeySignature(signature - 7) << 0
        assert tonic_key % str() == major_keys_signatures[signature]

    minor_keys_signatures: dict = {
        "Ab": -7, "Eb": -6, "Bb": -5, "F": -4, "C": -3, "G": -2, "D": -1,
        "A": 0,
        "E": +1, "B": +2, "F#": +3, "C#": +4, "G#": +5, "D#": +6, "A#": +7
    }
    for key, signature in minor_keys_signatures.items():
        tonic_key << KeySignature(signature, Minor())
        assert tonic_key % str() == key

    c_major_scale: Scale = Scale()

    for scale_mode in range(7):
        key_signature: KeySignature = KeySignature(scale_mode)
        key_signature_list: list = key_signature % list()
        tonic_key: Key = key_signature % Key()
        scale_mode_list: list = c_major_scale % (tonic_key)
        # print(scale_mode)
        # print(tonic_key % str())
        # print(key_signature_list)
        # print(scale_mode_list)
        assert key_signature_list == scale_mode_list

    for scale_mode in range(0, -7, -1):
        key_signature: KeySignature = KeySignature(scale_mode)
        key_signature_list: list = key_signature % list()
        tonic_key: Key = key_signature % Key()
        scale_mode_list: list = c_major_scale % (tonic_key)
        # print(scale_mode)
        # print(tonic_key % str())
        # print(key_signature_list)
        # print(scale_mode_list)
        assert key_signature_list == scale_mode_list

    E_minor_key: Key = Key(KeySignature("#", Minor()))
    assert E_minor_key % str() == "E"
    E_minor_key << Sharps(2) << Degree(3)
    assert E_minor_key % str() == "D"
    B_minor_scale_list: list = ["B", "C#", "D", "E", "F#", "G", "A"]
    # Sharp and Flat shall not be set by Degree
    for key_degree in range(1, 8):
        print(key_degree)
        E_minor_key << Degree(key_degree)
        assert E_minor_key % str() == B_minor_scale_list[key_degree - 1]
        E_minor_key % Sharp() >> Print(0)

test_key_signature_mod()


def test_key_mod():

    # Perform the operation
    key_1 = Key("A")
    key_1.getSerialization() % Data("degree") >> Print()
    (key_1 + 1).getSerialization() % Data("degree") >> Print()
    assert key_1 + 1    == Key("B")
    assert key_1 + 2.0  == Key("B")

    key_2 = Key(KeySignature(1)) << Degree("iii")  # Become Key B
    assert key_2 % int() == Key("B") % int()
    # (key_2 + 2) % float() >> Print()
    # (Key("D") + 12.0) % float() >> Print()
    assert key_2 + 2 == Key("D") + 12.0
    assert key_1 << Sharp() == Key("A") + 1.0
    assert Key("Ab") == Key("A") - 1.0

# def test_track_mod():

#     # Perform the operation
#     track_drums = Track("Drums", Channel(10))
#     track_pad = Track("Pad")

#     assert track_drums != track_pad
#     assert track_drums % Channel() != track_pad % Channel()
#     assert track_drums % str() != track_pad % str()
#     assert track_drums % MidiTrack() != track_pad % MidiTrack()
#     assert track_drums % MidiTrack() % str() == track_pad % MidiTrack() % str()
#     assert track_drums % Device() == track_pad % Device()
