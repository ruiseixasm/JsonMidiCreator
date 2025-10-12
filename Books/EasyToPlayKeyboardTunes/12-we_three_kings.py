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
src_path = os.path.join(os.path.dirname(__file__), '../../', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)


from JsonMidiCreator import *


settings << Folder("Books/EasyToPlayKeyboardTunes/")


ProgramChange("Electric grand piano", Channel(1)) + ProgramChange("Synth voice", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(6, 8) << KeySignature('') << Quantization(1/2)


# / has precedence over +

chords = Clip()
melody = Clip()

# Measure 0
chords *= "c,m1,A"
melody *= "n,1/4,E,o5  n,1/8,D,o5  n,1/4,C,o5  n,1/8,A"
# Measure 1
chords *= "c,:1/4,G             c,b9,A"
melody *= "n,1/8,B  n,1/8,C,o5  n,1/8,B  n,:1/4,A"
# Measure 2
chords *= ""
melody *= "n,1/4,E,o5  n,1/8,D,o5  n,1/4,C,o5  n,1/8,A"
# Measure 3
chords *= "c,:1/4,G          c,:2/4,A"
melody *= "n,1/8,B  n,1/8,C,o5  n,1/8,B  n,:1/4,A"
# Measure 4
chords *= "c,p3/8,:1/4,G"
melody *= "n,b2,C,o5  n,b1,C,o5   n,b2,D,o5  n,b1,D,o5"
# Measure 5
chords *= "c,b3,C   c,b3,G"
melody *= "n,b2,E,o5   n,b1,E,o5   n,b1,G,o5  n,b1,F,o5  n,b1,E,o5"
# Measure 6
chords *= "c,b3,D   c,b3,E"
melody *= "n,b1,D,o5   n,b1,E,o5   n,b1,D,o5  n,b2,C,o5  n,b1,B"
# Measure 7
chords *= "c,b3,A   c,b3,G"
melody *= "n,b3,A   n,b2,B  n,b1,D,o5"
# Measure 8
chords *= "c,b6,A"
melody *= "n,b2,C,o5   n,b1,C,o5  n,b2,C,o5  n,b1,G"
# Measure 9
chords *= "c,b3,F   c,b3,C"
melody *= "n,b2,C,o5   n,b1,A  n,b3,C,o5"
# Measure 10
chords *= "c,b6,C"
melody *= "n,b2,C,o5   n,b1,C,o5  n,b2,C,o5     n,b1,G"
# Measure 11
chords *= "c,b3,F   c,b3,C"
melody *= "n,b2,C,o5    n,b1,A  n,b3,C,o5"
# Measure 12
chords *= "c,b3,A   c,b3,G"
melody *= "n,b2,C,o5    n,b1,C,o5   n,b2,D,o5   n,b1,E,o5"
# Measure 13
chords *= "c,b3,F   c,b3,G"
melody *= "n,b2,F,o5    n,b1,E,o5   n,b2,D,o5   n,b1,E,o5"
# Measure 14
chords *= "c,b6,C"
melody *= "n,b2,C,o5   n,b1,C,o5  n,b2,C,o5  n,b1,G"
# Measure 15
chords *= "c,b3,F   c,b3,C"
melody *= "n,b2,C,o5    n,b1,A  n,b3,C5"



melody << Title("Melody") << Velocity(85) >> Plot(block=False)


chords << Channel(2) << Octave(2) << Velocity(60) << Gate(.99)
chords >>= Smooth(5)


melody / 2 + chords.copy(Disable()) / 2 >> Plot(composition=chords / 2, title="Lightly Row")


