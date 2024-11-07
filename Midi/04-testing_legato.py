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
from midiutil import MIDIFile

# Create a MIDI file with 1 track
midi_file = MIDIFile(1)

# Define parameters
track = 0
channel = 0
tempo = 10  # Set tempo to 120 BPM
midi_file.addTempo(track, 0, tempo)

# Add notes with 100% gate overlap
# Ensuring each note duration ends exactly when the next one starts
time = 0  # Start time in beats
duration = 1.1  # Duration for each note, matching the gap until the next note

# Adding a series of notes meant to play legato
midi_file.addNote(track, channel, 60, time, duration, volume=100)  # C4
midi_file.addNote(track, channel, 60, time + 1, duration, volume=100)  # D4
midi_file.addNote(track, channel, 60, time + 2, duration, volume=100)  # E4
midi_file.addNote(track, channel, 60, time + 3, duration, volume=100)  # F4
midi_file.addNote(track, channel, 60, time + 4, duration, volume=100)  # G4

# Save to file
with open("Midi/legato_example.mid", "wb") as output_file:
    midi_file.writeFile(output_file)
