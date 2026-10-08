from jsonmidicreator import *

two_triggers = Clip(DrumKit("808")) << Line("t::Kick, t::Kick")

two_triggers >> Plot()
