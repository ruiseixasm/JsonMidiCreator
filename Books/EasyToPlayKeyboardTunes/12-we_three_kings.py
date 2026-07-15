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


from jsonmidicreator import *

settings << Folder("Books/EasyToPlayKeyboardTunes/")
ProgramChange("Electric grand piano", Channel(1)) + ProgramChange("Synth voice", Channel(2)) >> Play()
settings << Tempo(240) << TimeSignature(6, 8) << KeySignature('') << Quantization(1/2)


chords = Line()  # Checksum: da16
melody = Line()  # Checksum: 1540


# THE DEFAULT DURATION OF A NOTE IS 1 BEAT AND NOT 1/4 NECESSARILY
# For a TimeSignature fo 6/8, the default duration is 1/8
# Beat = atomic temporal unit of current meter

# Measure 0
chords += "c:1m:A"  # Previous type of argument sets the default type of the next one
melody += ":1/4:E5, :1b:D5, :1/4:C5, :1b:A4"
# Measure 1
chords += ":1/4d:G, :1md:A"
melody += ":1b:B, ::C5, ::B4, :1/4d:A4"
# Measure 2
chords += ""
melody += ":1/4:E5, :1b:D5, :1/4:C5, :1b:A4" # Repeated from MEasure 0
# Measure 3
chords += ":1/4d:G, :1/2d:A"
melody += ":1b:B4, ::C5, ::B4, :1/4d:A4" # Repeated from MEasure 1
# Measure 4
chords += ":1/4d:G"
melody += ":2b:C5, :1b:C5, :2b:D5, :1b:D5"
# Measure 5
chords += ":3b:C, :3b:G"
melody += ":2b:E5, :1b:E5, ::G5, ::F5, ::E5"
# Measure 6
chords += ":3b:D, :3b:E"
melody += ":1b:D5, ::E5, ::D5, :2b:C5, :1b:B4"
# Measure 7
chords += ":3b:A, :3b:G"
melody += ":3b:A4, :2b:B4, :1b:D5"
# Measure 8
chords += ":6b:A"
melody += ":2b:C5, :1b:C5, :2b:C5, :1b:G4"
# Measure 9
chords += ":3b:F, :3b:C"
melody += ":2b:C5, :1b:A4, :3b:C5"
# Measure 10
chords += ":6b:C"
melody += ":2b:C5, :1b:C5, :2b:C5, :1b:G4"
# Measure 11
chords += ":3b:F, :3b"
melody += ":2b:C5, :1b:A4, :3b:C5"
# Measure 12
chords += ":3b:A, :3b:G"
melody += ":2b:C5, :1b:C5, :2b:D5, :1b:E5"
# Measure 13
chords += ":3b:F, :3b:G"
melody += ":2b:F5, :1b:E5, :2b:D5, :1b:E5"
# Measure 14
chords += ":1m:C"
melody += ":1/4:C5, :1b:C5, :1/4:C5, :1b:G4"
# Measure 15
chords += ":4d:F, :4d:C"
melody += ":2b:C5, :1b:A4, :3b:C5"



# Print the full content
chords >> Print()
melody >> Print()

chords_clip = Clip(chords * 2)  # Checksum: da16
melody_clip = Clip(melody * 2)  # Checksum: 1540

melody_clip << Title("Melody (New)") << Velocity(85) >> Plot(block=False)   # Checksum: 1540
chords_clip << Channel(2) << Octave(3) << Velocity(60) << Gate(.99)
chords_clip >>= Smooth(4)
melody_clip + chords_clip.copy(Disable()) >> Plot(composition=chords_clip, title="We Three Kings (New)")    # Checksum: da16


