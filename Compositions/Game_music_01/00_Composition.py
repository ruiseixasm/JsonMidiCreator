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

    # Intro
    # Verse
    # Chorus
    # Verse
    # Chorus
    # Bridge
    # Chorus
    # Outro

settings << Tempo(100)
part_composition = Part("Composition")

block_intro = Load("Compositions/Game_music_01/Saves/01_intro_save.json")
part_composition += block_intro
block_verse_1 = Load("Compositions/Game_music_01/Saves/02_verse_save.json")
part_composition += block_verse_1 << Measure(4) << "Verse_1"
part_composition["Verse_1"] += Measures(4)

part_composition % Length() % float() >> Print()
part_composition >> Plot()
