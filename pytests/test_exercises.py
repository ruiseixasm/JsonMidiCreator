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

from jsonmidicreator import *


# Run the tests with 'pytest tests\python_functions.py' on windows
# Run the tests with 'pytest tests/python_functions.py' on linux

from io import StringIO
import pytest     # pip install pytest
import sys


def test_cutting_note():

    settings << None    # Reset settings

    simple_cuts = Note(1/1) * 1
    # Main splits (Positional)
    simple_cuts //= Beat(1)
    simple_cuts //= Position(1) - Steps(1)
    # Secondary splits (Durational)
    # Shallow clip splitting
    simple_cuts[Beat(0)] //= Steps(1)
    simple_cuts[Last()] << Channel(3)
    simple_cuts *= Rest(1/1)    # Add a simple rest
    # simple_cuts[4] % Duration() >> Print()
    # simple_cuts >> Plot(title="By Pitch", block=False)
    # simple_cuts >> Plot(by_channel=True, title="By Channel")
    assert simple_cuts[4] % Duration() == Beats(3) - Steps(1)

    parameter_1 = Parameter(ControlChange("Pan"))
    parameter_3 = Parameter(ControlChange("Pan", Channel(3)))
    parameter_M = Parameter(ControlChange("Modulation"))
    parameter_P = Parameter(PitchBend())
    dots_1 = Dots() + Dot(1.0, 100)
    dots_3 = Dots() + Dot(0.0, 100) + Dot(1.0, 0)
    dots_M = Dots() + Dot(0.0, 70) + Dot(1.0, 30)
    dots_P = Dots() + Dot(0.0, 30) + Dot(2.0, 70)
    automation_1 = Automation(parameter_1, dots_1, Duration(1/32))
    automation_3 = Automation(parameter_3, dots_3, Duration(1/32))
    automation_M = Automation(parameter_M, dots_M, Duration(1/32))
    automation_P = Automation(parameter_P, dots_P, Duration(1/32))
    automation_clip = Clip() << [automation_1, automation_3, automation_M, automation_P]
    print(f"automation_clip.len(): {automation_clip.len()}")
    # automation_clip >> Plot(title="Automation of a ControlChange")

    triggers_16 = Trigger() * 16 + Rest(1/1) << DrumKit("808") << Velocity(50)
    # triggers_16 >> Plot(by_channel=True, title="Waveform Triggers")
    assert triggers_16.len() == 16 + 1

# test_cutting_note()


def test_transform_note():

    settings << None    # Reset settings

    simple_cuts = Note(1/1) * 1
    # Main splits (Positional)
    split_1 = Operate(lambda clip: clip // Beat(1))
    split_2 = Operate(lambda clip: clip // (Position(1) - Steps(1)))
    split_3 = Operate(lambda clip: clip // Equal(Beat(0))**Steps(1))
    add_rest = Operate(lambda clip: clip * Rest(1/1))
    # Chaining all the transformations
    global_transform = split_1**split_2**split_3**add_rest
    # simple_cuts >> Plot(transform=global_transform)

    simple_cuts << global_transform
    simple_cuts[4] % Duration() >> Print()
    # simple_cuts >> Plot()
    assert simple_cuts[4] % Duration() == Beats(3) - Steps(1)

# test_transform_note()


