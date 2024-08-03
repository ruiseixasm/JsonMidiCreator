
from staff import *
# Example using typing.Union (compatible with Python < 3.10)
from typing import Union

class Operand:
    def __pow__(self, operand: 'Operand') -> 'Operand':
        return self % operand

class Empty(Operand):
    def __init__(self, operand: Operand):
        self._operand = operand

    def getOperand(self):
        return self._operand


# Units have never None values and are also const, with no setters
class Unit(Operand):
    def __init__(self, unit: int = 0):
        self._unit: int = 0 if unit is None else round(unit)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case int():     return round(self._unit)
            case float():   return 1.0 * self._unit
            case _:         return operand

    def __eq__(self, other_unit: 'Unit') -> bool:
        return self % int() == other_unit % int()
    
    def __lt__(self, other_unit: 'Unit') -> bool:
        return self % int() < other_unit % int()
    
    def __gt__(self, other_unit: 'Unit') -> bool:
        return self % int() > other_unit % int()
    
    def __le__(self, other_unit: 'Unit') -> bool:
        return not (self > other_unit)
    
    def __ge__(self, other_unit: 'Unit') -> bool:
        return not (self < other_unit)
    
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

    def copy(self): # read only Operand doesn't have to be duplicated, it never changes
        return self

    def __add__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__(self % int() + unit % int())
            case int() | float(): return self.__class__(self % int() + unit)
    
    def __sub__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__(self % int() - unit % int())
            case int() | float(): return self.__class__(self % int() - unit)
        return self.__class__(self % int() - unit)
    
    def __mul__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__((self % int()) * (unit % int()))
            case int() | float(): return self.__class__(self % int() * unit)
    
    def __truediv__(self, unit: Union['Unit', int, float]) -> 'Unit':
        match unit:
            case Unit(): return self.__class__((self % int()) / (unit % int()))
            case int() | float(): return self.__class__(self % int() / unit)
    
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
        if key is None:
            key = get_global_staff().getData__key()
        match key:
            case str():
                super().__init__(Key.keyStrToKeyUnit(key))
            case int() | float():
                super().__init__(key)
            case _:
                super().__init__(None)

    def getData_str(self) -> str:
        return Key.getKey(self.getData(self))

class Octave(Unit):

    def __init__(self, octave: int = None):
        if octave is None:
            octave = get_global_staff().getData__octave()
        super().__init__(octave)

class Velocity(Unit):
    
    def __init__(self, velocity: int = None):
        if velocity is None:
            velocity = get_global_staff().getData__velocity()
        super().__init__(velocity)

class ValueUnit(Unit):

    def __init__(self, value_unit: int = None):
        if value_unit is None:
            value_unit = 64     # 64 for Center
        super().__init__(value_unit)

class Channel(Unit):

    def __init__(self, channel: int = None):
        if channel is None:
            channel = get_global_staff().getData__channel()
        super().__init__(channel)

class Pitch(Unit):
    
    def __init__(self, pitch: int = None):
        if pitch is None:
            pitch = 0
        super().__init__(pitch)

class KeyNote(Operand):

    def __init__(self):
        self._key: Key = Key()
        self._octave: Octave = Octave()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Key():     return self._key
            case Octave():  return self._octave
            case _:         return operand

    def getValue__key_str(self) -> str:
        return self._key.getData_str()

    def getValue__midi_key_note(self) -> int:
        key = self._key % int()
        octave = self._octave % int()
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
        return KeyNote() << self._key << self._octave

    def __lshift__(self, operand: Operand) -> 'KeyNote':
        if operand.__class__ == Key:    self._measure = operand
        if operand.__class__ == Octave: self._beat = operand
        return self

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


# Values have never None values and are also const, with no setters
class Value(Operand):

    def __init__(self, value: float = 0):
        self._value: float = 0 if value is None else value

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case float():   return 1.0 * self._value
            case int():     return round(self._value)
            case _:         return operand

    def __eq__(self, other_value: 'Value') -> bool:
        return self % int() == other_value % int()
    
    def __lt__(self, other_value: 'Value') -> bool:
        return self % int() < other_value % int()
    
    def __gt__(self, other_value: 'Value') -> bool:
        return self % int() > other_value % int()
    
    def __le__(self, other_value: 'Value') -> bool:
        return not (self > other_value)
    
    def __ge__(self, other_value: 'Value') -> bool:
        return not (self < other_value)
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "value": self._value
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "value" in serialization):

            self._value = serialization["value"]
        return self
        
    def copy(self): # read only Operand doesn't have to be duplicated, it never changes
        return self

    def __add__(self, value: Union['Value', float, int]) -> 'Value':
        match value:
            case Value(): return self.__class__(self % float() + value % float())
            case float() | int(): return self.__class__(self % float() + value)
    
    def __sub__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value(): return self.__class__(self % float() - value % float())
            case float() | int(): return self.__class__(self % float() - value)
        return self.__class__(self % float() - value)
    
    def __mul__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value(): return self.__class__((self % float()) * (value % float()))
            case float() | int(): return self.__class__(self % float() * value)
    
    def __truediv__(self, value: Union['Value', float]) -> 'Value':
        match value:
            case Value():
                if value % float() != 0:
                    return self.__class__((self % float()) / (value % float()))
            case float() | int():
                if value != 0:
                    return self.__class__(self % float() / value)
        return self.__class__()

class YieldValue(Value):
    def __init__(self, value: float = 0):
        super().__init__(value)

class Measure(Value):

    def __init__(self, value: float = 0):
        super().__init__(value)

    def getTime_ms(self):
        return Beat(1).getTime_ms() * get_global_staff().getValue__beats_per_measure() * self._value
     
class Beat(Value):

    def __init__(self, value: float = 0):
        super().__init__(value)

    def getTime_ms(self):
        return 60.0 * 1000 / get_global_staff().getData__tempo() * (self % float())
     
class NoteValue(Value):

    def __init__(self, value: float = 0):
        super().__init__(value)

    def getTime_ms(self):
        return Beat(1).getTime_ms() * get_global_staff().getValue__beats_per_note() * self._value
     
class Step(Value):

    def __init__(self, value: float = 0):
        super().__init__(value)

    def getTime_ms(self):
        return NoteValue(1).getTime_ms() / get_global_staff().getValue__steps_per_note() * self._value
     
class Length(Operand):
    
    def __init__(self):
        # Default values already, no need to wrap them with Default()
        self._measure       = Measure(0)
        self._beat          = Beat(0)
        self._note_value    = NoteValue(0)
        self._step          = Step(0)

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Measure():     return self._measure
            case Beat():        return self._beat
            case NoteValue():   return self._note_value
            case Step():        return self._step
            case _:             return operand

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
        return self._measure.getTime_ms() + self._beat.getTime_ms() \
                + self._note_value.getTime_ms() + self._step.getTime_ms()
        
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "measure": self._measure.getSerialization(),
            "beat": self._beat.getSerialization(),
            "note_value": self._note_value.getSerialization(),
            "step": self._step.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "measure" in serialization and "beat" in serialization and
            "note_value" in serialization and "step" in serialization):

            self._measure = Measure().loadSerialization(serialization["measure"])
            self._beat = Beat().loadSerialization(serialization["beat"])
            self._note_value = NoteValue().loadSerialization(serialization["note_value"])
            self._step = Step().loadSerialization(serialization["step"])

        return self
        
    def getLength(self) -> 'Length':
        return Length() << self._measure << self._beat << self._note_value << self._step

    def copy(self) -> 'Length':
        return self.__class__() << self._measure << self._beat << self._note_value << self._step

    def __lshift__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Measure(): self._measure = operand
            case Beat(): self._beat = operand
            case NoteValue(): self._note_value = operand
            case Step(): self._step = operand
            case Length():
                self._measure = operand % Measure()
                self._beat = operand % Beat()
                self._note_value = operand % NoteValue()
                self._step = operand % Step()
            case float() | int():
                self._measure = Measure(operand)
                self._beat = Beat(operand)
                self._note_value = NoteValue(operand)
                self._step = Step(operand)
        return self

    # adding two lengths 
    def __add__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Value():
                return self.__class__() << self % operand + operand
            case Length():
                return self.__class__() \
                    << self._measure + operand % Measure() \
                    << self._beat + operand % Beat() \
                    << self._note_value + operand % NoteValue() \
                    << self._step + operand % Step()
        return self.__class__()
    
    # subtracting two lengths 
    def __sub__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Value():
                return self.__class__() << self % operand - operand
            case Length():
                return self.__class__() \
                    << self._measure - operand % Measure() \
                    << self._beat - operand % Beat() \
                    << self._note_value - operand % NoteValue() \
                    << self._step - operand % Step()
        return self.__class__()
    
    def __mul__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Value():
                return self.__class__() << self % operand * operand
            case Length():
                return self.__class__() \
                    << self._measure * (operand % Measure()) \
                    << self._beat * (operand % Beat()) \
                    << self._note_value * (operand % NoteValue()) \
                    << self._step * (operand % Step())
        return self.__class__()
    
    def __truediv__(self, operand: Union[Value, 'Length']) -> 'Length':
        match operand:
            case Value():
                return self.__class__() << self % operand / operand
            case Length():
                return self.__class__() \
                    << self._measure / (operand % Measure()) \
                    << self._beat / (operand % Beat()) \
                    << self._note_value / (operand % NoteValue()) \
                    << self._step / (operand % Step())
        return self.__class__()

class Position(Length):
    def __init__(self):
        super().__init__()

class Duration(Length):
    def __init__(self):
        super().__init__()

class TimeLength(Length):
    def __init__(self):
        super().__init__()
    
class Identity(Length):
    
    def __init__(self):
        super().__init__()
        self._measure       = Measure(1)
        self._beat          = Beat(1)
        self._note_value    = NoteValue(1)
        self._step          = Step(1)
    
# Read only class
class Device(Operand):

    def __init__(self, device_list: list[str] = None):
        self._device_list: list[str] = get_global_staff().getData__device_list() \
                            if device_list is None else device_list

    def __mod__(self, operand: list) -> 'Device':
        match operand:
            case list(): return self._device_list
            case _: return self

    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "device_list": self._device_list
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "device_list" in serialization):

            self._device_list = serialization["device_list"]
        return self


class Inner(Operand):
    def __init__(self, operand: Operand):
        self._operand: Operand = operand

    def __mod__(self, operand: Operand) -> Operand:
        return self.getOperand()
    
    def getOperand(self):
        return self._operand

class Default(Operand):
    def __init__(self, operand: Operand):
        self._operand: Operand = operand

    def __mod__(self, operand: Operand) -> Operand:
        return self.getOperand()
    
    def getOperand(self):
        return self._operand

class Selection(Operand):
    
    def __init__(self, operand: Operand):
        self._position: Position = Position()
        self._time_length: TimeLength = TimeLength() << Measure(1)
        self._operand = operand

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case Position():
                return self._position
            case TimeLength():
                return self._time_length
            case Operand():
                return self._operand
        return self
    
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "position": self._position.getSerialization(),
            "time_length": self._time_length.getSerialization(),
            "operand": self._operand.getSerialization()
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Selection':
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and
            "position" in serialization and "time_length" in serialization and
            "operand" in serialization):

            self._position  = Position().loadSerialization(serialization["position"])
            self._time_length    = TimeLength().loadSerialization(serialization["length"])
            class_name = serialization["class"]
            self._operand   = globals()[class_name]().loadSerialization(serialization["operand"])
        return self

    def copy(self) -> 'Selection':
        return Selection((self % Operand()).copy()) << self._position.copy() << self._time_length.copy()

    def __lshift__(self, operand: Operand) -> 'Operand':
        match operand:
            case Position(): self._position = operand
            case TimeLength(): self._time_length = operand
            case Operand(): self._operand = operand
        return self
    

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

