from staff import *
from operand import *
import enum

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
                 channel: int = None, device: Device = None):
        self._position: Position = position
        self._length: Length = length
        self._channel: Channel = channel
        self._device: Device = device

    def __rshift__(self, operand):
        match operand:
            case Position():    return self._position
            case Length():      return self._length
            case Channel():     return self._channel
            case Device():      return self._device
            case _:             return Empty()

    def getValue__position(self) -> Position:
        if self._position is None:
            return Position()
        return self._position
    
    def getValue__length(self) -> Length:
        if self._length is None:
            return Length()
        return self._length
    
    def getValue__channel(self) -> Channel:
        if self._channel is None:
            return Channel().getDefault()
        return self._channel

    def getValue__device(self) -> Device:
        if self._device is None:
            return Device().getDefault()
        return self._device

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

            self._position      = Position().loadSerialization(serialization["position"])
            self._length        = Length().loadSerialization(serialization["length"])
            self._channel       = Channel().loadSerialization(serialization["channel"])
            self._device   = serialization["device"]
        return self
        
    def copy(self) -> 'Element':
        return self.__class__(
                position    = None if self._position is None else self._position.copy(),
                length      = None if self._length is None else self._length.copy(),
                channel     = None if self._channel is None else self._channel.getData(),   # Unit objects are const objects, read only
                device      = None if self._device is None else self._device.getData()      # Device are read only objects
            )

    def __lshift__(self, operand):
        if operand.__class__ == Empty:
            operand = operand.getOperand()
            operand_data = None
        else:
            operand_data = operand
        match operand:
            case Position():    self._position  = operand_data
            case Length():      self._length    = operand_data
            case Channel():     self._channel   = operand_data
            case Device():      self._device    = operand_data
        return self

    def __add__(self, other_element: 'Element') -> 'Element':
        return self.__class__(
                position = self._position,
                length = None if self._length is None or other_element >> Length() is None
                    else self._length + other_element >> Length(),
                channel = self._channel,
                device = self._device
            )
    
    def __sub__(self, other_element: 'Element') -> 'Element':
        return self.__class__(
                position = self._position,
                length = None if self._length is None or other_element >> Length() is None
                    else self._length - other_element >> Length(),
                channel = self._channel,
                device = self._device
            )

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
        clock_position: Position = self.getValue__position() + Position() if position is None else position
        staff_length = Length(measures=get_global_staff().getData__measures())
        clock_mode = ClockModes.single if self._mode is None else self._mode
        clock_length = staff_length if clock_mode == ClockModes.single else self.getValue__length()
        device = self.getValue__device()

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
        element_copy: Clock = super().copy()
        return element_copy.setData__mode(self._mode).setData__pulses_per_quarternote(self._pulses_per_quarternote)

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

    def __rshift__(self, operand):
        match operand:
            case Duration():    return self._duration
            case KeyNote():     return self._key_note
            case Velocity():    return self._velocity
            case _:             return super().__rshift__(operand)

    def getValue__length(self) -> Length:
        if self._length is None:
            return self.getValue__duration().getLength()
        return self._length
    
    def getValue__duration(self) -> Duration:
        if self._duration is None:
            return Duration().getDefault()
        return self._duration

    def getValue__key_note(self) -> KeyNote:
        if self._key_note is None:
            return KeyNote().getDefault()
        return self._key_note

    def getValue__velocity(self) -> Velocity:
        if self._velocity is None:
            return Velocity().getDefault()
        return self._velocity

    def getPlayList(self, position: Position = None):
        
        note_position: Position = self.getValue__position() + Position() if position is None else position
        duration_ms = self.getValue__duration().getTime_ms()
        midi_key_note = self.getValue__key_note().getValue__midi_key_note()
        midi_velocity = self.getValue__velocity().getData()
        midi_channel = self.getValue__channel().getData()
        device_list = self.getValue__device().getData()

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
            self._duration = Duration.loadSerialization(serialization["duration"])
            self._key_note = KeyNote.loadSerialization(serialization["key_note"])
            self._velocity = Velocity.loadSerialization(serialization["velocity"])
        return self
      
    def copy(self) -> 'Note':
        note_copy: Note = super().copy()
        note_duration = Empty(Duration()) if self._duration is None else self._duration
        note_key_note = Empty(KeyNote()) if self._key_note is None else self._key_note
        note_velocity = Empty(Velocity()) if self._velocity is None else self._velocity
        return note_copy << note_duration << note_key_note << note_velocity

    def __lshift__(self, operand):
        super().__lshift__(operand)
        if operand.__class__ == Empty:
            operand = operand.getOperand()
            operand_data = None
        else:
            operand_data = operand
        match operand:
            case Duration():    self._duration = operand_data
            case KeyNote():     self._key_note = operand_data
            case Velocity():    self._velocity = operand_data
        return self

class Sequence(Element):

    def __init__(self, position: Position = Position(0), length: Length = None,
                 trigger_notes: TriggerNotes = None,
                 duration: Duration = None, key_note: KeyNote = None, velocity: Velocity = None,
                 channel: Channel = None, device: Device = None):
        super().__init__(position, length, channel, device)
        self._trigger_notes: TriggerNotes = trigger_notes
        self._duration: Duration = duration
        self._key_note: KeyNote = key_note
        self._velocity: Velocity = velocity

    def __rshift__(self, operand):
        match operand:
            case TriggerNotes():    return self._trigger_notes  # case [] | [Note(), *rest]:  # Match an empty list or a list with one or more Note instances
            case Duration():        return self._duration
            case KeyNote():         return self._key_note
            case Velocity():        return self._velocity
        return super() >> operand

    def getValue__length(self) -> Length:
        if self._length is None:
            last_position: Position = self._trigger_notes.getLastPosition()
            sequence_length: Length = Length(measures=1)
            while last_position > sequence_length:
                sequence_length += Length(measures=1)
            return sequence_length
        return self._length
    
    def getValue__duration(self) -> Duration:
        if self._duration is None:
            return Duration().getDefault()
        return self._duration

    def getValue__key_note(self) -> KeyNote:
        if self._key_note is None:
            return KeyNote().getDefault()
        return self._key_note

    def getValue__velocity(self) -> Velocity:
        if self._velocity is None:
            return Velocity().getDefault()
        return self._velocity

    def getPlayList(self, position: Position = None):
        
        sequence_position: Position = self.getValue__position() + Position() if position is None else position
        sequence_length: Length = self.getValue__length()
        sequence_duration: Duration = self.getValue__duration()
        sequence_key_note: KeyNote = self.getValue__key_note()
        sequence_velocity_value = self.getValue__velocity().getData()
        sequence_channel_value = self.getValue__channel().getData()
        sequence_device_value = self.getValue__device().getData()
        
        play_list = []
        for trigger_note in self._trigger_notes.getValue():

            if trigger_note.getValue__position() < sequence_length:

                trigger_position: Position = sequence_position + trigger_note.getValue__position()
                trigger_duration = sequence_duration if trigger_note >> Duration() is None else trigger_note >> Duration()
                trigger_key_note = sequence_key_note if trigger_note >> KeyNote() is None else trigger_note >> KeyNote()
                trigger_velocity_value = sequence_velocity_value if trigger_note >> Velocity() is None else (trigger_note >> Velocity()).getValue()
                trigger_channel_value = sequence_channel_value if trigger_note >> Channel() is None else (trigger_note >> Channel()).getValue()
                trigger_device_value = sequence_device_value if trigger_note >> Device() is None else (trigger_note >> Device()).getValue()

                start_time_ms = (self._position + position).getTime_ms()
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
            "trigger_notes": trigger_notes_serialization,
            "duration": self._duration.getSerialization(),
            "key_note": self._key_note.getSerialization(),
            "velocity": self._velocity.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "trigger_notes" in serialization and "duration" in serialization and
            "key_note" in serialization and "velocity" in serialization):

            trigger_notes = []
            for trigger_note_serialization in serialization["trigger_notes"]:
                trigger_notes.append(
                        Note().loadSerialization(trigger_note_serialization)
                    )

            super().loadSerialization(serialization)
            self._trigger_notes: list = trigger_notes
            self._duration = Duration.loadSerialization(serialization["duration"])
            self._key_note = KeyNote.loadSerialization(serialization["key_note"])
            self._velocity = Velocity.loadSerialization(serialization["velocity"])

        return self
    
    def copy(self) -> 'Sequence':
        element_copy: Sequence = super().copy()
        
        trigger_notes: list[Note] = []
        for trigger_note in self._trigger_notes:
            trigger_notes.append(trigger_note.copy())

        element_copy.setData__trigger_notes(trigger_notes).setData__duration(self._duration.copy())
        return element_copy.setData__key_note(self._key_note.copy()).setData__velocity(self._velocity.getData())

    def __lshift__(self, operand):
        super().__lshift__(operand)
        if operand.__class__ == Empty:
            operand = operand.getOperand()
            operand_data = None
        else:
            operand_data = operand
        match operand:
            case TriggerNotes():    self._trigger_notes = operand_data
            case Duration():        self._duration = operand_data
            case KeyNote():         self._key_note = operand_data
            case Velocity():        self._velocity = operand_data
        return self

    # Right add (+) means is self being added to other_sequence
    def __radd__(self, other_sequence: 'Sequence'):
        merged_sequence = other_sequence.copy()     # Right add
        merged_trigger_notes = other_sequence.getData__trigger_notes() + self._trigger_notes
        merged_sequence.setData__trigger_notes(merged_trigger_notes)

        return other_sequence.sort()

    def __add__(self, operand = Position(note=1/4)):
        incremented_sequence = self.copy()
        operands_list = self.getList__trigger_operands(operand.__class__)
        trigger_notes = incremented_sequence.getData__trigger_notes()
        
        for trigger_i in range(len(operands_list)):
            if operands_list[trigger_i]["opperand"] is not None:
                trigger_notes[trigger_i][operands_list[trigger_i]["index_j"]] = operands_list[trigger_i]["opperand"] + operand

        return incremented_sequence

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
            play_list = play_list + placed_element["element"].getPlayList(
                    placed_element["position"] + (self._position + position)
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

