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

movement = Note() * (3*4 + 1)
movement << Equal(Measures(3))**Pitch("D", 5) << Equal(Measures(3))**NoteValue(1) \
         << Equal(Measures(0))**Key("E") << Equal(Measures(1))**Key("G") << Equal(Measures(2))**Key("B")
movement += Equal(Measures(0))**Iterate()**Key()
movement += Equal(Measures(1))**Iterate()**Key()
movement += Equal(Measures(2))**Iterate()**Key()
movement >> Play(True)

Rest(1) >> Export("json/_Export_Rest_01.1.json") >> Play(True)

movement = Note(Octave(5)) * 9
movement << Container(Duration(1/2), None, None, Duration(1/2), Duration(1/2), Duration(1/2), None, None, Duration(1/1))
movement << Container(None, None, None, Pitch("B", 4), None, Key("D"), Key("D"), Key("D"), None)
movement >> Stack() >> Play()

Rest(1) >> Export("json/_Export_Rest_01.2.json") >> Play(True)

movement = Note() * 12
movement << Nth(7)**Duration(1/2) << Nth(12)**Duration(1/1)
movement += Container(9, 6, 7, 10, 9, 8, 7, 6, 5, 4, 0, 1)
movement >> Stack() >> Play()

