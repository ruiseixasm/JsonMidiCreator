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
    clock = Clock(4.0)  # 4 for Position and 4.0 for Duration
    clock % NoteValue() % Measures() % float() >> Print()

    # Restore stdout
    sys.stdout = sys.__stdout__

    # Assert the captured output
    assert captured_output.getvalue().strip() == "4.0"

# test_clock_mod()


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

    first_note = Note() << (Position() << Steps(3*4 + 2))
    first_note_playlist = first_note.getPlaylist()

    # Sets the common device as that isn't being check
    first_note_playlist[0]["midi_message"]["device"] = playlist[0]["midi_message"]["device"]
    first_note_playlist[1]["midi_message"]["device"] = playlist[0]["midi_message"]["device"]

    assert first_note_playlist[0] == playlist[0]    # Position kind of error
    assert first_note_playlist[1] == playlist[1]    # Duration kind of error
    assert first_note_playlist == playlist

    # Resets changed Tempo to the default value of 120 bpm
    staff << Tempo(120)

    note.clear()

    assert note % Measure() == 0
    assert note == Measure(0)
    note += Measures(1)
    assert note % Measure() == 1
    assert note == Measure(1)

# test_note_mod()


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
    chord = Chord("A") << Scale("minor") << Size("7th") << Duration(1/2)
    chord_string = chord % Degree() % str()

    assert chord_string == "I"

    triad_c_major: Chord = Chord(KeySignature())  # C Major scale
    three_notes: list[Note] = triad_c_major.get_chord_notes()
    assert three_notes[0] == "C"
    assert three_notes[1] == "E"
    assert three_notes[2] == "G"

    triad_e_minor: Chord = Chord(KeySignature(1, Minor()), "minor")  # E minor scale
    three_notes = triad_e_minor.get_chord_notes()
    print(f"Key: {three_notes[0] % str()}")
    assert three_notes[0] == "E"
    print(f"Key: {three_notes[1] % str()}")
    assert three_notes[1] == "G"
    print(f"Key: {three_notes[2] % str()}")
    assert three_notes[2] == "B"

    print("------")
    triad_e_minor: Chord = Chord(KeySignature(1, Minor()))  # E minor scale
    three_notes = triad_e_minor.get_chord_notes()
    print(f"Key: {three_notes[0] % str()}")
    assert three_notes[0] == "E"
    print(f"Key: {three_notes[1] % str()}")
    assert three_notes[1] == "G"
    print(f"Key: {three_notes[2] % str()}")
    assert three_notes[2] == "B"


    staff << KeySignature(+1, Minor())  # Sets the default Key Signature configuration as E minor
    triad: Chord = Chord()
    staff << KeySignature() # Resets the default Key Scale to Major C

    print("------")
    three_notes = triad.get_chord_notes()
    print(f"Key: {three_notes[0] % str()}")
    assert three_notes[0] == "E"
    print(f"Key: {three_notes[1] % str()}")
    assert three_notes[1] == "G"
    print(f"Key: {three_notes[2] % str()}")
    assert three_notes[2] == "B"



# test_chord_mod()


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

    duration_steps = NoteValue(1/16 * (3*4 + 2))
    rest = Rest(duration_steps)
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


def test_clock_element():

    clock_measure = Clock(length.getDuration(Measure(1)))
    clock_playlist: list = clock_measure.getPlaylist()
    expected_messages: int = 1 * 4 * 24 + 1 # +1 for the Stop clock message
    total_messages: int = len(clock_playlist)
    print(f"{total_messages} / {expected_messages}")
    assert total_messages == expected_messages
    # 1.0 Measure = 1.0 * 4 Beats = 1.0 * 4 / 120 * 60 * 1000
    clock_start = clock_playlist[0]
    clock_stop = clock_playlist[total_messages - 1]
    assert clock_start["time_ms"] == 0.0
    assert clock_stop["time_ms"] == round(1.0 * 4 / 120 * 60 * 1000, 3)

    staff << Tempo(90)
    clock_default = Clock()
    position_tempo: Tempo = clock_default % DataSource( Position() ) % Tempo()
    position_tempo >> Print(0)
    assert position_tempo == staff % Tempo()
    clock_specific = Clock(NoteValue(Measures(1)))
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

# test_clock_element()


def test_note3_element():

    triplet_note = Note3("C")
    assert triplet_note % NoteValue() == Duration(1/4)
    assert triplet_note % od.DataSource( NoteValue() ) == Duration(1/2)
    assert triplet_note % Position() == 0.0
    triplet_note << NoteValue(1/8)
    assert triplet_note % NoteValue() == Duration(1/8)
    assert triplet_note % od.DataSource( NoteValue() ) == Duration(1/4)
    assert triplet_note % Position() == 0.0
    triplet_note << NoteValue(1/16)
    assert triplet_note % NoteValue() == Duration(1/16)
    assert triplet_note % od.DataSource( NoteValue() ) == Duration(1/8)
    assert triplet_note % Position() == 0.0

    assert (Note3(MidiTrack(1, "Piano")) << (NoteValue() << Duration(1/16))) % NoteValue() == Duration(1/16)
    assert (Note3(MidiTrack(1, "Piano")) << (NoteValue() << Duration(1/16))) % od.DataSource( NoteValue() ) == Duration(1/8)
    assert (Note3(MidiTrack(1, "Piano")) << (NoteValue() << Duration(1/16))) % Position() == 0.0

# test_note3_element()


def test_note_position():

    note: Note = Note()
    assert note % Position() == 0.0

    note << Position(1.0)
    assert note % Position() == 1.0

    measure_length: Length = Length(1)
    note += measure_length
    assert note % Position() == 2.0

# test_note_position()


def test_note_pitch():

    note: Note = Note()
    assert note % str() == "C"
    assert (note + 0.0) % str() == "C"

    note_e: Note = Note(E)
    assert note_e % str() == "E"

    # Test all semitones from 0 to 11
    expected_keys: list[str] = ["C",  "C#", "D", "D#", "E",  "F",  "F#", "G", "G#", "A", "A#", "B"]

    for key_i in range(12):
        note % str() >> Print()
        assert note % str() == expected_keys[key_i]
        note += Semitone(1)

    print("------")
    note << 0 # Tonic key again
    keys: list = ["C", "D", "E", "F", "G", "A", "B"]
    for degree in range(7):
        note << Degree(degree + 1)
        note % str() >> Print()
        assert note == keys[degree]

    print("------")
    note << 0 << 1 # Tonic key again and resets the degree to 1
    note << Octave(4)    # Makes sure it's C4 again
    note_copy_2 = note.copy()
    note_copy_2 += 2
    print(f"Key: {(note_copy_2) % str()}, \
            tone: {(note_copy_2) % Pitch() % float()}, degree: {(note_copy_2) % Degree() % int()}")
    assert note + 2 == Note("E")    # C - D - E

    
    note.clear()    # Becomes like a new note

    print(note // Pitch() // float())
    assert note // Pitch() // float() == 60.0  # White Key
    note << Pitch(35.0)
    print(note // Pitch() // float())
    assert note // Pitch() // float() == 35.0  # White Key
    note << Pitch(42.0)
    print(note // Pitch() // float())
    assert note // Pitch() // float() == 42.0  # Black Key
    note << Pitch(39.0)
    print(note // Pitch() // float())
    assert note // Pitch() // float() == 39.0  # Black Key

    note << DrumKit("Drum")
    print(note // Pitch() // float())
    assert note // Pitch() // float() == 35.0  # White Key
    note << DrumKit("Hi-Hat")
    print(note // Pitch() // float())
    assert note // Pitch() // float() == 42.0  # Black Key
    note << DrumKit("Clap")
    print(note // Pitch() // float())
    assert note // Pitch() // float() == 39.0  # Black Key

    note.clear()

    assert note % Octave() == 4
    note -= Octave()
    assert note % Octave() == 3
    note += Octave()
    assert note % Octave() == 4


# test_note_pitch()



def test_chord_element():

    triad: Chord = Chord()
    assert Note(triad) % str() == "C"
    triad_notes: list[Note] = triad.get_chord_notes()
    #                                +4   +3
    expected_keys: list[str] = ["C", "E", "G"]
    for key in range(3):
        triad_notes[key] % str() >> Print()
        assert triad_notes[key] % str() == expected_keys[key]

    # WITH DEGREE
    print("------")
    triad << Degree("ii")
    assert Note(triad) % str() == "D"
    triad_notes = triad.get_chord_notes()
    #                      +3   +4
    expected_keys = ["D", "F", "A"]
    for key in range(3):
        triad_notes[key] % str() >> Print()
        assert triad_notes[key] % str() == expected_keys[key]

    # WITH ROOT NOTE
    print("------")
    triad << Degree("I") << "D"
    assert Note(triad) % str() == "D"
    triad_notes = triad.get_chord_notes()
    #                      +4   +3
    expected_keys = ["D", "F#", "A"]
    for key in range(3):
        triad_notes[key] % str() >> Print()
        assert triad_notes[key] % str() == expected_keys[key]

# test_chord_element()


