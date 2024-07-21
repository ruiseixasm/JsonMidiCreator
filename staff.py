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
    
class Staff:

    def __init__(self, measures: int = 8,
                tempo: int = 120,
                quantization: float = 1/16,
                time_signature: list = [4, 4]):
        
        self._measures = measures
        self._tempo = tempo
        self._quantization = quantization
        self._time_signature = time_signature

    def getData__measures(self):
        return self._measures

    def getData__tempo(self):
        return self._tempo

    def getData__quantization(self):
        return self._quantization

    def getData__time_signature(self):
        return self._time_signature
    
    def getValue__steps_per_note(self):
        return round(1 / self._quantization, 6) # round avoids floating-point error
    
    def getValue__beats_per_measure(self):
        return self._time_signature[0]
    
    def getValue__beats_per_note(self):
        return self._time_signature[1]

    def getValue__notes_per_measure(self):
        return self.getValue__beats_per_measure() / self.getValue__beats_per_note()

    def getValue__steps_per_measure(self):
        return self.getValue__steps_per_note() * self.getValue__notes_per_measure()
    
    def getTime_ms(self, position_measure: float, displacement_beat: float = 0,
                   displacement_note: float = 0, displacement_step: float = 0):
        beat_time_ms = 60.0 * 1000 / self._tempo
        measure_time_ms = beat_time_ms * self.getValue__beats_per_measure()
        note_time_ms = beat_time_ms * self.getValue__beats_per_note()
        step_time_ms = note_time_ms / self.getValue__steps_per_note();
        
        return position_measure * measure_time_ms + displacement_beat * beat_time_ms \
                + displacement_note * note_time_ms + displacement_step * step_time_ms
        
    def getList(self):
        ...

    def loadList(self, json_list):
        ...
        
    # CHAINED OPERATIONS

    def setData__measures(self, measures: int = 8):
        self._measures = measures
        return self

    def setData__tempo(self, tempo: int = 120):
        self._tempo = tempo
        return self

    def setData__quantization(self, quantization: float = 1/16):
        self._quantization = quantization
        return self

    def setData__time_signature(self, time_signature: list = [4, 4]):
        self._time_signature = time_signature
        return self

