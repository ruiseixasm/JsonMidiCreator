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
familiar_bar4 = Note("B", Duration(1/1))
familiar_bar1 >> familiar_bar2 >> familiar_bar3 >> familiar_bar4 >> Play()


tension = Note("B", 5) * 12 << Nth(7)**Duration(1/2) >> Stack() << Match(Measures(3))**Duration(1/1) >> Stack()
tension + Foreach(1, 0, 1, 2, 3, 5, 4, 3, 2, 1, 0, 1)
tension >> Play()


settings << KeySignature("#")
center = Note("B", 5) * 11 << Foreach(1/2, None, None, 1/2, None, None, None, None, None, None, 1/1) >> Stack()

(center | Measures(0)) + Foreach(0, -2, -1)
(center | Measures(1)) + Foreach(0, 2, 1)
(center | Measures(2)) + Foreach(0, -1, -2, -1)
center >> Play()


settings << KeySignature("b") << Tempo(90)
repeat_1 = Note("B", 5) * 5 + Foreach(-1, 0, -1, -2, -1) << Foreach(1/8, 1/8)
repeat_2 = Note("B", 5) * 4 + Foreach(-1, 0, -1, -2) << Foreach(1/8, 1/8, 1/4, 1/2)
repeat_3 = Note("B", 5) * 5 + Foreach(-1, 0, -1, -2, -3) << Foreach(1/8, 1/8)
repeat_4 = Note("B", 5) - 2 << 1/1
(repeat_1, repeat_2, repeat_3) >> repeat_4 >> Play()


form_1 = Note("B", 5, Gate(1)) * 6 << Nth(1, 6)**Duration(1/1) << Nth(2, 3, 4, 5)**Duration(1/2) << Nth(6)**Gate(0.9) >> Stack()
form_1 + Foreach(0, 3, 2, 1, 2)

form_2 = (form_1 | Match(Measures(0), Measures(3))) >> Copy()
form_2 = form_2 + Note("B", 5, Measures(1), Gate(1)) * 5 >> Sort()
form_2 + Foreach(-1, 0, -1, -2, -1, 0, -1)
form_2 << Nth(6)**Duration(1/1) >> Stack()

form_3 = Note("B", 5, Gate(1)) * 10 << Nth(1, 8, 9)**Duration(1/2) << Nth(10)**(Duration(1/1), Gate(0.9))
form_3 + Foreach(-2, 5, 4, 3, 2, 1, -1, 0, 1, 2)

form_4 = Note("B", 5, Gate(1)) * 8 << Nth(6, 7)**Duration(1/2) << Nth(1, 8)**(Duration(1/1)) << Nth(8)**(Gate(0.9))
form_4 + Foreach(3, 2, 1, -2, -1, 0, -3, -2)

settings << KeySignature("#") << Tempo(125)
form_1 >> form_2 >> form_3 >> form_4 >> Play()


out_range = Note("F", 1/2) + Note("A") + Note("B") + (Note("C") + Note("F") + Note("G") + Note("A") + Note("B", 1/2) + Note("F", 1/2) + Note("G", 1/1) << 5)
settings << KeySignature("bb")
out_range >> Stack() >> Play()
