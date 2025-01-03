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



# def test_track_mod():

#     # Perform the operation
#     default_track = Track()
#     assert default_track % str() == "Default"
#     test_track_1 = Track("Test")
#     test_track_2 = Track("Test")
#     assert test_track_1 == test_track_2

def test_key_offset():

    pitch: Pitch = Pitch()  # Pitch 60, Key 0
    assert pitch.octave_key_offset(0) == (0, 0)
    assert pitch.octave_key_offset(3) == (0, 3)
    assert pitch.octave_key_offset(12) == (1, 0)
    assert pitch.octave_key_offset(15) == (1, 3)
    
    assert pitch.octave_key_offset(-3) == (-1, 9)
    assert pitch.octave_key_offset(-12) == (-1, 0)
    assert pitch.octave_key_offset(-15) == (-2, 9)

    pitch << "D"            # Pitch 62, Key 2
    assert pitch.octave_key_offset(0) == (0, 0)
    assert pitch.octave_key_offset(3) == (0, 3)
    assert pitch.octave_key_offset(12) == (1, 0)
    assert pitch.octave_key_offset(15) == (1, 3)
    
    assert pitch.octave_key_offset(-3) == (-1, +9)
    assert pitch.octave_key_offset(-12) == (-1, 0)
    assert pitch.octave_key_offset(-15) == (-2, +9)


def test_pitch_mod():

    # Perform the operation
    pitch = Pitch()
    assert pitch % int() == 60      # middle C
    assert pitch % float() == 60.0  # middle C
    assert pitch % Key() % str() == "C"
    assert (pitch + Octave()) % float() == 60 + 12
    assert (pitch + 1) % float() == 60 + 2
    assert not pitch % Sharp()
    assert (pitch + 1.0) % Sharp()
    assert (pitch + 1.0 << Natural()) % float() == 60

# test_pitch_mod()


def test_scale_mod():

    # Perform the operation
    scale = Scale()
    assert scale % str() == "Major"
    assert scale.modulate(6) % str() == "minor" # 6th Mode
    assert scale % Mode() % str() == "1st"

    fifth_transposition: int = Scale("Major") % Transposition(5 - 1)
    assert fifth_transposition == 7 # Semitones


def test_pitch_set():

    pitch_1 = Pitch(Sharp(), Degree(2), Scale("minor"))
    pitch_2 = Pitch()
    pitch_2.sharp().degree(2).scale("minor")
    assert pitch_1 == pitch_2



def test_pitch_key_signature():

    major_keys_signatures: list[str] = [
        "B", "Gb", "Db", "Ab", "Eb", "Bb", "F",
        "C",
        "G", "D", "A", "E", "B", "F#", "C#"
    ]
    pitch_key = Pitch()
    for signature in range(len(major_keys_signatures)): # Major
        print(f"Major Signature: {signature - 7}")
        pitch_key << KeySignature(signature - 7)
        assert pitch_key % str() == major_keys_signatures[signature]

    minor_keys_signatures: list[str] = [
        "Ab", "Eb", "Bb", "F", "C", "G", "D",
        "A",
        "E", "B", "F#", "C#", "G#", "D#", "A#"
    ]
    for signature in range(len(minor_keys_signatures)): # Minor
        print(f"minor Signature: {signature - 7}")
        pitch_key << KeySignature(signature - 7, Minor())
        assert pitch_key % str() == minor_keys_signatures[signature]

    c_major_scale: Scale = Scale()

    for scale_mode in range(7):         # For Sharps
        key_signature: KeySignature = KeySignature(scale_mode)
        key_signature_list: list = key_signature % list()
        pitch_key: Key = key_signature % Key()
        scale_mode_list: list = c_major_scale % pitch_key
        print(scale_mode)
        print(pitch_key % str())
        print(key_signature_list)
        print(scale_mode_list)
        assert key_signature_list == scale_mode_list

    for scale_mode in range(0, -7, -1): # For Flats
        key_signature: KeySignature = KeySignature(scale_mode)
        key_signature_list: list = key_signature % list()
        pitch_key: Key = key_signature % Key()
        scale_mode_list: list = c_major_scale % pitch_key
        print(scale_mode)
        print(pitch_key % str())
        print(key_signature_list)
        print(scale_mode_list)
        assert key_signature_list == scale_mode_list

    E_minor_key: Pitch = Pitch(KeySignature("#", Minor()))
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

# test_pitch_key_signature()


def test_pitch_add():

    # Perform the operation
    pitch_1 = Pitch("A")
    pitch_1.getSerialization() % Data("degree") >> Print()
    (pitch_1 + 1).getSerialization() % Data("degree") >> Print()
    assert pitch_1 + 1    == Pitch("B")
    assert pitch_1 + 2.0  == Pitch("B")

    pitch_2 = Pitch(KeySignature(1)) << Degree("iii")  # Become Key B (60.0 + 11.0 = 71.0)
    assert pitch_2 % Octave() == 4
    assert (pitch_2 + 2) % Octave() == 5
    pitch_2 % int() >> Print()
    assert pitch_2 % int() == Pitch("B") % int()
    (pitch_2 + 2) % float() >> Print()          # 74.0
    (Pitch("D") + 12.0) % float() >> Print()    # 74.0
    assert pitch_2 + 2 == Pitch("D") + 12.0 # Next octave
    assert pitch_1 << Sharp() == Pitch("A") + 1.0
    assert pitch_1 << Natural() == Pitch("A")
    assert Pitch("Ab") == Pitch("A") - 1.0

    pitch_3: Pitch = Pitch()
    assert pitch_3 % str() == "C"

    # Test all semitones from 0 to 11
    expected_keys: list[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    for key_i in range(12):
        (pitch_3 + Semitone(key_i)) % str() >> Print()
        assert (pitch_3 + Semitone(key_i)) % str() == expected_keys[key_i]

    print("------")
    keys: list = ["C", "D", "E", "F", "G", "A", "B"]
    for degree in range(7):
        (pitch_3 << Degree(degree + 1)) % str() >> Print()
        assert pitch_3 << Degree(degree + 1) == keys[degree]

    pitch_4: Pitch = Pitch()
    assert pitch_4 % str() == "C"

    print("------")
    # Test all semitones from 0 to 11
    expected_pitches_float: list[str] = [60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0, 70.0, 71.0]
    for key_i in range(12):
        (pitch_4 + Semitone(key_i)) % float() >> Print()
        assert (pitch_4 + Semitone(key_i)) % float() == expected_pitches_float[key_i]

    print("------")
    white_pitches: list = [60.0, 62.0, 64.0, 65.0, 67.0, 69.0, 71.0]
    for degree in range(7):
        (pitch_4 << Degree(degree + 1)) % float() >> Print()
        assert (pitch_4 << Degree(degree + 1)) % float() == white_pitches[degree]

    print("------")
    pitch_5: Pitch = Pitch()
    (pitch_5 + 0.0) % str() >> Print()
    assert pitch_5 + 0.0 == Key("C")
    (pitch_5 + 1.0) % str() >> Print()
    assert pitch_5 + 1.0 == Key("C#")
    pitch_5 << Degree(2)
    (pitch_5 + 0.0) % str() >> Print()
    assert pitch_5 + 0.0 == Key("D")
    (pitch_5 + 1.0) % str() >> Print()
    assert pitch_5 + 1.0 == Key("D#")

# test_pitch_add()



