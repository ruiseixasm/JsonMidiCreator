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
global_staff << Tempo(120) << Measure(7)

# All Sharps(#) of the Major Scale on the Circle of Fifths
(KeyScale("C") << Scale("Major")) * 8 + Iterate(Scale("Major") % Mode("5th"))**Key() + Iterate()**Measure() << NoteValue(1) << Velocity(70) >> Play(True) \
    >> Save("json/_Save_9.1_circle_fifths.json") >> Export("json/_Export_9.1_circle_fifths.json")
# All Fats(b) of the Major Scale on the Circle of Fifths
(KeyScale("C") << Scale("Major")) * 8 + Iterate(Scale("Major") % Mode("4th"))**Key() + Iterate()**Measure() << NoteValue(1) << Velocity(70) >> Play(True)

# All Sharps(#) of the minor Scale on the Circle of Fifths
(KeyScale("A") << Scale("minor")) * 8 + Iterate(Scale("minor") % Mode("5th"))**Key() + Iterate()**Measure() << NoteValue(1) << Velocity(70) >> Play(True)
# All Fats(b) of the minor Scale on the Circle of Fifths
(KeyScale("A") << Scale("minor")) * 8 + Iterate(Scale("minor") % Mode("4th"))**Key() + Iterate()**Measure() << NoteValue(1) << Velocity(70) >> Play(True)

