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

indochine_motif = Clip() << Line(
    "n:2:C#7, :6:B6, :2:A6, :6:E7, :2:C#7, :6:B6, :2:A6, :6:E7, :2:C#7, :6:B6, :2:C#7, :22:A6"
)

indochine_motif[0] >> Print()

next_notes = indochine_motif[First(2)] * 8 << Octave(7) << Match(Step(2))**Iterate()**Semitone()
next_notes >> Plot()



