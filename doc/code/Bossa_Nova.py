from jsonmidicreator import *

settings << Tempo(120)

percussion_preset: str = (
    # Has to add "," in order to be considered as a Line if set as string
    "pc::32," # Jazz Percussion Preset, the 32
)

clip = Clip(DrumKit("808"), Title("Bossa Nova"), percussion_preset)
# It's a 2 Measures pattern (`* 2`)
clip += Clip(
    "t::Kick, :_6, :_8, :_14,"  # Integers on Position parameter means Step
) * 2
clip += Clip(
    "t::Stick, :_6, :_12,"
    ":_1M_4, :_10,"
)
# It's possible to set an `Element` with a `Token` ("::Shaker:70:")
clip += Trigger("::Shaker:70") * 16 * 2 << OnBeat()**Velocity(110)

clip * 2 << Channel(10) >> Plot()