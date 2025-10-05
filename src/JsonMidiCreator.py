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

# Data aliases
Title = Name = TrackName
# Unit aliases
K = Key
Root = RootKey
Tonic = TonicKey
W = Tone
H = Semitone
Ch = Channel
KS = KeySignature
# Rational aliases
Bars = Measures
Bar = Measure
# Element aliases
CC = ControlChange
PC = ProgramChange
# Generic aliases
TS = TimeSignature
# Frame aliases
Each = Foreach
# Container aliases
Section = Part

# Keys
C = Key("C")
D = Key("D")
E = Key("E")
F = Key("F")
G = Key("G")
A = Key("A")
B = Key("B")

# Note Values alias, abbreviations
whole = Duration(1/1)
half = Duration(1/2)
quarter = Duration(1/4)
eight = Duration(1/8)
sixteenth = Duration(1/16)
dotted_whole = Dotted(1/1)
dotted_half = Dotted(1/2)
dotted_quarter = Dotted(1/4)
dotted_eight = Dotted(1/8)
dotted_sixteenth = Dotted(1/16)


