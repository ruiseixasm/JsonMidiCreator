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

original_phrase: Sequence = Note("B") * 5 + Foreach(2, -1, 0, 2, 1) >> Link(True)
original_phrase >> Rest() >> Play()

variation_a: Sequence = original_phrase.copy() << Equal(Measure(0))**NoteValue(1/8)
(variation_a | Measure(0)) >> Stack()
variation_a + Note("C", 5, 1/2, Gate(1), Position(Beat(2))) >> Link(True)

variation_b: Sequence = original_phrase.copy() << Equal(Measure(0))**Foreach(1/8, 1/8, 1/2, 1/4)**NoteValue() >> Stack()
variation_c: Sequence = original_phrase.copy() << Equal(Measure(0))**Foreach(1/4, 1/2, 1/8, 1/8)**NoteValue() >> Stack()
variation_d: Sequence = original_phrase.copy() << Equal(Measure(0))**Foreach(1/4, 1/8, 1/8, 1/2)**NoteValue() >> Stack()

variation_e: Sequence = Rest() + (original_phrase.copy() << Equal(Measure(0))**NoteValue(1/8)) >> Stack()

variation_f: Sequence = ((original_phrase | Measure(0) | Less(Beat(3))).copy() << Gate(1)) + original_phrase << Equal(Measure(0))**NoteValue(1/8) >> Sort()
variation_f = Rest(1/8) + variation_f

variation_a >> variation_b >> variation_c >> variation_d >> variation_e >> variation_f >> Rest() >> Play()
