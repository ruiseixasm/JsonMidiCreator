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

# https://youtu.be/TbDUsEmbsPw?si=kkpOfJ1vrp1ECd1x

# Global Staff setting up
defaults << Tempo(120)

# All whites
b_minor_scale = KeyScale(Scale("Dorian"), "D")
b_minor_scale >> P
R() >> P

seven_keys = Note(1/1) / 7 << Iterate()
seven_keys >> P
R() >> P

seven_keys << CParameter(Scale("Dorian"))
seven_keys >> P
R() >> P

seven_keys << Degree(0) # Degree 0 sets the Scale natural tonic
seven_keys >> P
R() >> P

