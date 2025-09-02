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

chaos = Cycle(Modulus(7))   # Works like a cyclic picker

def new_clip(clip: Clip) -> Clip:
    clip << Input(chaos)**Choice("C", "D", "E", "F", "G", "A", "B")
    return clip

triads = Chord(1/2) * 7    # Equivalent to 3 Measures and 2 Beats

ghost_notes = Note(DrumKit("Snare"), 1/16) * 16 * 8 << Velocity(50)
snare_part = Part(ghost_notes)

triads / 2 >> Plot(iterations=1, n_button=new_clip, composition=snare_part)




