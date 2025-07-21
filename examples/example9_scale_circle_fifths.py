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
settings << Tempo(240)

# All Sharps(#) of the Major Scale on the Circle of Fifths
play_list_1 = Playlist() << ((KeyScale("C") << Scale("Major") << NoteValue(1)) / 8 
    + Iterate(step=7)**Semitone()
    << Duration(1/1) << Velocity(70) << Octave(4))
play_list_1 >> Play(True)

# All Fats(b) of the Major Scale on the Circle of Fifths
play_list_2 = Playlist() << ((KeyScale("C") << Scale("Major") << NoteValue(1)) / 8 
    + Iterate(step=5)**Semitone()
    << Duration(1/1) << Velocity(70) << Octave(4))
# play_list_2 >> Play()

# All Sharps(#) of the minor Scale on the Circle of Fifths
play_list_3 = Playlist() << ((KeyScale("A") << Scale("minor") << NoteValue(1)) / 8 
    + Iterate(step=7)**Semitone()
    << Duration(1/1) << Velocity(70) << Octave(4))
# play_list_3 >> Play()

# All Fats(b) of the minor Scale on the Circle of Fifths
play_list_4 = Playlist() << ((KeyScale("A") << Scale("minor") << NoteValue(1)) / 8 
    + Iterate(step=5)**Semitone()
    << Duration(1/1) << Velocity(70) << Octave(4))
# play_list_4 >> Play()

play_list_1 + Measures(0 * 8) \
    >> play_list_2 + Measure(1 * 8) \
    >> play_list_3 + Measure(2 * 8) \
    >> play_list_4 + Measure(3 * 8) \
    >> Play(True) >> Export("json/_Export_Example9_circle_fifths.json")
# play_list_2 >> Play()
