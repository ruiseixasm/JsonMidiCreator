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


ProgramChange("Electric piano 2", Channel(1)) + ProgramChange("Cello", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('b') << Quantization(1/4)


melody = Note() / 4 * 8 << Title("Melody")
melody << DownTo(Beat(2))**Either(Bar(1))**(Chord(1/2) / 1)
melody << Nth(2)**(Chord(1/8) / 2)


chords = \
    Chord("C", Bars(2)) * 1 \
        << Title("Chords") << Channel(2) << Octave(3) << Velocity(60) << Gate(.99)
chords >>= Smooth(4)


silent_night = melody + chords << Title("Hush Little Baby")
(melody + chords.copy(Disable())) * 2 >> Plot(composition=chords * 2)


