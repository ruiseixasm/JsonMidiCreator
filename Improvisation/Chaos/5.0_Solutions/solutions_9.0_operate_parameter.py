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

settings += Device("Blofeld")
settings << Tempo(140)
settings % Tempo() >> Print()

west_side = RP_Patterns.west_side()
west_side % [Degree()] >> Print()
west_side % TimeSignature() >> Print()


clip_solution = RS_Clip(west_side, [1], 4)
phrase_notes = clip_solution.mask(Measure(3)).operate_parameter(
        -9,
        chaos=SinX(Wrap(int())**Repeat()**Increase(1)**Modulo(7)),
        parameter=Degree()
    ).mask(Measure(3), Or(Beat(1), Beat(2))).operate_parameter(
        0,
        chaos=SinX(Wrap(int())**Repeat()**Increase(1)**Modulo(7)),
        parameter=Degree()
    ).mask(Measure(3), Beat(2)).operate_parameter(
        9,
        chaos=SinX(Wrap(int())**Repeat()**Increase(1)**Modulo(7)),
        parameter=Semitone()
    ).solution()


settings << Settings()  # Resets to Defaults
settings % Tempo() >> Print()

