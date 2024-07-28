import creator
from staff import *
from operand import *
from element import *

# print("Test Creator")

# global objects

set_global_staff(Staff(tempo=110)).setData__measures(4)

# element ojects

default_note = Note()

trigger_notes = [
            [ Position(Length(steps=0)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=1)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=2)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=3)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=4)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=5)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=6)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=7)), Velocity(100), Duration(Length(note=1/16)) ]
        ]

first_sequence = Sequence(10, 60, Length(beats=2), trigger_notes)
second_sequence = first_sequence.copy()
second_sequence.op_add(Position(Length(steps=2)))

# print(second_sequence.getSerialization())
print(Length(beats=4).is_eq(Length(measures=1)))

placed_elements = Composition()
# placed_elements.placeElement(default_clock, Position(Length()))
placed_elements.placeElement(default_note, Position(Length(beats=1)))
placed_elements.placeElement(first_sequence, Position(Length(1)))
placed_elements.placeElement(second_sequence, Position(Length(1)))

placed_elements.setData__device_list();
elements_list = placed_elements.getPlayList()

# print(elements_list)
# print(isinstance(default_note.getData__device_list(), list))
# print(isinstance(placed_elements.getData__device_list(), list))

# creator objects

default_creator = creator.PlayList()
default_creator.saveJsonMidiPlay(elements_list, "example_play_file.json")
default_creator.jsonMidiPlay(elements_list)

default_creator.saveJsonMidiCreator(second_sequence.getSerialization(), "_jsonMidiCreator.json")
# print(default_creator.loadJsonMidiCreator("_jsonMidiCreator.json"))
