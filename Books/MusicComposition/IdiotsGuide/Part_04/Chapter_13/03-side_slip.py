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
settings << "#" << 120
Key() % str() >> Print()    # Returns the tonic key (I)

motif = Note() * 6 << Foreach(quarter, eight, eight, dotted_quarter, eight, whole) >> Stack()
motif << Foreach(-3, 1, 2, 3, 2, -3)**Degree()

side_slipping = motif >> (motif % Copy() + 1.0 << Nth(1,6)**Natural()) >> motif  # up a half-step
side_slipping >> rest_play
# Key Scales implementation needs to be more developed (disabled key signature with Key Scale)
side_slipping = motif >> (motif % Copy() + 1.0 << Scale("Major")) >> motif  # up a half-step
side_slipping >> rest_play
