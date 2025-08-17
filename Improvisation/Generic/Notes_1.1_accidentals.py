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
from jsonmidicreator_import import *    # This ensures src is added & JsonMidiCreator is imported



many_notes = Note() / 16 << TrackName("Accidentals")

sharped_degree = Degree(Sharp())
sharped_degree % Sharp() >> Print()
many_notes << Odd()**sharped_degree
many_notes.inline() + Crossing()**Flat(1)
many_notes << Equal(Measure(0))**KeySignature("####") << Equal(Measure(2))**KeySignature("bbbb")
many_notes >> Plot()

