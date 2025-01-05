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

rest_play = (R, P)
staff << KeySignature(-1)   # Sets the default Key Note configuration
staff << Tempo(120)

melody_playlist: Playlist = Import("./Books/MusicComposition/IdiotsGuide/Part_04/Chapter_14/exported_lead_sheet_melody_jmp.json")
# melody_playlist >> Play()

chords: Sequence = Chord(1) + Chord(2, Octave(3), Inversion(2)) + Chord(6, 1/2, Octave(4)) + Chord(3, 1/2, Octave(3), Inversion(1)) + Chord(6, Octave(4)) >> Stack()
chords *= 4
# chords >> Play()

bass_line: Sequence = Note(1/1) + Note(2, 1/1) + Note(1/2, 6) + Note(1/2, 3) + Note(1/1, 6) << Foreach(3, 3, 3, 2, 3)**Octave() >> Stack()
bass_line *= 4
# bass_line >> Play()

block_chord: Sequence = chords + bass_line << Channel(2) << Track("Block Chord")
# block_chord >> Play()

composition: Song = Song(block_chord) + melody_playlist
composition >> Play()
