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
# pip install MIDIFile
from MIDI import MIDIFile

# Initialize a new MIDI file with one track
midi_file = MIDIFile(1)  # One track in the file
track = 0  # Track index
time = 0   # Start time in beats
channel = 0
pitch = 60  # Middle C (MIDI note number)
duration = 1  # Duration in beats
volume = 100  # Max volume (0-127)

# Set up track name and tempo
midi_file.addTrackName(track, time, "Track 1")
midi_file.addTempo(track, time, 120)

# Add a note to the MIDI file
midi_file.addNote(track, channel, pitch, time, duration, volume)

# Write the file to disk
with open("output.mid", "wb") as output_file:
    midi_file.writeFile(output_file)

print("MIDI file 'output.mid' created successfully!")

