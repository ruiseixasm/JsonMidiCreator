
from staff import *
# Example using typing.Union (compatible with Python < 3.10)
from typing import Union

class Operand:
    pass

class Empty(Operand):

    def __init__(self, operand: Operand):
        self._operand = operand

    def getOperand(self):
        return self._operand

class Length(Operand):
    
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
        
    def getLength(self) -> 'Length':
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

    def getDefault(self) -> 'Length':
        return Length(
            measures=get_global_staff().getData__measures()
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

    def getDefault(self) -> 'Position':
        return Position()

class Duration(Length):
    
    def __init__(self, measures: float = 0, beats: float = 0, note: float = 0, steps: float = 0):
        super().__init__(measures, beats, note, steps)
    
    # CHAINABLE OPERATIONS

    def getDefault(self) -> 'Duration':
        return Duration(
            note=get_global_staff().getData__duration_note()
        )


# Units have never None values and are also const, with no setters
class Unit(Operand):

    def __init__(self, unit: int = None):
        self._unit: int = None if unit is None else round(unit)

    def getData(self):
        return self._unit
    
    def getValue(self) -> int:
        if self._unit is None:
            return self.getDefault().getData()
        return self._unit
    
    def getDefault(self) -> 'Unit':
        return Unit(0)
        
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "unit": self._unit
        }

    def __eq__(self, other_unit: Union['Unit', int, float]) -> bool:
        if other_unit.__class__ == int or other_unit.__class__ == float: # Allows the direct comparison with a number
            return self.getValue() == other_unit
        return self.getValue() == other_unit.getValue()
    
    def __lt__(self, other_unit: Union['Unit', int, float]) -> bool:
        if other_unit.__class__ == int or other_unit.__class__ == float: # Allows the direct comparison with a number
            return self.getValue() < other_unit
        return self.getValue() < other_unit.getValue()
    
    def __gt__(self, other_unit: Union['Unit', int, float]) -> bool:
        if other_unit.__class__ == int or other_unit.__class__ == float: # Allows the direct comparison with a number
            return self.getValue() > other_unit
        return self.getValue() > other_unit.getValue()
    
    def __le__(self, other_unit: Union['Unit', int, float]) -> bool:
        return not (self > other_unit)
    
    def __ge__(self, other_unit: Union['Unit', int, float]) -> bool:
        return not (self < other_unit)
    
    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "unit" in serialization):

            self._unit = serialization["unit"]
        return self
        
    def __add__(self, other_unit: Union['Unit', int, float]) -> 'Unit':
        if other_unit.__class__ == int or other_unit.__class__ == float: # Allows the direct add of a number
            return self.__class__(self.getValue() + other_unit)
        return self.__class__(self.getValue() + other_unit.getValue())
    
    def __sub__(self, other_unit: Union['Unit', int, float]) -> 'Unit':
        if other_unit.__class__ == int or other_unit.__class__ == float:
            return self.__class__(self.getValue() - other_unit)
        return self.__class__(self.getValue() - other_unit.getValue())
    
    def __mul__(self, other_unit: Union['Unit', int, float]) -> 'Unit':
        if other_unit.__class__ == int or other_unit.__class__ == float:
            return self.__class__(self.getValue() * other_unit)
        return self.__class__(self.getValue() * other_unit.getValue())
    
    def __div__(self, other_unit: Union['Unit', int, float]) -> 'Unit':
        if other_unit.__class__ == int or other_unit.__class__ == float:
            return self.__class__(self.getValue() / other_unit)
        return self.__class__(self.getValue() / other_unit.getValue())
    
    def __rmul__(self, scalar: int | float) -> 'Unit':
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

    def getValue_str(self) -> str:
        return Key.getKey(self.getValue(self))

    def getDefault(self) -> 'Key':
        return Key(get_global_staff().getData__key())
        
class Octave(Unit):

    def __init__(self, octave: int = None):
        super().__init__(octave)

    def getDefault(self) -> 'Octave':
        return Octave(get_global_staff().getData__octave())
        
class Velocity(Unit):
    
    def __init__(self, velocity: int = None):
        super().__init__(velocity)

    def getDefault(self) -> 'Velocity':
        return Velocity(get_global_staff().getData__velocity())
        
class ValueUnit(Unit):

    def __init__(self, value: int = None):
        super().__init__(value)

    def getDefault(self) -> 'Value':
        return Value(64)    # 64 for Center
        
class Channel(Unit):

    def __init__(self, channel: int = None):
        super().__init__(channel)

    def getDefault(self) -> 'Channel':
        return Channel(get_global_staff().getData__channel())
        
class Pitch(Unit):
    
    def __init__(self, pitch: int = None):
        super().__init__(pitch)

    def getDefault(self) -> 'Pitch':
        return Pitch(0)

# Values have never None values and are also const, with no setters
class Value(Operand):

    def __init__(self, value: float = None):
        self._value: float = None if value is None else value

    def getData(self):
        return self._value
    
    def getValue(self) -> float:
        if self._value is None:
            return self.getDefault().getData()
        return self._value
    
    def getDefault(self) -> 'Value':
        return Value(0)
        
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "value": self._value
        }

    def __eq__(self, other_value: Union['Value', int, float]) -> bool:
        if other_value.__class__ == int or other_value.__class__ == float: # Allows the direct comparison with a number
            return self.getValue() == other_value
        return self.getValue() == other_value.getValue()
    
    def __lt__(self, other_value: Union['Value', int, float]) -> bool:
        if other_value.__class__ == int or other_value.__class__ == float: # Allows the direct comparison with a number
            return self.getValue() < other_value
        return self.getValue() < other_value.getValue()
    
    def __gt__(self, other_value: Union['Value', int, float]) -> bool:
        if other_value.__class__ == int or other_value.__class__ == float: # Allows the direct comparison with a number
            return self.getValue() > other_value
        return self.getValue() > other_value.getValue()
    
    def __le__(self, other_value: Union['Value', int, float]) -> bool:
        return not (self > other_value)
    
    def __ge__(self, other_value: Union['Value', int, float]) -> bool:
        return not (self < other_value)
    
    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "value" in serialization):

            self._value = serialization["value"]
        return self
        
    def __add__(self, other_value: Union['Value', int, float]) -> 'Value':
        if other_value.__class__ == int or other_value.__class__ == float: # Allows the direct add of a number
            return self.__class__(self.getValue() + other_value)
        return self.__class__(self.getValue() + other_value.getValue())
    
    def __sub__(self, other_value: Union['Value', int, float]) -> 'Value':
        if other_value.__class__ == int or other_value.__class__ == float:
            return self.__class__(self.getValue() - other_value)
        return self.__class__(self.getValue() - other_value.getValue())
    
    def __mul__(self, other_value: Union['Value', int, float]) -> 'Value':
        if other_value.__class__ == int or other_value.__class__ == float:
            return self.__class__(self.getValue() * other_value)
        return self.__class__(self.getValue() * other_value.getValue())
    
    def __div__(self, other_value: Union['Value', int, float]) -> 'Value':
        if other_value.__class__ == int or other_value.__class__ == float:
            return self.__class__(self.getValue() / other_value)
        return self.__class__(self.getValue() / other_value.getValue())
    
    def __rmul__(self, scalar: int | float) -> 'Value':
        return  self * scalar
    
class Measure(Value):

    def __init__(self, value: int = None):
        super().__init__(value)

    def getDefault(self) -> 'Measure':
        return Measure(0)
        
class Beat(Value):

    def __init__(self, value: int = None):
        super().__init__(value)

    def getDefault(self) -> 'Beat':
        return Beat(0)
        
class NoteValue(Value):

    def __init__(self, value: int = None):
        super().__init__(value)

    def getDefault(self) -> 'NoteValue':
        return NoteValue(0)
        
class Step(Value):

    def __init__(self, value: int = None):
        super().__init__(value)

    def getDefault(self) -> 'Step':
        return Step(0)
        
class Default():

    def __init__(self, unit: Unit):
        self._unit: Unit = unit

    def getData(self):
        return self._unit
        
    def getValue(self):
        return self._unit.getDefault().getValue()
        

class KeyNote(Operand):

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

    def getDefault(self) -> 'KeyNote':
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


# Read only class
class Device(Operand):

    def __init__(self, device_list: list[str] = None):
        self._device_list = device_list

    def getData(self):
        return self._device_list
    
    def getValue(self) -> list[str]:
        if self._device_list is None:
            return self.getDefault()
        return self._device_list

    def getDefault(self) -> 'Device':
        return Device(get_global_staff().getData__device_list())
    
class Range(Operand):

    def __init__(self, operand: Operand, position: Position = None, length: Length = None):
        self._operand = operand
        self._position = position
        self._length = length

class Repeat(Operand):
    
    def __init__(self, unit: Unit, repeat: int = 1):
        self._unit = unit
        self._repeat = repeat

    def step(self) -> Unit | Empty:
        if self._repeat > 0:
            self._repeat -= 1
            return self._unit
        return Empty(self._unit)

class Increment(Operand):
    """
    The Increment class initializes with a Unit and additional arguments,
    similar to the arguments in the range() function.

    Parameters:
    unit (Unit): The unit object.
    *argv (int): Additional arguments, similar to the range() function.

    The *argv works similarly to the arguments in range():
    - If one argument is provided, it's taken as the end value.
    - If two arguments are provided, they're taken as start and end.
    - If three arguments are provided, they're taken as start, end, and step.

    Increment usage:
    operand = Increment(unit, 8)
    operand = Increment(unit, 0, 10, 2)
    """

    def __init__(self, unit: Unit, *argv: int):
        """
        Initialize the Increment with a Unit and additional arguments.

        Parameters:
        unit (Unit): The unit object.
        *argv: Additional arguments, similar to the range() function.

        The *argv works similarly to the arguments in range():
        - If one argument is provided, it's taken as the end value.
        - If two arguments are provided, they're taken as start and end.
        - If three arguments are provided, they're taken as start, end, and step.

        Increment usage:
        operand = Increment(unit, 8)
        operand = Increment(unit, 0, 10, 2)
        """

        self._unit = unit
        self._start = 0
        self._stop = 0
        self._step = 1
        if len(argv) == 1:
            self._stop = argv[0]
        elif len(argv) == 2:
            self._start = argv[0]
            self._stop = argv[1]
        elif len(argv) == 3:
            self._start = argv[0]
            self._stop = argv[1]
            self._step = argv[2]
        else:
            raise ValueError("Increment requires 1, 2, or 3 arguments for the range.")

        self._iterator = self._start

    def step(self) -> Unit | Empty:
        if self._iterator < self._stop:
            self._unit += self._step
            self._iterator += 1
            return self._unit
        return Empty(self._unit)


class IntervalQuality(Operand):

    def __init__(self, interval_quality: str = 0):
        self._interval_quality: str = interval_quality

        # Augmented (designated as A or +)
        # Major (ma)
        # Perfect (P)
        # Minor (mi)
        # Diminished (d or o)

class Inversion(Operand):
    
    def __init__(self, inversion: int = 0):
        self._inversion: int = inversion


class Swing(Operand):

    def __init__(self, swing: float = 0):
        self._swing: float = swing


class Gate(Operand):

    def __init__(self, gate: float = 0.50):
        self._gate: float = gate

