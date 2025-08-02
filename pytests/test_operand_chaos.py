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

    modulus = Modulus(Period(4))

    assert modulus * 0 % int() == 0
    assert modulus * 1 % int() == 1
    assert modulus * 2 % int() == 2
    assert modulus * 3 % int() == 3
    assert modulus * 4 % int() == 0

    assert modulus @ 0 % int() == 0
    assert modulus @ 1 % int() == 1
    assert modulus @ 1 % int() == 2
    assert modulus @ 1 % int() == 3
    assert modulus @ 1 % int() == 0

# test_modulus()


def test_chained_chaos():

    modulus_sinx = Modulus()**SinX()
    modulus_sinx *= 2.01

    modulus_sinx % int() >> Print()
    assert modulus_sinx % int() < 12

    sinx = SinX()
    modulus = Modulus()
    assert modulus != modulus_sinx

    sinx *= 2.01
    modulus << sinx
    modulus *= 2.01
    assert modulus == modulus_sinx

# test_chained_chaos()


