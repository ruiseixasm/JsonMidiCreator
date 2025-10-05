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


# Global Staff setting up
settings << Tempo(100)


sixteen_notes = Note() * 16 << Foreach(1, 4, 5, 1)

# sixteen_notes >> Play()

filtered_notes = sixteen_notes >> Measure(1)
filtered_notes << Measure(0)
filtered_notes += Note(6, Step(10))
filtered_notes[0] % Position() % float() >> Print()
filtered_notes >> Link() >> Play()
filtered_notes << Measure(1)
filtered_notes[0] % Position() % float() >> Print()

sixteen_notes * 2 >> Play()
