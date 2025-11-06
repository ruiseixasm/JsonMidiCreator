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

settings << Tempo(160) << Folder("examples/")


two_program_changes = \
    ProgramChange(Channel(11), Program("Viola")) \
    + ProgramChange(Channel(12), Program("Cello"))

two_program_changes >> Play()


yield_notes = YieldDegrees()
yielded_notes = Clip(yield_notes)
yielded_notes >> Plot(title="Yielded Notes", block=False)

chained_yield = YieldDegrees()**YieldDurations([1/8, 1/4, 1/8, 1/2])
chained_notes = Clip(chained_yield)
chained_notes >> Plot(title="Chained Notes", block=False)

duration_yield = YieldDurations([1/16])**YieldDegrees()**YieldDurations([1/8, 1/4, 1/8, 1/2])
duration_notes = Clip(duration_yield)
duration_notes >> Plot(title="Duration Notes", block=False)

stepped_yield = YieldDegrees()**YieldSteps()
stepped_notes = Clip(stepped_yield)
stepped_notes >> Plot(title="Stepped Notes", block=False)

YieldDegrees()**YieldPattern() >> Plot(title="Triplet Notes", block=False)

# Equivalent to the previous YieldPattern
Note(Beats(2/3)) / Measure(4) << Each(1, 3, 5)**Degree() >> Plot(title="Equivalent Triplet Notes")
