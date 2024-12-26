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


# Global Staff setting up
staff << Tempo(60)

chord = Chord() << NoteValue(2) << Gate(1) >> Save("json/_Save_4.1_control_change.json")
controller = (Oscillator(Value()) << Offset(64) << Amplitude(50) \
              | ControlChange("Pan") * (2*16 + 1) << Iterate()**Measures()**NoteValue()**Steps()) \
                >> Save("json/_Save_4.2_control_change.json")
    
chord + controller >> Print() >> Play(1) >> Export("json/_Export_4.1_control_change.json")


oscillator = Oscillator(Bend()) << Amplitude(8191 / 2)
pitch_bend = PitchBend() * (2*16 + 1) << Wrap(Position())**Wrap(NoteValue())**Iterate()**Steps() << Extract(Bend())**Wrap(oscillator)**Wrap(PitchBend())**Iterate(4)**Steps()

chord + pitch_bend >> Play(1) >> Save("json/_Save_4.2_pitch_bend.json") >> Export("json/_Export_4.2_pitch_bend.json")
