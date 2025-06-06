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

import time

import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
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


from operand_element import Chord
from operand_data import Plot, Decompose, Stack, Copy
from operand_frame import Nth
from operand_rational import Duration
from operand_unit import Degree

single_chord = Chord(1/4) * 1 >> Decompose() >> Stack()
single_chord /= single_chord[0]

single_chord >> Plot(False)

third_note = single_chord >> Nth(3)
third_note /= Duration(2)
third_note /= third_note[0] >> Copy() << Degree(4)

third_note >> Plot(False)
single_chord >> Plot()
