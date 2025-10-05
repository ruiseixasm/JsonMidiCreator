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

rest_play = ( Rest(), P)
settings << KeySignature(+1, Minor())  # Sets the default Key Signature configuration as E minor

# https://youtu.be/7rhZAXjhPzI?si=7qEpDmaWQ80skir2



hi_hat: Clip = Note(Duration(settings % Quant()), DrumKit("Hi-Hat")) * 16 << IsNot(Step(0))**Velocity(70)
hi_hat *= 4     # 4 measures long
# hi_hat << Disable()
# hi_hat >> Play()

kick: Clip = Note(Duration(settings % Quant()), DrumKit("Drum"), Stackable(False)) * 4 + Iterate(Beats(1))
kick *= 4       # 4 measures long
kick << Velocity(80) # less pronounced kick
# kick << Disable()
# kick >> Play()

clap: Clip = Note(Duration(settings % Quant()), DrumKit("Clap"), Stackable(False)) * 2 + Iterate(Beats(1)) + Beats(1)
clap *= 4       # 4 measures long
# clap << Disable()
# clap >> Play()

no_syncopation: Clip = hi_hat + kick + clap
# no_syncopation * 2 >> Play()


base_line: Clip = Note(dotted_eight) * Measures(4) # Tonic note E in E minor (see Key Signature setting above)
base_line << Octave(1)  # Sets it as a Base line, lower Octave
base_line << Velocity(70)   # Reduces the velocity to make it less prominent
base_line[0] % str() >> Print() # Prints the real key being played
# base_line << Disable()
# base_line >> Play()

syncopation_1: Clip = no_syncopation + (base_line + Step(1) << 1/16)
# syncopation_1 >> Play()
# print("Delay for 0.5 seconds")
# time.sleep(0.5)

chords: Clip = Chord([]) * 4 << Foreach(1, 5, 6, 4)    # Sets Chords Degree
chords -= IsNot(Measure(0))**Octave(1)
chords -= Octave(1)
chords *= 4
chords << Velocity(80)  # Chords tend to be loud, so they need to be softened
# chords << Disable()
# chords >> Play()

# syncopation_1 >> Play()
# print("Delay for 0.5 seconds")
# time.sleep(0.5)
# syncopation_1 * 4 >> Play()

syncopation_2: Clip = syncopation_1 * 4 + chords # x4 because chords are 4x longer than the original syncopation
syncopation_2 >> Save("YouTube/Syncopation/save_chords_syncopation.json")
syncopation_2 >> Render("YouTube/Syncopation/save_chords_syncopation.mid")
syncopation_2 >> Play()


