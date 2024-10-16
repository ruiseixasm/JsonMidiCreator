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

staff << KeySignature("b")

approach: Sequence = (Note("C", 5, Dotted(1/2)) + Note("G")) * 4
approach -= approach % Last()
approach << Equal(Measure(3))**NoteValue(1)
approach - Equal(Measure(1))**2 - Equal(Measure(2), Measure(3))**Equal(Beat(0))**4
approach >> Play()

(approach | Measure(0) | Beat(3)) + 4
(approach | Measure(1) | Beat(3)) + 4
(approach | Measure(2) | Beat(3)) - 3
approach >> Play()

four_steps: Sequence = Note("C", 1/16) * 4 - Increment()
approach |= Beat(0)
approach = approach \
            + (four_steps.copy() + Octave(1) + 2 << Position(Measure(0), Beat(3)) >> Stack()) \
            + (four_steps.copy() + Octave(1) << Position(Measure(1), Beat(3)) >> Stack()) \
            + (four_steps.copy() + 2 << Position(Measure(2), Beat(3)) >> Stack() >> Reverse()) \
        >> Link()
approach >> Play(1)
