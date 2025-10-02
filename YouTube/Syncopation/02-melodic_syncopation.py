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
settings << KeySignature(+1, Minor())  # Sets the default Key Signature configuration as E minor

# https://youtu.be/7rhZAXjhPzI?si=7qEpDmaWQ80skir2

hi_hat: Clip = Nt(Dur(settings % Quant()), DrumKit("Hi-Hat")) * 16 << IsNot(Step(0))**Velocity(70)
hi_hat *= 4     # 4 measures long
# hi_hat >> Play()

kick: Clip = Nt(Dur(settings % Quant()), DrumKit("Drum"), Stackable(False)) * 4 + Iterate(Beats(1))**Position()
kick *= 4       # 4 measures long
kick << Vel(80) # less pronounced kick
# kick >> Play()

clap: Clip = Nt(Dur(settings % Quant()), DrumKit("Clap"), Stackable(False)) * 2 + Iterate(Beats(1))**Position() + All()**Beats(1)
clap *= 4       # 4 measures long
# clap >> Play()

no_syncopation: Clip = hi_hat + kick + clap
# no_syncopation * 2 >> Play()


base_line: Clip = Nt(dotted_eight) * Measures(4) # Tonic note E in E minor (see Key Signature setting above)
base_line << Octave(1)  # Sets it as a Base line, lower Octave
base_line << Velocity(70)   # Reduces the velocity to make it less prominent
base_line[0] % str() >> Print() # Prints the real key being played

syncopation_1: Clip = no_syncopation + base_line
syncopation_1 >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

syncopation_2: Clip = no_syncopation + (base_line << 1/16)
syncopation_2 >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

syncopation_3: Clip = no_syncopation + (base_line + All()**Step(1) << 1/16)
syncopation_3 >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

syncopation_4: Clip = no_syncopation + (base_line + All()**Step(2) << 1/16)
syncopation_4 >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

syncopation_5: Clip = no_syncopation + (base_line + All()**Step(3) << 1/16)
syncopation_5 >> Play(1)
print("Delay for 0.5 seconds")
time.sleep(0.5)

# Best outcome with some extra variation
syncopation_6: Clip = no_syncopation + (base_line + Every(5)**Step(1) << 1/16)
syncopation_6 >> Play(1)
print("Delay for 0.5 seconds")
time.sleep(0.5)

# Best outcome with some extra variation
syncopation_7: Clip = no_syncopation + (base_line + Every(4)**Step(1) + Every(5)**Step(1) << 1/16)
syncopation_7 >> Play(1)
print("Delay for 0.5 seconds")
time.sleep(0.5)

