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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from operand_staff import global_staff
# Json Midi Creator Libraries
from operand import *
from operand_unit import *
from operand_value import *


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
        from operand_staff import global_staff
        super().__init__()
        self << global_staff % self

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
  