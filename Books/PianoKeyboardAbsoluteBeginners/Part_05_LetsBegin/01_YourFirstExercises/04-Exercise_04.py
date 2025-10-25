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
import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '../../../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

settings << Tempo(90)
settings << Folder("Books/PianoKeyboardAbsoluteBeginners/PianoKeyboardAbsoluteBeginners/01_YourFirstExercises/")


ProgramChange("Organ") + ProgramChange("Piccolo", Channel(2)) >> Play()

right_hand = Clip("1  2  3  2  4  3  5  4  1")
right_hand << Last()**(Beats(2), Velocity(60))
left_hand = right_hand.copy(Octave(3))
left_hand += Measure(2)

right_hand_mirrored = right_hand.copy().mirror().add(Measure(4))
left_hand_mirrored = left_hand.copy().mirror().add(Measure(4)) << Last()**(1/1, Velocity(120))


right_hand + left_hand + right_hand_mirrored + left_hand_mirrored >> Plot(title="Exercise 4")

