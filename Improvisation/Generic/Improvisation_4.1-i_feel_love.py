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

# https://youtu.be/sIBSN1_9Geo?si=_AW-FASDVtHK8irY

# Global Staff setting up
defaults << Tempo(120)
defaults << Minor()

first_notes = Note(1/8) * 3 << Duration(1/16)

# Sets the right C minor Key Signature
first_notes << Use(Key("C")) << None # Resets the Tonic key from A to C
first_notes % KeySignature() % int() >> Print()
first_notes % KeySignature() % str() >> Print()


# C - G - Bb | C minor
first_notes << Cycle("C", "G", "B")**Key()
first_notes[0] % Degree() % int() >> Print()
first_notes[1] % Degree() % int() >> Print()
first_notes[2] % Degree() % int() >> Print()

second_notes = first_notes + Step(1)
patter_notes = first_notes + second_notes + Even()**Octave(1)

final_pattern = patter_notes.filter(Nth(1, 2)) / patter_notes / 2
final_pattern * 8 >> P >> MidiExport("Midi/improvisation_4.1.mid")
