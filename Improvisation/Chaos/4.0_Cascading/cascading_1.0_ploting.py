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
many_notes = Note() / 8 << Foreach(1/2, 1/4, 1/4, 1/8, 1/8, 1/16 * 3/2, 1/16, 1/16)
durations_list = list_get(many_notes.stack() % list(), Duration())

def iteration(clip: Clip) -> Clip:
    picked_durations = list_pick(durations_list, chaos % [2, 4, 4, 2, 1, 0, 3])
    clip_notes = clip % list()
    clip <<= list_set(clip_notes, picked_durations)
    return clip.stack().quantize().link()

snare = Note(DrumKit("Snare"), 1/16, Velocity(50)) / 16 * 2
def composition(clip: Clip) -> Composition:
    return snare + clip

many_notes >> Plot(iterations=10, n_button=iteration, c_button=composition, title="Note Durations")
