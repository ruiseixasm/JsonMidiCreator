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

settings << Tempo(160) << Folder("examples/")


two_program_changes = \
    ProgramChange(Channel(11), Program("Viola")) \
    + ProgramChange(Channel(12), Program("Cello"))

two_program_changes >> Play()


tokens_clip = Clip()
tokens_clip *= "n;A n;C;1/8"

tokens_clip >> Plot(block=False, title="Tokens Clip")

new_clip = Clip("1/4;E 1/8")
new_clip >> Plot(title="New Clip")


