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

chaos = SinX(340)

def new_clip(clip: Clip) -> Clip:
    clip << Input(chaos)**Choice(60, 70, 80, 90, 100)**Velocity()
    return clip

ghost_notes = Note(DrumKit("Snare"), 1/16) / 16 * 8 << Velocity(50)

snare_part = Part(ghost_notes) >> Plot()

def composition(clip: Clip) -> Composition:
    # This filter retains the clip as a Clip and not as a Mask
    one_measure = clip >> Filter(Or(Measure(0), Measure(1)))

    # Automatically sorted by position
    interrupted_clip = one_measure + Measures(4) + one_measure
    return snare_part + interrupted_clip


four_notes = Note() * 4 << Key("A") << Duration(1/8) << Channel(2)
seed_clip: Clip = (Chord(Key("C"), Size("7th")) * Chord(Key("E"), Size("7th")) << Tied()) * 2 + four_notes

seed_clip >> Plot(iterations=10, n_button=new_clip, c_button=composition)

