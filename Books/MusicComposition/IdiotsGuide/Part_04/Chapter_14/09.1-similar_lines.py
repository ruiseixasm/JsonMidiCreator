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
src_path = os.path.join(os.path.dirname(__file__), '../../../../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

settings << KeySignature('bbb')

theme_1 = Note(Key('Bb')) / [1/8, 0, 0, 0, 1/4, 0, 1/2, 0, 1/4, 0, 0, 0, 1/1] << Name("Original")
theme_1[0] >>= Rest()
theme_1[8] >>= Rest()
theme_1 += InputType(Note)**Foreach(0, 1, 0, 1, 2, 3, 1, 3, 5, 4, 3)**Degree()
theme_1 >> Plot(block=False)

if False:

    theme_2 = theme_1 - Octave(1) << Channel(2)
    theme_2 = RS_Clip(theme_2, [1], 4, theme_1).pitch_similar_motion(5).solution() << Name("Similar")
    (theme_1 + theme_2) * 2 << Name("Similar Lines") >> Plot(block=True)

else:

    theme_2 = theme_1 - Octave(1) << Channel(2)
    final_composition = theme_1 + theme_2
    final_composition = RS_Clip(final_composition, [1], 4, theme_1).mask(Channel(2)).pitch_similar_motion(5).unmask().solution()
    final_composition * 2 << Name("Similar Lines") >> Plot(block=True)

