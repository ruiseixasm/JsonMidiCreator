from jsonmidicreator import *

settings << ClockedDevices(["loop"]) << Tempo(100.5)

RD_Hybrid.program_change(27, 1) >> Play()   # Sets the instrument to 27. Steel Galloper

three_notes = Clip(TimeSignature(7, 4), Name("Riffle"), Line(
    "n:3b:C5, :2b:D5, ::D#5"
))

three_notes *= 4

three_notes * [1, 2] >> Export("Instruments/Hybrid/three_notes.json") >> Play(True)
