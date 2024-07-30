class Staff:

    def __init__(self, measures: int = 8,
                tempo: int = 120,
                quantization: float = 1/16,
                time_signature: list = [4, 4],
                note_duration: float = 1/4,
                key: str = "C",
                octave: int = 4,
                note_velocity: int = 100,
                channel: int = 1,
                device_list: list = ["FLUID", "Midi", "Port", "Synth"]):
        
        self._measures = measures
        self._tempo = tempo
        self._quantization = quantization
        self._time_signature = time_signature
        self._note_duration = note_duration
        self._key = key
        self._octave = octave
        self._note_velocity = note_velocity
        self._channel = channel
        self._device_list = device_list

    def getData__measures(self):
        return self._measures

    def getData__tempo(self):
        return self._tempo

    def getData__quantization(self):
        return self._quantization

    def getData__time_signature(self):
        return self._time_signature
    
    def getData__note_duration(self):
        return self._note_duration
    
    def getData__key(self):
        return self._key
    
    def getData__octave(self):
        return self._octave
    
    def getData__note_velocity(self):
        return self._note_velocity
    
    def getData__channel(self):
        return self._channel
    
    def getData__device_list(self):
        return self._device_list
    
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

    def setData__note_duration(self, note_duration: float = 1/4):
        self._note_duration = note_duration
        return self
    
    def setData__key(self, key: str = "C"):
        self._key = key
        return self
    
    def setData__octave(self, octave: int = 4):
        self._octave = octave
        return self
    
    def setData__note_velocity(self, note_velocity: int = 100):
        self._note_velocity = note_velocity
        return self
    
    def setData__channel(self, channel: int = 1):
        self._channel = channel
        return self
    
    def setData__device_list(self, device_list: list = ["FLUID", "Midi", "Port", "Synth"]):
        self._device_list = device_list
        return self
    
global_staff: Staff = Staff()

def get_global_staff():
    if global_staff is not None and isinstance(global_staff, Staff):
        return global_staff
    print("Global Staff NOT defined!")
    return Staff()

def set_global_staff(staff: Staff = Staff()):
    global global_staff     # Declares it as global variable
    global_staff = staff
    return global_staff

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
    