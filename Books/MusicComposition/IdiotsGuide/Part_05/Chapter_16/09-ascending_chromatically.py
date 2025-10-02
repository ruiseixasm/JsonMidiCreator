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


settings << Tempo(160) << Folder("Books/MusicComposition/IdiotsGuide/Part_05/Chapter_16/")

melody_up = Note(Dotted(1/4)) / Note(1/8) / 8 << Foreach("1", "3")
melody_up += Mux(2)**Iterate()**RootKey()
melody_up * 4 << Title("Ascending Chromatically") >> Plot(block=False)

melody_down = Note(Dotted(1/4)) / Note(1/8) / 8 << Foreach("1", "3")
melody_down -= Mux(2)**Iterate()**RootKey()
melody_down * 4 << Title("Descending Chromatically") >> Plot(block=False)

melody_zig = melody_up * [0, -1, 2, -1] + melody_down * [-1, 1, -1, 3]
melody_zig * 4 << Title("Zig Zag Chromatically") >> Plot(block=False)

melody_super = Note(Dotted(1/4)) / Note(1/8) / 8 * 2 << Foreach("1", "3")
melody_super += Mux(2)**Iterate()**RootKey()
melody_super % [Octave(), int()] >> Print()
melody_super * 2 << Title("Super Ascending") >> Plot(block=False)

melody_minor = Note(Dotted(1/4)) / Note(1/8) / 8 * 2 << Foreach("1", "3") << Minor()
melody_minor += Mux(2)**Iterate()**RootKey()
melody_minor % [Octave(), int()] >> Print()
melody_minor * 2 << Title("Minor Ascending") >> Plot()

