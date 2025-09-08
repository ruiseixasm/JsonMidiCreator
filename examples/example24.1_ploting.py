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

settings << Tempo(140) << TimeSignature(3, 4)
settings % TimeSignature() >> Print()

west_side = Clip(TrackName("West Side"))
west_side += Note(1/8) / 6
west_side /= Note(1/4) / 3
west_side << Nth(1, 2, 3)**Key("G")
west_side << Nth(4, 5, 6)**(Octave(5), Key("C"))
west_side << Nth(7, 8, 9)**Foreach("A", "F", "C")**Key()
west_side * 2 >> Plot()

settings << Settings()  # Rests to Defaults
settings % TimeSignature() >> Print()

