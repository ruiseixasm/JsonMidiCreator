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
from fractions import Fraction
# Json Midi Creator Libraries
import creator as c
from operand import Operand
import operand_staff as os
import operand_value as ov
import operand_frame as of
import operand_label as ol


class Time(Operand):
    def __init__(self):
        # Default values already, no need to wrap them with Default()
        self._measure       = ov.Measure()
        self._beat          = ov.Beat()
        self._note_value    = ov.NoteValue()
        self._step          = ov.Step()

    def __mod__(self, operand: Operand) -> Operand:
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case ov.Measure():      return self._measure
            case ov.Beat():         return self._beat
            case ov.NoteValue():    return self._note_value
            case ov.Step():         return self._step
            case ol.Null() | None:  return ol.Null()
            case _:                 return self

    def __eq__(self, other_length):
        return self.getTime_rational() == other_length.getTime_rational()
    
    def __lt__(self, other_length):
        return self.getTime_rational() < other_length.getTime_rational()
    
    def __gt__(self, other_length):
        return self.getTime_rational() > other_length.getTime_rational()
    
    def __le__(self, other_length):
        return not (self > other_length)
    
    def __ge__(self, other_length):
        return not (self < other_length)
    
    def getTime_rational(self) -> Fraction:
        return self._measure.getTime_rational() + self._beat.getTime_rational() \
                + self._note_value.getTime_rational() + self._step.getTime_rational()
        
    def getTime_ms(self) -> float:
        # int * float results in a float
        # Fraction * float results in a float
        # Fraction * Fraction results in a Fraction
        return round(1.0 * self.getTime_rational(), 3)
        
    def getSerialization(self):
        return {
            "class": self.__class__.__name__,
            "parameters": {
                "measure": self._measure % float(),
                "beat": self._beat % float(),
                "note_value": self._note_value % float(),
                "step": self._step % float()
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "measure" in serialization["parameters"] and "beat" in serialization["parameters"] and
            "note_value" in serialization["parameters"] and "step" in serialization["parameters"]):

            self._measure = ov.Measure(serialization["parameters"]["measure"])
            self._beat = ov.Beat(serialization["parameters"]["beat"])
            self._note_value = ov.NoteValue(serialization["parameters"]["note_value"])
            self._step = ov.Step(serialization["parameters"]["step"])

        return self
        
    def copy(self) -> 'Time':
        return self.__class__() << self._measure.copy() << self._beat.copy() << self._note_value.copy() << self._step.copy()

    def __lshift__(self, operand: Operand) -> 'Time':
        match operand:
            case of.Frame():        self << (operand & self)
            case Time():
                self._measure       = operand % ov.Measure()
                self._beat          = operand % ov.Beat()
                self._note_value    = operand % ov.NoteValue()
                self._step          = operand % ov.Step()
            case ov.Measure():      self._measure = operand
            case ov.Beat():         self._beat = operand
            case ov.NoteValue():    self._note_value = operand
            case ov.Step():         self._step = operand
            case Fraction() | float() | int():
                self._measure       = ov.Measure(operand)
                self._beat          = ov.Beat(operand)
                self._note_value    = ov.NoteValue(operand)
                self._step          = ov.Step(operand)
        return self

    # adding two lengths 
    def __add__(self, operand: Operand) -> 'Time':
        self_copy = self.copy()
        match operand:
            case of.Frame():        return self + (operand & self)
            case Time():            self_copy \
                                        << self._measure + operand % ov.Measure() \
                                        << self._beat + operand % ov.Beat() \
                                        << self._note_value + operand % ov.NoteValue() \
                                        << self._step + operand % ov.Step()
            case ov.TimeUnit():     self_copy << self % operand + operand
        return self_copy
    
    # subtracting two lengths 
    def __sub__(self, operand: Operand) -> 'Time':
        self_copy = self.copy()
        match operand:
            case of.Frame():        return self - (operand & self)
            case Time():            self_copy \
                                        << self._measure - operand % ov.Measure() \
                                        << self._beat - operand % ov.Beat() \
                                        << self._note_value - operand % ov.NoteValue() \
                                        << self._step - operand % ov.Step()
            case ov.TimeUnit():     self_copy << self % operand - operand
        return self_copy
    
    def __mul__(self, operand: Operand) -> 'Time':
        self_copy = self.copy()
        match operand:
            case of.Frame():        return self * (operand & self)
            case Time():            self_copy \
                                        << self._measure * (operand % ov.Measure()) \
                                        << self._beat * (operand % ov.Beat()) \
                                        << self._note_value * (operand % ov.NoteValue()) \
                                        << self._step * (operand % ov.Step())
            case ov.TimeUnit():     self_copy << self % operand * operand
            case ov.Value() | Fraction() | float() | int():
                self_copy << self._measure * operand << self._beat * operand \
                          << self._note_value * operand << self._step * operand
        return self_copy
    
    def __rmul__(self, operand: Operand) -> 'Time':
        return self * operand
    
    def __truediv__(self, operand: Operand) -> 'Time':
        self_copy = self.copy()
        match operand:
            case of.Frame():        return self / (operand & self)
            case Time():            self_copy \
                                        << self._measure / (operand % ov.Measure()) \
                                        << self._beat / (operand % ov.Beat()) \
                                        << self._note_value / (operand % ov.NoteValue()) \
                                        << self._step / (operand % ov.Step())
            case ov.TimeUnit():     self_copy << self % operand / operand
            case ov.Value() | Fraction() | float() | int():
                self_copy << self._measure / operand << self._beat / operand \
                          << self._note_value / operand << self._step / operand
        return self_copy

    def __rtruediv__(self, operand: Operand) -> 'Time':
        return self / operand
    
class Position(Time):
    def __init__(self, step: float = None):
        super().__init__()
        if step is not None:
            self._step = ov.Step(step)

    def start(self) -> 'Position':
        return self

    def end(self) -> 'Position':
        return self

class Duration(Time):
    def __init__(self, note_value: float = None):
        super().__init__()
        if note_value is not None:
            self._note_value = ov.NoteValue(note_value)

class Length(Time):
    def __init__(self, note_value: float = None):
        super().__init__()
        if note_value is not None:
            self._note_value = ov.NoteValue(note_value)
    
class Identity(Time):
    def __init__(self):
        self._measure       = ov.Measure(1)
        self._beat          = ov.Beat(1)
        self._note_value    = ov.NoteValue(1)
        self._step          = ov.Step(1)
  