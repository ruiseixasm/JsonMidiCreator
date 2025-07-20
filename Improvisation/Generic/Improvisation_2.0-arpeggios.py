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

# https://youtu.be/1v578xNBDyY?si=_eveiFQ4K4cfyhuB

# Global Staff setting up
settings << Tempo(110)

tonic_key = TonicKey("C")
chromatic_notes = PitchChord(tonic_key, [0.0, 1.0, 2.0, 3.0], 4.0, Arpeggio("UpDown", 1/8)) * 1

for key in range(8):
    chromatic_notes += TonicKey(key)
    chromatic_notes >> Play()
    Rest() >> Play()

chromatic_notes << tonic_key
Rest(1/2) >> Play()

for key in range(8):
    chromatic_notes += Semitone(key)
    chromatic_notes >> Play()
    Rest() >> Play()
