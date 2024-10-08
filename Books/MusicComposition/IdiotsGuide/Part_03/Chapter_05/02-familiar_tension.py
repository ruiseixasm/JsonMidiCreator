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

familiar_bar1 = Note("F", 5) * 4 - Iterate()**0
familiar_bar2 = Note("B", Dotted(1/2)) + Note("F", 5)
familiar_bar3 = Note("E", 5) + Note("D", 5) + Note("G") + Note("A")
familiar_bar4 = Note("B", NoteValue(1))

# familiar_bar1 >> familiar_bar2 >> familiar_bar3 >> familiar_bar4 >> Play()


tension = Note("B", 5) * 12 << Nth(7)**NoteValue(1/2) >> Stack() << Equal(Measure(3))**NoteValue(1) >> Stack()
tension + (1, 0, 1, 2, 3, 5, 4, 3, 2, 1, 0, 1)
tension >> Play()

staff << KeySignature("#")
center = Note("B", 5) * 11 << (1/2, None, None, 1/2, None, None, None, None, None, None, 1/1) >> Stack()

(center | Measure(0)) + (0, -2, -1)
(center | Measure(1)) + (0, 2, 1)
(center | Measure(2)) + (0, -1, -2, -1)
center >> Play()

staff << KeySignature("b") << Tempo(90)
repeat_1 = Note("B", 5) * 5 + (-1, 0, -1, -2, -1) << (1/8, 1/8)
repeat_2 = Note("B", 5) * 4 + (-1, 0, -1, -2) << (1/8, 1/8, 1/4, 1/2)
repeat_3 = Note("B", 5) * 5 + (-1, 0, -1, -2, -3) << (1/8, 1/8)
repeat_4 = Note("B", 5) - 2 << 1/1

repeat_1 >> repeat_2 >> repeat_3 >> repeat_4 >> Play()

