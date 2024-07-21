import staff
import element
import creator

print("Test Creator")

# staff objects

default_staff = staff.Staff()
default_timesignature = staff.TimeSignature()
default_tempo = staff.Tempo(240)

# element ojects

default_clock = element.Clock(1.5)
default_note = element.Note()

sequence = [
            {"beat": 0/4, "velocity": 100, "duration_note": 1/16},
            {"beat": 1/4, "velocity": 100, "duration_note": 1/16},
            {"beat": 2/4, "velocity": 100, "duration_note": 1/16},
            {"beat": 3/4, "velocity": 100, "duration_note": 1/16},
            {"beat": 4/4, "velocity": 100, "duration_note": 1/16},
            {"beat": 5/4, "velocity": 100, "duration_note": 1/16},
            {"beat": 6/4, "velocity": 100, "duration_note": 1/16},
            {"beat": 7/4, "velocity": 100, "duration_note": 1/16}
        ]

default_sequence = element.Sequence(10, 60, 2, sequence)

placed_elements = element.Composition(default_timesignature, default_tempo)
#placed_elements.placeElement(default_clock, 0, 4)
placed_elements.placeElement(default_note, 1, 0.25)
placed_elements.placeElement(default_sequence, 2, 0)

elements_list = placed_elements.getPlayList()
print(elements_list)

# creator objects

default_creator = creator.PlayListCreator()
default_creator.saveJsonPlay(elements_list, "example_play_file.mjp")