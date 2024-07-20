import json

class Staff:

    def __init__(self, measures = 8):
        self._measures = measures

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

    def getPlayList(self, staff):
        ...
        
class TimeSignature:
        
    def __init__(self, beats_per_measure = 4, beats_per_note = 4):
        self._beats_per_measure = beats_per_measure
        self._beats_per_note = beats_per_note

    def getList(self):
        ...

    def loadList(self, json_list):
        ...

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

    def saveJson(self, json_list, filename):
        pass

    def loadJson(self, filename):
        pass

    def saveJsonPlay(self, json_list, filename):
        pass

