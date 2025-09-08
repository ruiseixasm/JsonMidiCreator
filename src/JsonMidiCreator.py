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
from operand_unit import *
from operand_rational import *
from operand_data import *
from operand_label import *
from operand_frame import *
# Container needs to be imported before generic due to Staff
from operand_container import *
from operand_generic import *
from operand_element import *
from operand_tamer import *
from operand_chaos import *
from resource_devices import *
from resource_operands import *
from resource_solutions import *
from resource_patterns import *


# Determine the operating system
import platform
current_os = platform.system()
if current_os == "Windows":
    settings << Devices(["loopMIDI", "Microsoft"])  # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    settings << Devices(["IAC Bus", "Apple"])       # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    settings << Devices(["VMPK", "FLUID"])          # FLUID Synth


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

# Staff Position

# Measures
M1 = Measures(0)
M2 = Measures(1)
M3 = Measures(2)
M4 = Measures(3)
M5 = Measures(4)
M6 = Measures(5)
M7 = Measures(6)
M8 = Measures(7)

# Beats
B1 = Beats(0)
B2 = Beats(1)
B3 = Beats(2)
B4 = Beats(3)
B5 = Beats(4)
B6 = Beats(5)
B7 = Beats(6)
B8 = Beats(7)

# Steps
S1 = Steps(0)
S2 = Steps(1)
S3 = Steps(2)
S4 = Steps(3)
S5 = Steps(4)
S6 = Steps(5)
S7 = Steps(6)
S8 = Steps(7)
S9 = Steps(8)
S10 = Steps(9)
S11 = Steps(10)
S12 = Steps(11)
S13 = Steps(12)
S14 = Steps(13)
S15 = Steps(14)
S16 = Steps(15)
S17 = Steps(16)
S18 = Steps(17)
S19 = Steps(18)
S20 = Steps(19)
S21 = Steps(20)
S22 = Steps(21)
S23 = Steps(22)
S24 = Steps(23)
S25 = Steps(24)
S26 = Steps(25)
S27 = Steps(26)
S28 = Steps(27)
S29 = Steps(28)
S30 = Steps(29)
S31 = Steps(30)
S32 = Steps(31)

