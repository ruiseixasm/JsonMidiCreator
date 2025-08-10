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

# Solution                0,  1
iterations: list[int] = [-7, +12]


snare = Note(DrumKit("Snare"), 1/16, Velocity(50)) / 16 * 4
def composition(clip: Clip) -> Composition:
    return snare + clip


SOLUTION = 0

many_notes = Note() / 8
rhythm_solution = RS_Clip(many_notes, plot=Plot(c_button=composition, title="Note Durations"))

rhythm_notes = rhythm_solution.rhythm_fast_quantized(iterations[SOLUTION]).solution()


SOLUTION = 1

chaos_2 = SinX(340, Conjunct(Strictness(0.95))**Modulo(7))
def tonality(clip: Clip) -> Clip:
    chaos_2.access(Tamer()).reset() # Resets tamer only
    chaos_data = chaos_2 % [2, 4, 4, 2, 1, 0, 3]
    multiple_degrees = list_mod(chaos_data, 7)
    # One can simple ignore the clip and work on the original clip
    new_clip = rhythm_notes * [0] # Just the first Measure
    new_clip += Foreach(*multiple_degrees)**Degree()
    return new_clip * 4

if iterations[SOLUTION] < 0:
    phrase_notes = rhythm_notes >> Plot(iterations=10, n_button=tonality, c_button=composition, title="Note Pitches")
else:
    phrase_notes = rhythm_notes >> Call(iterations=iterations[SOLUTION], n_button=tonality)


phrase_notes >> Plot()

