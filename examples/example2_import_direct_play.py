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
first_import + Measure(0) >> first_import + Measure(2) >> first_import + Measure(4) >> first_import + Measure(6) \
    >> second_import + Measure(8) \
    >> Export("json/_Export_2.1_multiple_imports.json") >> Play(1)

# Process Loaded files as Elements
note = Note(Load("json/testing/_Save_1.1_first_note.json"))
note / 4 >> Save ("json/_Save_2.1_multiple_notes.json") >> Print() >> Play(True)

# Process Loaded files as Serialization
load = Note(Load("json/testing/_Save_1.1_first_note.json").copy())
load / 4 >> Save ("json/_Save_2.2_sequence_notes.json") >> Print() >> Play(True)
