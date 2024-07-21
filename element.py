import staff
import enum

class ClockModes(enum.Enum):
    single = 1
    first = 2
    middle = 3
    last = 4

class Clock:

    def __init__(self, measures = 8, mode: ClockModes = ClockModes.single):
        self._measures = measures
        self._mode = mode

    def getData__measures(self):
        return self._measures

    def getData__mode(self):
        return self._mode

    def getPlayList(self, position_measure, displacement_note, time_signature = staff.TimeSignature(), tempo = staff.Tempo()):
        pulses_per_note = 4 * tempo.getData__pulses_per_quarternote()
        pulses_per_beat = pulses_per_note / time_signature.getData__beats_per_note()
        pulses_per_measure = pulses_per_beat * time_signature.getData__beats_per_measure()
        clock_pulses = round(pulses_per_measure * self._measures)

        notes_per_measure = time_signature.getData__beats_per_measure() / time_signature.getData__beats_per_note()
        start_measure = position_measure + displacement_note / notes_per_measure
        measure_duration_ms = time_signature.getData__beats_per_measure() * 60.0 * 1000 / tempo.getData__bpm()
        clock_start_ms = start_measure * measure_duration_ms
        clock_stop_ms = clock_start_ms + self._measures * measure_duration_ms

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
                        "status_byte": 0xFA if self._mode == ClockModes.single or self._mode == ClockModes.first else 0xF8
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

        if self._mode == ClockModes.single or self._mode == ClockModes.last:

            play_list.append(
                {
                    "time_ms": round(clock_stop_ms, 3),
                    "midi_message": {
                        "status_byte": 0xFC
                    }
                }
            )

        return play_list

    # CHAINED OPERATIONS


class Note:

    def __init__(self, channel = 1, key_note = 60, velocity = 100, duration_note = 0.25):
        self._channel = channel
        self._key_note = key_note
        self._velocity = velocity
        self._duration_note = duration_note

    def getData__channel(self):
        return self._channel

    def getData__key_note(self):
        return self._key_note

    def getData__velocity(self):
        return self._velocity

    def getData__duration_note(self):
        return self._duration_note
    
    def getLength_beats(self, time_signature = staff.TimeSignature()):
        return self._duration_note * time_signature.getData__beats_per_note()

    def getPlayList(self, position_measure, displacement_note, time_signature, tempo):
        on_position_ms = tempo.getTime_ms(position_measure, displacement_note, time_signature)
        off_position_ms = on_position_ms + tempo.getTime_ms(0, self._duration_note, time_signature)
        return [
                {
                    "time_ms": round(on_position_ms, 3),
                    "midi_message": {
                        "status_byte": 0x90 | 0x0F & (self._channel - 1),
                        "data_byte_1": self._key_note,
                        "data_byte_2": self._velocity
                    }
                },
                {
                    "time_ms": round(off_position_ms, 3),
                    "midi_message": {
                        "status_byte": 0x80 | 0x0F & (self._channel - 1),
                        "data_byte_1": self._key_note,
                        "data_byte_2": 0
                    }
                }
            ]
    
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

    def transpose(self, chromatic_steps = 12):
        self._key_note = self._key_note + chromatic_steps
        return self
    

    
class ControlChange:

    def __init__(self, channel = 1, control_change = 10, value = 64):    # 10 - pan
        pass

    # CHAINED OPERATIONS


class MidiMessage:

    def __init__(self, status_byte = 0xF2, data_byte_1 = 0, data_byte_2 = 0):   # 0xF2 - Song Position
        self._status_byte = status_byte
        self._data_byte_1 = data_byte_1
        self._data_byte_2 = data_byte_2

class Panic:
    ...

    # CHAINED OPERATIONS


class Chord:
    def __init__(self, root_note = 60, size = 3, scale = staff.Scale()):   # 0xF2 - Song Position
        self._root_note = root_note
        self._size = size
        self._scale = scale
        self._notes = []

    # CHAINED OPERATIONS


class Loop:
    ...
    
    # CHAINED OPERATIONS


class Agregation:
    ...

    # CHAINED OPERATIONS


class Stack:
    ...

    # CHAINED OPERATIONS


class Positioner:

    def __init__(self, time_signature = staff.TimeSignature(), tempo = staff.Tempo()):
        self._placed_elements = []
        self._time_signature = time_signature
        self._tempo = tempo

    def setTimeSignature(self, time_signature = staff.TimeSignature()):
        self._time_signature = time_signature
        return self

    def setTempo(self, tempo = staff.Tempo()):
        self._tempo = tempo
        return self

    def placeElement(self, element, position_measure, displacement_note):
        self._placed_elements.append({
                "element": element,
                "position_measure": position_measure,
                "displacement_note": displacement_note
            })

    def takeElement(self, element, position_measure, displacement_note):
        self._placed_elements.remove({
                "element": element,
                "position_measure": position_measure,
                "displacement_note": displacement_note
            })
        
    def replaceAll(self, position_measure, displacement_note):
        ...
        return self

    def moveAll(self, position_measure, displacement_note):
        ...
        return self

    def getPlayList(self):
        play_list = []
        for placed_element in self._placed_elements:
            play_list = play_list + placed_element["element"].getPlayList(
                    placed_element["position_measure"], placed_element["displacement_note"],
                    self._time_signature, self._tempo
                )
        return play_list

    # CHAINED OPERATIONS

