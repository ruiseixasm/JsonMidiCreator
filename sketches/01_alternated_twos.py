from jsonmidicreator import *

two_triggers = Clip(DrumKit("808")) << Line("t::Kick, ::Kick, :_b2:Snare, ::Snare")

two_triggers >> Plot()
