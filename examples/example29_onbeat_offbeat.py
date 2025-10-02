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

settings << Tempo(95) << Folder("examples/")


snare = Note(1/16, Channel(2)) / 16 * 4

snare >> Plot(block=False, title="All Beats")
snare >> Mask(OnBeat()) >> Plot(block=False, title="On Beat")
snare >> Mask(OffBeat()) >> Plot(block=False, title="Off Beat")
snare >> Mask(DownBeat()) >> Plot(block=False, title="Down Beat")
snare >> Mask(UpBeat()) >> Plot(block=False, title="Up Beat")

snare >> Mask(IsNull()**OnBeat()) >> Plot(block=False, title="Is Null")
snare >> Mask(IsNot(OnBeat())) >> Plot(block=False, title="Is Not On Beat")
snare >> Mask(IsNot(First())) >> Plot(block=True, title="Is Not the First")

