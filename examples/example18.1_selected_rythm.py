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

rhythmic_notes = Note() * 8 * 8 << Loop(whole, dotted_half, half, dotted_quarter, dotted_eight, eight, dotted_sixteenth, sixteenth) >> Stack()
# rhythmic_notes >> P

mutated_clip = Note() * 8 << of.Loop(2, 3, 2, -3, 1, -3, 4, 5) # Degree
# mutated_clip >> P

duration_mutation = Shuffling(Duration) * 22
duration_mutation << rhythmic_notes
length_condition = Condition(Length(1.0))
minimum_notes = Least(8)
total_plays = Before(12)
final_clip = Clip()
first_clip = Before(1)
original_clip = mutated_clip.copy() - Octave()

for _ in range(400):
    mutated_clip <<= duration_mutation
    original_clip += mutated_clip
    original_clip >> first_clip >> MidiExport("Midi/18.1_first_clip.mid")
    final_clip *= mutated_clip.copy().stack().trim().link() >> minimum_notes >> length_condition >> total_plays

final_clip % Length() % float() >> Print()
final_clip >> MidiExport("Midi/18.1_chaotic_rhythm_3.mid")
