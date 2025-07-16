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

chaos = SinX(340)

def new_clip(clip: Clip) -> Clip:
    clip << Input(chaos)**Choice(60, 70, 80, 90, 100)**Velocity()
    return clip

ghost_notes = Note(DrumKit("Snare"), 1/16) * 16 * 8 << Velocity(50)

ghost_notes >> Plot()

snare_part = Part(ghost_notes)

def composition(clip: Clip) -> Composition:
    # This filter retains the clip as a Clip and not as a Mask
    one_measure = clip.filter(Or(Measure(0), Measure(1)))
    # Automatically sorted by position

    # PROBLEM HERE

        #         interrupted_clip = one_measure + Measures(4) + one_measure
        #                     ~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~
        # File "/home/rui/GitHub/JsonMidiCreator/src/operand.py", line 433, in __add__
        #     return self.copy().__iadd__(operand)
        #         ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
        # File "/home/rui/GitHub/JsonMidiCreator/src/operand_container.py", line 2074, in __iadd__
        #     self += single_element
        # File "/home/rui/GitHub/JsonMidiCreator/src/operand_container.py", line 2080, in __iadd__
        #     return self._append([ new_element ], self_last_element)._sort_items()  # Shall be sorted!
        #         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
        # File "/home/rui/GitHub/JsonMidiCreator/src/operand_container.py", line 168, in _sort_items
        #     self._items.sort()  # Operands implement __lt__ and __gt__
        #     ~~~~~~~~~~~~~~~~^^
        # File "/home/rui/GitHub/JsonMidiCreator/src/operand_element.py", line 1024, in __lt__
        #     if self._position_beats == other._position_beats:
        #     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # File "/usr/local/lib/python3.13/fractions.py", line 967, in __eq__
        #     return (a._numerator == b.numerator and
        #                             ^^^^^^^^^^^
        # File "/usr/local/lib/python3.13/fractions.py", line 414, in numerator
        #     @property
            
        # KeyboardInterrupt


    interrupted_clip = one_measure + Measures(4) + one_measure
    return snare_part + interrupted_clip


four_notes = Note() * 4 << Key("A") << Duration(1/8) << Channel(2)
seed_clip: Clip = (Chord(Key("C"), Size("7th")) * Chord(Key("E"), Size("7th")) << Tied()) * 2 + four_notes

# masked_clip = seed_clip.filter(Or(Measure(0), Measure(1)))
# masked_clip >> Plot()   # Returns a copy of the mask as a real Clip
# masked_interrupted_clip = masked_clip + Measures(4) + masked_clip
# masked_interrupted_clip >> Plot()   # Returns a copy of the mask as a real Clip


# # Testing composition method first
# composed_clip: Composition = composition(seed_clip)
# composed_clip >> Plot()


def pass_trough_composition(clip: Clip) -> Composition:
    return clip


seed_clip >> Plot(iterations=10, n_button=new_clip, c_button=pass_trough_composition)




