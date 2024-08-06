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
from operand import *
from operand_unit import *
from operand_value import *
from operand_generic import *
from operand_staff import global_staff


# Set the Default Staff values here
                                            # Time Signature is BeatsPerMeasure / BeatNoteValue like 4/4
global_staff << Measure(8) << Tempo(120) << BeatsPerMeasure(4) << BeatNoteValue(1/4)
global_staff << Quantization(1/16) << (Duration() << NoteValue(1/4)) << Key("C") << Octave(4) << Velocity(100)
global_staff << ValueUnit(64) << Channel(1) << Device(["FLUID", "Midi", "Port", "Synth"])
                # 64 for CC Center

