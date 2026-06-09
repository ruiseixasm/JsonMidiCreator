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



def test_sinx_mod():

    # Perform the operation
    sin_x = SinX()

    # sin_x remains unchangeable
    sin_x_1000  = sin_x * 1000   # Implicit copy
    sin_x_1     = sin_x * 1      # Implicit copy

    assert sin_x_1000 != sin_x_1
    assert sin_x_1000 == sin_x_1 * 999
    sin_x_1.reset()
    assert sin_x_1 == sin_x
    sin_x *= 1000   # This changes the original sin_x
    assert sin_x_1000 == sin_x
    assert sin_x_1000 * 1 == sin_x_1 * 1000 * 1

# test_sinx_mod()


def test_modulus():

    cycle = Cycle(Modulus(4))

    assert cycle % int() == 0
    assert cycle % int() == 1
    assert cycle % int() == 2
    assert cycle % int() == 3
    assert cycle % int() == 0
    assert cycle % int() == 1
    assert cycle % int() == 2
    assert cycle % int() == 3
    assert cycle % int() == 0

# test_modulus()


def test_chaos_discretion():
    chaos = SinX(340)
    total_values = 4*16
    values = set()
    assert len(values) == 0
    for _ in range(300):
        new_value = 1 >> chaos
        new_value %= total_values
        values.add(new_value)
    assert len(values) == total_values


def test_chained_chaos():
    # CHAINING CHAOS RESULTS IN SINGLE ITERATIONS FORM TAIL TO HEAD
    # WHERE THE XN VALUE OF EACH PREVIOUS CHAOS OPERAND IS SET BY THE
    # TAILED CHAOS OPERAND

    modulus_sinx = Cycle()**SinX()
    tailed_sinx = SinX()
    assert modulus_sinx._next_operand == tailed_sinx

    print(f"modulus_sinx: {modulus_sinx % Pipe(float())}")
    modulus_sinx *= 2.01    # same as Cycle(SinX() * 2) * 2
    chained_cycle = Cycle(SinX() * 2) * 2
    print(f"modulus_sinx: {modulus_sinx % Pipe(float())}")
    print(f"chained_cycle: {chained_cycle % Pipe(float())}")
    assert chained_cycle == modulus_sinx
    assert modulus_sinx % Pipe(int()) < 12  # Pipe avoids iterations

    modulus = Cycle()   # Xn starts as 0
    assert modulus != modulus_sinx

    sinx = SinX()       # Xn starts as 2
    print(f"sinx: {sinx % Pipe(float())}")
    sinx *= 2.01    # same as 2
    print(f"sinx: {sinx % Pipe(float())}")
    # The purpose of chaining Chaos vvvvvv
    modulus << sinx # sets the xn as sinx result from above
    modulus *= 2.01 # same as 2
    modulus % Pipe(float()) >> Print()
    modulus_sinx % Pipe(float()) >> Print()
    assert modulus == modulus_sinx

# test_chained_chaos()


def test_list_chaos():
    note_values: list[float] = [1/2, 1/4, 1/8, 1/16]
    four_indexes_1: list[int] = []
    sin_x_1 = SinX()
    sin_x_2 = SinX()
    assert sin_x_2 == sin_x_1

    for _ in range(4):
        four_indexes_1.append(sin_x_1 % 1)
    assert sin_x_2 != sin_x_1

    four_indexes_2: list[int] = sin_x_2 % [1, 1, 1, 1]
    assert sin_x_2 == sin_x_1
    assert four_indexes_2 == four_indexes_1

    note_values_1 = list_choose(note_values, four_indexes_1)
    note_values_2 = list_choose(note_values, four_indexes_2)
    assert note_values_2 == note_values_1

# test_list_chaos()


def test_reset():
    chaos = Cycle(Modulus(120))**SinX(24)
    chaos_copy = chaos.copy()
    assert chaos_copy == chaos
    chaos_copy *= 10
    assert chaos_copy != chaos
    chaos_copy.reset()
    assert chaos_copy == chaos

# test_reset()


def test_get_list():
    chaos = Cycle(Modulus(120))**SinX(24)
    measures_int: list[int] = [1] * 4
    results_int: list[int] = chaos % measures_int
    results_a = list_wrap(results_int, Velocity())
    measures_velocity = [Velocity(1)] * 4
    results_b = chaos.reset() % measures_velocity
    print(f"measures_int: {measures_int}")
    print(f"results_int: {results_int}")
    print(f"measures_velocity: {list_mod(measures_velocity, int())}")
    print(f"results_a: {list_mod(results_a, int())}")
    print(f"results_b: {list_mod(results_b, int())}")
    assert results_b == results_a

# test_get_list()
