import staff
import element
import creator

print("Test Creator")

default_staff = staff.Staff()
default_timesignature = staff.TimeSignature()
default_tempo = staff.Tempo()

default_clock = element.Clock()
default_note = element.Note()
placed_elements = element.Composition(default_timesignature, default_tempo)
placed_elements.placeElement(default_clock, 0, 4)
placed_elements.placeElement(default_note, 1, 0.25)

elements_list = placed_elements.getPlayList()
print(elements_list)

default_creator = creator.PlayListCreator()
default_creator.saveJsonPlay(elements_list, "example_play_file.mjp")