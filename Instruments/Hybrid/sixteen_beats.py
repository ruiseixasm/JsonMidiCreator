from jsonmidicreator import *

settings << ClockedDevices(["MIDI"])

settings << [
    Tempo(30),
    Tempo(90, Beats(4*4))
]

sixteen_notes = Note(Beats(1)) / 4 * 4
sixteen_notes >> Export("sixteen_beats.json") >> Play(loop=1, verbose=True)

