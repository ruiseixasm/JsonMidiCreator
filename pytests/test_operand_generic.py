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



def test_track_mod():

    # Perform the operation
    default_track = Track()
    assert default_track % str() == "Default"
    test_track_1 = Track("Test")
    test_track_2 = Track("Test")
    assert test_track_1 == test_track_2


def test_pitch_mod():

    # Perform the operation
    pitch = Pitch()
    assert pitch % float() == 60    # middle C
    assert pitch % Key() % str() == "C"
    assert (pitch + Octave()) % float() == 60 + 12
    assert (pitch + 1) % float() == 60 + 2
    assert not pitch % Sharp()
    assert (pitch + 1.0) % Sharp()
    assert (pitch + 1.0 << Natural()) % float() == 60

def test_scale_mod():

    # Perform the operation
    scale = Scale()
    assert scale % str() == "Major"
    assert scale.modulate(6) % str() == "minor" # 6th Mode
    assert scale % Mode() % str() == "1st"

