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
src_path = os.path.join(os.path.dirname(__file__), '../../../../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *

settings << KeySignature(-1) << Tempo(130)
motif = Note("B", 1/8) + Note("C", 5, 1/16) + Note("B", 1/16) + Note("A", 1/8)

end_point_1 = Note("G", 1/8) + Note("A", Dotted(1/4)) + Note("F", 1/8)
end_point_2 = Note("E", 1/8) + Note("D", 1/2)

# motif >> end_point_1 >> motif >> end_point_2 >> Play()

motif % NoteValue() >> Print(0)
end_point_1 % NoteValue() >> Print(0)
end_point_2 % NoteValue() >> Print(0)

motif << Gate(1)
end_point_1 << Gate(1)
end_point_2 << Nth(1)**Gate(1)
end_point_3 = Note("A", 1/8, Gate(1)) * 5 + Iterate()**0
measure_1 = Note("C", 5, 1/1)
measure_2 = Note("C", 5, Gate(1)) * 4 + Foreach(0, 3, -2, 1) << Nth(4)**Gate(0.9)

ProgramChange(75, NoteValue(Measures(1))) >> motif >> end_point_1 >> motif >> end_point_2 >> motif >> end_point_3 >> measure_1 \
>> motif + 4 >> end_point_1 + 4 >> measure_2 >> motif >> end_point_1 >> measure_1 - 4 << Match(Measures(1 + 6))**Match(Beats(3))**Key("G") >> ProgramChange(1, Beats(2)) >> Play()
