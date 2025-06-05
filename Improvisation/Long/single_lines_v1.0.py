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
src_path = os.path.join(os.path.dirname(__file__), '../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Determine the operating system
import platform
from operand_generic import defaults
from operand_container import Devices
current_os = platform.system()
if current_os == "Windows":
    defaults << Devices(["loopMIDI", "Microsoft"])  # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    defaults << Devices(["IAC Bus", "Apple"])       # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    defaults << Devices(["VMPK", "FLUID"])          # FLUID Synth


from JsonMidiCreator import *


# Chord(1/4) * 4 * 2 << Foreach("i", "IV", "iii", "V")**Degree() >> Plot(False)
# Polychord(1/4) * 4 * 2 << Foreach("i", "IV", "iii", "V")**Degree() >> Plot(False)

# Chord() * 1 - Degree(1) >> Plot(False)
# Polychord() * 1 - Degree(1) >> Plot(False)
# Polychord([-1, 2, 4]) * 1 >> Plot()


# Simple progression:
chord_progression: Frame = Foreach("i", "IV", "iii", "V")**Degree()

defaults << Scale("Major")

major_triad: Clip = Chord(1/4) * 4
major_triad << chord_progression

defaults << Scale("minor")

# By being a "minor" scale it will get
# different root notes from C "Major" but equal intervals
minor_triad: Clip = Chord(1/4, Channel(2)) * 4
minor_triad << chord_progression
minor_triad -= Octave() # Key A is the Tonic, meaning, an high key
# minor_triad >> Plot()

# THIS WILL MAKE THE MINOR_TRIAD ADOPT THE MAJOR STAFF !!!!!
# major_triad * minor_triad * 8 >> Plot()
# HAS TO BE WRAPPED IN A PART FIRST !!!
final_part: Part = Part(major_triad) * minor_triad * 8
# BOTH OF THESE ARE EQUIVALENT
final_part += Equal(Measure(3))**Octave(1)  # Option 1
# final_part[3] += Octave(1)                  # Option 2
final_part % int() >> Print()
final_part >> Plot()

