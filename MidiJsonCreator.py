import elements

print("Test Creator")

default_staff = elements.Staff()
default_timesignature = elements.TimeSignature()
default_tempo = elements.Tempo()

clock_list = default_tempo.getPlayList(default_staff, default_timesignature)

default_note = elements.Note()
placed_elements = elements.PlacedElements(default_timesignature, default_tempo)
placed_elements.placeElement(default_note, 1, 0.25)

elements_list = placed_elements.getPlayList()

final_list = clock_list + elements_list

default_creator = elements.PlayListCreator()
default_creator.addDevice(final_list, "Midi Through")
default_creator.addDevice(final_list, "loopMIDI Port")
default_creator.addDevice(final_list, "GS Wavetable Synth")

print(final_list)

default_creator.saveJsonPlay(final_list, "example_play_file.mjp")