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
src_path = os.path.join(os.path.dirname(__file__), '../..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *



# https://youtu.be/gDS6oerX0wY?si=n3TQLqnub8xBLGIh


device_list = settings % Devices() % list() >> Print()
device_list.insert(0, "Blofeld")
device_list >> Print()
settings << Device(device_list)
settings << TimeSignature(3, 4) << Tempo(90)

chords = Chord() * 4 << Once("I", "IV", "V", "I")**Degree()
# chords >> Play()

chord_notes_i = Chord(Degree("I")) % Clip()
chord_notes_iv = Chord(Degree("IV")) % Clip()
chord_notes_v = Chord(Degree("V")) % Clip()
# chord_notes_i * chord_notes_iv * chord_notes_v * chord_notes_i * 4 >> Play()

decomposed_chords = chords.copy().decompose()
# decomposed_chords >> Play()

stacked_notes = decomposed_chords.copy(1/4).stack() # Each single note is now 1/4 note
# stacked_notes >> Play()

measure_operations = [
    (Measure(0), Operate(Octave(1), "+")),
    (Measure(1), Operate(Octave(1), "+"), Reverse(), Rotate(-1)),
    (Measure(2), Reverse(), Rotate(-1)),
    (Measure(3), Rotate(-1), Beat(0), Operate(Octave(1), "+"), Link()),
    (Measure(3), Greater(Beat(0)), Erase()),
    (And(Measure(1), Beat(2)), Operate(Octave(1), "-")),
    (And(Measure(2), Beat(2)), Operate(Degree(5)), Operate(Octave(1), "+"))
]

chords_melody = stacked_notes.copy()
chords_melody >> measure_operations

# chords_melody >> Measure(2) >> Play()

# Total Notes = 3 * 4 - 2 = 10 notes
chords_melody.len() >> Print()
chords_melody * 4 >> Play()
# chords_melody * 4 >> MidiExport("Midi/21_melody_from_chords_1.2.mid")

# ADD SOME RHYTHM

chords_melody >> Measure(0) << Once(dotted_quarter, eight) >> Stack()
chords_melody >> Measure(2) << Once(dotted_quarter, eight) >> Stack()

chords_melody * 4 >> Play()


