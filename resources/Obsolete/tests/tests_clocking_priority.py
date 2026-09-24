from jsonmidicreator import *

settings << ClockedDevices(["loop", "VMPK"])

whole_note = Note(1/1) * 1
step_note = Note(Steps(1), "G")
whole_note + step_note >> Play(verbose=True)


