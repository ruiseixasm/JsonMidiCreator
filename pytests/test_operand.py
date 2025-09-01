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
from typing import Type


def test_tail_recur():

    note_velocity = Note(3)
    note_degree = Note(Degree(3))
    assert note_degree != note_velocity

    note_degree_int = Note()**Degree(3)
    assert note_degree_int != note_velocity
    assert note_degree_int == note_degree

# test_tail_recur()


def test_operand_mod():

    # Perform the operation
    generated_note = find_class_by_name(Operand, "Note")()
    instantiated_note = Note()
    assert generated_note == instantiated_note

    unknown_class = find_class_by_name(Operand, "Unknown")
    assert not unknown_class

    assert instantiated_note.copy() == instantiated_note


def test_classes_getters():

    list_all_classes: list[Type[Operand]] = list_all_operand_classes(Operand)
    assert len(list_all_classes) > 0

    root_classes_list: list[Type[Operand]] = get_root_classes_list(Operand)
    assert len(root_classes_list) > 0

    assert root_classes_list == list_all_classes


def test_floordiv_sequence():

    note: Note = Note()
    source_pitch: Pitch = note % od.Pipe( Pitch() )

    assert id(source_pitch) == id(note._pitch)
        
# test_floordiv_sequence()



# The -m flag in pytest is used to select tests to run based on markers (m).
# It allows you to filter tests by their custom markers, enabling you to
# run only a subset of your test suite.

# Do 'pytest --markers' to see markers
# Exclude the heavy testing with:
#     pytest -m "not heavy"
# Execute only the heavy testing with:
#     pytest -m heavy

@pytest.mark.heavy
def test_operand_copy():

    basic_parameters: tuple = (None, 6, "minor", "##", [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1], True, 6.2)
    list_all_classes: list[Type[Operand]] = list_all_operand_classes(Operand)

    print("1st Cycle - Simple data")
    for single_class in list_all_classes:
        class_object: Operand = single_class()
        if isinstance(class_object, Clip):
            class_object << Note() << Rest()
        if isinstance(class_object, Song):
            class_object << Part(Clip(Note(),Rest()), Clip(Note(),Rest()))
        if class_object and not isinstance(class_object, (int)):
            class_object << basic_parameters
            if class_object != class_object.copy():
                print(f"Culprit Copy i: {single_class.__name__}")
                assert class_object == class_object.copy()
            if isinstance(class_object, Clip):
                if not class_object._test_owner_clip():
                    print(f"Culprit Copy Owner i: {single_class.__name__}")
                    assert class_object._test_owner_clip()
            if isinstance(class_object, Song):
                if not class_object._test_owner_song():
                    print(f"Culprit Copy Owner i: {single_class.__name__}")
                    assert class_object._test_owner_song()

    print("2nd Cycle - Unit objects data")
    for single_class in list_all_classes:
        class_object: Operand = single_class()
        if isinstance(class_object, Clip):
            class_object << Note() << Rest()
        if isinstance(class_object, Song):
            class_object << Part(Clip(Note(),Rest()), Clip(Note(),Rest()))
        if class_object and not isinstance(class_object, (int)):
            list_unit_classes: list[Type[Unit]] = list_all_operand_classes(Unit)
            for single_unit_class in list_unit_classes:
                unit_class_object: Unit = single_unit_class() << basic_parameters
                class_object << unit_class_object
            if class_object != class_object.copy():
                print(f"Culprit Copy ii: {single_class.__name__}")
                assert class_object == class_object.copy()
            if isinstance(class_object, Clip):
                if not class_object._test_owner_clip():
                    print(f"Culprit Copy Owner ii: {single_class.__name__}")
                    assert class_object._test_owner_clip()
            if isinstance(class_object, Song):
                if not class_object._test_owner_song():
                    print(f"Culprit Copy Owner ii: {single_class.__name__}")
                    assert class_object._test_owner_song()

    print("3rd Cycle - Rational objects data")
    for single_class in list_all_classes:
        class_object: Operand = single_class()
        if isinstance(class_object, Clip):
            class_object << Note() << Rest()
        if isinstance(class_object, Song):
            class_object << Part(Clip(Note(),Rest()), Clip(Note(),Rest()))
        if class_object and not isinstance(class_object, (int)):
            list_unit_classes: list[Type[Rational]] = list_all_operand_classes(Rational)
            for single_rational_class in list_unit_classes:
                rational_class_object: Rational = single_rational_class() << basic_parameters
                class_object << rational_class_object
            if class_object != class_object.copy():
                print(f"Culprit Copy iii: {single_class.__name__}")
                assert class_object == class_object.copy()
            if isinstance(class_object, Clip):
                if not class_object._test_owner_clip():
                    print(f"Culprit Copy Owner iii: {single_class.__name__}")
                    assert class_object._test_owner_clip()
            if isinstance(class_object, Song):
                if not class_object._test_owner_song():
                    print(f"Culprit Copy Owner iii: {single_class.__name__}")
                    assert class_object._test_owner_song()

    print("4th Cycle - DataSource Unit objects data")
    for single_class in list_all_classes:
        class_object: Operand = single_class()
        if isinstance(class_object, Clip):
            class_object << Note() << Rest()
        if isinstance(class_object, Song):
            class_object << Part(Clip(Note(),Rest()), Clip(Note(),Rest()))
        if class_object and not isinstance(class_object, (int)):
            list_unit_classes: list[Type[Unit]] = list_all_operand_classes(Unit)
            for single_unit_class in list_unit_classes:
                unit_class_object: Unit = single_unit_class() << basic_parameters
                class_object << Pipe( unit_class_object )     # DataSource injection
            if class_object != class_object.copy():
                print(f"Culprit Copy iv: {single_class.__name__}")
                assert class_object == class_object.copy()
            if isinstance(class_object, Clip):
                if not class_object._test_owner_clip():
                    print(f"Culprit Copy Owner iv: {single_class.__name__}")
                    assert class_object._test_owner_clip()
            if isinstance(class_object, Song):
                if not class_object._test_owner_song():
                    print(f"Culprit Copy Owner iv: {single_class.__name__}")
                    assert class_object._test_owner_song()

    print("5th Cycle - DataSource Rational objects data")
    for single_class in list_all_classes:
        class_object: Operand = single_class()
        if isinstance(class_object, Clip):
            class_object << Note() << Rest()
        if isinstance(class_object, Song):
            class_object << Part(Clip(Note(),Rest()), Clip(Note(),Rest()))
        if class_object and not isinstance(class_object, (int)):
            list_unit_classes: list[Type[Rational]] = list_all_operand_classes(Rational)
            for single_rational_class in list_unit_classes:
                rational_class_object: Rational = single_rational_class() << basic_parameters
                class_object << Pipe( rational_class_object ) # DataSource injection
            if class_object != class_object.copy():
                print(f"Culprit Copy v: {single_class.__name__}")
                assert class_object == class_object.copy()
            if isinstance(class_object, Clip):
                if not class_object._test_owner_clip():
                    print(f"Culprit Copy Owner v: {single_class.__name__}")
                    assert class_object._test_owner_clip()
            if isinstance(class_object, Song):
                if not class_object._test_owner_song():
                    print(f"Culprit Copy Owner v: {single_class.__name__}")
                    assert class_object._test_owner_song()

# test_operand_copy()


# Do 'pytest --markers' to see markers
# Exclude the heavy testing with:
#     pytest -m "not heavy"
# Execute only the heavy testing with:
#     pytest -m heavy

@pytest.mark.heavy
def test_operand_serialization():

    basic_parameters: tuple = (None, 6, "minor", "##", [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1], True, 6.3)
    list_all_classes: list[Type[Operand]] = list_all_operand_classes(Operand)

    print("1st Cycle - Simple data")
    for single_class in list_all_classes:
        class_object = single_class()
        if isinstance(class_object, Clip):
            class_object << Note() << Rest()
        if isinstance(class_object, Song):
            class_object << Part(Clip(Note(),Rest()), Clip(Note(),Rest()))
        if class_object and not isinstance(class_object, (int)):
            class_object << basic_parameters
            serialization: dict = class_object.getSerialization()
            loaded_instantiation: Operand = single_class()
            loaded_instantiation.loadSerialization(serialization)
            if not len(serialization) > 0:
                print(f"Culprit Serialization len i: {single_class.__name__}")
                assert len(serialization) > 0
            if loaded_instantiation != class_object:
                print(f"Culprit Serialization equal i: {single_class.__name__}")
                assert loaded_instantiation == class_object
            if isinstance(loaded_instantiation, Clip):
                if not loaded_instantiation._test_owner_clip():
                    print(f"Culprit Owner i: {single_class.__name__}")
                    assert loaded_instantiation._test_owner_clip()
            if isinstance(loaded_instantiation, Song):
                if not loaded_instantiation._test_owner_song():
                    print(f"Culprit Owner i: {single_class.__name__}")
                    assert loaded_instantiation._test_owner_song()

    print("2nd Cycle - Unit objects data")
    for single_class in list_all_classes:
        class_object: Operand = single_class()
        if isinstance(class_object, Clip):
            class_object << Note() << Rest()
        if isinstance(class_object, Song):
            class_object << Part(Clip(Note(),Rest()), Clip(Note(),Rest()))
        if class_object and not isinstance(class_object, (int)):
            list_unit_classes: list[Type[Unit]] = list_all_operand_classes(Unit)
            for single_unit_class in list_unit_classes:
                unit_class_object: Unit = single_unit_class() << basic_parameters
                class_object << unit_class_object
            serialization: dict = class_object.getSerialization()
            loaded_instantiation: Operand = single_class()
            loaded_instantiation.loadSerialization(serialization)
            if not len(serialization) > 0:
                print(f"Culprit Serialization len ii: {single_class.__name__}")
                assert len(serialization) > 0
            if loaded_instantiation != class_object:
                print(f"Culprit Serialization equal ii: {single_class.__name__}")
                assert loaded_instantiation == class_object
            if isinstance(loaded_instantiation, Clip):
                if not loaded_instantiation._test_owner_clip():
                    print(f"Culprit Owner ii: {single_class.__name__}")
                    assert loaded_instantiation._test_owner_clip()
            if isinstance(loaded_instantiation, Song):
                if not loaded_instantiation._test_owner_song():
                    print(f"Culprit Owner ii: {single_class.__name__}")
                    assert loaded_instantiation._test_owner_song()

    print("3rd Cycle - Rational objects data")
    for single_class in list_all_classes:
        class_object: Operand = single_class()
        if isinstance(class_object, Clip):
            class_object << Note() << Rest()
        if isinstance(class_object, Song):
            class_object << Part(Clip(Note(),Rest()), Clip(Note(),Rest()))
        if class_object and not isinstance(class_object, (int)):
            list_unit_classes: list[Type[Rational]] = list_all_operand_classes(Rational)
            for single_rational_class in list_unit_classes:
                rational_class_object: Rational = single_rational_class() << basic_parameters
                class_object << rational_class_object
            serialization: dict = class_object.getSerialization()
            loaded_instantiation: Operand = single_class()
            loaded_instantiation.loadSerialization(serialization)
            if not len(serialization) > 0:
                print(f"Culprit Serialization len iii: {single_class.__name__}")
                assert len(serialization) > 0
            if loaded_instantiation != class_object:
                print(f"Culprit Serialization equal iii: {single_class.__name__}")
                assert loaded_instantiation == class_object
            if isinstance(loaded_instantiation, Clip):
                if not loaded_instantiation._test_owner_clip():
                    print(f"Culprit Owner iii: {single_class.__name__}")
                    assert loaded_instantiation._test_owner_clip()
            if isinstance(loaded_instantiation, Song):
                if not loaded_instantiation._test_owner_song():
                    print(f"Culprit Owner iii: {single_class.__name__}")
                    assert loaded_instantiation._test_owner_song()

# test_operand_serialization()


def test_dictionary_getter():

    midi_track: MidiTrack = MidiTrack(3, "Drums")
    serialization: dict = midi_track.getSerialization()

    parameters: dict = get_dict_key_data("parameters", serialization)
    print(parameters)
    # {'unit': 3, 'name': 'Drums', 'devices': ['VMPK', 'FLUID']}    # 'devices' not the same in all OS
    assert parameters['unit'] == 3
    assert parameters['name'] == 'Drums'

    parameters = serialization % Data("parameters")
    print(parameters)
    # {'unit': 3, 'name': 'Drums', 'devices': ['VMPK', 'FLUID']}    # 'devices' not the same in all OS
    assert parameters['unit'] == 3
    assert parameters['name'] == 'Drums'

# test_dictionary_getter()


def test_handy_methods():
    list_int = [12, 3, 45]
    assert list_mod(list_int) == [0, 1, 1]

    assert list_trim(list_int, 20) == [12, 3, 5]
    list_float = [1/4, 1/8, 1/2]
    assert list_trim(list_float, 3/4) == [1/4, 1/8, 3/8]

    assert list_extend(list_int, 100) == [12, 3, 85]
    list_float = [1/4, 1/8, 1/8]
    assert list_extend(list_float, 1/1) == [1/4, 1/8, 5/8]

    assert list_rotate(list_int, 1) == [3, 45, 12]

    places = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    pattern = "1... 1... 1... 1..."
    assert string_to_list(pattern) == places
    assert list_to_string(places) == pattern

# test_handy_methods()


