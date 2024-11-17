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

    # def __init__(self, *parameters):
    #     super().__init__()
    #     self._data = None
    #     if len(parameters) > 0:
    #         self << parameters

    def __mod__(self, operand: o.Operand):
        """
        The % symbol is used to extract a Parameter, because a Data has
        only one type of Parameters that's a generic type of Parameter
        it should be used in conjugation with Operand() to extract it.

        Examples
        --------
        >>> some_data = Data(Bend(8191))
        >>> some_data % Operand() >> Print(0)
        {'class': 'Bend', 'parameters': {'unit': 8191}}
        """
        match operand:
            case DataSource():
                match operand % o.Operand():
                    case of.Frame():                return self % DataSource( operand % o.Operand() )
                    case Data():                    return self
                    case ol.Null() | None:          return ol.Null()
                    case _:                         return self._data
            case of.Frame():                return self % (operand % o.Operand())
            case Data():                    return self.copy()
            case _:
                if isinstance(self._data, operand.__class__):
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
                return super().__mod__(operand)
            
    def __eq__(self, other_data: o.Operand) -> bool:
        other_data = self & other_data    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other_data, Data):
            return self._data == other_data._data
        if other_data.__class__ == o.Operand:
            return True
        return False
    
    def __lt__(self, other_data: o.Operand) -> bool:
        other_data = self & other_data    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other_data, Data):
            return self._data < other_data._data
        return False
    
    def __gt__(self, other_data: o.Operand) -> bool:
        other_data = self & other_data    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(other_data, Data):
            return self._data > other_data._data
        return False
    
    def __le__(self, other_data: o.Operand) -> bool:
        return self == other_data or self < other_data
    
    def __ge__(self, other_data: o.Operand) -> bool:
        return self == other_data or self > other_data

    def getSerialization(self) -> dict:
        data_serialization = super().getSerialization()
        data_serialization["parameters"]["data"] = self._data
        if isinstance(self._data, o.Operand):
            data_serialization["parameters"]["data"] = self._data.getSerialization()
        return data_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Data':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "data" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._data = serialization["parameters"]["data"]
            if isinstance(self._data, dict) and "class" in self._data and "parameters" in self._data:
                self._data      = o.Operand().loadSerialization(self._data)
        return self

    def __lshift__(self, operand: o.Operand) -> 'Data':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case self.__class__():  # Particular case Data restrict self copy to self, no wrapping possible!
                super().__lshift__(operand)
                operand_data = operand._data
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
            case DataSource():
                self._data = operand % o.Operand()
            case Serialization():
                self.loadSerialization(operand % DataSource( dict() ))
            case o.Operand():
                self._data = operand.copy()
            case list():
                many_operands: list = []
                for single_operand in operand:
                    match single_operand:
                        case o.Operand():
                            many_operands.append(single_operand.copy())
                        case _:
                            many_operands.append(single_operand)
                self._data = many_operands
            case tuple():
                for single_operand in operand:
                    self << single_operand
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
        super().__init__()
        self._data = o.Operand() if operand is None else operand

    def __mod__(self, operand: o.Operand):
        """
        The % symbol will extract the data source value.

        Examples
        --------
        >>> dotted_note = Dotted(1/4)
        >>> dotted_note % float() >> Print()
        0.25
        >>> dotted_note % DataSource( float() ) >> Print()
        0.375
        """
        return self._data
    
    # CHAINABLE OPERATIONS

    # # STILL NEEDED BECAUSE DataSource is DataSource before Data!!!!
    # # CAN'T USE << SELF!!!
    # # # NEEDS TO REMOVE THIS METHOD
    # def copy(self, *parameters) -> 'DataSource':
    #     self_copy = self.__class__()
    #     self_data = self._data
    #     match self_data:
    #         case o.Operand():
    #             self_copy._data = self_data.copy()
    #         case list():
    #             many_operands: list = []
    #             for single_operand in self_data:
    #                 match single_operand:
    #                     case o.Operand():
    #                         many_operands.append(single_operand.copy())
    #                     case _:
    #                         many_operands.append(single_operand)
    #             self_copy._data = many_operands
    #         case _:
    #             self_copy._data = self_data
    #     # COPY THE SELF OPERANDS RECURSIVELY
    #     if self._next_operand is not None:
    #         self_copy._next_operand = self._next_operand.copy()
    #     return self_copy << parameters

class Parameters(Data):
    def __init__(self, *parameters):    # Allows multiple parameters
        super().__init__()
        self._data = parameters # Tuple

class Reporters(Data):
    def __init__(self, *parameters):    # Allows multiple parameters
        super().__init__()
        self._data = parameters # Tuple

class Result(Data):
    pass

class SideEffects(Data):
    def __init__(self, operand: o.Operand):
        super().__init__()
        self._data = operand

class LeftShift(SideEffects):
    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(self._data, o.Operand):
            self._data << operand
            return operand
        else:
            return super().__rrshift__(operand)

class RightShift(SideEffects):
    # CHAINABLE OPERATIONS

    def __rrshift__(self, operand: o.Operand) -> o.Operand:
        if isinstance(self._data, o.Operand):
            operand >> self._data
            return operand
        else:
            return super().__rrshift__(operand)

class Serialization(Data):
    def __init__(self, serialization: dict | o.Operand = None):
        super().__init__()
        if isinstance(serialization, o.Operand):
            self._data = serialization.copy()
        elif isinstance(serialization, dict) and "class" in serialization and "parameters" in serialization:
            self._data = o.Operand().loadSerialization(serialization)
        else:
            self._data = ol.Null()

    def __mod__(self, operand: any) -> any:
        """
        The % symbol is used to extract a Parameter, for the case a Serialization(),
        those Operands are pass right away to the self Data Operand, with the
        exception of "% Operand()", that returns the self Data operand.

        Examples
        --------
        >>> serialization = Serialization() << Retrigger("D")
        >>> serialization % DataSource( Duration() ) >> Print(False)
        {'class': 'Duration', 'parameters': {'time_unit': {'class': 'NoteValue', 'parameters': {'value': 0.03125}}}}
        >>> serialization = Serialization() << (Retrigger("D") << Division(6))
        >>> serialization % DataSource( Duration() ) >> Print(False)
        {'class': 'Duration', 'parameters': {'time_unit': {'class': 'NoteValue', 'parameters': {'value': 0.08333333333333333}}}}
        """
        match operand:
            case o.Operand():
                return self._data
            case dict():
                if isinstance(self._data, o.Operand):
                    return self._data.getSerialization()
                if isinstance(self._data, dict):
                    return self.deep_copy_dict(self._data)
                return dict()
            case _:
                return self._data % operand

    def __eq__(self, other_operand: any) -> bool:
        other_operand = self & other_operand    # Processes the tailed self operands or the Frame operand if any exists
        if self._data is None:
            if other_operand is None:
                return True
            return False
        match other_operand:
            case dict():
                return self._data.getSerialization() == other_operand
            case o.Operand():
                return self._data.getSerialization() == other_operand.getSerialization()
        return super().__eq__(other_operand)
    
    def getPlaylist(self, position: ot.Position = None) -> dict:
        return self._data.getPlaylist(position)

    def getSerialization(self) -> dict:
        if self._data is None:
            return {}
        return self._data.getSerialization()

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        self._data.loadSerialization(serialization)
        return self
        
    # # NEEDS TO REMOVE THIS METHOD
    # def copy(self, *parameters):
    #     self_copy: Data = self.__class__(self._data.copy()).loadSerialization( self.getSerialization() ) << parameters
    #     # COPY THE SELF OPERANDS RECURSIVELY
    #     if self._next_operand is not None:
    #         self_copy._next_operand = self._next_operand.copy()
    #     return self_copy

    def __lshift__(self, operand: any) -> 'o.Operand':
        if isinstance(operand, o.Operand):
            self._data = operand.copy()
        elif isinstance(operand, dict) and "class" in operand and "parameters" in operand:
            self._data = o.Operand().loadSerialization(operand)
        return self

    def __rrshift__(self, operand: any) -> o.Operand:
        if not isinstance(self._data, ol.Null) and isinstance(operand, o.Operand) and isinstance(self._data, o.Operand):
            return operand >> self._data
        else:
            return super().__rrshift__(operand)

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

    @staticmethod
    def deep_copy_dict(data):
        """
        Recursively creates a deep copy of a dictionary that may contain lists and other dictionaries.

        Args:
            data (dict): The dictionary to copy.

        Returns:
            dict: A deep copy of the original dictionary.
        """
        if isinstance(data, dict):
            # Create a new dictionary
            copy_dict = {}
            for key, value in data.items():
                # Recursively copy each value
                copy_dict[key] = Serialization.deep_copy_dict(value)
            return copy_dict
        elif isinstance(data, list):
            # Create a new list and recursively copy each element
            return [Serialization.deep_copy_dict(element) for element in data]
        else:
            # Base case: return the value directly if it's neither a list nor a dictionary
            return data

class Playlist(Data):
    def __init__(self, *parameters):
        super().__init__([])
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, for the case a Playlist(),
        there is only one data to be extracted, a Play List, the only and always
        the result of the "%" operator.

        Examples
        --------
        >>> play_list = Playlist() << Retrigger("D")
        >>> play_list >> Play()
        <operand_data.Playlist object at 0x0000022EC9967490>
        """
        return self._data

    def __eq__(self, other_operand: any) -> bool:
        other_operand = self & other_operand    # Processes the tailed self operands or the Frame operand if any exists
        if self._data is None:
            if other_operand is None:
                return True
            return False
        match other_operand:
            case list():
                return self._data == other_operand
            case o.Operand():
                return self._data == other_operand.getPlaylist()
        return super().__eq__(other_operand)
    
    def getPlaylist(self) -> list:
        return Playlist.copy_play_list(self._data)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: o.Operand) -> 'Playlist':
        import operand_container as oc
        import operand_element as oe
        match operand:
            case oc.Sequence() | oe.Element() | Playlist():
                self._data = operand.getPlaylist()
            case list():
                self._data = Playlist.copy_play_list(operand)
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

    def __rrshift__(self, operand) -> 'Playlist':
        import operand_container as oc
        import operand_element as oe
        if isinstance(self._data, list) and len(self._data) > 0 and isinstance(operand, (oc.Sequence, oe.Element, Playlist, ot.Position, ot.Length)):
            operand_play_list = operand.getPlaylist()
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
            return self.copy()
        if isinstance(operand, (oc.Sequence, oe.Element, Playlist)):
            return operand + self
        else:
            return super().__rrshift__(operand)

    def __add__(self, operand: o.Operand) -> 'Playlist':
        match operand:
            case ot.Length():
                playlist_copy = Playlist.copy_play_list(self._data)
                increase_position_ms: float = operand.getTime_ms()
                for midi_element in playlist_copy:
                    if "time_ms" in midi_element:
                        midi_element["time_ms"] = round(midi_element["time_ms"] + increase_position_ms, 3)
                return Playlist( playlist_copy )
            case list():        return Playlist( Playlist.copy_play_list(self._data) + Playlist.copy_play_list(operand) )
            case o.Operand():   return Playlist( Playlist.copy_play_list(self._data) + Playlist.copy_play_list(operand.getPlaylist()) )
            case _:             return Playlist( Playlist.copy_play_list(self._data) )

    @staticmethod
    def copy_play_list(play_list: list[dict]) -> list[dict]:
        copy_play_list = []
        for single_dict in play_list:
            copy_play_list.append(single_dict.copy())
        return copy_play_list

class Load(Serialization):
    def __init__(self, file_name: str = None):
        match file_name:
            case str():
                super().__init__( c.loadJsonMidiCreator(file_name) )
            case _:
                super().__init__()

class Import(Playlist):
    def __init__(self, file_name: str = None):
        super().__init__( [] if file_name is None else c.loadJsonMidiPlay(file_name) )

# LABEL - Process

# GENERIC

class Scale(Data):
    """
    A Scale() represents a given scale rooted in the key of C.
    
    Parameters
    ----------
    first : integer_like and string_like
        It can have the name of a scale as input, like, "Major" or "Melodic"
    """
    def __init__(self, *parameters):
        super().__init__()
        self._scale_list: list[int] = []
        self._mode: ou.Mode         = ou.Mode()
        if len(parameters) > 0:
            self << parameters

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, a Scale has many extraction modes
        one type of extraction is its list() type of Parameter representing a scale
        but it's also possible to extract the same scale on other Tonic() key based on C.

        Examples
        --------
        >>> major_scale = Scale()
        >>> (major_scale >> Modulate("5th")) % str() >> Print()
        Mixolydian
        """
        match operand:
            case DataSource():
                match operand % o.Operand():
                    case ou.Mode():             return self._mode
                    case list():                return self._scale_list
                    case str():                 return __class__.get_scale_name(self._scale_list)
                    case int():                 return __class__.get_scale_number(self._scale_list)
                    case _:                     return super().__mod__(operand)
            case ou.Mode():             return self._mode.copy()
            case list():                return self.modulation(None)
            case str():                 return __class__.get_scale_name(self.modulation(None))
            case int():                 return __class__.get_scale_number(self.modulation(None))
            case ou.Transposition():    return self.transposition(operand % int())
            case ou.Modulation():       return self.modulation(operand % int())
            case _:                     return super().__mod__(operand)

    def __eq__(self, other_scale: 'Scale') -> bool:
        other_scale = self & other_scale    # Processes the tailed self operands or the Frame operand if any exists
        if other_scale.__class__ == o.Operand:
            return True
        if type(self) != type(other_scale):
            return False
        return  self._scale_list == other_scale._scale_list
    
    def hasScale(self) -> bool:
        if self._scale_list == [] or self._scale_list == -1 or self._scale_list == "":
            return False
        return True

    def keys(self) -> int:
        scale_keys = 0
        self_scale = self._scale_list
        for key in self_scale:
            scale_keys += key
        return scale_keys

    def transposition(self, tones: int) -> int:        # Starting in C
        transposition = 0
        if isinstance(self._scale_list, list) and len(self._scale_list) == 12:
            modulated_scale = self.modulation(None)
            while tones > 0:
                transposition += 1
                if modulated_scale[transposition % 12]:
                    tones -= 1
        return transposition

    def modulation(self, mode: int | str = "5th") -> list: # AKA as remode (remoding)
        self_scale = self._scale_list.copy()
        if isinstance(self._scale_list, list) and len(self._scale_list) == 12:
            mode = self._mode if mode is None else mode
            # transposition = self.transposition(max(1, mode % int()) - 1)
            tones = max(1, mode % int()) - 1    # Modes start on 1, so, mode - 1 = tones
            transposition = 0
            if isinstance(self._scale_list, list) and len(self._scale_list) == 12:
                while tones > 0:
                    transposition += 1
                    if self._scale_list[transposition % 12]:
                        tones -= 1
            if transposition != 0:
                for key_i in range(12):
                    self_scale[key_i] = self._scale_list[(key_i + transposition) % 12]
        return self_scale

    def getSerialization(self) -> dict:
        element_serialization = super().getSerialization()
        element_serialization["parameters"]["scale_list"]   = self._scale_list
        element_serialization["parameters"]["mode"]         = self._mode % DataSource( int() )
        return element_serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Scale':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "scale_list" in serialization["parameters"] and "mode" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._scale_list    = serialization["parameters"]["scale_list"]
            self._mode          = ou.Mode()     << DataSource( serialization["parameters"]["mode"] )
        return self
        
    def modulate(self, mode: int | str = "5th") -> 'Scale': # AKA as remode (remoding)
        self._scale_list = self.modulation(mode)
        return self

    def __lshift__(self, operand: any) -> 'Scale':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case DataSource():
                match operand % o.Operand():
                    case ou.Mode():         self._mode = operand % o.Operand()
                    case _:                 super().__lshift__(operand)
            case Scale():
                super().__lshift__(operand)
                self._scale_list    = operand._scale_list.copy()
                self._mode          << operand._mode
            case ou.Mode() | int():
                self._mode << operand
            case str():
                self_scale = __class__.get_scale(operand)
                if len(self_scale) == 12:
                    self._scale_list = self_scale.copy()
            case list():
                if len(operand) == 12 and all(x in {0, 1} for x in operand):
                    self._scale_list = operand.copy()
                elif operand == []:
                    self._scale_list = []
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
        ["Diminished", "diminished"],
        ["Augmented", "augmented"],
        ["Blues", "blues"],
        ["Whole-tone", "Whole tone", "Whole", "whole"]
    ]
    _scales = [
    #       Db    Eb       Gb    Ab    Bb
    #       C#    D#       F#    G#    A#
    #    C     D     E  F     G     A     B
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        # Diatonic Scales
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],   # Major
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0],   # Dorian
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0],   # Phrygian
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],   # Lydian
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0],   # Mixolydian
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0],   # minor (Aeolian)
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0],   # Locrian
        # Other Scales
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],   # Harmonic
        [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],   # Melodic
        [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],   # Octatonic HW
        [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],   # Octatonic WH
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],   # Pentatonic Major
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],   # Pentatonic minor
        [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],   # Diminished
        [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],   # Augmented
        [1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0],   # Blues
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]    # Whole-tone
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
        if scale != [] and scale != -1 and scale != "":
            scale_number = __class__.get_scale_number(scale)
            if scale_number >= 0:
                return __class__._scales[scale_number]
        return []   # Has no scale at all
