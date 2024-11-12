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
from fractions import Fraction
# Json Midi Creator Libraries
from operand import *
from operand_staff import *
from operand_unit import *
from operand_rational import *
from operand_time import *
from operand_data import *
from operand_label import *
from operand_frame import *
from operand_operator import *
from operand_generic import *
from operand_container import *
from operand_element import *
from operand_chaotic_randomizer import *
from operand_iterator import *

# Determine the operating system
import platform
current_os = platform.system()
if current_os == "Windows":
    staff << Device(["loopMIDI", "Microsoft"])   # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    staff << Device(["IAC Bus", "Apple"])        # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    staff << Device(["VMPK", "FLUID"])           # FLUID Synth

# Set group of constants
# Keys
K = Key()
C = Key("C")
D = Key("D")
E = Key("E")
F = Key("F")
G = Key("G")
A = Key("A")
B = Key("B")
# Octaves
O0 = Octave(0)
O1 = Octave(1)
O2 = Octave(2)
O3 = Octave(3)
O4 = Octave(4)
O5 = Octave(5)
O6 = Octave(6)
O7 = Octave(7)
O8 = Octave(8)
O9 = Octave(9)
# Elements
N = Note()
R = Rest()
# Actions
L = Link()
LT = LJ = Link(True)
S = Stack()
P = Play()
# Note Values
NV1 = whole = NoteValue(1/1)
NV2 = half = NoteValue(1/2)
NV4 = quarter = NoteValue(1/4)
NV8 = eight = NoteValue(1/8)
NV16 = sixteenth = NoteValue(1/16)
NV32 = NoteValue(1/32)
Dot1 = dotted_whole = Dotted(1/1)
Dot2 = dotted_half = Dotted(1/2)
Dot4 = dotted_quarter = Dotted(1/4)
Dot8 = dotted_eight = Dotted(1/8)
Dot16 = dotted_sixteenth = Dotted(1/16)
Dot32 = Dotted(1/32)
# Staff Position
# Measures
M1 = Measure(0)
M2 = Measure(1)
M3 = Measure(2)
M4 = Measure(3)
M5 = Measure(4)
M6 = Measure(5)
M7 = Measure(6)
M8 = Measure(7)
# Beats
B1 = Beat(0)
B2 = Beat(1)
B3 = Beat(2)
B4 = Beat(3)
B5 = Beat(4)
B6 = Beat(5)
B7 = Beat(6)
B8 = Beat(7)
# Steps
S1 = Step(0)
S2 = Step(1)
S3 = Step(2)
S4 = Step(3)
S5 = Step(4)
S6 = Step(5)
S7 = Step(6)
S8 = Step(7)
S9 = Step(8)
S10 = Step(9)
S11 = Step(10)
S12 = Step(11)
S13 = Step(12)
S14 = Step(13)
S15 = Step(14)
S16 = Step(15)
S17 = Step(16)
S18 = Step(17)
S19 = Step(18)
S20 = Step(19)
S21 = Step(20)
S22 = Step(21)
S23 = Step(22)
S24 = Step(23)
S25 = Step(24)
S26 = Step(25)
S27 = Step(26)
S28 = Step(27)
S29 = Step(28)
S30 = Step(29)
S31 = Step(30)
S32 = Step(31)

