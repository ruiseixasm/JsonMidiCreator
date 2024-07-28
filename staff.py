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
        return round(1 / self._quantization, 9) # round avoids floating-point error
    
    def getValue__beats_per_measure(self):
        return self._time_signature[0]
    
    def getValue__beats_per_note(self):
        return self._time_signature[1]

    def getValue__notes_per_measure(self):
        return self.getValue__beats_per_measure() / self.getValue__beats_per_note()

    def getValue__steps_per_measure(self):
        return self.getValue__steps_per_note() * self.getValue__notes_per_measure()
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "measures": self._measures,
            "tempo": self._tempo,
            "quantization": self._quantization,
            "time_signature": self._time_signature
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measures" in serialization and "tempo" in serialization and
            "quantization" in serialization and "time_signature" in serialization):

            self._measures = serialization["measures"]
            self._tempo = serialization["tempo"]
            self._quantization = serialization["quantization"]
            self._time_signature = serialization["time_signature"]

        return self
        
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

global_staff: Staff = Staff()

def get_global_staff():
    if global_staff is not None and isinstance(global_staff, Staff):
        return global_staff
    print("Global Staff NOT definned!")
    return Staff()

def set_global_staff(staff: Staff = Staff()):
    global_staff = staff

class Length:
    
    def __init__(self, measures: float = 0, beats: float = 0, note: float = 0, steps: float = 0,
                 staff: Staff = None):
        self._measures = measures
        self._beats = beats
        self._note = note
        self._steps = steps
        self._staff: Staff = staff

    def getData__measures(self):
        return self._measures

    def getData__beats(self):
        return self._beats

    def getData__note(self):
        return self._note

    def getData__steps(self):
        return self._steps

    def is_eq(self, other_length, staff: Staff = None):
        return round(self.getTime_ms(staff), 3) == round(other_length.getTime_ms(staff), 3)
    
    def is_lt(self, other_length, staff: Staff = None):
        return round(self.getTime_ms(staff), 3) < round(other_length.getTime_ms(staff), 3)
    
    def is_gt(self, other_length, staff: Staff = None):
        return round(self.getTime_ms(staff), 3) > round(other_length.getTime_ms(staff), 3)
    
    def is_le(self, other_length, staff: Staff = None):
        return not self.is_gt(other_length, staff)
    
    def is_ge(self, other_length, staff: Staff = None):
        return not self.is_lt(other_length, staff)
    
    # Type hints as string literals to handle forward references
    def getTime_ms(self, staff: Staff = None):

        on_staff = get_global_staff()
        if (self._staff is not None):
            on_staff = self._staff
        elif (staff is not None):
            on_staff = staff

        beat_time_ms = 60.0 * 1000 / on_staff.getData__tempo()
        measure_time_ms = beat_time_ms * on_staff.getValue__beats_per_measure()
        note_time_ms = beat_time_ms * on_staff.getValue__beats_per_note()
        step_time_ms = note_time_ms / on_staff.getValue__steps_per_note()
        
        return self._measures * measure_time_ms + self._beats * beat_time_ms \
                + self._note * note_time_ms + self._steps * step_time_ms
        
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "measures": self._measures,
            "beats": self._beats,
            "note": self._note,
            "steps": self._steps,
            "staff": None if self._staff is None else self._staff.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measures" in serialization and "beats" in serialization and
            "note" in serialization and "steps" in serialization):

            self._measures = serialization["measures"]
            self._beats = serialization["beats"]
            self._note = serialization["note"]
            self._steps = serialization["steps"]
            self._staff = None if serialization["staff"] is None else Staff().loadSerialization(serialization["staff"])

        return self
        
    def copy(self):
        return Length(
                self._measures,
                self._beats,
                self._note,
                self._steps
            )

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
    
    # multiply with a scalar 
    def __mul__(self, scalar: float):
        return Length(
                self._measures * scalar,
                self._beats * scalar,
                self._note * scalar,
                self._steps * scalar
            )
    
    # multiply with a scalar 
    def __rmul__(self, scalar: float):
        return self * scalar
    
    # multiply with a scalar 
    def __div__(self, scalar: float):
        if (scalar != 0):
            return Length(
                    self._measures / scalar,
                    self._beats / scalar,
                    self._note / scalar,
                    self._steps / scalar
                )
        return Length(
                self._measures,
                self._beats,
                self._note,
                self._steps
            )
    
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
    