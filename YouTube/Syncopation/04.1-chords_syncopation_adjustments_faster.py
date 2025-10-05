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
settings << Tempo(115)     # Same tempo than the video tutorial

# https://youtu.be/7rhZAXjhPzI?si=7qEpDmaWQ80skir2



hi_hat: Clip = Note(Duration(settings % Quant()), DrumKit("Hi-Hat")) * 16 << IsNot(Step(0))**Velocity(70)
hi_hat *= 4     # 4 measures long
# hi_hat << Disable()
# hi_hat >> Play()

kick: Clip = Note(Duration(settings % Quant()), DrumKit("Drum"), Stackable(False)) * 4
kick += Iterate(Beats(1))
kick *= 4       # 4 measures long
kick << Vel(80) # less pronounced kick
# kick << Disable()
# kick >> Play()

clap: Clip = Note(Duration(settings % Quant()), DrumKit("Clap"), Stackable(False)) * 2
clap += Iterate(Beats(1))
clap += Beats(1)
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

base_line += Step(1)
base_line << 1/16
syncopation_1: Clip = no_syncopation + base_line
# syncopation_1 >> Play()
# print("Delay for 0.5 seconds")
# time.sleep(0.5)

chords: Clip = Chord([]) * 4 << Foreach(1, 5, 6, 4)    # Sets Chords Degree
chords -= IsNot(Measure(0))**Octave(1)
chords -= Octave(1)
chords *= 4
chords << Velocity(80)  # Chords tend to be loud, so they need to be softened

# Adjust Chords duration to 1/16
chords << Duration(1/16)
# Duplicate the pattern to repeat it at 1 Beat forward
chords << Iterate(2)**Measures()
chords % Length() % float() >> Print()  # Measures
repeated_chords: Clip = Clip()

for step in range(16*2//3 + 1):
    repeated_chords += chords
    Steps(3) >> chords

# Make it shorter to fit in x4 composition
repeated_chords.sort()
repeated_chords /= 2
# repeated_chords >> Play()

# chords << Disable()
# chords >> Play()

# syncopation_1 >> Play()
# print("Delay for 0.5 seconds")
# time.sleep(0.5)
# syncopation_1 * 4 >> Play()

syncopation_1_4: Clip = syncopation_1 * 4
syncopation_2: Clip = syncopation_1_4 + repeated_chords # x4 because chords are 4x longer than the original syncopation
# syncopation_2 >> Play()

c.profiling_timer.call_timer_a()

# Move forward 1/16 note (a step)
syncopation_3: Clip = Clip()
for _ in range(2):
    repeated_chords += Step(1)
    syncopation_3 = syncopation_1_4 + repeated_chords
    # syncopation_3 >> Play()

c.profiling_timer.call_timer_b()

lead_notes: Clip = Note() * repeated_chords.len()
lead_notes << Input(repeated_chords)
lead_notes << Equal(Degree(5))**Degree(7) << Equal(6)**5
lead_notes += Octave(1)
# lead_notes += Degree(4)
# lead_notes >> Play()

syncopation_4: Clip = syncopation_3 + lead_notes
syncopation_4.getPlaylist()
# syncopation_4 >> Play()

print(c.profiling_timer)
