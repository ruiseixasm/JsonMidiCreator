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

read_notes = Load("timed_read_notes_clip_18bc_save.json") << Title("Read Notes")
read_notes >> Plot(block=False)

quantized_notes = read_notes >> Quantize(quantize_duration=True) << Title("Quantized Notes")
quantized_notes >> Plot(block=False)

match_pitch = RS_Clip(quantized_notes, [1, 0, 0, 0], 2)\
    .mask(Beat(0))\
    .set_parameter(10, SinX(Increase(1)**Modulo(7)), Degree(), 3)\
    .unmask().solution()

