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

four_notes = Note(1/1) * 4

def pre_filter(candidate: Clip, seed: Clip) -> bool:
    """Uses a `Frame` selector `Equal`, resulting in a new list of same type of content, `Element`, in this case"""
    if candidate[Equal(Duration(Steps(2)))].len() > 0:
        return False
    return True

notes_splitter = I_DurationsSplitter(3*6, chaos=SinX(540), pre_filter=pre_filter, max_tries=200)
four_notes >> notes_splitter >> Plot()

