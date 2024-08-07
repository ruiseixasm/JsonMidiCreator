'''
JsonMidiCreator - Json Midi Creator is intended to be used
in conjugation with the Json Midi Player to Play composed Elements
Original Copyright (c) 2024 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
https://github.com/ruiseixasm/JsonMidiCreator
https://github.com/ruiseixasm/JsonMidiPlayer
'''
# Example using typing.Union (compatible with Python < 3.10)
from typing import Union
# Json Midi Creator Libraries
from operand import Operand
import operand_staff as os
import operand_unit as ou


# Values have never None values and are also const, with no setters
class Value(Operand):
    def __init__(self, value: float = None):
        self._value: float = 0.0
        self._value = os.global_staff % self % float() if value is None else round(1.0 * value, 9)  # rounding to 9 avoids floating-point errors

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case float():   return round(1.0 * self._value, 9)  # rounding to 9 avoids floating-point errors
            case int():     return round(self._value)
            case _:         return operand

    def __eq__(self, other_value: 'Value') -> bool:
        return self % float() == other_value % float()
    
    def __lt__(self, other_value: 'Value') -> bool:
        return self % float() < other_value % float()
    
    def __gt__(self, other_value: 'Value') -> bool:
        return self % float() > other_value % float()
    
    def __le__(self, other_value: 'Value') -> bool:
        return not (self > other_value)
    
    def __ge__(self, other_value: 'Value') -> bool:
        return not (self < other_value)
    
    # CHAINABLE OPERATIONS

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

class Quantization(Value):
    def __init__(self, quantization: float = None):
        super().__init__(quantization)

class BeatsPerMeasure(Value):
    def __init__(self, beats_per_measure: float = None):
        super().__init__(beats_per_measure)

class BeatNoteValue(Value):
    def __init__(self, beat_note_value: float = None):
        super().__init__(beat_note_value)

class NotesPerMeasure(Value):
    def __init__(self, notes_per_measure: float = None):
        super().__init__(notes_per_measure)

class StepsPerMeasure(Value):
    def __init__(self, steps_per_measure: float = None):
        super().__init__(steps_per_measure)

class StepsPerNote(Value):
    def __init__(self, steps_per_note: float = None):
        super().__init__(steps_per_note)

class Tempo(Value):
    def __init__(self, tempo: int = None):
        super().__init__(tempo)

class TimeUnit(Value):
    def __init__(self, value: float = None):
        super().__init__(value)

class Measure(TimeUnit):
    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return Beat(1).getTime_ms() * (os.global_staff % BeatsPerMeasure() % float()) * self._value
     
class Beat(TimeUnit):
    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return 60.0 * 1000 / (os.global_staff % Tempo() % float()) * self._value
    
class NoteValue(TimeUnit):
    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return Beat(1).getTime_ms() / (os.global_staff % BeatNoteValue() % float()) * self._value
     
class Step(TimeUnit):
    def __init__(self, value: float = None):
        super().__init__(value)

    def getTime_ms(self):
        return NoteValue(1).getTime_ms() / (os.global_staff % StepsPerNote() % float()) * self._value
    

class Swing(Value):
    def __init__(self, swing: float = 0):
        super().__init__(swing)


class Gate(Value):
    def __init__(self, gate: float = 0.50):
        super().__init__(gate)

