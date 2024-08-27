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
        import operand_container as oc
        import operand_data as od
        import operand_element as oe
        import operand_frame as of
        import operand_generic as og
        import operand_operator as oo
        import operand_staff as os
        import operand_time as ot
        import operand_unit as ou
        import operand_value as ov

        self._names: dict = {

            # Operand class (o)
            "Operand":          o.Operand,

            # Container class operands (oc)
            "Container":        oc.Container,
            "Sequence":         oc.Sequence,
            "Chain":            oc.Chain,

            # Data class operands (od)
            "Data":             od.Data,
            "DataSource":       od.DataSource,
            "DataScale":        od.DataScale,
            "Device":           od.Device,
            "Save":             od.Save,
            "Serialization":    od.Serialization,
            "Load":             od.Load,
            "Export":           od.Export,
            "PlayList":         od.PlayList,
            "Import":           od.Import,
            "Function":         od.Function,
            "Copy":             od.Copy,
            "Len":              od.Len,
            "Sort":             od.Sort,
            "Reverse":          od.Reverse,
            "First":            od.First,
            "Last":             od.Last,
            "Start":            od.Start,
            "End":              od.End,

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
            "Panic":            oe.Panic,

            # Frame class operands (of)
            "Frame":            of.Frame,
            "FrameFilter":      of.FrameFilter,
            "Canvas":           of.Canvas,
            "Blank":            of.Blank,
            "Inner":            of.Inner,
            "Outer":            of.Outer,
            "Odd":              of.Odd,
            "Even":             of.Even,
            "Nths":             of.Nths,
            "Nth":              of.Nth,
            "SubjectFilter":    of.SubjectFilter,
            "Equal":            of.Equal,
            "Greater":          of.Greater,
            "Lower":            of.Lower,
            "OperandFilter":    of.OperandFilter,
            "Subject":          of.Subject,
            "Iterate":          of.Iterate,
            "Wrapper":          of.Wrapper,
            "Extractor":        of.Extractor,
            "OperandEditor":    of.OperandEditor,
            "Increment":        of.Increment,

            # Generic class operands (og)
            "Generic":          og.Generic,
            "KeyNote":          og.KeyNote,
            "Controller":       og.Controller,

            # Operator class operands (oo)
            "Operator":         oo.Operator,
            "Oscillator":       oo.Oscillator,
            "Line":             oo.Line,

            # Staff class operands (os)
            "Staff":            os.Staff,

            # Time class operands (ot)
            "Time":             ot.Time,
            "Position":         ot.Position,
            "Duration":         ot.Duration,
            "Length":           ot.Length,
            "Identity":         ot.Identity,

            # Unit class operands (ou)
            "Unit":             ou.Unit,
            "Key":              ou.Key,
            "Root":             ou.Root,
            "Home":             ou.Home,
            "Tonic":            ou.Tonic,
            "Octave":           ou.Octave,
            "KeySignature":     ou.KeySignature,
            "Sharps":           ou.Sharps,
            "Flats":            ou.Flats,
            "Scale":            ou.Scale,
            "Degree":           ou.Degree,
            "Type":             ou.Type,
            "Mode":             ou.Mode,
            "Operation":        ou.Operation,
            "Transposition":    ou.Transposition,
            "Progression":      ou.Progression,
            "Inversion":        ou.Inversion,
            "Play":             ou.Play,
            "Midi":             ou.Midi,
            "Velocity":         ou.Velocity,
            "Pressure":         ou.Pressure,
            "Program":          ou.Program,
            "Channel":          ou.Channel,
            "Pitch":            ou.Pitch,
            "ControlValue":     ou.ControlValue,
            "ControlNumber":    ou.ControlNumber,

            # Value class operands (ov)
            "Value":            ov.Value,
            "Negative":         ov.Negative,
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
            "Offset":           ov.Offset

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
        