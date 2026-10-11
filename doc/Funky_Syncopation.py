from jsonmidicreator import *

funky_syncopation: str = (
    "t:1/16_2S:Snare:50, :_6S, :_9S, :_11S,"
    "t:1/16_4S:Snare:100,"
    "t:1/16_0m:Close:80," + ":," * 15 +
    "t:1/16_0m:Kick:90, :_3S, :_7S, :_10S,"
)

drum_kit = DrumKit("808")
clip = Clip(drum_kit) << Title("Funky Syncopation") << Line(funky_syncopation)

clip >> Plot()