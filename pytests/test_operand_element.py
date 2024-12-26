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
    clock % Duration() % Measures() % float() >> Print()

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Assert the captured output
    assert captured_output.getvalue().strip() == "4.0"


def test_note_mod():

    # Perform the operation
    note = Note("F")
    assert note % Key() % str() == "F"

    staff << Tempo(110)

    playlist: list = [    
        {
            "time_ms": 1909.091,
            "midi_message": {
                "status_byte": 144,
                "data_byte_1": 60,
                "data_byte_2": 100,
                "device": [
                    "loopMIDI",
                    "Microsoft"
                ]
            }
        },
        {
            "time_ms": 2454.545,
            "midi_message": {
                "status_byte": 128,
                "data_byte_1": 60,
                "data_byte_2": 0,
                "device": [
                    "loopMIDI",
                    "Microsoft"
                ]
            }
        }
    ]

    first_note = Note() << (Position() << Step(3*4 + 2))
    first_note_playlist = first_note.getPlaylist()

    # Sets the common device as that isn't being check
    first_note_playlist[0]["midi_message"]["device"] = playlist[0]["midi_message"]["device"]
    first_note_playlist[1]["midi_message"]["device"] = playlist[0]["midi_message"]["device"]

    assert first_note_playlist[0] == playlist[0]    # Position kind of error
    assert first_note_playlist[1] == playlist[1]    # Duration kind of error
    assert first_note_playlist == playlist

    # Resets changed Tempo to the default value of 120 bpm
    staff << Tempo(120)


def test_keyscale_mod():

    # Perform the operation
    key_scale = KeyScale()
    key_scale_string = key_scale % Scale() % str()

    assert key_scale_string == "Major"

    key_scale << Scale("minor")
    key_scale_string = key_scale % Scale() % str()

    assert key_scale_string == "minor"

    key_scale_list = key_scale % list()

    assert key_scale_list == [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]


def test_chord_mod():

    # Perform the operation
    chord = Chord("A") << Scale("minor") << Size("7th") << NoteValue(1/2)
    chord_string = chord % Degree() % str()

    assert chord_string == "I"


def test_retrigger_mod():

    # Perform the operation
    retrigger = Retrigger("G") << Division(32)
    retrigger_int = retrigger % Division() % int()

    assert retrigger_int == 32


def test_modulation_mod():

    # Perform the operation
    controller = Controller("Modulation")
    controller_int = controller % Number() % int()

    assert controller_int == 1


def test_pitchbend_mod():

    # Perform the operation
    pitch_bend = PitchBend(8190 / 2 + 1)
    pitch_bend_int = pitch_bend % int()

    assert pitch_bend_int == 4096


def test_aftertouch_mod():

    # Perform the operation
    aftertouch = Aftertouch(2) << Pressure(128 / 2)
    aftertouch_int = aftertouch % Pressure() % int()

    assert aftertouch_int == 64


def test_poly_aftertouch_mod():

    # Perform the operation
    poly_aftertouch = PolyAftertouch("E") << Pressure(128 / 2)
    poly_aftertouch_int = poly_aftertouch % Channel() % int()

    assert poly_aftertouch_int == 1


def test_program_change_mod():

    # Perform the operation
    program_change = ProgramChange(12)
    program_change_int = program_change % Program() % int()

    assert program_change_int == 12


def test_milliseconds_duration():

    note_value = NoteValue(Step(3*4 + 2))
    assert note_value == Beat(3.5)
    rest = Rest(note_value)
    rest_playlist = rest.getPlaylist()
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    rest_start = rest_playlist[0]
    rest_stop = rest_playlist[1]
    assert rest_start["time_ms"] == 0.0
    assert rest_stop["time_ms"] == 1750.0

    rest_copy = rest.copy()
    rest_playlist = rest_copy.getPlaylist()
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    rest_start = rest_playlist[0]
    rest_stop = rest_playlist[1]
    assert rest_start["time_ms"] == 0.0
    assert rest_stop["time_ms"] == 1750.0

    rest_default = Rest()
    rest_playlist = rest_default.getPlaylist()
    # 1.0 beat / 120 bpm * 60 * 1000 = 500.0 ms
    rest_start = rest_playlist[0]
    rest_stop = rest_playlist[1]
    assert rest_start["time_ms"] == 0.0
    assert rest_stop["time_ms"] == 500.0

    clock_measure = Clock(Duration(Measures(1)))
    clock_playlist: list = clock_measure.getPlaylist()
    total_messages = len(clock_playlist)
    # 1.0 Measure = 1.0 * 4 Beats = 1.0 * 4 / 120 * 60 * 1000
    clock_start = clock_playlist[0]
    clock_stop = clock_playlist[total_messages - 1]
    assert clock_start["time_ms"] == 0.0
    assert clock_stop["time_ms"] == round(1.0 * 4 / 120 * 60 * 1000, 3)

    staff << Tempo(90)
    clock_default = Clock()
    position_tempo: Tempo = clock_default % DataSource( Position() ) % Tempo()
    duration_tempo: Tempo = clock_default % DataSource( Duration() ) % Tempo()
    position_tempo >> Print(0)
    assert position_tempo == staff % Tempo()
    assert duration_tempo == staff % Tempo()
    clock_specific = Clock(Duration(Measures(1)))
    clock_playlist = clock_specific.getPlaylist()
    total_messages = len(clock_playlist)
    # 1.0 Measure = 1.0 * 4 Beats = 1.0 * 4 / 90 * 60 * 1000
    clock_start = clock_playlist[0]
    clock_stop = clock_playlist[total_messages - 1]
    assert clock_start["time_ms"] == 0.0
    assert clock_stop["time_ms"] == round(1.0 * 4 / 90 * 60 * 1000, 3)

    clock_clock = clock_specific.copy()
    clock_playlist = clock_clock.getPlaylist()
    total_messages = len(clock_playlist)
    # 1.0 Measure = 1.0 * 4 Beats = 1.0 * 4 / 90 * 60 * 1000
    clock_start = clock_playlist[0]
    clock_stop = clock_playlist[total_messages - 1]
    assert clock_start["time_ms"] == 0.0
    assert clock_stop["time_ms"] == round(1.0 * 4 / 90 * 60 * 1000, 3)

    staff << Tempo(120)
