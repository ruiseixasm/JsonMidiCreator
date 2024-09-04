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

        self._dynamic_names: dict = Names.get_dict_class_names(o.Operand)

        # import operand_container as oc
        # import operand_data as od
        # import operand_element as oe
        # import operand_frame as of
        # import operand_generic as og
        # import operand_label as ol
        # import operand_operator as oo
        # import operand_staff as os
        # import operand_time as ot
        # import operand_unit as ou
        # import operand_value as ov

        # self._names: dict = {

        #     # Operand class (o)
        #     "Operand":          o.Operand,

        #     # Container class operands (oc)
        #     "Container":        oc.Container,
        #     "Sequence":         oc.Sequence,
        #     "Chain":            oc.Chain,

        #     # Data class operands (od)
        #     "Data":             od.Data,
        #     "DataSource":       od.DataSource,
        #     "DataScale":        od.DataScale,
        #     "Device":           od.Device,
        #     "Save":             od.Save,
        #     "Serialization":    od.Serialization,
        #     "Load":             od.Load,
        #     "Export":           od.Export,
        #     "PlayList":         od.PlayList,
        #     "Import":           od.Import,
        #     "Sort":             od.Sort,

        #     # Element class operands (oe)
        #     "Element":          oe.Element,
        #     "Clock":            oe.Clock,
        #     "Rest":             oe.Rest,
        #     "Note":             oe.Note,
        #     "KeyScale":         oe.KeyScale,
        #     "Chord":            oe.Chord,
        #     "Note3":            oe.Note3,
        #     "Triplet":          oe.Triplet,
        #     "Tuplet":           oe.Tuplet,
        #     "ControlChange":    oe.ControlChange,
        #     "PitchBend":        oe.PitchBend,
        #     "Aftertouch":       oe.Aftertouch,
        #     "PolyAftertouch":   oe.PolyAftertouch,
        #     "ProgramChange":    oe.ProgramChange,
        #     "Panic":            oe.Panic,

        #     # Frame class operands (of)
        #     "Frame":            of.Frame,
        #     "FrameFilter":      of.FrameFilter,
        #     "Canvas":           of.Canvas,
        #     "Blank":            of.Blank,
        #     "Inner":            of.Inner,
        #     "Outer":            of.Outer,
        #     "Odd":              of.Odd,
        #     "Even":             of.Even,
        #     "Nths":             of.Nths,
        #     "Nth":              of.Nth,
        #     "SubjectFilter":    of.SubjectFilter,
        #     "Equal":            of.Equal,
        #     "Greater":          of.Greater,
        #     "Lower":            of.Lower,
        #     "OperandFilter":    of.OperandFilter,
        #     "Subject":          of.Subject,
        #     "Iterate":          of.Iterate,
        #     "Wrapper":          of.Wrapper,
        #     "Extractor":        of.Extractor,
        #     "OperandEditor":    of.OperandEditor,
        #     "Increment":        of.Increment,

        #     # Generic class operands (og)
        #     "Generic":          og.Generic,
        #     "KeyNote":          og.KeyNote,
        #     "Controller":       og.Controller,

        #     # Label class operands (ol)
        #     "Label":            ol.Label,
        #     "Null":             ol.Null,
        #     "Dummy":            ol.Dummy,
        #     "MidiValue":        ol.MidiValue,
        #     "MSB":              ol.MSB,
        #     "LSB":              ol.LSB,
        #     "Copy":             ol.Copy,
        #     "Len":              ol.Len,
        #     "Reverse":          ol.Reverse,
        #     "First":            ol.First,
        #     "Last":             ol.Last,
        #     "Start":            ol.Start,
        #     "End":              ol.End,

        #     # Names class operands (on)
        #     "Names":            Names,

        #     # Operator class operands (oo)
        #     "Operator":         oo.Operator,
        #     "Oscillator":       oo.Oscillator,
        #     "Line":             oo.Line,

        #     # Staff class operands (os)
        #     "Staff":            os.Staff,

        #     # Time class operands (ot)
        #     "Time":             ot.Time,
        #     "Position":         ot.Position,
        #     "Old__Duration":         ot.Old__Duration,
        #     "Length":           ot.Length,
        #     "Identity":         ot.Identity,

        #     # Unit class operands (ou)
        #     "Unit":             ou.Unit,
        #     "Key":              ou.Key,
        #     "Root":             ou.Root,
        #     "Home":             ou.Home,
        #     "Tonic":            ou.Tonic,
        #     "Octave":           ou.Octave,
        #     "KeySignature":     ou.KeySignature,
        #     "Sharps":           ou.Sharps,
        #     "Flats":            ou.Flats,
        #     "Scale":            ou.Scale,
        #     "Degree":           ou.Degree,
        #     "Type":             ou.Type,
        #     "Mode":             ou.Mode,
        #     "Operation":        ou.Operation,
        #     "Transposition":    ou.Transposition,
        #     "Progression":      ou.Progression,
        #     "Inversion":        ou.Inversion,
        #     "Play":             ou.Play,
        #     "Print":            ou.Print,
        #     "PPQN":             ou.PPQN,
        #     "Midi":             ou.Midi,
        #     "Velocity":         ou.Velocity,
        #     "Pressure":         ou.Pressure,
        #     "Program":          ou.Program,
        #     "Channel":          ou.Channel,
        #     "Pitch":            ou.Pitch,
        #     "ControlValue":     ou.ControlValue,
        #     "ControlNumber":    ou.ControlNumber,

        #     # Value class operands (ov)
        #     "Value":            ov.Value,
        #     "Negative":         ov.Negative,
        #     "Quantization":     ov.Quantization,
        #     "BeatsPerMeasure":  ov.BeatsPerMeasure,
        #     "BeatNoteValue":    ov.BeatNoteValue,
        #     "NotesPerMeasure":  ov.NotesPerMeasure,
        #     "StepsPerMeasure":  ov.StepsPerMeasure,
        #     "StepsPerNote":     ov.StepsPerNote,
        #     "Tempo":            ov.Tempo,
        #     "TimeUnit":         ov.TimeUnit,
        #     "Measure":          ov.Measure,
        #     "Beat":             ov.Beat,
        #     "NoteValue":        ov.NoteValue,
        #     "Step":             ov.Step,
        #     "Dotted":           ov.Dotted,
        #     "Swing":            ov.Swing,
        #     "Gate":             ov.Gate,
        #     "Amplitude":        ov.Amplitude,
        #     "Offset":           ov.Offset

        # }

    def hasName(self, name: str) -> bool:
        if name in self._dynamic_names:
            return True
        return False
    
    def newOperand(self, name: str) -> o.Operand:
        import operand_label as ol
        if self.hasName(name):
            return self._dynamic_names[name]()
        return ol.Null()

    @staticmethod
    def find_all_subclasses(cls) -> set:
        # Create a set that includes the class itself
        subclasses = set([cls])
        # Add all subclasses recursively
        for subclass in cls.__subclasses__():
            subclasses.update(Names.find_all_subclasses(subclass))
        return subclasses           

    @staticmethod
    def get_dict_class_names(base_class) -> dict:
        # Get all subclasses of the base class recursively, including the base class itself
        all_subclasses = Names.find_all_subclasses(base_class)

        # Automatically generate a dictionary of class names to class objects
        dict_class_names = {cls.__name__: cls for cls in all_subclasses}
        
        return dict_class_names