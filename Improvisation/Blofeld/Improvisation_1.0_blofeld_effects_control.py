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

defaults % Devices() % list() >> Print()
defaults << D_Blofeld.device
defaults % Devices() % list() >> Print()


defaults << Tempo(120)


variables_decay_cc = ControlChange(
        Channel(1), D_Blofeld.midi_cc["ENVELOPE FILTER"]["Decay"]
    ) * 16 << Iterate(100, -6) >> Reverse()

variables_decay_cc * 4 + Chord(4/1) >> P


defaults -= D_Blofeld.device
defaults % Devices() % list() >> Print()
