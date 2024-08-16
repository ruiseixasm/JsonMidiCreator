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
from operand import Operand
import operand_unit as ou
import operand_value as ov
import operand_length as ol
import operand_data as od
import operand_generic as og
import operand_frame as of
import operand_tag as ot


class Staff(Operand):
    def __init__(self):
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._measure: ov.Measure                   = None
        self._tempo: ov.Tempo                       = None
        # Time Signature is BeatsPerMeasure / BeatNoteValue like 4/4
        self._beats_per_measure: ov.BeatsPerMeasure = None
        self._beat_note_value: ov.BeatNoteValue     = None
        # Key Signature is an alias of Sharps and Flats of a Scale
        self._scale: og.Scale                       = None
        self._quantization: ov.Quantization         = None
        self._duration: ol.Duration                 = None
        self._key: ou.Key                           = None
        self._octave: ou.Octave                     = None
        self._velocity: ou.Velocity                 = None
        self._midi_cc: ou.MidiCC                    = None
        self._channel: ou.Channel                   = None
        self._device: od.Device                     = None

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():            return self % (operand % Operand())
            # Direct Values
            case ov.Measure():          return self._measure
            case ov.Tempo():            return self._tempo
            case ov.BeatsPerMeasure():  return self._beats_per_measure
            case ov.BeatNoteValue():    return self._beat_note_value
            case og.Scale():            return self._scale
            case ov.Quantization():     return self._quantization
            case ol.Duration():         return self._duration
            case ou.Key():              return self._key
            case ou.Octave():           return self._octave
            case ou.Velocity():         return self._velocity
            case ou.MidiCC():           return self._midi_cc
            case ou.Channel():          return self._channel
            case od.Device():           return self._device
            # Calculated Values
            case ov.NotesPerMeasure():
                return ov.NotesPerMeasure((self % ov.BeatsPerMeasure() % float()) * (self % ov.BeatNoteValue() % float()))
            case ov.StepsPerMeasure():
                return ov.StepsPerMeasure((self % ov.StepsPerNote() % float()) * (self % ov.NotesPerMeasure() % float()))
            case ov.StepsPerNote():
                return ov.StepsPerNote(1 / (self._quantization % float()))
        return ot.Null()

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "measures": self._measure % float(),
            "tempo": self._tempo % int(),
            "beats_per_measure": self._beats_per_measure % float(),
            "beat_note_value": self._beat_note_value % float(),
            "scale": self._scale.getSerialization(),
            "quantization": self._quantization % float(),
            "duration": self._duration.getSerialization(),
            "key": self._key % int(),
            "octave": self._octave % int(),
            "velocity": self._velocity % int(),
            "midi_cc": self._midi_cc % int(),
            "channel": self._channel % int(),
            "device": self._device % list()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measures" in serialization and "tempo" in serialization and
            "quantization" in serialization and "beats_per_measure" in serialization and "beat_note_value" in serialization and
            "scale" in serialization and "duration" in serialization and "key" in serialization and
            "octave" in serialization and "velocity" in serialization and "midi_cc" in serialization and
            "channel" in serialization and "device" in serialization):

            self._measures = ov.Measure(serialization["measures"])
            self._tempo = ov.Tempo(serialization["tempo"])
            self._beats_per_measure = ov.BeatsPerMeasure(serialization["beats_per_measure"])
            self._beat_note_value = ov.BeatNoteValue(serialization["beat_note_value"])
            self._scale = og.Scale().loadSerialization(serialization["scale"])
            self._quantization = ov.Quantization(serialization["quantization"])
            self._duration = ol.Duration(serialization["duration"])
            self._key = ou.Key(serialization["key"])
            self._octave = ou.Octave(serialization["octave"])
            self._velocity = ou.Velocity(serialization["velocity"])
            self._midi_cc = ou.MidiCC(serialization["midi_cc"])
            self._channel = ou.Channel(serialization["channel"])
            self._device = od.Device(serialization["device"])
        return self
        
    def __lshift__(self, operand: Operand) -> 'Staff':
        match operand:
            case ov.Measure():          self._measure = operand
            case ov.Tempo():            self._tempo = operand
            case ov.BeatsPerMeasure():  self._beats_per_measure = operand
            case ov.BeatNoteValue():    self._beat_note_value = operand
            case og.Scale():            self._scale = operand
            case ov.Quantization():     self._quantization = operand    # Note Value
            case ol.Duration():         self._duration = operand
            case ou.Key():              self._key = operand
            case ou.Octave():           self._octave = operand
            case ou.Velocity():         self._velocity = operand
            case ou.MidiCC():           self._midi_cc = operand
            case ou.Channel():          self._channel = operand
            case od.Device():           self._device = operand
            # Calculated Values
            case ov.NotesPerMeasure():
                self._beat_note_value = ov.BeatNoteValue( (operand % float()) / (self % ov.BeatsPerMeasure()) )
            case ov.StepsPerMeasure():
                self._quantization = ov.Quantization( (self % ov.NotesPerMeasure()) / (operand % float()) )
            case ov.StepsPerNote():
                self._quantization = ov.Quantization( 1 / (operand % float()) )
        return self

# Set the Default Staff values here.
global_staff: Staff = Staff() #    Time Signature is BeatsPerMeasure / BeatNoteValue like 4/4!
global_staff << ov.Measure(8) << ov.Tempo(120.0) << ov.BeatsPerMeasure(4) << ov.BeatNoteValue(1/4) \
    << (og.Scale() << ou.Key("C") << ou.CScale("Major")) << ov.Quantization(1/16) \
    << (ol.Duration() << ov.NoteValue(1/4)) << ou.Key("C") << ou.Octave(4) \
    << ou.Velocity(100) << ou.MidiCC("Pan") << ou.Channel(1) << od.Device(["FLUID", "Midi", "Port", "Synth"])
