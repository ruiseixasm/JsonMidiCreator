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
src_path = os.path.join(os.path.dirname(__file__), '../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *



# Polychords
"""

Chord(1/4) * 4 * 2 << Foreach("i", "IV", "iii", "V")**Degree() >> Plot(False)
Polychord(1/4) * 4 * 2 << Foreach("i", "IV", "iii", "V")**Degree() >> Plot(False)

Chord() * 1 - Degree(1) >> Plot(False)
Polychord() * 1 - Degree(1) >> Plot(False)
Polychord([-1, 2, 4]) * 1 >> Plot()

"""




# Simple progression:
"""

chord_progression: Frame = Foreach("i", "IV", "iii", "V")**Degree()

defaults << Scale("Major")

major_triad: Clip = Chord(1/4) * 4
major_triad << chord_progression

defaults << Scale("minor")

# By being a "minor" scale it will get
# different root notes from C "Major" but equal intervals
minor_triad: Clip = Chord(1/4, Channel(2)) * 4
minor_triad << chord_progression
minor_triad -= Octave() # Key A is the Tonic, meaning, an high key
# minor_triad >> Plot()

# THIS WILL MAKE THE MINOR_TRIAD ADOPT THE MAJOR STAFF !!!!!
# major_triad * minor_triad * 8 >> Plot()
# HAS TO BE WRAPPED IN A PART FIRST !!!
final_part: Part = Part(major_triad) * minor_triad * 8
# BOTH OF THESE ARE EQUIVALENT
final_part += Equal(Measure(3))**Octave(1)  # Option 1
# final_part[3] += Octave(1)                  # Option 2
final_part % int() >> Print()
final_part >> Plot()

"""



# entire_part: Part = Part()

# # Setting the Key Signature for the global Staff
# for sharps in range(8):
#     defaults << KeySignature(sharps)
#     chord_progression: Clip = Chord(1/4) * 3 << Last()**(1/2)
#     chord_progression << Foreach(1, 4, 5)**Degree()
#     entire_part *= chord_progression * 4

# entire_part >> Plot()

# entire_part = Part()

# for sharps in range(0, -8, -1):
#     defaults << KeySignature(sharps)
#     chord_progression: Clip = Chord(1/4) * 3 << Last()**(1/2)
#     chord_progression << Foreach(1, 4, 5)**Degree()
#     entire_part *= chord_progression * 4

# entire_part >> Plot()

# two_notes: Clip = Note(Tied()) * 2
# two_notes >> Plot()

# two_chords: Clip = Chord(Tied()) * 2
# two_chords >> Plot()


entire_part: Part = Part()

# Setting the Key Signature for the global Staff
settings << KeySignature(1)
chord_progression: Clip = Chord(Channel(2), Tied()) * 4
chord_progression << Foreach(1, 4, 5)**Degree()
chord_progression >> Rotate(-1) >> Decompose() >> Plot(block=False)
# chord_progression % int() >> Print()
chord_progression += Rest(Measure(3))   # To occupy the 4th Measure
chord_progression >> Tie()  # Removes notes
chord_progression << LessOrEqual(Duration(1/1))**Duration(7/8)

entire_part += chord_progression
entire_part * 4 >> Plot()

# print(chord_progression % int())
