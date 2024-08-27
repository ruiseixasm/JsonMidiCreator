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

# Process Exported files
first_import = Import("json/_Export_1.1_sequence.json")
second_import = Import("json/_Export_1.2_all_elements.json")    # It has a clock!
(Position(0) >> first_import) + (Position(1) >> first_import) + (Position(2) >> first_import) + (Position(3) >> first_import) + (Position(4) >> second_import) \
    >> Export("json/_Export_2.1_multiple_imports.json") >> Play(1)

# Process Loaded files
first_load = Load("json/_Save_1.1_first_note.json")
note_0 = Note() << (Position(0) >> first_load)
note_1 = Note() << (Position(1) >> first_load)
note_2 = Note() << (Position(2) >> first_load)
note_3 = Note() << (Position(3) >> first_load)
note_0 + note_1 + note_2 + note_3 >> Save ("json/_Save_2.1_multiple_notes.json") >> Print() >> Play(True)
