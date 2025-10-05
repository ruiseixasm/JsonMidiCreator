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

rest_play = ( Rest(), P)
settings << Tempo(140)

tresillo: Clip = Note(DrumKit("Drum"), 1/16) * 3 << Iterate(3)**Steps() << TimeSignature(2, 4)
snare: Clip = Note(DrumKit("Snare"), 1/16, Step(4)) * 1 << TimeSignature(2, 4)
hi_hat: Clip = Note(DrumKit("Hi-Hat"), 1/16) * 4 << Iterate(2)**Steps() << TimeSignature(2, 4)

(tresillo >> snare >> hi_hat) * 16 >> P

snare << TimeSignature(4, 4) << Beats(2) # Base 0 NOT base 1
hi_hat >>= Even()

(tresillo >> hi_hat) * 16 >> snare * 8 << Tempo(90) >> P

