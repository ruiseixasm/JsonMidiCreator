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
    
    # CHAINABLE OPERATIONS

    def setData__key(self, key):
        self._key = key
        return self

    def setData__scale(self, scale):
        self._scale = scale
        return self
    
class Length:
    
    def __init__(self, measures: float = 0, beats: float = 0, note: float = 0, steps: float = 0):
        self._measures = measures
        self._beats = beats
        self._note = note
        self._steps = steps

    def getData__measures(self):
        return self._measures

    def getData__beats(self):
        return self._beats

    def getData__note(self):
        return self._note

    def getData__steps(self):
        return self._steps

    def __eq__(self, other_length):
        return (self._measures, self._beats, self._note, self._steps) == \
               (other_length.getData__measures(),
                other_length.getData__beats(),
                other_length.getData__note(),
                other_length.getData__steps())
    
    # CHAINABLE OPERATIONS

    # adding two lengths 
    def __add__(self, other_length):
        return Length(
                self._measures + other_length.getData__measures(),
                self._beats + other_length.getData__beats(),
                self._note + other_length.getData__note(),
                self._steps + other_length.getData__steps()
            )
    
    # subtracting two lengths 
    def __sub__(self, other_length):
        return Length(
                self._measures - other_length.getData__measures(),
                self._beats - other_length.getData__beats(),
                self._note - other_length.getData__note(),
                self._steps - other_length.getData__steps()
            )
    
    # multiply two lengths 
    def __mul__(self, other_length):
        return Length(
                self._measures * other_length.getData__measures(),
                self._beats * other_length.getData__beats(),
                self._note * other_length.getData__note(),
                self._steps * other_length.getData__steps()
            )
    
    # multiply with a escalator 
    def __rmul__(self, number: float):
        return Length(
                self._measures * number,
                self._beats * number,
                self._note * number,
                self._steps * number
            )
    
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
    
    def getTime_ms(self, length: Length = Length(0, 0, 0, 0)):
        beat_time_ms = 60.0 * 1000 / self._tempo
        measure_time_ms = beat_time_ms * self.getValue__beats_per_measure()
        note_time_ms = beat_time_ms * self.getValue__beats_per_note()
        step_time_ms = note_time_ms / self.getValue__steps_per_note()
        
        return length.getData__measures() * measure_time_ms + length.getData__beats() * beat_time_ms \
                + length.getData__note() * note_time_ms + length.getData__steps() * step_time_ms
        
    def getList(self):
        ...

    def loadList(self, json_list):
        ...
        
    # CHAINABLE OPERATIONS

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

