from jsonmidicreator import *

settings << ClockedDevices(["loop"])

whole_note = Note(1/1) * 1
whole_note >> Play(verbose=True)


