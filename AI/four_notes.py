from jsonmidicreator import *

four_notes = Clip() << Line("n:1/4, :1/4, :1/4, :1/4") >> Save("AI/four_notes.json")

loaded_notes = Load("AI/four_notes.json")
loaded_notes >> Plot()
