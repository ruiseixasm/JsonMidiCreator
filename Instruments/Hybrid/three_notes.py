from jsonmidicreator import *

RD_Hybrid.program_change(27, 1) >> Play()   # Sets the instrument to 27. Steel Galloper

three_notes = Clip(Line(
    "n:1/2:C5, :1/4:D5, ::D#5"
))

three_notes >> Plot()
