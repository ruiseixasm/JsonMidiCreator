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
    "n:2:C#7, :6:E7, :2:C#7, :6:B6, :2:C#7, :6:E7, :2:C#7, :6:B6, :2:C#7, :6:E7, :2:F#6, :6:F6"
) << Name("Indochine")

indochine_motif[0] >> Print()

# Sets all notes on the Octave 7
next_notes = indochine_motif[First(4)] * 4 << Octave(7) \
    << Match(Step(2))**Semitone(4) \
    << Match(Beat(2))**Semitone(1) \
    << Every(4)**Iterate(-2)**Semitone()


# next_notes = indochine_motif \
#     << Last(2)**Iterate(-4)**Semitone()

last_notes = ~indochine_motif
last_notes << Select(Last(2))
last_notes *= 4
last_notes += Mux(2)**Iterate()**Semitone()

# last_notes >> Plot()


four_notes = Clip(
    Line(":2:C#7, :6:E7, :2:F#6, :6:F6")
) << Select(Nth(3)) << Name("Four Notes")

notes_setting = I_Setter(Semitone(), Cycle())
# last_measure = four_notes \
#     >> Plot(n_button=notes_setting.new_iteration, iterations=2) << Select(Nth(4)) >> Plot(n_button=notes_setting.new_iteration, iterations=5) \
#     << Unmask()

# final_motif = indochine_motif * [0, 1] * last_measure
# final_motif >> Plot()   # Same as "n:2:C#7, :6:E7, :2:C#7, :6:B6, :2:C#7, :6:E7, :2:C#7, :6:B6, :2:C#7, :6:E7, :2:C#6, :6:F#"


real_motif = Clip(
    "n:2:C#7, :6:E7, :2:C#7, :6:B6, :2:C#7, :6:E7, :2:C#7, :6:B6, :2:C#7, :6:E7, :2:E6, :6:F#"
) << Name("Real Motif")
real_motif >> Plot()

