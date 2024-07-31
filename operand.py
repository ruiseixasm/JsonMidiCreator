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

    def getValue__measures(self) -> int:
        if self._measures is None:
            return 0
        return self._measures

    def getValue__beats(self) -> int:
        if self._beats is None:
            return 0
        return self._beats

    def getValue__note(self) -> int:
        if self._note is None:
            return 0
        return self._note

    def getValue__steps(self) -> int:
        if self._steps is None:
            return 0
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
        
    def getLength(self):
        return Length(
            measures    = self._measures,
            beats       = self._measures,
            note        = self._note,
            steps       = self._note
        )

    def copy(self) -> 'Length':
        return self.__class__(
                measures    = self._measures,
                beats       = self._beats,
                note        = self._note,
                steps       = self._steps
            )

    # adding two lengths 
    def __add__(self, other_length) -> 'Length':
        return self.__class__(
                self._measures + other_length.getData__measures(),
                self._beats + other_length.getData__beats(),
                self._note + other_length.getData__note(),
                self._steps + other_length.getData__steps()
            )
    
    # subtracting two lengths 
    def __sub__(self, other_length) -> 'Length':
        return self.__class__(
                self._measures - other_length.getData__measures(),
                self._beats - other_length.getData__beats(),
                self._note - other_length.getData__note(),
                self._steps - other_length.getData__steps()
            )
    
    # multiply with a scalar 
    def __mul__(self, scalar: float) -> 'Length':
        return self.__class__(
                self._measures * scalar,
                self._beats * scalar,
                self._note * scalar,
                self._steps * scalar
            )
    
    # multiply with a scalar 
    def __rmul__(self, scalar: float) -> 'Length':
        return self * scalar
    
    # multiply with a scalar 
    def __div__(self, scalar: float) -> 'Length':
        if (scalar != 0):
            return self.__class__(
                    self._measures / scalar,
                    self._beats / scalar,
                    self._note / scalar,
                    self._steps / scalar
                )
        return self.__class__(
                self._measures,
                self._beats,
                self._note,
                self._steps
            )

class Position(Length):

    def __init__(self, measures: float = 0, beats: float = 0, note: float = 0, steps: float = 0):
        super().__init__(measures, beats, note, steps)

    # CHAINABLE OPERATIONS

    def getDefault(self):
        return Duration()
        

class Duration(Length):
    
    def __init__(self, measures: float = 0, beats: float = 0, note: float = 0, steps: float = 0):
        super().__init__(measures, beats, note, steps)
    
    # CHAINABLE OPERATIONS

    def getDefault(self):
        return Duration(
            note=get_global_staff().getData__duration_note()
        )


# Units have never None values and are also const, with no setters
class Unit:

    def __init__(self, unit: int = 0):
        self._unit: int = None if unit is None else round(unit)

    def getData(self):
        return self._unit
    
    def getValue(self) -> int:
        if self._unit is None:
            return 0
        return self._unit
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "unit": self._unit
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "unit" in serialization):

            self._unit = serialization["unit"]
        return self
        
    def __add__(self, other_unit: 'Unit') -> 'Unit':
        if other_unit.__class__ == int or other_unit.__class__ == float:
            return self.__class__(self.getValue() + other_unit)
        return self.__class__(self.getValue() + other_unit.getValue())
    
    def __sub__(self, other_unit: 'Unit') -> 'Unit':
        if other_unit.__class__ == int or other_unit.__class__ == float:
            return self.__class__(self.getValue() - other_unit)
        return self.__class__(self.getValue() - other_unit.getValue())
    
    def __mul__(self, other_unit: 'Unit') -> 'Unit':
        if other_unit.__class__ == int or other_unit.__class__ == float:
            return self.__class__(self.getValue() * other_unit)
        return self.__class__(self.getValue() * other_unit.getValue())
    
    def __div__(self, other_unit: 'Unit') -> 'Unit':
        if other_unit.__class__ == int or other_unit.__class__ == float:
            return self.__class__(self.getValue() / other_unit)
        return self.__class__(self.getValue() / other_unit.getValue())
    
    def __rmul__(self, scalar: float) -> 'Unit':
        return  self * scalar
    
class Key(Unit):

    _keys: list[str] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
                        "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    
    @staticmethod
    def getKey(note_key: int = 0) -> str:
        return Key._keys[note_key % 12]

    @staticmethod
    def keyStrToKeyUnit(key: str = "C") -> int:
        key_number = 0
        for key_i in range(len(Key._keys)):
            if  Key._keys[key_i].lower().find(key.strip().lower()) != -1:
                key_number += key_i % 12
                break
        return key_number

    def __init__(self, key: str = None):

        match key:
            case str():
                super().__init__(Key.keyStrToKeyUnit(key))
            case int() | float():
                super().__init__(key)
            case _:
                super().__init__(None)

    def getValue(self) -> int:
        if self._unit is None:
            return Key(get_global_staff().getData__key()).getData()
        return self._unit

    def getValue_str(self) -> str:
        return Key.getKey(self.getValue(self))

class Octave(Unit):

    def __init__(self, octave: int = None):
        super().__init__(octave)

    def getValue(self) -> int:
        if self._unit is None:
            return get_global_staff().getData__octave()
        return self._unit

class Velocity(Unit):
    
    def __init__(self, velocity: int = None):
        super().__init__(velocity)

    def getValue(self) -> int:
        if self._unit is None:
            return get_global_staff().getData__velocity()
        return self._unit

class Value(Unit):

    def __init__(self, value: int = None):
        super().__init__(value)

    def getValue(self) -> int:
        if self._unit is None:
            return 64   # Center
        return self._unit

class Channel(Unit):

    def __init__(self, channel: int = None):
        super().__init__(channel)

    def getValue(self) -> int:
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

    def __init__(self, key: str | int = None, octave: int = None):
        self._key: Key = Key(key)
        self._octave: Octave = Octave(octave)

    def getValue__key(self) -> int:
        return self._key.getValue()
    
    def getValue__key_str(self) -> str:
        return self._key.getValue_str()

    def getValue__octave(self) -> int:
        return self._octave.getValue()

    def getValue__midi_key_note(self) -> int:
        key = self._key.getValue()
        octave = self._octave.getValue()
        return 12 * (octave + 1) + key
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "key": self._key.getSerialization(),
            "octave": self._octave.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "key" in serialization and "octave" in serialization):

            self._key = Key().loadSerialization(serialization["key"])
            self._octave = Octave().loadSerialization(serialization["octave"])
        return self
        
    def copy(self) -> 'KeyNote':
        return self.__class__(
                self._key,
                self._octave
            )

    def getDefault(self):
        return KeyNote(
            get_global_staff().getData__key(),
            get_global_staff().getData__octave()
        )
        
    def __add__(self, unit) -> 'KeyNote':
        key: Key = self._key
        octave: Octave = self._octave
        match unit:
            case Key():
                key += unit
            case Octave():
                octave += unit
            case _:
                return self.copy()

        return KeyNote(
            key     = key.getData(),
            octave  = octave.getData()
        )
     
    def __sub__(self, unit) -> 'KeyNote':
        key: Key = self._key
        octave: Octave = self._octave
        match unit:
            case Key():
                key -= unit
            case Octave():
                octave -= unit
            case _:
                return self.copy()

        return KeyNote(
            key     = key.getData(),
            octave  = octave.getData()
        )
     
    # def __rshift__(self, semitones: int) -> 'KeyNote':
    #     return self.copy().setData__position(self.getValue__position() + length)

    # def __lshift__(self, semitones: int) -> 'KeyNote':
    #     return self.copy().setData__position(self.getValue__position() - length)

    


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

