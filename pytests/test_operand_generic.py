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



# def test_track_mod():

#     # Perform the operation
#     default_track = Track()
#     assert default_track % str() == "Default"
#     test_track_1 = Track("Test")
#     test_track_2 = Track("Test")
#     assert test_track_1 == test_track_2

def test_staff_mod():

    # Perform the operation
    staff_1 = Staff()
    staff_2 = staff_1.copy()
    
    assert staff_1 == staff_2
    assert staff_1 % Tempo() % float() == 120.0
    assert staff_1 % BeatsPerMeasure() % float() == 4.0
    staff_1 << 110
    assert staff_1 != staff_2


def test_staff_parameters():

    assert defaults % Tempo() == 120.0
    defaults << Tempo(145)
    assert defaults % Tempo() == 145.0
    defaults << Tempo(120)
    assert defaults % Tempo() == 120.0

    assert defaults % KeySignature() == 0
    defaults << KeySignature(2)
    assert defaults % KeySignature() == 2
    defaults << KeySignature()

# test_staff_parameters()


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
    assert pitch % int() == 1       # 1st Degree
    assert pitch % float() == 60.0  # middle C
    assert pitch % Key() % str() == "C"
    assert (pitch + Octave()) % float() == 60 + 12
    assert (pitch + 1) % float() == 60 + 2
    assert not pitch % Sharp()
    assert (pitch + 1.0) % Sharp()
    assert (pitch + 1.0 << Natural()) % float() == 60

# test_pitch_mod()


def test_pitch_tonic():

    pitch = Pitch()

    assert pitch % Tonic() == "C"

    defaults << Scale("Dorian")

    assert pitch % Tonic() == "C"
    pitch << Degree(0)
    assert pitch % Tonic() == "D"

    defaults << Scale([])

# test_pitch_tonic()


def test_scale_mod():

    defaults << Scale([])

    # Perform the operation
    scale = Scale()
    assert scale % str() == "Major"
    assert scale.modulate(6) % str() == "minor" # 6th Mode
    assert scale % Mode() % str() == "1st"

    fifth_transposition: int = Scale("Major") % Transposition(5 - 1)
    assert fifth_transposition == 7 # Semitones

    scale.clear()

    assert scale % str() == "Major"
    scale << KeySignature(Minor()) % list()
    assert scale % str() == "minor"


def test_pitch_set():

    defaults << Scale("minor")

    pitch_1 = Pitch(Sharp(), Degree(2))
    pitch_2 = Pitch()
    pitch_2.sharp().degree(2)
    assert pitch_1 == pitch_2

    defaults << Scale([])


def test_pitch_degrees():

    defaults << KeySignature() << Scale([])
    
    major_keys: list[int] = [
        60, 62, 64, 65, 67, 69, 71
    ]

    # White Tonic Key
    sharp_pitch = Pitch()   # With Degree 1
    for degree in range(1, 8):
        print(f"Key: {sharp_pitch % float()}")
        assert sharp_pitch % float() == major_keys[degree - 1]
        sharp_pitch += 1    # Increases by degree

    # Black Tonic Key
    print("------")
    sharp_pitch << 1 << 61.0    # Has to reset previous Degree to 1 first
    for degree in range(1, 8):
        print(f"Key: {sharp_pitch % float()}")
        assert sharp_pitch % float() == major_keys[degree - 1] + 1
        sharp_pitch += 1    # Increases by degree

    print("------")
    key_pitch = Pitch() # It has a reference to defaults, so, only defaults need to be changed
    for flats_sharps in range(-7, 8):         # For all Flats and Sharps!
        defaults << KeySignature(flats_sharps)

        reference_keys: list[float] = []
        for degree in range(1, 8):
            key_pitch << 1 << 60.0 << degree    # Has to reset previous Degree to 1 first
            reference_keys.append( key_pitch % float() )

        for pitch_int in range(60, 72):
            print("---")
            key_pitch << 1 << float(pitch_int)  # Has to reset previous Degree to 1 first
            for degree in range(1, 8):
                key_pitch << degree
                print(f"Key: {key_pitch % float()}")
                assert key_pitch % float() == reference_keys[degree - 1] + (pitch_int - 60)

    print("------")
    defaults << KeySignature("###") # A Major scale key signature
    a_major_scale: list[str] = [
        "A", "B", "C#", "D", "E", "F#", "G#"
    ]
    a_degree_d_major_scale: list[str] = [
        "D", "E", "F#", "G#", "A", "B", "C#"
    ]
    pitch = Pitch(Key("D"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == a_degree_d_major_scale[degree]
        pitch += 1  # One degree each time

    print("---")
    a_degree_cs_major_scale: list[str] = [
        "C#", "D", "E", "F#", "G#", "A", "B"
    ]
    pitch = Pitch(Key("C#"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == a_degree_cs_major_scale[degree]
        pitch += 1  # One degree each time

    print("---")
    pitch = Pitch(Key("C")) # Shall become C# because in A Major C is sharped
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == a_degree_cs_major_scale[degree]
        pitch += 1  # One degree each time

    print("---")
    a_degree_f_major_scale: list[str] = [
        "F#", "G#", "A", "B", "C#", "D", "E"
    ]
    pitch = Pitch(Key("F"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == a_degree_f_major_scale[degree]
        pitch += 1  # One degree each time

    print("---")
    a_degree_f_major_scale: list[str] = [
        "G#", "A", "B", "C#", "D", "E", "F#"
    ]
    pitch = Pitch(Key("G"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == a_degree_f_major_scale[degree]
        pitch += 1  # One degree each time

    print("------")
    defaults << KeySignature("##") # D Major scale key signature
    d_major_scale: list[str] = [
        "D", "E", "F#", "G", "A", "B", "C#"
    ]
    pitch = Pitch()
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == d_major_scale[degree]
        pitch += 1  # One degree each time

    print("---")
    d_degree_fs_major_scale: list[str] = [
        "F#", "G", "A", "B", "C#", "D", "E"
    ]
    pitch = Pitch(Key("F#"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == d_degree_fs_major_scale[degree]
        pitch += 1  # One degree each time
    print("---")
    pitch = Pitch(Key("F"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == d_degree_fs_major_scale[degree]
        pitch += 1  # One degree each time

    print("------")
    defaults << KeySignature("b") # F Major scale key signature
    f_major_scale: list[str] = [
        "F", "G", "A", "Bb", "C", "D", "E"
    ]
    pitch = Pitch()
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == f_major_scale[degree]
        pitch += 1  # One degree each time

    print("---")
    f_degree_bb_major_scale: list[str] = [
        "Bb", "C", "D", "E", "F", "G", "A"
    ]
    pitch = Pitch(Key("Bb"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == f_degree_bb_major_scale[degree]
        pitch += 1  # One degree each time
    print("---")
    pitch = Pitch(Key("B"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == f_degree_bb_major_scale[degree]
        pitch += 1  # One degree each time

    print("------")
    defaults << KeySignature("bb") # Bb Major scale key signature
    bb_major_scale: list[str] = [
        "Bb", "C", "D", "Eb", "F", "G", "A"
    ]
    pitch = Pitch()
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == bb_major_scale[degree]
        pitch += 1  # One degree each time

    print("---")
    bb_degree_eb_major_scale: list[str] = [
        "Eb", "F", "G", "A", "Bb", "C", "D"
    ]
    pitch = Pitch(Key("Eb"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == bb_degree_eb_major_scale[degree]
        pitch += 1  # One degree each time
    print("---")
    pitch = Pitch(Key("E"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"Key: {pitch % str()}")
        assert pitch == bb_degree_eb_major_scale[degree]
        pitch += 1  # One degree each time


    # Resets the defaults
    defaults << KeySignature() << Scale([])

# test_pitch_degrees()


def test_pitch_key_signature():

    defaults << KeySignature() << Scale([])

    defaults << KeySignature("###") # A Major scale
    a_major_scale: list[str] = [
        "A", "B", "C#", "D", "E", "F#", "G#"
    ]
    pitch = Pitch()
    for degree in {1, 2, 3, 4, 5, 6, 7}:
        assert pitch == a_major_scale[degree - 1]
        pitch += 1  # Increases by 1 degree

    pitch << Tonic(3)   # (3) D♯ Major with A Major Key Signature (###)
    ds_major_scale: list[str] = [
        # "D#", "E#", "F##", "G#", "A#", "B#", "C##"
        "D#", "E#", "F##", "G#", "A#", "B#", "D"
    ]
    for degree in {1, 2, 3, 4, 5, 6, 7}:
        print(f"Key: {pitch % str()}")
        assert pitch == ds_major_scale[degree - 1]
        pitch += 1  # Increases by 1 degree


    defaults << KeySignature()

    major_keys_signatures: list[str] = [
        "Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F",
        "C",
        "G", "D", "A", "E", "B", "F#", "C#"
    ]
    for signature in range(len(major_keys_signatures)): # Major

        defaults << KeySignature(signature - 7)
        pitch_key: Pitch = Pitch()

        print(f"Major Signature: {signature - 7}, result: {pitch_key % str()}")
        assert pitch_key % str() == major_keys_signatures[signature]

    minor_keys_signatures: list[str] = [
        "Ab", "Eb", "Bb", "F", "C", "G", "D",
        "A",
        "E", "B", "F#", "C#", "G#", "D#", "A#"
    ]
    for signature in range(len(minor_keys_signatures)): # Minor
        
        defaults << KeySignature(signature - 7, Minor())
        pitch_key: Pitch = Pitch()

        print(f"minor Signature: {signature - 7}, result: {pitch_key % str()}")
        assert pitch_key % str() == minor_keys_signatures[signature]

    c_major_scale: Scale = Scale()

    for scale_mode in range(7):         # For Sharps, shall be 8 but there is only 7 Diatonic scales to compare with!
        key_signature: KeySignature = KeySignature(scale_mode)
        key_signature_list: list = key_signature.get_modulated_scale_list()
        pitch_key: Key = key_signature % Key()
        scale_mode_list: list = c_major_scale % list([pitch_key])
        print(scale_mode)
        print(pitch_key % str())
        print(key_signature_list)
        print(scale_mode_list)
        assert key_signature_list == scale_mode_list

    for scale_mode in range(0, -7, -1): # For Flats, shall be -8 but there is only 7 Diatonic scales to compare with!
        key_signature: KeySignature = KeySignature(scale_mode)
        key_signature_list: list = key_signature.get_modulated_scale_list()
        pitch_key: Key = key_signature % Key()
        scale_mode_list: list = c_major_scale % list([pitch_key])
        print(scale_mode)
        print(pitch_key % str())
        print(key_signature_list)
        print(scale_mode_list)
        assert key_signature_list == scale_mode_list

    defaults << KeySignature("#", Minor())
    E_minor_key: Pitch = Pitch()

    assert E_minor_key % str() == "E"
    defaults << Sharps(2)   # Changes to B minor (##) but remains the Tonic E
    E_minor_key << Degree(3)
    assert E_minor_key % str() == "G"
    E_minor_key << Tonic("B") << 1  # Starts by Degree 1 the Tonic
    E_minor_B_tonic_key: list = ["B", "C#", "D", "E", "F#", "G", "A"]   # Same as B minor
    # Sharp and Flat shall not be set by Degree
    print("------")
    for key_degree in range(1, 8):
        print(key_degree)
        assert E_minor_key % str() == E_minor_B_tonic_key[(key_degree - 1) % 7]
        E_minor_key % Sharp() >> Print(0)
        E_minor_key += 1    # Increases by 1 degree

    defaults << KeySignature()

# test_pitch_key_signature()


def test_pitch_scales():

    defaults << KeySignature() << Scale([])

    major_scale_keys: list[str] = [
        "C", "D", "E", "F", "G", "A", "B"
    ]

    defaults << Scale("Major")
    major_pitch: Pitch = Pitch()
    
    for degree_increase in range(7):  # Excludes 7
        print((major_pitch + degree_increase) % str())
        assert (major_pitch + degree_increase) % str() == major_scale_keys[degree_increase]

    print("------")
    minor_scale_keys: list[str] = [
        "A", "B", "C", "D", "E", "F", "G"
    ]
    defaults << Scale("minor")
    minor_pitch: Pitch = Pitch()
    
    for degree_increase in range(7):  # Excludes 7
        print((minor_pitch + degree_increase) % str())
        assert (minor_pitch + degree_increase) % str() == minor_scale_keys[degree_increase]

    defaults << Scale([])

# test_pitch_scales()


def test_set_chromatic_pitch():

    defaults << KeySignature() << Scale([])

    pitch: Pitch = Pitch()

    print(f"Pitch: {pitch % float()}")
    assert pitch % float() == 60.0

    for degree in range(1, 8):
        print(f"------------ {degree} ------------")
        pitch << degree
        for pitch_int in range(128):
            pitch_float: float = float(pitch_int)
            pitch.set_chromatic_pitch(pitch_float)
            pitch % float() >> Print()
            assert pitch == pitch_float

    for sharps in range(1, 8): # 8 is excluded
        print(f"------------ {sharps} ------------")
        defaults << KeySignature(sharps)
        for pitch_int in range(128):
            pitch_float: float = float(pitch_int)
            pitch.set_chromatic_pitch(pitch_float)
            pitch % float() >> Print()
            assert pitch == pitch_float

    for flats in range(-1, -8, -1): # 8 is excluded
        print(f"------------ {flats} ------------")
        defaults << KeySignature(flats)
        for pitch_int in range(128):
            pitch_float: float = float(pitch_int)
            pitch.set_chromatic_pitch(pitch_float)
            pitch % float() >> Print()
            assert pitch == pitch_float

    defaults << KeySignature()

# test_set_chromatic_pitch()


def test_pitch_add():

    defaults << KeySignature() << Scale([])

    pitch_degree = Pitch()
    assert pitch_degree % Degree() == 1
    assert pitch_degree % Octave() == 4

    pitch_degree << Degree(8)
    assert pitch_degree % Degree() == 1
    assert pitch_degree % Octave() == 4

    pitch_degree += Degree(7)
    assert pitch_degree % Degree() == 1
    assert pitch_degree % Octave() == 5

    pitch_integer = Pitch()
    assert pitch_integer % int() == 1
    assert pitch_integer % Octave() == 4

    pitch_integer << 8
    assert pitch_integer % int() == 1
    assert pitch_integer % Octave() == 4

    pitch_integer += 7
    assert pitch_integer % int() == 1
    assert pitch_integer % Octave() == 5


    # Perform the operation
    pitch_b: Pitch = Pitch()    # 60.0
    assert pitch_b % float() == 60.0
    pitch_b += Semitone(2)
    assert pitch_b % float() == 62.0
    pitch_b += Semitone(12)
    assert pitch_b % float() == 74.0

    pitch_1: Pitch = Pitch("A")
    pitch_1.getSerialization() % Data("degree") >> Print()
    (pitch_1 + 1).getSerialization() % Data("degree") >> Print()
    assert pitch_1 + 1    == Pitch("B")
    assert pitch_1 + 2.0  == Pitch("B")

    defaults << KeySignature(1)
    pitch_2 = Pitch() << Degree("iii")  # Become Key B (60.0 + 11.0 = 71.0)
    assert pitch_2 % Octave() == 4
    assert (pitch_2 + 2) % Octave() == 5
    pitch_2 % float() >> Print()
    assert pitch_2 % float() == Pitch("B") % float()
    (pitch_2 + 2) % float() >> Print()          # 74.0
    (Pitch("D") + 12.0) % float() >> Print()    # 74.0
    assert pitch_2 + 2 == Pitch("D") + 12.0 # Next octave

    defaults << KeySignature()
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
        (pitch_3 + degree) % str() >> Print()
        assert pitch_3 + degree == keys[degree]


    pitch_4: Pitch = Pitch(60.0)    # Middle C (60)
    assert pitch_4 % str() == "C"
    assert pitch_4 % float() == 60.0

    # Test all semitones from 0 to 11
    chromatic_pitches: list[float] = [60.0, 61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0, 69.0, 70.0, 71.0]



    for sharps in range(8): # 8 is excluded

        defaults << KeySignature(sharps)
        pitch_4 << 60.0 # Middle C (60)
        print(f"------------ {sharps} ------------")
        print("--UP--")
        for key_i in range(12):
            (pitch_4 + Semitone(key_i)) % float() >> Print()
            assert (pitch_4 + Semitone(key_i)) % float() == chromatic_pitches[key_i]
        pitch_4 << 71.0
        print("-DOWN-")
        for key_i in range(12):
            pitch_4 % float() >> Print()
            assert pitch_4 % float() == chromatic_pitches[11 - key_i]
            pitch_4 -= 1.0

    for flats in range(0, -8, -1): # -8 is excluded

        defaults << KeySignature(flats)
        pitch_4 << 60.0 # Middle C (60)
        print(f"------------ {flats} ------------")
        print("--UP--")
        for key_i in range(12):
            (pitch_4 + Semitone(key_i)) % float() >> Print()
            assert (pitch_4 + Semitone(key_i)) % float() == chromatic_pitches[key_i]
        pitch_4 << 71.0
        print("-DOWN-")
        for key_i in range(12):
            pitch_4 % float() >> Print()
            assert pitch_4 % float() == chromatic_pitches[11 - key_i]
            pitch_4 -= 1.0


    defaults << KeySignature()
    pitch_4 << Pitch(60.0)    # Middle C (60)

    print(f"------------ DEGREES ------------")
    print("------")
    for key_i in range(12):
        (pitch_4 + Semitone(key_i)) % float() >> Print()
        assert (pitch_4 + Semitone(key_i)) % float() == chromatic_pitches[key_i]

    print("------")
    white_pitches: list[float] = [60.0, 62.0, 64.0, 65.0, 67.0, 69.0, 71.0]
    for degree in range(7):
        (pitch_4 + degree) % float() >> Print()
        assert (pitch_4 + degree) % float() == white_pitches[degree]

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

    defaults << KeySignature() << Scale([])

# test_pitch_add()


def test_drum_kit():

    defaults << KeySignature() << Scale([])

    pitch: Pitch = Pitch()

    print(pitch % float())
    assert pitch % float() == 60.0  # White Key
    pitch << 35.0
    print(pitch % float())
    assert pitch % float() == 35.0  # White Key
    pitch << 42.0
    print(pitch % float())
    assert pitch % float() == 42.0  # Black Key
    pitch << 39.0
    print(pitch % float())
    assert pitch % float() == 39.0  # Black Key

    pitch << DrumKit("Drum")
    print(pitch % float())
    assert pitch % float() == 35.0  # White Key
    pitch << DrumKit("Hi-Hat")
    print(pitch % float())
    assert pitch % float() == 42.0  # Black Key
    pitch << DrumKit("Clap")
    print(pitch % float())
    assert pitch % float() == 39.0  # Black Key

    # A different KeySignature
    pitch << KeySignature(-1)
    pitch << DrumKit("Hi-Hat")
    print(pitch % float())
    assert pitch % float() == 42.0  # Black Key
    pitch << DrumKit("Drum")
    print(pitch % float())
    assert pitch % float() == 35.0  # White Key
    assert pitch == 35.0  # White Key

# test_drum_kit()


def test_basic_conversions():

    position = Position(10.5)

    assert position % Measures() % Fraction() == 10.5
    assert position % Measure() % Fraction() == 10
    assert position % Beats() % Fraction() == 10.5 * 4
    assert position % Beat() % Fraction() == 2      # Second beat in the Measure 10
    assert position % Steps() % Fraction() == 10.5 * 4 * 4
    assert position % Step() % Fraction() == 2 * 4  # Eight step in the Measure 10
    assert position % Duration() % Fraction() == 10 * (1/1) + 2 * (1/4)

# test_basic_conversions()


def test_full_conversions():

    defaults << KeySignature() << Scale([])
    
    default_staff: Staff = defaults % Staff()

    for time_value in (Position(10.5), Measures(10.5), Beats(10.5 * 4),
                       Steps(10.5 * 4 * 4), Duration(10 * (1/1) + 2 * (1/4))):
        assert default_staff.convertToMeasures(time_value) == 10.5
        assert default_staff.convertToMeasure(time_value) == 10
        assert default_staff.convertToBeats(time_value) == 10.5 * 4
        assert default_staff.convertToBeat(time_value) == 2
        assert default_staff.convertToSteps(time_value) == 10.5 * 4 * 4
        assert default_staff.convertToStep(time_value) == 2 * 4
        assert default_staff.convertToDuration(time_value) == 10 * (1/1) + 2 * (1/4)
        assert default_staff.convertToLength(time_value) == 10.5

    for time_value in (Length(10.5)):
        assert default_staff.convertToMeasures(time_value) == 10.5
        assert default_staff.convertToMeasure(time_value) == 11   # Considers entire Measure where it's present
        assert default_staff.convertToBeats(time_value) == 10.5 * 4
        assert default_staff.convertToBeat(time_value) == 2
        assert default_staff.convertToSteps(time_value) == 10.5 * 4 * 4
        assert default_staff.convertToStep(time_value) == 2 * 4
        assert default_staff.convertToDuration(time_value) == 10 * (1/1) + 2 * (1/4)
        assert default_staff.convertToLength(time_value) == 10.5

    for time_unit in (Position(10), Length(10), Measure(10), Beat(10 * 4), Step(10 * 4 * 4)):
        assert default_staff.convertToMeasures(time_unit) == 10
        assert default_staff.convertToMeasure(time_unit) == 10
        assert default_staff.convertToBeats(time_unit) == 10 * 4
        assert default_staff.convertToBeat(time_unit) == 0
        assert default_staff.convertToSteps(time_unit) == 10 * 4 * 4
        assert default_staff.convertToStep(time_unit) == 0 * 4
        assert default_staff.convertToDuration(time_unit) == 10 * (1/1)
        assert default_staff.convertToLength(time_unit) == 10.0

# test_full_conversions()


def test_staff_output():

    defaults << KeySignature() << Scale([])
    
    staff = Staff()
    staff << TimeSignature(3, 4)
    steps_per_measure = staff % StepsPerMeasure()
    steps_per_measure % Fraction() >> Print()
    assert steps_per_measure == 12.0

    staff << TimeSignature(4, 4)
    steps_per_measure = staff % StepsPerMeasure()
    steps_per_measure % Fraction() >> Print()
    assert steps_per_measure == 16.0

    staff << StepsPerMeasure(12)
    steps_per_measure = staff % StepsPerMeasure()
    steps_per_measure % Fraction() >> Print()
    assert steps_per_measure == 12.0


# test_staff_output()


def test_pitch_shifting():
    pitch_f_major: Pitch = Pitch("F", Scale("Major"))

    assert pitch_f_major % str() == "F"
    assert pitch_f_major % Scale() % str() == "Major"

    modulated_keys: list[str] = ["F", "G", "A", "B", "C", "D", "E"]
    for modulation in range(7):
        print(f"M{modulation} : {(pitch_f_major + Modulation(modulation)) % str()}")
        assert (pitch_f_major + Modulation(modulation)) % str() == modulated_keys[modulation]

    transposed_keys: list[str] = ["F", "G", "A", "A#", "C", "D", "E"]
    for transposition in range(7):
        print(f"T{transposition} : {(pitch_f_major + Transposition(transposition)) % str()}")
        assert (pitch_f_major + Transposition(transposition)) % str() == transposed_keys[transposition]

test_pitch_shifting()

