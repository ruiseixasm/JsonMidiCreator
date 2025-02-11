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
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *


# Global Staff setting up
# defaults << Tempo(90) << Measure(7)

# entire_scale = KeyScale("A")
# entire_scale << Mode("5th")
# print(entire_scale % list())
# print(entire_scale % str())

# single_chord = Chord("A") << Scale("minor") << Size("7th") << NoteValue(1/2)
# single_chord >> Play()

# single_triplet = Triplet(Note("B"), Note("F"), Note("G")) << Gate(0.75)
# single_triplet >> Play(True)

# single_triplet = Triplet(Note("C"), Note("G"), Note("F")) << Gate(0.75)
# single_triplet >> Play(True)

# tuplet = Tuplet( Note("C"), Note("F"), Note("G"), Note("C") )
# tuplet % Division() % int() >> Print()

# retrigger = Retrigger("G") << Gate(.9)
# retrigger << NoteValue(1) >> Play(True) >> Export("json/_Export_s.1_snippets_retirgger.json")
# retrigger << Swing(.75) >> Play(True) >> Export("json/_Export_s.2_snippets_retirgger.json")
# retrigger << Division(5) >> Play(True) >> Export("json/_Export_s.3_snippets_retirgger.json")

# scale = Scale([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
# scale % list() >> Print()
# scale % str() >> Print()
# scale % Modulation("6th") >> Print()
# (Scale() << scale % Modulation("6th")) % str() >> Print()
# (scale >> Copy() >> Modulate("6th")) % str() >> Print()


# # Perform the operation
# note = Note("F")
# note >> Print()
# note % Key() >> Print()
# note % Key() % str() >> Print()

# element = Element()
# element >> Print()
# element % Device() >> Print()
# element % Device() % list() >> Print()


# clock = Clock(4)
# clock % Duration() % Measure() % float() >> Print()

# scale = KeyScale()
# scale % str() >> Print()
# scale << "minor"
# scale % str() >> Print()
# scale % list() >> Print()


# all_classes: list = list_all_operand_classes(Operand)
# print(all_classes)


# class ParentClass:
#     _limit_denominator: int = 100  # Static variable in the parent class

# class SubClass(ParentClass):
#     _limit_denominator: int = 50  # Override the static variable in the subclass

# # Instances
# parent_instance = ParentClass()
# subclass_instance = SubClass()

# # Accessing the variable
# print(parent_instance._limit_denominator)  # Output: 100 (from ParentClass)
# print(subclass_instance._limit_denominator)  # Output: 50 (from SubClass)


sixteen_notes = Note(1/1) * 16
# sixteen_notes >> Play()

sixteen_notes << Get(Duration())**Divide(Iterate(1, 2))
sixteen_notes >> Stack() >> Play()

