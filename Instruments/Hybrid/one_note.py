from jsonmidicreator import *

settings << ClockedDevices(["loop"])

settings << [
    Tempo(30),
    Tempo(90, Beats(4*4))
]

one_note = Note() * 4
one_note >> Export("one_note.json") >> Play(loop=1, verbose=True)

