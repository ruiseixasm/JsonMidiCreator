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

# rest_play = (R, P)
staff << 150
K % str() >> Print()    # Returns the tonic key (I)

single_notes = N * 12 << Nth(1, 2, 5, 6, 7, 8, 9, 12)**Foreach(dotted_quarter, eight, dotted_quarter, eight, half, dotted_quarter, eight, whole) >> S
single_notes << Foreach(A, B, A, G, A, B, A, B, D, C, B, A) >> Smooth()
slow_melody = N * 5 << 1/1 << Nth(2, 3)**half >> S
slow_melody << Foreach(G, E, A, B, "G#")
fast_melody = \
    (N * 9 << eight << Nth(1, 2)**sixteenth << Foreach(1, 2, 3, 3, 3, 2, 1, 2, 3)**Degree()) + \
    (N * 7 << eight << Nth(5)**quarter      << Foreach(1, -2, 1, 2, 3, -4, 2)**Degree()) + \
    (N * 9 << eight << Nth(1, 2)**sixteenth << Foreach(1, 2, 3, 3, 5, 3, 2, 1)**Degree()) + \
    (N * 5 << eight << Nth(5)**half         << Foreach(2, 2, 2, 3, 2)**Degree()) << Gate(0.7) >> S

sequences = Sequences(
    single_notes, slow_melody, fast_melody
)

sequence = N * 12   # blank sequence to work on
crossing_over = Crossover(sequence, sequences)

final_mutation = crossing_over * 40 * 8.37
final_mutation >> Print()
