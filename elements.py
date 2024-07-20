import json

class Staff:

    def __init__(self, measures = 8):
        self._measures = measures

    def getList(self):
        ...

    def loadList(self, json_list):
        ...
        
class TimeSignature:
        
    def __init__(self, beats_per_measure = 4, beats_per_note = 4):
        self._beats_per_measure = beats_per_measure
        self._beats_per_note = beats_per_note

    def getList(self):
        ...

    def loadList(self, json_list):
        ...

class Tempo:
        
    def __init__(self, bpm = 120, pulses_per_quarternote = 24):
        self._bpm = bpm
        self._pulses_per_quarternote = pulses_per_quarternote

    def getList(self):
        ...

    def loadList(self, json_list):
        ...

    def getPlayList(self, staff, time_signature):
        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note / time_signature._beats_per_note
        staff_pulses = pulses_per_beat * time_signature._beats_per_measure * staff._measures
        staff_duration_ms = (60 * 1000 / self._bpm) * time_signature._beats_per_measure * staff._measures

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
                    "time_ms": 0,
                    "midi_message": {
                        "status_byte": 0xFA
                    }
                }
            ]

        for staff_pulse in range(1, staff_pulses):
            play_list.append(
                {
                    "time_ms": staff_duration_ms * staff_pulse / staff_pulses,
                    "midi_message": {
                        "status_byte": 0xF8
                    }
                }
            )

        play_list.append(
            {
                "time_ms": staff_duration_ms,
                "midi_message": {
                    "status_byte": 0xFC
                }
            }
        )

        return play_list


class Quantization:
        
    def __init__(self, divisions_per_note = 16):
        self._divisions_per_note = divisions_per_note

    def getList(self):
        ...

    def loadList(self, json_list):
        ...

class Creator:

    def __init__(self):
        pass

    def addDevice(play_list, devicename):
        pass

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

    def saveJsonPlay(self, json_list, filename):
        pass

