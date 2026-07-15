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

# Four Notes
"n," * 4 >> Plot(title="Four Notes", block=False)

# Pitched Notes
":, ::E, ::G, :," >> Plot(title="Pitched Notes", block=False)

# Three Chords
"c:, c_-_4:2b:3_4., c:2b:5.:80," >> Plot(title="Three Chords", block=False)

# Two Clusters
"cl_-_2:3b:3m_1._3._4., cl:1b:m_2._4._6._9., " >> Plot(title="Two Clusters with an Inversion")

