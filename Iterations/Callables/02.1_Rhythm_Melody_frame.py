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
from jsonmidicreator_import import *    # This ensures src is added & JsonMidiCreator is imported

settings << Tempo(137)
indochine_motif = Clip() << Line(
    "n:2:C#, :6:B, :2:C#, :6:E, n:2:C#, :6:B, :2:C#, :6:E, n:2:C#, :6:B, :2:C#, :6:E"
)

indochine_motif[0] >> Print()

# Sets all notes on the Octave 7
next_notes = indochine_motif[First(4)] * 4 << Octave(7) \
    << Match(Step(2))**Semitone(4) \
    << Match(Beat(2))**Semitone(1) \
    << Every(4)**Semitone(-3)




next_notes >> Plot()



