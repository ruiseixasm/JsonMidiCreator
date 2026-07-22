from jsonmidicreator import *

settings << Device("loop")
whole_note = Note(1/1, "E") + Note(1/1) + Note(1/1)
whole_note.len() >> Print()

whole_note >> Plot()


