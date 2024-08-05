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
from operand import *
from creator import *
import enum

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

class Element:

    def __init__(self):
        self._position: Position    = Position()
        self._time_length: TimeLength        = TimeLength()
        self._channel: Channel      = Channel()
        self._device: Device        = Device()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Position():    return self._position
            case TimeLength():      return self._time_length
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
            case MultiElements():
                last_element = element_operand.lastElement()
                if type(last_element) != Void:
                    self << last_element % Position() + last_element % TimeLength()
            case Element(): self << element_operand % Position() + element_operand % TimeLength()
            case Position(): self << element_operand
            case TimeLength(): self += Position() << element_operand
        return self

    def __add__(self, operand: Operand) -> 'Element':
        match operand:
            case Element():
                return MultiElements(self.copy, operand.copy())
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

class Void(Element):
    pass

class MultiElements():  # Just a container of Elements

    def __init__(self, *multi_elements: list[Element] | Element):
        self._multi_elements = []
        if multi_elements is not None:
            for single_element in multi_elements:
                if isinstance(single_element, Element):
                    self._multi_elements.append(single_element)
                elif isinstance(single_element, list) and all(isinstance(elem, Element) for elem in single_element):
                    self._multi_elements.extend(single_element)
        self._selection: Selection = None
        self._element_iterator = 0

    def len(self) -> int:
        return len(self._multi_elements)

    def __iter__(self):
        return self
    
    def __next__(self):
        if self._element_iterator < len(self._multi_elements):
            single_element = self._multi_elements[self._element_iterator]
            self._element_iterator += 1
            return single_element
        else:
            self._element_iterator = 0  # Reset to 0 when limit is reached
            raise StopIteration
        
    def getLastPosition(self) -> Position:
        last_position: Position = Position()
        for single_element in self._multi_elements:
            if single_element % Position() > last_position:
                last_position = single_element % Position()
        return last_position

    def __mod__(self, operand: list) -> list[Element]:
        if operand.__class__ == list:
            return self._multi_elements
        return []

    def firstElement(self) -> Element:
        if len(self._multi_elements) > 0:
            return self._multi_elements[0]
        return Void()

    def lastElement(self) -> Element:
        if len(self._multi_elements) > 0:
            return self._multi_elements[len(self._multi_elements) - 1]
        return Void()

    def getPlayList(self, position: Position = None):
        play_list = []
        for single_element in self % list():
            if isinstance(single_element, Element):
                play_list.extend(single_element.getPlayList(position))
        return play_list

    def getSerialization(self):
        multi_elements_serialization = []
        for single_element in self % list():
            multi_elements_serialization.append(single_element.getSerialization())
        return {
            "class": self.__class__.__name__,
            "multi_elements": multi_elements_serialization
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "multi_elements" in serialization):

            multi_elements = []
            multi_elements_serialization = serialization["multi_elements"]
            for single_element in multi_elements_serialization:
                class_name = single_element["class"]
                multi_elements.append(globals()[class_name]().loadSerialization(single_element))

            self._multi_elements = multi_elements
        return self
        
    def copy(self) -> 'MultiElements':
        multi_elements: list[Element] = []
        for single_element in self._multi_elements:
            multi_elements.append(single_element.copy())
        return MultiElements(multi_elements)

    def play(self, verbose: bool = False) -> 'MultiElements':
        jsonMidiPlay(self.getPlayList(), verbose)
        return self

    def __lshift__(self, operand: list[Element] | Operand) -> 'MultiElements':
        match operand:
            case list():
                self._multi_elements = operand
            case MultiElements():
                self._multi_elements = operand % list()
            case Operand():
                for single_element in self._multi_elements:
                    single_element << operand
        return self

    def __rshift__(self, multi_elements: 'MultiElements') -> 'MultiElements':
        return multi_elements.__rrshift__(self)

    def __rrshift__(self, other_operand: Union['MultiElements', 'Element', Operand]) -> Union['MultiElements', 'Element', Operand]:
        self_first_element = self.firstElement()
        if type(self_first_element) != Void:
            match other_operand:
                case MultiElements():
                    other_last_element = self.lastElement()
                    if type(other_last_element) != Void:
                        other_last_element >> self_first_element
                case Element(): other_operand % Position() + other_operand % TimeLength() >> self_first_element
                case Position() | TimeLength(): other_operand >> self_first_element
            for single_element_i in range(1, len(self._multi_elements)):
                self._multi_elements[single_element_i - 1] >> self._multi_elements[single_element_i]
        return self

    def __add__(self, operand: Union['MultiElements', Element, Operand, int]) -> 'MultiElements':
        match operand:
            case MultiElements():
                return MultiElements(self.copy() % list() + operand.copy() % list())
            case Element():
                return MultiElements(self.copy() % list() + [operand.copy()])
            case Operand():
                element_copy = self.copy()
                element_list = element_copy % list()
                for single_element in element_list:
                    single_element << single_element % operand + operand
                return element_copy
            case int(): # repeat n times the last argument if any
                element_copy = self.copy()
                element_list = element_copy % list()
                if len(self._multi_elements) > 0:
                    last_element = self._multi_elements[len(self._multi_elements) - 1]
                    while operand > 0:
                        element_list.append(last_element.copy)
                        operand -= 1
                return element_copy
        return self.copy()

    def __sub__(self, operand: Union['MultiElements', Element, Operand, int]) -> 'MultiElements':
        match operand:
            case MultiElements():
                return MultiElements(self % list() - operand % list()).copy()
            case Element():
                return MultiElements((self % list()) - [operand]).copy()
            case Operand():
                element_copy = self.copy()
                element_list = element_copy % list()
                for single_element in element_list:
                    single_element << single_element % operand - operand
                return element_copy
            case int(): # repeat n times the last argument if any
                element_copy = self.copy()
                element_list = element_copy % list()
                if len(self._multi_elements) > 0:
                    last_element = self._multi_elements[len(self._multi_elements) - 1]
                    while operand > 0 and len(element_list) > 0:
                        element_list.pop()
                        operand -= 1
                return element_copy
        return self.copy()

    # multiply with a scalar 
    def __mul__(self, operand: Union['MultiElements', Element, Operand, int]) -> 'MultiElements':
        match operand:
            case Operand():
                element_copy = self.copy()
                element_list = element_copy % list()
                for single_element in element_list:
                    single_element << single_element % operand * operand
                return element_copy
            case int(): # repeat n times the last argument if any
                multi_elements = MultiElements()    # empty list
                while operand > 0:
                    multi_elements += self
                    operand -= 1
                return multi_elements
        return self.copy()
    
    def __truediv__(self, operand: Union['MultiElements', Element, Operand, int]) -> 'MultiElements':
        match operand:
            case Operand():
                self_copy = self.copy()
                elements_list = self_copy % list()
                for single_element in elements_list:
                    single_element << single_element % operand / operand
                return self_copy
            case int(): # repeat n times the last argument if any
                if operand > 0:
                    self_copy = self.copy()
                    elements_list = self_copy % list()
                    elements_to_be_removed = round(1 - self_copy.len() / operand)
                    while elements_to_be_removed > 0:
                        elements_list.pop()
                        elements_to_be_removed -= 1
                return self_copy
        return self.copy()
    
    def __floordiv__(self, time_length: TimeLength) -> 'MultiElements':
        match time_length:
            case TimeLength():
                starting_position = None
                for single_element in self._multi_elements:
                    if starting_position is None:
                        starting_position = single_element % Position()
                    else:
                        starting_position += time_length
                        single_element << Position() << starting_position
        return self


class ClockModes(enum.Enum):
    single  = 1
    first   = 2
    middle  = 3
    last    = 4
    resume  = 5

class Clock(Element):

    def __init__(self):
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
        key_note_midi: KeyNote  = (self % KeyNote()).getValue__midi_key_note()
        velocity_int: Velocity  = self % Velocity() % int()
        channel_int: Channel    = self % Channel() % int()
        device_list: Device     = self % Device() % list()

        on_time_ms = note_position.getTime_ms()
        off_time_ms = on_time_ms + duration.getTime_ms()
        play_list = [
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

        return play_list
    
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
        super().__lshift__(operand)
        if operand.__class__ == Duration: self._duration = operand
        if operand.__class__ == KeyNote: self._key_note = operand
        if operand.__class__ == Velocity: self._velocity = operand
        return self

    def __mul__(self, operand: Operand) -> MultiElements | Element:
        match operand:
            case int():
                multi_notes = []
                for note_i in range(0, operand):
                    multi_notes.append(self.copy())
                return MultiElements(multi_notes)
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
                            "data_byte_1": trigger_key_note.getValue__midi_key_note(),
                            "data_byte_2": trigger_velocity % int(),
                            "device": trigger_device % list()
                        }
                    })
                
                off_time_ms = on_time_ms + trigger_duration.getTime_ms()
                play_list.append({
                        "time_ms": round(off_time_ms, 3),
                        "midi_message": {
                            "status_byte": 0x80 | 0x0F & (trigger_channel % int() - 1),
                            "data_byte_1": trigger_key_note.getValue__midi_key_note(),
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
  
    
class ControlChange:

    def __init__(self, channel = 1, control_change = 10, value = 64):    # default is 10 - pan
        pass

    # CHAINABLE OPERATIONS


class MidiMessage:

    def __init__(self, status_byte = 0xF2, data_byte_1 = 0, data_byte_2 = 0):   # 0xF2 - Song Position
        self._status_byte = status_byte
        self._data_byte_1 = data_byte_1
        self._data_byte_2 = data_byte_2
        self._device: list = None

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

