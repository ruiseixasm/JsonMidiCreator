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
import json
import enum
# Json Midi Creator Libraries
import creator as c
from operand import Operand
import operand_staff as os
import operand_unit as ou
import operand_value as ov
import operand_length as ol
import operand_data as od
import operand_tag as ot
import operand_frame as of
import operand_generic as og
import operand_container as oc
import operand_frame as of

class Element(Operand):
    def __init__(self):
        self._position: ol.Position         = ol.Position()
        self._time_length: ol.TimeLength    = ol.TimeLength()
        self._channel: ou.Channel           = ou.Channel()
        self._device: od.Device             = od.Device()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case ol.Position():     return self._position
            case ov.TimeUnit():     return self._position % operand
            case ol.TimeLength():   return self._time_length
            case ou.Channel():      return self._channel
            case od.Device():       return self._device
            case _:                 return ot.Null()

    def getPlayList(self, position: ol.Position = None) -> list:
        return []

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "position": self._position.getSerialization(),
            "time_length": self._time_length.getSerialization(),
            "channel": self._channel % int(),
            "device": self._device % list()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "position" in serialization and "time_length" in serialization and
            "channel" in serialization and "device" in serialization):

            self._position  = ol.Position().loadSerialization(serialization["position"])
            self._time_length    = ol.TimeLength().loadSerialization(serialization["time_length"])
            self._channel   = ou.Channel(serialization["channel"])
            self._device    = od.Device(serialization["device"])
        return self
        
    def copy(self) -> 'Element':
        return self.__class__() << self._position.copy() << self._time_length.copy() << self._channel << self._device

    def __lshift__(self, operand: Operand) -> 'Element':
        match operand:
            case ol.Position(): self._position = operand
            case ov.TimeUnit(): self._position << operand
            case ol.TimeLength(): self._time_length = operand
            case ou.Channel(): self._channel = operand
            case od.Device(): self._device = operand
            case od.Load():
                serialization = c.loadJsonMidiCreator(operand % str())
                self.loadSerialization(serialization)
            case oc.Chain():
                for single_operand in operand:
                    self << single_operand
        return self

    # operand is the pusher
    def __rrshift__(self, operand: Operand) -> 'Element':
        match operand:
            case ot.Null(): pass
            case oc.Many():
                last_element = operand.lastElement()
                if type(last_element) != ot.Null:
                    self << last_element % ol.Position() + last_element % ol.TimeLength()
            case Element(): self << operand % ol.Position() + operand % ol.TimeLength()
            case ol.Position(): self << operand
            case ol.TimeLength(): self += ol.Position() << operand
        return self

    def __add__(self, operand: Operand) -> 'Element':
        match operand:
            case Element():
                return oc.Many(self.copy(), operand.copy())
            case oc.Many():
                return oc.Many(self.copy(), operand.copy() % list())
            case Operand():
                element_copy = self.copy()
                return element_copy << element_copy % operand + operand
        return self

    def __sub__(self, operand: Operand) -> 'Element':
        element_copy = self.copy()
        return element_copy << element_copy % operand - operand

    def __mul__(self, operand: Operand) -> 'Element':
        element_copy = self.copy()
        return element_copy << element_copy % operand * operand

    def __truediv__(self, operand: Operand) -> 'Element':
        element_copy = self.copy()
        return element_copy << element_copy % operand / operand

class ClockModes(enum.Enum):
    single  = 1
    first   = 2
    middle  = 3
    last    = 4
    resume  = 5

class Clock(Element):
    def __init__(self):
        super().__init__()
        self._time_length = ol.TimeLength() << ov.Measure(os.global_staff % ov.Measure() % int())
        self._mode: ClockModes = ClockModes.single
        self._pulses_per_quarternote: int = 24

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ClockModes():  return self._mode
            case int():         return self._pulses_per_quarternote
            case _:             return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        
        clock_position: ol.Position = self % ol.Position() + ol.Position() if position is None else position
        clock_length = ol.TimeLength() << ov.Measure(os.global_staff % ov.Measure() % int()) \
                if self._time_length is None else self._time_length
        clock_mode = ClockModes.single if self._mode is None else self._mode
        if clock_mode == ClockModes.single:
            clock_position = ol.Position()
            clock_length = ol.TimeLength() << ov.Measure(os.global_staff % ov.Measure() % int())
        device = self % od.Device()

        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note * (os.global_staff % ov.BeatNoteValue() % float())
        pulses_per_measure = pulses_per_beat * (os.global_staff % ov.BeatsPerMeasure() % float())
        clock_pulses = round(pulses_per_measure * (clock_length % ov.Measure() % float()))

        single_measure_ms = ov.Measure(1).getTime_ms()
        clock_start_ms = clock_position.getTime_ms()
        clock_stop_ms = clock_start_ms + clock_length.getTime_ms()

        """
            System Real-Time Message         Status Byte 
            ------------------------         -----------
            Timing Clock                         F8
            Start Sequence                       FA
            Continue Sequence                    FB
            Stop Sequence                        FC
            Active Sensing                       FE
            System Reset                         FF
        """

        play_list = [
                {
                    "time_ms": round(clock_start_ms, 3),
                    "midi_message": {
                        "status_byte": 0xFA if clock_mode == ClockModes.single or clock_mode == ClockModes.first
                            else 0xFB if clock_mode == ClockModes.resume else 0xF8,
                        "device": device % list()
                    }
                }
            ]

        for clock_pulse in range(1, clock_pulses):
            play_list.append(
                {
                    "time_ms": round(clock_start_ms + single_measure_ms \
                                     * (clock_length % ov.Measure() % int()) * clock_pulse / clock_pulses, 3),
                    "midi_message": {
                        "status_byte": 0xF8,
                        "device": device % list()
                    }
                }
            )

        if clock_mode == ClockModes.single or clock_mode == ClockModes.last:
            play_list.append(
                {
                    "time_ms": round(clock_stop_ms, 3),
                    "midi_message": {
                        "status_byte": 0xFC,
                        "device": device % list()
                    }
                }
            )
        
        return play_list

    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["mode"] = self._mode.value
        element_serialization["pulses_per_quarternote"] = self._pulses_per_quarternote
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "mode" in serialization and "pulses_per_quarternote" in serialization):

            super().loadSerialization(serialization)
            self._mode = ClockModes(serialization["mode"])
            self._pulses_per_quarternote = serialization["pulses_per_quarternote"]
        return self

    def copy(self) -> 'Clock':
        return super().copy() << self._mode << self._device << self._pulses_per_quarternote

    def __lshift__(self, operand: Operand) -> 'Clock':
        match operand:
            case ol.Position(): self._position = ol.Position() << ov.Measure(operand % ov.Measure() % int())
            case ol.TimeLength(): self._time_length = ol.TimeLength() << ov.Measure(operand % ov.Measure() % int())
            case ClockModes(): self._mode = operand
            case int(): self._pulses_per_quarternote = operand
        return self

class Rest(Element):
    pass

class Note(Element):
    def __init__(self):
        super().__init__()
        self._duration: ol.Duration = ol.Duration() << os.global_staff % ol.Duration()
        self._key_note: og.KeyNote  = og.KeyNote() \
            << ou.Key( os.global_staff % ou.Key() % int() ) << ou.Octave( os.global_staff % ou.Octave() % int() )
        self._velocity: ou.Velocity = ou.Velocity( os.global_staff % ou.Velocity() % int() )
        self._gate: ov.Gate         = ov.Gate(.90)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ol.Duration():     return self._duration
            case ov.NoteValue():    return self._duration % operand
            case og.KeyNote():      return self._key_note
            case ou.Key() | ou.Octave():
                                    return self._key_note % operand
            case ou.Velocity():     return self._velocity
            case ov.Gate():         return self._gate
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        
        note_position: ol.Position  = self % ol.Position() + ol.Position() if position is None else position
        duration: ol.Duration       = self % ol.Duration()
        key_note_midi: int          = (self % og.KeyNote()).getMidi__key_note()
        velocity_int: int           = self % ou.Velocity() % int()
        channel_int: int            = self % ou.Channel() % int()
        device_list: list           = self % od.Device() % list()

        on_time_ms = note_position.getTime_ms()
        off_time_ms = on_time_ms + self._gate % float() * duration.getTime_ms()
        return [
                {
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & (channel_int - 1),
                        "data_byte_1": key_note_midi,
                        "data_byte_2": velocity_int,
                        "device": device_list
                    }
                },
                {
                    "time_ms": round(off_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & (channel_int - 1),
                        "data_byte_1": key_note_midi,
                        "data_byte_2": 0,
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["duration"] = self._duration.getSerialization()
        element_serialization["key_note"] = self._key_note.getSerialization()
        element_serialization["velocity"] = self._velocity % int()
        element_serialization["gate"] = self._gate % float()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "duration" in serialization and "key_note" in serialization and
            "velocity" in serialization and "gate" in serialization):

            super().loadSerialization(serialization)
            self._duration = ol.Duration().loadSerialization(serialization["duration"])
            self._key_note = og.KeyNote().loadSerialization(serialization["key_note"])
            self._velocity = ou.Velocity(serialization["velocity"])
            self._gate = ov.Gate(serialization["gate"])
        return self
      
    def copy(self) -> 'Note':
        return super().copy() << self._duration.copy() << self._key_note.copy() << self._velocity << self._gate

    def __lshift__(self, operand: Operand) -> 'Note':
        match operand:
            case ol.Duration():     self._duration = operand
            case ov.NoteValue():    self._duration << operand
            case og.KeyNote():      self._key_note = operand
            case ou.Key() | ou.Octave():
                                    self._key_note << operand
            case ou.Velocity():     self._velocity = operand
            case ov.Gate():         self._gate = operand
            case _: super().__lshift__(operand)
        return self

    def __mul__(self, operand: Operand) -> oc.Many | Element:
        match operand:
            case int():
                multi_notes = []
                for _ in range(0, operand):
                    multi_notes.append(self.copy())
                return oc.Many(multi_notes)
        return super().__mul__(self)

class Note3(Note):
    """
    A Note3() is the repetition of a given Note three times on a row
    Triplets have each Note Duration set to the following Values:
        | 1T    = (1    - 1/4)   = 3/4
        | 1/2T  = (1/2  - 1/8)   = 3/8
        | 1/4T  = (1/4  - 1/16)  = 3/16
        | 1/8T  = (1/8  - 1/32)  = 3/32
        | 1/16T = (1/16 - 1/64)  = 3/64
        | 1/32T = (1/32 - 1/128) = 3/128
    """
    def __init__(self):
        super().__init__()
        self._duration *= (2/3) # 3 instead of 2
        self._gate      = ov.Gate(.50)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ol.Duration():     return self._duration * (3/2)
            case ov.NoteValue():    return self._duration * (3/2) % operand
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        note_position: ol.Position = ol.Position() if position is None else position
        triplet_playlist = []
        for _ in range(3):
            triplet_playlist.extend(super().getPlayList(note_position))
            note_position += self._duration
        return triplet_playlist
    
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: Operand) -> 'Note':
        match operand:
            case ol.Duration():     self._duration = operand * (2/3)
            case ov.NoteValue():    self._duration << operand * (2/3)
            case _: super().__lshift__(operand)
        return self

class Chord(Note):
    def __init__(self, size: int = None):   # 0xF2 - Song ol.Position
        super().__init__()
        self._scale: ou.Scale = os.global_staff % og.KeyScale() % ou.Scale()   # Default Scale for Chords
        self._mode: ou.Mode = ou.Mode(1)    # 1 for Tonic
        self._inversion: ou.Inversion = ou.Inversion()
        self._size: int = 3 if size is None else size
        # Need to add inversions and other parameters

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ou.Scale():        return self._scale
            case ou.Mode():         return self._mode
            case ou.Inversion():    return self._inversion
            case int():             return self._size
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        note_position: ol.Position  = self % ol.Position() + ol.Position() if position is None else position

        root_key_note = self % og.KeyNote()
        chord_key_notes = []
        for key_note_i in range(self._size):
            chromatic_transposition = self._scale.transpose((self._mode % int() - 1) + key_note_i * 2)
            chord_key_notes.append(root_key_note + chromatic_transposition)

        # Where the inversions are done
        first_key_note = chord_key_notes[self._inversion % int()]
        not_first_key_note = True
        while not_first_key_note:
            not_first_key_note = False
            for key_note in chord_key_notes:
                if key_note < first_key_note:
                    if (key_note + ou.Octave(1)).getMidi__key_note() > 127:
                        break
                    else:
                        key_note << key_note % ou.Octave() + 1
                        not_first_key_note = True

        chord_playlist = []
        for key_note in chord_key_notes:
            self << key_note
            chord_playlist.extend(super().getPlayList(note_position))
        self << root_key_note

        return chord_playlist
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["scale"] = self._scale % int()
        element_serialization["mode"] = self._mode % int()
        element_serialization["inversion"] = self._inversion % int()
        element_serialization["size"] = self._size
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "scale" in serialization and "mode" in serialization and
            "inversion" in serialization and "size" in serialization):

            super().loadSerialization(serialization)
            self._scale = ou.Scale(serialization["scale"])
            self._mode = ou.Mode(serialization["mode"])
            self._inversion = ou.Inversion(serialization["inversion"])
            self._size = serialization["size"]
        return self
      
    def copy(self) -> 'Chord':
        return super().copy() << self._scale.copy() << self._mode << self._size

    def __lshift__(self, operand: Operand) -> 'Chord':
        match operand:
            case ou.Scale():        self._scale = operand
            case ou.Mode():         self._mode = operand
            case ou.Inversion():    self._inversion = operand
            case int():             self._size = operand
            case _: super().__lshift__(operand)
        return self

class ControlChange(Element):
    def __init__(self):
        super().__init__()
        self._controller: og.Controller = og.Controller()
        self._midi_value: ou.MidiValue  = ou.MidiValue()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case og.Controller():   return self._controller
            case ou.MidiValue():    return self._midi_value
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        
        note_position: ol.Position  = self % ol.Position() + ol.Position() if position is None else position
        controller_int: int         = self % og.Controller() % int()
        value_midi: int             = (self % ou.MidiValue()).getMidi__midi_value()
        channel_int: int            = self % ou.Channel() % int()
        device_list: list           = self % od.Device() % list()

        on_time_ms = note_position.getTime_ms()
        return [
                {
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & (channel_int - 1),
                        "data_byte_1": controller_int,
                        "data_byte_2": value_midi,
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["controller"] = self._controller.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "controller" in serialization):

            super().loadSerialization(serialization)
            self._controller = og.Controller().loadSerialization(serialization["controller"])
        return self
      
    def copy(self) -> 'ControlChange':
        return super().copy() << self._controller << self._midi_value

    def __lshift__(self, operand: Operand) -> 'ControlChange':
        match operand:
            case og.Controller():
                self._controller = operand
            case ou.MidiCC() | ou.MidiValue():
                self._controller << operand
            case _: super().__lshift__(operand)
        return self

    def __mul__(self, operand: Operand) -> oc.Many | Element:
        match operand:
            case int():
                multi_control_changes = []
                for _ in range(0, operand):
                    multi_control_changes.append(self.copy())
                return oc.Many(multi_control_changes)
        return super().__mul__(self)

class PitchBend(Element):
    def __init__(self):
        super().__init__()
        self._pitch: ou.Pitch = ou.Pitch()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ou.Pitch():       return self._pitch
            case _:             return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        
        note_position: ol.Position  = self % ol.Position() + ol.Position() if position is None else position
        pitch_list_midi: list[int]  = (self % ou.Pitch()).getMidi__pitch_pair()
        channel_int: int            = self % ou.Channel() % int()
        device_list: list           = self % od.Device() % list()

        on_time_ms = note_position.getTime_ms()
        return [
                {
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0xE0 | 0x0F & (channel_int - 1),
                        "data_byte_1": pitch_list_midi[0],
                        "data_byte_2": pitch_list_midi[1],
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["pitch"] = self._pitch % int()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "pitch" in serialization):

            super().loadSerialization(serialization)
            self._pitch = ou.Pitch(serialization["pitch"])
        return self
      
    def copy(self) -> 'PitchBend':
        return super().copy() << self._pitch

    def __lshift__(self, operand: Operand) -> 'PitchBend':
        match operand:
            case ou.Pitch():
                self._pitch = operand
            case _: super().__lshift__(operand)
        return self

    def __mul__(self, operand: Operand) -> oc.Many | Element:
        match operand:
            case int():
                multi_pitch_ends = []
                for _ in range(0, operand):
                    multi_pitch_ends.append(self.copy())
                return oc.Many(multi_pitch_ends)
        return super().__mul__(self)

class Sequence(Element):
    def __init__(self):
        super().__init__()
        self._time_length = ol.TimeLength() << ov.Measure(1)
        self._trigger_notes: oc.Many = oc.Many()

    def len(self) -> int:
        return self._trigger_notes.len()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ol.TimeLength():
                if self._time_length is None:
                    last_position: ol.Position = self._trigger_notes.getLastol.Position()
                    sequence_length: ol.TimeLength = ol.TimeLength(measures=1)
                    while last_position > sequence_length:
                        sequence_length += ol.TimeLength(measures=1)
                    return sequence_length
                return self._time_length
            case oc.Many():         return self._trigger_notes
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        
        sequence_position: ol.Position = self % ol.Position() + ol.Position() if position is None else position
        sequence_length: ol.TimeLength     = self % ol.TimeLength()
        
        play_list = []
        for trigger_note in self._trigger_notes % list():

            if trigger_note % ol.Position() < sequence_length:

                trigger_position    = sequence_position + trigger_note % ol.Position()
                trigger_duration    = trigger_note % ol.Duration()
                trigger_key_note    = trigger_note % og.KeyNote()
                trigger_velocity    = trigger_note % ou.Velocity()
                trigger_channel     = trigger_note % ou.Channel()
                trigger_device      = trigger_note % od.Device()

                start_time_ms = sequence_position.getTime_ms()
                on_time_ms = start_time_ms + trigger_position.getTime_ms()
                play_list.append({
                        "time_ms": round(on_time_ms, 3),
                        "midi_message": {
                            "status_byte": 0x90 | 0x0F & (trigger_channel % int() - 1),
                            "data_byte_1": trigger_key_note.getMidi__key_note(),
                            "data_byte_2": trigger_velocity % int(),
                            "device": trigger_device % list()
                        }
                    })
                
                off_time_ms = on_time_ms + trigger_duration.getTime_ms()
                play_list.append({
                        "time_ms": round(off_time_ms, 3),
                        "midi_message": {
                            "status_byte": 0x80 | 0x0F & (trigger_channel % int() - 1),
                            "data_byte_1": trigger_key_note.getMidi__key_note(),
                            "data_byte_2": 0,
                            "device": trigger_device % list()
                        }
                    })

        return play_list
    
    def getSerialization(self):
        trigger_notes_serialization = []
        for trigger_note in self._trigger_notes % list():
            trigger_notes_serialization.append(trigger_note.getSerialization())

        element_serialization = super().getSerialization()
        element_serialization["trigger_notes"] = self._trigger_notes.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "trigger_notes" in serialization):

            super().loadSerialization(serialization)
            self._trigger_notes = oc.Many().loadSerialization(serialization["trigger_notes"])

        return self
    
    def copy(self) -> 'Sequence':
        return super().copy() << self._trigger_notes.copy()

    def __lshift__(self, operand: Operand) -> 'Sequence':
        match operand:
            case of.Frame():
                match operand % of.Inner():
                    case ot.Null():
                        return self
                    case _:
                        inner_operand = operand % Operand()
                        self._trigger_notes << inner_operand
                        return self
            case ol.Position() | ol.TimeLength():
                super().__lshift__(operand)
            case oc.Many():
                self._trigger_notes = operand
            case Operand():
                self._trigger_notes << operand
        return self

    def __add__(self, operand: Operand) -> 'Element':
        if isinstance(operand, ot.Null): return ot.Null()
        sequence_copy = self.copy()
        if isinstance(of.Inner() & operand, ot.Null):
            sequence_copy << sequence_copy % operand + (operand & self)
        else:
            sequence_copy << self._trigger_notes + operand.pop(of.Inner())
        return sequence_copy

    def __sub__(self, operand: Operand) -> 'Element':
        if isinstance(operand, ot.Null): return ot.Null()
        sequence_copy = self.copy()
        if isinstance(of.Inner() & operand, ot.Null):
            sequence_copy << sequence_copy % operand - (operand & self)
        else:
            sequence_copy << self._trigger_notes - operand.pop(of.Inner())
        return sequence_copy

    def __mul__(self, operand: Operand) -> 'Element':
        if isinstance(operand, ot.Null): return ot.Null()
        sequence_copy = self.copy()
        if isinstance(of.Inner() & operand, ot.Null):
            sequence_copy << sequence_copy % operand * (operand & self)
        else:
            sequence_copy << self._trigger_notes * operand.pop(of.Inner())
        return sequence_copy

    def __truediv__(self, operand: Operand) -> 'Element':
        if isinstance(operand, ot.Null): return ot.Null()
        sequence_copy = self.copy()
        if isinstance(of.Inner() & operand, ot.Null):
            sequence_copy << sequence_copy % operand / (operand & self)
        else:
            sequence_copy << self._trigger_notes / operand.pop(of.Inner())
        return sequence_copy

    def __floordiv__(self, time_length: ol.TimeLength) -> 'Sequence':
        return self << self._trigger_notes // time_length

class Triplet(Element):
    def __init__(self):
        super().__init__()
        self._duration *= (2/3) # 3 instead of 2
        self._elements: list[Element] = [Rest(), Rest(), Rest()]

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ol.Duration():     return self._duration * (3/2)
            case ov.NoteValue():    return self._duration * (3/2) % operand
            case list():            return self._elements
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        element_position: ol.Position = ol.Position() if position is None else position
        triplet_playlist = []
        for element_i in range(3):
            triplet_playlist.extend(self._elements[element_i].getPlayList(element_position))
            element_position += self._duration
        return triplet_playlist
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["duration"] = self._duration.getSerialization()
        element_serialization["elements"] = self._elements
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "duration" in serialization and "elements" in serialization):

            super().loadSerialization(serialization)
            self._duration = ol.Duration().loadSerialization(serialization["duration"])
            self._elements = serialization["elements"]
        return self
      
    def copy(self) -> 'Triplet':
        elements = []
        for single_element in self._elements:
            elements.append(single_element.copy())
        return super().copy() << self._duration.copy() << elements

    def __lshift__(self, operand: Operand) -> 'Triplet':
        match operand:
            case ol.Duration():     self._duration = operand * (2/3)
            case ov.NoteValue():    self._duration << operand * (2/3)
            case list():
                if len(operand) < 3:
                    for element_i in range(len(operand)):
                        self._elements[element_i] = operand[element_i]
                else:
                    for element_i in range(3):
                        self._elements[element_i] = operand[element_i]
            case _: super().__lshift__(operand)
        return self

class Tuplet(Element):
    def __init__(self, division: int = 3):
        super().__init__()
        self._division: int = division
        if self._division == 2:
            self._duration *= (3/2) # from 3 notes to 2
            self._elements: list[Element] = [Rest(), Rest()]
        else:
            self._duration *= (2/self._division) # from 2 notes to division
            self._elements: list[Element] = []
            for _ in range(self._division):
                self._elements.append(Rest())                

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case int():             return self._division
            case ol.Duration():     return self._duration * (2/3) if self._division == 2 else (self._division/2)
            case ov.NoteValue():    return self._duration * (2/3) if self._division == 2 else (self._division/2) % operand
            case list():            return self._elements
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        element_position: ol.Position = ol.Position() if position is None else position
        triplet_playlist = []
        for element_i in range(self._division):
            triplet_playlist.extend(self._elements[element_i].getPlayList(element_position))
            element_position += self._duration
        return triplet_playlist
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["division"] = self._division
        element_serialization["duration"] = self._duration.getSerialization()
        element_serialization["elements"] = self._elements
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "division" in serialization and "duration" in serialization and "elements" in serialization):

            super().loadSerialization(serialization)
            self._division = serialization["division"]
            self._duration = ol.Duration().loadSerialization(serialization["duration"])
            self._elements = serialization["elements"]
        return self
      
    def copy(self) -> 'Tuplet':
        elements = []
        for single_element in self._elements:
            elements.append(single_element.copy())
        return super().copy() << self._division << self._duration.copy() << elements

    def __lshift__(self, operand: Operand) -> 'Tuplet':
        match operand:
            case int():             self._division = operand
            case ol.Duration():     self._duration = operand * (2/3) if self._division == 2 else (self._division/2)
            case ov.NoteValue():    self._duration << operand * (2/3) if self._division == 2 else (self._division/2)
            case list():
                if len(operand) < self._division:
                    for element_i in range(len(operand)):
                        self._elements[element_i] = operand[element_i]
                else:
                    for element_i in range(self._division):
                        self._elements[element_i] = operand[element_i]
            case _: super().__lshift__(operand)
        return self

class Panic:
    ...

    # CHAINABLE OPERATIONS

class Arpeggio(Element):
    ...

    # CHAINABLE OPERATIONS


class Loop(Element):
    def __init__(self, element, repeat = 4):
        self._element = element
        self._repeat = repeat
        self._device: list = None
    
    # CHAINABLE OPERATIONS


class Stack(Element):
    ...

    # CHAINABLE OPERATIONS

class Automation(Element):
    ...

    # CHAINABLE OPERATIONS


class Retrigger(Element):
    ...
    
    # CHAINABLE OPERATIONS


class Composition(Element):
    def __init__(self):
        super().__init__()
        self._many_elements: oc.Many = oc.Many()

    def len(self) -> int:
        return self._many_elements.len()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case oc.Many():         return self._many_elements
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ol.Position = None):
        
        composition_position: ol.Position = self % ol.Position() + ol.Position() if position is None else position
        
        play_list = []
        for single_element in self._many_elements % list():
            play_list.extend(single_element.getPlayList(composition_position))
        return play_list
    
    def getSerialization(self):
        many_elements_serialization = []
        for many_element in self._many_elements % list():
            many_elements_serialization.append(many_element.getSerialization())

        element_serialization = super().getSerialization()
        element_serialization["many_elements"] = self._many_elements.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "many_elements" in serialization):

            super().loadSerialization(serialization)
            self._many_elements = oc.Many().loadSerialization(serialization["many_elements"])

        return self
    
    def copy(self) -> 'Composition':
        return super().copy() << self._many_elements.copy()

    def __lshift__(self, operand: Operand) -> 'Composition':
        match operand:
            case oc.Many(): self._many_elements = operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: Operand) -> 'Element':
        composition_copy = self.copy()
        if isinstance(operand, of.Frame):
            if not isinstance(operand % of.Inner(), ot.Null) and not isinstance(operand % Operand(), ot.Null):
                composition_copy << (self._many_elements + (operand % Operand())).copy()
        else:
            match operand:
                case ol.Position() | ol.TimeLength():
                    composition_copy << composition_copy % operand + operand
                case Operand():
                    composition_copy << (self._many_elements + operand).copy()
        return composition_copy

    def __sub__(self, operand: Operand) -> 'Element':
        composition_copy = self.copy()
        if isinstance(operand, of.Frame):
            if not isinstance(operand % of.Inner(), ot.Null) and not isinstance(operand % Operand(), ot.Null):
                composition_copy << (self._many_elements - (operand % Operand())).copy()
        else:
            match operand:
                case ol.Position() | ol.TimeLength():
                    composition_copy << composition_copy % operand - operand
                case Operand():
                    composition_copy << (self._many_elements - operand).copy()
        return composition_copy

    def __mul__(self, operand: Operand) -> 'Element':
        composition_copy = self.copy()
        if isinstance(operand, of.Frame):
            if not isinstance(operand % of.Inner(), ot.Null) and not isinstance(operand % Operand(), ot.Null):
                composition_copy << (self._many_elements * (operand % Operand())).copy()
        else:
            match operand:
                case ol.Position() | ol.TimeLength():
                    composition_copy << composition_copy % operand * operand
                case Operand():
                    composition_copy << (self._many_elements * operand).copy()
        return composition_copy

    def __truediv__(self, operand: Operand) -> 'Element':
        composition_copy = self.copy()
        composition_copy << composition_copy % operand / (operand & composition_copy)
        composition_copy << self._many_elements / (operand & of.Inner()**self._many_elements)
        return composition_copy

    def __floordiv__(self, time_length: ol.TimeLength) -> 'Composition':
        return self << self._many_elements // time_length






# Voice Message           Status Byte      Data Byte1          Data Byte2
# -------------           -----------   -----------------   -----------------
# Note off                      8x      Key number          Note Off velocity
# Note on                       9x      Key number          Note on velocity
# Polyphonic Key Pressure       Ax      Key number          Amount of pressure
# Control Change                Bx      Controller number   Controller value
# Program Change                Cx      Program number      None
# Channel Pressure              Dx      Pressure value      None            
# Pitch Bend                    Ex      MSB                 LSB

