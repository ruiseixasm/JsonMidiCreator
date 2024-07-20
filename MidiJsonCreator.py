import elements

print("Test Creator")

default_staff = elements.Staff()
default_timesignature = elements.TimeSignature()
default_tempo = elements.Tempo()
default_creator = elements.PlayListCreator()

clock_list = default_tempo.getPlayList(default_staff, default_timesignature)

# print(clock_list)

default_creator.addDevice(clock_list, "Midi Through")
default_creator.addDevice(clock_list, "loopMIDI Port")
default_creator.addDevice(clock_list, "GS Wavetable Synth")

# print(clock_list)

default_note = elements.Note()
placed_elements = elements.PlacedElements(default_timesignature, default_tempo)
placed_elements.placeElement(default_note, 1, 0.25)

elements_list = placed_elements.getPlayList()

default_creator.addDevice(elements_list, "Midi Through")
default_creator.addDevice(elements_list, "loopMIDI Port")
default_creator.addDevice(elements_list, "GS Wavetable Synth")

print(elements_list)

default_creator.saveJsonPlay(elements_list, "example_play_file.mjp")