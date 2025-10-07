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

settings << KeySignature("##")

long_notes: Clip = Note("D", 1/1) * 4 + Note("D", 1/2, Position(Measures(1), Beats(2))) >> Link()
long_notes << Foreach(6, 5, 1, 2, 6)**Degree() << Nth(3, 4)**Octave(5)
long_notes_pl = Playlist(long_notes)
long_notes_pl >> Rest() >> Play()

short_notes: Clip = long_notes - (long_notes.copy() | Measures(2)) + (long_notes.copy() << Duration(1/4) | Measures(2)) * 4 >> Link()
short_notes >> Rest() >> Play()

# repeated_notes: Track = short_notes.copy() << Equal(Measure(2))**Odd()**Dotted(1/4) << Equal(Measure(2))**Even()**NoteValue(1/8) >> Stack()
position_1 = Position(2, Beats(1))
position_2 = Position(2, Beats(2))
position_1 += Position()**Duration() << 1/16
position_2 -= Position()**Duration() << 1/16
repeated_notes: Clip = short_notes.copy() + Match(Measures(2))**Even()**Position(Duration(1/16)) >> Link()
repeated_notes >> Rest() >> Play(True)
