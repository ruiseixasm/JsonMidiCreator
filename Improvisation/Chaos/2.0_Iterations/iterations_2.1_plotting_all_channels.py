'''
JsonMidiCreator - Json Midi Creator is intended to be used
in conjugation with the Json Midi Player to Play composed Elements
Original Copyright (c) 2024 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
https://github.com/ruiseixasm/JsonMidiCreator
https://github.com/ruiseixasm/JsonMidiPlayer
'''
from jsonmidicreator_import import *    # This ensures src is added & JsonMidiCreator is imported

chaos = SinX(340)

def new_clip(clip: Clip) -> Clip:
    clip << Input(chaos)**Choice(30, 50, 60, 75, 100)**Value()
    return clip

ghost_notes = Note(DrumKit("Snare"), 1/16) * 16 * 8 << Velocity(50)
snare_part = Part(ghost_notes)

volume_automation = ControlChange("Volume", 100, 1/4) * 4 * 4 + Get(Beats())**Channel()

volume_automation >> Plot(iterations=10, n_button=new_clip, composition=snare_part)




