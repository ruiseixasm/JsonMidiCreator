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


def test_element_mod():

    element = Element()

    # Redirect stdout to capture the print output
    captured_output = StringIO()
    sys.stdout = captured_output

    # Restore stdout
    sys.stdout = sys.__stdout__

    assert element % Enable()
    assert not element % Disable()
    element << Disable()
    assert not element % Enable()
    assert element % Disable()
    element << Enable()
    assert element % Enable()
    assert not element % Disable()


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


def test_clock_div_floor():

    clock: Clock = Clock(Length(8))
    assert clock // Duration() == 8

# test_clock_div_floor()


def test_note_mod():

    # Perform the operation
    note = Note("F")
    assert note % Key() % str() == "F"

    defaults << Tempo(110)

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
    defaults << Tempo(120)

    note.clear()

    assert note % Measure() == 0
    assert note == Measure(0)
    note += Measures(1)
    assert note % Measure() == 1
    assert note == Measure(1)

# test_note_mod()


def test_note_lshift():
    
    note: Note = Note()

    assert note % Position() == 0.0
    note += Measures(1)
    assert note % Position() == 1.0
    note += Beats(2)
    assert note % Position() == 1.5
    assert note % Beat() == 2
    note << Beat(0)
    print(note % Position() % float())
    assert note % Position() == 1.0
    assert note % Beat() == 0

    note << Measure(0)
    print(note % Position() % float())
    assert note % Position() == 0.0
    assert note % Beat() == 0

# test_note_lshift()


def test_note_length():

    note: Note = Note()
    assert note % Length() == 0.25  # Measures

    rest: Rest = Rest()
    assert rest % Length() == 0.25  # Measures

# test_note_length()


def test_note_mul():

    single_note: Note = Note()
    assert single_note * 2 % Length() == Beats(2)   # Results in a Clip of 2 Notes
    assert type(single_note * 2) == Clip
    assert single_note * 2.0 % Length() == Beats(2) # Multiplies the Duration instead, still a single Note, NOT a Clip!
    assert type(single_note * 2.0) == Note
    assert single_note * Beat(6) % Length() == Beats(6)
    assert single_note * Beats(6) % Length() == Beats(6)

    many_notes = Note() * Loop(4, 3, 2, 1)
    assert type(many_notes) == Clip
    assert many_notes.len() == 4

    rest = Rest()
    clip = Rest() * 1

    assert clip[0] == Position(0)
    rest_clip = rest * clip
    assert rest_clip.len() == 2
    rest_clip[0] % Position() % float() >> Print()
    assert rest_clip[0] == Position(0)
    rest_clip[1] % Position() % float() >> Print()
    assert rest_clip[1] == Position(0.25)

    rest_note_clip = (Note() + Rest()) * 3

    assert rest_note_clip.len() == 2*3
    assert type(rest_note_clip[0]) == type(Note())
    assert type(rest_note_clip[1]) == type(Rest())

    mul_clip = rest * rest_note_clip

    assert mul_clip.len() == 1 + 2*3
    assert type(mul_clip[0]) == type(Rest())
    assert type(mul_clip[1]) == type(Note())
    assert type(mul_clip[2]) == type(Rest())

# test_note_mul()


def test_note_shift():

    note: Note = Note("A")
    assert note % Position() == 0.0 # Measures
    note += Beats(2)
    print(f"Position: {note % Position() % float()}")
    assert note % Position() == 0.5 # Measures (4 Beats per Measure)

    second_note: Note = Note("G")
    assert second_note % Position() == 0.0 # Measures
    two_notes: Clip = note + second_note   # Must be a Clip!
    assert two_notes.len() == 2
    print(f"Position: {two_notes[0] % Position() % float()}")
    assert two_notes[0] % Position() == 0.0 # Measures
    assert two_notes[0] == second_note
    print(f"Position: {two_notes[1] % Position() % float()}")
    assert two_notes[1] % Position() == 0.5 # Measures
    assert two_notes[1] == note

# test_note_shift()


def test_note_scale():

    defaults << KeySignature() << Scale([])

    defaults << Scale("Major")
    major_note: Note = Note()

    assert major_note % Pitch() % Key() == "C"
    major_note << Degree(2)
    assert major_note % Pitch() % Key() == "D"
    major_note += Degree(1)
    assert major_note % Pitch() % Key() == "E"
    major_note += 1 # integers are considered degree by Note
    assert major_note % Pitch() % Key() == "F"

    defaults << Scale("minor")
    minor_note: Note = Note()

    assert minor_note % Pitch() % Key() == "A"
    minor_note << Degree(2)
    assert minor_note % Pitch() % Key() == "B"
    minor_note += Degree(1)
    assert minor_note % Pitch() % Key() == "C"
    minor_note += 1 # integers are considered degree by Note
    assert minor_note % Pitch() % Key() == "D"

    defaults << Scale([])

# test_note_scale()


def test_keyscale_mod():

    # Perform the operation
    key_scale = KeyScale("Major")
    key_scale_string = key_scale % Scale() % str()

    assert key_scale_string == "Major"

    key_scale << Scale("minor")
    key_scale_string = key_scale % Scale() % str()

    assert key_scale_string == "minor"

    key_scale_list = key_scale % Src(list())

    assert key_scale_list == [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]


def test_chord_mod():

    defaults << KeySignature() << Scale([])

    # Perform the operation
    chord = Chord("A") << Scale("minor") << Size("7th") << Duration(1/2)
    chord_string = chord % Degree() % str()

    assert chord_string == "I"

    triad_c_major: Chord = Chord()  # C Major scale
    three_notes: list[Note] = triad_c_major.get_component_elements()
    assert three_notes[0] == "C"
    assert three_notes[1] == "E"
    assert three_notes[2] == "G"

    defaults << KeySignature(1, Minor())    # E minor scale
    triad_e_minor: Chord = Chord("minor")
    defaults << KeySignature()

    three_notes = triad_e_minor.get_component_elements()
    print(f"Key: {three_notes[0] % str()}")
    assert three_notes[0] == "E"
    print(f"Key: {three_notes[1] % str()}")
    assert three_notes[1] == "G"
    print(f"Key: {three_notes[2] % str()}")
    assert three_notes[2] == "B"

    print("------")
    defaults << KeySignature(1, Minor())    # E minor scale
    triad_e_minor: Chord = Chord()

    three_notes = triad_e_minor.get_component_elements()
    print(f"Key: {three_notes[0] % str()}")
    assert three_notes[0] == "E"
    print(f"Key: {three_notes[1] % str()}")
    assert three_notes[1] == "G"
    print(f"Key: {three_notes[2] % str()}")
    assert three_notes[2] == "B"


    defaults << KeySignature(+1, Minor())  # Sets the default Key Signature configuration as E minor
    triad: Chord = Chord()
    defaults << KeySignature() # Resets the default Key Scale to C Major

    print("------")
    three_notes = triad.get_component_elements()
    print(f"Key: {three_notes[0] % str()}")
    assert three_notes[0] == "E"
    print(f"Key: {three_notes[1] % str()}")
    assert three_notes[1] == "G#"   # Because defaults is now using the C Major scale
    print(f"Key: {three_notes[2] % str()}")
    assert three_notes[2] == "B"

# test_chord_mod()


def test_retrigger_mod():

    # Perform the operation
    retrigger = Retrigger("G") << Divisions(32)
    retrigger_int = retrigger % Divisions() % int()

    assert retrigger_int == 32


def test_modulation_mod():

    # Perform the operation
    controller = Controller("Modulation")
    controller_int = controller % Number() % int()

    assert controller_int == 1


def test_pitchbend_mod():

    # Perform the operation
    pitch_bend = PitchBend(int(8190 / 2 + 1))
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
    note = Note(duration_steps)
    note_playlist = note.getPlaylist()
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    note_start = note_playlist[0]
    note_stop = note_playlist[1]
    assert note_start["time_ms"] == 0.0
    assert note_stop["time_ms"] == 1750.0

    note_copy = note.copy()
    note_playlist = note_copy.getPlaylist()
    # 3.5 beats / 120 bpm * 60 * 1000 = 1750.0 ms
    note_start = note_playlist[0]
    note_stop = note_playlist[1]
    assert note_start["time_ms"] == 0.0
    assert note_stop["time_ms"] == 1750.0

    note_default = Note()
    note_playlist = note_default.getPlaylist()
    # 1.0 beat / 120 bpm * 60 * 1000 = 500.0 ms
    note_start = note_playlist[0]
    note_stop = note_playlist[1]
    assert note_start["time_ms"] == 0.0
    assert note_stop["time_ms"] == 500.0


def test_clock_element():

    clock_measure = Clock(Length(1), ClockStopModes("Stop"))
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

    defaults << Tempo(90)
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

    defaults << Tempo(120)

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
    assert note % Position() == 1.0
    assert note % Length() == 1.0 + 1/4

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
        (note + degree) % str() >> Print()
        assert note + degree == keys[degree]

    print("------")
    note << 0 << 1 # Tonic key again and resets the degree to 1
    note << Octave(4)    # Makes sure it's C4 again
    note_copy_2 = note.copy()
    note_copy_2 += 2
    print(f"Key: {(note_copy_2) % str()}, \
            tone: {(note_copy_2) % Pitch() % float()}, degree: {(note_copy_2) % Degree() % int()}")
    assert note + 2 == Note("E")    # C - D - E

    
    note.clear()    # Becomes like a new note

    print(note // Pitch() % float())
    assert note // Pitch() % float() == 60.0  # White Key
    note << Pitch(35.0)
    print(note // Pitch() % float())
    assert note // Pitch() % float() == 35.0  # White Key
    note << Pitch(42.0)
    print(note // Pitch() % float())
    assert note // Pitch() % float() == 42.0  # Black Key
    note << Pitch(39.0)
    print(note // Pitch() % float())
    assert note // Pitch() % float() == 39.0  # Black Key

    note << DrumKit("Drum")
    print(note // Pitch() % float())
    assert note // Pitch() % float() == 35.0  # White Key
    note << DrumKit("Hi-Hat")
    print(note // Pitch() % float())
    assert note // Pitch() % float() == 42.0  # Black Key
    note << DrumKit("Clap")
    print(note // Pitch() % float())
    assert note // Pitch() % float() == 39.0  # Black Key

    note << Pitch()
    assert note % Pitch() == 60.0   # Middle C

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
    triad_notes: list[Note] = triad.get_component_elements()
    #                                +4   +3
    expected_keys: list[str] = ["C", "E", "G"]
    for key in range(3):
        triad_notes[key] % str() >> Print()
        assert triad_notes[key] % str() == expected_keys[key]

    # WITH DEGREE
    print("------")
    triad << Degree("ii") << Scale([])  # Uses the Staff signature (Major Scale)
    assert Note(triad) % str() == "D"
    triad_notes = triad.get_component_elements()
    #                      +3   +4
    expected_keys = ["D", "F", "A"]
    for key in range(3):
        triad_notes[key] % str() >> Print()
        assert triad_notes[key] % str() == expected_keys[key]

    # WITH ROOT NOTE
    print("------")
    triad << Degree("I") << "D" << Scale("Major")
    assert Note(triad) % str() == "D"
    triad_notes = triad.get_component_elements()
    #                      +4   +3
    expected_keys = ["D", "F#", "A"]
    for key in range(3):
        triad_notes[key] % str() >> Print()
        assert triad_notes[key] % str() == expected_keys[key]

# test_chord_element()


