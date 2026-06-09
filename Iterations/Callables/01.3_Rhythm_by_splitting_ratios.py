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

def exclusion(clip) -> bool:
    """Makes sure each Note matches a specific duration pattern"""
    # Last 4 notes must have the same duration
    last_four = clip[Last(4)]
    return last_four != AllMatch(Duration())

def post_processing(clip) -> Clip:
    """Adds a 1 measure Rest"""
    clip *= 4
    clip *= Rest(1/1)
    return clip
    

notes_splitter = RC_Splitter(6, chaos=SinX(540), extra_exclusion=exclusion, post_processing=post_processing, packed_repeats=4)
rhythm_motif = measure_note >> Plot(n_button=notes_splitter.new_iteration, title="Rhythm", block=False)
rhythm_motif *= [0] # Just the first MEasure

# Build a melody from motifs and short phrases
degrees_chooser = RC_Chooser(["1", "2", "3", "4", "5", "6", "7"], post_processing=post_processing)
rhythm_phrase = rhythm_motif >> Plot(n_button=degrees_chooser.new_iteration, title="Melody")

