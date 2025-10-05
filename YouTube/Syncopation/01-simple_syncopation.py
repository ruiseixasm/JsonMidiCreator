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

rest_play = (R(), P)
settings << KeySignature(-1)   # Sets the default Key Signature configuration

# Note() >> Play()    # tests playing

# https://youtu.be/7rhZAXjhPzI?si=7qEpDmaWQ80skir2

hi_hat: Clip = Note(Duration(settings % Quant()), DrumKit("Hi-Hat")) * 16 << IsNot(Step(0))**Velocity(70)
hi_hat *= 4     # 4 measures long
# hi_hat >> Play()

kick: Clip = Note(Duration(settings % Quant()), DrumKit("Drum"), Stackable(False)) * 4 + Iterate(Beats(1))**Position()
kick *= 4       # 4 measures long
# kick >> Play()

clap: Clip = Note(Duration(settings % Quant()), DrumKit("Clap"), Stackable(False)) * 2 + Iterate(Beats(1))**Position() + Beats(1)
clap *= 4       # 4 measures long
# clap >> Play()

no_syncopation: Clip = hi_hat + kick + clap
# no_syncopation * 2 >> Play()


wood_block: Clip = Note(DrumKit("Wood Block"), dotted_eight) * Measures(4) # (3/2 * 1/8) * 21 = 3.9375 = 63/16
# wood_block >> Play()

syncopation_1: Clip = no_syncopation + wood_block
syncopation_1 >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

syncopation_2: Clip = no_syncopation + (wood_block << 1/16)
syncopation_2 >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

syncopation_3: Clip = no_syncopation + (wood_block + All()**Step(1) << 1/16)
syncopation_3 >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

syncopation_4: Clip = no_syncopation + (wood_block + All()**Step(2) << 1/16)
syncopation_4 >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

syncopation_5: Clip = no_syncopation + (wood_block + All()**Step(3) << 1/16)
syncopation_5 >> Play(1)
print("Delay for 0.5 seconds")
time.sleep(0.5)

# Best outcome with some extra variation
syncopation_6: Clip = no_syncopation + (wood_block + Every(5)**Step(1) << 1/16)
syncopation_6 >> Play(1)
print("Delay for 0.5 seconds")
time.sleep(0.5)

# Best outcome with some extra variation
syncopation_7: Clip = no_syncopation + (wood_block + Every(4)**Step(1) + Every(5)**Step(1) << 1/16)
syncopation_7 >> Play(1)
print("Delay for 0.5 seconds")
time.sleep(0.5)

