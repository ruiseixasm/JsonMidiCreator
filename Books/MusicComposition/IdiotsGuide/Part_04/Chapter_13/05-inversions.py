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

rest_play = ( Rest(), Play())
settings << "#" << 90
Key() % str() >> Print()    # Returns the tonic key (I)

motif = Note() * 6 << Foreach(quarter, eight, eight, dotted_quarter, eight, whole) >> Stack()
motif << Foreach(-3, 1, 2, 3, 2, -3)**Degree()

# Flips three degrees from -3 to +3 up reversion by 3 Degrees up and 3 Degrees down
melodic_inversion = motif >> (motif % Copy() << Get(Degree())**Add(3)**Multiply(-1)**Subtract(3))
melodic_inversion >> rest_play

# Flips three degrees from -3 to +3 up needs to go 6 - 1 degrees down
melodic_inversion = motif >> (motif % Copy() << Get(Degree())**Multiply(-1)) - Degree(6 - 1)
melodic_inversion >> rest_play

# Floats multiplication on Key works in a Chromatic fashion while Integer works by Steps
mirror_inversion = motif >> motif % Copy() - Get(Pitch())**Get(int())**Subtract(Pitch(E) % int())**Multiply(2.0)
mirror_inversion >> rest_play

# Integer multiplication on Pitch ignores KeySignature sharps and flats while Floats don't
mirror_inversion = motif >> motif % Copy() - Get(Pitch())**Subtract(Pitch(E))**Multiply(2)
mirror_inversion >> rest_play


contour_inversion = melodic_inversion - Bellow(Pitch(E))**Bellow(B4)**1 + Bellow(Pitch(E))**Match(B4)**1
contour_inversion >> rest_play

