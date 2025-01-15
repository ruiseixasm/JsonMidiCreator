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
import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_label as ol
import operand_frame as of
import operand_generic as og
import operand_frame as of

TypeElement = TypeVar('TypeElement', bound='Element')  # TypeElement represents any subclass of Operand


if TYPE_CHECKING:
    from operand_container import Clip

class Element(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        self._position: ra.Position         = ra.Position()
        self._duration: Fraction            = og.defaults._duration
        self._stackable: bool               = True
        self._channel: int                  = og.defaults._channel
        self._device: list[str]             = og.defaults._device.copy()
        self._enabled: bool                 = True

        self._staff_reference: og.Staff     = og.defaults._staff

        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> 'Element':
        if isinstance(staff_reference, og.Staff):
            self._staff_reference = staff_reference
        return self

    def position(self: TypeElement, position: float = None) -> TypeElement:
        self._position = ra.Position(position)
        return self

    def duration(self: 'TypeElement', duration: float = None) -> 'TypeElement':
        self._duration = ra.Duration(duration)._rational
        return self

    def stackable(self: 'TypeElement', stackable: bool = None) -> 'TypeElement':
        self._stackable = stackable
        return self

    def channel(self: TypeElement, channel: int = None) -> TypeElement:
        self._channel = channel
        return self

    def device(self: 'TypeElement', device: list[str] = None) -> 'TypeElement':
        self._device = device
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
                match operand._data:
                    case ra.Position():     return self._position
                    case ra.Duration():     return operand._data << od.DataSource( self._duration )
                    case ou.Stackable():    return ou.Stackable() << od.DataSource( self._stackable )
                    case ou.Channel():      return ou.Channel() << od.DataSource( self._channel )
                    case od.Device():       return od.Device() << od.DataSource( self._device )
                    case Element():         return self
                    case ou.Enable():       return ou.Enable(self._enabled)
                    case ou.Disable():      return ou.Disable(not self._enabled)
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % (operand._data)
            case ra.Duration():     return operand.copy() << od.DataSource( self._duration )
            case ra.Length():       return ra.Length(self._position)
            case ra.Position():     return self._position.copy()
            case ra.TimeValue() | ou.TimeUnit() \
                | og.TimeSignature() | ra.BeatsPerMeasure() | ra.BeatNoteValue() | ra.NotesPerMeasure() \
                | ra.Tempo() | ra.Quantization():
                                    return self._position % operand
            case ou.Stackable():    return ou.Stackable() << od.DataSource( self._stackable )
            case ou.Channel():      return ou.Channel() << od.DataSource( self._channel )
            case od.Device():       return od.Device() << od.DataSource( self._device )
            case Element():         return self.copy()
            case od.Start():        return self.start()
            case od.End():          return self.finish()
            case int():             return self._position % operand
            case float():           return float( self._duration )
            case ou.Enable():       return ou.Enable(self._enabled)
            case ou.Disable():      return ou.Disable(not self._enabled)
            case _:                 return super().__mod__(operand)

    def eq_time(self, other: 'Element') -> bool:
        return  self._position      == other._position \
            and self._duration      == other._duration \
            and self._stackable     == other._stackable

    def eq_midi(self, other: 'Element') -> bool:
        return  self._channel       == other._channel \
            and self._device        == other._device

    def __eq__(self, other: 'o.Operand') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Element():
                return self.eq_time(other) and self.eq_midi(other)
            case ra.Duration():
                return self._duration == other._rational
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
            case Element():
                return  False
            case ra.Duration():
                return self._duration < other._rational
            case ra.TimeValue() | ou.TimeUnit():
                return self._position < other
            case _:
                return self % od.DataSource( other ) < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case Element():
                return  False
            case ra.Duration():
                return self._duration > other._rational
            case ra.TimeValue() | ou.TimeUnit():
                return self._position > other
            case _:
                return self % od.DataSource( other ) > other
    
    def start(self) -> ra.Position:
        return self._position.copy()

    def finish(self) -> ra.Position:
        return self._position + self % ra.Duration()

    def getPlaylist(self, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)
        return [
                {
                    "time_ms":  self.get_time_ms(self_position_ms)
                }
            ]

    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        midi_track: ou.MidiTrack = ou.MidiTrack() if not isinstance(midi_track, ou.MidiTrack) else midi_track

        if isinstance(position, ra.Position):
            self_numerator: int = position._time_signature._top
            self_denominator: int = position._time_signature._bottom
            self_position: float = (position.getBeats() + position.getBeats(self._position)) % od.DataSource( float() )
            self_duration: float = position.getBeats(self // ra.Duration()) % od.DataSource( float() )
            self_tempo: float = float(position._tempo)
        else:
            self_numerator: int = self._position._time_signature._top
            self_denominator: int = self._position._time_signature._bottom
            self_position: float = self._position % od.DataSource( float() )
            self_duration: float = self._position.getBeats(self // ra.Duration()) % od.DataSource( float() )
            self_tempo: float = float(self._position._tempo)

        # Validation is done by midiutil Midi Range Validation
        return [
                {
                    "event":        "Element",
                    "track":        midi_track % int() - 1,  # out of range shouldn't be exported as a midi track
                    "track_name":   midi_track % str(),
                    "numerator":    self_numerator,
                    "denominator":  self_denominator,
                    "channel":      self._channel - 1,
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
        serialization["parameters"]["enabled"]      = self.serialize(self._enabled)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Element':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "duration" in serialization["parameters"] and
            "stackable" in serialization["parameters"] and "channel" in serialization["parameters"] and "device" in serialization["parameters"] and
            "enabled" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position      = self.deserialize(serialization["parameters"]["position"])
            self._duration      = self.deserialize(serialization["parameters"]["duration"])
            self._stackable     = self.deserialize(serialization["parameters"]["stackable"])
            self._channel       = self.deserialize(serialization["parameters"]["channel"])
            self._device        = self.deserialize(serialization["parameters"]["device"])
            self._enabled       = self.deserialize(serialization["parameters"]["enabled"])

        return self

    def __lshift__(self, operand: o.Operand) -> 'Element':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():

                super().__lshift__(operand)
                self._position      << operand._position
                self._duration      = operand._duration
                self._stackable     = operand._stackable
                self._channel       = operand._channel
                self._device        = operand._device   # It's a list of strings, but it won't be changed directly
                self._enabled       = operand._enabled

            case od.DataSource():
                match operand._data:
                    case ra.Position():     self._position  = operand._data
                    case ra.Duration():     self._duration  = operand._data._rational
                    case ou.Stackable():    self._stackable = operand._data // bool()
                    case ou.Channel():      self._channel   = operand._data._unit
                    case od.Device():       self._device    = operand._data._data
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Duration():
                self._duration      = operand._rational
            case Fraction():
                self._duration      = operand
            case float():
                self._duration      = ra.Duration(operand)._rational
            case ra.Position() | ra.TimeValue() | ou.TimeUnit() | int() \
                | og.TimeSignature() | ra.BeatsPerMeasure() | ra.BeatNoteValue() | ra.NotesPerMeasure() \
                | ra.Tempo() | ra.Quantization():
                self._position      << operand
            case ou.Stackable():
                self._stackable     = operand // bool()
            case ou.Channel():
                self._channel       = operand._unit
            case od.Device():
                self._device        = operand._data
            case ou.Enable():
                self._enabled       = operand._unit != 0
            case ou.Disable():
                self._enabled       = operand._unit == 0
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
            case Element() | oc.Clip():
                return operand + self >> od.Stack()
            case od.Serialization():
                return operand % od.DataSource() >> self
            case od.Playlist():
                return operand >> od.Playlist(self.getPlaylist())
            case _:
                return super().__rrshift__(operand)

    def __add__(self, operand: any) -> 'Element':
        self_copy: Element = self.copy()
        return self_copy.__iadd__(operand)

    def __iadd__(self, operand: any) -> 'Element':
        import operand_container as oc
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():
                new_sequence: oc.Clip = oc.Clip()
                elements_list: list[Element] = [self, operand.copy()]
                return new_sequence << od.DataSource( elements_list )
            case oc.Clip():
                self_sequence: oc.Clip = operand.empty_copy()
                self_sequence += self
                self_sequence += operand
                return self_sequence
            case ra.Position():
                self._position += operand  # Specific and compounded parameter
                return self
            case _:
                self_operand: any = self % operand
                self_operand += operand
                return self << self_operand

    def __sub__(self, operand: any) -> 'Element':
        self_copy: Element = self.copy()
        return self_copy.__isub__(operand)

    def __isub__(self, operand: any) -> 'Element':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ra.Position():
                self._position -= operand  # Specific and compounded parameter
                return self
            case _:
                self_operand: any = self % operand
                self_operand -= operand
                return self << self_operand

    def __mul__(self, operand: any) -> 'Element':
        self_copy: Element = self.copy()
        return self_copy.__imul__(operand)

    def __imul__(self, operand: any) -> Union['Element', 'Clip']:
        import operand_container as oc
        match operand:  # Allows Frame skipping to be applied to the elements' parameters!
            case int() | float():
                new_sequence: oc.Clip = oc.Clip()
                multiplier: int = int(operand)
                if multiplier > 0:
                    new_sequence._datasource_list.append(od.DataSource( self ))
                    for _ in range(multiplier - 1):
                        new_sequence._datasource_list.append(od.DataSource( self.copy() ))
                return new_sequence.stack()
            case ra.TimeValue() | ou.TimeUnit():
                self_repeating: int = 0
                if self._duration > 0:
                    operand_duration: Fraction = self._position.getDuration(operand)._rational
                    self_repeating: int = operand_duration // self._duration
                return self.__imul__(self_repeating)
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        self_operand: any = self % operand
        self_operand *= operand
        return self << self_operand

    def __truediv__(self, operand: any) -> 'Element':
        self_copy: Element = self.copy()
        return self_copy.__itruediv__(operand)

    def __itruediv__(self, operand: o.Operand) -> 'Element':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        if operand != 0:
            self_operand: any = self % operand
            self_operand /= operand
            return self << self_operand
        return self

    def get_position_duration_ms(self, position: ra.Position = None) -> tuple:

        if isinstance(position, ra.Position):
            reference_position: ra.Position = position
            self_position_ms: Fraction = \
                position.getMillis_rational() + self._position.getMillis_rational()
        else:
            reference_position: ra.Position = self._position
            self_position_ms: Fraction = self._position.getMillis_rational()

        self_duration_ms: Fraction = reference_position.getMillis_rational( ra.Duration(self._duration) )

        return self_position_ms, self_duration_ms

    @staticmethod
    def get_time_ms(rational: Fraction) -> float:
        # Validation is done by JsonMidiPlayer and midiutil Midi Range Validation
        return round(float(rational), 3)



class Clock(Element):
    def __init__(self, *parameters):
        super().__init__()
        self._duration = self._position.getDuration(og.defaults._staff._measures)._rational
        self._pulses_per_quarternote: int = 24
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def ppqn(self: 'Clock', ppqn: int = None) -> 'Clock':
        self._pulses_per_quarternote = ppqn
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
                match operand._data:
                    case ou.PPQN():         return ou.PPQN() << od.DataSource( self._pulses_per_quarternote )
                    case ra.Measures() | ou.Measure():
                                            return operand << self._duration
                    case _:                 return super().__mod__(operand)
            case ou.PPQN():         return ou.PPQN() << od.DataSource( self._pulses_per_quarternote )
            case ra.Measures() | ou.Measure():
                                    return operand.copy() << self._duration
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pulses_per_quarternote == other._pulses_per_quarternote
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        pulses_per_note: int = self._pulses_per_quarternote * 4
        pulses_per_beat: Fraction = (self._position % ra.BeatNoteValue() % od.DataSource( Fraction() )) * pulses_per_note
        total_clock_pulses: int = (self._position.getBeats( self // ra.Duration() ) * pulses_per_beat) % od.DataSource( int() )

        single_pulse_duration_ms: Fraction = self_duration_ms / total_clock_pulses

        # First quarter note pulse (total 1 in 24 pulses per quarter note)
        self_playlist = [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xFA,    # Start Track
                        "device": self._device
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
                        "device": self._device
                    }
                }
            )

        # Last quarter note pulse (45 pulses where this last one sets the stop)
        self_playlist.append(
            {
                "time_ms": self.get_time_ms(single_pulse_duration_ms * total_clock_pulses),
                "midi_message": {
                    "status_byte": 0xFC,    # Stop Track
                    "device": self._device
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
                self._pulses_per_quarternote = operand._pulses_per_quarternote
            case od.DataSource():
                match operand._data:
                    case ou.PPQN():         self._pulses_per_quarternote = operand._data._unit
                    case ra.Measures() | ou.Measure():
                                            self._duration = self._position.getDuration(operand._data)._rational
                    case _:                 super().__lshift__(operand)
            case ou.PPQN():         self._pulses_per_quarternote = operand._unit
            case ra.Measures() | ou.Measure():
                                    self._duration = self._position.getDuration(operand)._rational
            case _: super().__lshift__(operand)
        return self

class Rest(Element):

    def getPlaylist(self, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        # Midi validation is done in the JsonMidiPlayer program
        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0x00 | 0x0F & self._channel - 1,
                        "device": self._device
                    }
                },
                {
                    "time_ms": self.get_time_ms(self_position_ms + self_duration_ms),
                    "midi_message": {
                        "status_byte": 0x00 | 0x0F & self._channel - 1,
                        "device": self._device
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position)
        self_midilist[0]["event"]       = "Rest"
        return self_midilist


class Tiable(Element):
    def __init__(self, *parameters):
        self._velocity: int         = og.defaults._velocity
        self._gate: Fraction        = Fraction(1)
        self._tied: bool            = False
        super().__init__(*parameters)

    def velocity(self: 'Tiable', velocity: int = 100) -> 'Tiable':
        self._velocity = velocity
        return self

    def gate(self: 'Tiable', gate: float = None) -> 'Tiable':
        self._gate = ra.Gate(gate)._rational
        return self

    def tied(self: 'Tiable', tied: bool = True) -> 'Tiable':
        self._tied = tied
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand._data:
                    case ou.Velocity():     return ou.Velocity() << od.DataSource(self._velocity)
                    case ra.Gate():         return ra.Gate() << od.DataSource(self._gate)
                    case ou.Tied():         return ou.Tied() << od.DataSource( self._tied )
                    case _:                 return super().__mod__(operand)
            case ou.Velocity():     return ou.Velocity() << od.DataSource(self._velocity)
            case ra.Gate():         return ra.Gate() << od.DataSource(self._gate)
            case ou.Tied():         return ou.Tied() << od.DataSource( self._tied )
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._velocity  == other._velocity \
                    and self._gate      == other._gate \
                    and self._tied      == other._tied
            case _:
                return super().__eq__(other)
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "Tiable"
        self_midilist[0]["duration"]    = float(self._position.getBeats( self // ra.Duration() )._rational * self._gate)
        self_midilist[0]["velocity"]    = self._velocity
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["velocity"] = self.serialize( self._velocity )
        serialization["parameters"]["gate"]     = self.serialize( self._gate )
        serialization["parameters"]["tied"]     = self.serialize( self._tied )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Tiable':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "velocity" in serialization["parameters"] and "gate" in serialization["parameters"] and
            "tied" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._velocity  = self.deserialize( serialization["parameters"]["velocity"] )
            self._gate      = self.deserialize( serialization["parameters"]["gate"] )
            self._tied      = self.deserialize( serialization["parameters"]["tied"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Tiable':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Tiable():
                super().__lshift__(operand)
                self._velocity      = operand._velocity
                self._gate          = operand._gate
                self._tied          = operand._tied
            case od.DataSource():
                match operand._data:
                    case ou.Velocity():     self._velocity  = operand._data._unit
                    case ra.Gate():         self._gate      = operand._data._rational
                    case ou.Tied():         self._tied      = operand._data // bool()
                    case _:                 super().__lshift__(operand)
            case ou.DrumKit():      self << od.DataSource( ou.Channel(10) )
            case ou.Velocity():     self._velocity = operand._unit
            case ra.Gate():         self._gate = operand._rational
            case ou.Tied():         self._tied = operand // bool()
            case _:                 super().__lshift__(operand)
        return self


class Note(Tiable):
    def __init__(self, *parameters):
        self._pitch: og.Pitch       = og.Pitch()
        super().__init__(*parameters)


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> 'Note':
        super().set_staff_reference(staff_reference)
        self._pitch._staff_reference = self._staff_reference
        return self

    def pitch(self: 'Note', key: Optional[ou.Key] = None, octave: Optional[int] = None) -> 'Note':
        self._pitch = og.Pitch(key, octave)
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
                match operand._data:
                    case og.Pitch():        return self._pitch
                    case _:                 return super().__mod__(operand)
            case og.Pitch():        return self._pitch.copy()
            case int():             return self._pitch._degree
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() | ou.Tone() | ou.Semitone() \
                | str() | ou.Key() | ou.Octave() | ou.Natural() | ou.Degree() | og.Scale() | ou.Mode() | list():
                                    return self._pitch % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pitch     == other._pitch
            case int(): # int() for Note concerns Degree
                return self._pitch._degree == other
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)
        pitch_int: int = int(self._pitch % float())

        # Midi validation is done in the JsonMidiPlayer program
        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & self._channel - 1,
                        "data_byte_1": pitch_int,
                        "data_byte_2": self._velocity,
                        "device": self._device
                    }
                },
                {
                    "time_ms": self.get_time_ms(self_position_ms + self_duration_ms * self._gate),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & self._channel - 1,
                        "data_byte_1": pitch_int,
                        "data_byte_2": 0,
                        "device": self._device
                    }
                }
            ]

    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        
        pitch_int: int = int(self._pitch % float())

        self_midilist: list = super().getMidilist(midi_track, position)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "Note"
        self_midilist[0]["pitch"]       = pitch_int
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pitch"]    = self.serialize( self._pitch )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Note':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pitch" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pitch     = self.deserialize( serialization["parameters"]["pitch"] )
        return self
      
    def __lshift__(self, operand: o.Operand) -> 'Note':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Note():
                super().__lshift__(operand)
                self._pitch         << operand._pitch
            case od.DataSource():
                match operand._data:
                    case og.Pitch():        self._pitch     = operand._data
                    case _:                 super().__lshift__(operand)
            case ou.KeySignature() | ou.Major() | ou.Minor() | ou.Sharps() | ou.Flats() \
                | og.Pitch() | ou.Key() | ou.Octave() | ou.Tone() | ou.Semitone() \
                | ou.Natural() | ou.Degree() | og.Scale() | ou.Mode() | int() | str() | None:
                                    self._pitch << operand
            case ou.DrumKit():
                                    self << od.DataSource( ou.Channel(10) )
                                    self._pitch << operand
            case _:                 super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'Note':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                self._pitch += operand  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> 'Note':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                self._pitch -= operand  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)


class Cluster(Tiable):
    def __init__(self, *parameters):
        self._pitches: list[og.Pitch] = [og.Pitch(1), og.Pitch(3), og.Pitch(5)]
        super().__init__( *parameters )


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> 'Note':
        super().set_staff_reference(staff_reference)
        for single_pitch in self._pitches:
            single_pitch._staff_reference = self._staff_reference
        return self

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case od.DataSource():
                match operand._data:
                    case list():            return self._pitches
                    case _:                 return super().__mod__(operand)
            case list():            return self.get_chord_notes()
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
            case Cluster():
                super().__lshift__(operand)
                self._pitches  = self.deep_copy(operand % od.DataSource( list() ))
            case od.DataSource():
                match operand._data:
                    case list():                self._pitches = operand._data
                    case _:                     super().__lshift__(operand)
            case list():
                if len(operand) > 0 and all(isinstance(single_note, Note) for single_note in operand):
                    self._pitches = []
                    for single_note in operand:
                        self._pitches.append(single_note % og.Pitch())
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

    def __iadd__(self, operand: any) -> 'Cluster':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                for single_pitch in self._pitches:
                    single_pitch << od.DataSource( single_pitch + operand ) # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> 'Cluster':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                for single_pitch in self._pitches:
                    single_pitch << od.DataSource( single_pitch - operand ) # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)
    
class Dyad(Cluster):
    # In music, a dyad is a set of two notes or pitches.
    ...

class KeyScale(Note):
    def __init__(self, *parameters):
        super().__init__()
        self << self._position.getDuration(ra.Measures(1))  # By default a Scale and a Chord has one Measure duration
        self._scale: og.Scale  = og.Scale( og.defaults._staff._key_signature % list() ) # Sets the default Scale based on the Staff Key Signature
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
                match operand._data:
                    case og.Scale():        return self._scale
                    case list():            return self._scale % list()
                    case _:                 return super().__mod__(operand)
            case og.Scale():        return self._scale.copy()
            case ou.Mode():         return self._scale % operand
            case list():            return self.get_scale_notes()
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
                new_note: Note = Note(self)
                new_note._pitch += float(transposition) # Jumps by semitones (chromatic tones)
                scale_notes.append( new_note )
        else:   # Uses the staff keys straight away
            for degree_i in range(self._pitch._scale.keys()):
                new_note: Note = Note(self)
                new_note._pitch._degree += degree_i # Jumps by degrees (scale tones)
                scale_notes.append( new_note )
        return scale_notes
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist: list = []
        for single_note in self.get_scale_notes():
            self_playlist.extend(single_note.getPlaylist(position))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = []
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
                match operand._data:
                    case og.Scale():        self._scale = operand._data
                    case _:                 super().__lshift__(operand)
            case og.Scale() | list() | ou.Mode():   # It's the element scale that is set
                self._scale << operand
            case ou.KeySignature():
                super().__lshift__(operand)
                self._scale << operand % list()
            case _:
                super().__lshift__(operand)
        return self

class Chord(KeyScale):
    def __init__(self, *parameters):
        self._size: int             = 3
        self._inversion: int        = 0
        self._dominant: bool        = False
        self._diminished: bool      = False
        self._augmented: bool       = False
        self._sus2: bool            = False
        self._sus4: bool            = False
        super().__init__(*parameters)

    def size(self: 'Chord', size: int = 3) -> 'Chord':
        self._size = size
        return self

    def inversion(self: 'Chord', inversion: int = 1) -> 'Chord':
        self._inversion = inversion
        return self

    def dominant(self: 'Chord', dominant: bool = True) -> 'Chord':
        self._dominant = dominant
        return self

    def diminished(self: 'Chord', diminished: bool = True) -> 'Chord':
        self._diminished = diminished
        return self

    def augmented(self: 'Chord', augmented: bool = True) -> 'Chord':
        self._augmented = augmented
        return self

    def sus2(self: 'Chord', sus2: bool = True) -> 'Chord':
        self._sus2 = sus2
        return self

    def sus4(self: 'Chord', sus4: bool = True) -> 'Chord':
        self._sus4 = sus4
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
                match operand._data:
                    case ou.Size():         return ou.Size() << od.DataSource(self._size)
                    case ou.Inversion():    return ou.Inversion() << od.DataSource(self._inversion)
                    case ou.Dominant():     return ou.Dominant() << od.DataSource(self._dominant)
                    case ou.Diminished():   return ou.Diminished() << od.DataSource(self._diminished)
                    case ou.Augmented():    return ou.Augmented() << od.DataSource(self._augmented)
                    case ou.Sus2():         return ou.Sus2() << od.DataSource(self._sus2)
                    case ou.Sus4():         return ou.Sus4() << od.DataSource(self._sus4)
                    case _:                 return super().__mod__(operand)
            case ou.Size():         return ou.Size() << od.DataSource(self._size)
            case ou.Inversion():    return ou.Inversion() << od.DataSource(self._inversion)
            case ou.Dominant():     return ou.Dominant() << od.DataSource(self._dominant)
            case ou.Diminished():   return ou.Diminished() << od.DataSource(self._diminished)
            case ou.Augmented():    return ou.Augmented() << od.DataSource(self._augmented)
            case ou.Sus2():         return ou.Sus2() << od.DataSource(self._sus2)
            case ou.Sus4():         return ou.Sus4() << od.DataSource(self._sus4)
            case list():            return self.get_chord_notes()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._size          == other._size \
                    and self._inversion     == other._inversion \
                    and self._dominant      == other._dominant \
                    and self._diminished    == other._diminished \
                    and self._augmented     == other._augmented \
                    and self._sus2          == other._sus2 \
                    and self._sus4          == other._sus4
            case _:
                return super().__eq__(other)
    
    def get_chord_notes(self) -> list[Note]:
        chord_notes: list[Note] = []
        max_size = self._scale.keys()
        if max_size % 2 == 0:
            max_size //= 2
        max_size = min(self._size, max_size)
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
                new_note: Note = Note(self)
                new_note._pitch += float(transposition) # Jumps by semitones (chromatic tones)
                chord_notes.append( new_note )
        else:   # Uses the staff keys straight away
            # modulated_scale: og.Scale = og.defaults % og.Scale(self._mode) # already modulated
            for note_i in range(max_size):          # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...
                key_step: int = note_i * 2
                if key_step == 3:   # Third
                    if self._sus2:
                        key_step -= 1
                    if self._sus4:
                        key_step += 1   # cancels out if both sus2 and sus4 are set to true
                new_note: Note = Note(self)
                new_note._pitch._degree += key_step # Jumps by degrees (scale tones)
                chord_notes.append( new_note )

        # Where the inversions are done
        inversion = min(self._inversion, len(chord_notes) - 1)
        if inversion > 0:
            first_note = chord_notes[inversion]
            not_first_note = True
            while not_first_note:   # Try to implement while inversion > 0 here
                not_first_note = False
                for single_note in chord_notes:
                    if single_note._pitch < first_note._pitch:   # Critical operation
                        single_note << single_note % ou.Octave() + 1
                        if single_note % od.DataSource( int() ) < 128:
                            not_first_note = True # to result in another while loop
        return chord_notes
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist: list = []
        for single_note in self.get_chord_notes():
            self_playlist.extend(single_note.getPlaylist(position))    # extends the list with other list
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        self_midilist: list = []
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
                self._size          = operand._size
                self._inversion     = operand._inversion
                self._dominant      = operand._dominant
                self._diminished    = operand._diminished
                self._augmented     = operand._augmented
                self._sus2          = operand._sus2
                self._sus4          = operand._sus4
            case od.DataSource():
                match operand._data:
                    case ou.Size():                 self._size = operand._data._unit
                    case ou.Inversion():            self._inversion = operand._data._unit
                    case ou.Dominant():             self._dominant = operand._data // bool()
                    case ou.Diminished():           self._diminished = operand._data // bool()
                    case ou.Augmented():            self._augmented = operand._data // bool()
                    case ou.Sus2():                 self._sus2 = operand._data // bool()
                    case ou.Sus4():                 self._sus4 = operand._data // bool()
                    case _:                         super().__lshift__(operand)
            case ou.Size():                 self._size = operand._unit
            case ou.Inversion():            self._inversion = operand._unit
            case str():
                operand = operand.strip()
                # Set Chord root note
                self._pitch << operand
                # Set Chord size
                self._size = ou.Size(od.DataSource( self._size ), operand)._unit
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
                self._dominant = operand // bool()
            case ou.Diminished():
                if operand:
                    self.set_all()
                self._diminished = operand // bool()
            case ou.Augmented():
                if operand:
                    self.set_all()
                self._augmented = operand // bool()
            case ou.Sus2():
                if operand:
                    self.set_all()
                self._sus2 = operand // bool()
            case ou.Sus4():
                if operand:
                    self.set_all()
                self._sus4 = operand // bool()
            case _: super().__lshift__(operand)
        return self
    
    def set_all(self, data: any = False):    # mutual exclusive
        self._dominant      = ou.Dominant(od.DataSource( self._dominant ), data) // bool()
        self._diminished    = ou.Diminished(od.DataSource( self._diminished ), data) // bool()
        self._augmented     = ou.Augmented(od.DataSource( self._augmented ), data) // bool()
        self._sus2          = ou.Sus2(od.DataSource( self._sus2 ), data) // bool()
        self._sus4          = ou.Sus4(od.DataSource( self._sus4 ), data) // bool()

class Retrigger(Note):
    def __init__(self, *parameters):
        self._division: int     = 16
        self._swing: Fraction   = Fraction(0.5)
        super().__init__()
        self._duration  *= 2 # Equivalent to twice single note duration
        self._gate      = Fraction(0.5)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def division(self: 'Retrigger', division: int = 16) -> 'Retrigger':
        self._division = division
        return self

    def swing(self: 'Retrigger', swing: float = 0.5) -> 'Retrigger':
        self._swing = Fraction(swing)
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
                match operand._data:
                    case ou.Division():     return ou.Division() << od.DataSource(self._division)
                    case ra.Swing():        return ra.Swing() << od.DataSource(self._swing)
                    case _:                 return super().__mod__(operand)
            case ou.Division():     return ou.Division() << od.DataSource(self._division)
            case int():             return self._division
            case ra.Swing():        return ra.Swing() << od.DataSource(self._swing)
            # Returns the SYMBOLIC value of each note
            case ra.Duration():     return operand.copy() << od.DataSource( self._duration / 2 )
            case list():            return get_retrigger_notes()
            case _:                 return super().__mod__(operand)

    def get_retrigger_notes(self) -> list[Note]:
        retrigger_notes: list[Note] = []
        self_iteration: int = 0
        note_position: ra.Position = self._position.copy()
        single_note_duration: ra.Duration = ra.Duration( self._duration/(self._division) ) # Already 2x single note duration
        for _ in range(self._division):
            swing_ratio = self._swing
            if self_iteration % 2:
                swing_ratio = 1 - swing_ratio
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
        self_midilist: list = []
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
            case Retrigger():
                super().__lshift__(operand)
                self._division  = operand._division
                self._swing     = operand._swing
            case od.DataSource():
                match operand._data:
                    case ou.Division():             self._division = operand._data // int()
                    case ra.Swing():                self._swing = operand._data._rational
                    case _:                         super().__lshift__(operand)
            case int():
                if operand > 0:
                    self._division = operand
            case ou.Division():
                if operand > 0:
                    self._division = operand // int()
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ra.Duration():
                self._duration = operand._rational * 2  # Equivalent to two sized Notes
            case _:
                super().__lshift__(operand)
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
        self._division = 3
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
        self._swing: Fraction           = Fraction(0.5)
        self._elements: list[Element]   = [Note(ra.Gate(0.5)), Note(ra.Gate(0.5)), Note(ra.Gate(0.5))]
        super().__init__()
        self._duration  *= 2 # Equivalent to twice single note duration
        self.set_elements_duration()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def swing(self: 'Tuplet', swing: float = 0.5) -> 'Tuplet':
        self._swing = Fraction(swing)
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
                single_element << ra.Duration( elements_duration )

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
                match operand._data:
                    case ra.Swing():        return ra.Swing() << od.DataSource(self._swing)
                    case list():            return self._elements
                    case _:                 return super().__mod__(operand)
            case ra.Swing():        return ra.Swing() << od.DataSource(self._swing)
            case ou.Division():     return ou.Division() << len(self._elements)
            case int():             return len(self._elements)
            case ra.Duration():     return operand << od.DataSource( self._duration / 2 )
            case list():            return get_tuplet_elements()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._swing     == other._swing \
                    and self._elements  == other._elements
            case _:
                return super().__eq__(other)
    
    def get_tuplet_elements(self) -> list[Element]:
        tuplet_elements: list[Element] = []
        element_position: ra.Position = self % ra.Position()
        self_iteration: int = 0
        for single_element in self._elements:
            element_duration = single_element % od.DataSource( ra.Duration() )
            tuplet_elements.append(single_element.copy() << element_position)
            swing_ratio = self._swing
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
            case Tuplet():
                super().__lshift__(operand)
                self._swing     = operand._swing
                self._elements  = self.deep_copy(operand % od.DataSource( list() ))
            case od.DataSource():
                match operand._data:
                    case ra.Swing():            self._swing = operand._data._rational
                    case list():                self._elements = operand._data
                    case _:                     super().__lshift__(operand)
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ra.Duration():
                self._duration = operand._rational * 2  # Equivalent to two sized Notes
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
            case _:
                super().__lshift__(operand)
        return self

class Automation(Element):
    def __init__(self, *parameters):
        super().__init__(*parameters)   # (*parameters) is required by correct Step duration initiation relative to self._position
        # Requires self._position, so, it has to be defined after super() initiation
        self._duration = self._position._quantization   # Equivalent to one Step
        for single_parameter in parameters: # Faster than passing a tuple
            if isinstance(single_parameter, ra.Duration):   # Others already processed above
                self << single_parameter

class ControlChange(Automation):
    def __init__(self, *parameters):
        self._controller: og.Controller = og.defaults % og.Controller()
        super().__init__(*parameters)

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
                match operand._data:
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
        if not self._enabled:
            return []

        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        # Midi validation is done in the JsonMidiPlayer program
        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & self._channel - 1,
                        "data_byte_1": self._controller._number,
                        "data_byte_2": self._controller._value,
                        "device": self._device
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position)
        self_midilist[0]["event"]       = "ControllerEvent"
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["number"]      = self._controller._number
        self_midilist[0]["value"]       = self._controller._value
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
            case ControlChange():
                super().__lshift__(operand)
                self._controller << operand._controller
            case od.DataSource():
                match operand._data:
                    case og.Controller():       self._controller = operand._data
                    case _:                     super().__lshift__(operand)
            case og.Controller() | ou.Number() | ou.Value() | int() | float() | str():
                self._controller << operand
            case _: super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'ControlChange':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | float() | ou.Value():
                self._controller += operand  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> 'ControlChange':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int() | float() | ou.Value():
                self._controller -= operand  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)

class PitchBend(Automation):
    def __init__(self, *parameters):
        self._bend: int = 0
        super().__init__(*parameters)

    def bend(self: 'PitchBend', bend: int = 0) -> 'PitchBend':
        self._bend = bend
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
                match operand._data:
                    case ou.Bend():         return ou.Bend() << od.DataSource(self._bend)
                    case _:                 return super().__mod__(operand)
            case ou.Bend():         return ou.Bend() << od.DataSource(self._bend)
            case int():             return self._bend
            case float():           return float(self._bend)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._bend == other._bend
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        amount = 8192 + self._bend          # 2^14 = 16384, 16384 / 2 = 8192
        amount = max(min(amount, 16383), 0) # midi safe

        msb_midi: int = amount >> 7         # MSB - total of 14 bits, 7 for each side, 2^7 = 128
        lsb_midi: int = amount & 0x7F       # LSB - 0x7F = 127, 7 bits with 1s, 2^7 - 1
    
        # Midi validation is done in the JsonMidiPlayer program
        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xE0 | 0x0F & self._channel - 1,
                        "data_byte_1": lsb_midi,
                        "data_byte_2": msb_midi,
                        "device": self._device
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "PitchWheelEvent"
        self_midilist[0]["value"]       = self._bend
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
            case PitchBend():
                super().__lshift__(operand)
                self._bend = operand._bend
            case od.DataSource():
                match operand._data:
                    case ou.Bend():             self._bend = operand._data._unit
                    case _:                     super().__lshift__(operand)
            case ou.Bend():
                self._bend = operand._unit
            case int():
                self._bend = operand
            case float():
                self._bend = int(operand)
            case _:
                super().__lshift__(operand)
        return self

class Aftertouch(Automation):
    def __init__(self, *parameters):
        self._pressure: int = 0
        super().__init__(*parameters)

    def pressure(self: 'Aftertouch', pressure: int = 0) -> 'Aftertouch':
        self._pressure = pressure
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
                match operand._data:
                    case ou.Pressure():     return ou.Pressure() << od.DataSource(self._pressure)
                    case _:                 return super().__mod__(operand)
            case ou.Pressure():     return ou.Pressure() << od.DataSource(self._pressure)
            case int():             return self._pressure
            case float():           return float(self._pressure)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pressure == other._pressure
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        # Midi validation is done in the JsonMidiPlayer program
        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xD0 | 0x0F & self._channel - 1,
                        "data_byte": self._pressure,
                        "device": self._device
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "ChannelPressure"
        self_midilist[0]["pressure"]    = self._pressure
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
            case Aftertouch():
                super().__lshift__(operand)
                self._pressure = operand._pressure
            case od.DataSource():
                match operand._data:
                    case ou.Pressure():         self._pressure = operand._data // int()
                    case _:                     super().__lshift__(operand)
            case ou.Pressure():
                self._pressure = operand // int()
            case int():
                self._pressure = operand
            case float():
                self._pressure = int(operand)
            case _:
                super().__lshift__(operand)
        return self

class PolyAftertouch(Aftertouch):
    def __init__(self, *parameters):
        self._pitch: og.Pitch  = og.Pitch()
        super().__init__(*parameters)


    def set_staff_reference(self, staff_reference: 'og.Staff' = None) -> 'Note':
        super().set_staff_reference(staff_reference)
        self._pitch._staff_reference = self._staff_reference
        return self

    def pitch(self: 'PolyAftertouch', key: Optional[ou.Key] = ou.Key("C"), octave: Optional[int] = ou.Octave(4)) -> 'PolyAftertouch':
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
                match operand._data:
                    case og.Pitch():    return self._pitch
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
        if not self._enabled:
            return []

        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)
        pitch_int: int = int(self._pitch % float())

        # Midi validation is done in the JsonMidiPlayer program
        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xA0 | 0x0F & self._channel - 1,
                        "data_byte_1": pitch_int,
                        "data_byte_2": self._pressure,
                        "device": self._device
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
            case PolyAftertouch():
                super().__lshift__(operand)
                self._pitch << operand._pitch
            case od.DataSource():
                match operand._data:
                    case og.Pitch():          self._pitch = operand._data
                    case _:                     super().__lshift__(operand)
            case og.Pitch() | ou.Key() | ou.Octave() | ou.Flat() | ou.Sharp() | ou.Natural() | int() | float() | str():
                                self._pitch << operand
            case _:             super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'PolyAftertouch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                self._pitch += operand  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> 'PolyAftertouch':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | int() | float() | Fraction():
                self._pitch -= operand  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)

class ProgramChange(Automation):
    def __init__(self, *parameters):
        self._program: int = ou.Program("Piano")._unit
        super().__init__(*parameters)

    def program(self: 'ProgramChange', program: int | str = "Piano") -> 'ProgramChange':
        self._program = ou.Program(program)._unit
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
                match operand._data:
                    case ou.Program():      return ou.Program() << od.DataSource(self._program)
                    case _:                 return super().__mod__(operand)
            case ou.Program():      return ou.Program() << od.DataSource(self._program)
            case int():             return self._program
            case float():           return float(self._program)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._program == other._program
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_position_ms, self_duration_ms = self.get_position_duration_ms(position)

        # Midi validation is done in the JsonMidiPlayer program
        return [
                {
                    "time_ms": self.get_time_ms(self_position_ms),
                    "midi_message": {
                        "status_byte": 0xC0 | 0x0F & self._channel - 1,
                        "data_byte": self._program,
                        "device": self._device
                    }
                }
            ]
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position: ra.Position = None) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "ProgramChange"
        self_midilist[0]["program"]     = self._program
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
            case ProgramChange():
                super().__lshift__(operand)
                self._program = operand._program
            case od.DataSource():
                match operand._data:
                    case ou.Program():          self._program = operand._data._unit
                    case _:                     super().__lshift__(operand)
            case ou.Program():
                self._program = operand._unit
            case int():
                self._program = operand
            case float():
                self._program = int(operand)
            case str():
                self._program = ou.Program(self._program, operand)._unit
            case _:
                super().__lshift__(operand)
        return self

class Panic(Element):
    def getPlaylist(self, position: ra.Position = None) -> list:
        self_playlist: list = []
        self_playlist.extend((ControlChange(123) << ou.Value(0)).getPlaylist(position))
        self_playlist.extend(PitchBend(0).getPlaylist(position))
        self_playlist.extend((ControlChange(64) << ou.Value(0)).getPlaylist(position))
        self_playlist.extend((ControlChange(1) << ou.Value(0)).getPlaylist(position))
        self_playlist.extend((ControlChange(121) << ou.Value(0)).getPlaylist(position))

        on_time_ms = self.get_time_ms(self._position.getMillis_rational())

        # Midi validation is done in the JsonMidiPlayer program
        for key_note_midi in range(128):
            self_playlist.append(
                {   # Needs the Note On first in order to the following Note Off not be considered redundant
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & self._channel - 1,
                        "data_byte_1": key_note_midi,
                        "data_byte_2": 0,   # 0 means it will result in no sound
                        "device": self._device
                    }
                },
                {
                    "time_ms": on_time_ms,
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & self._channel - 1,
                        "data_byte_1": key_note_midi,
                        "data_byte_2": 0,
                        "device": self._device
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
