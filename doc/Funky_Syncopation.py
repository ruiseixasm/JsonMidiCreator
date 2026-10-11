from jsonmidicreator import *

funky_syncopation: od.Line = od.Line(
    "t:1/16:Kick:90, :_3S, :_7S, :_10S," + \
    "t:1/16_4S:Snare," + \
    "t:1/16_2S:Snare:50, :_6S, :_9S, :_11S," + \
    "t:1/16_0:Close:80," + ":," * 15
)

drum_kit = DrumKit("808")
clip = Clip(drum_kit) << Title("Funky Syncopation")
clip << funky_syncopation

clip >> Plot()
