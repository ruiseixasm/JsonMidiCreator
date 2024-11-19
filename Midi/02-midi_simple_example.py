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
# pip install midiutil
from midiutil import MIDIFile

# Create a single-track MIDI file
midi_file = MIDIFile(1)

# Set track and tempo information
track = 0
midi_file.addTrackName(track, 0, "MidiTrack 1")
midi_file.addTempo(track, 0, 120)

# Define notes and durations
notes = [
    (60, 1),  # Middle C, quarter note
    (64, 1),  # E, quarter note
    (67, 1),  # G, quarter note
    (72, 2)   # High C, half note
]

# Add each note to the track
start_time = 0
for pitch, duration in notes:
    midi_file.addNote(track, channel=0, pitch=pitch, time=start_time, duration=duration, volume=100)
    start_time += duration

# Write to file
with open("Midi/example_1.mid", "wb") as output_file:
    midi_file.writeFile(output_file)

print("MIDI file 'example.mid' created.")

