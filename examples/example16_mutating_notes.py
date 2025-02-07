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

rest_play = (R, P)
defaults << 150
Key() % str() >> Print()    # Returns the tonic key (I)
motif = oe.Note() * 6 << of.Foreach(1/4, 1/8, 1/8, ra.Dotted(1/4), 1/4, 1/1) \
    >> od.Stack() << of.Foreach(-3, 1, 2, 3, 2, -3) # Degree
motif * 2 >> Play()

mutation = Mutation()
# for _ in range(5):
#     mutation * 10 % motif * 2.0 >> Sort() >> Stack() >> Play()
#     # mutation * 10 % motif * 2.0 >> Sort() >> Stack()

crossover = Crossover(Pitch, 2.0)
for _ in range(4):
    crossover * 40 % motif * 2.0 >> Play()


# mutation = TranslocateRhythm(mutation) * 60 * 4.01
# mutation = TranslocatePitch(mutation) * 35 * 4.02

# mutation >> Print()
