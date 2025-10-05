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

rest_play = ( Rest(), P)
settings << KeySignature(-1)   # Sets the default Key Note configuration


four_eights: Clip = Note(eight) * 4 + 3 # Increases 3 degrees from I to IV, from F to Bb
four_eights -= Iterate()    # Decreases degrees from IV to I
# four_eights >> Play()

first_half_1: Clip = Note() + 2 * Note(eight) >> Stack() << Foreach(3, 2, 3)
# first_half_1 >> Play()

first_half_2: Clip = first_half_1 * 1 << Nth(1)**2
# first_half_2 >> Play()

melody: Clip = first_half_1 >> four_eights >> first_half_2 >> Note(1/2, 2) * 1 >> first_half_2 - 1 >> four_eights - 1 >> Note(1/1) << MidiTrack("melody")
melody * 4 >> Export("./Books/MusicComposition/IdiotsGuide/Part_04/Chapter_14/exported_lead_sheet_melody_jmp.json") # Export as a JsonMidiPlayer file
# melody * 4 >> Play()

chords: Clip = Chord(1) + Chord(2) + Chord(6, 1/2) + Chord(3, 1/2) + Chord(6) >> Stack() << MidiTrack("chords") << Octave(3)
# chords * 4 >> Play()

lead_sheet: Part = melody + chords
lead_sheet >> Play()
