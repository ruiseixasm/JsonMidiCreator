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

settings << TimeSignature(3, 4) << KeySignature("#")
outline = Note("D") * 2 + Note("E") + Note("G") + Note("C") << Dotted(1/2) << Octave(5)
outline += Note("B", Dotted(1/2)) * 3 - Iterate()
outline >> Stack()
outline >> Play()

flesh = Note(Measures(0), Beats(1)) * 2 + Note(Measures(1), Beats(1), 1/2) + Note(Measures(2), Beats(1)) * 2 + Note(Measures(3), Beats(1), 1/2)
flesh += Note(Measures(4), Beats(2)) + Note(Measures(5), Beats(2)) + Note(Measures(6), Beats(2))
flesh - 1 + Foreach(5, 7, 5, 8, 10, 5, 6, 5, 4)
outline << Nth(1, 2, 3, 4)**NoteValue(1/4) << Nth(5, 6, 7)**NoteValue(1/2)
outline + flesh >> Link() >> Play()

embellishing = Note("G", Measures(0), Beats(1), 1/8) * 4 + Iterate()
embellishing += Note("G", Measures(1), Beats(1)) * 2
embellishing += Note("C", 5, Measures(2), Beats(1), 1/8) * 4 + Iterate()
embellishing += Note("G", Measures(3), Beats(1)) * 2
embellishing += Note("D", 5, Measures(4), Beats(1), 1/8) * 4 - Iterate()
embellishing += Note("C", 5, Measures(5), Beats(1), 1/8) * 4 - Iterate()
embellishing += Note("B", Measures(6), Beats(1), 1/8) * 4 - Iterate()
full = outline + embellishing >> Link()
full << Get(NoteValue())**NoteValue()
full >> Play()

# ((full | Measure(0)) >> Print()) % Duration() >> Print(0)

settings << TimeSignature(9, 8) << KeySignature(2) << Tempo(180)
outline: Clip = Note("B", Dotted(1/4)) * 3 + Nth(2)**2
outline *= 4
outline + Match(Measures(1), Measures(3))**2 + Match(Measures(2))**4
(outline - outline[-1] | outline[-1]) << Dotted(1/2)
outline << Match(Measures(2))**Match(Beats(6))**Pitch("A", 4)
outline >> Play()

outline -= outline | Beats(0)
embellishing = Note("B", Dotted(1/8)) + Note("F", 1/16) + Note("B", 1/8) >> Stack()
embellishing += (Measures(1) >> embellishing) + (Measures(2) >> embellishing) + (Measures(3) >> embellishing)
embellishing + Match(Measures(1), Measures(3))**2 + Match(Measures(2))**4

(outline + embellishing >> Link() >> Play() | Measures(3)) % NoteValue() >> Print(0)
