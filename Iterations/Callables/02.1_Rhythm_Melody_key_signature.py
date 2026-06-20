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

settings << Tempo(137)

real_motif = Clip(
    "n:2:C#7, :6:E7, :2:C#7, :6:B6, :2:C#7, :6:E7, :2:C#7, :6:B6, :2:C#7, :6:E7, :2:E6, :6:F#"
) << Name("Real Motif")
# real_motif >> Plot()


key_signature_setter = I_Setter(Pipe()**KeySignature(), Counter()**int(-7), global_setting=True)
key_motif = real_motif >> Plot(n_button=key_signature_setter.new_iteration)
