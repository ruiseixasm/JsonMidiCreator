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

simple_phrase: Sequence = Note("B") * 3 + Nth(2)**1 >> Link(True)
simple_phrase >> Rest() >> Play()

dotted_quarter: Sequence = simple_phrase.copy() << Foreach(Dotted(1/4), 1/8, 1/2) >> Stack() >> Link(True)
dotted_quarter >> Rest() >> Play()

off_beat: Sequence = simple_phrase.copy() << Nth(2)**Position(NoteValue(1/8)) >> Link(True)
off_beat >> Rest() >> Play()

speeding_up: Sequence = dotted_quarter.copy() - Nth(2, 3)**Position(1/4) >> Link(True)
speeding_up >> Rest() >> Play()

staff << KeySignature("#")

simple_phrase = Note("B") * 5 + Foreach(2, -1, 0, 2, 1) >> Link(True)
simple_phrase >> Rest() >> Play()
