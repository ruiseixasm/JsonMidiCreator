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


def new_tempo(clip: Clip) -> Clip:

    clip += Tempo(5)
    clip % Tempo() % int() >> Print()
    return clip

many_notes = Note() * 4 << Tempo(90)

many_notes << Velocity(65) << First()**Velocity(100) << 1/8


many_notes * 8 >> Plot(n_button=new_tempo)

many_notes * 8 << Velocity(100) << Match(Beat(0))**Velocity(65) >> Plot(iterations=10, n_button=new_tempo)
