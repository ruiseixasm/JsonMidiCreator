from jsonmidicreator import *

settings << ClockedDevices(["MIDI"])

three_notes = Clip(TimeSignature(7, 4), Name("Riffle"), Line(
    "n:3b:C5, :2b:D5, ::D#5"
))

three_notes += RD_Devices.Clip_program_change(27, 1)   # Sets the instrument to 27. Steel Galloper

settings << [
    Tempo(100),
    Tempo(100, three_notes * 2 % Length()),
    Tempo(200, three_notes * 2 % Length())
]


three_notes *= 4
# In order to the following `.json` file be created in the same folder, run Python in the folder
three_notes * [1, 2] * 2 >> Export("three_notes.json") >> Play(loop=1, verbose=True)

# If the total duration for a loop is 28 seconds then the interpolation is working fine.

