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

def test_element_mod():

    element = Element()
    element_device = element % Device()

    # Redirect stdout to capture the print output
    captured_output = StringIO()
    sys.stdout = captured_output

    # Perform the operation
    element_device % list() >> Print()

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Assert the captured output
    assert captured_output.getvalue().strip() in ["['VMPK', 'FLUID']", "['loopMIDI', 'Microsoft']"]

def test_clock_mod():
    # Redirect stdout to capture the print output
    captured_output = StringIO()
    sys.stdout = captured_output

    # Perform the operation
    clock = Clock(4)
    clock % Length() % Measure() % float() >> Print()

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Assert the captured output
    assert captured_output.getvalue().strip() == "4.0"

def test_note_mod():
    # Redirect stdout to capture the print output
    captured_output = StringIO()
    sys.stdout = captured_output

    # Perform the operation
    note = Note("F")
    note % Key() % str() >> Print()

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Assert the captured output
    assert captured_output.getvalue().strip() == "F"

def test_keyscale_mod():

    # Perform the operation
    scale = KeyScale()
    scale_string = scale % str()

    assert scale_string == "Major"

    scale << "minor"
    scale_string = scale % str()

    assert scale_string == "minor"

    scale_list = scale % list()

    assert scale_list == [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]

test_keyscale_mod()
