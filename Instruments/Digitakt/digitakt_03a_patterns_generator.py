from jsonmidicreator import *

# Actual firmware version Digitakt: 1.52A
settings << Devices(["Digitakt"]) << ClockedDevices(["Digitakt"])

four_on_four = Sequencer() % Clip()

four_on_four >> Plot()


