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

settings += Device("Digitakt")
settings << Tempo(114)

open_hat = Note(1/8, Channel(6), Velocity(120)) / 8 << TrackName("Open Hat")
open_hat * 4 >> Plot(by_channel=True, block=False)

kick = Note(1/8, Channel(1), Velocity(90)) / "11.1.1.1"
snare = Note(1/8, Channel(2), Velocity(90)) / "..1...1."
rest = Rest(1/8) / string_nor("11.1.1.1", "..1...1.")
kick_snare = kick + snare + rest << TrackName("Kick & Snare")
# kick_snare * 4 >> Plot(True, composition=open_hat)



rhythm_solution = RS_Clip(kick_snare * 4, composition=open_hat * 4)
moved_beats = rhythm_solution.move_around(-10, by_channel=True).solution()

