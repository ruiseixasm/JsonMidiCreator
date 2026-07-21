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
    range_chaos = SinX(340, Interval([5, 8]))  # 8 is excluded
    results: set = set()
    for _ in range(10):
        print(f"Chaotic int: {range_chaos % int()}")
        results.add(range_chaos % int())
    assert len(results) == 3

# test_range_int()


def test_probability():
    free_chaos = SinX()
    tamed_chaos = SinX(Probability(1/2))
    free_values: list[Fraction] = []
    tamed_values: list[Fraction] = []
    for _ in range(10):
        free_number: Fraction = free_chaos % Fraction()
        free_number %= 100
        free_integer: int = 1 if free_number < Fraction(1, 2) * 100 else 0
        free_values.append(free_integer)
        tamed_number: int = tamed_chaos % int()
        tamed_values.append(tamed_number)
    assert free_values == tamed_values

# test_probability()

