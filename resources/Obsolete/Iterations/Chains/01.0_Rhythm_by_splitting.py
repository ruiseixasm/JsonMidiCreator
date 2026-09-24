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
from jsonmidicreator import *

measure_note = Note(1/1) * 1

notes_splitter = I_SplitDuration()
multiple_notes = measure_note >> notes_splitter >> Plot()


notes_setter = I_SetParameter(no_repetitions=True)
chained_iterations = \
    multiple_notes  << Select(Beat(0)) >> notes_setter >> Plot() \
                    << Select(Beat(1)) >> notes_setter >> Plot() \
                    << Select(Beat(2)) >> notes_setter >> Plot() \
                    << Select(Beat(3)) >> notes_setter >> Plot() << Unmask()

