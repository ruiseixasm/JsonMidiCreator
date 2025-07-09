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
src_path = os.path.join(os.path.dirname(__file__), '../../../../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

rest_play = (R(), P)
settings << Tempo(110)

tresillo: Clip = Note(DrumKit("Drum"), 1/16) * 6 << Iterate(3)**Steps()
tresillo *= tresillo / Mask(Nth(1, 2)) << Foreach(B2, B3)
clap: Clip = Note(DrumKit("Clap"), 1/16) * 4 << Iterate(2)**Add(1)**Beats()

strong_contrast: Clip = tresillo + clap
strong_contrast % Length() % Steps() % float() >> Print()

strong_contrast * 8 >> P

