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
import json
from typing import TypeVar
T = TypeVar('T')  # T can represent any type, including user-defined classes
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_frame as of


class Label(o.Operand):
    pass

class Null(Label):
    pass
    
class Dummy(Label):
    pass

class MidiValue(Label):
    pass

class MSB(MidiValue):
    """
    MSB() represents the Most Significant Byte.
    """
    pass

class LSB(MidiValue):
    """
    LSB() represents the Least Significant Byte.
    """
    pass

class Process(Label):
    def __init__(self, parameter: any = 0):
        super().__init__()
        self._parameter: any = parameter

class Copy(Process):
    """
    Copy() does an total duplication of the Operand including its parts.
    """
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(operand, o.Operand):
            return operand.copy()
        else:
            return super().__rrshift__(operand)

class Join(Process):
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.join()
        else:
            return super().__rrshift__(operand)

class Tie(Process):
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.tie()
        else:
            return super().__rrshift__(operand)

class Slur(Process):
    def __init__(self, gate: float = 1.0):
        super().__init__(gate)

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.slur(self._parameter)
        else:
            return super().__rrshift__(operand)

class Smooth(Process):
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.smooth()
        else:
            return super().__rrshift__(operand)

class Play(Process):
    """
    Play() allows to send a given Element to the Player directly without the need of Exporting to the respective .json Player file.
    
    Parameters
    ----------
    first : integer_like
        By default it's configured without any verbose, set to 1 or True to enable verbose
    """
    def __init__(self, verbose: bool = False):
        super().__init__(1 if verbose else 0)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case o.Operand():
                c.jsonMidiPlay(operand.getPlaylist(), False if self._parameter == 0 else True )
                return operand
            case _:
                return super().__rrshift__(operand)

class Print(Process):
    """
    Print() allows to get on the console the configuration of the source Operand in a JSON layout.
    
    Parameters
    ----------
    first : integer_like
        Sets the indent of the JSON print layout with the default as 4
    """
    def __init__(self, formatted: bool = True):
        super().__init__( 1 if formatted is None else formatted )

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case o.Operand():
                operand_serialization = operand.getSerialization()
                if self._parameter:
                    serialized_json_str = json.dumps(operand_serialization)
                    json_object = json.loads(serialized_json_str)
                    json_formatted_str = json.dumps(json_object, indent=4)
                    print(json_formatted_str)
                else:
                    print(operand_serialization)
            case tuple():
                return super().__rrshift__(operand)
            case _: print(operand)
        return operand

class Link(Process):
    def __init__(self, and_join: bool = False):
        super().__init__( 0 if and_join is None else and_join )
        
    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.link(bool(self._parameter))
        else:
            return super().__rrshift__(operand)

class Getter(Label):
    def __init__(self, parameter: int = 0):
        super().__init__()
        self._parameter: int = parameter

class Len(Getter):
    def get(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.len()
        return Null()

class First(Getter):
    def get(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.first()
        return Null()

class Last(Getter):
    def get(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.last()
        return Null()

class Middle(Getter):
    """
    Middle() represent the Nth Operand in a Container or Sequence.
    
    Parameters
    ----------
    first : integer_like
        The Nth Operand in a Container like 2 for the 2nd Operand
    """
    def __init__(self, nth: int = None):
        super().__init__( 1 if nth is None else nth )

    def get(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.middle(self._parameter)
        return Null()

class Start(Getter):
    def get(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.start()
        return Null()

class End(Getter):
    def get(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Sequence):
            return operand.end()
        return Null()

class Reverse(Getter):
    def get(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.reverse()
        return Null()
    
    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.reverse()
        else:
            return super().__rrshift__(operand)

class Name(Getter):
    pass
