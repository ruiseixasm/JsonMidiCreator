import staff
import element
import creator

print("Test Creator")

# staff objects

default_staff = staff.Staff(4, 110)

# element ojects

default_clock = element.Clock()
default_note = element.Note()

sequence = [
            {"step": 0, "velocity": 100, "duration_note": 1/16},
            {"step": 1, "velocity": 100, "duration_note": 1/16},
            {"step": 2, "velocity": 100, "duration_note": 1/16},
            {"step": 3, "velocity": 100, "duration_note": 1/16},
            {"step": 4, "velocity": 100, "duration_note": 1/16},
            {"step": 5, "velocity": 100, "duration_note": 1/16},
            {"step": 6, "velocity": 100, "duration_note": 1/16},
            {"step": 7, "velocity": 100, "duration_note": 1/16}
        ]

default_sequence = element.Sequence(10, 60, 2, sequence)

placed_elements = element.Composition()
placed_elements.placeElement(default_clock, 0, 4)
placed_elements.placeElement(default_note, 1, 0.25)
placed_elements.placeElement(default_sequence, 2, 0)

placed_elements.setData__device_list();
elements_list = placed_elements.getPlayList(default_staff)
print(elements_list)
print(isinstance(default_note.getData__device_list(), list))
print(isinstance(placed_elements.getData__device_list(), list))

# creator objects

default_creator = creator.PlayListCreator()
default_creator.saveJsonPlay(elements_list, "example_play_file.mjp")