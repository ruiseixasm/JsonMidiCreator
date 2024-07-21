import staff
import enum
import json

class ClockModes(enum.Enum):
    full = 1
    start = 2
    middle = 3
    stop = 4

class Clock:

    def __init__(self, measures = 8, mode: ClockModes = ClockModes.full):
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
                        "status_byte": 0xFA if self._mode == ClockModes.full or self._mode == ClockModes.start else 0xF8
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

        if self._mode == ClockModes.full or self._mode == ClockModes.stop:

            play_list.append(
                {
                    "time_ms": round(clock_stop_ms, 3),
                    "midi_message": {
                        "status_byte": 0xFC
                    }
                }
            )

        return play_list

class Note:

    def __init__(self, channel = 1, key_note = 60, velocity = 100, duration_note = 0.25):
        self._channel = channel
        self._key_note = key_note
        self._velocity = velocity
        self._duration_note = duration_note

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
    
class ControlChange:

    def __init__(self, channel = 1, control_change = 10, value = 64):    # 10 - pan
        pass

class MidiMessage:

    def __init__(self, status_byte = 0xF2, data_byte_1 = 0, data_byte_2 = 0):   # 0xF2 - Song Position
        self._status_byte = status_byte
        self._data_byte_1 = data_byte_1
        self._data_byte_2 = data_byte_2

class Panic:
    ...

class Chord:
    ...

class Agregation:
    ...

class Stack:
    ...

class Positioner:

    def __init__(self, time_signature, tempo):
        self._placed_elements = []
        self._time_signature = time_signature
        self._tempo = tempo

    def setTimeSignature(self, time_signature):
        self._time_signature = time_signature
        return self

    def setTempo(self, tempo):
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

class PlayListCreator:

    def __init__(self):
        pass

    def addDevice(self, play_list, devicename):
        for element in play_list:
            if "midi_message" in element:
                if "device" in element["midi_message"]:
                    element["midi_message"]["device"].append(devicename)
                else:
                    element["midi_message"]["device"] = [ devicename ]
        return play_list

    def removeDevice(play_list, devicename):
        pass

    def printDevices(play_list):
        pass

    def setChannel(play_list, channel):
        pass

    def saveJson(self, json_list, filename):
        pass

    def loadJson(self, filename):
        pass

    def saveJsonPlay(self, play_list, filename):
        json_file_dict = {
                "filetype": "Midi Json Player",
                "content": play_list
            }
        
        with open(filename, "w") as outfile:
            json.dump(json_file_dict, outfile)

