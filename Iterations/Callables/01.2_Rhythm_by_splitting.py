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

four_notes = Note(1/1) * 4

def exclusion(clip) -> bool:
    """Uses a `Frame` selector `Equal`, resulting in a new list of same type of content, `Element`, in this case"""
    if clip[Equal(Duration(Steps(2)))].len() > 0:
        return True
    return False

notes_splitter = RC_Splitter(3*6, chaos=SinX(540), extra_exclusion=exclusion, max_tries=200)
four_notes >> Plot(n_button=notes_splitter.new_iteration)

