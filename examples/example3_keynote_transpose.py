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

# Determine the operating system
import platform
current_os = platform.system()
if current_os == "Windows":
    global_staff << Device(["loop", "Microsoft"])   # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    global_staff << Device(["Apple"])               # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    global_staff << Device(["VMPK", "FLUID"])       # FLUID Synth


# Global Staff setting up
global_staff << Tempo(110) << Measure(6)

single_note = Note() << (Duration() << Measure(2)) >> Play()
note_transposed = single_note + Key(5) >> Play()
