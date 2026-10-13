from jsonmidicreator import *

settings << Tempo(100)

basic_rock: str = (
    "pc_10::17," # Power Kit Preset 17 ("pc" for Program Change)
    "t_10:1/16_0m_2S:Snare:40, :_6S, :_9S, :_11S, :_15S,"
        ":_0m_4S:Snare:100, :_12S,"
        ":_0m:Closed:60," + ":," * 15 +
        ":_0m:Kick:90, :_3S::70, :_7S, :_10S, :_13S,"
)

clip = Clip(DrumKit("808"), Title("Basic Rock"), Line(basic_rock))

clip * 4 >> Plot()