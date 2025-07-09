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
settings << Tempo(120) << Measures(7)

# All Sharps(#) of the Major Scale on the Circle of Fifths
clip = Note("C", NoteValue(0), NoteValue(4), Velocity(85), Gate(1)) * 8 + Iterate()**0
clip >> Play(True)

# Global Staff setting up
settings << KeySignature(1)
clip >> Play(True)
settings << KeySignature(6)
clip >> Play()
settings << KeySignature(7)
clip >> Play()

settings << KeySignature()
clip += 1
clip >> Play()
