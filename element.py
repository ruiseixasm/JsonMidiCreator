from staff import *
from operand import *
import enum
# Example using typing.Union (compatible with Python < 3.10)
from typing import Union

"""
    Operators logic:
        +	__add__(self, other)
            slide to right by length of the Position given
            increases the length by the the Length given
            

        –	__sub__(self, other)
            slide to left length of the Position given
            increases the length by the the Length given
        

        >>	__mod__(self, other)
            gets the respective length data if any Length() is given
            gets the respective position data if any Position is given

        <<	__lshift__(self, other)
            sets the position by the Position given
            sets the length by the Length given

        |	__or__(self, other)
            Stacks position of second element on the first

        
"""

class Element:

    def __init__(self):
        self._position: Position    = Position()
        self._length: Length        = Length()
        self._channel: Channel      = Channel()
        self._device: Device        = Device()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Position():    return self._position
            case Length():      return self._length
            case Channel():     return self._channel
            case Device():      return self._device
            case _:             return operand

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "position": self._position.getSerialization(),
            "length": self._length.getSerialization(),
            "channel": self._channel.getSerialization(),
            "device": self._device.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "position" in serialization and "length" in serialization and
            "channel" in serialization and "device" in serialization):

            self._position  = Position().loadSerialization(serialization["position"])
            self._length    = Length().loadSerialization(serialization["length"])
            self._channel   = Channel().loadSerialization(serialization["channel"])
            self._device    = Device().loadSerialization(serialization["device"])
        return self
        
    def copy(self) -> 'Element':
        return self.__class__() << self._position.copy() << self._length.copy() << self._channel << self._device
    
    def __or__(self, other_element: 'Element') -> 'Element':
        return other_element << self % Position() + self % Length()

    def __lshift__(self, operand: Operand) -> 'Element':
        if operand.__class__ == Position: self._position = operand
        if operand.__class__ == Length: self._length = operand
        if operand.__class__ == Channel: self._channel = operand
        if operand.__class__ == Device: self._device = operand
        return self

    def __add__(self, operand: Operand) -> 'Element':
        element_copy = self.copy()
        return element_copy << element_copy % operand + operand

    def __sub__(self, operand: Operand) -> 'Element':
        element_copy = self.copy()
        return element_copy << element_copy % operand - operand

    # multiply with a scalar 
    def __mul__(self, scalar: float) -> 'Element':
        return self.__class__(
                position = self._position,
                length = None if self._length is None else self._length * scalar,
                channel = self._channel,
                device = self._device
            )
    
    # multiply with a scalar 
    def __rmul__(self, scalar: float) -> 'Element':
        return self * scalar
    
    def __div__(self, operand: Operand) -> 'Element':
        element_copy = self.copy()
        return element_copy << element_copy % operand / operand
    
class MultiElements():  # Just a container of Elements

    def __init__(self, *multi_elements: list[Element] | Element):
        self._multi_elements = []
        if multi_elements is not None:
            for single_element in multi_elements:
                if isinstance(single_element, Element):
                    self._multi_elements.append(single_element)
                elif isinstance(single_element, list) and all(isinstance(elem, Element) for elem in single_element):
                    self._multi_elements.extend(single_element)

    def getLastPosition(self) -> Position:
        last_position: Position = Position()
        for single_element in self._multi_elements:
            if single_element % Position() > last_position:
                last_position = single_element % Position()
        return last_position

    def __mod__(self, operand: list) -> list[Element]:
        return self._multi_elements

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

    def __lshift__(self, operand: list[Element]) -> 'MultiElements':
        self._multi_elements = operand
        return self

    def __add__(self, operand: Union['MultiElements', Element, Operand]) -> 'MultiElements':
        match operand:
            case MultiElements():
                return MultiElements(self % list() + operand % list()).copy()
            case Element():
                return MultiElements((self % list()) + [operand]).copy()
            case Operand():
                element_copy = self.copy()
                element_list = element_copy % list()
                for single_element in element_list:
                    single_element << single_element % operand + operand
                return element_copy << element_copy % operand + operand
        return self.copy()

    def __sub__(self, operand: Union['MultiElements', Element]) -> 'MultiElements':
        match operand:
            case MultiElements():
                return MultiElements(self % list() - operand % list()).copy()
            case Element():
                return MultiElements((self % list()) - [operand]).copy()
        return self.copy()

    # multiply with a scalar 
    def __mul__(self, scalar: float) -> 'Element':
        return self.__class__(
                position = self._position,
                length = None if self._length is None else self._length * scalar,
                channel = self._channel,
                device = self._device
            )
    
    # multiply with a scalar 
    def __rmul__(self, scalar: float) -> 'Element':
        return self * scalar
    
    # multiply with a scalar 
    def __div__(self, scalar: float) -> 'Element':
        if (scalar != 0):
            return self * (1/scalar)
        return self.copy()
    
class ClockModes(enum.Enum):
    single  = 1
    first   = 2
    middle  = 3
    last    = 4
    resume  = 5

class Clock(Element):

    def __init__(self):
        super().__init__()
        self._length = Length() << Measure(get_global_staff().getData__measures())
        self._mode: ClockModes = ClockModes.single
        self._pulses_per_quarternote = 24

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case ClockModes():  return self._mode
            case int():         return self._pulses_per_quarternote
            case _:             return super().__mod__(operand)

    def getPlayList(self, position: Position = None):
        
        staff = get_global_staff()
        clock_position: Position = self % Position() + Position() if position is None else position
        staff_length = Length() << Measure(staff.getData__measures())
        clock_mode = ClockModes.single if self._mode is None else self._mode
        clock_length = staff_length if clock_mode == ClockModes.single else self % Length()
        device = self % Device()

        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note / staff.getValue__beats_per_note()
        pulses_per_measure = pulses_per_beat * staff.getValue__beats_per_measure()
        clock_pulses = round(pulses_per_measure * clock_length % Measure() % float())

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
                                     * clock_length % Measure() % int() * clock_pulse / clock_pulses, 3),
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
        if operand.__class__ == Length: self._length = Length() << Measure(operand % Measure() % int())
        if operand.__class__ == ClockModes: self._mode = operand
        if operand.__class__ == int: self._pulses_per_quarternote = operand
        return self

class Note(Element):

    def __init__(self):
        super().__init__()
        self._duration: Duration    = Duration() << NoteValue(1/4)
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

class Sequence(Element):

    def __init__(self):
        super().__init__()
        self._length = Length() << Measure(1)
        self._trigger_notes: MultiElements = MultiElements()

    def __mod__(self, operand: Operand) -> Operand:
        if operand.__class__ == Length:
            if self._length is None:
                last_position: Position = self._trigger_notes.getLastPosition()
                sequence_length: Length = Length(measures=1)
                while last_position > sequence_length:
                    sequence_length += Length(measures=1)
                return sequence_length
            return self._length
        match operand:
            case Duration():    self._duration
            case KeyNote():     self._key_note
            case Velocity():    self._velocity
            case _:             return super().__mod__(operand)

    def getPlayList(self, position: Position = None):
        
        sequence_position: Position = self % Position() + Position() if position is None else position
        sequence_length: Length     = self % Length()
        
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
        super().__lshift__(operand)
        if operand.__class__ == MultiElements: self._trigger_notes = operand
        if operand.__class__ == Duration: self._duration = operand
        if operand.__class__ == KeyNote: self._key_note = operand
        if operand.__class__ == Velocity: self._velocity = operand
        return self

    def __add__(self, other_element: Element):

        return self

    def __mul__(self, n_times: int):
        actual_length = self._length
        n_times = round(n_times)
        new_length = actual_length * n_times

        in_range_trigger_notes = []
        out_range_trigger_notes = []

        for trigger_note in self._trigger_notes:
            for operand in trigger_note:
                if operand.__class__ == Position:
                    if operand.is_gt(actual_length):
                        out_range_trigger_notes.append(trigger_note)
                    else:
                        in_range_trigger_notes.append(trigger_note)

        # Better to develop new Sequence function to help on this one as delegation (self call)

        return self

    
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

    def __init__(self, root_note = 60, size = 3, scale = Scale()):   # 0xF2 - Song Position
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

    def __init__(self, position: Position = Position(), length: Length = Length()):
        self._position: Position = position
        self._length: Length = length
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

    def displace(self, displacement = Length()):
        ...
        return self

