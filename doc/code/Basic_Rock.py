from jsonmidicreator import *

settings << Tempo(100)

basic_rock: str = (
    "pc::17," # Power Kit, Preset 17 ("pc" for Program Change)
)

clip = Clip(DrumKit("808"), Title("Basic Rock"), Line(basic_rock))
clip += Trigger("Kick") * 16 % OnBeat()**Odd()
clip += Trigger("Snare") * 16 % OnBeat()**Even()
clip += Trigger("Closed") * 16 % Odd()

clip * 4 << Channel(10) >> Plot()