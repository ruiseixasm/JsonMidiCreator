import staff
import element
import operator

print("Test Creator")

default_staff = staff.Staff()
default_timesignature = staff.TimeSignature()
default_tempo = staff.Tempo()

default_clock = element.Clock()
default_note = element.Note()
placed_elements = element.Positioner(default_timesignature, default_tempo)
placed_elements.placeElement(default_clock, 0, 4)
placed_elements.placeElement(default_note, 1, 0.25)

elements_list = placed_elements.getPlayList()

default_creator = element.PlayListCreator()
default_creator.addDevice(elements_list, "Midi Through")
default_creator.addDevice(elements_list, "loopMIDI Port")
default_creator.addDevice(elements_list, "GS Wavetable Synth")

print(elements_list)

default_creator.saveJsonPlay(elements_list, "example_play_file.mjp")