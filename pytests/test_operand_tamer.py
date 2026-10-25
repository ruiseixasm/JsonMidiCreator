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



def test_range_int():
    ranged_chaos = Interval([5, 8], SinX(340))  # 8 is excluded
    results: set = set()
    for _ in range(10):
        print(f"Chaotic int: {ranged_chaos % int()}")
        results.add(ranged_chaos % int())
    assert len(results) == 3

# test_range_int()


def test_tamer_decoupling():
    untamed = Untamed()
    assert untamed._index == -1
    untamed_copy = untamed.copy()
    assert untamed_copy._index == -1
    assert untamed._index == -1
    untamed_copy.iterate()
    assert untamed_copy._index == 0
    assert untamed._index == -1

# test_tamer_decoupling()


def test_untamed_mod():

    # Perform the operation
    untamed = Untamed()

    # untamed remains unchangeable
    untamed_1     = untamed * 1      # Implicit copy
    untamed_1000  = untamed * 1000   # Implicit copy

    # Index starts at 0, the first iteration, thus the -1
    assert untamed_1._index == 1 - 1
    assert untamed_1000._index == 1000 - 1

    assert untamed_1000 != untamed_1
    assert untamed_1000 == untamed_1 * 999
    untamed_1.reset()
    assert untamed_1 == untamed
    untamed *= 1000   # This changes the original untamed
    assert untamed_1000 == untamed
    assert untamed_1000 * 1 == untamed_1 * 1000 * 1

# test_untamed_mod()


def test_cycle():
    cycle = Untamed(Cycle()) # Default modulus is 12
    for value in range(12):
        assert cycle % int() == value

# test_cycle()


def test_counter():
    counter_int = Untamed(Counter(-7))**int()
    assert counter_int % Pipe(int()) == -7
    for iteration in range(-7, 8):
        number = counter_int.chaoticize()
        assert isinstance(number, int)
        assert number == iteration

# test_counter()


def test_cycle_modulo():

    cycle = Modulo(4, Cycle())

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


def test_probability():
    free_chaos = Untamed()
    tamed_chaos = Probability(1/2)
    free_values: list[Fraction] = []
    tamed_values: list[Fraction] = []
    for _ in range(10):
        free_number: Fraction = free_chaos % Fraction()
        free_number %= 1
        free_integer: int = 1 if 1 - free_number < Fraction(1, 2) else 0
        free_values.append(free_integer)
        tamed_number: int = tamed_chaos % int()
        tamed_values.append(tamed_number)
    assert free_values == tamed_values

# test_probability()



