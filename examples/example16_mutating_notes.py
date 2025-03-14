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
import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

rest_play = (R(), P)
defaults << 150
defaults % Key() % str() >> Print()    # Returns the tonic key (I)

motif_1 = oe.Note() * 6 << of.Loop(1/4, 1/8, 1/8, ra.Dotted(1/4), 1/4, 1/1) \
            >> od.Stack() << of.Loop(2, 3, 2, -3, 1, -3) # Degree

motif_2 = oe.Note() * 6 << of.Loop(1/4, 1/8, 1/8, ra.Dotted(1/4), 1/4, 1/1) \
            >> od.Stack() << of.Loop(-3, 1, 2, 3, 2, -3) # Degree

motif_2 * 2 >> Play()

mutation = Shuffling()
for _ in range(5):
    R() >> P
    motif_2.process(mutation) / 2 >> S >> P
    # motif_2 / mutation * 2.0 >> Stack()

crossover = Crossover(Pitch, 2.0) * 40
for _ in range(4):
    R() >> P
    motif_2.process(crossover).stack() / 2 >> Play()


# mutation = TranslocateRhythm(mutation) * 60 * 4.01
# mutation = TranslocatePitch(mutation) * 35 * 4.02

# mutation >> Print()
