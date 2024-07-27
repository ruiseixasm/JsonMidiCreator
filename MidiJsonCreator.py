import creator
from staff import *
from operand import *
from element import *

# print("Test Creator")

# staff objects

default_staff = Staff(4, 110)

# element ojects

default_clock = Clock()
default_note = Note()

sequence = [
            [ Position(Length(steps=0)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=1)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=2)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=3)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=4)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=5)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=6)), Velocity(100), Duration(Length(note=1/16)) ],
            [ Position(Length(steps=7)), Velocity(100), Duration(Length(note=1/16)) ]
        ]

default_sequence = Sequence(10, 60, 2, sequence)

placed_elements = Composition()
placed_elements.placeElement(default_clock, Position(Length()))
placed_elements.placeElement(default_note, Position(Length(1, 0.25)))
placed_elements.placeElement(default_sequence, Position(Length(1)))

placed_elements.setData__device_list();
elements_list = placed_elements.getPlayList(default_staff)

# print(elements_list)
# print(isinstance(default_note.getData__device_list(), list))
# print(isinstance(placed_elements.getData__device_list(), list))

# creator objects

default_creator = creator.PlayList()
default_creator.saveJsonPlayList(elements_list, "example_play_file.mjp")
default_creator.playPlayList(elements_list)

