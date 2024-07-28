from staff import *
from operand import *
import enum

class ClockModes(enum.Enum):
    single = 1
    first = 2
    middle = 3
    last = 4
    resume = 5

class Clock:

    def __init__(self, position: Position = Position(0), length: Length = None, mode: ClockModes = ClockModes.single, device_list: list = None, pulses_per_quarternote: int = 24):
        self._position: Position = position
        self._length: Length = length
        self._mode = mode
        self._device_list: list = device_list
        self._pulses_per_quarternote = pulses_per_quarternote

    def getData__length(self):
        return self._length

    def getData__mode(self):
        return self._mode

    def getData__device_list(self):
        return self._device_list

    def getPlayList(self, position: Position = None):
        
        on_staff = get_global_staff()
        position = Position(0) if position is None else position

        clock_length = Length(on_staff.getData__measures()) if self._length is None else self._length

        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note / on_staff.getValue__beats_per_note()
        pulses_per_measure = pulses_per_beat * on_staff.getValue__beats_per_measure()
        clock_pulses = round(pulses_per_measure * clock_length.getData__measures())

        single_measure_length_ms = Length(measures=1).getTime_ms()
        clock_start_ms = position.getTime_ms()
        clock_stop_ms = clock_start_ms + clock_length.getTime_ms()

        # System Real-Time Message         Status Byte 
        # ------------------------         -----------
        # Timing Clock                         F8
        # Start Sequence                       FA
        # Continue Sequence                    FB
        # Stop Sequence                        FC
        # Active Sensing                       FE
        # System Reset                         FF

        play_list = [
                {
                    "time_ms": round(clock_start_ms, 3),
                    "midi_message": {
                        "status_byte": 0xFA if self._mode == ClockModes.single or self._mode == ClockModes.first
                            else 0xFB if self._mode == ClockModes.resume else 0xF8
                    }
                }
            ]

        for clock_pulse in range(1, clock_pulses):
            play_list.append(
                {
                    "time_ms": round(clock_start_ms + single_measure_length_ms \
                                     * clock_length.getData__measures() * clock_pulse / clock_pulses, 3),
                    "midi_message": {
                        "status_byte": 0xF8
                    }
                }
            )

        if self._mode == ClockModes.single or self._mode == ClockModes.last:

            play_list.append(
                {
                    "time_ms": round(clock_stop_ms, 3),
                    "midi_message": {
                        "status_byte": 0xFC
                    }
                }
            )
        
        if isinstance(self._device_list, list):
            for list_element in play_list:
                list_element["midi_message"]["device"] = self._device_list

        return play_list

    # CHAINABLE OPERATIONS

    def setData__device_list(self, device_list: list = None):
        self._device_list = device_list
        return self


class Note:

    def __init__(self, position: Position = Position(0), length: Length = Length(beats=1),
                 duration: Duration = None, note_key: int = None, velocity: int = None, channel: int = None, device_list: list = None):
        self._position: Position = position
        self._length: Length = length
        self._duration: Duration = duration
        self._note_key = note_key
        self._velocity = velocity
        self._channel = channel
        self._device_list: list = device_list

    def getData__position(self):
        return self._position
    
    def getData__length(self):
        return self._length
    
    def getData__duration(self):
        return self._duration
    
    def getData__note_key(self):
        return self._note_key

    def getData__velocity(self):
        return self._velocity

    def getData__channel(self):
        return self._channel

    def getData__device_list(self):
        return self._device_list

    def getPlayList(self, position: Position = None):
        
        position = Position(0) if position is None else position
        on_time_ms = (self._position + position).getTime_ms()
        note_duration = Duration(note=get_global_staff().getData__note_duration()) if self._duration is None else self._duration
        note_key = get_global_staff().getData__note_key() if self._note_key is None else self._note_key
        note_velocity = get_global_staff().getData__note_velocity() if self._velocity is None else self._velocity
        note_channel = get_global_staff().getData__channel() if self._channel is None else self._channel
        device_list = get_global_staff().getData__device_list() if self._device_list is None else self._device_list
        off_time_ms = on_time_ms + note_duration.getTime_ms()
        play_list = [
                {
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & (note_channel - 1),
                        "data_byte_1": note_key,
                        "data_byte_2": note_velocity
                    }
                },
                {
                    "time_ms": round(off_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & (note_channel - 1),
                        "data_byte_1": note_key,
                        "data_byte_2": 0
                    }
                }
            ]
    
        if isinstance(device_list, list):
            for list_element in play_list:
                list_element["midi_message"]["device"] = device_list

        return play_list
    
    # CHAINABLE OPERATIONS

    def setData__position(self, position: Position = Position(0)):
        self._position = position
        return self

    def setData__length(self, length: Length = Length(beats=1)):
        self._length = length
        return self

    def setData__duration(self, duration: Duration = None):
        self._duration = duration
        return self

    def setData__note_key(self, note_key: int):
        self._note_key = note_key
        return self

    def setData__velocity(self, velocity: int):
        self._velocity = velocity
        return self

    def setData__channel(self, channel: int):
        self._channel = channel
        return self

    def setData__device_list(self, device_list: list = None):
        self._device_list = device_list
        return self

    def transpose(self, semitones: int = 12):
        self._note_key = self._note_key + semitones
        return self
    
    def quantize(self, amount = 100):
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
        self._device_list: list = None

class Panic:
    ...

    # CHAINABLE OPERATIONS


class Chord:

    def __init__(self, root_note = 60, size = 3, scale = Scale()):   # 0xF2 - Song Position
        self._root_note = root_note
        self._size = size
        self._scale = scale
        self._notes = []
        self._device_list: list = None

    # CHAINABLE OPERATIONS

class Arpeggio:
    ...

    # CHAINABLE OPERATIONS


class Loop:

    def __init__(self, element, repeat = 4):
        self._element = element
        self._repeat = repeat
        self._device_list: list = None
    
    # CHAINABLE OPERATIONS


class Stack:
    ...

    # CHAINABLE OPERATIONS

class Automation:
    ...

    # CHAINABLE OPERATIONS

class Sequence:

    def __init__(self, position: Position = Position(0), length: Length = Length(beats=4), trigger_notes: list = [],
                 duration: Duration = None, note_key: int = None, velocity: int = None, channel: int = None, device_list: list = None):
        self._position: Position = position
        self._length: Length = length
        self._channel = channel
        self._note_key = note_key
        self._trigger_notes: list = trigger_notes
        self._device_list: list = None

        self.sort()
    
    def getData__channel(self):
        return self._channel

    def getData__note_key(self):
        return self._note_key

    def getData__trigger_notes(self):
        return self._trigger_notes

    def getData__device_list(self):
        return self._device_list
    
    def getList__trigger_operands(self, opperand_type = Position):
        trigger_operands = []
        for trigger_i in range(0, len(self._trigger_notes)):
            for operand_j in range(0, len(self._trigger_notes[trigger_i])):
                if (self._trigger_notes[trigger_i][operand_j].__class__ == opperand_type):
                    trigger_operands.append({
                            "index_i": trigger_i,
                            "index_j": operand_j,
                            "opperand": self._trigger_notes[trigger_i][operand_j]
                        })
                    break
                trigger_operands.append({
                        "index_i": -1,
                        "index_j": -1,
                        "opperand": None
                    })
        return trigger_operands

    def is_position_triggered(self, position: Position):
        ...

    def getPlayList(self, position: Position = None):
        
        position = Position(0) if position is None else position
        start_time_ms = (self._position + position).getTime_ms()

        play_list = []
        for trigger_note in self._trigger_notes:

            on_position = Position(0)
            with_duration = Duration(note=1/4)
            with_velocity = Velocity(100)

            # for note_operand in trigger_note:
            #     match note_operand.__class__:
            #         case Position:
            #             on_position = note_operand
            #         case Duration:
            #             with_duration = note_operand
            #         case Velocity:
            #             with_velocity = note_operand

            for note_operand in trigger_note:
                if (note_operand.__class__ == Position):
                    on_position = note_operand
                elif (note_operand.__class__ == Duration):
                    with_duration = note_operand
                elif (note_operand.__class__ == Velocity):
                    with_velocity = note_operand

            on_time_ms = start_time_ms + on_position.getTime_ms()
            play_list.append({
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & (self._channel - 1),
                        "data_byte_1": self._note_key,
                        "data_byte_2": with_velocity.getData__velocity()
                    }
                })
            
            off_time_ms = on_time_ms + with_duration.getTime_ms()
            play_list.append({
                    "time_ms": round(off_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & (self._channel - 1),
                        "data_byte_1": self._note_key,
                        "data_byte_2": 0
                    }
                })

        if isinstance(self._device_list, list):
            for list_element in play_list:
                list_element["midi_message"]["device"] = self._device_list

        return play_list
    
    def getSerialization(self):
        trigger_notes_serialization = []
        for trigger_note in self._trigger_notes:
            note_operand_serialization = []
            for note_operand in trigger_note:
                note_operand_serialization.append(
                    note_operand.getSerialization()
                )
            trigger_notes_serialization.append(note_operand_serialization)

        return {
            "class": self.__class__.__name__,
            "channel": self._channel, 
            "note_key": self._note_key,
            "length": None if self._length is None else self._length.getSerialization(),
            "trigger_notes": trigger_notes_serialization,
            "device_list": self._device_list
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "channel" in serialization and "note_key" in serialization and "length" in serialization and
            "trigger_notes" in serialization and "device_list" in serialization):

            trigger_notes_serialization = []
            for trigger_note in serialization["trigger_notes"]:
                note_operand_serialization = []
                for note_operand in trigger_note:
                    note_operand_serialization.append(
                        globals()[note_operand["class"]].loadSerialization(note_operand)
                    )
                trigger_notes_serialization.append(note_operand_serialization)

            self._channel = serialization["channel"]
            self._note_key = serialization["note_key"]
            self._length = None if serialization["length"] is None else \
                Length().loadSerialization(serialization["length"])
            self._trigger_notes: list = trigger_notes_serialization
            self._device_list: list = serialization["device_list"]

        return self
    
    def copy(self):
        device_list_copy = []
        for trigger_note in self._trigger_notes:
            note_operand_copy = []
            for note_operand in trigger_note:
                note_operand_copy.append(
                    note_operand.copy()
                )
            device_list_copy.append(note_operand_copy)

        sequence_copy = Sequence(
            self._channel,
            self._note_key,
            self._length,
            device_list_copy
        )

        if self._device_list is not None:
            sequence_copy.setData__device_list(self._device_list.copy())
            
        return sequence_copy

    def setData__channel(self, channel: int = 10):
        self._channel = channel
        return self

    def setData__note_key(self, note_key: int = 60):
        self._note_key = note_key
        return self

    def setData__trigger_notes(self, trigger_notes: list):
        self._trigger_notes = trigger_notes
        return self

    def setData__device_list(self, device_list: list = None):
        self._device_list = device_list
        return self

    def remove_unplaced_trigger_notes(self):
        trigger_notes_to_remove = []
        for trigger_i in range(0, len(self._trigger_notes)):
            for operand_j in range(0, len(self._trigger_notes[trigger_i])):
                if (self._trigger_notes[trigger_i][operand_j].__class__ == Position):
                    break
                trigger_notes_to_remove.append(trigger_i)
        for trigger_note_index in trigger_notes_to_remove:
            self._trigger_notes.pop(trigger_note_index)

        return self

    def sort(self):

        self.remove_unplaced_trigger_notes()
        trigger_operands = self.getList__trigger_operands(Position)



        for trigger_k in range(len(self._trigger_notes), 0, -1):
            for trigger_i in range(trigger_k):

                changed_position = False

                for operand_j in range(0, len(self._trigger_notes[trigger_i])):
                    if (self._trigger_notes[trigger_i][operand_j].__class__ == Position):
                        position_i = self._trigger_notes[trigger_i][operand_j]
                        break
                for operand_j in range(0, len(self._trigger_notes[trigger_i - 1])):
                    if (self._trigger_notes[trigger_i - 1][operand_j].__class__ == Position):
                        position_i_1 = self._trigger_notes[trigger_i - 1][operand_j]
                        break
                    
                if position_i < position_i_1:
                    trigger_note = self._trigger_notes[trigger_i]
                    self._trigger_notes[trigger_i] = self._trigger_notes[trigger_i - 1]
                    self._trigger_notes[trigger_i - 1] = trigger_note
                    changed_position = True

                if not changed_position:
                    break

        return self

    def trim(self, position = Position(beats=4)):

        self.sort()
        sorted_trigger_notes = self._trigger_notes

        for trigger_i in range(0, len(sorted_trigger_notes)):
            for operand_j in range(0, len(sorted_trigger_notes[trigger_i])):
                if (sorted_trigger_notes[trigger_i][operand_j].__class__ == Position):
                    trigger_position: Position = sorted_trigger_notes[trigger_i][operand_j]
                    break
            if (trigger_position.is_gt(position)):
                trim_trigger_i = trigger_i
                break

        self._trigger_notes = sorted_trigger_notes[0, trim_trigger_i]
    
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

    def op_add(self, operand = Duration()):
        for trigger_i in range(0, len(self._trigger_notes)):
            for operand_j in range(0, len(self._trigger_notes[trigger_i])):
                if (self._trigger_notes[trigger_i][operand_j].__class__ == operand.__class__):
                    self._trigger_notes[trigger_i][operand_j] += operand




class Retrigger:
    ...
    
    # CHAINABLE OPERATIONS


class Composition:

    def __init__(self, position: Position = Position(0), length: Length = Length(measures=4)):
        self._position: Position = position
        self._length: Length = length
        self._placed_elements = []
        self._device_list: list = None

    def getData__device_list(self):
        return self._device_list

    def getPlayList(self, position: Position = None):
        
        position = Position(0) if position is None else position
        play_list = []
        for placed_element in self._placed_elements:
            play_list = play_list + placed_element["element"].getPlayList(
                    placed_element["position"] + (self._position + position)
                )
            
        if isinstance(self._device_list, list):
            for list_element in play_list:
                if "midi_message" in list_element:
                    if "device" not in list_element["midi_message"]:
                            list_element["midi_message"]["device"] = self._device_list

        return play_list

    # CHAINABLE OPERATIONS

    def setData__device_list(self, device_list: list = ["FLUID", "Midi", "Port", "Synth"]):
        self._device_list = device_list
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

