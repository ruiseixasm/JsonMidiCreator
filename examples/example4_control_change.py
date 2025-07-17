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


# Global Staff setting up
settings << Tempo(60)

chord: Element = Chord() << Duration(2.0) << Gate(1) >> Save("json/_Save_4.1_control_change.json")
oscillate: Oscillate = Oscillate(50, offset=64)
control_change: Clip = ControlChange("Pan") * (2*16 + 1) << Iterate()**Steps()
control_change >>= oscillate
control_change >> Save("json/_Save_4.2_control_change.json")
    
chord + control_change >> Print() >> Play(1) >> Export("json/_Export_4.1_control_change.json")


# The length of the entire wave is one Measure or 4 beats or 16 steps
oscillate: Oscillate = Oscillate(int(128*128 / 2 - 1), 1/4)

# Stepping by 4 Steps is equivalent ot step by 1 Beat, same as , 1/4 Measure
# The default wavelength of the Oscillator is 1 Measure, so, for each PitchBend position:
#   0 Step = 0
#   1 Step = peak = 8191 / 2 = +4095
#   2 Step = 0
pitch_bend: Clip = PitchBend() * (2*16 + 1) << Iterate()**Steps()
pitch_bend >>= oscillate

chord + pitch_bend >> Play(1) >> Save("json/_Save_4.2_pitch_bend.json") >> Export("json/_Export_4.2_pitch_bend.json")
