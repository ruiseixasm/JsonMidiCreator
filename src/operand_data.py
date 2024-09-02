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
import operand as o
import operand_staff as os
import operand_unit as ou
import operand_frame as of
import operand_label as ol
import operand_time as ot


class Data(o.Operand):
    def __init__(self, data = None):
        super().__init__()
        self._data = data

    def __mod__(self, operand: o.Operand):
        """
        The % symbol is used to extract a Parameter, because a Data has
        only one type of Parameters that's a generic type of Parameter
        it should be used in conjugation with Operand() to extract it.

        Examples
        --------
        >>> some_data = Data(Pitch(8191)) % Operand()
        >>> print(some_data)
        <operand_unit.Pitch object at 0x00000135E6437290>
        """
        match operand:
            case DataSource():
                match operand % o.Operand():
                    case of.Frame():                return self % DataSource( operand % o.Operand() )
                    case Data():                    return self
                    case ol.Null() | None:          return ol.Null()
                    case _:                         return self._data
            case of.Frame():                return self % (operand % o.Operand())
            case ol.Null() | None:          return ol.Null()
            case _:
                match self._data:
                    case o.Operand():
                        return self._data.copy()
                    case list():
                        many_operands: list = []
                        for single_operand in self._data:
                            match single_operand:
                                case o.Operand():
                                    many_operands.append(single_operand.copy())
                                case _:
                                    many_operands.append(single_operand)
                        return many_operands
                    case _: return self._data

    def __eq__(self, other_data: o.Operand) -> bool:
        if isinstance(other_data, Data):
            return self._data == other_data % DataSource()
        return False
    
    def __lt__(self, other_data: o.Operand) -> bool:
        if isinstance(other_data, Data):
            return self._data < other_data % DataSource()
        return False
    
    def __gt__(self, other_data: o.Operand) -> bool:
        if isinstance(other_data, Data):
            return self._data > other_data % DataSource()
        return False
    
    def __le__(self, other_data: o.Operand) -> bool:
        return self == other_data or self < other_data
    
    def __ge__(self, other_data: o.Operand) -> bool:
        return self == other_data or self > other_data

    def getSerialization(self):
        serialization = {
            "class": self.__class__.__name__,
            "parameters": {
                "data": self._data
            }
        }
        if isinstance(self._data, o.Operand):
            serialization["parameters"]["data"] = self._data.getSerialization()

        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "data" in serialization["parameters"]):

            self._data = serialization["parameters"]["data"]
            if isinstance(self._data, dict) and "class" in self._data and "parameters" in self._data:
                self._data      = o.Operand().loadSerialization(self._data)
        return self

    def __lshift__(self, operand: o.Operand) -> 'Data':
        if self._next_operand is not None and operand != self._next_operand:
            self << self._next_operand << operand
        else:
            match operand:
                case DataSource():      self._data = operand % o.Operand()
                case Data():
                    operand_data = operand % DataSource( o.Operand() )
                    match operand_data:
                        case o.Operand():
                            self._data = operand_data.copy()
                        case list():
                            many_operands: list = []
                            for single_operand in operand_data:
                                match single_operand:
                                    case o.Operand():
                                        many_operands.append(single_operand.copy())
                                    case _:
                                        many_operands.append(single_operand)
                            self._data = many_operands
                        case _:
                            self._data = operand_data
                case of.Frame():        self << (operand & self)
                case Serialization():
                    self.loadSerialization(operand % DataSource())
                case o.Operand():
                    self._data = self._data.copy()
                case list():
                    many_operands: list = []
                    for single_operand in operand:
                        match single_operand:
                            case o.Operand():
                                many_operands.append(single_operand.copy())
                            case _:
                                many_operands.append(single_operand)
                    self._data = many_operands
                case _: self._data = operand
        return self

class DataSource(Data):
    """
    DataSource() allows the direct extraction (%) or setting (<<)
    of the given Operand parameters without the normal processing.
    
    Parameters
    ----------
    first : Operand_like
        The Operand intended to be directly extracted or set

    Examples
    --------
    >>> single_note = Note()
    >>> position_source = single_note % DataSource( Position() )
    >>> position_copy = single_note % Position()
    >>> print(id(position_source))
    >>> print(id(position_copy))
    1941569818512
    1941604026545
    """
    def __init__(self, operand: o.Operand = None):
        super().__init__( o.Operand() if operand is None else operand )

    def __mod__(self, operand: o.Operand):
        """
        The % symbol will extract the data source value.

        Examples
        --------
        >>> data_source = DataSource( Position() )
        >>> print(data_source % Operand())
        <operand_time.Position object at 0x000001C4109E4F10>
        """
        return self._data
    
class SideEffects(Data):
    pass

class LeftShift(SideEffects):
    def __init__(self, operand: o.Operand):
        super().__init__( operand )

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(self._data, o.Operand):
            self._data << operand
        return operand

class RightShift(SideEffects):
    def __init__(self, operand: o.Operand):
        super().__init__( operand )

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(self._data, o.Operand):
            operand >> self._data
        return operand

class Scale(Data):
    """
    A Scale() represents a given scale rooted in the key of C.
    
    Parameters
    ----------
    first : integer_like and string_like
        It can have the name of a scale as input, like, "Major" or "Melodic"
    """
    def __init__(self, scale: list[int] | str | int = None):
        self_scale = __class__.get_scale(scale)
        if self_scale == []:
            self_scale = os.staff % DataSource( self ) % DataSource()
        super().__init__( self_scale.copy() )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, a Scale has many extraction modes
        one type of extraction is its list() type of Parameter representing a scale
        but it's also possible to extract the same scale on other Tonic() key based on C.

        Examples
        --------
        >>> tonic_a_scale = Scale([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]) % Tonic("A") % list()
        >>> print(tonic_a_scale)
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        """
        match operand:
            case DataSource():          return super().__mod__(operand)
            case list():                return self._data.copy()
            case str():                 return __class__.get_scale_name(self._data)
            case int():                 return __class__.get_scale_number(self._data)
            case ou.Transposition():    return self.transposition(operand % int())
            case ou.Modulation():       return self.modulation(operand % int())
            case _:                     return super().__mod__(operand)

    def keys(self) -> int:
        scale_keys = 0
        self_scale = self._data
        for key in self_scale:
            scale_keys += key
        return scale_keys

    def transposition(self, mode: int | str = "5th") -> int:
        transposition = 0
        mode_transpose = ou.Mode(mode) % DataSource() - 1
        while mode_transpose > 0:
            transposition += 1
            if self._data[transposition % 12]:
                mode_transpose -= 1
        return transposition

    def modulation(self, mode: int | str = "5th") -> list: # AKA as remode (remoding)
        self_scale = self._data.copy()
        transposition = self.transposition(mode)
        if transposition != 0:
            for key_i in range(12):
                self_scale[key_i] = self._data[(key_i + transposition) % 12]
        return self_scale

    # CHAINABLE OPERATIONS

    def modulate(self, mode: int | str = "5th") -> 'Scale': # AKA as remode (remoding)
        self._data = self.modulation(mode)
        return self

    def __lshift__(self, operand: any) -> 'Scale':
        if self._next_operand is not None and operand != self._next_operand:
            self << self._next_operand << operand
        else:
            match operand:
                case list() | str() | int():
                    self_scale = __class__.get_scale(operand)
                    if len(self_scale) == 12:
                        self._data = self_scale.copy()
                case _: super().__lshift__(operand)
        return self

    _names = [
        ["Chromatic", "chromatic"],
        # Diatonic Scales
        ["Major", "Maj", "maj", "M", "Ionian", "ionian", "C", "1", "1st", "First"],
        ["Dorian", "dorian", "D", "2", "2nd", "Second"],
        ["Phrygian", "phrygian", "E", "3", "3rd", "Third"],
        ["Lydian", "lydian", "F", "4", "4th", "Fourth"],
        ["Mixolydian", "mixolydian", "G", "5", "5th", "Fifth"],
        ["minor", "min", "m", "Aeolian", "aeolian", "A", "6", "6th", "Sixth"],
        ["Locrian", "locrian", "B", "7", "7th", "Seventh"],
        # Other Scales
        ["harmonic"],
        ["melodic"],
        ["octatonic_hw"],
        ["octatonic_wh"],
        ["pentatonic_maj", "Pentatonic"],
        ["pentatonic_min", "pentatonic"],
        ["diminished"],
        ["augmented"],
        ["blues"],
        ["Whole-tone", "Whole tone", "Whole"]
    ]
    _scales = [
    #       Db    Eb       Gb    Ab    Bb
    #       C#    D#       F#    G#    A#
    #    C     D     E  F     G     A     B
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        # Diatonic Scales
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],
        # Other Scales
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
        [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
        [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    ]

    @staticmethod
    def get_scale_number(scale: int | str | list = 0) -> int:
        match scale:
            case int():
                total_scales = len(__class__._scales)
                if scale >= 0 and scale < total_scales:
                    return scale
            case str():
                for scale_i in range(len(__class__._names)):
                    for scale_j in range(len(__class__._names[scale_i])):
                        if scale.strip() == __class__._names[scale_i][scale_j]:
                            return scale_i
            case list():
                if len(scale) == 12:
                    for scale_i in range(len(__class__._scales)):
                        if __class__._scales[scale_i] == scale:
                            return scale_i
        return -1

    @staticmethod
    def get_scale_name(scale: int | str | list = 0) -> str:
        scale_number = __class__.get_scale_number(scale)
        if scale_number < 0:
            return "Unknown Scale!"
        else:
            return __class__._names[scale_number][0]

    @staticmethod
    def get_scale(scale: int | str | list = 0) -> list:
        scale_number = __class__.get_scale_number(scale)
        if scale_number >= 0:
            return __class__._scales[scale_number]
        return []

class Device(Data):
    def __init__(self, device_list: list[str] = None):
        super().__init__( os.staff % DataSource( self ) % list() if device_list is None else device_list )

class Save(Data):
    def __init__(self, file_name: str = "json/_Save_jsonMidiCreator.json"):
        super().__init__(file_name)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        c.saveJsonMidiCreator(operand.getSerialization(), self % str())
        return operand

class Serialization(Data):
    def __init__(self, serialization: dict | o.Operand = None):
        if isinstance(serialization, o.Operand):
            self._data = serialization
        elif isinstance(serialization, dict) and "class" in serialization and "parameters" in serialization:
            operand_class_name = serialization["class"]
            operand = self.getOperand(operand_class_name)
            if operand:
                super().__init__( operand.loadSerialization(serialization) )
            else:
                super().__init__( ol.Null() )
        else:
            super().__init__( ol.Null() )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, for the case of a Load(),
        those Operands are pass right away to the self Data Operand, with the
        exception of "% Operand()", that returns the self Data operand.

        Examples
        --------
        >>> loaded_chord = Load("json/_Save_Chord_jsonMidiCreator.json")
        >>> print(loaded_chord % Type() % str())
        7th
        """
        if operand.__class__ == o.Operand:
            return self._data
        return self._data % operand

    def __eq__(self, other_operand: any) -> bool:
        match other_operand:
            case dict():
                return self._data.getSerialization() == other_operand
            case o.Operand():
                return self._data.getSerialization() == other_operand.getSerialization()
        return super().__eq__(other_operand)
    
    def getPlayList(self, position: ot.Position = None) -> dict:
        return self._data.getPlayList(position)

    def getSerialization(self) -> dict:
        return self._data.getSerialization()

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        self._data.loadSerialization(serialization)
        return self
        
    def copy(self):
        return self.__class__(self._data.copy()).loadSerialization( self.getSerialization() )

    def __lshift__(self, operand: o.Operand) -> 'o.Operand':
        if self._next_operand is not None and operand != self._next_operand:
            self << self._next_operand << operand
        else:
            self._data = operand.copy()
        return self

    def __rrshift__(self, operand) -> o.Operand:
        return operand >> self._data

    def __add__(self, operand: 'o.Operand') -> 'o.Operand':
        return self._data + operand

    def __sub__(self, operand: o.Operand) -> 'o.Operand':
        return self._data - operand

    def __mul__(self, operand: o.Operand) -> 'o.Operand':
        return self._data * operand

    def __truediv__(self, operand: o.Operand) -> 'o.Operand':
        return self._data / operand

    def __floordiv__(self, length: ot.Length) -> 'o.Operand':
        return self._data // length

class Load(Serialization):
    def __init__(self, file_name: str = None):
        match file_name:
            case str():
                super().__init__( c.loadJsonMidiCreator(file_name) )
            case _:
                super().__init__( ol.Null() )

class Export(Data):
    def __init__(self, file_name: str = "json/_Export_jsonMidiPlayer.json"):
        super().__init__(file_name)

    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        c.saveJsonMidiPlay(operand.getPlayList(), self % str())
        return operand

class PlayList(Data):
    def __init__(self, play_list: list = None):
        super().__init__( [] if play_list is None else play_list )

    def __mod__(self, operand: o.Operand) -> o.Operand:
        match operand:
            case ot.Position():
                if isinstance(self._data, ot.Position):
                    return self._data
                return None
            case _:                 return None

    def __eq__(self, other_operand: any) -> bool:
        match other_operand:
            case list():
                return self._data == other_operand
            case o.Operand():
                return self._data == other_operand.getPlayList()
        return super().__eq__(other_operand)
    
    def getPlayList(self) -> list:
        return PlayList.copyPlayList(self._data)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'PlayList':
        import operand_container as oc
        import operand_element as oe
        if self._next_operand is not None and operand != self._next_operand:
            self << self._next_operand << operand
        else:
            if isinstance(operand, (oc.Sequence, oe.Element, PlayList)):
                self._data = operand.getPlayList()
        return self

    def __rrshift__(self, operand) -> 'PlayList':
        import operand_container as oc
        import operand_element as oe
        if len(self._data) > 0 and isinstance(operand, (oc.Sequence, oe.Element, PlayList, ot.Position, ot.Length)):
            operand_play_list = operand.getPlayList()
            ending_position_ms = operand_play_list[0]["time_ms"]
            for midi_element in operand_play_list:
                if "time_ms" in midi_element and midi_element["time_ms"] > ending_position_ms:
                    ending_position_ms = midi_element["time_ms"]
            increase_position_ms = ending_position_ms
            if not isinstance(operand, ot.Length):
                starting_position_ms = self._data[0]["time_ms"]
                for midi_element in self._data:
                    if "time_ms" in midi_element and midi_element["time_ms"] < starting_position_ms:
                        starting_position_ms = midi_element["time_ms"]
                increase_position_ms = ending_position_ms - starting_position_ms
            for midi_element in self._data:
                if "time_ms" in midi_element:
                    midi_element["time_ms"] = round(midi_element["time_ms"] + increase_position_ms, 3)
        if isinstance(operand, (oc.Sequence, oe.Element, PlayList)):
            return operand + self
        else:
            return self.copy()

    def __add__(self, operand: o.Operand) -> 'PlayList':
        match operand:
            case ot.Length():
                playlist_copy = PlayList.copyPlayList(self._data)
                increase_position_ms: float = operand.getTime_ms()
                for midi_element in playlist_copy:
                    if "time_ms" in midi_element:
                        midi_element["time_ms"] = round(midi_element["time_ms"] + increase_position_ms, 3)
                return PlayList( playlist_copy )
            case list():        return PlayList( PlayList.copyPlayList(self._data) + PlayList.copyPlayList(operand) )
            case o.Operand():   return PlayList( PlayList.copyPlayList(self._data) + PlayList.copyPlayList(operand.getPlayList()) )
            case _:             return PlayList( PlayList.copyPlayList(self._data) )

    @staticmethod
    def copyPlayList(play_list: list[dict]) -> list[dict]:
        copy_play_list = []
        for single_dict in play_list:
            copy_play_list.append(single_dict.copy())
        return copy_play_list

class Import(PlayList):
    def __init__(self, file_name: str = None):
        super().__init__( [] if file_name is None else c.loadJsonMidiPlay(file_name) )

class Sort(Data):
    def __init__(self, compare: o.Operand = None):
        super().__init__(compare)

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        import operand_container as oc
        if isinstance(operand, oc.Container):
            return operand.sort()
        return operand

