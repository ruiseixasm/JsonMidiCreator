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
src_path = os.path.join(os.path.dirname(__file__), '../../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Determine the operating system
import platform
from operand_generic import settings
from operand_container import Devices
current_os = platform.system()
if current_os == "Windows":
    settings << Devices(["loopMIDI", "Microsoft"])  # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    settings << Devices(["IAC Bus", "Apple"])       # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    settings << Devices(["VMPK", "FLUID"])          # FLUID Synth




from operand_element import PitchChord
from operand_data import Play, Plot
from operand_container import Clip
from operand_unit import Inversion

polychord: Clip = PitchChord("minor", [1, 3, 5], Inversion(1)) * 1

polychord >> Plot()

