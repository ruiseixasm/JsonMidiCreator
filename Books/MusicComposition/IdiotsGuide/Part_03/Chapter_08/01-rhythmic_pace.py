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

simple_phrase: Clip = Note("B") * 3 + Nth(2)**1 >> Link()
simple_phrase >> Rest() >> Play()

dotted_quarter: Clip = simple_phrase.copy() << Foreach(Dotted(1/4), 1/8, 1/2) >> Stack() >> Link()
dotted_quarter >> Rest() >> Play()

off_beat: Clip = simple_phrase.copy() << Nth(2)**Position(Duration(1/8)) >> Link()
off_beat >> Rest() >> Play()

speeding_up: Clip = dotted_quarter.copy() - Nth(2, 3)**Position(1/4) >> Link()
speeding_up >> Rest() >> Play()

settings << KeySignature("#")

original_phrase: Clip = Note("B") * 5 + Foreach(2, -1, 0, 2, 1) >> Link()
original_phrase >> Rest() >> Play()

variation_a: Clip = original_phrase.copy() << Match(Measures(0))**Duration(1/8)
(variation_a | Measures(0)) >> Stack()
variation_a + Note("C", 5, 1/2, Gate(1), Position(Beats(2))) >> Link()

variation_b: Clip = original_phrase.copy() << Match(Measures(0))**Foreach(1/8, 1/8, 1/2, 1/4)**Duration() >> Stack()
variation_c: Clip = original_phrase.copy() << Match(Measures(0))**Foreach(1/4, 1/2, 1/8, 1/8)**Duration() >> Stack()
variation_d: Clip = original_phrase.copy() << Match(Measures(0))**Foreach(1/4, 1/8, 1/8, 1/2)**Duration() >> Stack()

variation_e: Clip = Rest() + (original_phrase.copy() << Match(Measures(0))**Duration(1/8)) >> Stack()

variation_f: Clip = ((original_phrase | Measures(0) | Bellow(Beats(3))).copy() << Gate(1)) + original_phrase << Match(Measures(0))**Duration(1/8) >> Sort()
variation_f = Rest(1/8) + variation_f

variation_a >> variation_b >> variation_c >> variation_d >> variation_e >> variation_f >> Rest() >> Play()
