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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from operand_staff import global_staff
# Example using typing.Union (compatible with Python < 3.10)
from typing import Union
import enum
# Json Midi Creator Libraries
from operand import *
from operand_unit import *
from operand_value import *
from operand_generic import *
from operand_setup import *
from operand_container import MultiElements

"""
    Operators logic:
        +	__add__(self, other)
            slide to right by time_length of the Position given
            increases the time_length by the the Length given
            

        –	__sub__(self, other)
            slide to left time_length of the Position given
            increases the time_length by the the Length given
        

        >>	__mod__(self, other)
            gets the respective time_length data if any Length() is given
            gets the respective position data if any Position is given

        <<	__lshift__(self, other)
            sets the position by the Position given
            sets the time_length by the Length given

        |	__or__(self, other)
            Stacks position of second element on the first

        
"""

class Element(Operand):
    def __init__(self):
        self._position: Position    = Position()
        self._time_length: TimeLength        = TimeLength()
        self._channel: Channel      = Channel()
        self._device: Device        = Device()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Position():    return self._position
            case TimeLength():  return self._time_length
            case Channel():     return self._channel
            case Device():      return self._device
            case _:             return operand

    def getPlayList(self, position: Position = None) -> list:
        return []

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "position": self._position.getSerialization(),
            "time_length": self._time_length.getSerialization(),
            "channel": self._channel.getSerialization(),
            "device": self._device.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "position" in serialization and "time_length" in serialization and
            "channel" in serialization and "device" in serialization):

            self._position  = Position().loadSerialization(serialization["position"])
            self._time_length    = TimeLength().loadSerialization(serialization["time_length"])
            self._channel   = Channel().loadSerialization(serialization["channel"])
            self._device    = Device().loadSerialization(serialization["device"])
        return self
        
    def copy(self) -> 'Element':
        return self.__class__() << self._position.copy() << self._time_length.copy() << self._channel << self._device

    def play(self, verbose: bool = False) -> 'Element':
        jsonMidiPlay(self.getPlayList(), verbose)
        return self

    def __lshift__(self, operand: Operand) -> 'Element':
        match operand:
            case Position(): self._position = operand
            case TimeLength(): self._time_length = operand
            case Channel(): self._channel = operand
            case Device(): self._device = operand
        return self

    def __rshift__(self, element: 'Element') -> 'Element':
        return element.__rrshift__(self)

    def __rrshift__(self, element_operand: Union['Element', Operand]) -> Union['Element', Operand]:
        match element_operand:
            case Null():
                pass
            case MultiElements():
                last_element = element_operand.lastElement()
                if type(last_element) != Null:
                    self << last_element % Position() + last_element % TimeLength()
            case Element(): self << element_operand % Position() + element_operand % TimeLength()
            case Position(): self << element_operand
            case TimeLength(): self += Position() << element_operand
        return self

    def __add__(self, operand: Operand) -> 'Element':
        match operand:
            case Element():
                return MultiElements(self.copy(), operand.copy())
            case MultiElements():
                return MultiElements(self.copy(), operand.copy() % list())
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
        from operand_staff import global_staff
        super().__init__()
        self._time_length = TimeLength() << Measure(global_staff % Measure() % int())
        self._mode: ClockModes = ClockModes.single
        self._pulses_per_quarternote: int = 24

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ClockModes():  return self._mode
            case int():         return self._pulses_per_quarternote
            case _:             return super().__mod__(operand)

    def getPlayList(self, position: Position = None):
        from operand_staff import global_staff
        
        clock_position: Position = self % Position() + Position() if position is None else position
        clock_length = TimeLength() << Measure(global_staff % Measure() % int()) \
                if self._time_length is None else self._time_length
        clock_mode = ClockModes.single if self._mode is None else self._mode
        if clock_mode == ClockModes.single:
            clock_position = Position()
            clock_length = TimeLength() << Measure(global_staff % Measure() % int())
        device = self % Device()

        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note * (global_staff % BeatNoteValue() % float())
        pulses_per_measure = pulses_per_beat * (global_staff % BeatsPerMeasure() % float())
        clock_pulses = round(pulses_per_measure * (clock_length % Measure() % float()))

        single_measure_ms = Measure(1).getTime_ms()
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
                                     * (clock_length % Measure() % int()) * clock_pulse / clock_pulses, 3),
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
        if operand.__class__ == Position: self._position = Position() << Measure(operand % Measure() % int())
        if operand.__class__ == TimeLength: self._time_length = TimeLength() << Measure(operand % Measure() % int())
        if operand.__class__ == ClockModes: self._mode = operand
        if operand.__class__ == int: self._pulses_per_quarternote = operand
        return self

class Note(Element):
    def __init__(self):
        super().__init__()
        self._duration: Duration    = Duration()
        self._key_note: KeyNote     = KeyNote()
        self._velocity: Velocity    = Velocity()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Duration():    return self._duration
            case KeyNote():     return self._key_note
            case Velocity():    return self._velocity
            case _:             return super().__mod__(operand)

    def getPlayList(self, position: Position = None):
        
        note_position: Position = self % Position() + Position() if position is None else position
        duration: Duration      = self % Duration()
        key_note_midi: KeyNote  = (self % KeyNote()).getMidi__key_note()
        velocity_int: Velocity  = self % Velocity() % int()
        channel_int: Channel    = self % Channel() % int()
        device_list: Device     = self % Device() % list()

        on_time_ms = note_position.getTime_ms()
        off_time_ms = on_time_ms + duration.getTime_ms()
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
        element_serialization["velocity"] = self._velocity.getSerialization()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "duration" in serialization and "key_note" in serialization and
            "velocity" in serialization):

            super().loadSerialization(serialization)
            self._duration = Duration().loadSerialization(serialization["duration"])
            self._key_note = KeyNote().loadSerialization(serialization["key_note"])
            self._velocity = Velocity().loadSerialization(serialization["velocity"])
        return self
      
    def copy(self) -> 'Note':
        return super().copy() << self._duration.copy() << self._key_note.copy() << self._velocity

    def __lshift__(self, operand: Operand) -> 'Note':
        if operand.__class__ == Duration: self._duration = operand
        if operand.__class__ == KeyNote: self._key_note = operand
        if operand.__class__ == Velocity: self._velocity = operand
        return super().__lshift__(operand)

    def __mul__(self, operand: Operand) -> MultiElements | Element:
        match operand:
            case int():
                multi_notes = []
                for _ in range(0, operand):
                    multi_notes.append(self.copy())
                return MultiElements(multi_notes)
        return super().__mul__(self)

class ControlChange(Element):
    def __init__(self):
        super().__init__()
        self._number: Number = Number()
        self._value_unit: ValueUnit = ValueUnit()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Number():      return self._number
            case ValueUnit():   return self._value_unit
            case _:             return super().__mod__(operand)

    def getPlayList(self, position: Position = None):
        
        note_position: Position = self % Position() + Position() if position is None else position
        number_int: Number      = self % Number() % int()
        value_int: ValueUnit    = self % ValueUnit() % int()
        channel_int: Channel    = self % Channel() % int()
        device_list: Device     = self % Device() % list()

        on_time_ms = note_position.getTime_ms()
        return [
                {
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & (channel_int - 1),
                        "data_byte_1": number_int,
                        "data_byte_2": value_int,
                        "device": device_list
                    }
                }
            ]
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        element_serialization["number"] = self._number % int()
        element_serialization["value_unit"] = self._value_unit % int()
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "number" in serialization and "value_unit" in serialization):

            super().loadSerialization(serialization)
            self._number = Number(serialization["number"])
            self._value_unit = ValueUnit(serialization["value_unit"])
        return self
      
    def copy(self) -> 'ControlChange':
        return super().copy() << self._number << self._value_unit

    def __lshift__(self, operand: Operand) -> 'ControlChange':
        match operand:
            case Number():
                self._number = operand
            case ValueUnit():
                self._value_unit = operand
        return super().__lshift__(operand)

    def __mul__(self, operand: Operand) -> MultiElements | Element:
        match operand:
            case int():
                multi_control_changes = []
                for _ in range(0, operand):
                    multi_control_changes.append(self.copy())
                return MultiElements(multi_control_changes)
        return super().__mul__(self)

class PitchBend(Element):
    def __init__(self):
        super().__init__()
        self._pitch: Pitch = Pitch()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Pitch():       return self._pitch
            case _:             return super().__mod__(operand)

    def getPlayList(self, position: Position = None):
        
        note_position: Position = self % Position() + Position() if position is None else position
        pitch_list: list[int]   = (self % Pitch()).getMidi__pitch_pair()
        channel_int: Channel    = self % Channel() % int()
        device_list: Device     = self % Device() % list()

        on_time_ms = note_position.getTime_ms()
        return [
                {
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0xE0 | 0x0F & (channel_int - 1),
                        "data_byte_1": pitch_list[0],
                        "data_byte_2": pitch_list[1],
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
            self._pitch = Pitch(serialization["pitch"])
        return self
      
    def copy(self) -> 'PitchBend':
        return super().copy() << self._pitch

    def __lshift__(self, operand: Operand) -> 'PitchBend':
        match operand:
            case Pitch():
                self._pitch = operand
        return super().__lshift__(operand)

    def __mul__(self, operand: Operand) -> MultiElements | Element:
        match operand:
            case int():
                multi_pitch_ends = []
                for _ in range(0, operand):
                    multi_pitch_ends.append(self.copy())
                return MultiElements(multi_pitch_ends)
        return super().__mul__(self)

class Sequence(Element):
    def __init__(self):
        super().__init__()
        self._time_length = TimeLength() << Measure(1)
        self._trigger_notes: MultiElements = MultiElements()

    def len(self) -> int:
        return self._trigger_notes.len()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case TimeLength():
                if self._time_length is None:
                    last_position: Position = self._trigger_notes.getLastPosition()
                    sequence_length: TimeLength = TimeLength(measures=1)
                    while last_position > sequence_length:
                        sequence_length += TimeLength(measures=1)
                    return sequence_length
                return self._time_length
            case MultiElements():   return self._trigger_notes
            case _:                 return super().__mod__(operand)

    def getPlayList(self, position: Position = None):
        
        sequence_position: Position = self % Position() + Position() if position is None else position
        sequence_length: TimeLength     = self % TimeLength()
        
        play_list = []
        for trigger_note in self._trigger_notes % list():

            if trigger_note % Position() < sequence_length:

                trigger_position    = sequence_position + trigger_note % Position()
                trigger_duration    = trigger_note % Duration()
                trigger_key_note    = trigger_note % KeyNote()
                trigger_velocity    = trigger_note % Velocity()
                trigger_channel     = trigger_note % Channel()
                trigger_device      = trigger_note % Device()

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
            self._trigger_notes = MultiElements().loadSerialization(serialization["trigger_notes"])

        return self
    
    def copy(self) -> 'Sequence':
        return super().copy() << self._trigger_notes.copy()

    def __lshift__(self, operand: Operand) -> 'Sequence':
        match operand:
            case Setup():
                match operand % Inner():
                    case Null():
                        return self
                    case _:
                        inner_operand = operand % Operand()
                        self._trigger_notes << inner_operand
                        return self
        match operand:
            case Position() | TimeLength():
                super().__lshift__(operand)
            case MultiElements():
                self._trigger_notes = operand
            case Operand():
                self._trigger_notes << operand
        return self

    def __add__(self, operand: Operand) -> 'Element':
        sequence_copy = self.copy()
        if isinstance(operand, Setup):
            if not isinstance(operand % Inner(), Null) and not isinstance(operand % Operand(), Null):
                sequence_copy << (self._trigger_notes + (operand % Operand())).copy()
        else:
            match operand:
                case Position() | TimeLength():
                    sequence_copy << sequence_copy % operand + operand
                case Operand():
                    sequence_copy << (self._trigger_notes + operand).copy()
        return sequence_copy

    def __sub__(self, operand: Operand) -> 'Element':
        sequence_copy = self.copy()
        if isinstance(operand, Setup):
            if not isinstance(operand % Inner(), Null) and not isinstance(operand % Operand(), Null):
                sequence_copy << (self._trigger_notes - (operand % Operand())).copy()
        else:
            match operand:
                case Position() | TimeLength():
                    sequence_copy << sequence_copy % operand - operand
                case Operand():
                    sequence_copy << (self._trigger_notes - operand).copy()
        return sequence_copy

    def __mul__(self, operand: Operand) -> 'Element':
        sequence_copy = self.copy()
        if isinstance(operand, Setup):
            if not isinstance(operand % Inner(), Null) and not isinstance(operand % Operand(), Null):
                sequence_copy << (self._trigger_notes * (operand % Operand())).copy()
        else:
            match operand:
                case Position() | TimeLength():
                    sequence_copy << sequence_copy % operand * operand
                case Operand():
                    sequence_copy << (self._trigger_notes * operand).copy()
        return sequence_copy

    def __truediv__(self, operand: Operand) -> 'Element':
        sequence_copy = self.copy()
        if isinstance(operand, Setup):
            if not isinstance(operand % Inner(), Null) and not isinstance(operand % Operand(), Null):
                sequence_copy << (self._trigger_notes / (operand % Operand())).copy()
        else:
            match operand:
                case Position() | TimeLength():
                    sequence_copy << sequence_copy % operand / operand
                case Operand():
                    sequence_copy << (self._trigger_notes / operand).copy()
        return sequence_copy

    def __floordiv__(self, time_length: TimeLength) -> 'Sequence':
        return self << self._trigger_notes // time_length
  

class Panic:
    ...

    # CHAINABLE OPERATIONS


class Chord:

    def __init__(self, root_note = 60, size = 3, scale = None):   # 0xF2 - Song Position
        self._root_note = root_note
        self._size = size
        self._scale = scale
        self._notes = []
        self._device: list = None

    # CHAINABLE OPERATIONS

class Arpeggio:
    ...

    # CHAINABLE OPERATIONS


class Loop:

    def __init__(self, element, repeat = 4):
        self._element = element
        self._repeat = repeat
        self._device: list = None
    
    # CHAINABLE OPERATIONS


class Stack:
    ...

    # CHAINABLE OPERATIONS

class Automation:
    ...

    # CHAINABLE OPERATIONS



class Retrigger:
    ...
    
    # CHAINABLE OPERATIONS


class Composition:

    def __init__(self, position: Position = Position(), time_length: TimeLength = TimeLength()):
        self._position: Position = position
        self._time_length: TimeLength = time_length
        self._placed_elements = []
        self._device: list = None

    def getData__device(self):
        return self._device

    def getPlayList(self, position: Position = None):
        
        position = Position() if position is None else position
        play_list = []
        for placed_element in self._placed_elements:
            play_list = play_list.extend(
                    placed_element["element"].getPlayList(
                        placed_element["position"] + (self._position + position)
                    )
                )
            
        if isinstance(self._device, list):
            for list_element in play_list:
                if "midi_message" in list_element:
                    if "device" not in list_element["midi_message"]:
                            list_element["midi_message"]["device"] = self._device

        return play_list

    # CHAINABLE OPERATIONS

    def setData__device(self, device: list = ["FLUID", "Midi", "Port", "Synth"]):
        self._device = device
        return self

    def placeElement(self, element, position = Position()):
        self._placed_elements.append({
                "element": element,
                "position": position
            })
        return self

    def takeElement(self, element, position = Position()):
        self._placed_elements.remove({
                "element": element,
                "position": position
            })
        return self
        
    def clear(self):
        self._placed_elements = []
        return self

    def displace(self, displacement = TimeLength()):
        ...
        return self

# Voice Message           Status Byte      Data Byte1          Data Byte2
# -------------           -----------   -----------------   -----------------
# Note off                      8x      Key number          Note Off velocity
# Note on                       9x      Key number          Note on velocity
# Polyphonic Key Pressure       Ax      Key number          Amount of pressure
# Control Change                Bx      Controller number   Controller value
# Program Change                Cx      Program number      None
# Channel Pressure              Dx      Pressure value      None            
# Pitch Bend                    Ex      MSB                 LSB

