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
import json
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_staff as os
import operand_unit as ou
import operand_value as ov
import operand_time as ot
import operand_data as od
import operand_label as ol
import operand_frame as of
import operand_generic as og
import operand_container as oc
import operand_frame as of


class Element(o.Operand):
    def __init__(self):
        super().__init__()
        self._position: ot.Position         = ot.Position()
        self._length: ot.Length             = ot.Length()
        self._channel: ou.Channel           = ou.Channel()
        self._device: od.Device             = od.Device()

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of an Element,
        those Parameters can be Position, Length, midi Channel and midi Device

        Examples
        --------
        >>> default_element = Element()
        >>> print(default_element % Device() % list())
        ['loopMIDI', 'Microsoft']
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ot.Position():     return self._position
                    case ot.Length():       return self._length
                    case ou.Channel():      return self._channel
                    case od.Device():       return self._device
                    case Element():         return self
                    case _:                 return ol.Null()
            case of.Frame():        return self % (operand % o.Operand())
            case ot.Position():     return self._position.copy()
            case ov.TimeUnit():     return self._position % operand
            case ot.Length():       return self._length.copy()
            case ou.Channel():      return self._channel.copy()
            case od.Device():       return self._device.copy()
            case Element():         return self.copy()
            case _:                 return ol.Null()

    def __eq__(self, other_operand: 'o.Operand') -> bool:
        match other_operand:
            case self.__class__():
                return  self._position == other_operand % od.DataSource( ot.Position() ) \
                    and self._length == other_operand % od.DataSource( ot.Length() ) \
                    and self._channel == other_operand % od.DataSource( ou.Channel() ) \
                    and self._device == other_operand % od.DataSource( od.Device() )
            case ov.TimeUnit():
                return self._position == other_operand
            case _:
                return self % od.DataSource( other_operand ) == other_operand

    def __lt__(self, other_operand: 'o.Operand') -> bool:
        match other_operand:
            case self.__class__():
                return  False
            case ov.TimeUnit():
                return self._position < other_operand
            case _:
                return self % od.DataSource( other_operand ) < other_operand
    
    def __gt__(self, other_operand: 'o.Operand') -> bool:
        match other_operand:
            case self.__class__():
                return  False
            case ov.TimeUnit():
                return self._position > other_operand
            case _:
                return self % od.DataSource( other_operand ) > other_operand
    
    def __le__(self, other_operand: 'o.Operand') -> bool:
        return self == other_operand or self < other_operand
    
    def __ge__(self, other_operand: 'o.Operand') -> bool:
        return self == other_operand or self > other_operand

    def start(self) -> ot.Position:
        return self._position.copy()

    def end(self) -> ot.Position:
        return self._position + self._length

    def getPlayList(self, position: ot.Position = None) -> list:
        self_position: ot.Position  = self._position + ot.Position() if position is None else position
        
        return [
                {
                    "time_ms": self_position.getTime_ms()
                }
            ]

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "position": self._position.getSerialization(),
                "length":   self._length.getSerialization(),
                "channel":  self._channel % od.DataSource( int() ),
                "device":   self._device % od.DataSource( list() )
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "length" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "device" in serialization["parameters"]):

            self._position  = ot.Position().loadSerialization(serialization["parameters"]["position"])
            self._length    = ot.Length().loadSerialization(serialization["parameters"]["length"])
            self._channel   = ou.Channel()  << od.DataSource( serialization["parameters"]["channel"] )
            self._device    = od.Device()   << od.DataSource( serialization["parameters"]["device"] )
        return self
        
    def __xor__(self, operand: o.Operand):
        """
        ^ calls the respective Operand's method by name.
        """
        match operand:
            case ol.Start():
                return self.start()
            case ol.End():
                return self.end()
            case _:
                return super().__xor__(operand)

    def __lshift__(self, operand: o.Operand) -> 'Element':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ot.Position():     self._position = operand % o.Operand()
                    case ot.Length():       self._length = operand % o.Operand()
                    case ou.Channel():      self._channel = operand % o.Operand()
                    case od.Device():       self._device = operand % o.Operand()
            case Element():
                self._position      = (operand % od.DataSource( ot.Position() )).copy()
                self._length        = (operand % od.DataSource( ot.Length() )).copy()
                self._channel       = (operand % od.DataSource( ou.Channel() )).copy()
                self._device        = (operand % od.DataSource( od.Device() )).copy()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ot.Position() | ov.TimeUnit():
                                    self._position << operand
            case ot.Length():       self._length << operand
            case ou.Channel():      self._channel << operand
            case od.Device():       self._device << operand
            case od.Serialization():
                self.loadSerialization(operand.getSerialization())
            case oc.Chain():
                for single_operand in operand:
                    self << single_operand
        return self

    # operand is the pusher
    def __rrshift__(self, operand: o.Operand) -> 'Element':
        if isinstance(operand, (ot.Position, Element, oc.Sequence)):
            operand_end = operand.end()
            self_start = self.start()
            if type(operand_end) != ol.Null and type(self_start) != ol.Null:
                self_drag = ot.Length() << operand_end - self_start
                self << self % ot.Position() + self_drag
        if isinstance(operand, (oc.Sequence, Element)):
            return operand + self
        else:
            return self.copy()

    def __add__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():         return oc.Sequence(self_copy, operand.copy())
            case oc.Sequence():     return oc.Sequence(self_copy, operand.copy() % list())
            case o.Operand():       return self_copy << self % operand + operand
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():         return self
            case oc.Sequence():     return self
            case o.Operand():       return self_copy << self % operand - operand
        return self_copy

    def __mul__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():
                ...
            case oc.Sequence():
                ...
            case o.Operand():
                return self_copy << self % operand * operand    # implicit copy (*)
            case int():
                multi_elements = []
                for _ in range(0, operand):
                    multi_elements.append(self.copy())
                return oc.Sequence(multi_elements)
        return self_copy

    def __truediv__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():
                ...
            case oc.Sequence():
                ...
            case o.Operand():
                return self_copy << self % operand / operand
        return self_copy

    @staticmethod
    def midi_128(midi_value: int = 0):
        return min(max(midi_value, 0), 127)

    @staticmethod
    def midi_16(midi_value: int = 0):
        return min(max(midi_value, 0), 15)

class Clock(Element):
    def __init__(self, measure: float = None):
        super().__init__()
        self._length = ot.Length() << (ov.Measure() << \
                        ( os.staff % od.DataSource( ov.Measure() ) % od.DataSource( Fraction() ) if measure is None else measure ))
        self._pulses_per_quarternote: ou.PPQN = ou.PPQN()

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Clock,
        those Parameters are the ones of the Element, like Position and Length,
        plus the Pulses Per Quarter Note, the last one as 24 by default.

        Examples
        --------
        >>> clock = Clock(4)
        >>> clock % Length() >> Print(0)
        {'class': 'Length', 'parameters': {'measure': 4.0, 'beat': 0.0, 'note_value': 0.0, 'step': 0.0}}
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.PPQN():     return self._pulses_per_quarternote
                    case _:             return super().__mod__(operand)
            case ou.PPQN():     return self._pulses_per_quarternote.copy()
            case _:             return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._pulses_per_quarternote == other_operand % od.DataSource( ou.PPQN() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        device = self % od.Device()

        pulses_per_note = 4 * self._pulses_per_quarternote % od.DataSource( Fraction() )
        pulses_per_beat = pulses_per_note * (os.staff % ov.BeatNoteValue() % od.DataSource( Fraction() ))
        pulses_per_measure = pulses_per_beat * (os.staff % ov.BeatsPerMeasure() % od.DataSource( Fraction() ))
        clock_pulses = round(pulses_per_measure * (self._length % od.DataSource( ov.Measure() ) % od.DataSource( Fraction() )))

        single_measure_rational_ms = ov.Measure(1).getTime_rational()
        clock_start_rational_ms = self_position.getTime_rational()
        clock_stop_rational_ms = clock_start_rational_ms + self._length.getTime_rational()

        self_playlist = [
                {
                    "time_ms": round(float(clock_start_rational_ms), 3),
                    "midi_message": {
                        "status_byte": 0xFA,    # Start Sequence
                        "device": device % od.DataSource( list() )
                    }
                }
            ]

        for clock_pulse in range(1, clock_pulses):
            self_playlist.append(
                {
                    "time_ms": round(float(clock_start_rational_ms \
                                     + single_measure_rational_ms * (self._length % od.DataSource( ov.Measure() ) % od.DataSource( Fraction() )) \
                                     * clock_pulse / clock_pulses), 3),
                    "midi_message": {
                        "status_byte": 0xF8,    # Timing Clock
                        "device": device % od.DataSource( list() )
                    }
                }
            )

        self_playlist.append(
            {
                "time_ms": round(float(clock_stop_rational_ms), 3),
                "midi_message": {
                    "status_byte": 0xFC,    # Stop Sequence
                    "device": device % od.DataSource( list() )
                }
            }
        )
        
        return self_playlist

    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["pulses_per_quarternote"]   = self._pulses_per_quarternote % od.DataSource( int() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pulses_per_quarternote" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pulses_per_quarternote    = ou.PPQN() << od.DataSource( serialization["parameters"]["pulses_per_quarternote"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'Clock':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.PPQN():         self._pulses_per_quarternote = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case Clock():
                super().__lshift__(operand)
                self._pulses_per_quarternote = (operand % od.DataSource( ou.PPQN() )).copy()
            case ou.PPQN():         self._pulses_per_quarternote << operand
            case int() | float():   self._length = ot.Length(operand)
            case _: super().__lshift__(operand)
        return self

class Rest(Element):
    def __init__(self):
        super().__init__()
        self._duration: ot.Duration = os.staff % ot.Duration()
        self._length << self._duration  # By default a note has the same Length as its Duration

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ot.Duration():     return self._duration
                    case _:                 return super().__mod__(operand)
            case ot.Duration():     return self._duration.copy()
            case ov.NoteValue():    return self._duration % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._duration == other_operand % od.DataSource( ot.Duration() )
            case ov.NoteValue():
                return self._duration == other_operand
            case _:
                return super().__eq__(other_operand)
    
    def __lt__(self, other_operand: 'o.Operand') -> bool:
        match other_operand:
            case ov.NoteValue():
                return self._duration < other_operand
            case _:
                return super().__lt__(other_operand)
    
    def __gt__(self, other_operand: 'o.Operand') -> bool:
        match other_operand:
            case ov.NoteValue():
                return self._duration > other_operand
            case _:
                return super().__gt__(other_operand)
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["duration"] = self._duration.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "duration" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._duration  = ot.Duration().loadSerialization(serialization["parameters"]["duration"])
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Note':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ot.Duration():     self._duration = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case Rest():
                super().__lshift__(operand)
                self._duration      = (operand % od.DataSource( ot.Duration() )).copy()
            case ot.Duration() | ov.NoteValue():
                                    self._duration << operand
            case _: super().__lshift__(operand)
        return self

class Note(Rest):
    def __init__(self, key: int | str = None):
        super().__init__()
        self._key_note: og.KeyNote  = og.KeyNote()  << (os.staff % ou.Key() if key is None else ou.Key(key)) \
                                                    <<  os.staff % ou.Octave()
        self._velocity: ou.Velocity = os.staff % ou.Velocity()
        self._gate: ov.Gate         = ov.Gate(.90)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Note,
        those Parameters are the ones of the Element, like Position and Length,
        plus the Duration, KeyNote, Velocity and Gate, the last one as 0.90 by default.

        Examples
        --------
        >>> some_note = Note("F")
        >>> print(some_note % Key() % str())
        F
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.KeyNote():      return self._key_note
                    case ou.Velocity():     return self._velocity
                    case ov.Gate():         return self._gate
                    case _:                 return super().__mod__(operand)
            case og.KeyNote():      return self._key_note.copy()
            case ou.Key() | ou.Octave():
                                    return self._key_note % operand
            case ou.Velocity():     return self._velocity.copy()
            case ov.Gate():         return self._gate.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._key_note == other_operand % od.DataSource( og.KeyNote() ) \
                    and self._velocity == other_operand % od.DataSource( ou.Velocity() ) \
                    and self._gate == other_operand % od.DataSource( ov.Gate() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        duration: ot.Duration       = self._duration
        key_note_int: int           = self._key_note % od.DataSource( int() )
        velocity_int: int           = self._velocity % od.DataSource( int () )
        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )

        on_time_ms = self_position.getTime_ms()
        off_time_ms = (self_position + duration * self._gate).getTime_ms()
        return [
                {
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(key_note_int),
                        "data_byte_2": Element.midi_128(velocity_int),
                        "device": device_list
                    }
                },
                {
                    "time_ms": off_time_ms,
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(key_note_int),
                        "data_byte_2": 0,
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["key_note"] = self._key_note.getSerialization()
        element_serialization["parameters"]["velocity"] = self._velocity % od.DataSource( int() )
        element_serialization["parameters"]["gate"]     = self._gate % od.DataSource( float() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key_note" in serialization["parameters"] and
            "velocity" in serialization["parameters"] and "gate" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._key_note  = og.KeyNote().loadSerialization(serialization["parameters"]["key_note"])
            self._velocity  = ou.Velocity() << od.DataSource( serialization["parameters"]["velocity"] )
            self._gate      = ov.Gate()     << od.DataSource( serialization["parameters"]["gate"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Note':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.KeyNote():      self._key_note = operand % o.Operand()
                    case ou.Velocity():     self._velocity = operand % o.Operand()
                    case ov.Gate():         self._gate = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case Note():
                super().__lshift__(operand)
                self._key_note      = (operand % od.DataSource( og.KeyNote() )).copy()
                self._velocity      = (operand % od.DataSource( ou.Velocity() )).copy()
                self._gate          = (operand % od.DataSource( ov.Gate() )).copy()
            case og.KeyNote() | ou.Key() | ou.Octave() | int() | float():
                                    self._key_note << operand
            case ou.Velocity():     self._velocity << operand
            case ov.Gate():         self._gate << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case ou.Key() | og.KeyNote() | int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._key_note + operand
            case _:             return super().__add__(operand)
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case ou.Key() | og.KeyNote() | int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._key_note - operand
            case _:             return super().__sub__(operand)
        return self_copy

class KeyScale(Note):
    def __init__(self, key: int | str = None):
        super().__init__(key)
        self._scale: od.Scale = os.staff % od.Scale()    # default Staff scale
        self._mode: ou.Mode = ou.Mode()

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a KeyScale,
        those Parameters are the ones of the Element, like Position and Length,
        together with the ones of a Note, like Duration and KeyNote,
        plus the Scale and Mode, the last one as 1 by default.

        Examples
        --------
        >>> entire_scale = KeyScale()
        >>> entire_scale << Scale("minor")
        >>> print(entire_scale % str())
        minor
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Scale():        return self._scale
                    case ou.Mode():         return self._mode
                    case _:                 return super().__mod__(operand)
            case od.Scale():        return self._scale.copy()
            case list():            return self._scale % list()
            case str():             return self._scale % str()
            case ou.Mode():         return self._mode.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._scale == other_operand % od.DataSource( od.Scale() ) \
                    and self._mode == other_operand % od.DataSource( ou.Mode() )
            case _:
                return super().__eq__(other_operand)
    
    def getSharps(self, key: ou.Key = None) -> int:
        ...

    def getFlats(self, key: ou.Key = None) -> int:
        ...

    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        root_key_note = self._key_note.copy()
        scale_key_notes = []
        for key_note_i in range(self._scale.keys()): # presses entire scale, 7 keys for diatonic scales
            transposition = self._scale.transposition(self._mode % od.DataSource( int() ) + key_note_i)
            scale_key_notes.append(root_key_note + transposition)

        self_playlist = []
        for key_note in scale_key_notes:
            self << key_note
            self_playlist.extend(super().getPlayList(self_position))
        self << root_key_note

        return self_playlist
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["scale"]        = self._scale % od.DataSource( list() )
        element_serialization["parameters"]["mode"]         = self._mode % od.DataSource( int() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeyScale':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "mode" in serialization["parameters"] and "scale" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._scale         = od.Scale()        << od.DataSource( serialization["parameters"]["scale"] )
            self._mode          = ou.Mode()         << od.DataSource( serialization["parameters"]["mode"] )
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'KeyScale':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Scale():        self._scale = operand % o.Operand()
                    case ou.Mode():         self._mode = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case KeyScale():
                super().__lshift__(operand)
                self._scale = (operand % od.DataSource( od.Scale() )).copy()
                self._mode  = (operand % od.DataSource( ou.Mode() )).copy()
            case od.Scale() | list():   self._scale << operand
            case ou.Mode():             self._mode << operand
            case _: super().__lshift__(operand)
        return self

class Chord(Note):
    def __init__(self, key: int | str = None):
        super().__init__(key)
        self._scale: od.Scale = os.staff % od.Scale()   # Default Scale for Chords
        self._degree: ou.Degree = ou.Degree()
        self._inversion: ou.Inversion = ou.Inversion()
        self._type: ou.Type = ou.Type()
        self._sus: ou.Sus = ou.Sus()

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Chord,
        those Parameters are the ones of the Element, like Position and Length,
        plus the ones of a Note, and the Scale, Degree, Inversion and others.

        Examples
        --------
        >>> single_chord = Chord("A") << Scale("minor") << Type("7th") << NoteValue(1/2)
        >>> print(single_chord % Degree() % str())
        I
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Scale():        return self._scale
                    case ou.Type():         return self._type
                    case ou.Degree():       return self._degree
                    case ou.Inversion():    return self._inversion
                    case ou.Sus():          return self._sus
                    case _:                 return super().__mod__(operand)
            case od.Scale():        return self._scale.copy()
            case ou.Type():         return self._type.copy()
            case ou.Degree():       return self._degree.copy()
            case ou.Inversion():    return self._inversion.copy()
            case ou.Sus():          return self._sus.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._scale == other_operand % od.DataSource( od.Scale() ) \
                    and self._type == other_operand % od.DataSource( ou.Type() ) \
                    and self._degree == other_operand % od.DataSource( ou.Degree() ) \
                    and self._inversion == other_operand % od.DataSource( ou.Inversion() ) \
                    and self._sus == other_operand % od.DataSource( ou.Sus() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        max_type = self._scale.keys()
        if max_type % 2 == 0:
            max_type //= 2
        max_type = min(self._type % od.DataSource( int() ), max_type)

        root_key_note = self._key_note
        chord_key_notes = []
        for key_note_i in range(max_type):
            key_note_nth = key_note_i * 2
            if key_note_nth == 2:
                if self._sus % od.DataSource( int() ) == 1:
                    key_note_nth -= 1
                if self._sus % od.DataSource( int() ) == 2:
                    key_note_nth += 1
            transposition = self._scale.transposition(self._degree % od.DataSource( int() ) + key_note_nth)
            chord_key_notes.append(root_key_note + transposition)

        # Where the inversions are done
        inversion = min(self._inversion % od.DataSource( int() ), self._type % od.DataSource( int() ) - 1)
        first_key_note = chord_key_notes[inversion]
        not_first_key_note = True
        while not_first_key_note:
            not_first_key_note = False
            for key_note in chord_key_notes:
                if key_note < first_key_note:
                    key_note << key_note % ou.Octave() + 1
                    if key_note % od.DataSource( int() ) < 128:
                        not_first_key_note = True

        self_playlist = []
        for key_note in chord_key_notes:
            self._key_note = key_note
            self_playlist.extend(super().getPlayList(self_position))
        self._key_note = root_key_note

        return self_playlist
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["scale"]        = self._scale % od.DataSource( list() )
        element_serialization["parameters"]["type"]         = self._type % od.DataSource( int() )
        element_serialization["parameters"]["degree"]       = self._degree % od.DataSource( int() )
        element_serialization["parameters"]["inversion"]    = self._inversion % od.DataSource( int() )
        element_serialization["parameters"]["sus"]          = self._sus % od.DataSource( int() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "scale" in serialization["parameters"] and "degree" in serialization["parameters"] and
            "inversion" in serialization["parameters"] and "type" in serialization["parameters"] and "sus" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._scale         = od.Scale()        << od.DataSource( serialization["parameters"]["scale"] )
            self._type          = ou.Type()         << od.DataSource( serialization["parameters"]["type"] )
            self._degree        = ou.Degree()       << od.DataSource( serialization["parameters"]["degree"] )
            self._inversion     = ou.Inversion()    << od.DataSource( serialization["parameters"]["inversion"] )
            self._sus           = ou.Sus()          << od.DataSource( serialization["parameters"]["sus"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Chord':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case od.Scale():                self._scale = operand % o.Operand()
                    case ou.Type():                 self._type = operand % o.Operand()
                    case ou.Degree():               self._degree = operand % o.Operand()
                    case ou.Inversion():            self._inversion = operand % o.Operand()
                    case ou.Sus():                  self._sus = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Chord():
                super().__lshift__(operand)
                self._scale         = (operand % od.DataSource( od.Scale() )).copy()
                self._type          = (operand % od.DataSource( ou.Type() )).copy()
                self._degree        = (operand % od.DataSource( ou.Degree() )).copy()
                self._inversion     = (operand % od.DataSource( ou.Inversion() )).copy()
                self._sus           = (operand % od.DataSource( ou.Sus() )).copy()
            case od.Scale() | list():       self._scale << operand
            case ou.Type():                 self._type << operand
            case ou.Degree():               self._degree << operand
            case ou.Inversion():            self._inversion << operand
            case ou.Sus():                  self._sus << operand
            case _: super().__lshift__(operand)
        return self

class Retrigger(Note):
    def __init__(self, key: int | str = None):
        super().__init__(key)
        self._division  = ou.Division(16)
        self._duration  = self._duration * 2/(self._division % int())
        self._length   << self._duration * (self._division % int())
        self._gate      = ov.Gate(.50)
        self._swing     = ov.Swing(.50)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Retrigger,
        those Parameters are the ones of the Element, like Position and Length,
        plus the ones of a Note and the Division.

        Examples
        --------
        >>> retrigger = Retrigger("G") << Division(32)
        >>> retrigger % Division() % int() >> Print()
        32
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Division():     return self._division
                    case ov.Swing():        return self._swing
                    case _:                 return super().__mod__(operand)
            case ou.Division():     return self._division.copy()
            case int():             return self._division % int()
            case ov.Swing():        return self._swing.copy()
            case ot.Duration():     return self._duration * (self._division % int())/2
            case ov.NoteValue():    return self._duration * (self._division % int())/2 % operand
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        self_playlist = []
        self_iteration = 0
        original_duration = self._duration
        for _ in range(self._division % od.DataSource( int() )):
            swing_ratio = self._swing % od.DataSource( Fraction() )
            if self_iteration % 2: swing_ratio = 1 - swing_ratio
            self._duration = original_duration * 2 * swing_ratio
            self_playlist.extend(super().getPlayList(self_position))
            self_position += self._duration
            self_iteration += 1
        self._duration << original_duration
        return self_playlist
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["division"] = self._division % od.DataSource( int() )
        element_serialization["parameters"]["swing"]    = self._swing % od.DataSource( float() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "division" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._division  = ou.Division() << od.DataSource( serialization["parameters"]["division"] )
            self._swing     = ov.Swing()    << od.DataSource( serialization["parameters"]["swing"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'Retrigger':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Division():             self._division = operand % o.Operand()
                    case ov.Swing():                self._swing = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Retrigger():
                super().__lshift__(operand)
                self._division  = (operand % od.DataSource( ou.Division() )).copy()
                self._swing     = (operand % od.DataSource( ov.Swing() )).copy()
            case ou.Division() | int():
                if operand > 0:
                    self._duration << self._duration * self._division/operand
                    self._division << operand
            case ov.Swing():
                if operand < 0:     self._swing << 0
                elif operand > 1:   self._swing << 1
                else:               self._swing << operand
            case ot.Duration() | ov.NoteValue():
                self._duration << operand * 2/(self._division % int())
            case _:                 super().__lshift__(operand)
        return self

class Note3(Retrigger):
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
    def __init__(self, key: int | str = None):
        super().__init__(key)
        self._division  << ou.Division(3)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Note3':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Division() | int():
                return self # disables the setting of Division, always 3
            case _:                 super().__lshift__(operand)
        return self

class Tuplet(Rest):
    def __init__(self, *elements: Element):
        super().__init__()
        self._swing     = ov.Swing(.50)
        self._elements: list[Element] = []
        if len(elements) > 0 and all(isinstance(single_element, Element) for single_element in elements):
            self._elements = o.Operand.copy_operands_list(elements)
        if len(self._elements) == 2:
            # Can't be "*= 3/2" in order to preserve the Fraction!
            self._duration = self._duration * 3/2 # from 3 notes to 2
            self._length << self._duration * 2  # Length as the entire duration of the Note tuplet
        elif len(self._elements) > 0:
            # Can't be "*= 2 / self._division" in order to preserve the Fraction!
            self._duration = self._duration * 2 / len(self._elements) # from 2 notes to division
            self._length << self._duration * len(self._elements)  # Length as the entire duration of the Note tuplet
        self.set_elements_duration()

    def set_elements_duration(self):
        for single_element in self._elements:
            single_element << self._duration

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Tuplet,
        those Parameters are the ones of the Element, like Position and Length,
        and the Division and a List of Elements.

        Examples
        --------
        >>> tuplet = Tuplet( Note("C"), Note("F"), Note("G"), Note("C") )
        >>> tuplet % Division() % int() >> Print()
        4
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ov.Swing():        return self._swing
                    case list():            return self._elements
                    case _:                 return super().__mod__(operand)
            case ot.Duration():
                if len(self._elements) == 2:    return self._duration * 2/3  
                elif len(self._elements) > 0:   return self._duration * len(self._elements) / 2
                return self._duration.copy()
            case ov.NoteValue():
                if len(self._elements) == 2:    return self._duration * 2/3 % operand
                elif len(self._elements) > 0:   return self._duration * len(self._elements) / 2 % operand
                return self._duration % operand
            case ov.Swing():        return self._swing.copy()
            case ou.Division():     return ou.Division() << len(self._elements)
            case int():             return len(self._elements)
            case list():            return o.Operand.copy_operands_list(self._elements)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._swing     == other_operand % od.DataSource( ov.Swing() ) \
                    and self._elements  == other_operand % od.DataSource( list() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position
        
        self_playlist = []
        self_iteration = 0
        for element_i in range(len(self._elements)):
            self_playlist.extend(self._elements[element_i].getPlayList(self_position))
            swing_ratio = self._swing % od.DataSource( Fraction() )
            if self_iteration % 2: swing_ratio = 1 - swing_ratio
            self_position += self._duration * 2 * swing_ratio
            self_iteration += 1
        return self_playlist
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["swing"]    = self._swing % od.DataSource( float() )
        elements = []
        for single_element in self._elements:
            elements.append(single_element.getSerialization())
        element_serialization["parameters"]["elements"] = elements
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "swing" in serialization["parameters"] and "elements" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._swing     = ov.Swing()    << od.DataSource( serialization["parameters"]["swing"] )
            elements = []
            elements_serialization = serialization["parameters"]["elements"]
            for single_element_serialization in elements_serialization:
                if isinstance(single_element_serialization, dict) and "class" in single_element_serialization:
                    element = self.getOperand(single_element_serialization["class"])
                    if element: elements.append(element.loadSerialization(single_element_serialization))
            self._elements = elements
        return self

    def __lshift__(self, operand: o.Operand) -> 'Tuplet':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        for single_element in self._elements:
            single_element << operand
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ov.Swing():            self._swing = operand % o.Operand()
                    case list():                self._elements = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case Tuplet():
                super().__lshift__(operand)
                self._duration = (operand % od.DataSource( ot.Duration() )).copy()
                self._swing = (operand % od.DataSource( ov.Swing() )).copy()
                self._elements = o.Operand.copy_operands_list(operand % od.DataSource( list() ))
            case ot.Duration() | ov.NoteValue():
                if len(self._elements) == 2:
                    self._duration << operand * 3/2
                elif len(self._elements) > 0:
                    self._duration << operand * 2/len(self._elements)
                else:
                    self._duration << operand
                self.set_elements_duration()
            case ov.Swing():
                if operand < 0:     self._swing << 0
                elif operand > 1:   self._swing << 1
                else:               self._swing << operand
            case list():
                elements: list[Element] = operand
                if len(elements) > 0 and all(isinstance(single_element, Element) for single_element in elements):
                    net_duration = self % ot.Duration()
                    if len(elements) == 2:
                        # Can't be "*= 3/2" in order to preserve the Fraction!
                        self._duration = net_duration * 3/2 # from 3 notes to 2
                        self._length << self._duration * 2  # Length as the entire duration of the Note tuplet
                    elif len(elements) > 0:
                        # Can't be "*= 2 / self._division" in order to preserve the Fraction!
                        self._duration = net_duration * 2 / len(elements) # from 2 notes to division
                        self._length << self._duration * len(elements)  # Length as the entire duration of the Note tuplet
                    self._elements = o.Operand.copy_operands_list(elements)
                    self.set_elements_duration()
            case _: super().__lshift__(operand)
        return self

class Triplet(Tuplet):
    def __init__(self, *elements: Element):
        super().__init__(*elements)
        if self % int() != 3: self << [Rest(), Rest(), Rest()]

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand | list[Element]) -> 'Triplet':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case list():
                if len(operand) == 3:
                    super().__lshift__(operand)
            case _: super().__lshift__(operand)
        return self

class ControlChange(Element):
    def __init__(self, number: int | str = None):
        super().__init__()
        self._controller: og.Controller = (os.staff % og.Controller()).copy()
        if number is not None:
            self._controller = og.Controller(number)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a ControlChange,
        those Parameters are the ones of the Element, like Position and Length,
        and the Controller Number and Value as ControlNumber and ControlValue.

        Examples
        --------
        >>> controller = Controller("Modulation")
        >>> controller % ControlNumber() % int() >> Print()
        1
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Controller():       return self._controller
                    case _:                     return super().__mod__(operand)
            case og.Controller():       return self._controller.copy()
            case ou.ControlNumber():    return self._controller % ou.ControlNumber()
            case ou.ControlValue():     return self._controller % ou.ControlValue()
            case int() | float():       return self._controller % operand
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._controller == other_operand % od.DataSource( og.Controller() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        control_number_int: int     = self % ou.ControlNumber() % od.DataSource( int() )
        control_value_int: int      = self % ou.ControlValue() % od.DataSource( int() )
        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )

        on_time_ms = self_position.getTime_ms()
        return [
                {
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(control_number_int),
                        "data_byte_2": Element.midi_128(control_value_int),
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["controller"] = self._controller.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "controller" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._controller = og.Controller().loadSerialization(serialization["parameters"]["controller"])
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'ControlChange':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Controller():       self._controller = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case ControlChange():
                super().__lshift__(operand)
                self._controller = (operand % od.DataSource( og.Controller() )).copy()
            case og.Controller() | ou.ControlNumber() | ou.ControlValue() | int() | float():
                self._controller << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case int() | float() | ou.Integer() | ov.Float():
                self_copy << self._controller + operand
            case _:             return super().__add__(operand)
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case int() | float() | ou.Integer() | ov.Float():
                self_copy << self._controller - operand
            case _:             return super().__sub__(operand)
        return self_copy

class PitchBend(Element):
    def __init__(self, pitch: int = None):
        super().__init__()
        self._pitch: ou.Pitch = ou.Pitch( 0 if pitch is None else pitch )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Pitch():        return self._pitch
                    case _:                 return super().__mod__(operand)
            case ou.Pitch():        return self._pitch.copy()
            case int() | float():   return self._pitch % od.DataSource( int() )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._pitch == other_operand % od.DataSource( ou.Pitch() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        msb_midi: int               = self._pitch % ol.MSB()
        lsb_midi: int               = self._pitch % ol.LSB()
        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( int() )

        on_time_ms = self_position.getTime_ms()
        return [
                {
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0xE0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": lsb_midi,
                        "data_byte_2": msb_midi,
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["pitch"] = self._pitch % od.DataSource( int() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pitch" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pitch     = ou.Pitch()    << od.DataSource( serialization["parameters"]["pitch"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'PitchBend':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Pitch():            self._pitch = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case PitchBend():
                super().__lshift__(operand)
                self._pitch = (operand % od.DataSource( ou.Pitch() )).copy()
            case ou.Pitch() | int() | float():  self._pitch << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case ou.Pitch() | int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._pitch + operand
            case _:             return super().__add__(operand)
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case ou.Pitch() | int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._pitch - operand
            case _:             return super().__sub__(operand)
        return self_copy

class Aftertouch(Element):
    def __init__(self, channel: int = None):
        super().__init__()
        self._channel = ou.Channel(channel)
        self._pressure: ou.Pressure = ou.Pressure()

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Pressure():     return self._pressure
                    case _:                 return super().__mod__(operand)
            case ou.Pressure():     return self._pressure.copy()
            case int() | float():   return self._pressure % od.DataSource( int() )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._pressure == other_operand % od.DataSource( ou.Pressure() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        pressure_int: int   = self._pressure % od.DataSource( int() )
        channel_int: int    = self._channel % od.DataSource( int() )
        device_list: list   = self._device % od.DataSource( list() )

        on_time_ms = self_position.getTime_ms()
        return [
                {
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0xD0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(pressure_int),
                        "data_byte_2": None,
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["pressure"] = self._pressure % od.DataSource( int() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pressure" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pressure  = ou.Pressure() << od.DataSource( serialization["parameters"]["pressure"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Aftertouch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Pressure():         self._pressure = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case Aftertouch():
                super().__lshift__(operand)
                self._pressure = (operand % od.DataSource( ou.Pressure() )).copy()
            case ou.Pressure() | int() | float():
                self._pressure << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case ou.Pressure() | int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._pressure + operand
            case _:             return super().__add__(operand)
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case ou.Pressure() | int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._pressure - operand
            case _:             return super().__sub__(operand)
        return self_copy

class PolyAftertouch(Aftertouch):
    def __init__(self, key: int | str = None):
        super().__init__()
        self._key_note: og.KeyNote  = og.KeyNote(key)

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.KeyNote():  return self._key_note
                    case _:             return super().__mod__(operand)
            case og.KeyNote():  return self._key_note.copy()
            case ou.Key():      return self._key_note % ou.Key()
            case ou.Octave():   return self._key_note % ou.Octave()
            case _:             return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._key_note == other_operand % od.DataSource( og.KeyNote() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        key_note_int: int   = self._key_note % od.DataSource( int() )
        pressure_int: int   = self._pressure % od.DataSource( int() )
        channel_int: int    = self._channel % od.DataSource( int() )
        device_list: list   = self._device % od.DataSource( list() )

        on_time_ms = self_position.getTime_ms()
        return [
                {
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0xA0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(key_note_int),
                        "data_byte_2": Element.midi_128(pressure_int),
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["key_note"] = self._key_note.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "key_note" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._key_note = og.KeyNote().loadSerialization(serialization["parameters"]["key_note"])
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'PolyAftertouch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.KeyNote():          self._key_note = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case PolyAftertouch():
                super().__lshift__(operand)
                self._key_note = (operand % od.DataSource( og.KeyNote() )).copy()
            case og.KeyNote() | ou.Key() | ou.Octave():
                                self._key_note << operand
            case _:             super().__lshift__(operand)
        return self

class ProgramChange(Element):
    def __init__(self, program: int = None):
        super().__init__()
        self._program: ou.Program = ou.Program( 0 if program is None else program )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Program():      return self._program
                    case _:                 return super().__mod__(operand)
            case ou.Program():      return self._program.copy()
            case int() | float():   return self._program % od.DataSource( int() )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other_operand: o.Operand) -> bool:
        match other_operand:
            case self.__class__():
                return super().__eq__(other_operand) \
                    and self._program == other_operand % od.DataSource( ou.Program() )
            case _:
                return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        program_int: int    = self._program % od.DataSource( int() )
        channel_int: int    = self._channel % od.DataSource( int() )
        device_list: list   = self._device % od.DataSource( list() )

        on_time_ms = self_position.getTime_ms()
        return [
                {
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0xC0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(program_int),
                        "data_byte_2": None,
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["program"] = self._program % od.DataSource( int() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "program" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._program   = ou.Program()  << od.DataSource( serialization["parameters"]["program"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'ProgramChange':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Program():          self._program = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case ProgramChange():
                super().__lshift__(operand)
                self._program = (operand % od.DataSource( ou.Program() )).copy()
            case ou.Program() | int() | float():
                self._program << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case ou.Program() | int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._program + operand
            case _:             return super().__add__(operand)
        return self_copy

    def __sub__(self, operand: o.Operand) -> 'Element':
        self_copy = self.copy()
        match operand:
            case ou.Program() | int() | float() | ou.Integer() | ov.Float() | Fraction():
                self_copy << self._program - operand
            case _:             return super().__sub__(operand)
        return self_copy

class Panic(Element):
    def getPlayList(self, position: ot.Position = None):
        self_position: ot.Position  = self._position + ot.Position() if position is None else position

        self_playlist = []
        self_playlist.extend((ControlChange(123) << ou.ControlValue(0)).getPlayList(self_position))
        self_playlist.extend(PitchBend(0).getPlayList(self_position))
        self_playlist.extend((ControlChange(64) << ou.ControlValue(0)).getPlayList(self_position))
        self_playlist.extend((ControlChange(1) << ou.ControlValue(0)).getPlayList(self_position))
        self_playlist.extend((ControlChange(121) << ou.ControlValue(0)).getPlayList(self_position))

        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )
        on_time_ms = self_position.getTime_ms()
        for key_note_midi in range(128):
            self_playlist.append(
                {   # Needs the Note On first in order to the following Note Off not be considered redundant
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": key_note_midi,
                        "data_byte_2": 0,   # 0 means it will result in no sound
                        "device": device_list
                    }
                },
                {
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": key_note_midi,
                        "data_byte_2": 0,
                        "device": device_list
                    }
                }
            )

        self_playlist.extend((ControlChange(7) << ou.ControlValue(100)).getPlayList(self_position))
        self_playlist.extend((ControlChange(11) << ou.ControlValue(127)).getPlayList(self_position))

        return self_playlist

    # CHAINABLE OPERATIONS



# Voice Message           Status Byte      Data Byte1          Data Byte2
# -------------           -----------   -----------------   -----------------
# Note off                      8x      Key number          Note Off velocity
# Note on                       9x      Key number          Note on velocity
# Polyphonic Key Pressure       Ax      Key number          Amount of pressure
# Control Change                Bx      Controller number   Controller value
# Program Change                Cx      Program number      None
# Channel Pressure              Dx      Pressure value      None            
# Pitch Bend                    Ex      MSB                 LSB

# System Real-Time Message         Status Byte 
# ------------------------         -----------
# Timing Clock                         F8
# Start Sequence                       FA
# Continue Sequence                    FB
# Stop Sequence                        FC
# Active Sensing                       FE
# System Reset                         FF
