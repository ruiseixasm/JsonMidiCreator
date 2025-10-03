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

rest_play = (R(), P)
settings << "bbb" << 120
Key() % str() >> Print()    # Returns the tonic key (I)

motif = Note() * 5 << eight >> LJ << Foreach(9, 6, 8, 9, 9)**Degree() >> Tie()
# motif >> rest_play
measure_2 = Note() * 3 << Equal(B1)**half >> S << Foreach(10, 9, 8)**Degree()
measure_4 = Note() * 2 << half << Foreach(8, 7)**Degree()
motif % NoteValue() >> Print(0)
measure_2 % NoteValue() >> Print(0)
measure_4 % NoteValue() >> Print(0)
(motif >> measure_2 >> motif >> measure_4 >> Rest(1/1) >> P >> Render("Midi/short_motif.mid")) % NoteValue() >> Print(0)

clarinet = \
    ProgramChange("Clarinet") + \
    (R << whole) + \
    motif + \
    (Note() * 3 << Nth(1)**half << Foreach(9, 11, 10)**Degree()) + \
    motif \
    >> S >> Tie() << Channel(1) << MidiTrack(1, "Clarinet") << Velocity(60)
clarinet % Measures(0) % NoteValue() >> Print(0)
# clarinet >> rest_play >> Render("Midi/clarinet.mid")
trumpet = \
    ProgramChange("Trumpet") + \
    motif + \
    (Note() * 2 << half << Foreach(5, 7)**Degree()) + \
    motif + \
    (Note() * 2 << half << Foreach(7, 6)**Degree()) \
    >> S << Channel(2) << MidiTrack(2, "Trumpet") << Velocity(30)
# trumpet >> rest_play
clarinet + trumpet >> L >> Rest(1/1) >> Render("Midi/theme.mid") >> ProgramChange(0, Channel(0)) >> ProgramChange(0, Channel(1)) >> P
