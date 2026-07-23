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

settings << Tempo(137)
indochine_motif = Clip() << Line(
    "n:2:C#6, :6:B5, :2:A5, :6:E6, :2:C#6, :6:B5, :2:A5, :6:E6, :2:C#6, :6:B5, :2:C#6, :22:A5"
)

indochine_motif[0] >> Print()

def pre_filter(candidate: Clip, seed: Clip) -> bool:
    return candidate[0] == "C#7"

def post_process(clip) -> Composition:
    
    clip[0] << "C#7"
    return clip

SinX(340).first_collision_index() >> Print()    # If -1 it means no collision (cycling results)

octave_setter = I_SetParameter(Octave(), SinX(340, Interval([6, 8])))    # 8 is excluded
semitone_setter = I_SetParameter(Semitone(), SinX(340, Interval([0, 12]))**SinX(), post_process=post_process, no_repetitions=True, max_tries=1000)
motif_generator = octave_setter**semitone_setter
indochine_motif >> motif_generator >> Plot()



