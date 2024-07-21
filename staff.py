
class Staff:

    def __init__(self, measures = 8):
        self._measures = measures

    def getData__measures(self):
        return self._measures

    def getList(self):
        ...

    def loadList(self, json_list):
        ...
        
    # CHAINED OPERATIONS


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

    # CHAINED OPERATIONS


class Tempo:
        
    def __init__(self, bpm = 120):
        self._bpm = bpm

    def getTime_ms(self, position_measure, displacement_note, time_signature = TimeSignature()):
        beat_time_ms = 60.0 * 1000 / self._bpm
        measure_time_ms = beat_time_ms * time_signature.getData__beats_per_measure()
        note_time_ms = beat_time_ms * time_signature.getData__beats_per_note()
        
        return position_measure * measure_time_ms + displacement_note * note_time_ms
        
    def getData__bpm(self):
        return self._bpm

    def getData__pulses_per_quarternote(self):
        return self._pulses_per_quarternote

    def getList(self):
        ...

    def loadList(self, json_list):
        ...

    # CHAINED OPERATIONS


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

    # CHAINED OPERATIONS


class Scale:

    def __init__(self, key = "C", scale = "Major"):
        self._key = key
        self._scale = scale

    def getData__key(self):
        return self._key

    def getData__scale(self):
        return self._scale
    
    def getSemitones(self, scale_steps, reference_key):
        ...
    
    # CHAINED OPERATIONS

    def setData__key(self, key):
        self._key = key
        return self

    def setData__scale(self, scale):
        self._scale = scale
        return self
    
