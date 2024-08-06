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
# Json Midi Creator Libraries
import operand_staff as os
import operand_unit as ou
import operand_value as ov
import operand_length as ol
import operand_data as od


# Set the Default Staff values here
                                    # Time Signature is BeatsPerMeasure / BeatNoteValue like 4/4
os.global_staff << ov.Measure(8) << ou.Tempo(120) << ov.BeatsPerMeasure(4) << ov.BeatNoteValue(1/4) \
    << ov.Quantization(1/16) << (ol.Duration() << ov.NoteValue(1/4)) << ou.Key("C") << ou.Octave(4) \
    << ou.Velocity(100) << ou.ValueUnit(64) << ou.Channel(1) << od.Device(["FLUID", "Midi", "Port", "Synth"])
                                      # 64 for CC Center

