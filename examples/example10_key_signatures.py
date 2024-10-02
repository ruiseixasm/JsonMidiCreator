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


# Global Staff setting up
staff << Tempo(120) << Measure(7)

# All Sharps(#) of the Major Scale on the Circle of Fifths
sequence = Note("C") * 8 + Iterate()**Key() << NoteValue(4) << Velocity(85)
# sequence >> Play(True)

sequence += Key(1)
sequence >> Play()

# # Global Staff setting up
# staff << KeySignature(1)
# sequence >> Play(True)
# staff << KeySignature(6)
# sequence >> Play()
# staff << KeySignature(7)
# sequence >> Play()
