from jsonmidicreator import *

settings << ClockedDevices(["loop"])

settings << [
    Tempo(60),
    Tempo(60, Beats(4*4))
]

one_note = Note() * 4
one_note >> Play(loop=1, verbose=True)

