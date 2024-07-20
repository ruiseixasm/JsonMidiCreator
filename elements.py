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

    def noteDivisionFromBeats(self, beats):
        return beats / self._beats_per_note
        
    def noteDivisionFromMeasures(self, measures):
        return measures * self._beats_per_measure / self._beats_per_note
        
    def getList(self):
        ...

    def loadList(self, json_list):
        ...

class Tempo:
        
    def __init__(self, bpm = 120, pulses_per_quarternote = 24):
        self._bpm = bpm
        self._pulses_per_quarternote = pulses_per_quarternote

    def getTime_ms(self, measure, notedivision, time_signature):
        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note / time_signature._beats_per_note
        pulses_per_measure = pulses_per_beat * time_signature._beats_per_measure
        
        return (60.0 * 1000 / self._bpm / pulses_per_beat) * (pulses_per_measure * measure + pulses_per_note * notedivision)
        
    def getList(self):
        ...

    def loadList(self, json_list):
        ...

    def getPlayList(self, staff, time_signature):
        pulses_per_note = 4 * self._pulses_per_quarternote
        pulses_per_beat = pulses_per_note / time_signature._beats_per_note
        staff_pulses = round(pulses_per_beat * time_signature._beats_per_measure * staff._measures)
        staff_duration_ms = (60.0 * 1000 / self._bpm) * time_signature._beats_per_measure * staff._measures

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
                    "time_ms": 0.000,
                    "midi_message": {
                        "status_byte": 0xFA
                    }
                }
            ]

        for staff_pulse in range(1, staff_pulses):
            play_list.append(
                {
                    "time_ms": round(staff_duration_ms * staff_pulse / staff_pulses, 3),
                    "midi_message": {
                        "status_byte": 0xF8
                    }
                }
            )

        play_list.append(
            {
                "time_ms": round(staff_duration_ms, 3),
                "midi_message": {
                    "status_byte": 0xFC
                }
            }
        )

        return play_list

class Quantization:
        
    def __init__(self, steps_per_note = 16):
        self._steps_per_note = steps_per_note

    def noteDivisionFromSteps(self, steps):
        return steps / self._steps_per_note
        
    def getList(self):
        ...

    def loadList(self, json_list):
        ...

class Note:

    def __init__(self, channel = 1, key_note = 60, velocity = 100, notedivision_duration = 0.25):
        self._channel = channel
        self._key_note = key_note
        self._velocity = velocity
        self._notedivision_duration = notedivision_duration

    def getPlayList(self, measure, notedivision, time_signature, tempo):
        on_position_ms = tempo.getTime_ms(measure, notedivision, time_signature)
        off_position_ms = on_position_ms + tempo.getTime_ms(0, self._notedivision_duration, time_signature)
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
    
class Automation:

    def __init__(self, channel = 1, control_change = 10, value = 64):    # 10 - pan
        pass

class MidiMessage:

    def __init__(self, status_byte = 0xF2, data_byte_1 = 0, data_byte_2 = 0):   # 0xF2 - Song Position
        self._status_byte = status_byte
        self._data_byte_1 = data_byte_1
        self._data_byte_2 = data_byte_2

class PlacedElements:

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

    def placeElement(self, element, measure, notedivision):
        self._placed_elements.append({
                "element": element,
                "measure": measure,
                "notedivision": notedivision
            })

    def takeElement(self, element, measure, notedivision):
        self._placed_elements.remove({
                "element": element,
                "measure": measure,
                "notedivision": notedivision
            })
        
    def replaceAll(self, measure, notedivision):
        ...
        return self

    def moveAll(self, measure, notedivision):
        ...
        return self

    def getPlayList(self):
        play_list = []
        for placed_element in self._placed_elements:
            play_list = play_list + placed_element["element"].getPlayList(
                    placed_element["measure"], placed_element["notedivision"],
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

