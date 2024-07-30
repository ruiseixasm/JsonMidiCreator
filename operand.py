from staff import *

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
        return round(self.getTime_ms(), 3) == round(other_length.getTime_ms(), 3)
    
    def __lt__(self, other_length):
        return round(self.getTime_ms(), 3) < round(other_length.getTime_ms(), 3)
    
    def __gt__(self, other_length):
        return round(self.getTime_ms(), 3) > round(other_length.getTime_ms(), 3)
    
    def __le__(self, other_length):
        return not (self > other_length)
    
    def __ge__(self, other_length):
        return not (self < other_length)
    
    # Type hints as string literals to handle forward references
    def getTime_ms(self):

        on_staff = get_global_staff()

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
            "steps": self._steps
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

class Position(Length):

    def __init__(self, measures: float = 0, beats: float = 0, note: float = 0, steps: float = 0):
        super().__init__(measures, beats, note, steps)

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "length": super().getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        super().loadSerialization(serialization)

        return self
        
    def copy(self):
        return Position(self._measures, self._beats, self._note, self._steps)

    # adding two durations 
    def __add__(self, other_length: Length):
        return Position(
                self._measures + other_length.getData__measures(),
                self._beats + other_length.getData__beats(),
                self._note + other_length.getData__note(),
                self._steps + other_length.getData__steps(),
            )
    
    # subtracting two Positions 
    def __sub__(self, other_length: Length):
        return Position(
                self._measures - other_length.getData__measures(),
                self._beats - other_length.getData__beats(),
                self._note - other_length.getData__note(),
                self._steps - other_length.getData__steps(),
            )

    # multiply two Positions 
    def __mul__(self, scalar: float):
        return Position(
                self._measures * scalar,
                self._beats * scalar,
                self._note * scalar,
                self._steps * scalar
            )
    
    # multiply with a scalar
    def __rmul__(self, scalar: float):
        return self * scalar    

class Duration(Length):
    
    def __init__(self, measures: float = 0, beats: float = 0, note: float = 0, steps: float = 0):
        super().__init__(measures, beats, note, steps)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "length": super().getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        super().loadSerialization(serialization)

        return self
    
    def getDefault(self):
        return Duration(
            note=get_global_staff().getData__note_duration()
        )
        
    def copy(self):
        return Duration(self._measures, self._beats, self._note, self._steps)

    # adding two durations 
    def __add__(self, other_length: Length):
        return Duration(
                self._measures + other_length.getData__measures(),
                self._beats + other_length.getData__beats(),
                self._note + other_length.getData__note(),
                self._steps + other_length.getData__steps(),
            )
    
    # subtracting two durations 
    def __sub__(self, other_length: Length):
        return Duration(
                self._measures - other_length.getData__measures(),
                self._beats - other_length.getData__beats(),
                self._note - other_length.getData__note(),
                self._steps - other_length.getData__steps(),
            )

    # multiply two durations 
    def __mul__(self, scalar: float):
        return Duration(
                self._measures * scalar,
                self._beats * scalar,
                self._note * scalar,
                self._steps * scalar
            )
    
    # multiply with a scalar
    def __rmul__(self, scalar: float):
        return self * scalar

# Units have never None values (const, no setters)
class Unit:

    def __init__(self, unit: int = 0):
        self._unit: int = unit

    def getData(self):
        return self._unit
    
    # adding two positions
    def __add__(self, other_unit):
        return self._unit + other_unit.getData__unit()
    
    # subtracting two positions
    def __sub__(self, other_unit):
        return self._unit - other_unit.getData__unit()

    # multiply two positions
    def __mul__(self, other_unit):
        return self._unit * other_unit.getData__unit()
    
    # multiply with a scalar
    def __rmul__(self, scalar: float):
        return scalar * self._unit.getData__unit()
    
class Key(Unit):

    _keys: list[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
                        "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    
    @staticmethod
    def getKey(note_key: int = 0) -> str:
        return Key._keys[note_key % 12]

    @staticmethod
    def keyToKeyNumber(key: str) -> int:
        key_number = 0
        for key_i in range(len(Key._keys)):
            if key.lower() == Key._keys[key_i].lower():
                key_number += key_i % 12
                break
        return key_number

    def __init__(self, key: str = None):
        if key is None:
            super().__init__(None)
        else:
            super().__init__(Key.keyToKeyNumber(key))

    def getValue(self) -> str:
        if self._unit is None:
            return get_global_staff().getData__key()
        return Key.getKey(self._unit)

    def getValue_number(self) -> int:
        if self._unit is None:
            return Key(get_global_staff().getData__key()).getData()
        return self._unit

class Octave(Unit):

    def __init__(self, octave: int = None):
        super().__init__(octave)

    def getValue(self) -> str:
        if self._unit is None:
            return get_global_staff().getData__octave()
        return self._unit

class Velocity(Unit):
    
    def __init__(self, velocity: int = None):
        super().__init__(velocity)

    def getValue(self) -> str:
        if self._unit is None:
            return get_global_staff().getData__note_velocity()
        return self._unit

class Channel(Unit):

    def __init__(self, channel: int = None):
        super().__init__(channel)

    def getValue(self) -> str:
        if self._unit is None:
            return get_global_staff().getData__channel()
        return self._unit

class Pitch(Unit):
    
    def __init__(self, pitch: int = None):
        super().__init__(pitch)

    def getValue(self) -> str:
        if self._unit is None:
            return 0
        return self._unit


class KeyNote():

    def __init__(self, key: str = None, octave: int = None):
        self._key: Key = Key(key)
        self._octave: Octave = Octave(octave)

    def getValue__key(self):
        return self._key.getValue()

    def getValue__octave(self):
        return self._octave.getValue()

    def getValue__midi_key_note(self) -> int:
        key_number = self._key.getValue_number()
        octave = self._octave.getValue()
        return 12 * (octave + 1) + key_number
    
    # CHAINABLE OPERATIONS
    
    def getDefault(self):
        return KeyNote(
            get_global_staff().getData__key(),
            get_global_staff().getData__octave()
        )
        

    


class Range:

    def __init__(self, operand, position: Position = None, length: Length = None):
        self._position = position
        self._length = length
        self._operand = operand



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

