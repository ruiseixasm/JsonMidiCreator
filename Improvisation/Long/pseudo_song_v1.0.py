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
from operand_generic import settings
from operand_container import Devices
current_os = platform.system()
if current_os == "Windows":
    settings << Devices(["loopMIDI", "Microsoft"])  # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    settings << Devices(["IAC Bus", "Apple"])       # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    settings << Devices(["VMPK", "FLUID"])          # FLUID Synth


from JsonMidiCreator import *


total_measures: int = settings.convert_time_to_measures(seconds=40)
print(total_measures)

triad = Chord() * 4
triad << 0.9 << Cycle(1, 5, 4, 7)**Degree()
# triad << Parameters(Length(6))
triad *= Rest(2.0)
triad % Length() % Fraction() >> Print()
Rest(2.0) % Length() % Beats() % Fraction() >> Print()
# Must be with "/=" because it's a stacking on the end and not on the start
# triad /= 3
triad /= int( total_measures / (triad % Length() % int()) )



# triad >> Play(True)
triad >> Plot()
