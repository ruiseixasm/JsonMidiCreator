from jsonmidicreator import *

settings << Device("loop")
overlapping_notes = Note(1/2, "E") + Note(1/2, Beat(1), "E")
overlapping_notes.len() >> Print()

overlapping_notes >> Plot()

