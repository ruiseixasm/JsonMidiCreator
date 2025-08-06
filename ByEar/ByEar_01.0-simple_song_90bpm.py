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
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

# https://youtu.be/0HAxftAH-PU?si=Ou4FZwYBRoGh8ML1


device_list = settings % Devices() % list() >> Print()
device_list.insert(0, "Blofeld")
device_list >> Print()
settings << Device(device_list)

# Global Staff setting up
settings << Tempo(90)

note_duration = Duration(1/16)
three_notes = Note() * 3 << Foreach(Dotted(note_duration), note_duration, note_duration) >> Stack()
three_notes += Octave(1)
three_notes << Once("G", "G", "A")
# three_notes << CPar(Length(2.0))

three_notes * 64 << Duration(1/16) >> Play()
