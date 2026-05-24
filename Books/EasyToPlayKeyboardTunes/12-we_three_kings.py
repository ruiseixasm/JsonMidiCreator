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

settings << Tempo(240) << TimeSignature(6, 8) << KeySignature('') << Quantization(1/2)


# / has precedence over +

chords = Clip()
melody = Clip()

# Measure 0
chords *= "c;m1;A"
melody *= "n;1/4;E;o5  n;1/8;D;o5  n;1/4;C;o5  n;1/8;A"
# Measure 1
chords *= "c;d1/4;G             c;b9;A"
melody *= "n;1/8;B  n;1/8;C;o5  n;1/8;B  n;d1/4;A"
# Measure 2
chords *= ""
melody *= "n;1/4;E;o5  n;1/8;D;o5  n;1/4;C;o5  n;1/8;A" # Repeated from MEasure 0
# Measure 3
chords *= "c;d1/4;G          c;d2/4;A"
melody *= "n;1/8;B  n;1/8;C;o5  n;1/8;B  n;d1/4;A"  # Repeated from MEasure 1
# Measure 4
chords *= "c;p0.5;d1/4;G"
melody *= "n;b2;C;o5  n;b1;C;o5   n;b2;D;o5  n;b1;D;o5"
# Measure 5
chords *= "c;b3;C   c;b3;G"
melody *= "n;b2;E;o5   n;b1;E;o5   n;b1;G;o5  n;b1;F;o5  n;b1;E;o5"
# Measure 6
chords *= "c;b3;D   c;b3;E"
melody *= "n;b1;D;o5   n;b1;E;o5   n;b1;D;o5  n;b2;C;o5  n;b1;B"
# Measure 7
chords *= "c;b3;A   c;b3;G"
melody *= "n;b3;A   n;b2;B  n;b1;D;o5"
# Measure 8
chords *= "c;b6;A"
melody *= "n;b2;C;o5   n;b1;C;o5  n;b2;C;o5  n;b1;G"
# Measure 9
chords *= "c;b3;F   c;b3;C"
melody *= "n;b2;C;o5   n;b1;A  n;b3;C;o5"
# Measure 10
chords *= "c;b6;C"
melody *= "n;b2;C;o5   n;b1;C;o5  n;b2;C;o5     n;b1;G"
# Measure 11
chords *= "c;b3;F   c;b3;C"
melody *= "n;b2;C;o5    n;b1;A  n;b3;C;o5"
# Measure 12
chords *= "c;b3;A   c;b3;G"
melody *= "n;b2;C;o5    n;b1;C;o5   n;b2;D;o5   n;b1;E;o5"
# Measure 13
chords *= "c;b3;F   c;b3;G"
melody *= "n;b2;F5    n;b1;E5   n;b2;D5   n;b1;E5"
# Measure 14
chords *= "c_1;C"
melody *= "n4;C5   n8;C5  n4;C5  n8;G"
# Measure 15
chords *= "c4d;F    c4d;C"
melody *= "b2;C5    b1;A    b3;C5"



melody << Title("Melody") << Velocity(85) >> Plot(block=False)
chords << Channel(2) << Octave(3) << Velocity(60) << Gate(.99)
chords >>= Smooth(4)
melody / 2 + chords.copy(Disable()) / 2 >> Plot(block=False, composition=chords / 2, title="We Three Kings")


chords = Line()
melody = Line()


# THE DEFAULT DURATION OF A NOTE IS 1 BEAT AND NOT 1/4 NECESSARILY
# For a TimeSignature fo 6/8, the default duration is 1/8
# Beat = atomic temporal unit of current meter

# Measure 0
chords += "c:1m:A"
melody += ":1/4:E5, ::D5, :1/4:C5, ::A"
# Measure 1
chords += "c:1/4d:G, c:1md:A"
melody += "::B, ::C5, ::B, :1/4d:A"
# Measure 2
chords += ""
melody += ":1/4:E5, ::D5, :1/4:C5, ::A" # Repeated from MEasure 0
# Measure 3
chords += "c:1/4d:G, c:1/2d:A"
melody += "::B, ::C5, ::B, :1/4d:A" # Repeated from MEasure 1
# Measure 4
chords += "c:1/4d:G"
melody += ":2b:C5, ::C5, :2b:D5, ::D5"
# Measure 5
chords += "c:3b:C, c:3b:G"
melody += ":2b:E5, ::E5, ::G5, ::F5, ::E5"
# Measure 6
chords += "c:3b:A, c:3b:G"
melody += "::D5, ::E5, ::D5, :2b:C5, ::B"
# Measure 7
chords += "c:3b:A, c:3b:G"
melody += ":3b:A, :2b:B, ::D5"
# Measure 8
chords += "c:6b:A"
melody += ":2b:C5, ::C5, :2b:C5, ::G"
# Measure 9
chords += "c:3b:F, c:3b:C"
melody += ":2b:C5, ::A, :3b:C5"
# Measure 10
chords += "c:6b:C"
melody += ":2b:C5, ::C5, :2b:C5, ::G"
# Measure 11
chords += "c:3b:F, c:3b"
melody += ":2b:C5, ::A, :3b:C5"
# Measure 12
chords += "c:3b:A, c:3b:G"
melody += ":2b:C5, ::C5, :2b:D5, ::E5"
# Measure 13
chords += "c:3b:F, c:3b:G"
melody += ":2b:F5, ::E5, :2b:D5, ::E5"
# Measure 14
chords += "c:1m:C"
melody += ":1/4:C5, ::C5, :1/4:C5, ::G"
# Measure 15
chords += "c:4d:F, c:4d:C"
melody += ":2b:C5, ::A, :3b:C5"



# Print the full content
chords >> Print()
melody >> Print()

chords_clip = Clip(chords * 2)
melody_clip = Clip(melody * 2)

melody_clip << Title("Melody (New)") << Velocity(85) >> Plot(block=False)
chords_clip << Channel(2) << Octave(3) << Velocity(60) << Gate(.99)
chords_clip >>= Smooth(4)
melody_clip + chords_clip.copy(Disable()) >> Plot(composition=chords_clip, title="We Three Kings (New)")


