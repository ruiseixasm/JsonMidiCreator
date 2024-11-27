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

    assert o.found_dict_in_dict(
        {'next_operand': None, 'initiated': False, 'set': False, 'index': 0, 'unit': 8191},
        data_dict
    )

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
    serialization_duration = serialization % DataSource( Duration() )

    assert serialization_duration == ot.Duration(1/4)
    
test_serialization_mod()


