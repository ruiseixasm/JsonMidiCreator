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


# Global Staff setting up
global_staff << Tempo(120) << Measure(1)
single_clock = Clock()

single_note = Note() << (Duration() << Measure(2)) >> Play()
note_transposed = single_note + Key(5) >> Play()

(Note3() << Key("E") << NoteValue(1/16)) * 8 + Iterate(1/2)**Beat() + single_clock \
    >> Save("json/_Save_3.1_triple_note3.json") >> Play(True)

(Note3() << Key("G") << NoteValue(1/16)) * 8 + Wrapper(Position())**Iterate(1/2)**Beat() + single_clock \
    >> Export("json/_Export_3.1_triple_note3.json") >> Play(True)
