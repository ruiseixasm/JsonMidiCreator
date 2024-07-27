from staff import *
from operand import *
import enum

class ClockModes(enum.Enum):
    entire = 0
    single = 1
    first = 2
    middle = 3
    last = 4
    resume = 5

class Clock:

    def __init__(self, duration = Duration(Length(measures=8)), mode: ClockModes = ClockModes.entire, pulses_per_quarternote = 24):
        self._duration: Duration = duration
        self._mode = mode
        self._pulses_per_quarternote = pulses_per_quarternote
        self._device_list: list = None
        self._staff: Staff = None

    def getData__duration(self):
        return self._duration

    def getData__mode(self):
        return self._mode

    def getData__device_list(self):
        return self._device_list

    def getData__staff(self):
        return self._staff

    def getPlayList(self, staff = Staff(), position: Position = Position()):
        
        on_staff = self._staff if self._staff is not None else staff

        clock_duration = Duration(Length(on_staff.getData__measures())) if self._mode == ClockModes.entire else self._duration

        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note / on_staff.getValue__beats_per_note()
        pulses_per_measure = pulses_per_beat * on_staff.getValue__beats_per_measure()
        clock_pulses = round(pulses_per_measure * clock_duration.getData__length().getData__measures())

        single_measure_duration_ms = on_staff.getTime_ms(Length(1))
        clock_start_ms = position.getTime_ms(on_staff)
        clock_stop_ms = clock_start_ms + clock_duration.getTime_ms(on_staff)

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
                        "status_byte": 0xFA if self._mode == ClockModes.entire
                                or self._mode == ClockModes.single
                                or self._mode == ClockModes.first
                            else 0xFB if self._mode == ClockModes.resume else 0xF8
                    }
                }
            ]

        for clock_pulse in range(1, clock_pulses):
            play_list.append(
                {
                    "time_ms": round(clock_start_ms + single_measure_duration_ms \
                                     * clock_duration.getData__length().getData__measures() * clock_pulse / clock_pulses, 3),
                    "midi_message": {
                        "status_byte": 0xF8
                    }
                }
            )

        if self._mode == ClockModes.entire or self._mode == ClockModes.single or \
                self._mode == ClockModes.last:

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

    def setData__device_list(self, device_list: list = ["Midi", "Port", "Synth"]):
        self._device_list = device_list
        return self


class Note:

    def __init__(self, channel = 1, key_note = 60, velocity = 100, duration = Duration(Length(note=1/4))):
        self._channel = channel
        self._key_note = key_note
        self._velocity = velocity
        self._duration: Duration = duration
        self._device_list: list = None
        self._staff: Staff = None

    def getData__channel(self):
        return self._channel

    def getData__key_note(self):
        return self._key_note

    def getData__velocity(self):
        return self._velocity

    def getData__duration(self):
        return self._duration
    
    def getLength_steps(self, staff = Staff()):
        return self._duration * staff.getData__quantization().getData__steps_per_note()

    def getData__device_list(self):
        return self._device_list

    def getData__staff(self):
        return self._staff

    def getPlayList(self, staff = Staff(), position: Position = Position()):
        
        on_staff = self._staff if self._staff is not None else staff

        on_time_ms = position.getTime_ms(on_staff)
        off_time_ms = on_time_ms + self._duration.getTime_ms(on_staff)
        play_list = [
                {
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & (self._channel - 1),
                        "data_byte_1": self._key_note,
                        "data_byte_2": self._velocity
                    }
                },
                {
                    "time_ms": round(off_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & (self._channel - 1),
                        "data_byte_1": self._key_note,
                        "data_byte_2": 0
                    }
                }
            ]
    
        if isinstance(self._device_list, list):
            for list_element in play_list:
                list_element["midi_message"]["device"] = self._device_list

        return play_list
    
    # CHAINABLE OPERATIONS

    def setData__channel(self, channel: int):
        self._channel = channel
        return self

    def setData__key_note(self, key_note: int):
        self._key_note = key_note
        return self

    def setData__velocity(self, velocity: int):
        self._velocity = velocity
        return self

    def setData__duration(self, duration: Duration):
        self._duration = duration
        return self

    def setData__device_list(self, device_list: list = ["Midi", "Port", "Synth"]):
        self._device_list = device_list
        return self

    def transpose(self, semitones: int = 12):
        self._key_note = self._key_note + semitones
        return self
    
    def quantize(self, amount = 100, staff = Staff()):
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
        self._staff: Staff = None

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
        self._staff: Staff = None

    # CHAINABLE OPERATIONS

class Arpeggio:
    ...

    # CHAINABLE OPERATIONS


class Loop:

    def __init__(self, element, repeat = 4):
        self._element = element
        self._repeat = repeat
        self._device_list: list = None
        self._staff: Staff = None
    
    # CHAINABLE OPERATIONS


class Stack:
    ...

    # CHAINABLE OPERATIONS

class Automation:
    ...

    # CHAINABLE OPERATIONS

class Sequence:

    def __init__(self, channel = 1, key_note = 60, length_beats = 4, sequence: list = [
            [ Position(Length(steps=0)), Velocity(100), Duration(Length(note=1/8)) ],
            [ Position(Length(steps=4)), Velocity(100), Duration(Length(note=1/8)) ],
            [ Position(Length(steps=8)), Velocity(100), Duration(Length(note=1/8)) ],
            [ Position(Length(steps=12)), Velocity(100), Duration(Length(note=1/8)) ]
        ]):
        self._channel = channel
        self._key_note = key_note
        self._length_beats = length_beats   # to change to Length type
        self._sequence: list = sequence
        self._device_list: list = None
        self._staff: Staff = None
    
    def getData__device_list(self):
        return self._device_list

    def getData__staff(self):
        return self._staff

    def getPlayList(self, staff = Staff(), position: Position = Position()):
        
        on_staff = self._staff if self._staff is not None else staff

        start_time_ms = position.getTime_ms(on_staff)

        play_list = []
        for trigger_note in self._sequence:

            on_position = Position(Length(0))
            with_duration = Duration(Length(note=1/4))
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

            on_time_ms = start_time_ms + on_position.getTime_ms(on_staff)
            play_list.append({
                    "time_ms": round(on_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & (self._channel - 1),
                        "data_byte_1": self._key_note,
                        "data_byte_2": with_velocity.getData__velocity()
                    }
                })
            
            off_time_ms = on_time_ms + with_duration.getTime_ms(on_staff)
            play_list.append({
                    "time_ms": round(off_time_ms, 3),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & (self._channel - 1),
                        "data_byte_1": self._key_note,
                        "data_byte_2": 0
                    }
                })

        if isinstance(self._device_list, list):
            for list_element in play_list:
                list_element["midi_message"]["device"] = self._device_list

        return play_list
    
    # CHAINABLE OPERATIONS

    def copy(self):
        sequence_copy = Sequence(
            self._channel,
            self._key_note,
            self._length_beats,
            self._sequence.copy()
        )
        if self._device_list is not None:
            sequence_copy.setData__device_list(self._device_list.copy())
        if self._staff is not None:
            sequence_copy.setData__staff(self._staff)
            
        return sequence_copy

    def setData__device_list(self, device_list: list = ["Midi", "Port", "Synth"]):
        self._device_list = device_list
        return self

    def setData__staff(self, staff: Staff = None):
        self._staff = staff
        return self

    def op_add(self, operand = Duration()):
        for trigger_i in range(0, len(self._sequence)):
            for operand_j in range(0, len(self._sequence[trigger_i])):
                if (self._sequence[trigger_i][operand_j].__class__ == operand.__class__):
                    self._sequence[trigger_i][operand_j] += operand




class Retrigger:
    ...
    
    # CHAINABLE OPERATIONS


class Composition:

    def __init__(self):
        self._placed_elements = []
        self._device_list: list = None
        self._staff: Staff = None

    def getData__device_list(self):
        return self._device_list

    def getData__staff(self):
        return self._staff

    def getPlayList(self, staff = Staff(), position: Position = Position()):
        
        on_staff = self._staff if self._staff is not None else staff

        play_list = []
        for placed_element in self._placed_elements:
            play_list = play_list + placed_element["element"].getPlayList(
                    on_staff, placed_element["position"] + position
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

