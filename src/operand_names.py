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
# Example using typing.Union (compatible with Python < 3.10)
from typing import Union
from fractions import Fraction
# Json Midi Creator Libraries
import creator as c
import operand as o

class Names(o.Operand):
    def __init__(self, operand: o.Operand = None):
        import operand_time as ot
        import operand_value as ov
        import operand_data as od
        import operand_label as ol
        import operand_frame as of
        import operand_container as oc
        import operand_element as oe

        self._names: dict = {
            # Value class operands (ov)
            "Value":            ov.Value,
            "Quantization":     ov.Quantization,
            "BeatsPerMeasure":  ov.BeatsPerMeasure,
            "BeatNoteValue":    ov.BeatNoteValue,
            "NotesPerMeasure":  ov.NotesPerMeasure,
            "StepsPerMeasure":  ov.StepsPerMeasure,
            "StepsPerNote":     ov.StepsPerNote,
            "Tempo":            ov.Tempo,
            "TimeUnit":         ov.TimeUnit,
            "Measure":          ov.Measure,
            "Beat":             ov.Beat,
            "NoteValue":        ov.NoteValue,
            "Step":             ov.Step,
            "Dotted":           ov.Dotted,
            "Swing":            ov.Swing,
            "Gate":             ov.Gate,
            "Amplitude":        ov.Amplitude,
            "Offset":           ov.Offset,
            # Element class operands (oe)
            "Element":          oe.Element,
            "Clock":            oe.Clock,
            "Rest":             oe.Rest,
            "Note":             oe.Note,
            "KeyScale":         oe.KeyScale,
            "Chord":            oe.Chord,
            "Note3":            oe.Note3,
            "Triplet":          oe.Triplet,
            "Tuplet":           oe.Tuplet,
            "ControlChange":    oe.ControlChange,
            "PitchBend":        oe.PitchBend,
            "Aftertouch":       oe.Aftertouch,
            "PolyAftertouch":   oe.PolyAftertouch,
            "ProgramChange":    oe.ProgramChange,
            "Panic":            oe.Panic
        }

    def hasName(self, name: str) -> bool:
        if name in self._names:
            return True
        return False
    
    def newOperand(self, name: str) -> o.Operand:
        import operand_label as ol
        if self.hasName(name):
            return self._names[name]()
        return ol.Null()
        