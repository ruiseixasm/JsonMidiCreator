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

# Determine the operating system
import platform
current_os = platform.system()
if current_os == "Windows":
    global_staff << Device(["loop", "Microsoft"])   # Microsoft GS Wavetable Synth
elif current_os == "Darwin":  # macOS
    global_staff << Device(["Apple"])               # Apple DLS Synthesizer
else:  # Assume Linux/Unix
    global_staff << Device(["VMPK", "FLUID"])       # FLUID Synth


# Global Staff setting up
global_staff << Tempo(110) << Measure(6)

# Set the default single Clock for the entire Staff Length
single_clock = Clock() >> Save("json/_Clock_jsonMidiCreator.json") >> Print()

# Multiple individual Notes creation and sequentially played
first_note = Note() << (Position() << Beat(3) << Step(2)) << (TimeLength() << NoteValue(1/2)) >> Save("json/_Note_jsonMidiCreator.json")
multi_notes = Null() >> first_note * 3 >> Play(0) >> Save("json/_Many_jsonMidiCreator.json") >> Export("json/_Play2_jsonMidiPlayer.json")

first_note << Key("F") >> Play()
first_note << Load("_Note_jsonMidiCreator.json")

Note3() << (Duration() << NoteValue(1/8)) >> Play(1)

# Base Note creation to be used in the Sequencer
base_note = Note() << (Duration() << Dotted(1/64))

# Creation and configuration of first Sequencer
first_sequence = Sequence() << Measure(1)
first_sequence << base_note * 8 // Step(1) << Inner()**Channel(10) >> Save("json/_Sequence_jsonMidiCreator.json")

# Creation and configuration of second Sequencer
second_sequence = first_sequence.copy()
second_sequence << (Position() << Measure(2))
second_sequence /= Inner()**(Position() << Identity() << Step(2))
second_sequence /= Inner()**(Duration() << Identity() << NoteValue(2))

# Creations, aggregation of both Sequences in a Many element and respective Play
all_elements = Many(first_sequence) + Many(second_sequence)
all_elements += (TimeLength() << Beat(2) >> first_note) + single_clock
all_elements >> Print() >> Play(1) >> Export("json/_Play_jsonMidiPlayer.json")

