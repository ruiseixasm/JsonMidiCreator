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
import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

# DRUM PATTERNS

drums = Drums()
# four_on_floor = drums.four_on_the_floor()
# four_on_floor * 8 >> Play()

# boom_bap = drums.boom_bap()
# boom_bap * 4 >> Play()

# backbeat = drums.backbeat()
# backbeat * 8 >> Play()

# half_groove = drums.half_time_groove()
# half_groove * 8 >> Play()

# d_beat = drums.d_beat()
# d_beat * 8 >> Play()

# reggae_drop = drums.reggae_one_drop()
# reggae_drop * 8 >> Play()

# funk_shuffle = drums.funk_shuffle()
# funk_shuffle * 8 >> Play()

# breakbeat = drums.breakbeat()
# breakbeat * 8 >> Play()

# bossa_nova = drums.bossa_nova()
# bossa_nova * 4 >> Play()

# blast_beat = drums.blast_beat()
# blast_beat * 8 >> Play()


# MELODIC PATTERNS

melodies = Melodies()

# sequence = melodies.sequence()
# sequence * 4 >> Play()

# arpeggio = melodies.arpeggio()
# arpeggio * 4 >> Play()

# passing_tones = melodies.passing_tones()
# passing_tones * 4 >> Play()

# pedal_tones = melodies.pedal_tones()
# pedal_tones * 4 >> Play()

# call_response = melodies.call_response()
# call_response * 4 >> Play()

# ostinato = melodies.ostinato()
# ostinato * 4 >> Play()

# riff = melodies.riff()
# riff * 4 >> Play()

# chromatic_run = melodies.chromatic_run()
# chromatic_run * 4 >> Play()

# syncopation = melodies.syncopation()
# syncopation * 4 >> Play()

# modal_interchange = melodies.modal_interchange()
# modal_interchange * 4 >> Play()



# AUTOMATION PATTERNS

automations = Automations()


fade_out = automations.fade_in_out()
fade_out >> Play()

fade_in = automations.fade_in_out(Value(0), Value(100))
fade_in >> Play()

