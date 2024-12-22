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

staff << KeySignature("bbb")

slow_paced: Sequence = Note("E", 1/2) * 7 >> Link() << Foreach(6, 5, 1, 3, 6, 5, 2)**Degree()
slow_paced >> Rest() >> Play()

embellishing: Sequence = \
    Note("E", Degree("IV"), Position(Measure(0) + Dotted(1/4))) + \
    Note("E", Degree("ii"), Position(Measure(1) - NoteValue(1/8))) + \
    Note("E", Degree("ii"), Position(Measure(1) + NoteValue(1/4))) + \
    Note("E", Degree("IV"), Position(Measure(1) + NoteValue(1/4 + 1/8))) + \
    Note("E", Degree("V"), Position(Measure(2) - NoteValue(1/8))) + \
    Note("E", Degree("viiº"), Position(Measure(2) + NoteValue(1/4))) + \
    Note("E", Degree("vi"), Position(Measure(2) + NoteValue(1/4 + 1/8))) + \
    Note("E", Degree("iii"), Position(Measure(3) - NoteValue(1/8)))
slow_paced + embellishing >> Link() >> Rest() >> Play()

variation: Sequence = Note("E") * 10
variation << Foreach(
        Measure(0, Step(2)),
        Measure(0, Step(4)),
        Measure(0, Step(10)),
        Measure(0, Step(12)),
        Measure(1, Step(4)),
        Measure(1, Step(10)),
        Measure(1, Step(12)),
        Measure(2, Step(10)),
        Measure(2, Step(12)),
    )**Position() << Foreach(
        7, 6, 6, 5, 2, 4, 3, 6, 5
    )**Degree()
slow_paced + variation >> Link() >> Rest() >> Play()
