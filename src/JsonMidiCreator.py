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
from operand_value import *
from operand_time import *
from operand_data import *
from operand_label import *
from operand_frame import *
from operand_operator import *
from operand_generic import *
from operand_container import *
from operand_element import *

# Determine the operating system
import platform
current_os = platform.system()
if current_os == "Windows":
    staff << Device(["loopMIDI", "Microsoft"])   # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    staff << Device(["IAC Bus", "Apple"])        # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    staff << Device(["VMPK", "FLUID"])           # FLUID Synth
