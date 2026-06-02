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
import time
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')

if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

settings << Folder("examples/")

"cc:1/4," * 5 >> Plot(title="Five ControlChange", block=False)
"at:1/4," * 5 >> Plot(title="Five Aftertouch", block=False)
"pb:1/4," * 5 >> Plot(title="Five PitchBend", block=False)
"a_pb:1/32:10:volume::100_1m" >> Plot(title="Smoothstep Automation at 0m", block=False)
"a_pb:1/32_1m:10:volume::100_1m" >> Plot(title="Smoothstep Automation at 1m", block=False)
"a_pb:1/32:10:volume:1:100_1m" >> Plot(title="Linear Automation at 0m", block=False)
"a_pb:1/32_1m:10:volume:1:100_1m" >> Plot(title="Linear Automation at 1m")

