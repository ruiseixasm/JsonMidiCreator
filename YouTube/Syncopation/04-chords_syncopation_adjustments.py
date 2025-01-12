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
staff << Tempo(115)     # Same tempo than the video tutorial

# https://youtu.be/7rhZAXjhPzI?si=7qEpDmaWQ80skir2



hi_hat: Seq = Nt(Dur(staff % Quant()), DrumKit("Hi-Hat")) * 16 << NotEqual(Step(0))**Velocity(70)
hi_hat *= 4     # 4 measures long
# hi_hat << Disable()
# hi_hat >> Play()

kick: Seq = Nt(Dur(staff % Quant()), DrumKit("Drum"), Stackable(False)) * 4 + Iterate(Beats(1))
kick *= 4       # 4 measures long
kick << Vel(80) # less pronounced kick
# kick << Disable()
# kick >> Play()

clap: Seq = Nt(Dur(staff % Quant()), DrumKit("Clap"), Stackable(False)) * 2 + Iterate(Beats(1)) + Beats(1)
clap *= 4       # 4 measures long
# clap << Disable()
# clap >> Play()

print(f"Hi-Hat length:  {hi_hat % Length() % float()}")
print(f"Kick length:    {kick % Length() % float()}")
print(f"Clap length:    {clap % Length() % float()}")

no_syncopation: Seq = hi_hat + kick + clap
no_syncopation >> Play()
# no_syncopation * 2 >> Play()


base_line: Seq = Nt(dotted_eight) * Measures(4) # Tonic note E in E minor (see Key Signature setting above)
base_line << Octave(1)  # Sets it as a Base line, lower Octave
base_line << Velocity(70)   # Reduces the velocity to make it less prominent
base_line[0] % str() >> Print() # Prints the real key being played
# base_line << Disable()

syncopation_1: Seq = no_syncopation + (base_line + Step(1) << 1/16)
# syncopation_1 >> Play()
# print("Delay for 0.5 seconds")
# time.sleep(0.5)

chords: Seq = Chord() * 4 << Foreach(1, 5, 6, 4)    # Sets Chords Degree
chords -= NotEqual(Measure(0))**Octave(1)
chords -= Octave(1)
chords *= 4
chords << Velocity(80)  # Chords tend to be loud, so they need to be softened

# Adjust Chords duration to 1/16
chords << Duration(1/16)
# Duplicate the pattern to repeat it at 1 Beat forward
chords << Iterate(2)**Measures()

# chords % Length() >> Print()

repeated_chords: Seq = Sequence()
for step in range(16*2//3 + 1):
    moved_chords: Seq = Step(step * 3) >> chords.copy()
    repeated_chords += moved_chords
# Make it shorter to fit in x4 composition
repeated_chords = repeated_chords.sort() / 2
# repeated_chords >> Play()

# chords << Disable()
# chords >> Play()

# syncopation_1 >> Play()
# print("Delay for 0.5 seconds")
# time.sleep(0.5)
# syncopation_1 * 4 >> Play()

syncopation_2: Seq = syncopation_1 * 4 + repeated_chords # x4 because chords are 4x longer than the original syncopation
# syncopation_2 >> Play()

# Move forward 1/16 note (a step)
syncopation_3: Seq = Sequence()
for _ in range(2):
    repeated_chords += Step(1)
    syncopation_3 = syncopation_1 * 4 + repeated_chords
    # syncopation_3 >> Play()

lead_notes: Seq = Note() * repeated_chords.len()
lead_notes << Foreach(repeated_chords)
lead_notes << Equal(Degree(5))**Degree(7) << Equal(6)**5
lead_notes += Octave(1)
# lead_notes += Degree(4)
# lead_notes >> Play()

syncopation_4: Seq = syncopation_3 + lead_notes
# syncopation_4.getPlaylist()
# syncopation_4 >> Play()

print(c.profiling_timer)
