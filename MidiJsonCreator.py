import staff
import element
import creator
from staff import Length

# print("Test Creator")

# staff objects

default_staff = staff.Staff(4, 110)

# element ojects

default_clock = element.Clock()
default_note = element.Note()

sequence = [
            {"position": Length(steps=0), "velocity": 100, "duration": Length(note=1/16)},
            {"position": Length(steps=1), "velocity": 100, "duration": Length(note=1/16)},
            {"position": Length(steps=2), "velocity": 100, "duration": Length(note=1/16)},
            {"position": Length(steps=3), "velocity": 100, "duration": Length(note=1/16)},
            {"position": Length(steps=4), "velocity": 100, "duration": Length(note=1/16)},
            {"position": Length(steps=5), "velocity": 100, "duration": Length(note=1/16)},
            {"position": Length(steps=6), "velocity": 100, "duration": Length(note=1/16)},
            {"position": Length(steps=7), "velocity": 100, "duration": Length(note=1/16)}
        ]

default_sequence = element.Sequence(10, 60, 2, sequence)

placed_elements = element.Composition()
placed_elements.placeElement(default_clock, Length())
# placed_elements.placeElement(default_note, Length(1, 0.25))
placed_elements.placeElement(default_sequence, Length(2))

placed_elements.setData__device_list();
elements_list = placed_elements.getPlayList(default_staff)
print(elements_list)
# print(isinstance(default_note.getData__device_list(), list))
# print(isinstance(placed_elements.getData__device_list(), list))

# creator objects

default_creator = creator.PlayList()
default_creator.saveJsonPlayList(elements_list, "example_play_file.mjp")

default_creator.playPlayList(elements_list)

