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

from jsonmidicreator import *


# Run the tests with 'pytest tests\python_functions.py' on windows
# Run the tests with 'pytest tests/python_functions.py' on linux

from io import StringIO
import pytest     # pip install pytest
import sys


def test_cycle_setter():
    two_notes = Note(1/2) / 2 << Select(At(1)) << Name("Two Notes")
    notes_setting = I_ParameterSetter(two_notes, Semitone(), Cycle(), no_repetitions=True)
    for semitone in range(12):
        new_iteration: Clip = notes_setting.get_clip()
        second_note: Note = new_iteration[0]
        print(f"Semitone {semitone}: {second_note._pitch._get_chromatic_pitch()} VS {60 + semitone}")
        assert second_note._pitch._get_chromatic_pitch() == 60 + semitone
    four_notes = Clip(
        Line("n:2:C#7, :6:E7, :2:F#6, :6:F6")
    ) << Select(At(2)) << Name("Four Notes")
    notes_setting.set_seed(four_notes)
    for semitone in range(12):
        new_iteration: Clip = notes_setting.get_clip()
        second_note: Note = new_iteration[0]
        print(f"Semitone {semitone}: {second_note._pitch._get_chromatic_pitch()} VS {60 + 2*12 + semitone}")
        assert second_note._pitch._get_chromatic_pitch() == 60 + 2*12 + semitone

# test_cycle_setter()

