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

# https://youtu.be/TbDUsEmbsPw?si=kkpOfJ1vrp1ECd1x

# Global Staff setting up
settings << Tempo(120)

# All whites
b_minor_scale = KeyScale(Scale("Dorian"), "D")
b_minor_scale >> P
 Rest() >> P

seven_keys = Note(1/1) / 7 << Iterate()
seven_keys >> P
 Rest() >> P

seven_keys % Pipe(Staff()) << Scale("Dorian")
seven_keys >> P
 Rest() >> P

seven_keys << Degree(0) # Degree 0 sets the Scale natural tonic
seven_keys >> P
 Rest() >> P

