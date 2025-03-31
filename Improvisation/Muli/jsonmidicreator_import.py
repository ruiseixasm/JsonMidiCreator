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

# jsonmidicreator_import.py
import sys
import os

def add_src_to_path():
    """Dynamically finds and adds 'src' directory to sys.path."""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    while current_dir:
        src_path = os.path.join(current_dir, 'src')
        if os.path.exists(src_path):
            if src_path not in sys.path:
                sys.path.append(src_path)
            break
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # Stop if we reach the root
            break
        current_dir = parent_dir

# Add 'src' to sys.path before importing JsonMidiCreator
add_src_to_path()

# Import everything from JsonMidiCreator
from JsonMidiCreator import *


