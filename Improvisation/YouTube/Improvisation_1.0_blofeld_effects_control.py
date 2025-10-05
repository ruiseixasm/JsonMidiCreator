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

# This Episode DIDN'T AGE SO WELL - AudioPilz
# https://youtu.be/d5MURYNbpgo?si=MJiqT9olxOTyvPrB


settings % Devices() % list() >> Print()
settings += RD_Blofeld.device
settings % Devices() % list() >> Print()


# settings << Tempo(120).read()
settings << Tempo(140)

melody_6_00 = Note().read()

melody_6_00 >> Plot()

