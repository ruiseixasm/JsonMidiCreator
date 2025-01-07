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
staff << KeySignature(+1, Minor())  # Sets the default Key Signature configuration as E minor

# https://youtu.be/7rhZAXjhPzI?si=7qEpDmaWQ80skir2

hi_hat: Seq = Nt(Dur(staff % Quant()), DrumKit("Hi-Hat")) * 16 << NotEqual(Step(0))**Velocity(70)
hi_hat *= 4     # 4 measures long
# hi_hat >> Play()

kick: Seq = Nt(Dur(staff % Quant()), DrumKit("Drum"), Stackable(False)) * 4 + Iterate(Beats(1))**Position()
kick *= 4       # 4 measures long
kick << Vel(80) # less pronounced kick
# kick >> Play()

clap: Seq = Nt(Dur(staff % Quant()), DrumKit("Clap"), Stackable(False)) * 2 + Iterate(Beats(1))**Position() + Beats(1)
clap *= 4       # 4 measures long
# clap >> Play()

no_syncopation: Seq = hi_hat + kick + clap
# no_syncopation * 2 >> Play()


base_line: Seq = Nt(dotted_eight) * Measures(4) # Tonic note E in E minor (see Key Signature setting above)
base_line << Octave(1)  # Sets it as a Base line, lower Octave
base_line << Velocity(70)   # Reduces the velocity to make it less prominent
base_line[0] % str() >> Print() # Prints the real key being played

syncopation: Seq = no_syncopation + (base_line + Step(1) << 1/16)
# syncopation >> Play()
print("Delay for 0.5 seconds")
time.sleep(0.5)

chords: Seq = Chord() * 4 << Foreach(1, 5, 6, 4)    # Sets Chords Degree
# chords >> Play()
chords -= NotEqual(Measure(0))**Octave(1)
chords *= 4
chords >> Play()


