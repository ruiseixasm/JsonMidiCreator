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
from jsonmidicreator import *

def snares() -> Clip:
    snares_16 = Note(Steps(1)) / 16
    snares_16[DownTo(Step(12))] //= Steps(1/2)
    snares_16[Less(Step(12))] -= Even()
    return snares_16


# snares() >> Plot()


def pattern_beats(beats_iterations: list[int] = [0, 0, 0, 0], probability: float = 0.9) -> Clip:

    pattern = Clip()
    for beat, iterations in enumerate(beats_iterations):
        sequencer = Sequencer(SinX(23, Probability(probability)), Beats(1))
        beat_clip = Note(Steps(1)) * sequencer
        for _ in range(iterations):
            beat_clip = Note(Steps(1)) * sequencer
        beat_clip += Beat(beat)
        pattern += beat_clip
        
    return pattern


def pattern_beats_n(clip: Clip) -> Clip:
    return clip


pattern_beats([3, 9, 5, 2]) >> Plot()



