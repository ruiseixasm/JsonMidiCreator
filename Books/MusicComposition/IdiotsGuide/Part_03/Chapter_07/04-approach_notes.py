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

settings << KeySignature("b")

approach: Clip = (Note("C", 5, Dotted(1/2)) + Note("G")) * 4
approach -= approach[-1]
approach << Equal(Measures(3))**Duration(1/1)
approach - Equal(Measures(1))**2 - Equal(Measures(2), Measures(3))**Equal(Beats(0))**4
approach >> Play()

(approach | Measures(0) | Beats(3)) + 4
(approach | Measures(1) | Beats(3)) + 4
(approach | Measures(2) | Beats(3)) - 3
approach >> Play()

four_steps: Clip = Note("C", 1/16) * 4 - Iterate()
approach >>= Beats(0)
approach = approach \
            + (four_steps.copy() + Octave(1) + 2 << Position(Measures(0), Beats(3)) >> Stack()) \
            + (four_steps.copy() + Octave(1) << Position(Measures(1), Beats(3)) >> Stack()) \
            + (four_steps.copy() + 2 << Position(Measures(2), Beats(3)) >> Stack() >> Reverse()) \
        >> Link()
approach >> Play(1)
