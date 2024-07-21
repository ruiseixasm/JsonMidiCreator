
class Staff:

    def __init__(self, measures = 8):
        self._measures = measures

    def getData__measures(self):
        return self._measures

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
        
    def getData__beats_per_measure(self):
        return self._beats_per_measure

    def getData__beats_per_note(self):
        return self._beats_per_note

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
        
        return  (pulses_per_measure * measure + pulses_per_note * notedivision) * 60.0 * 1000 / self._bpm / pulses_per_beat
        
    def getData__bpm(self):
        return self._bpm

    def getData__pulses_per_quarternote(self):
        return self._pulses_per_quarternote

    def getList(self):
        ...

    def loadList(self, json_list):
        ...

class Quantization:
        
    def __init__(self, steps_per_note = 16):
        self._steps_per_note = steps_per_note

    def getData__steps_per_note(self):
        return self._steps_per_note

    def noteDivisionFromSteps(self, steps):
        return steps / self._steps_per_note
        
    def getList(self):
        ...

    def loadList(self, json_list):
        ...

class Scale:

    def __init__(self, key = "C", scale = "Major"):
        self._key = key
        self._scale = scale

    def getData__key(self):
        return self._key

    def getData__scale(self):
        return self._scale
    


