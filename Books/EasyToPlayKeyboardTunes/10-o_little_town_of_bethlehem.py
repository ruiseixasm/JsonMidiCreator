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


ProgramChange("Trumpet", Channel(1)) + ProgramChange("Mandolin", Channel(2)) >> Play()

settings << Tempo(140) << TimeSignature(4, 4) << KeySignature('#') << Quantization(1/2)


pickup_bar = \
    Note(Beat(3))**1
main_phrase = \
    Note("G")**3 / Note("A") / Note(1/8, "B") / Note(1/8, "A") / Note(1/8, "B") / Note(1/8, "C") / Note("D") / Note("B")
variant_phrase_ = \
    Note() / Note(1/8, )**2 / Note()**2 / Note(Dotted(1/2)) << Foreach("C", "B", "G", "A", "A", "G")
central_period = \
    Note(Dotted(1/4), "D") / Note(1/8, "E")**5 / Note(1/8, )**["G", "A", "B", "C"] / Note("D")**2 / \
    Note()**["G", "B", "A", "G"] / Note(1/2, "D")**2 \
        << Match(0, "E")**Previous(Pipe(Degree()))**Subtract(1)**Pipe()

melody = \
    pickup_bar * \
    main_phrase * variant_phrase_ / Note("D") * main_phrase * variant_phrase_ / Note(1/8, "G") / Note(1/8, "B") * \
    central_period * main_phrase * variant_phrase_ >> Smooth() << First()**("D", Octave(4))
melody << Title("Melody") << Velocity(85) >> Plot(block=False)



chords = \
    Rest(1., 1)**2 / Rest(1/2, ) / \
    Chord(1/2, "D") / Chord(3., "G") / Chord(1/2, "C") / Chord(1/2, "D") / \
    Chord(4., "G") / Chord(1., "D") / Chord(2., "G") / Chord(1/2, "C") / Chord(1/2, "D") / Chord(1., "G")

chords << Channel(2) << Octave(3) << Velocity(90) << Gate(.99)
chords >>= Smooth(4)


melody / 2 + chords.copy(Disable()) / 2 >> Plot(composition=chords / 2, title="O Little Town of Bethlehem")


