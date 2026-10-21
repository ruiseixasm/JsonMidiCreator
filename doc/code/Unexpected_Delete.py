from jsonmidicreator import *

settings << Tempo(80)

clip = Clip(DrumKit("808"), Title("Unexpected Delete"))
clip += Trigger("Snare") * 16 << OnBeat()**Excluding()**Even()**Delete()

clip * 4 << Channel(10) >> Plot()