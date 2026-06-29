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

measure_note = Note(1/1) * 1

notes_splitter = I_Splitter()
multiple_notes = measure_note >> Plot(n_button=notes_splitter.get_clip)


notes_setter = I_Setter(no_repetitions=True)
chained_iterations = \
    multiple_notes  << Select(Beat(0)) >> Plot(n_button=notes_setter.get_clip) \
                    << Select(Beat(1)) >> Plot(n_button=notes_setter.get_clip) \
                    << Select(Beat(2)) >> Plot(n_button=notes_setter.get_clip) \
                    << Select(Beat(3)) >> Plot(n_button=notes_setter.get_clip) << Unmask()


