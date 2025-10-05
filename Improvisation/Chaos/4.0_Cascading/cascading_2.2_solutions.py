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


snare = Note(DrumKit("Snare"), 1/16, Velocity(50)) / 16 * 4

seed_notes = Note() / 8
clip_solution = RS_Clip(seed_notes)

phrase_notes = clip_solution.rhythm_fast_quantized(7).mask(Beat(0)) \
    .pitch_tonality_conjunct_but_slacked(3).unmask().solution()
# phrase_notes >> Plot()

key_signatures = RS_Clip(phrase_notes)
phrase_notes = key_signatures.pitch_sweep_sharps(7).solution()
# phrase_notes >> Plot()

