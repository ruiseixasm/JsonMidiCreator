from jsonmidicreator import *

# Actual firmware version Digitakt: 1.52A
settings << Devices(["loop", "Digitakt"]) << ClockedDevices(["loop", "Digitakt"])


clocked_rest = Rest(1/1) * 2 << Name("Pattern")
# clocked_rest >> Plot(by_channel=True)




