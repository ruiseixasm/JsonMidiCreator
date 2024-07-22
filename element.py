import staff
import enum

class ClockModes(enum.Enum):
    entire = 0
    single = 1
    first = 2
    middle = 3
    last = 4
    resume = 5

class Clock:

    def __init__(self, measures = 8, mode: ClockModes = ClockModes.entire, pulses_per_quarternote = 24):
        self._measures = measures
        self._mode = mode
        self._pulses_per_quarternote = pulses_per_quarternote
        self._device_list: list = None
        self._staff: staff.Staff = None

    def getData__measures(self):
        return self._measures

    def getData__mode(self):
        return self._mode

    def getData__device_list(self):
        return self._device_list

    def getData__staff(self):
        return self._staff

    def getPlayList(self, staff = staff.Staff(), position_measure: float = 0, displacement_beat: float = 0,
                    displacement_note: float = 0, displacement_step: float = 0):
        
        apt_staff = self._staff if self._staff is not None else staff

        length_measure = apt_staff.getData__measures() if self._mode == ClockModes.entire else self._measures

        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note / apt_staff.getValue__beats_per_note()
        pulses_per_measure = pulses_per_beat * apt_staff.getValue__beats_per_measure()
        clock_pulses = round(pulses_per_measure * length_measure)

        start_measure = 0 if self._mode == ClockModes.entire \
                else position_measure \
                    + displacement_beat / apt_staff.getValue__beats_per_measure() \
                    + displacement_note / apt_staff.getValue__notes_per_measure() \
                    + displacement_step / apt_staff.getValue__steps_per_measure()
        measure_duration_ms = apt_staff.getTime_ms(1)
        clock_start_ms = apt_staff.getTime_ms(start_measure)
        clock_stop_ms = clock_start_ms + apt_staff.getTime_ms(length_measure)

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
                    "time_ms": round(clock_start_ms + measure_duration_ms * self._measures * clock_pulse / clock_pulses, 3),
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

    # CHAINED OPERATIONS

    def setData__device_list(self, device_list: list = ["Midi", "Port", "Synth"]):
        self._device_list = device_list
        return self


class Note:

    def __init__(self, channel = 1, key_note = 60, velocity = 100, duration_note = 0.25):
        self._channel = channel
        self._key_note = key_note
        self._velocity = velocity
        self._duration_note = duration_note
        self._device_list: list = None
        self._staff: staff.Staff = None

    def getData__channel(self):
        return self._channel

    def getData__key_note(self):
        return self._key_note

    def getData__velocity(self):
        return self._velocity

    def getData__duration_note(self):
        return self._duration_note
    
    def getLength_steps(self, staff = staff.Staff()):
        return self._duration_note * staff.getData__quantization().getData__steps_per_note()

    def getData__device_list(self):
        return self._device_list

    def getData__staff(self):
        return self._staff

    def getPlayList(self, staff = staff.Staff(), position_measure: float = 0, displacement_beat: float = 0,
                    displacement_note: float = 0, displacement_step: float = 0):
        
        apt_staff = self._staff if self._staff is not None else staff

        on_time_ms = apt_staff.getTime_ms(position_measure, displacement_beat, displacement_note, displacement_step)
        off_time_ms = on_time_ms + apt_staff.getTime_ms(0, 0, self._duration_note)
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
    
    # CHAINED OPERATIONS

    def setData__channel(self, channel):
        self._channel = channel
        return self

    def setData__key_note(self, key_note):
        self._key_note = key_note
        return self

    def setData__velocity(self, velocity):
        self._velocity = velocity
        return self

    def setData__duration_note(self, duration_note):
        self._duration_note = duration_note
        return self

    def setData__device_list(self, device_list: list = ["Midi", "Port", "Synth"]):
        self._device_list = device_list
        return self

    def transpose(self, semitones = 12):
        self._key_note = self._key_note + semitones
        return self
    
    def quantize(self, mount = 100, staff = staff.Staff()):
        return self

    
class ControlChange:

    def __init__(self, channel = 1, control_change = 10, value = 64):    # default is 10 - pan
        pass

    # CHAINED OPERATIONS


class MidiMessage:

    def __init__(self, status_byte = 0xF2, data_byte_1 = 0, data_byte_2 = 0):   # 0xF2 - Song Position
        self._status_byte = status_byte
        self._data_byte_1 = data_byte_1
        self._data_byte_2 = data_byte_2
        self._device_list: list = None
        self._staff: staff.Staff = None

class Panic:
    ...

    # CHAINED OPERATIONS


class Chord:

    def __init__(self, root_note = 60, size = 3, scale = staff.Scale()):   # 0xF2 - Song Position
        self._root_note = root_note
        self._size = size
        self._scale = scale
        self._notes = []
        self._device_list: list = None
        self._staff: staff.Staff = None

    # CHAINED OPERATIONS

class Arpeggio:
    ...

    # CHAINED OPERATIONS


class Loop:

    def __init__(self, element, repeat = 4):
        self._element = element
        self._repeat = repeat
        self._device_list: list = None
        self._staff: staff.Staff = None
    
    # CHAINED OPERATIONS


class Stack:
    ...

    # CHAINED OPERATIONS

class Automation:
    ...

    # CHAINED OPERATIONS

class Sequence:

    def __init__(self, channel = 1, key_note = 60, length_beats = 4, sequence = [
            {"step": 0, "velocity": 100, "duration_note": 1/8},
            {"step": 3, "velocity": 100, "duration_note": 1/8},
            {"step": 7, "velocity": 100, "duration_note": 1/8},
            {"step": 11, "velocity": 100, "duration_note": 1/8}
        ]):
        self._channel = channel
        self._key_note = key_note
        self._length_beats = length_beats
        self._sequence = sequence
        self._device_list: list = None
        self._staff: staff.Staff = None
    
    def getData__device_list(self):
        return self._device_list

    def getData__staff(self):
        return self._staff

    def getPlayList(self, staff = staff.Staff(), position_measure: float = 0, displacement_beat: float = 0,
                    displacement_note: float = 0, displacement_step: float = 0):
        
        apt_staff = self._staff if self._staff is not None else staff

        start_time_ms = apt_staff.getTime_ms(position_measure, displacement_beat, displacement_note, displacement_step)

        play_list = []
        for trigger_note in self._sequence:

            if "step" in trigger_note and "velocity" in trigger_note and "duration_note" in trigger_note:

                on_time_ms = start_time_ms + apt_staff.getTime_ms(0, 0, 0, trigger_note["step"])
                play_list.append({
                        "time_ms": round(on_time_ms, 3),
                        "midi_message": {
                            "status_byte": 0x90 | 0x0F & (self._channel - 1),
                            "data_byte_1": self._key_note,
                            "data_byte_2": trigger_note["velocity"]
                        }
                    })
                
                off_time_ms = on_time_ms + apt_staff.getTime_ms(0, 0, trigger_note["duration_note"])
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
    
    # CHAINED OPERATIONS

    def setData__device_list(self, device_list: list = ["Midi", "Port", "Synth"]):
        self._device_list = device_list
        return self

    def setData__staff(self, staff: staff.Staff = None):
        self._staff = staff
        return self


class Retrigger:
    ...
    
    # CHAINED OPERATIONS


class Composition:

    def __init__(self):
        self._placed_elements = []
        self._device_list: list = None
        self._staff: staff.Staff = None

    def getData__device_list(self):
        return self._device_list

    def getData__staff(self):
        return self._staff

    def getPlayList(self, staff = staff.Staff(), position_measure: float = 0, displacement_beat: float = 0,
                    displacement_note: float = 0, displacement_step: float = 0):
        
        apt_staff = self._staff if self._staff is not None else staff

        play_list = []
        for placed_element in self._placed_elements:
            play_list = play_list + placed_element["element"].getPlayList(
                    apt_staff,
                    placed_element["position_measure"] + position_measure,
                    placed_element["displacement_beat"] + displacement_beat,
                    placed_element["displacement_note"] + displacement_note,
                    placed_element["displacement_step"] + displacement_step
                )
            
        if isinstance(self._device_list, list):
            for list_element in play_list:
                if "midi_message" in list_element:
                    if "device" not in list_element["midi_message"]:
                            list_element["midi_message"]["device"] = self._device_list

        return play_list

    # CHAINED OPERATIONS

    def setData__device_list(self, device_list: list = ["Midi", "Port", "Synth"]):
        self._device_list = device_list
        return self

    def placeElement(self, element, position_measure: float, displacement_beat: float = 0,
                    displacement_note: float = 0, displacement_step: float = 0):
        self._placed_elements.append({
                "element": element,
                "position_measure": position_measure,
                "displacement_beat": displacement_beat,
                "displacement_note": displacement_note,
                "displacement_step": displacement_step
            })
        return self

    def takeElement(self, element, position_measure: float, displacement_beat: float = 0,
                    displacement_note: float = 0, displacement_step: float = 0):
        self._placed_elements.remove({
                "element": element,
                "position_measure": position_measure,
                "displacement_beat": displacement_beat,
                "displacement_note": displacement_note,
                "displacement_step": displacement_step
            })
        return self
        
    def clear(self):
        self._placed_elements = []
        return self

    def displace(self, displacement_note):
        ...
        return self

