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

settings += Device("Blofeld")
settings << Tempo(100)
settings % Tempo() >> Print()


big_note = Note(Measures(4))

rests_chopper = RS_Clip(big_note, [1], 4)
melody_wanna_be = \
    rests_chopper.multi_splitter(
        -9
    ).multi_wrapper(
        10,
        list_repeat([Note(), Rest(), Null()], [5, 1, 3])
        ).solution



settings << Settings()  # Resets to Defaults
settings % Tempo() >> Print()

