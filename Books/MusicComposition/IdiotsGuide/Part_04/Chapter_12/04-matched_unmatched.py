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

rest_play = (R(), P)
defaults << "bb"
Key() % str() >> Print()    # Returns the tonic key (I)

matched_phrases = \
    (Note() * 4 << Nth(1, 2)**Loop(dotted_quarter, eight)         << Loop(1, 3, 2, 1)**Degree()) + \
    (Note() * 3 << Loop(dotted_quarter, eight, half)              << Loop(-3, 1, -4)**Degree()) + \
    (Note() * 4 << Loop(dotted_quarter, eight, quarter, quarter)  << Loop(2, 5, 4, 3)**Degree()) + \
    (Note() * 3 << Loop(dotted_quarter, eight, half)              << Loop(3, 2, 1)**Degree()) >> S
matched_phrases % Equal(M1, M2) >> Slur()
matched_phrases % Equal(M3, M4) >> Slur(0.99)
matched_phrases % NoteValue() >> Print(0)
matched_phrases >> rest_play

unmatched_phrases = \
    (Note() * 4 << Nth(1, 2)**Loop(dotted_quarter, eight) << Loop(1, 3, 2, 1)**Degree()) + \
    (Note() * 3 << Loop(dotted_quarter, eight, half)      << Loop(-3, 1, -4)**Degree()) + \
    (Note() * 4 << Loop(half, eight, eight, quarter)      << Loop(-3, -4, -3, 1)**Degree()) + \
    (Note() * 1 << whole                                     << Degree(2)) >> S
unmatched_phrases % Equal(M1, M2) >> Slur()
unmatched_phrases % Equal(M3, M4) >> Slur()
unmatched_phrases % NoteValue() >> Print(0)
unmatched_phrases >> rest_play
