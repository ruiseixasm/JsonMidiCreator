'''JsonMidiCreator - Json Midi Creator is intended to be used
in conjugation with the Json Midi Player to Play composed Elements
Original Copyright (c) 2024 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.'''
class Staff:

    def __init__(self, measures: int = 8,
                tempo: int = 120,
                quantization: float = 1/16,
                time_signature: list = [4, 4],
                duration_note: float = 1/4,
                key: str = "C",
                octave: int = 4,
                velocity: int = 100,
                channel: int = 1,
                device_list: list = ["FLUID", "Midi", "Port", "Synth"]):
        
        self._measures = measures
        self._tempo = tempo
        self._quantization = quantization
        self._time_signature = time_signature
        self._duration_note = duration_note
        self._key = key
        self._octave = octave
        self._velocity = velocity
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
    
    def getData__duration_note(self):
        return self._duration_note
    
    def getData__key(self):
        return self._key
    
    def getData__octave(self):
        return self._octave
    
    def getData__velocity(self):
        return self._velocity
    
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
            "time_signature": self._time_signature,
            "duration_note": 1/4,
            "key": "C",
            "octave": 4,
            "velocity": 100,
            "channel": 1,
            "device_list": ["FLUID", "Midi", "Port", "Synth"]
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measures" in serialization and "tempo" in serialization and
            "quantization" in serialization and "time_signature" in serialization and
            "duration_note" in serialization and "key" in serialization and
            "octave" in serialization and "velocity" in serialization and
            "channel" in serialization and "device_list" in serialization):

            self._measures = serialization["measures"]
            self._tempo = serialization["tempo"]
            self._quantization = serialization["quantization"]
            self._time_signature = serialization["time_signature"]
            self._duration_note = serialization["duration_note"]
            self._key = serialization["key"]
            self._octave = serialization["octave"]
            self._velocity = serialization["velocity"]
            self._channel = serialization["channel"]
            self._device_list = serialization["device_list"]

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

    def setData__duration_note(self, duration_note: float = 1/4):
        self._duration_note = duration_note
        return self
    
    def setData__key(self, key: str = "C"):
        self._key = key
        return self
    
    def setData__octave(self, octave: int = 4):
        self._octave = octave
        return self
    
    def setData__velocity(self, velocity: int = 100):
        self._velocity = velocity
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
    