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

staff << TimeSignature(3, 4) << KeySignature("#")
outline = Note("D") * 2 + Note("E") + Note("G") + Note("C") << Dotted(1/2) << Octave(5)
outline += Note("B", Dotted(1/2)) * 3 - Iterate()**0
outline >> Stack()
outline >> Play()

flesh = Note(Measure(0), Beat(1)) * 2 + Note(Measure(1), Beat(1), 1/2) + Note(Measure(2), Beat(1)) * 2 + Note(Measure(3), Beat(1), 1/2)
flesh += Note(Measure(4), Beat(2)) + Note(Measure(5), Beat(2)) + Note(Measure(6), Beat(2))
flesh - 1 + (5, 7, 5, 8, 10, 5, 6, 5, 4)
outline << Nth(1, 2, 3, 4)**Duration(1/4) << Nth(5, 6, 7)**Duration(1/2)
outline + flesh >> Link() >> Play()

embelishing = Note("G", Measure(0), Beat(1), 1/8) * 4 + Iterate()**0
embelishing += Note("G", Measure(1), Beat(1)) * 2
embelishing += Note("C", 5, Measure(2), Beat(1), 1/8) * 4 + Iterate()**0
embelishing += Note("G", Measure(3), Beat(1)) * 2
embelishing += Note("D", 5, Measure(4), Beat(1), 1/8) * 4 - Iterate()**0
embelishing += Note("C", 5, Measure(5), Beat(1), 1/8) * 4 - Iterate()**0
embelishing += Note("B", Measure(6), Beat(1), 1/8) * 4 - Iterate()**0
full = outline + embelishing >> Link()
full << Get(Length())**Duration()
full >> Play()

# ((full | Measure(0)) >> Print()) % Length() >> Print(0)

staff << TimeSignature(9, 8) << KeySignature(2) << Tempo(180)
outline: Sequence = Note("B", Dotted(1/4)) * 3 + Nth(2)**2
outline *= 4
outline + Equal(Measure(1), Measure(3))**2 + Equal(Measure(2))**4
(outline - outline % Last() | outline % Last()) << Dotted(1/2)
outline << Equal(Measure(2))**Equal(Beat(6))**KeyNote("A", 4)
outline >> Play()

outline -= outline | Beat(0)
embelishing = Note("B", Dotted(1/8)) + Note("F", 1/16) + Note("B", 1/8) >> Stack()
embelishing += (Measure(1) >> embelishing) + (Measure(2) >> embelishing) + (Measure(3) >> embelishing)
embelishing + Equal(Measure(1), Measure(3))**2 + Equal(Measure(2))**4

(outline + embelishing >> Link() >> Play() | Measure(3)) % Length() >> Print(0)