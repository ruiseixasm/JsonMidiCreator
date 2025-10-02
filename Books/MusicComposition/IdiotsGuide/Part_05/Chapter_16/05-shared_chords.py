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


settings << Folder("Books/MusicComposition/IdiotsGuide/Part_05/Chapter_16/")

chords = Chord(1/2, Octave(3)) / 3 << Last()**(1/1)
chords *= 2
chords << Foreach("1", "6", "2", "6", "4", "1")
chords << Greater(Measure(1))**KeySignature(-1)

melody = Chord(1/2, Octave(3)) / 3 << Last()**(1/1)
melody *= 2
melody << Foreach("5", "1", "6", "3", "4", "5")
melody << Greater(Measure(1))**KeySignature(-1)


chords % [Key(), str()] >> Print()
melody % [Key(), str()] >> Print()

(chords + melody) * 4 << Title("Shared Chords") >> Plot()

