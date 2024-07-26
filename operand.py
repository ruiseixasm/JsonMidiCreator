import staff


class Duration:
    
    def __init__(self, duration = staff.Length()):
        self._duration: staff.Length = duration



class Position:

    def __init__(self, position = staff.Length()):
        self._position: staff.Length = position



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
    
    def __init__(self, note_on: int = 0):
        self._note_on: int = note_on

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


