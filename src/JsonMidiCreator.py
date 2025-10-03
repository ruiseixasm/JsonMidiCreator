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
import time
# Json Midi Creator Libraries
from operand import *
from operand_label import *
from operand_data import *
from operand_unit import *
from operand_rational import *
# Container needs to be imported before generic due to Staff
from operand_generic import *
from operand_element import *
from operand_frame import *
from operand_tamer import *
from operand_chaos import *
from operand_container import *
from resource_devices import *
from resource_operands import *
from resource_solutions import *
from resource_patterns import *


settings << Devices(["VMPK", "FLUID", "loopMIDI", "Microsoft", "IAC Bus", "Apple"])


# Set group of constants

# Class alias, abbreviations
N = Nt = Note
R = Rst = Rest
Ch = Channel
DS = Src = Pipe
Bars = Meas = Measures
Bar = Mea = Measure
Bts = Beats
Pt = Pitch
Pos = Position
Dur = Duration
Vel = Velocity
Deg = Degree
W = Tone
H = Semitone
KS = KeySignature
TS = TimeSignature
CC = ControlChange
PC = ProgramChange
T = Tmp = Tpo = Tempo
Q = Qtz = Qtzn = Quant = Quantization
High = HighResolution


# Keys
K = Key # The class not the object
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

# Actions
L = Link()
S = Stack()
P = Play(False)
Pv = Play(True)
Pr = Print()
Pl = Plot()

# Note Values alias, abbreviations
NV1 = whole = Duration(1/1)
NV2 = half = Duration(1/2)
NV4 = quarter = Duration(1/4)
NV8 = eight = Duration(1/8)
NV16 = sixteenth = Duration(1/16)
NV32 = Duration(1/32)
Dot1 = dotted_whole = Dotted(1/1)
Dot2 = dotted_half = Dotted(1/2)
Dot4 = dotted_quarter = Dotted(1/4)
Dot8 = dotted_eight = Dotted(1/8)
Dot16 = dotted_sixteenth = Dotted(1/16)
Dot32 = Dotted(1/32)


