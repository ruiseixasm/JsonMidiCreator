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

settings << KeySignature("bbb")

slow_paced: Clip = Note("E", 1/2) * 7 >> Link() << Foreach(6, 5, 1, 3, 6, 5, 2)**Degree()
slow_paced >> Rest() >> Play()

embellishing: Clip = \
    Note("E", Degree("IV"), Position(Measures(0) + Dotted(1/4))) + \
    Note("E", Degree("ii"), Position(Measures(1) - Duration(1/8))) + \
    Note("E", Degree("ii"), Position(Measures(1) + Duration(1/4))) + \
    Note("E", Degree("IV"), Position(Measures(1) + Duration(1/4 + 1/8))) + \
    Note("E", Degree("V"), Position(Measures(2) - Duration(1/8))) + \
    Note("E", Degree("viiº"), Position(Measures(2) + Duration(1/4))) + \
    Note("E", Degree("vi"), Position(Measures(2) + Duration(1/4 + 1/8))) + \
    Note("E", Degree("iii"), Position(Measures(3) - Duration(1/8)))
slow_paced + embellishing >> Link() >> Rest() >> Play()

variation: Clip = Note("E") * 10
variation << Foreach(
        Measures(0, Steps(2)),
        Measures(0, Steps(4)),
        Measures(0, Steps(10)),
        Measures(0, Steps(12)),
        Measures(1, Steps(4)),
        Measures(1, Steps(10)),
        Measures(1, Steps(12)),
        Measures(2, Steps(10)),
        Measures(2, Steps(12)),
    )**Position() << Foreach(
        7, 6, 6, 5, 2, 4, 3, 6, 5
    )**Degree()
slow_paced + variation >> Link() >> Rest() >> Play()
