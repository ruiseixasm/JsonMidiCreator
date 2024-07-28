from staff import *


class Duration:
    
    def __init__(self, length = Length(note=1/4)):
        self._length: Length = length
    
    def getData__length(self):
        return self._length

    def is_eq(self, other_length):
        return self._length.is_eq(other_length)
    
    def is_lt(self, other_length):
        return self._length.is_lt(other_length)
    
    def is_gt(self, other_length):
        return self._length.is_gt(other_length)
    
    def is_le(self, other_length):
        return self._length.is_le(other_length)
    
    def is_ge(self, other_length):
        return self._length.is_ge(other_length)
    
    def getTime_ms(self):
        return self._length.getTime_ms()
        
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "length": self._length.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "length" in serialization):

            self._length = Length().loadSerialization(serialization["length"])

        return self
        
    def copy(self):
        return Duration(self._length.copy())

    # adding two durations 
    def __add__(self, other_duration):
        return Duration(self._length + other_duration.getData__length())
    
    # subtracting two durations 
    def __sub__(self, other_duration):
        return Duration(self._length - other_duration.getData__length())

    # multiply two durations 
    def __mul__(self, other_duration):
        return Duration(self._length * other_duration.getData__length())
    
    # multiply with a scalar
    def __rmul__(self, scalar: float):
        return Duration(scalar * self._length.getData__length())
    


class Position:

    def __init__(self, length = Length(0)):
        self._length: Length = length

    def getData__length(self):
        return self._length

    def is_eq(self, other_length):
        return self._length.is_eq(other_length)
    
    def is_lt(self, other_length):
        return self._length.is_lt(other_length)
    
    def is_gt(self, other_length):
        return self._length.is_gt(other_length)
    
    def is_le(self, other_length):
        return self._length.is_le(other_length)
    
    def is_ge(self, other_length):
        return self._length.is_ge(other_length)
    
    def getTime_ms(self):
        return self._length.getTime_ms()
        
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "length": self._length.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "length" in serialization):

            self._length = Length().loadSerialization(serialization["length"])

        return self
        
    def copy(self):
        return Position(self._length.copy())

    # adding two positions 
    def __add__(self, other_position):
        return Position(self._length + other_position.getData__length())
    
    # subtracting two positions 
    def __sub__(self, other_position):
        return Position(self._length - other_position.getData__length())

    # multiply two positions 
    def __mul__(self, other_position):
        return Position(self._length * other_position.getData__length())
    
    # multiply with a scalar
    def __rmul__(self, scalar: float):
        return Position(scalar * self._length.getData__length())
    


class Value:
    
    def __init__(self, value: int = 0):
        self._value: int = value


class Pitch:
    
    def __init__(self, pitch: int = 0):
        self._pitch: int = pitch

class Key:

    def __init__(self, key: str = 0):
        self._key: str = key


class Octave:

    def __init__(self, octave: int = 4):
        self._octave: int = octave


class KeyNote:
    
    def __init__(self, key: Key = Key(), octave: Octave = Octave()):
        self._key: Key = key
        self._octave: Octave = octave


class NoteOn:
    
    def __init__(self, note_on: int = 60):
        self._note_on: int = note_on

class Velocity:
    
    def __init__(self, velocity: int = 100):
        self._velocity: int = velocity

    def getData__velocity(self):
        return self._velocity

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "velocity": self._velocity
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "velocity" in serialization):

            self._velocity = serialization["velocity"]

        return self
        
    def copy(self):
        return Velocity(self._velocity)


class IntervalQuality:

    def __init__(self, interval_quality: str = 0):
        self._interval_quality: str = interval_quality

        # Augmented (designated as A or +)
        # Major (ma)
        # Perfect (P)
        # Minor (mi)
        # Diminished (d or o)

class Inversion:
    
    def __init__(self, inversion: int = 0):
        self._inversion: int = inversion



class Swing:

    def __init__(self, swing: float = 0):
        self._swing: float = swing



class Swing:

    def __init__(self, swing: float = 0.50):
        self._swing: float = swing


class Gate:

    def __init__(self, gate: float = 0.50):
        self._gate: float = gate

