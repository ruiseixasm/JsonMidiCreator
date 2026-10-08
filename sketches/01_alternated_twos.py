from jsonmidicreator import *

two_triggers = Clip(DrumKit("808")) << Line("t::Kick, :, :_b2:Snare, :")

two_triggers >> Plot()
