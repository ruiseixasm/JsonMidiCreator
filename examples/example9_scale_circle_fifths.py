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
staff << Tempo(240) << Measure(7)

# All Sharps(#) of the Major Scale on the Circle of Fifths
play_list_1 = PlayList() << (Position(0) >> (KeyScale("C") << Scale("Major") << NoteValue(1) << Velocity(70)) * 8 
    + Iterate(Scale("Major") % Transposition("5th"))**Key() + Iterate()**Measure() + Clock(8))

# All Fats(b) of the Major Scale on the Circle of Fifths
play_list_2 = PlayList() << (Position(8) >> (KeyScale("C") << Scale("Major") << NoteValue(1) << Velocity(70)) * 8 
    + Iterate(Scale("Major") % Transposition("4th"))**Key() + Iterate()**Measure() + Clock(8))

# All Sharps(#) of the minor Scale on the Circle of Fifths
play_list_3 = PlayList() << (Position(16) >> (KeyScale("A") << Scale("minor") << NoteValue(1) << Velocity(70)) * 8 
    + Iterate(Scale("minor") % Transposition("5th"))**Key() + Iterate()**Measure() + Clock(8))

# All Fats(b) of the minor Scale on the Circle of Fifths
play_list_4 = PlayList() << (Position(24) >> (KeyScale("A") << Scale("minor") << NoteValue(1) << Velocity(70)) * 8 
    + Iterate(Scale("minor") % Transposition("4th"))**Key() + Iterate()**Measure() + Clock(8))

play_list_1 + play_list_2 + play_list_3 + play_list_4 >> Play(True)
