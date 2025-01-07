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
from typing import Union, TYPE_CHECKING, TypeVar, Optional, List
from fractions import Fraction
import json
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_staff as os
import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_label as ol
import operand_frame as of
import operand_generic as og
import operand_frame as of

TypeElement = TypeVar('TypeElement', bound='Element')  # TypeElement represents any subclass of Operand


if TYPE_CHECKING:
    from operand_container import Sequence

class Element(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        self._position: ra.Position         = ra.Position()
        self._duration: ra.Duration         = ra.Duration(os.staff._duration)
        self._stackable: ou.Stackable       = ou.Stackable()
        self._channel: ou.Channel           = ou.Channel()
        self._device: od.Device             = od.Device()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def position(self: TypeElement, position: float = None) -> TypeElement:
        self._position = ra.Position(position)
        return self

    def duration(self: 'TypeElement', duration: float = None) -> 'TypeElement':
        self._duration = ra.Duration(duration)
        return self

    def stackable(self: 'TypeElement', stackable: bool = None) -> 'TypeElement':
        self._stackable = ou.Stackable(stackable)
        return self

    def channel(self: TypeElement, channel: int = None) -> TypeElement:
        self._channel = ou.Channel(channel)
        return self

    def device(self: 'TypeElement', device: list[str] = None) -> 'TypeElement':
        self._device = od.Device(device)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of an Element,
        those Parameters can be Position, Duration, midi Channel and midi Device

        Examples
        --------
        >>> element = Element()
        >>> element % Device() % list() >> Print()
        ['loopMIDI', 'Microsoft']
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ra.Position():     return self._position
                    case ra.Duration():     return self._duration
                    case ou.Stackable():    return self._stackable
                    case ou.Channel():      return self._channel
                    case od.Device():       return self._device
                    case Element():         return self
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % (operand % o.Operand())
            case ra.Duration():     return self._duration % operand
            case ra.Length():       return ra.Length(self._position)
            case ra.Position():     return self._position.copy()
            case ra.TimeValue() | ou.TimeUnit() \
                | og.TimeSignature() | ra.BeatsPerMeasure() | ra.BeatNoteValue() | ra.NotesPerMeasure() \
                | ra.Tempo() | ra.Quantization():
                                    return self._position % operand
            case ou.Stackable():    return self._stackable.copy()
            case ou.Channel():      return self._channel.copy()
            case od.Device():       return self._device.copy()
            case Element():         return self.copy()
            case od.Start():        return self.start()
            case od.End():          return self.finish()
            case int():             return self._position % operand
            case float():           return self._duration % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: 'o.Operand') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return  self._position      == other % od.DataSource( ra.Position() ) \
                    and self._duration      == other % od.DataSource( ra.Duration() ) \
                    and self._stackable     == other % od.DataSource( ou.Stackable() ) \
                    and self._channel       == other % od.DataSource( ou.Channel() ) \
                    and self._device        == other % od.DataSource( od.Device() )
            case ra.Duration():
                return self._duration == other
            case ra.TimeValue() | ou.TimeUnit():
                return self._position == other
            case _:
                if other.__class__ == o.Operand:
                    return True
                if type(other) == ol.Null:
                    return False    # Makes sure ol.Null ends up processed as False
                return self % other == other

    def __lt__(self, other: 'o.Operand') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return  False
            case ra.Duration():
                return self._duration < other
            case ra.TimeValue() | ou.TimeUnit():
                return self._position < other
            case _:
                return self % od.DataSource( other ) < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return  False
            case ra.Duration():
                return self._duration > other
            case ra.TimeValue() | ou.TimeUnit():
                return self._position > other
            case _:
                return self % od.DataSource( other ) > other
    
    def __le__(self, other: 'o.Operand') -> bool:
        return self == other or self < other
    
    def __ge__(self, other: 'o.Operand') -> bool:
        return self == other or self > other

    def start(self) -> ra.Position:
        return self._position.copy()

    def finish(self) -> ra.Position:
        return self._position + self._duration

    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        return [
                {
                    "time_ms":  self.get_time_ms(self_position_ms)
                }
            ]

    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        midi_track: ou.MidiTrack = ou.MidiTrack() if not isinstance(midi_track, ou.MidiTrack) else midi_track

        if isinstance(position, ra.Position):
            self_numerator: int = position % ra.BeatsPerMeasure() % int()
            self_denominator: int = int(1 / (position % ra.BeatNoteValue() % Fraction()))
            self_position: float = (position.getBeats() + position.getBeats(self._position)) % od.DataSource( float() )
            self_duration: float = position.getBeats(self._duration) % od.DataSource( float() )
            self_tempo: float = position._tempo % od.DataSource( float() )
        else:
            self_numerator: int = self._position % ra.BeatsPerMeasure() % int()
            self_denominator: int = int(1 / (self._position % ra.BeatNoteValue() % Fraction()))
            self_position: float = self._position % od.DataSource( float() )
            self_duration: float = self._position.getBeats(self._duration) % od.DataSource( float() )
            self_tempo: float = self._position._tempo % od.DataSource( float() )

        return [
                {
                    "event":        "Element",
                    "track":        midi_track % int() - 1,  # out of range shouldn't be exported as a midi track
                    "track_name":   midi_track % str(),
                    "numerator":    self_numerator,
                    "denominator":  self_denominator,
                    "channel":      Element.midi_16(self._channel % int() - 1),
                    "time":         self_position,      # beats
                    "duration":     self_duration,      # beats
                    "tempo":        self_tempo          # bpm
                }
            ]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["position"]     = self.serialize(self._position)
        serialization["parameters"]["duration"]     = self.serialize(self._duration)
        serialization["parameters"]["stackable"]    = self.serialize(self._stackable)
        serialization["parameters"]["channel"]      = self.serialize(self._channel)
        serialization["parameters"]["device"]       = self.serialize(self._device)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Element':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "duration" in serialization["parameters"] and
            "stackable" in serialization["parameters"] and "channel" in serialization["parameters"] and "device" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position      = self.deserialize(serialization["parameters"]["position"])
            self._duration      = self.deserialize(serialization["parameters"]["duration"])
            self._stackable     = self.deserialize(serialization["parameters"]["stackable"])
            self._channel       = self.deserialize(serialization["parameters"]["channel"])
            self._device        = self.deserialize(serialization["parameters"]["device"])

        return self

    def __lshift__(self, operand: o.Operand) -> 'Element':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():
                super().__lshift__(operand)
                self._position      << operand._position
                self._duration      << operand._duration
                self._stackable     << operand._stackable
                self._channel       << operand._channel
                self._device        << operand._device
            case od.DataSource():
                match operand % o.Operand():
                    case ra.Position():     self._position  = operand % o.Operand()
                    case ra.Duration():     self._duration  = operand % o.Operand()
                    case ou.Stackable():    self._stackable = operand % o.Operand()
                    case ou.Channel():      self._channel   = operand % o.Operand()
                    case od.Device():       self._device    = operand % o.Operand()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Duration() | float() | Fraction():
                self._duration      << operand
            case ra.Position() | ra.TimeValue() | ou.TimeUnit() | int() \
                | og.TimeSignature() | ra.BeatsPerMeasure() | ra.BeatNoteValue() | ra.NotesPerMeasure() \
                | ra.Tempo() | ra.Quantization():
                self._position      << operand
            case ou.Stackable():
                self._stackable     << operand
            case ou.Channel():
                self._channel       << operand
            case od.Device():
                self._device        << operand
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    # operand is the pusher
    def __rrshift__(self, operand: o.Operand) -> 'Element':
        import operand_container as oc
        match operand:
            case ra.Length():
                return self.copy() << self % od.DataSource( ra.Position() ) + operand
            case ra.Position():
                return self.copy() << operand
            case Element() | oc.Sequence():
                return operand + self >> od.Stack()
            case od.Serialization():
                return operand % od.DataSource() >> self
            case od.Playlist():
                return operand >> od.Playlist(self.getPlaylist())
            case _:
                return super().__rrshift__(operand)

    def __add__(self, operand: any) -> 'Element':
        import operand_container as oc
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():
                return oc.Sequence(self, operand)   # copy already included in Sequence initiation
            case oc.Sequence():
                return operand.__radd__(self)
            case _:
                return self.copy() << self % operand + operand

    def __sub__(self, operand: any) -> 'Element':
        import operand_container as oc
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        return self.copy() << self % operand - operand

    def __mul__(self, operand: any) -> Union['Element', 'Sequence']:
        import operand_container as oc
        if isinstance(operand, int):    # Allows Frame skipping !
            new_sequence: oc.Sequence = oc.Sequence()
            for _ in range(operand):
                new_sequence += self # copy of element already included in Element processing
            return new_sequence.stack()
        elif isinstance(operand, ra.TimeValue):
            self_time_value: ra.TimeValue = self._duration % operand
            self_repeating: int = (operand // Fraction()) // (self_time_value // Fraction())
            return self.__mul__(self_repeating)
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        return self.copy() << self % operand * operand

    def __truediv__(self, operand: o.Operand) -> 'Element':
        import operand_container as oc
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        return self.copy() << self % operand / operand

    def get_position_duration_ms(self, position: ra.Position = None) -> tuple:
        sequence_position_ms: Fraction = Fraction(0)
        if isinstance(position, ra.Position):
            sequence_position_ms = position.getMillis_rational()
        element_position_ms: Fraction = self._position.getMillis_rational()
        self_position_ms: Fraction = sequence_position_ms + element_position_ms
        self_duration_ms: Fraction = self._position.getMillis_rational(self._duration)
        return self_position_ms,self_duration_ms
    
    @staticmethod
    def midi_128(midi_value: int | float = 0):
        return min(max(int(midi_value), 0), 127)

    @staticmethod
    def midi_16(midi_value: int | float = 0):
        return min(max(int(midi_value), 0), 15)
    
    @staticmethod
    def get_time_ms(rational: Fraction, precision: int = 3) -> float:
        precision = min(max(int(precision), 0), 12)
        return max(0.0, float(round(float(rational), precision)))

class Loop(Element):
    # Basically it's a short Sequence with a Position that can be used and placed as a loop
    ...

class Clock(Element):
    def __init__(self, *parameters):
        super().__init__()
        self._duration      << os.staff._measures
        self._pulses_per_quarternote: ou.PPQN = ou.PPQN()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def ppqn(self: 'Clock', ppqn: int = None) -> 'Clock':
        self._pulses_per_quarternote = ou.PPQN(ppqn)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Clock,
        those Parameters are the ones of the Element, like Position and Duration,
        plus the Pulses Per Quarter Note, the last one as 24 by default.

        Examples
        --------
        >>> clock = Clock(4)
        >>> clock % Duration() >> Print(0)
        {'class': 'Duration', 'parameters': {'time_unit': {'class': 'Measure', 'parameters': {'value': 4.0}}}}
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.PPQN():         return self._pulses_per_quarternote
                    case _:                 return super().__mod__(operand)
            case ou.PPQN():         return self._pulses_per_quarternote.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pulses_per_quarternote == other % od.DataSource( ou.PPQN() )
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        device_list: list = self._device % od.DataSource( list() )
        pulses_per_note: Fraction = 4 * self._pulses_per_quarternote % od.DataSource( Fraction() )
        pulses_per_beat: Fraction = pulses_per_note * (self._position % ra.BeatNoteValue() % od.DataSource( Fraction() ))
        total_clock_pulses: int = (pulses_per_beat * self._position.getBeats(self._duration)) % od.DataSource( int() )

        single_pulse_duration_ms: Fraction = self_duration_ms / total_clock_pulses

        # First quarter note pulse (total 1 in 24 pulses per quarter note)
        self_playlist = [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xFA,    # Start Sequence
                        "device": device_list
                    }
                }
            ]

        # Middle quarter note pulses (total 23 in 24 pulses per quarter note)
        for clock_pulse in range(1, total_clock_pulses):
            self_playlist.append(
                {
                    "time_ms": self.get_time_ms(single_pulse_duration_ms * clock_pulse),
                    "midi_message": {
                        "status_byte": 0xF8,    # Timing Clock
                        "device": device_list
                    }
                }
            )

        # Last quarter note pulse (45 pulses where this last one sets the stop)
        self_playlist.append(
            {
                "time_ms": self.get_time_ms(single_pulse_duration_ms * total_clock_pulses),
                "midi_message": {
                    "status_byte": 0xFC,    # Stop Sequence
                    "device": device_list
                }
            }
        )
        
        return self_playlist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pulses_per_quarternote"]   = self.serialize( self._pulses_per_quarternote )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pulses_per_quarternote" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pulses_per_quarternote    = self.deserialize( serialization["parameters"]["pulses_per_quarternote"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'Clock':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Clock():
                super().__lshift__(operand)
                self._pulses_per_quarternote << operand._pulses_per_quarternote
            case od.DataSource():
                match operand % o.Operand():
                    case ou.PPQN():         self._pulses_per_quarternote = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case ou.PPQN():         self._pulses_per_quarternote << operand
            case _: super().__lshift__(operand)
        return self

class Rest(Element):

    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )

        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0x00 | 0x0F & Element.midi_16(channel_int - 1),
                        "device": device_list
                    }
                },
                {
                    "time_ms": self.get_time_ms(self_position_ms + self_duration_ms),
                    "midi_message": {
                        "status_byte": 0x00 | 0x0F & Element.midi_16(channel_int - 1),
                        "device": device_list
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = super().getMidilist(midi_track, position)
        self_midilist[0]["event"]       = "Rest"
        return self_midilist

class Note(Element):
    def __init__(self, *parameters):
        self._pitch: og.Pitch       = og.Pitch()
        self._velocity: ou.Velocity = os.staff._velocity.copy()
        self._gate: ra.Gate         = ra.Gate(1.0)
        self._tied: ou.Tied         = ou.Tied(False)
        super().__init__(*parameters)

    def pitch(self: 'Note', key: Optional[ou.Key] = None, octave: Optional[int] = None) -> 'Note':
        self._pitch = og.Pitch(key, octave)
        return self

    def velocity(self: 'Note', velocity: int = None) -> 'Note':
        self._velocity = og.Pitch(velocity)
        return self

    def gate(self: 'Note', gate: float = None) -> 'Note':
        self._gate = og.Pitch(gate)
        return self

    def tied(self: 'Note', tied: bool = None) -> 'Note':
        self._tied = og.Pitch(tied)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Note,
        those Parameters are the ones of the Element, like Position and Duration,
        plus the Rest's Duration and Pitch, Velocity and Gate, the last one
        with a value of 0.90 by default.

        Examples
        --------
        >>> note = Note("F")
        >>> note % Key() % str() >> Print()
        F
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Pitch():        return self._pitch
                    case ou.Velocity():     return self._velocity
                    case ra.Gate():         return self._gate
                    case ou.Tied():         return self._tied
                    case _:                 return super().__mod__(operand)
            case og.Pitch():        return self._pitch.copy()
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | int() | str() | ou.Key() | ou.Octave() | ou.Natural() | ou.Degree() | og.Scale() | ou.Mode() | list():
                                    return self._pitch % operand
            case ou.Velocity():     return self._velocity.copy()
            case ra.Gate():         return self._gate.copy()
            case ou.Tied():         return self._tied.copy()
            case int():             return self._pitch._degree % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pitch     == other._pitch \
                    and self._velocity  == other._velocity \
                    and self._gate      == other._gate \
                    and self._tied      == other._tied
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )
        key_note_float: float       = self._pitch % od.DataSource( float() )
        velocity_int: int           = self._velocity % od.DataSource( int () )

        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(key_note_float),
                        "data_byte_2": Element.midi_128(velocity_int),
                        "device": device_list
                    }
                },
                {
                    "time_ms": self.get_time_ms(self_position_ms + self_duration_ms * self._gate._rational),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(key_note_float),
                        "data_byte_2": 0,
                        "device": device_list
                    }
                }
            ]

    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = super().getMidilist(midi_track, position)
        self_midilist[0]["event"]       = "Note"
        self_midilist[0]["duration"]    = self._duration % od.DataSource( ra.Beats() ) % float() * (self._gate % float())
        self_midilist[0]["bend"]        = Element.midi_128(self._pitch % float())
        self_midilist[0]["velocity"]    = Element.midi_128(self._velocity % int())
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pitch"]    = self.serialize( self._pitch )
        serialization["parameters"]["velocity"] = self.serialize( self._velocity )
        serialization["parameters"]["gate"]     = self.serialize( self._gate )
        serialization["parameters"]["tied"]     = self.serialize( self._tied )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pitch" in serialization["parameters"] and "velocity" in serialization["parameters"] and "gate" in serialization["parameters"] and
            "tied" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pitch     = self.deserialize( serialization["parameters"]["pitch"] )
            self._velocity  = self.deserialize( serialization["parameters"]["velocity"] )
            self._gate      = self.deserialize( serialization["parameters"]["gate"] )
            self._tied      = self.deserialize( serialization["parameters"]["tied"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Note':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Note():
                super().__lshift__(operand)
                self._pitch         << operand._pitch
                self._velocity      << operand._velocity
                self._gate          << operand._gate
                self._tied          << operand._tied
            case od.DataSource():
                match operand % o.Operand():
                    case og.Pitch():        self._pitch     = operand % o.Operand()
                    case ou.Degree():       self._degree    = operand % o.Operand()
                    case ou.Velocity():     self._velocity  = operand % o.Operand()
                    case ra.Gate():         self._gate      = operand % o.Operand()
                    case ou.Tied():         self._tied      = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | og.Pitch() | ou.Key() | ou.Octave() | ou.Tone() | ou.Semitone() \
                | ou.Semitone() | ou.Natural() | ou.Degree() | og.Scale() | ou.Mode() | int() | str() | None:
                                    self._pitch << operand
            case ou.DrumKit():
                                    self << od.DataSource( ou.Channel(10) )
                                    self._pitch << operand
            case ou.Velocity():     self._velocity << operand
            case ra.Gate():         self._gate << operand
            case ou.Tied():         self._tied << operand
            case _:                 super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Note':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                return self.copy() << od.DataSource( self._pitch + operand )    # Specific parameter
            case _:
                return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'Note':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                return self.copy() << od.DataSource( self._pitch - operand )    # Specific parameter
            case _:
                return super().__sub__(operand)


class Cluster(Rest):
    def __init__(self, *parameters):
        self._pitches: list[og.Pitch] = [og.Pitch(1), og.Pitch(3), og.Pitch(5)]
        super().__init__( *parameters )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case list():            return self._pitches
                    case _:                 return super().__mod__(operand)
            case list():            return self.deep_copy(self._pitches)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pitches  == other % od.DataSource( list() )
            case _:
                return super().__eq__(other)
    
    def get_cluster_notes(self) -> list[Note]:
        cluster_notes: list[Note] = []
        for single_pitch in self._pitches:
            cluster_notes.append( Note(self, single_pitch) )
        return cluster_notes

    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist: list = []
        for single_element in self.get_cluster_notes():
            self_playlist.extend(single_element.getPlaylist(position))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = []
        for single_element in self.get_cluster_notes():
            self_midilist.extend(single_element.getMidilist(midi_track, position))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pitches"] = self.serialize( self._pitches )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Cluster':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pitches" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pitches  = self.deserialize( serialization["parameters"]["pitches"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'Cluster':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        if not isinstance(operand, tuple):
            for single_element in self._pitches:
                single_element << operand
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case list():                self._pitches = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case Cluster():
                super().__lshift__(operand)
                self._pitches  = self.deep_copy(operand % od.DataSource( list() ))
            case list():
                if len(operand) > 0 and all(isinstance(single_pitch, og.Pitch) for single_pitch in operand):
                    self._pitches = self.deep_copy(operand)
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | og.Pitch() | ou.Key() | ou.Octave() | ou.Tone() | ou.Semitone() \
                | ou.Semitone() | ou.Natural() | ou.Degree() | og.Scale() | ou.Mode() | int() | str() | None:
                for single_pitch in self._pitches:
                    single_pitch << operand
            case ou.DrumKit():
                self << od.DataSource( ou.Channel(10) )
                for single_pitch in self._pitches:
                    single_pitch << operand
            case _:
                super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Cluster':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                self_copy = self.copy()
                for single_pitch in self_copy._pitches:
                    single_pitch << od.DataSource( single_pitch + operand ) # Specific parameter
                return self_copy
            case _:
                return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'Cluster':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                self_copy = self.copy()
                for single_pitch in self_copy._pitches:
                    single_pitch << od.DataSource( single_pitch - operand ) # Specific parameter
                return self_copy
            case _:
                return super().__sub__(operand)
    
class Dyad(Cluster):
    # In music, a dyad is a set of two notes or pitches.
    ...

class KeyScale(Note):
    def __init__(self, *parameters):
        super().__init__()
        self << self._position.getDuration(ra.Measures(1))  # By default a Scale and a Chord has one Measure duration
        self._scale: og.Scale  = og.Scale("Major")    # Major scale as default
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def scale(self: 'KeyScale', scale: list[int] | str = None) -> 'KeyScale':
        self._scale = og.Scale(scale)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a KeyScale,
        those Parameters are the ones of the Element, like Position and Duration,
        together with the ones of a Note, like Duration and Pitch,
        plus the Scale and Mode, the last one as 1 by default.

        Examples
        --------
        >>> scale = KeyScale()
        >>> scale % str() >> Print()
        Major
        >>> scale << "minor"
        >>> scale % str() >> Print()
        minor
        >>> scale % list() >> Print()
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Scale():        return self._scale
                    case _:                 return super().__mod__(operand)
            case og.Scale():        return self._scale.copy()
            case list() | ou.Mode():
                                    return self._scale % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._scale == other._scale
            case _:
                return super().__eq__(other)
            
    def get_scale_notes(self) -> list[Note]:
        scale_notes: list[Note] = []
        # Sets Scale to be used
        if self._scale.hasScale():
            for key_note_i in range(self._scale.keys()): # presses entire scale, 7 keys for diatonic scales
                transposition: int = self._scale.transposition(key_note_i)
                scale_notes.append(Note(self) + float(transposition))
        else:   # Uses the staff keys straight away
            key_note_scale: og.Scale = self._pitch._key % og.Scale()
            for note_i in range(key_note_scale.keys()):
                scale_notes.append(
                    Note(self) + note_i   # Jumps by steps (scale tones)
                )
        return scale_notes
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist = []
        for single_note in self.get_scale_notes():
            self_playlist.extend(single_note.getPlaylist(position))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist = []
        for single_note in self.get_scale_notes():
            self_midilist.extend(single_note.getMidilist(midi_track, position))
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["self_scale"] = self.serialize( self._scale )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeyScale':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "self_scale" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._scale = self.deserialize( serialization["parameters"]["self_scale"] )
        return self
        
    def __lshift__(self, operand: o.Operand) -> 'KeyScale':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyScale():
                super().__lshift__(operand)
                self._scale << operand._scale
            case od.DataSource():
                match operand % o.Operand():
                    case og.Scale():        self._scale = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case og.Scale() | list() | ou.Mode():   # It's the element scale that is set
                self._scale << operand
            case _: super().__lshift__(operand)
        return self

class Chord(KeyScale):
    def __init__(self, *parameters):
        self._size: ou.Size             = ou.Size(3)
        self._inversion: ou.Inversion   = ou.Inversion(0)
        self._dominant: ou.Dominant     = ou.Dominant(0)
        self._diminished: ou.Diminished = ou.Diminished(0)
        self._augmented: ou.Augmented   = ou.Augmented(0)
        self._sus2: ou.Sus2             = ou.Sus2(0)
        self._sus4: ou.Sus4             = ou.Sus4(0)
        super().__init__(*parameters)

    def size(self: 'Chord', size: int = None) -> 'Chord':
        self._size = ou.Size(size)
        return self

    def inversion(self: 'Chord', inversion: int = None) -> 'Chord':
        self._inversion = ou.Inversion(inversion)
        return self

    def dominant(self: 'Chord', dominant: int = None) -> 'Chord':
        self._dominant = ou.Dominant(dominant)
        return self

    def diminished(self: 'Chord', diminished: int = None) -> 'Chord':
        self._diminished = ou.Diminished(diminished)
        return self

    def augmented(self: 'Chord', augmented: int = None) -> 'Chord':
        self._augmented = ou.Augmented(augmented)
        return self

    def sus2(self: 'Chord', sus2: int = None) -> 'Chord':
        self._sus2 = ou.Sus2(sus2)
        return self

    def sus4(self: 'Chord', sus4: int = None) -> 'Chord':
        self._sus4 = ou.Sus4(sus4)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Chord,
        those Parameters are the ones of the Element, like Position and Duration,
        plus the ones of a Note, and the Scale, Degree, Inversion and others.

        Examples
        --------
        >>> chord = Chord("A") << Scale("minor") << Size("7th") << NoteValue(1/2)
        >>> chord % Degree() % str() >> Print()
        I
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Size():         return self._size
                    case ou.Inversion():    return self._inversion
                    case ou.Dominant():     return self._dominant
                    case ou.Diminished():   return self._diminished
                    case ou.Augmented():    return self._augmented
                    case ou.Sus2():         return self._sus2
                    case ou.Sus4():         return self._sus4
                    case _:                 return super().__mod__(operand)
            case ou.Size():         return self._size.copy()
            case ou.Inversion():    return self._inversion.copy()
            case ou.Dominant():     return self._dominant.copy()
            case ou.Diminished():   return self._diminished.copy()
            case ou.Augmented():    return self._augmented.copy()
            case ou.Sus2():         return self._sus2.copy()
            case ou.Sus4():         return self._sus4.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._size          == other % od.DataSource( ou.Size() ) \
                    and self._inversion     == other % od.DataSource( ou.Inversion() ) \
                    and self._dominant      == other % od.DataSource( ou.Dominant() ) \
                    and self._diminished    == other % od.DataSource( ou.Diminished() ) \
                    and self._augmented     == other % od.DataSource( ou.Augmented() ) \
                    and self._sus2          == other % od.DataSource( ou.Sus2() ) \
                    and self._sus4          == other % od.DataSource( ou.Sus4() )
            case _:
                return super().__eq__(other)
    
    def get_chord_notes(self) -> list[Note]:
        chord_notes: list[Note] = []
        max_size = self._scale.keys()
        if max_size % 2 == 0:
            max_size //= 2
        max_size = min(self._size % od.DataSource( int() ), max_size)
        # Sets Scale to be used
        if self._scale.hasScale():
            # modulated_scale: og.Scale = self._scale.copy().modulate(self._mode)
            for note_i in range(max_size):          # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...
                key_degree: int = note_i * 2 + 1    # all odd numbers, 1, 3, 5, ...
                if key_degree == 3:   # Third
                    if self._sus2:
                        key_degree -= 1
                    if self._sus4:
                        key_degree += 1   # cancels out if both sus2 and sus4 are set to true
                transposition: int = self._scale.transposition(key_degree - 1)
                if key_degree == 7:   # Seventh
                    if self._dominant:
                        transposition -= 1
                if key_degree == 3 or key_degree == 5:   # flattens Third and Fifth
                    if self._diminished:
                        transposition -= 1   # cancels out if both dominant and diminished are set to true
                chord_notes.append(
                    Note(self) + float(transposition)   # Jumps by semitones (floats)
                )
        else:   # Uses the staff keys straight away
            # modulated_scale: og.Scale = os.staff % og.Scale(self._mode) # already modulated
            for note_i in range(max_size):          # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...
                key_step: int = note_i * 2
                if key_step == 3:   # Third
                    if self._sus2:
                        key_step -= 1
                    if self._sus4:
                        key_step += 1   # cancels out if both sus2 and sus4 are set to true
                chord_notes.append(
                    Note(self) + key_step   # Jumps by steps (ints have become Degrees!!)
                )

        # Where the inversions are done
        inversion = min(self._inversion % od.DataSource( int() ), len(chord_notes) - 1)
        if inversion > 0:
            first_note = chord_notes[inversion]
            not_first_note = True
            while not_first_note:   # Try to implement while inversion > 0 here
                not_first_note = False
                for single_note in chord_notes:
                    if single_note % og.Pitch() < first_note % og.Pitch():   # Critical operation
                        single_note << single_note % ou.Octave() + 1
                        if single_note % od.DataSource( int() ) < 128:
                            not_first_note = True # to result in another while loop
        return chord_notes
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist = []
        for single_note in self.get_chord_notes():
            self_playlist.extend(single_note.getPlaylist(position))    # extends the list with other list
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist = []
        for single_note in self.get_chord_notes():
            self_midilist.extend(single_note.getMidilist(midi_track, position))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["size"]         = self.serialize( self._size )
        serialization["parameters"]["inversion"]    = self.serialize( self._inversion )
        serialization["parameters"]["dominant"]     = self.serialize( self._dominant )
        serialization["parameters"]["diminished"]   = self.serialize( self._diminished )
        serialization["parameters"]["augmented"]    = self.serialize( self._augmented )
        serialization["parameters"]["sus2"]         = self.serialize( self._sus2 )
        serialization["parameters"]["sus4"]         = self.serialize( self._sus4 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "inversion" in serialization["parameters"] and "size" in serialization["parameters"] and 
            "dominant" in serialization["parameters"] and "diminished" in serialization["parameters"] and 
            "augmented" in serialization["parameters"] and "sus2" in serialization["parameters"] and "sus4" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._size          = self.deserialize( serialization["parameters"]["size"] )
            self._inversion     = self.deserialize( serialization["parameters"]["inversion"] )
            self._dominant      = self.deserialize( serialization["parameters"]["dominant"] )
            self._diminished    = self.deserialize( serialization["parameters"]["diminished"] )
            self._augmented     = self.deserialize( serialization["parameters"]["augmented"] )
            self._sus2          = self.deserialize( serialization["parameters"]["sus2"] )
            self._sus4          = self.deserialize( serialization["parameters"]["sus4"] )
        return self
      
    def __lshift__(self, operand: any) -> 'Chord':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Chord():
                super().__lshift__(operand)
                self._size          << operand._size
                self._inversion     << operand._inversion
                self._dominant      << operand._dominant
                self._diminished    << operand._diminished
                self._augmented     << operand._augmented
                self._sus2          << operand._sus2
                self._sus4          << operand._sus4
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Size():                 self._size = operand % o.Operand()
                    case ou.Inversion():            self._inversion = operand % o.Operand()
                    case ou.Dominant():             self._dominant = operand % o.Operand()
                    case ou.Diminished():           self._diminished = operand % o.Operand()
                    case ou.Augmented():            self._augmented = operand % o.Operand()
                    case ou.Sus2():                 self._sus2 = operand % o.Operand()
                    case ou.Sus4():                 self._sus4 = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case ou.Size():                 self._size << operand
            case ou.Inversion():            self._inversion << operand
            case str():
                operand = operand.strip()
                # Set Chord root note
                self._pitch << operand
                # Set Chord size
                self._size << operand
                # Set Chord scale
                if (operand.find("m") != -1 or operand.find("min") != -1 or operand in {'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'}) \
                    and operand.find("dim") == -1:
                    self._scale << "minor"
                else:
                    self._scale << "Major"
                self.set_all(operand)
            case ou.Dominant():
                if operand:
                    self.set_all()
                self._dominant << operand
            case ou.Diminished():
                if operand:
                    self.set_all()
                self._diminished << operand
            case ou.Augmented():
                if operand:
                    self.set_all()
                self._augmented << operand
            case ou.Sus2():
                if operand:
                    self.set_all()
                self._sus2 << operand
            case ou.Sus4():
                if operand:
                    self.set_all()
                self._sus4 << operand
            case _: super().__lshift__(operand)
        return self
    
    def set_all(self, data: any = False):    # mutual exclusive
        self._dominant << data
        self._diminished << data
        self._augmented << data
        self._sus2 << data
        self._sus4 << data

class Retrigger(Note):
    def __init__(self, *parameters):
        super().__init__()
        self._duration *= 2 # Equivalent to twice single note duration
        self._gate      << 0.50
        self._division  = ou.Division(16)
        self._swing     = ra.Swing(0.50)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def division(self: 'Retrigger', division: int = None) -> 'Retrigger':
        self._division = ou.Division(division)
        return self

    def swing(self: 'Retrigger', swing: int = None) -> 'Retrigger':
        self._swing = ra.Swing(swing)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Retrigger,
        those Parameters are the ones of the Element, like Position and Duration,
        plus the ones of a Note and the Division as 16 by default.

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
                    case ra.Swing():        return self._swing
                    case _:                 return super().__mod__(operand)
            case ou.Division():     return self._division.copy()
            case int():             return self._division % int()
            case ra.Swing():        return self._swing.copy()
            # Returns the SYMBOLIC value of each note
            case ra.Duration():
                return self._duration / 2
            case _:                 return super().__mod__(operand)

    def get_retrigger_notes(self) -> list[Note]:
        retrigger_notes: list[Note] = []
        self_iteration: int = 0
        note_position: ra.Position = self % ra.Position()
        single_note_duration: ra.Duration = self._duration/(self._division % int()) # Already 2x single note duration
        for _ in range(self._division % od.DataSource( int() )):
            swing_ratio = self._swing % od.DataSource( Fraction() )
            if self_iteration % 2: swing_ratio = 1 - swing_ratio
            note_duration: ra.Duration = single_note_duration * 2 * swing_ratio
            retrigger_notes.append(Note(self, note_duration, note_position))
            note_position += note_duration
            self_iteration += 1
        return retrigger_notes

    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist: list = []
        for single_note in self.get_retrigger_notes():
            self_playlist.extend(single_note.getPlaylist(position))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist = []
        for single_note in self.get_retrigger_notes():
            self_midilist.extend(single_note.getMidilist(midi_track, position))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["division"] = self.serialize( self._division )
        serialization["parameters"]["swing"]    = self.serialize( self._swing )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "division" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._division  = self.deserialize( serialization["parameters"]["division"] )
            self._swing     = self.deserialize( serialization["parameters"]["swing"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'Retrigger':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Division():             self._division = operand % o.Operand()
                    case ra.Swing():                self._swing = operand % o.Operand()
                    case _:                         super().__lshift__(operand)
            case Retrigger():
                super().__lshift__(operand)
                self._division  << operand._division
                self._swing     << operand._swing
            case ou.Division() | int():
                if operand > 0:
                    self._division << operand
            case ra.Swing():
                if operand < 0:     self._swing << 0
                elif operand > 1:   self._swing << 1
                else:               self._swing << operand
            case ra.Duration():
                self._duration      << operand * 2  # Equivalent to two sized Notes
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
    def __init__(self, *parameters):
        super().__init__()
        self._division  << ou.Division(3)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Note3':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Division() | int():
                return self # disables the setting of Division, always 3
            case _:                 super().__lshift__(operand)
        return self

class Tuplet(Element):
    def __init__(self, *parameters):
        super().__init__()
        self._duration *= 2 # Equivalent to twice single note duration
        self._swing     = ra.Swing(.50)
        self._elements: list[Element] = [Note(ra.Gate(0.5)), Note(ra.Gate(0.5)), Note(ra.Gate(0.5))]
        self.set_elements_duration()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def swing(self: 'Tuplet', swing: int = None) -> 'Tuplet':
        self._swing = ra.Swing(swing)
        return self

    def elements(self: 'Tuplet', elements: Optional[List['Element']] = None) -> 'Tuplet':
        if isinstance(elements, list) and all(isinstance(element, Element) for element in elements):
            self._elements = elements
        return self

    def set_elements_duration(self):
        if len(self._elements) > 0:
             # Already 2x single note duration
            elements_duration = self._duration / len(self._elements) # from 2 notes to division
            if len(self._elements) == 2:
                 # Already 2x single note duration
                elements_duration = self._duration/2 * 3/2 # from 3 notes to 2
            for single_element in self._elements:
                single_element << elements_duration

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Tuplet,
        those Parameters are the ones of the Element, like Position and Duration,
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
                    case ra.Swing():        return self._swing
                    case list():            return self._elements
                    case _:                 return super().__mod__(operand)
            case ra.Swing():        return self._swing.copy()
            case ou.Division():     return ou.Division() << len(self._elements)
            case int():             return len(self._elements)
            case ra.Duration():
                return self._duration / 2
            case list():            return self.deep_copy(self._elements)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._swing     == other % od.DataSource( ra.Swing() ) \
                    and self._elements  == other % od.DataSource( list() )
            case _:
                return super().__eq__(other)
    
    def get_tuplet_elements(self) -> list[Element]:
        tuplet_elements: list[Element] = []
        element_position: ra.Position = self % ra.Position()
        self_iteration: int = 0
        for single_element in self._elements:
            element_duration = single_element % od.DataSource( ra.Duration() )
            tuplet_elements.append(single_element.copy() << element_position)
            swing_ratio = self._swing % od.DataSource( Fraction() )
            if self_iteration % 2:
                swing_ratio = 1 - swing_ratio
            element_position += element_duration * 2 * swing_ratio
            self_iteration += 1
        return tuplet_elements

    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist: list = []
        for single_element in self.get_tuplet_elements():
            self_playlist.extend(single_element.getPlaylist(position))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = []
        for single_element in self.get_tuplet_elements():
            self_midilist.extend(single_element.getMidilist(midi_track, position))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["swing"]    = self.serialize( self._swing )
        serialization["parameters"]["elements"] = self.serialize( self._elements )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Tuplet':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "swing" in serialization["parameters"] and "elements" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._swing     = self.deserialize( serialization["parameters"]["swing"] )
            self._elements  = self.deserialize( serialization["parameters"]["elements"] )
        return self

    def __lshift__(self, operand: o.Operand) -> 'Tuplet':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        if not isinstance(operand, tuple):
            for single_element in self._elements:
                single_element << operand
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ra.Swing():            self._swing = operand % o.Operand()
                    case list():                self._elements = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case Tuplet():
                super().__lshift__(operand)
                self._swing     << operand._swing
                self._elements  = self.deep_copy(operand % od.DataSource( list() ))
            case ra.Swing():
                if operand < 0:     self._swing << 0
                elif operand > 1:   self._swing << 1
                else:               self._swing << operand
            case ra.Duration():
                self._duration      << operand * 2  # Equivalent to two sized Notes
            case list():
                                                                     # Rest because is the root super class with Duration
                if len(operand) > 0 and all(isinstance(single_element, Rest) for single_element in operand):
                    self._elements = self.deep_copy(operand)
            case _:
                super().__lshift__(operand)
        self.set_elements_duration()
        return self

class Triplet(Tuplet):
    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand | list[Element]) -> 'Triplet':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case list():
                if len(operand) == 3:
                    super().__lshift__(operand)
                return self
            case _: super().__lshift__(operand)
        return self

class Automation(Element):
    def __init__(self, *parameters):
        super().__init__()
        self._duration      << self._position % od.DataSource( ra.Quantization() )  # Equivalent to one Step

class ControlChange(Automation):
    def __init__(self, *parameters):
        super().__init__()
        self._controller: og.Controller = os.staff % og.Controller()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def controller(self: 'ControlChange', number: Optional[int] = None, value: Optional[int] = None) -> 'ControlChange':
        self._controller = og.Controller(
                ou.Number(number), ou.Value(value)
            )
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a ControlChange,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Controller Number and Value as Number and Value.

        Examples
        --------
        >>> controller = Controller("Modulation")
        >>> controller % Number() % int() >> Print()
        1
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Controller():       return self._controller
                    case _:                     return super().__mod__(operand)
            case og.Controller():       return self._controller.copy()
            case ou.Number():           return self._controller % ou.Number()
            case ou.Value():            return self._controller % ou.Value()
            case int() | float():       return self._controller % operand
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._controller == other % od.DataSource( og.Controller() )
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        number_int: int             = self % ou.Number() % od.DataSource( int() )
        value_int: int              = self % ou.Value() % od.DataSource( int() )
        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )

        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(number_int),
                        "data_byte_2": Element.midi_128(value_int),
                        "device": device_list
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = super().getMidilist(midi_track, position)
        self_midilist[0]["event"]       = "ControllerEvent"
        self_midilist[0]["number"]      = Element.midi_128(self._controller._number % int())
        self_midilist[0]["value"]       = Element.midi_128(self._controller._value % int())
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["controller"] = self.serialize( self._controller )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "controller" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._controller = self.deserialize( serialization["parameters"]["controller"] )
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
                self._controller << operand._controller
            case og.Controller() | ou.Number() | ou.Value() | int() | float() | str():
                self._controller << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'ControlChange':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | float() | ou.Value():
                return self.copy() << od.DataSource( self._controller + operand )   # Specific parameter
            case _:
                return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'ControlChange':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | float() | ou.Value():
                return self.copy() << od.DataSource( self._controller - operand )   # Specific parameter
            case _:
                return super().__sub__(operand)

class PitchBend(Automation):
    def __init__(self, *parameters):
        super().__init__()
        self._bend: ou.Bend = ou.Bend()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def bend(self: 'PitchBend', bend: Optional[int] = None) -> 'PitchBend':
        self._bend = ou.Bend(bend)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a PitchBend,
        those Parameters are the ones of the Element, like Position and Duration,
        and the PitchBend bend with 0 as default.

        Examples
        --------
        >>> pitch_bend = PitchBend(8190 / 2 + 1)
        >>> pitch_bend % int() >> Print()
        4096
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Bend():         return self._bend
                    case _:                 return super().__mod__(operand)
            case ou.Bend():         return self._bend.copy()
            case int() | float():   return self._bend % od.DataSource( int() )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._bend == other % od.DataSource( ou.Bend() )
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        msb_midi: int               = self._bend % ol.MSB()
        lsb_midi: int               = self._bend % ol.LSB()
        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )

        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xE0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": lsb_midi,
                        "data_byte_2": msb_midi,
                        "device": device_list
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = super().getMidilist(midi_track, position)
        self_midilist[0]["event"]       = "PitchWheelEvent"
        self_midilist[0]["value"]       = self._bend % int()
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["bend"] = self.serialize( self._bend )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "bend" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._bend = self.deserialize( serialization["parameters"]["bend"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'PitchBend':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Bend():             self._bend = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case PitchBend():
                super().__lshift__(operand)
                self._bend << operand._bend
            case ou.Bend() | int() | float():  self._bend << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'PitchBend':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Bend() | int() | float() | ou.Bend() | Fraction():
                return self.copy() << od.DataSource( self._bend + operand )   # Specific parameter
            case _:
                return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'PitchBend':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Bend() | int() | float() | ou.Bend() | Fraction():
                return self.copy() << od.DataSource( self._bend - operand )   # Specific parameter
            case _:
                return super().__sub__(operand)

class Aftertouch(Automation):
    def __init__(self, *parameters):
        super().__init__()
        self._pressure: ou.Pressure = ou.Pressure()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def pressure(self: 'Aftertouch', pressure: Optional[int] = None) -> 'Aftertouch':
        self._pressure = ou.Bend(pressure)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Aftertouch,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Aftertouch pressure with 0 as default.

        Examples
        --------
        >>> aftertouch = Aftertouch(2) << Pressure(128 / 2)
        >>> aftertouch % Pressure() % int() >> Print()
        64
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Pressure():     return self._pressure
                    case _:                 return super().__mod__(operand)
            case ou.Pressure():     return self._pressure.copy()
            case int() | float():   return self._pressure % od.DataSource( int() )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pressure == other % od.DataSource( ou.Pressure() )
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        pressure_int: int           = self._pressure % od.DataSource( int() )
        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )

        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xD0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte": Element.midi_128(pressure_int),
                        "device": device_list
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = super().getMidilist(midi_track, position)
        self_midilist[0]["event"]       = "ChannelPressure"
        self_midilist[0]["pressure"]    = Element.midi_128(self._pressure % int())
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pressure"] = self.serialize( self._pressure )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pressure" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pressure = self.deserialize( serialization["parameters"]["pressure"] )
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
                self._pressure << operand._pressure
            case ou.Pressure() | int() | float():
                self._pressure << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'Aftertouch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Pressure() | int() | float() | ou.Pressure() | Fraction():
                return self.copy() << od.DataSource( self._pressure + operand )   # Specific parameter
            case _:
                return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'Aftertouch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Pressure() | int() | float() | ou.Pressure() | Fraction():
                return self.copy() << od.DataSource( self._pressure - operand )   # Specific parameter
            case _:
                return super().__sub__(operand)

class PolyAftertouch(Aftertouch):
    def __init__(self, *parameters):
        super().__init__()
        self._pitch: og.Pitch  = og.Pitch()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def pitch(self: 'PolyAftertouch', key: Optional[ou.Key] = None, octave: Optional[int] = None) -> 'PolyAftertouch':
        self._pitch = og.Pitch(key, octave)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a PolyAftertouch,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Key together with the PolyAftertouch pressure with value 0 as default.

        Examples
        --------
        >>> poly_aftertouch = PolyAftertouch("E") << Pressure(128 / 2)
        >>> poly_aftertouch % Channel() >> Print(0)
        {'class': 'Channel', 'parameters': {'unit': 0}}
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Pitch():  return self._pitch
                    case _:             return super().__mod__(operand)
            case og.Pitch():  return self._pitch.copy()
            case int() | float():
                    return self._pitch % operand
            case ou.Octave():   return self._pitch % ou.Octave()
            case _:             return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pitch == other % od.DataSource( og.Pitch() )
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        key_note_float: float       = self._pitch % od.DataSource( float() )
        pressure_int: int           = self._pressure % od.DataSource( int() )
        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )

        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xA0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte_1": Element.midi_128(key_note_float),
                        "data_byte_2": Element.midi_128(pressure_int),
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pitch"] = self.serialize( self._pitch )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pitch" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pitch = self.deserialize( serialization["parameters"]["pitch"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'PolyAftertouch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case og.Pitch():          self._pitch = operand % o.Operand()
                    case _:                     super().__lshift__(operand)
            case PolyAftertouch():
                super().__lshift__(operand)
                self._pitch << operand._pitch
            case og.Pitch() | ou.Key() | ou.Octave() | ou.Flat() | ou.Sharp() | ou.Natural() | int() | float() | str():
                                self._pitch << operand
            case _:             super().__lshift__(operand)
        return self

class ProgramChange(Automation):
    def __init__(self, *parameters):
        super().__init__()
        self._program: ou.Program = ou.Program()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def program(self: 'ProgramChange', program: Optional[int] = None) -> 'ProgramChange':
        self._program = og.Pitch(program)
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a ProgramChange,
        those Parameters are the ones of the Element, like Position and Duration,
        and the ProgramChange number with a value of 0 as default.

        Examples
        --------
        >>> program_change = ProgramChange(12)
        >>> program_change % Program() >> Print(0)
        {'class': 'Program', 'parameters': {'unit': 12}}
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ou.Program():      return self._program
                    case _:                 return super().__mod__(operand)
            case ou.Program():      return self._program.copy()
            case int() | float():   return self._program % od.DataSource( int() )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._program == other % od.DataSource( ou.Program() )
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        program_int: int            = self._program % od.DataSource( int() )
        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )

        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xC0 | 0x0F & Element.midi_16(channel_int - 1),
                        "data_byte": Element.midi_128(program_int),
                        "device": device_list
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = super().getMidilist(midi_track, position)
        self_midilist[0]["event"]       = "ProgramChange"
        self_midilist[0]["program"]     = Element.midi_128(self._program % int())
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["program"] = self.serialize( self._program )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "program" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._program = self.deserialize( serialization["parameters"]["program"] )
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
                self._program << operand._program
            case ou.Program() | int() | float() | str():
                self._program << operand
            case _: super().__lshift__(operand)
        return self

    def __add__(self, operand: o.Operand) -> 'ProgramChange':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Program() | int() | float() | ou.Program() | Fraction():
                return self.copy() << od.DataSource( self._program + operand )   # Specific parameter
            case _:
                return super().__add__(operand)

    def __sub__(self, operand: o.Operand) -> 'ProgramChange':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Program() | int() | float() | ou.Program() | Fraction():
                return self.copy() << od.DataSource( self._program - operand )   # Specific parameter
            case _:
                return super().__sub__(operand)

class Panic(Element):
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist = []
        self_playlist.extend((ControlChange(123) << ou.Value(0)).getPlaylist(position))
        self_playlist.extend(PitchBend(0).getPlaylist(position))
        self_playlist.extend((ControlChange(64) << ou.Value(0)).getPlaylist(position))
        self_playlist.extend((ControlChange(1) << ou.Value(0)).getPlaylist(position))
        self_playlist.extend((ControlChange(121) << ou.Value(0)).getPlaylist(position))

        channel_int: int            = self._channel % od.DataSource( int() )
        device_list: list           = self._device % od.DataSource( list() )
        on_time_ms = self.get_time_ms(self._position.getMillis_rational())
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

        self_playlist.extend((ControlChange(7) << ou.Value(100)).getPlaylist(position))
        self_playlist.extend((ControlChange(11) << ou.Value(127)).getPlaylist(position))

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
# Bend Bend                    Ex      MSB                 LSB

# System Real-Time Message         Status Byte 
# ------------------------         -----------
# Timing Clock                         F8
# Start Sequence                       FA
# Continue Sequence                    FB
# Stop Sequence                        FC
# Active Sensing                       FE
# System Reset                         FF
