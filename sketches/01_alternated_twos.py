from jsonmidicreator import *

two_triggers = Clip() << Line("t::Kick, t::Kick")

two_triggers >> Plot()
