import elements

print("Test Creator")

default_staff = elements.Staff()
default_timesignature = elements.TimeSignature()
default_tempo = elements.Tempo()
default_creator = elements.Creator()

clock_list = default_tempo.getPlayList(default_staff, default_timesignature)

print(clock_list)

default_creator.addDevice(clock_list, "Midi Through")

print(clock_list)

default_creator.saveJsonPlay(clock_list, "example_play_file.mjp")