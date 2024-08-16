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
from JsonMidiCreator import *
import platform

# Determine the operating system
current_os = platform.system()
if current_os == "Windows":
    global_staff << Device(["loop", "Microsoft"])   # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    global_staff << Device(["Apple"])       # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    global_staff << Device(["FLUID"])       # FLUID Synth


# Global Staff setting up
global_staff << Tempo(140) << Measure(7)

seven_major_triad_chords = (Chord(3) << (Duration() << Beat(1))) * 7 + Increment()**Beat()
seven_major_triad_chords += Increment()**Mode(0)
seven_major_triad_chords >> Print() >> Play(True)
