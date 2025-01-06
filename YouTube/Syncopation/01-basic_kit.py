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
src_path = os.path.join(os.path.dirname(__file__), '../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

rest_play = (R, P)
staff << KeySignature(-1)   # Sets the default Key Signature configuration

# Note() >> Play()    # tests playing

# https://youtu.be/7rhZAXjhPzI?si=7qEpDmaWQ80skir2

# Play a Maracas 16 times
maracas: Sequence = Note(DrumKit("Maracas"), sixteenth) * 16
# maracas >> Play()


hi_hat: Seq = Nt(Dur(staff % Quant()), DrumKit("Hi-Hat")) * 16
hi_hat >> Play()
