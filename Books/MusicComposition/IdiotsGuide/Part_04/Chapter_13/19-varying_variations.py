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
src_path = os.path.join(os.path.dirname(__file__), '../../../../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

rest_play = ( Rest(), Play())
settings << KeySignature(1, Minor())   # Sets the default Key Note configuration

# Original Motif to work on its pitches
motif: Clip = Note() * 6 << Foreach(quarter, eight, eight, dotted_quarter, eight, whole) >> Stack()
motif << Foreach(1, 3, 4, 5, 4, 1)**Degree()
motif_mirror: Clip = motif.copy() << Get(Degree())**Multiply(-1)
motif_reverse: Clip = motif_mirror.copy().reverse()
motif_modulated: Clip = motif_mirror.copy() + Octave() << "D"
# motif_modulated >> Play()

new_motif: Clip = Note() * 6 << Foreach(half, sixteenth, dotted_eight, sixteenth, sixteenth, eight) >> Stack()
new_motif % Length() >> Print() # Needs to be implemented
new_motif << Foreach(1, -4, -5, -4, -3, 1)**Degree()
# new_motif >> Play()
new_motif_modulated_a: Clip = new_motif.copy() << "A"
new_motif_reverse: Clip = new_motif_modulated_a.copy().reverse()
new_motif_modulated_b: Clip = new_motif.copy() << "B"

varying_variations: Clip = \
    motif >> motif_mirror >> motif_reverse >> \
    new_motif >> new_motif_modulated_a >> new_motif_reverse >> new_motif_modulated_b >> motif_modulated << MidiTrack("Melody")

varying_variations >> Play()
