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
    staff_1 = TimeSignature()
    staff_2 = staff_1.copy()
    
    assert staff_1 == staff_2
    # Tempo is centralized in defaults
    assert settings % Tempo() % float() == 120.0
    assert staff_1 % BeatsPerMeasure() % float() == 4.0


def test_staff_parameters():

    assert settings % Tempo() == 120.0
    settings << Tempo(145)
    assert settings % Tempo() == 145.0
    settings << Tempo(120)
    assert settings % Tempo() == 120.0

    assert settings % KeySignature() == 0
    settings << KeySignature(2)
    assert settings % KeySignature() == 2
    settings << KeySignature()

# test_staff_parameters()


def test_pitch_mod():

    # Perform the operation
    pitch = Pitch()
    assert pitch % float() == 1.0       # 1st Degree
    assert pitch % int() == 60  # middle C
    assert pitch % Key() % str() == "C"
    assert (pitch + Octave()) % int() == 60 + 12
    assert (pitch + 1.0) % int() == 60 + 2
    assert not pitch % Sharp()
    assert (pitch + 0.1) % Sharp()
    assert (pitch + 0.1 << Natural()) % int() == 60

# test_pitch_mod()


def test_pitch_tonic():

    pitch = Pitch()
    # Pitch keeps its own Key Signature
    pitch << KeySignature(2) # Dorian is the 2nd in the Circle of fifths

    assert pitch % TonicKey() == "C"
    pitch << None   # Resets the Tonic
    assert pitch % TonicKey() == "D"

    settings << KeySignature()

# test_pitch_tonic()


def test_scale_mod():

    # Perform the operation
    scale = Scale()
    assert scale % str() == "Major"
    assert scale.modulate(6) % str() == "minor" # 6th Mode

    fifth_transposition: int = Scale.transpose_key(5 - 1, Scale("Major") % list())
    assert fifth_transposition == 7 # Semitones

    scale.clear()

    assert scale % str() == "Major"
    scale << KeySignature(Minor()) % list()
    assert scale % str() == "minor"


def test_pitch_set():

    pitch_1 = Pitch(Sharp(), Degree(2))
    pitch_2 = Pitch()
    pitch_2.sharp().degree(2)
    assert pitch_1 == pitch_2


def test_pitch_degrees():

    settings << KeySignature()
    
    major_keys: list[int] = [
        60, 62, 64, 65, 67, 69, 71
    ]

    # White Tonic Key
    sharp_pitch = Pitch()   # With Degree 1
    for degree in range(1, 8):
        print(f"Pitch: {sharp_pitch % int()}")
        assert sharp_pitch % int() == major_keys[degree - 1]
        sharp_pitch += 1.0    # Increases by degree

    # Black Tonic Key
    print("------")
    sharp_pitch << 1.0 << 61    # Has to reset previous Degree to 1 first
    for degree in range(1, 8):
        print(f"Pitch: {sharp_pitch % int()}")
        assert sharp_pitch % int() == major_keys[degree - 1] + 1
        sharp_pitch += 1.0    # Increases by degree

    print("------")
    key_pitch = Pitch() # It has a reference to defaults, so, only defaults need to be changed
    for flats_sharps in range(-7, 8):         # For all Flats and Sharps!
        settings << KeySignature(flats_sharps)

        reference_keys: list[int] = []
        for degree in range(1, 8):
            key_pitch << 1.0 << 60 << float(degree)    # Has to reset previous Degree to 1 first
            reference_keys.append( key_pitch % int() )

        for pitch_int in range(60, 72):
            print("---")
            key_pitch << 1.0 << pitch_int  # Has to reset previous Degree to 1 first
            for degree in range(1, 8):
                print(f"Pitch: {key_pitch % int()}, Octave: {key_pitch._octave_0}, Tonic: {key_pitch._tonic_key}, "
                      f"Degree_0: {key_pitch._degree_0}, Degree: {key_pitch % Degree() % int()}, Transposition: {key_pitch._transposition}")
                assert key_pitch % int() == reference_keys[degree - 1] + (pitch_int - 60)
                key_pitch += float(1)  # += to increment Octave too

    # Resets the defaults
    settings << KeySignature()

# test_pitch_degrees()


def test_root_key():
    major_pitch = Pitch()
    assert major_pitch % Octave() == 4

    print("------")
    settings << KeySignature("###") # A Major scale key signature
    # The default Tonic key is A for "###" Key Signature
    # So, it ONLY uses A Major keys for root keys on the same scale

    a_degree_a_major_scale: list[str] = [
        "A", "B", "C#", "D", "E", "F#", "G#"
    ]
    pitch = Pitch() # KeySignature default Key
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == a_degree_a_major_scale[degree]
        pitch += 1.0  # One degree each time

    a_degree_d_major_scale: list[str] = [
        "D", "E", "F#", "G#", "A", "B", "C#"
    ]
    pitch = Pitch(RootKey("D"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == a_degree_d_major_scale[degree]
        pitch += 1.0  # One degree each time

    print("---")
    a_degree_cs_major_scale: list[str] = [
        "C#", "D", "E", "F#", "G#", "A", "B"
    ]
    pitch = Pitch(RootKey("C#"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == a_degree_cs_major_scale[degree]
        pitch += 1.0  # One degree each time

    print("---")
    a_degree_c_major_scale: list[str] = [
        "B#", "C#", "D#", "E#", "F##", "G#", "A#"
    ]
    pitch = Pitch(RootKey("C")) # Shall become C# because in A Major C is sharped
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == a_degree_c_major_scale[degree]
        pitch += 1.0  # One degree each time

    print("---")
    a_degree_f_major_scale: list[str] = [
        "E#", "F##", "G#", "A#", "B#", "C#", "D#"
    ]
    pitch = Pitch(RootKey("F"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == a_degree_f_major_scale[degree]
        pitch += 1.0  # One degree each time

    print("---")
    a_degree_f_major_scale: list[str] = [
        "F##", "G#", "A#", "B#", "C#", "D#", "E#"
    ]
    pitch = Pitch(RootKey("G"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == a_degree_f_major_scale[degree]
        pitch += 1.0  # One degree each time


    print("------")
    settings << KeySignature("##") # D Major scale key signature
    d_major_scale: list[str] = [
        "D", "E", "F#", "G", "A", "B", "C#"
    ]
    pitch = Pitch() # KeySignature default Key
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == d_major_scale[degree]
        pitch += 1.0  # One degree each time

    print("---")
    d_degree_fs_major_scale: list[str] = [
        "F#", "G", "A", "B", "C#", "D", "E"
    ]
    pitch = Pitch(RootKey("F#"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == d_degree_fs_major_scale[degree]
        pitch += 1.0  # One degree each time
    print("---")
    # It's right despite G# being strange !!
    d_degree_f_major_scale: list[str] = [
        "E#", "G", "G#", "A#", "B#", "D", "D#"
    ]
    pitch = Pitch(RootKey("F"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == d_degree_f_major_scale[degree]
        pitch += 1.0  # One degree each time


    print("------")
    settings << KeySignature("b") # F Major scale key signature
    f_major_scale: list[str] = [
        "F", "G", "A", "Bb", "C", "D", "E"
    ]
    pitch = Pitch() # KeySignature default Key
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == f_major_scale[degree]
        pitch += 1.0  # One degree each time

    print("---")
    f_degree_bb_major_scale: list[str] = [
        "Bb", "C", "D", "E", "F", "G", "A"
    ]
    pitch = Pitch(RootKey("Bb"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == f_degree_bb_major_scale[degree]
        pitch += 1.0  # One degree each time
    print("---")
    f_degree_b_major_scale: list[str] = [
        "Cb", "Db", "Eb", "F", "Gb", "Ab", "Bb"
    ]
    pitch = Pitch(RootKey("B"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == f_degree_b_major_scale[degree]
        pitch += 1.0  # One degree each time


    print("------")
    settings << KeySignature("bb") # Bb Major scale key signature
    bb_major_scale: list[str] = [
        "Bb", "C", "D", "Eb", "F", "G", "A"
    ]
    pitch = Pitch() # KeySignature default Key
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == bb_major_scale[degree]
        pitch += 1.0  # One degree each time

    print("---")
    bb_degree_eb_major_scale: list[str] = [
        "Eb", "F", "G", "A", "Bb", "C", "D"
    ]
    pitch = Pitch(RootKey("Eb"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == bb_degree_eb_major_scale[degree]
        pitch += 1.0  # One degree each time
    print("---")
    bb_degree_e_major_scale: list[str] = [
        "Fb", "Gb", "Ab", "A", "Cb", "Db", "D"
    ]
    pitch = Pitch(RootKey("E"))
    for degree in {0, 1, 2, 3, 4, 5, 6}:
        print(f"RootKey {degree}: {pitch % str()}")
        assert pitch == bb_degree_e_major_scale[degree]
        pitch += 1.0  # One degree each time

    # Resets the defaults
    settings << KeySignature()

# test_root_key()


def test_target_key():
    major_pitch = Pitch()
    assert major_pitch % Octave() == 4

    print("------")
    settings << KeySignature("###") # A Major scale key signature
    # The default Tonic key is A for "###" Key Signature
    # So, it ONLY uses A Major keys for root keys on the same scale

    a_degree_a_major_scale: list[str] = [
        "A", "B", "C#", "D", "E", "F#", "G#"
    ]
    pitch = Pitch() # KeySignature default Key
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == a_degree_a_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    a_degree_d_major_scale: list[str] = [
        "D", "E", "F#", "G#", "A", "B", "C#"
    ]
    pitch = Pitch(TargetKey("D"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == a_degree_d_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    print("---")
    a_degree_cs_major_scale: list[str] = [
        "C#", "D", "E", "F#", "G#", "A", "B"
    ]
    pitch = Pitch(TargetKey("C#"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == a_degree_cs_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    print("---")
    a_degree_c_major_scale: list[str] = [
        "B#", "C#", "D#", "E#", "F##", "G#", "A#"
    ]
    pitch = Pitch(TargetKey("C")) # Shall become C# because in A Major C is sharped
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == a_degree_c_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    print("---")
    a_degree_f_major_scale: list[str] = [
        "E#", "F##", "G#", "A#", "B#", "C#", "D#"
    ]
    pitch = Pitch(TargetKey("F"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == a_degree_f_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    print("---")
    a_degree_f_major_scale: list[str] = [
        "F##", "G#", "A#", "B#", "C#", "D#", "E#"
    ]
    pitch = Pitch(TargetKey("G"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == a_degree_f_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time


    print("------")
    settings << KeySignature("##") # D Major scale key signature
    d_major_scale: list[str] = [
        "D", "E", "F#", "G", "A", "B", "C#"
    ]
    pitch = Pitch() # KeySignature default Key
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == d_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    print("---")
    d_degree_fs_major_scale: list[str] = [
        "F#", "G", "A", "B", "C#", "D", "E"
    ]
    pitch = Pitch(TargetKey("F#"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == d_degree_fs_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time
    print("---")
    # It's right despite G# being strange !!
    d_degree_f_major_scale: list[str] = [
        "E#", "G", "G#", "A#", "B#", "D", "D#"
    ]
    pitch = Pitch(TargetKey("F"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == d_degree_f_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time


    print("------")
    settings << KeySignature("b") # F Major scale key signature
    f_major_scale: list[str] = [
        "F", "G", "A", "Bb", "C", "D", "E"
    ]
    pitch = Pitch() # KeySignature default Key
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == f_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    print("---")
    f_degree_bb_major_scale: list[str] = [
        "Bb", "C", "D", "E", "F", "G", "A"
    ]
    pitch = Pitch(TargetKey("Bb"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == f_degree_bb_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time
    print("---")
    f_degree_b_major_scale: list[str] = [
        "Cb", "Db", "Eb", "F", "Gb", "Ab", "Bb"
    ]
    pitch = Pitch(TargetKey("B"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == f_degree_b_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time


    print("------")
    settings << KeySignature("bb") # Bb Major scale key signature
    bb_major_scale: list[str] = [
        "Bb", "C", "D", "Eb", "F", "G", "A"
    ]
    pitch = Pitch() # KeySignature default Key
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == bb_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    print("---")
    bb_degree_eb_major_scale: list[str] = [
        "Eb", "F", "G", "A", "Bb", "C", "D"
    ]
    pitch = Pitch(TargetKey("Eb"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == bb_degree_eb_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time
    print("---")
    bb_degree_e_major_scale: list[str] = [
        "Fb", "Gb", "Ab", "A", "Cb", "Db", "D"
    ]
    pitch = Pitch(TargetKey("E"))
    for transposition in {0, 1, 2, 3, 4, 5, 6}:
        print(f"TargetKey {transposition}: {pitch % TargetKey() % str()}")
        assert pitch % TargetKey() == bb_degree_e_major_scale[transposition]
        pitch += Fraction(1)  # One transposition each time

    # Resets the defaults
    settings << KeySignature()

# test_target_key()


def test_pitch_key_signature():

    settings << KeySignature()

    settings << KeySignature("###") # A Major scale
    a_major_scale: list[str] = [
        "A", "B", "C#", "D", "E", "F#", "G#"
    ]
    pitch = Pitch()
    for degree in {1, 2, 3, 4, 5, 6, 7}:
        assert pitch == a_major_scale[degree - 1]
        pitch += 1.0  # Increases by 1 degree

    pitch << TonicKey(3)   # (3) D♯ Major with A Major Key Signature (###)
    ds_major_scale: list[str] = [
        # "D#", "E#", "F##", "G#", "A#", "B#", "C##"
        "D#", "E#", "F##", "G#", "A#", "B#", "D"
    ]
    for degree in {1, 2, 3, 4, 5, 6, 7}:
        print(f"Key: {pitch % str()}")
        assert pitch == ds_major_scale[degree - 1]
        pitch += 1.0  # Increases by 1 degree


    settings << KeySignature()

    major_keys_signatures: list[str] = [
        "Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F",
        "C",
        "G", "D", "A", "E", "B", "F#", "C#"
    ]
    for signature in range(len(major_keys_signatures)): # Major

        settings << KeySignature(signature - 7)
        pitch_key: Pitch = Pitch()

        print(f"Major Signature: {signature - 7}, result: {pitch_key % str()}")
        assert pitch_key % str() == major_keys_signatures[signature]

    minor_keys_signatures: list[str] = [
        "Ab", "Eb", "Bb", "F", "C", "G", "D",
        "A",
        "E", "B", "F#", "C#", "G#", "D#", "A#"
    ]
    for signature in range(len(minor_keys_signatures)): # Minor
        
        settings << KeySignature(signature - 7, Minor())
        pitch_key: Pitch = Pitch()

        print(f"minor Signature: {signature - 7}, result: {pitch_key % str()}")
        assert pitch_key % str() == minor_keys_signatures[signature]

    c_major_scale: Scale = Scale()

    for scale_mode in range(7):         # For Sharps, shall be 8 but there is only 7 Diatonic scales to compare with!
        key_signature: KeySignature = KeySignature(Mode(scale_mode + 1))
        key_signature_list: list = key_signature.get_scale()
        pitch_key: Key = key_signature % Key()
        scale_mode_list: list = c_major_scale.copy().modulation(scale_mode + 1)
        print(scale_mode)
        print(pitch_key % str())
        print(key_signature_list)
        print(scale_mode_list)
        assert key_signature_list == scale_mode_list

    for scale_mode in range(0, -7, -1): # For Flats, shall be -8 but there is only 7 Diatonic scales to compare with!
        key_signature: KeySignature = KeySignature(Mode(scale_mode + 1))
        key_signature_list: list = key_signature.get_scale()
        pitch_key: Key = key_signature % Key()
        scale_mode_list: list = c_major_scale.copy().modulation(scale_mode + 1)
        print(scale_mode)
        print(pitch_key % str())
        print(key_signature_list)
        print(scale_mode_list)
        assert key_signature_list == scale_mode_list

    settings << KeySignature("#", Minor())
    E_minor_key: Pitch = Pitch()

    assert E_minor_key % str() == "E"
    settings << Sharps(2)   # Changes to B minor (##) but remains the Tonic E
    E_minor_key << Degree(3)
    assert E_minor_key % str() == "G"
    E_minor_key << TonicKey("B") << 1.0  # Starts by Degree 1 the Tonic
    E_minor_B_tonic_key: list = ["B", "C#", "D", "E", "F#", "G", "A"]   # Same as B minor
    # Sharp and Flat shall not be set by Degree
    print("------")
    for key_degree in range(1, 8):
        print(key_degree)
        assert E_minor_key % str() == E_minor_B_tonic_key[(key_degree - 1) % 7]
        E_minor_key % Sharp() >> Print(0)
        E_minor_key += 1.0    # Increases by 1 degree

    settings << KeySignature()

# test_pitch_key_signature()


def test_pitch_scales():

    settings << KeySignature()

    staff_pitch: Pitch = Pitch()
    print(f"Tonic C: {staff_pitch % TonicKey() % str()}")
    assert staff_pitch % TonicKey() % str() == "C"
    
    major_scale_keys: list[str] = [
        "C", "D", "E", "F", "G", "A", "B"
    ]

    for degree in range(7):  # Excludes 7
        print((staff_pitch + float(degree)) % str())
        assert (staff_pitch + float(degree)) % str() == major_scale_keys[degree]

    print("------")
    # KeySignature is a Pitch attribute
    staff_pitch << Minor()
    minor_scale_keys: list[str] = [
        "A", "B", "C", "D", "E", "F", "G"
    ]
    staff_pitch << None # Auto sets the Key Signature tonic for "minor", meaning, A
    print(f"Tonic A: {staff_pitch % TonicKey() % str()}")
    assert staff_pitch % TonicKey() % str() == "A"
    for degree in range(7):  # Excludes 7
        print((staff_pitch + float(degree)) % str())
        assert (staff_pitch + float(degree)) % str() == minor_scale_keys[degree]

    settings << KeySignature()

# test_pitch_scales()


def test_set_chromatic_pitch():

    settings << KeySignature()

    pitch_ab = Pitch("Ab")
    pitch_a = Pitch("A")

    print(f"Ab scale, octave: {pitch_ab % (list(), (Octave(), int()))}")
    print(f"A scale, octave: {pitch_a % (list(), (Octave(), int()))}")

    print(f"Ab pitch_int: {pitch_ab.pitch_int()}")
    print(f"A pitch_int: {pitch_a.pitch_int()}")
    assert pitch_ab.pitch_int() == 68
    assert pitch_a.pitch_int() == 69


    pitch: Pitch = Pitch()

    print(f"Pitch: {pitch % int()}")
    assert pitch % int() == 60

    for degree in range(1, 8):
        print(f"------------ {degree} ------------")
        pitch << float(degree)
        for pitch_int in range(128):
            pitch << pitch_int
            pitch % int() >> Print()
            assert pitch == pitch_int

    for sharps in range(1, 8): # 8 is excluded
        print(f"------------ {sharps} ------------")
        settings << KeySignature(sharps)
        for pitch_int in range(128):
            pitch << pitch_int
            pitch % int() >> Print()
            assert pitch == pitch_int

    for flats in range(-1, -8, -1): # 8 is excluded
        print(f"------------ {flats} ------------")
        settings << KeySignature(flats)
        for pitch_int in range(128):
            pitch << pitch_int
            pitch % int() >> Print()
            assert pitch == pitch_int

    settings << KeySignature()

# test_set_chromatic_pitch()


def test_pitch_add():

    settings << KeySignature()

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
    assert pitch_integer % float() == 1
    assert pitch_integer % Octave() == 4

    pitch_integer << 8.0
    assert pitch_integer % float() == 1
    assert pitch_integer % Octave() == 4

    pitch_integer += 7.0
    assert pitch_integer % float() == 1
    assert pitch_integer % Octave() == 5


    # Perform the operation
    pitch_b: Pitch = Pitch()    # 60
    assert pitch_b % int() == 60
    pitch_b += Semitone(2)
    assert pitch_b % int() == 62
    pitch_b += Semitone(12)
    assert pitch_b % int() == 74

    pitch_1: Pitch = Pitch("A")
    pitch_1.getSerialization() % Data("degree") >> Print()
    (pitch_1 + 1).getSerialization() % Data("degree") >> Print()
    assert pitch_1 + 1.0    == Pitch("B")
    assert pitch_1 + 2      == Pitch("B")

    settings << KeySignature(1)
    pitch_2 = Pitch() << Degree("iii")  # Become Key B (60 + 11 = 71)
    assert pitch_2 % Octave() == 4
    key_pitch: Pitch = pitch_2 + 2.0
    print(f"Pitch: {key_pitch % int()}, Octave_0: {key_pitch._octave_0}, Octave: {key_pitch % Octave() % int()}, Tonic: {key_pitch._tonic_key}, "
            f"Degree_0: {key_pitch._degree_0}, Degree: {key_pitch % Degree() % int()}, Transposition: {key_pitch._transposition}")
    assert (pitch_2 + 2.0) % Octave() == 5
    pitch_2 % int() >> Print()
    assert pitch_2 % int() == Pitch("B") % int()
    (pitch_2 + 2.0) % int() >> Print()        # 74
    (Pitch("D") + 12) % int() >> Print()    # 74
    assert pitch_2 + 2.0 == Pitch("D") + 12 # Next octave

    settings << KeySignature()
    assert pitch_1 << Sharp() == Pitch("A") + 1
    assert pitch_1 << Natural() == Pitch("A")
    assert Pitch("Ab") == Pitch("A") - 1

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
        (pitch_3 + float(degree)) % str() >> Print()
        assert pitch_3 + float(degree) == keys[degree]


    pitch_4: Pitch = Pitch(60)    # Middle C (60)
    assert pitch_4 % str() == "C"
    assert pitch_4 % int() == 60

    # Test all semitones from 0 to 11
    chromatic_pitches: list[int] = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]


    for sharps in range(8): # 8 is excluded

        settings << KeySignature(sharps)
        pitch_4 << 60 # Middle C (60)
        print(f"------------ {sharps} ------------")
        print("--UP--")
        for key_i in range(12):
            (pitch_4 + Semitone(key_i)) % int() >> Print()
            assert (pitch_4 + Semitone(key_i)) % int() == chromatic_pitches[key_i]
        pitch_4 << 71
        print("-DOWN-")
        for key_i in range(12):
            pitch_4 % int() >> Print()
            assert pitch_4 % int() == chromatic_pitches[11 - key_i]
            pitch_4 -= 1

    for flats in range(0, -8, -1): # -8 is excluded

        settings << KeySignature(flats)
        pitch_4 << 60 # Middle C (60)
        print(f"------------ {flats} ------------")
        print("--UP--")
        for key_i in range(12):
            (pitch_4 + Semitone(key_i)) % int() >> Print()
            assert (pitch_4 + Semitone(key_i)) % int() == chromatic_pitches[key_i]
        pitch_4 << 71
        print("-DOWN-")
        for key_i in range(12):
            pitch_4 % int() >> Print()
            assert pitch_4 % int() == chromatic_pitches[11 - key_i]
            pitch_4 -= 1


    settings << KeySignature()
    pitch_4 << Pitch(60)    # Middle C (60)

    print(f"------------ DEGREES ------------")
    print("------")
    for key_i in range(12):
        (pitch_4 + Semitone(key_i)) % int() >> Print()
        assert (pitch_4 + Semitone(key_i)) % int() == chromatic_pitches[key_i]

    print("------")
    white_pitches: list[int] = [60, 62, 64, 65, 67, 69, 71]
    for degree in range(7):
        (pitch_4 + float(degree)) % int() >> Print()
        assert (pitch_4 + float(degree)) % int() == white_pitches[degree]

    print("------")
    pitch_5: Pitch = Pitch()
    (pitch_5 + 0) % str() >> Print()
    assert pitch_5 + 0 == Key("C")
    (pitch_5 + 1) % str() >> Print()
    assert pitch_5 + 1 == Key("C#")
    pitch_5 << Degree(2)
    (pitch_5 + 0) % str() >> Print()
    assert pitch_5 + 0 == Key("D")
    (pitch_5 + 1) % str() >> Print()
    assert pitch_5 + 1 == Key("D#")

    settings << KeySignature()

# test_pitch_add()


def test_drum_kit():

    settings << KeySignature()

    pitch: Pitch = Pitch()

    print(pitch % int())
    assert pitch % int() == 60  # White Key
    pitch << 35
    print(pitch % int())
    assert pitch % int() == 35  # White Key
    pitch << 42
    print(pitch % int())
    assert pitch % int() == 42  # Black Key
    pitch << 39
    print(pitch % int())
    assert pitch % int() == 39  # Black Key

    pitch << DrumKit("Drum")
    print(pitch % int())
    assert pitch % int() == 35  # White Key
    pitch << DrumKit("Hi-Hat")
    print(pitch % int())
    assert pitch % int() == 42  # Black Key
    pitch << DrumKit("Clap")
    print(pitch % int())
    assert pitch % int() == 39  # Black Key

    # A different KeySignature
    pitch << KeySignature(-1)
    pitch << DrumKit("Hi-Hat")
    print(pitch % int())
    assert pitch % int() == 42  # Black Key
    pitch << DrumKit("Drum")
    print(pitch % int())
    assert pitch % int() == 35  # White Key
    assert pitch == 35  # White Key

# test_drum_kit()


def test_staff_output():

    settings << KeySignature()
    
    settings << TimeSignature(3, 4)
    steps_per_measure = settings % StepsPerMeasure()
    steps_per_measure % Fraction() >> Print()
    assert steps_per_measure == 12.0

    settings << TimeSignature(4, 4)
    steps_per_measure = settings % StepsPerMeasure()
    steps_per_measure % Fraction() >> Print()
    assert steps_per_measure == 16.0

    settings << StepsPerMeasure(12)
    steps_per_measure = settings % StepsPerMeasure()
    steps_per_measure % Fraction() >> Print()
    assert steps_per_measure == 12.0

    # Quantization is in Beats ratio
    settings << Quantization(1/4)  # Resets settings quantization

# test_staff_output()


def test_scale_transposition():
    pitch_f_major: Pitch = Pitch("F", Scale("Major"))

    assert pitch_f_major % str() == "F"
    assert pitch_f_major % Scale() % str() == "Major"

    # TO BE REPLACED BY + TONE()
    transposed_keys: list[TargetKey] = list_wrap(["F", "G", "A", "A#", "C", "D", "E"], TargetKey())
    for transposition in range(7):
        print(f"T{transposition} : {(pitch_f_major + Transposition(transposition)) % TargetKey() % str()}")
        assert pitch_f_major + Transposition(transposition) == transposed_keys[transposition]

# test_scale_transposition()


def test_pitch_modulation():
    pitch_d_major: Pitch = Pitch(TonicKey(D))
    scale_degrees: list[str] = []
    for degree_0 in range(7):
        scale_degrees.append(
            (pitch_d_major + Degree(degree_0)) % str()
        )
    print(f"Scale of Degrees: {scale_degrees}")

    scale_modulated: list[str] = []
    for tones in range(7):
        scale_modulated.append(
            (pitch_d_major + Tones(tones)) % TargetKey() % str()
        )
    print(f"Scale Modulated: {scale_modulated}")

    assert scale_degrees == scale_modulated

# test_pitch_modulation()


def test_octave_matching():
    pitch_0: Pitch = Pitch(0)

    assert pitch_0 == 0

    for pitch_int in range(128):
        pitch_0 << pitch_int
        assert pitch_0 == pitch_int
        octave_0: int = pitch_0._octave_0
        assert octave_0 == pitch_int // 12

    pitch_0 << 0
    print(f"Tonic: {pitch_0 % TonicKey() % int()}, Degree: {pitch_0 % Degree() % int()}")
    assert pitch_0 == Degree(1)

    total_degrees: int = 128 * 7 // 12
    for tonic_key in range(12):
        pitch_0 << Degree(1) << TonicKey(tonic_key)
        print(f"Tonic: {tonic_key}")
        assert pitch_0 % TonicKey() == tonic_key
        for degree_0 in range(total_degrees):
            pitch_0 += Degree(1)
            print(f"\tDegree_0: {(degree_0 + 1) % 7}, Degree: {pitch_0 % Degree() % int()}", end = "")
            assert pitch_0 == Degree((degree_0 + 1) % 7 + 1)
            octave_0: int = pitch_0._octave_0
            pitch_int: int = pitch_0.pitch_int()
            print(f" | Octave_0: {octave_0}, Octave: {pitch_0 % Octave() % int()}")
            assert octave_0 == pitch_int // 12

    # Testing for the D minor Key Signature
    minor_d_pitch = Pitch()
    assert minor_d_pitch % TonicKey() == "C"

    minor_d_pitch << KeySignature(Minor(), "b")
    assert minor_d_pitch % TonicKey() == "C"
    minor_d_pitch << None   # Resets the Tonic to D
    assert minor_d_pitch % TonicKey() == "D"
    assert minor_d_pitch % RootKey() == "D"
    assert minor_d_pitch % Octave() == 4
    minor_d_pitch << Degree("VII")
    assert minor_d_pitch % TonicKey() == "D"
    assert minor_d_pitch % RootKey() == "C"
    # Makes sure changing the Degree doesn't change the Octave
    print(f"Octave: {minor_d_pitch % Octave() % int()}")
    assert minor_d_pitch % Octave() == 4

# test_octave_matching()


def test_degree_float():

    pitch_degree: Pitch = Pitch()
    assert pitch_degree % int() == 60

    pitch_degree << 5.0
    assert pitch_degree % int() == 60 + 7

    pitch_degree << 5.1
    assert pitch_degree % int() == 60 + 7 + 1

    pitch_degree << 5.2
    assert pitch_degree % int() == 60 + 7 - 1

# test_degree_float()


def test_time_signature():
    default_ts = TimeSignature()
    assert default_ts.copy() == default_ts

    default_ts << BeatsPerMeasure(3)
    assert default_ts.copy() == default_ts


def test_key_degrees():

    pitch_key = Pitch(KeySignature("bbb"), None)
    print(f"pitch_key % Key(): {pitch_key % Key() % str()}")
    print(f"pitch_key % Degree(): {pitch_key % Degree() % str()}")
    assert pitch_key % Key() == "Eb"

    pitch_key << Key("Bb")
    print(f"pitch_key % Key(): {pitch_key % Key() % str()}")
    print(f"pitch_key % Degree(): {pitch_key % Degree() % str()}")
    assert pitch_key % Degree() == "V"

    pitch_key << Key("F")
    print(f"pitch_key % Key(): {pitch_key % Key() % str()}")
    print(f"pitch_key % Degree(): {pitch_key % Degree() % str()}")
    assert pitch_key % Degree() == "ii"

# test_key_degrees()
