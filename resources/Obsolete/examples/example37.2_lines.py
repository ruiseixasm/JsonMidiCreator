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

from jsonmidicreator import *

settings << Folder("examples/")

"a_._10:1/32_1m:10:volume::100_1m:10_1m_2b" >> Plot(title="Smoothstep Automation at 1m", block=False)
automation = Automation("a__8:1/32_1m:10:volume::100_1m:10_1m_2b")
automation >> Plot(title="Smoothstep Automation Original", block=False)
automation + Dot(-1, +50) >> Plot(title="Smoothstep Automation + 50", block=False)
automation + Dot(-1, -50) >> Plot(title="Smoothstep Automation - 50", block=False)
automation - Dot(-1, 50) + Dot(-1, 50) >> Plot(title="Smoothstep Automation - 50 + 50")


