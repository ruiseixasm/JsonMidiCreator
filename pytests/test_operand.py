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
    source_pitch: Pitch = note // Pitch()

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

    basic_parameters: tuple = (3, "minor", "##", [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1])
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
                print(f"Culprit: {single_class.__name__}")
                assert class_object == class_object.copy()
            if isinstance(class_object, (Clip, Song)):
                if not class_object.test_staff_reference():
                    print(f"Culprit: {single_class.__name__}")
                    assert class_object.test_staff_reference()

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
                print(f"Culprit: {single_class.__name__}")
                assert class_object == class_object.copy()
            if isinstance(class_object, (Clip, Song)):
                if not class_object.test_staff_reference():
                    print(f"Culprit: {single_class.__name__}")
                    assert class_object.test_staff_reference()

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
                print(f"Culprit: {single_class.__name__}")
                assert class_object == class_object.copy()
            if isinstance(class_object, (Clip, Song)):
                if not class_object.test_staff_reference():
                    print(f"Culprit: {single_class.__name__}")
                    assert class_object.test_staff_reference()

# test_operand_copy()


# Do 'pytest --markers' to see markers
# Exclude the heavy testing with:
#     pytest -m "not heavy"
# Execute only the heavy testing with:
#     pytest -m heavy

@pytest.mark.heavy
def test_operand_serialization():

    basic_parameters: tuple = (3, "minor", "##", [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1])
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
                print(f"Culprit i: {single_class.__name__}")
                assert len(serialization) > 0
            if loaded_instantiation != class_object:
                print(f"Culprit i: {single_class.__name__}")
                assert loaded_instantiation == class_object
            if isinstance(loaded_instantiation, (Clip, Song)):
                if not loaded_instantiation.test_staff_reference():
                    print(f"Culprit i: {single_class.__name__}")
                    assert loaded_instantiation.test_staff_reference()

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
                print(f"Culprit i: {single_class.__name__}")
                assert len(serialization) > 0
            if loaded_instantiation != class_object:
                print(f"Culprit i: {single_class.__name__}")
                assert loaded_instantiation == class_object
            if isinstance(loaded_instantiation, (Clip, Song)):
                if not loaded_instantiation.test_staff_reference():
                    print(f"Culprit i: {single_class.__name__}")
                    assert loaded_instantiation.test_staff_reference()

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
                print(f"Culprit i: {single_class.__name__}")
                assert len(serialization) > 0
            if loaded_instantiation != class_object:
                print(f"Culprit i: {single_class.__name__}")
                assert loaded_instantiation == class_object
            if isinstance(loaded_instantiation, (Clip, Song)):
                if not loaded_instantiation.test_staff_reference():
                    print(f"Culprit i: {single_class.__name__}")
                    assert loaded_instantiation.test_staff_reference()

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

