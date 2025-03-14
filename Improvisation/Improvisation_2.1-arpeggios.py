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
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

# https://youtu.be/1v578xNBDyY?si=_eveiFQ4K4cfyhuB

# Global Staff setting up
defaults << Tempo(110)

tonic_key = Tonic("C")

chromatic_notes = Cluster(tonic_key, [0.0, 1.0, 2.0, 3.0], 1/4) * 1
chromatic_notes >> Decompose()
chromatic_notes /= 2
chromatic_notes >> Beat(0) >> Arpeggiate("Up")
chromatic_notes >> Beat(1) >> Arpeggiate("Down")

chromatic_notes >> Play()
