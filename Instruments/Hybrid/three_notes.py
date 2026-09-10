from jsonmidicreator import *

RD_Hybrid.program_change(27, 1) >> Play()   # Sets the instrument to 27. Steel Galloper

three_notes = Clip(TimeSignature(7, 4), Name("Riffle"), Line(
    "n:3b:C5, :2b:D5, ::D#5"
))

three_notes /= 4

three_notes >> Plot()
