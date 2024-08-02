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
        

        >>	__rshift__(self, other)
            gets the respective length data if any Length() is given
            gets the respective position data if any Position is given

        <<	__lshift__(self, other)
            sets the position by the Position given
            sets the length by the Length given

        |	__or__(self, other)
            Stacks position of second element on the first

        
"""

class Element:

    def __init__(self, position: Position = Position(0), length: Length = None,
                 channel: Channel = None, device: Device = None):
        self._position: Position = position
        self._length: Length = length
        self._channel: Channel = channel
        self._device: Device = device

    def __rshift__(self, operand: Operand) -> Operand:
        match operand:
            case Position():    return self._position
            case Length():      return self._length
            case Channel():     return self._channel
            case Device():      return self._device
            case _:             return operand

    def __pow__(self, operand: Operand) -> Operand:
        match operand:
            case Position():    return Position().getDefault() if self._position is None else self._position
            case Length():      return Length().getDefault() if self._length is None else self._length
            case Channel():     return Channel().getDefault() if self._channel is None else self._channel
            case Device():      return Device().getDefault() if self._device is None else self._device
            case _:             return operand

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "position": self._position.getSerialization(),
            "length": self._length.getSerialization(),
            "channel": self._channel.getSerialization(),
            "device": self._device
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "position" in serialization and "length" in serialization and
            "channel" in serialization and "device" in serialization):

            self._position  = Position().loadSerialization(serialization["position"])
            self._length    = Length().loadSerialization(serialization["length"])
            self._channel   = Channel().loadSerialization(serialization["channel"])
            self._device    = serialization["device"]
        return self
        
    def copy(self) -> 'Element':
        return self.__class__(
                position    = None if self._position is None else self._position.copy(),
                length      = None if self._length is None else self._length.copy(),
                channel     = None if self._channel is None else self._channel,     # Unit objects are const objects, read only
                device      = None if self._device is None else self._device        # Device are read only objects
            )
    
    def __or__(self, other_element: 'Element') -> 'Element':
        return other_element << self ** Position() + self ** Length()

    def __lshift__(self, operand: Operand) -> 'Element':
        operand_data = operand
        if operand.__class__ == Empty:
            operand = operand.getOperand()
            operand_data = None
        if operand.__class__ == Position: self._position = operand_data
        if operand.__class__ == Length: self._length = operand_data
        if operand.__class__ == Channel: self._channel = operand_data
        if operand.__class__ == Device: self._device = operand_data
        return self

    def __add__(self, operand: Operand) -> 'Element':
        element_copy = self.copy()
        return element_copy << element_copy ** operand + operand

    def __sub__(self, operand: Operand) -> 'Element':
        element_copy = self.copy()
        return element_copy << element_copy ** operand - operand

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
            if single_element ** Position() > last_position:
                last_position = single_element ** Position()
        return last_position

    def __rshift__(self, operand: list) -> list[Element]:
        return self._multi_elements

    def __pow__(self, operand: list) -> list[Element]:
        return self._multi_elements

    def getPlayList(self, position: Position = None):
        multi_elements = self ** list()
        play_list = []
        for single_element in multi_elements:
            if isinstance(single_element, Element):
                play_list.extend(single_element.getPlayList(position))
        return play_list

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "multi_elements": self._multi_elements
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "multi_elements" in serialization):

            self._multi_elements = serialization["multi_elements"]
        return self
        
    def copy(self) -> 'MultiElements':
        multi_elements: list[Element] = []
        for single_element in self._multi_elements:
            multi_elements.append(single_element.copy())
        return MultiElements(multi_elements)

    def __lshift__(self, operand: list[Element]) -> 'MultiElements':
        self._multi_elements = operand
        return self

    def __add__(self, operand: Union['MultiElements', Element]) -> 'MultiElements':
        match operand:
            case MultiElements():
                return MultiElements(self ** list() + operand ** list()).copy()
            case Element():
                return MultiElements((self ** list()) + [operand]).copy()
        return self.copy()

    def __sub__(self, operand: Union['MultiElements', Element]) -> 'MultiElements':
        match operand:
            case MultiElements():
                return MultiElements(self ** list() - operand ** list()).copy()
            case Element():
                return MultiElements((self ** list()) - [operand]).copy()
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

    def __init__(self, position: Position = Position(0), length: Length = None, mode: ClockModes = ClockModes.single,
                 device: Device = None, pulses_per_quarternote: int = 24):
        super().__init__(position, length, None, device)
        self._mode: ClockModes = mode
        self._pulses_per_quarternote = 24 if pulses_per_quarternote is None else pulses_per_quarternote

    def getData__mode(self):
        return self._mode

    def getData__pulses_per_quarternote(self):
        return self._pulses_per_quarternote

    def getPlayList(self, position: Position = None):
        
        staff = get_global_staff()
        clock_position: Position = self ** Position() + Position().getDefault() if position is None else position
        staff_length = Length(measures=get_global_staff().getData__measures())
        clock_mode = ClockModes.single if self._mode is None else self._mode
        clock_length = staff_length if clock_mode == ClockModes.single else self ** Length()
        device = self ** Device()

        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note / staff.getValue__beats_per_note()
        pulses_per_measure = pulses_per_beat * staff.getValue__beats_per_measure()
        clock_pulses = round(pulses_per_measure * clock_length.getData__measures())

        single_measure_ms = Length(measures=1).getTime_ms()
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
                        "device": device.getValue()
                    }
                }
            ]

        for clock_pulse in range(1, clock_pulses):
            play_list.append(
                {
                    "time_ms": round(clock_start_ms + single_measure_ms \
                                     * clock_length.getData__measures() * clock_pulse / clock_pulses, 3),
                    "midi_message": {
                        "status_byte": 0xF8,
                        "device": device.getValue()
                    }
                }
            )

        if clock_mode == ClockModes.single or clock_mode == ClockModes.last:
            play_list.append(
                {
                    "time_ms": round(clock_stop_ms, 3),
                    "midi_message": {
                        "status_byte": 0xFC,
                        "device": device.getValue()
                    }
                }
            )
        
        return play_list

    def getSerialization(self):
        element_serialization = super().getSerialization()
        return element_serialization + {
            "mode": self._mode,
            "pulses_per_quarternote": self._pulses_per_quarternote
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "mode" in serialization and "pulses_per_quarternote" in serialization):

            super().loadSerialization(serialization)
            self._mode = serialization["mode"]
            self._pulses_per_quarternote = serialization["pulses_per_quarternote"]
        return self
      
    def copy(self) -> 'Clock':
        return Clock(
                position    = None if self._position is None else self._position.copy(),
                length      = None if self._length is None else self._length.copy(),
                mode        = None if self._mode is None else self._mode,
                device      = None if self._device is None else self._device,       # Device are read only objects
                pulses_per_quarternote = None if self._pulses_per_quarternote is None else self._pulses_per_quarternote
            )

    def setData__mode(self, mode: ClockModes = ClockModes.single):
        self._mode = mode
        return self

    def setData__pulses_per_quarternote(self, pulses_per_quarternote: int = 24):
        self._pulses_per_quarternote = pulses_per_quarternote
        return self

class Note(Element):

    def __init__(self, position: Position = Position(0), length: Length = None,
                 duration: Duration = None, key_note: KeyNote = None, velocity: Velocity = None,
                 channel: Channel = None, device: Device = None):
        super().__init__(position, length, channel, device)
        self._duration: Duration = duration
        self._key_note: KeyNote = key_note
        self._velocity: Velocity = velocity

    def __rshift__(self, operand: Operand) -> Operand:
        match operand:
            case Duration():    return self._duration
            case KeyNote():     return self._key_note
            case Velocity():    return self._velocity
            case _:             return super().__rshift__(operand)

    def __pow__(self, operand: Operand) -> Operand:
        if operand.__class__ == Length: return (self ** Duration()).getLength() if self._length is None else self._length
        match operand:
            case Duration():    return Duration().getDefault() if self._duration is None else self._duration
            case KeyNote():     return KeyNote().getDefault() if self._key_note is None else self._key_note
            case Velocity():    return Velocity().getDefault() if self._velocity is None else self._velocity
            case _:             return super().__pow__(operand)

    def getPlayList(self, position: Position = None):
        
        note_position: Position = self ** Position() + Position().getDefault() if position is None else position
        duration_ms     = (self ** Duration()).getTime_ms()
        midi_key_note   = (self ** KeyNote()).getValue__midi_key_note()
        midi_velocity   = (self ** Velocity()).getData()
        midi_channel    = (self ** Channel()).getData()
        device_list     = (self ** Device()).getData()

        on_time_ms = note_position.getTime_ms()
        off_time_ms = on_time_ms + duration_ms
        play_list = [
                {
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & (midi_channel - 1),
                        "data_byte_1": midi_key_note,
                        "data_byte_2": midi_velocity,
                        "device": device_list
                    }
                },
                {
                    "time_ms": round(off_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & (midi_channel - 1),
                        "data_byte_1": midi_key_note,
                        "data_byte_2": 0,
                        "device": device_list
                    }
                }
            ]

        return play_list
    
    def getSerialization(self):
        element_serialization = super().getSerialization()
        return element_serialization + {
            "duration": self._duration.getSerialization(),
            "key_note": self._key_note.getSerialization(),
            "velocity": self._velocity.getSerialization()
        }

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
        note_copy: Note = super().copy()
        note_duration = Empty(Duration()) if self._duration is None else self._duration
        note_key_note = Empty(KeyNote()) if self._key_note is None else self._key_note
        note_velocity = Empty(Velocity()) if self._velocity is None else self._velocity
        return note_copy << note_duration << note_key_note << note_velocity

    def __lshift__(self, operand: Operand) -> 'Note':
        super().__lshift__(operand)
        operand_data = operand
        if operand.__class__ == Empty:
            operand = operand.getOperand()
            operand_data = None
        if operand.__class__ == Duration: self._duration = operand_data
        if operand.__class__ == KeyNote: self._key_note = operand_data
        if operand.__class__ == Velocity: self._velocity = operand_data
        return self

class Sequence(Element):

    def __init__(self, position: Position = Position(0), length: Length = None,
                 trigger_notes: MultiElements = None,
                 duration: Duration = None, key_note: KeyNote = None, velocity: Velocity = None,
                 channel: Channel = None, device: Device = None):
        super().__init__(position, length, channel, device)
        self._trigger_notes: MultiElements = trigger_notes
        self._duration: Duration = duration
        self._key_note: KeyNote = key_note
        self._velocity: Velocity = velocity

    def __rshift__(self, operand: Operand) -> Operand:
        match operand:
            case MultiElements():   return self._trigger_notes  # case [] | [Note(), *rest]:  # Match an empty list or a list with one or more Note instances
            case Duration():        return self._duration
            case KeyNote():         return self._key_note
            case Velocity():        return self._velocity
        return super().__rshift__(operand)

    def __pow__(self, operand: Operand) -> Operand:
        if operand.__class__ == Length:
            if self._length is None:
                last_position: Position = self._trigger_notes.getLastPosition()
                sequence_length: Length = Length(measures=1)
                while last_position > sequence_length:
                    sequence_length += Length(measures=1)
                return sequence_length
            return self._length
        match operand:
            case Duration():    return Duration().getDefault() if self._duration is None else self._duration
            case KeyNote():     return KeyNote().getDefault() if self._key_note is None else self._key_note
            case Velocity():    return Velocity().getDefault() if self._velocity is None else self._velocity
            case _:             return super().__pow__(operand)

    def getPlayList(self, position: Position = None):
        
        sequence_position: Position = self ** Position() + Position().getDefault() if position is None else position
        sequence_length: Length     = self ** Length()
        sequence_duration: Duration = self ** Duration()
        sequence_key_note: KeyNote  = self ** KeyNote()
        sequence_velocity_value     = (self ** Velocity()).getData()
        sequence_channel_value      = (self ** Channel()).getData()
        sequence_device_value       = (self ** Device()).getData()
        
        play_list = []
        for trigger_note in self._trigger_notes ** list():

            if trigger_note ** Position() < sequence_length:

                trigger_position: Position = sequence_position + trigger_note ** Position()
                trigger_duration = sequence_duration if trigger_note >> Duration() is None else trigger_note >> Duration()
                trigger_key_note = sequence_key_note if trigger_note >> KeyNote() is None else trigger_note >> KeyNote()
                trigger_velocity_value = sequence_velocity_value if trigger_note >> Velocity() is None else (trigger_note >> Velocity()).getValue()
                trigger_channel_value = sequence_channel_value if trigger_note >> Channel() is None else (trigger_note >> Channel()).getValue()
                trigger_device_value = sequence_device_value if trigger_note >> Device() is None else (trigger_note >> Device()).getValue()

                start_time_ms = sequence_position.getTime_ms()
                on_time_ms = start_time_ms + trigger_position.getTime_ms()
                play_list.append({
                        "time_ms": round(on_time_ms, 3),
                        "midi_message": {
                            "status_byte": 0x90 | 0x0F & (trigger_channel_value - 1),
                            "data_byte_1": trigger_key_note.getValue__midi_key_note(),
                            "data_byte_2": trigger_velocity_value,
                            "device": trigger_device_value
                        }
                    })
                
                off_time_ms = on_time_ms + trigger_duration.getTime_ms()
                play_list.append({
                        "time_ms": round(off_time_ms, 3),
                        "midi_message": {
                            "status_byte": 0x80 | 0x0F & (trigger_channel_value - 1),
                            "data_byte_1": trigger_key_note.getValue__midi_key_note(),
                            "data_byte_2": 0,
                            "device": trigger_device_value
                        }
                    })

        return play_list
    
    def getSerialization(self):
        trigger_notes_serialization = []
        for trigger_note in self._trigger_notes:
            trigger_notes_serialization.append(trigger_note.getSerialization())

        element_serialization = super().getSerialization()
        return element_serialization + {
            "trigger_notes": None if self._trigger_notes is None else self._trigger_notes.getSerialization(),
            "duration": None if self._duration is None else self._duration.getSerialization(),
            "key_note": None if self._key_note is None else self._key_note.getSerialization(),
            "velocity": None if self._velocity is None else self._velocity.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "trigger_notes" in serialization and "duration" in serialization and
            "key_note" in serialization and "velocity" in serialization):

            super().loadSerialization(serialization)
            self._trigger_notes = MultiElements().loadSerialization(serialization["trigger_notes"])
            self._duration = Duration().loadSerialization(serialization["duration"])
            self._key_note = KeyNote().loadSerialization(serialization["key_note"])
            self._velocity = Velocity().loadSerialization(serialization["velocity"])

        return self
    
    def copy(self) -> 'Sequence':
        trigger_notes   = Empty(MultiElements()) if self._trigger_notes is None else self._trigger_notes.copy()
        duration        = Empty(Duration()) if self._duration is None else self._duration.copy()
        key_note        = Empty(KeyNote()) if self._key_note is None else self._key_note.copy()
        velocity        = Empty(Velocity()) if self._velocity is None else self._velocity
        return super().copy() << trigger_notes << duration << key_note << velocity

    def __lshift__(self, operand: Operand) -> 'Sequence':
        super().__lshift__(operand)
        operand_data = operand
        if operand.__class__ == Empty:
            operand = operand.getOperand()
            operand_data = None
        if operand.__class__ == MultiElements: self._trigger_notes = operand_data
        if operand.__class__ == Duration: self._duration = operand_data
        if operand.__class__ == KeyNote: self._key_note = operand_data
        if operand.__class__ == Velocity: self._velocity = operand_data
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

    def __init__(self, position: Position = Position(0), length: Length = Length(measures=4)):
        self._position: Position = position
        self._length: Length = length
        self._placed_elements = []
        self._device: list = None

    def getData__device(self):
        return self._device

    def getPlayList(self, position: Position = None):
        
        position = Position(0) if position is None else position
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

