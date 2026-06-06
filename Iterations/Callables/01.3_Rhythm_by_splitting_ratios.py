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
    duration_0 = clip[0] % Duration()
    duration_1 = clip[1] % Duration()
    duration_2 = clip[2] % Duration()
    duration_3 = clip[3] % Duration()
    duration_4 = clip[4] % Duration()
    duration_5 = clip[5] % Duration()
    # Last 4 notes must have the same duration
    if duration_2 != duration_3 or duration_2 != duration_4 or duration_2 != duration_5:
        return True
    # # Makes sure the second note is half the duration of the first one
    # if duration_0 != duration_1 * 2:
    #     return True
    return False

def post_processing(clip) -> Clip:
    """Adds a 1 measure Rest"""
    clip *= 4
    clip *= Rest(1/1)
    return clip
    

notes_splitter = RC_Splitter(6, chaos=SinX(540), extra_exclusion=exclusion, post_processing=post_processing, packed_repeats=4, max_tries=1000)
rhythm_motif = measure_note >> Plot(n_button=notes_splitter.new_iteration, title="Rhythm", block=False)
rhythm_motif *= [0] # Just the first MEasure

# Build a melody from motifs and short phrases
degrees_chooser = RC_Chooser(["1", "2", "3", "4", "5", "6", "7"], post_processing=post_processing, max_tries=1000)
rhythm_phrase = rhythm_motif >> Plot(n_button=degrees_chooser.new_iteration, title="Melody") * 10

