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

def test_data_mod():

    # Perform the operation
    data = Data(Bend(8191))
    data_dict = data % dict()

    assert o.found_dict_in_dict({'unit': 8191}, data_dict)

    data = Data(Key())
    data_dict = data % {"parameters": "degree"}
    assert data_dict["parameters"] == {"unit": 1}

test_data_mod()


def test_data_source_mod():

    # Perform the operation
    single_note = Note()
    position_source = single_note % DataSource( Position() )

    assert position_source == ot.Position()

    position_copy = single_note % Position()

    assert position_copy == position_source

    assert id(position_copy) != id(position_source)


def test_serialization_mod():

    # Perform the operation
    serialization = Serialization() << Retrigger("D")
    serialization_total_duration = serialization % DataSource( Duration() )

    # Retrigger by default it's a Triplet with a real duration of 2* the default duration of 1/4 
    assert serialization_total_duration == ot.Duration(1/4 * 2)
    
    # A division of 6 means 6 notes in place of 2 (2 divisions/durations)
    retrigger = Retrigger("D") << Division(6)
    serialization = Serialization() << retrigger

    # Regardless, the net duration is always twice the default, meaning, 1/4 * 2
    assert serialization == retrigger

    serialization_total_duration = serialization % DataSource( Duration() )

    # Regardless, the net duration is always twice the default, meaning, 1/4 * 2
    assert serialization_total_duration == ot.Duration(1/4 * 2)

    serialization_single_note_duration = serialization % Duration()

    # Instead of 2 notes we have 6, BUT the SYMBOLIC value is the same, 1/4
    assert serialization_single_note_duration == ot.Duration(1/4)


def test_playlist_mod():

    # Perform the operation
    retrigger = Retrigger("D") << Division(6)
    play_list = Playlist() << retrigger
    
    # Depends on the order, different order results in False!
    assert play_list == retrigger
    
