from jsonmidicreator import *

settings << Tempo(100)

basic_rock: str = (
    "pc_10::17," # Power Kit, Preset 17 ("pc" for Program Change)
)

clip = Clip(DrumKit("808"), Title("Basic Rock"), Line(basic_rock))
clip += Trigger("Kick") * 16 << NotEqual(OnBeat())**Even()**Delete()

clip * 4 >> Plot()