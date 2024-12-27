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
# import pytest
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

def test_operand_copy():

    basic_parameters: tuple = (3, "minor", "##", [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1])
    list_all_classes: list[Type[Operand]] = list_all_operand_classes(Operand)

    for single_class in list_all_classes:
        class_object: Operand = single_class() << basic_parameters
        assert class_object == class_object.copy()

    exclude_class_names: str = ""
    for single_class in list_all_classes:
        class_object: Operand = single_class()
        if not isinstance(class_object, (
            Serialization, Playlist, Song, Sequence, Container, Panic, ProgramChange,
            PolyAftertouch, Aftertouch, PitchBend, ControlChange, Automation, Triplet,
            Tuplet, Note3, Retrigger, Chord, KeyScale, Dyad, Cluster, Note, Rest, Clock,
            Loop, Element, Staff, Scale, Controller, Pitch, TimeSignature, Generic, SinX,
            Bouncer, Flipper, Modulus, Chaos, Number, Value, Program, Bend, Pressure
            )):
            list_unit_classes: list[Type[Unit]] = list_all_operand_classes(Unit)
            for single_unit_class in list_unit_classes:
                unit_class_object: Unit = single_unit_class() << basic_parameters
                class_object << unit_class_object
            print(single_class.__name__)
            if not class_object == class_object.copy():
                exclude_class_names += single_class.__name__ + ", "
            assert class_object == class_object.copy()
    print(exclude_class_names)

# test_operand_copy()


def test_operand_serialization():

    basic_parameters: tuple = (3, "minor", "##", [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1])
    list_all_classes: list[Type[Operand]] = list_all_operand_classes(Operand)

    for single_class in list_all_classes:
        class_object = single_class()
        if not isinstance(class_object, (Serialization, Playlist)):
            # print(single_class.__name__)
            class_object << basic_parameters
            serialization: dict = class_object.getSerialization()
            loaded_instantiation: Operand = single_class()
            loaded_instantiation.loadSerialization(serialization)
            assert len(serialization) > 0
            assert loaded_instantiation == class_object

