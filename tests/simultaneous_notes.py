from jsonmidicreator import *

# settings << Device("loop")
simultaneous_notes = Note(1/1, "E") + Note(1/1) + Note(1/1)
simultaneous_notes.len() >> Print()

simultaneous_notes / 4 >> Play(verbose=True)

