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
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Tuple, Optional, Any, Generic
from typing import Self

from fractions import Fraction
import json
import enum
# Json Midi Creator Libraries
import creator as c
import operand as o
import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_label as ol
import operand_frame as of
import operand_generic as og
import operand_frame as of
import operand_chaos as ch

TypeElement = TypeVar('TypeElement', bound='Element')  # TypeElement represents any subclass of Operand


def get_channel_pitch(channel: int, pitch: int) -> int:
    return channel << 8 | pitch

if TYPE_CHECKING:
    from operand_container import Clip
    from operand_container import Part
    from operand_container import Song

class Element(o.Operand):
    """`Element`

    Element represents a type of midi message, like, `Note` and `ControlChange`.

    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        import operand_container as oc
        super().__init__()
        self._position_beats: Fraction      = Fraction(0)   # in Beats
        self._duration_beats: Fraction      = og.settings._duration
        self._channel: int                  = og.settings._channel
        self._enabled: bool                 = True

        self._owner_clip: oc.Clip           = None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter


    def _convert_staff_reference(self, staff_reference: 'og.Staff') -> Self:
        self._position_beats = ra.Position(staff_reference, self % od.Pipe( ra.Position() ))._rational
        self._duration_beats = ra.Duration(staff_reference, self % od.Pipe( ra.Duration() ))._rational
        return self


    def _set_owner_clip(self, owner_clip: 'Clip') -> Self:
        import operand_container as oc
        if isinstance(owner_clip, oc.Clip):
            self._owner_clip = owner_clip
        return self

    def _get_staff(self) -> 'og.Staff':
        if self._owner_clip is None:
            return og.settings._staff
        return self._owner_clip._staff


    def position(self, position_measures: float = None) -> Self:
        self._position_beats = self._get_staff().convertToPosition(ra.Measures(position_measures))._rational
        return self

    def duration(self, duration: float = None) -> Self:
        self._duration_beats = ra.Duration(duration)._rational
        return self

    def channel(self, channel: int = None) -> Self:
        self._channel = channel
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of an Element,
        those Parameters can be Position, Duration, midi Channel and midi Device

        Examples
        --------
        >>> element = Element()
        >>> element % Devices() % list() >> Print()
        ['loopMIDI', 'Microsoft']
        """
        import operand_container as oc
        match operand:
            case self.__class__():
                return self.copy()
            case od.Pipe():
                match operand._data:
                    case ra.Duration():
                        return operand._data._set_staff_reference(self._get_staff()) << od.Pipe( self._duration_beats )
                    case ra.Position():
                        return operand._data._set_staff_reference(self._get_staff()) << od.Pipe( self._position_beats )
                    case ra.Length():
                        return operand._data._set_staff_reference(self._get_staff()) \
                            << self._get_staff().convertToLength(ra.Duration(self._duration_beats))
                    case ou.Channel():      return ou.Channel() << od.Pipe( self._channel )
                    case Element():         return self
                    case ou.Enable():       return ou.Enable(self._enabled)
                    case ou.Disable():      return ou.Disable(not self._enabled)
                    case int():
                        return self._get_staff().convertToMeasures(ra.Beats(self._position_beats)) % int()
                    case float():           return float( self._duration_beats )
                    case Fraction():        return self._position_beats
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % operand
            case ra.Position():     return ra.Position(self, self._position_beats)
            case ra.Duration() | ra.Length():
                return operand.copy(self, self._duration_beats)
            case ra.NoteValue():
                return operand.copy()._set_staff_reference(self._get_staff()) << ra.Beats( self._duration_beats )
            case float():
                return self % ra.NoteValue() % float()
            case ra.TimeValue() | ou.TimeUnit():
                return self._get_staff().convertToPosition(ra.Beats(self._position_beats)) % operand
            case ou.Channel():      return ou.Channel() << od.Pipe( self._channel )
            case Element():         return self.copy()
            case int():
                return self._get_staff().convertToMeasures(ra.Beats(self._position_beats)) % int()
            case Fraction():        return self._position_beats
            case ou.Enable():       return ou.Enable(self._enabled)
            case ou.Disable():      return ou.Disable(not self._enabled)
            case Element():         return operand.__class__(self)
            case oc.Clip():         return oc.Clip(self)
            case _:                 return super().__mod__(operand)

    def get_component_elements(self) -> list['Element']:
        return [ self ]

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Element():
                return self._position_beats == other._position_beats \
                    and self._duration_beats == other._duration_beats \
                    and self._channel == other._channel
            case od.Conditional():
                return other == self
            case _:
                if other.__class__ == o.Operand:
                    return True
                if type(other) == ol.Null:
                    return False    # Makes sure ol.Null ends up processed as False
                return self % other == other

    def __lt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Element():
                if self._position_beats == other._position_beats:
                    return self._channel < other._channel
                return self._position_beats < other._position_beats
            case _:
                return self % other < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Element():
                if self._position_beats == other._position_beats:
                    return self._channel > other._channel
                return self._position_beats > other._position_beats
            case _:
                return self % other > other
    
    def start(self) -> ra.Position:
        return ra.Position(self, self._position_beats)

    def finish(self) -> ra.Position:
        return ra.Position(self, self._position_beats + self._duration_beats)


    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        return []

    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        
        self_position_min: Fraction = og.settings.beats_to_minutes(position_beats + self._position_beats)

        return [
                {
                    "time_ms": o.minutes_to_time_ms(self_position_min)
                }
            ]

    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list:
        if not self._enabled:
            return []
        midi_track: ou.MidiTrack = ou.MidiTrack() if not isinstance(midi_track, ou.MidiTrack) else midi_track

        self_numerator: int = self._get_staff()._time_signature._top
        self_denominator: int = self._get_staff()._time_signature._bottom
        self_position: float = float(position_beats + self._position_beats)
        self_duration: float = float(self._duration_beats)
        self_tempo: float = float(og.settings._tempo)

        # Validation is done by midiutil Midi Range Validation
        return [
                {
                    "event":        "Element",
                    "track":        midi_track % int() - 1,  # out of range shouldn't be exported as a midi track
                    "track_name":   midi_track % str(),
                    "numerator":    self_numerator,
                    "denominator":  self_denominator,
                    "channel":      self._channel - 1,
                    "time":         self_position,      # beats
                    "duration":     self_duration,      # beats
                    "tempo":        self_tempo          # bpm
                }
            ]

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["position"]     = self.serialize(self._position_beats)
        serialization["parameters"]["duration"]     = self.serialize(self._duration_beats)
        serialization["parameters"]["channel"]      = self.serialize(self._channel)
        serialization["parameters"]["enabled"]      = self.serialize(self._enabled)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Element':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "position" in serialization["parameters"] and "duration" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "enabled" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._position_beats        = self.deserialize(serialization["parameters"]["position"])
            self._duration_beats        = self.deserialize(serialization["parameters"]["duration"])
            self._channel               = self.deserialize(serialization["parameters"]["channel"])
            self._enabled               = self.deserialize(serialization["parameters"]["enabled"])
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():

                super().__lshift__(operand)
                self._channel               = operand._channel
                self._enabled               = operand._enabled
                # No conversion is done, beat and note_value values are directly copied (Same for Part)
                self._position_beats        = operand._position_beats
                self._duration_beats        = operand._duration_beats
                # Because an Element is also defined by the Owner Clip, this also needs to be copied!
                if self._owner_clip is None:    # << and copy operation doesn't override ownership
                    self._owner_clip        = operand._owner_clip

            case od.Pipe():
                match operand._data:
                    case ra.Position():     self._position_beats  = operand._data._rational
                    case ra.Duration() | ra.Length():
                        self._duration_beats  = operand._data._rational
                    case ou.Channel():      self._channel = operand._data._unit
                    case Fraction():        self._position_beats = operand._data
                    case float():           self._duration_beats = ra.Duration(operand._data)._rational

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Duration() | ra.Length():
                self._duration_beats        = operand._rational
            case ra.NoteValue():
                self << ra.Duration(self, operand)
            case float():
                self << ra.NoteValue(operand)
            case ra.Position():
                self._position_beats        = operand._rational
            case ra.TimeValue():
                self._position_beats        = self._get_staff().convertToBeats(operand)._rational
            case ou.TimeUnit():
                self_position: ra.Position  = ra.Position(od.Pipe( self._position_beats ))._set_staff_reference(self._get_staff()) << operand
                self._position_beats        = self_position._rational
            case Fraction():
                self._position_beats        = operand
            case int():
                self._position_beats        = self._get_staff().convertToBeats(ra.Measures(operand))._rational
            case ou.Channel():
                self._channel               = operand._unit
            case ou.Enable():
                self._enabled               = operand._unit != 0
            case ou.Disable():
                self._enabled               = operand._unit == 0
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


    def __rshift__(self, operand: o.T) -> Self:
        match operand:
            case od.Serialization():
                return self << operand % od.Pipe()
            case od.Playlist():
                operand.__rrshift__(self)
                return self
        return super().__rshift__(operand)


    def __add__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.copy().__iadd__(operand)
    
    def __sub__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.copy().__isub__(operand)
    
    def __mul__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.copy().__imul__(operand)
    
    def __truediv__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.copy().__itruediv__(operand)
    
    def __floordiv__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.copy().__ifloordiv__(operand)
    

    def __radd__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.__add__(operand)

    def __rsub__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.__mul__(-1).__add__(operand)

    def __rmul__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.__mul__(operand)

    def __rtruediv__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.__truediv__(operand)

    def __rfloordiv__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.__floordiv__(operand)


    def __iadd__(self, operand: any) -> Union[TypeElement, 'Clip']:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():
                return oc.Clip(self, operand)    # Clip does an += for << operator
            case oc.Clip():
                return operand.empty_copy(self).__iadd__(operand)   # Keeps the Clip Staff and integrates self
            # For efficient reasons
            case ra.Position():
                self._position_beats += operand._rational
            case ra.Duration() | ra.Length():
                self._duration_beats += operand._rational
            case _:
                self_operand: any = self % operand
                self_operand += operand
                return self << self_operand
        return self

    def __isub__(self, operand: any) -> Union[TypeElement, 'Clip']:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            # For efficient reasons
            case ra.Position():
                self._position_beats -= operand._rational
            case ra.Duration() | ra.Length():
                self._duration_beats -= operand._rational
            case _:
                self_operand: any = self % operand
                self_operand -= operand
                return self << self_operand
        return self

    def __imul__(self, operand: any) -> Union[TypeElement, 'Clip']:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:  # Allows Frame skipping to be applied to the elements' parameters!
            case Element():
                return oc.Clip(self).__imul__(operand)
            case oc.Clip():
                return operand.empty_copy(self).__imul__(operand)   # Keeps the Clip Staff and integrates self
            # Can be applied to owned elements
            case int():
                if self._owner_clip is not None:
                    new_elements: list[Element] = []
                    if operand > 1:
                        for next_element_i in range(1, operand):
                            next_element: Element = self.copy()
                            new_elements.append(next_element)
                            next_element._position_beats += ra.Beats(ra.Measures(self._owner_clip, 1) * next_element_i)._rational
                    return self._owner_clip._append(new_elements)   # Allows the chaining of Clip operations
                else:
                    new_clip: oc.Clip = oc.Clip()
                    if operand > 0:
                        for _ in range(operand):
                            new_clip.__imul__(self)
                    return new_clip
            case ra.TimeValue() | ou.TimeUnit():
                if self._owner_clip is not None:
                    new_elements: list[Element] = []
                    operand_value: Fraction = operand % Fraction()
                    self_repeating = int( operand_value / ra.Measures(self._owner_clip, 1) )
                    if self_repeating > 1:
                        for next_element_i in range(1, self_repeating):
                            next_element: Element = self.copy()
                            new_elements.append(next_element)
                            next_element._position_beats += ra.Beats(ra.Measures(self._owner_clip, 1) * next_element_i)._rational
                    return self._owner_clip._append(new_elements)   # Allows the chaining of Clip operations
                else:
                    return oc.Clip(self).__imul__(operand)
        self_operand: any = self % operand
        self_operand *= operand # Generic `self_operand`
        return self << self_operand

    def __itruediv__(self, operand: any) -> Union[TypeElement, 'Clip']:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:  # Allows Frame skipping to be applied to the elements' parameters!
            case Element():
                return oc.Clip(self).__itruediv__(operand)
            case oc.Clip():
                return operand.empty_copy(self).__itruediv__(operand)   # Keeps the Clip Staff and integrates self
            # Can be applied to owned elements
            case int():
                if self._owner_clip is not None:
                    new_elements: list[Element] = []
                    if operand > 1:
                        for next_element_i in range(1, operand):
                            next_element: Element = self.copy()
                            new_elements.append(next_element)
                            next_element._position_beats += self._duration_beats * next_element_i
                        self._owner_clip._append(new_elements)
                    return self._owner_clip._append(new_elements)   # Allows the chaining of Clip operations
                else:
                    new_clip: oc.Clip = oc.Clip()
                    if operand > 0:
                        for _ in range(operand):
                            new_clip.__itruediv__(self)
                    return new_clip
            case ra.TimeValue() | ou.TimeUnit():
                if self._owner_clip is not None:
                    new_elements: list[Element] = []
                    self_duration: ra.Duration = self % ra.Duration()
                    duration_value: Fraction = self_duration % operand % Fraction()
                    if duration_value > 0:
                        operand_value: Fraction = operand % Fraction()
                        self_repeating = int( operand_value / duration_value )
                        if self_repeating > 1:
                            for next_element_i in range(1, self_repeating):
                                next_element: Element = self.copy()
                                new_elements.append(next_element)
                                next_element._position_beats += self._duration_beats * next_element_i
                    return self._owner_clip._append(new_elements)   # Allows the chaining of Clip operations
                else:
                    return oc.Clip(self).__itruediv__(operand)
            case _:
                if operand != 0:
                    self_operand: any = self % operand
                    self_operand /= operand # Generic `self_operand`
                    return self << self_operand
        return self


    def __ifloordiv__(self, operand: any) -> Union[TypeElement, 'Clip']:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:  # Allows Frame skipping to be applied to the elements' parameters!
            case Element():
                return oc.Clip(self).__ifloordiv__(operand)
            case oc.Clip():
                return operand.empty_copy(self).__ifloordiv__(operand)  # Keeps the Clip Staff and integrates self
            # Can be applied to owned elements
            case int(): # This results in a simple repeat of elements
                if self._owner_clip is not None:
                    if operand > 1:
                        element_clip: oc.Clip = self._owner_clip
                        new_elements: list[Element] = []
                        for next_element_i in range(1, operand):
                            next_element: Element = self.copy()._set_owner_clip(element_clip)
                            new_elements.append(next_element)
                        element_clip._append(new_elements)
                    return self
                else:
                    new_clip: oc.Clip = oc.Clip()
                    if operand > 0:
                        for _ in range(operand):
                            new_clip.__ifloordiv__(self)
                    return new_clip
            # Divides the `Duration` by the given `Length` amount as denominator
            case ra.Length() | ra.Duration():
                if self._owner_clip is not None:
                    new_elements: list[Element] = []
                    total_segments: int = operand % int()   # Extracts the original imputed integer
                    if total_segments > 1:
                        self._duration_beats /= total_segments
                        for next_element_i in range(1, total_segments):
                            next_element: Element = self.copy()
                            new_elements.append(next_element)
                            next_element._position_beats += self._duration_beats * next_element_i
                    return self._owner_clip._append(new_elements)   # Allows the chaining of Clip operations
                else:
                    return oc.Clip(self).__ifloordiv__(operand)
            # Divides the `Duration` by sections with the given `Duration` (note value)
            case ra.NoteValue():
                if self._owner_clip is not None:
                    new_elements: list[Element] = []
                    group_length: Fraction = self._duration_beats
                    segment_duration: Fraction = ra.Duration(self, operand)._rational
                    if segment_duration < group_length:
                        group_position: Fraction = self._position_beats
                        group_finish: Fraction = group_position + self._duration_beats
                        self._duration_beats = segment_duration
                        next_split: Fraction = group_position + segment_duration
                        while group_finish > next_split:
                            next_element: Element = self.copy()
                            new_elements.append(next_element)
                            next_element._position_beats = next_split  # Just positions the `Element`
                            next_split += segment_duration
                            if next_split > group_finish:
                                next_element._duration_beats -= next_split - group_finish # Trims the extra `Duration`
                                break
                    return self._owner_clip._append(new_elements)   # Allows the chaining of Clip operations
                else:
                    return oc.Clip(self).__ifloordiv__(operand)
            case ra.Position() | ra.TimeValue() | ou.TimeUnit():
                if self._owner_clip is not None:
                    new_elements: list[Element] = []
                    left_start: Fraction = self._position_beats
                    split_position: Fraction = ra.Position(self, left_start, operand)._rational
                    if split_position > left_start:
                        right_finish: Fraction = left_start + self._duration_beats
                        if split_position < right_finish:
                            left_duration: Fraction = split_position - left_start
                            right_duration: Fraction = right_finish - split_position
                            self._duration_beats = left_duration
                            right_element: Element = self.copy()
                            new_elements.append(right_element)
                            right_element._position_beats = split_position
                            right_element._duration_beats = right_duration
                    return self._owner_clip._append(new_elements)   # Allows the chaining of Clip operations
                else:
                    return oc.Clip(self).__ifloordiv__(operand)
            case _:
                if operand != 0:
                    self_operand: any = self % operand
                    self_operand //= operand # Generic `self_operand`
                    return self << self_operand
        return self


class Group(Element):
    """`Element -> Group`

    A `Group` element aggregates any other type of `Element` of any amount.

    Parameters
    ----------
    list([ControlChange(ou.Number("Pan"), 0), Note()]) : A list with all the elements grouped by `Group`.
    Position(0), TimeValue, TimeUnit, int : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._elements: list[Element] = [
            # From top to down, from left to right
            ControlChange(ou.Number("Pan"), 0),
            Note()
        ]
        super().__init__(*parameters)

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():            return self._elements
                    case _:                 return super().__mod__(operand)
            case list():            return self._elements.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._elements == other._elements
            case _:
                return super().__eq__(other)
    
    def get_component_elements(self) -> list[Element]:
        return self._elements

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        self_playlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_playlist.extend(single_element.getPlotlist(midi_track, position_beats, channels))
        return self_playlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_playlist.extend(single_element.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list[dict]:
        self_midilist: list[dict] = []
        for single_element in self.get_component_elements():
            self_midilist.extend(single_element.getMidilist(midi_track, position_beats))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["elements"] = self.serialize( self._elements )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "elements" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._elements  = self.deserialize( serialization["parameters"]["elements"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Group():
                super().__lshift__(operand)
                self._elements = self.deep_copy( operand._elements )
            case od.Pipe():
                match operand._data:
                    case list():
                        self._elements = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                self._elements = self.deep_copy( operand )
            case dict():
                for key, value in operand.items():
                    if isinstance(key, int):
                        if 0 < key <= len(self._elements):
                            self._elements[key - 1] << value
            case _:
                super().__lshift__(operand)
        return self


class Clock(Element):
    """`Element -> Clock`

    A `Clock` element can be used to send midi clock messages in a specific way compared to the `defaults` one.

    Parameters
    ----------
    list([]), Devices, ClockedDevices : The `Devices` to which the clock messages are sent.
    PPQN(24) : Pulses Per Quarter Note.
    ClockStopModes(0), str : Sets the following Stop modes, 0 - "Stop", 1 - "Pause", 2 - "Continue", 3 - "Total".
    Position(0), TimeValue, TimeUnit, int : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._devices: list[str]    = []
        self._clock_ppqn: int       = 24    # Pulses Per Quarter Note
        self._clock_stop_mode: int  = 0     # 0 - "Stop", 1 - "Pause", 2 - "Continue", 3 - "Total"
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def ppqn(self, ppqn: int = None) -> Self:
        self._clock_ppqn = ppqn
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Clock,
        those Parameters are the ones of the Element, like Position and Duration,
        plus the Pulses Per Quarter Note, the last one as 24 by default.

        Examples
        --------
        >>> clock = Clock(4)
        >>> clock % Duration() >> Print(0)
        {'class': 'Duration', 'parameters': {'time_unit': {'class': 'Measure', 'parameters': {'value': 4.0}}}}
        """
        import operand_container as oc
        match operand:
            case od.Pipe():
                match operand._data:
                    case oc.Devices():          return oc.Devices(self._devices)
                    case oc.ClockedDevices():   return oc.ClockedDevices(self._devices)
                    case ou.PPQN():             return ou.PPQN(self._clock_ppqn)
                    case ou.ClockStopModes():   return ou.ClockStopModes(self._clock_stop_mode)
                    case _:                 return super().__mod__(operand)
            case oc.Devices():          return oc.Devices(self._devices)
            case oc.ClockedDevices():   return oc.ClockedDevices(self._devices)
            case ou.PPQN():             return ou.PPQN(self._clock_ppqn)
            case ou.ClockStopModes():   return ou.ClockStopModes(self._clock_stop_mode)
            case str():                 return ou.ClockStopModes(self._clock_stop_mode) % str()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._devices == other._devices \
                    and self._clock_ppqn == other._clock_ppqn \
                    and self._clock_stop_mode == other._clock_stop_mode
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True,
                                                                    global_staff: og.Staff = None) -> list[dict]:
        if not self._enabled:
            return []

        pulses_per_note: int = self._clock_ppqn * 4

        self_playlist: list[dict] = []

        # Set to be used as a Global clock !
        if isinstance(global_staff, og.Staff):

            single_devices: set[str] = set()
            self_clock_devices: list[list[str]] = []

            for clocked_device in self._devices:
                if clocked_device not in single_devices:
                    self_clock_devices.append(clocked_device)
                    single_devices.add(clocked_device)

            pulses_per_beat: Fraction = global_staff % od.Pipe( ra.BeatNoteValue() ) % Fraction() * pulses_per_note
            total_clock_pulses: int = int(self._duration_beats * pulses_per_beat)

            if total_clock_pulses > 0:
                
                self_duration_min: Fraction = og.settings.beats_to_minutes(self._duration_beats)
                single_pulse_duration_min: Fraction = self_duration_min / total_clock_pulses

                self_playlist.append(
                    {
                        "clock": {
                            # Has to add the extra Stop pulse message afterwards at (single_pulse_duration_min * total_clock_pulses)
                            "total_clock_pulses": total_clock_pulses,
                            "pulse_duration_min_numerator": single_pulse_duration_min.numerator,
                            "pulse_duration_min_denominator": single_pulse_duration_min.denominator,
                            "stop_mode": self._clock_stop_mode,
                            "devices": self_clock_devices
                        }
                    }
                )

        # NORMAL use case scenario
        else:

            pulses_per_beat: Fraction = self._get_staff() % od.Pipe( ra.BeatNoteValue() ) % Fraction() * pulses_per_note
            total_clock_pulses: int = int( self._duration_beats * pulses_per_beat )

            if total_clock_pulses > 0:

                self_position_min: Fraction = og.settings.beats_to_minutes(position_beats + self._position_beats)
                self_duration_min: Fraction = og.settings.beats_to_minutes(self._duration_beats)

                # Starts by setting the Devices
                if devices_header and isinstance(midi_track, ou.MidiTrack):
                    self_playlist.append(
                        {
                            "devices": midi_track._devices if midi_track else og.defaults._devices
                        }
                    )

                if self._clock_stop_mode == 2:  # 2 - "Continue"

                    # First quarter note pulse (total 1 in 24 pulses per quarter note)
                    self_playlist.append(
                        {
                            "time_ms": o.minutes_to_time_ms(self_position_min),
                            "midi_message": {
                                "status_byte": 0xFB     # Continue Track
                            }
                        }
                    )
            
                else:

                    # First quarter note pulse (total 1 in 24 pulses per quarter note)
                    self_playlist.append(
                        {
                            "time_ms": o.minutes_to_time_ms(self_position_min),
                            "midi_message": {
                                "status_byte": 0xFA     # Start Track
                            }
                        }
                    )
            
                single_pulse_duration_min: Fraction = self_duration_min / total_clock_pulses

                # Middle quarter note pulses (total 23 in 24 pulses per quarter note)
                for clock_pulse in range(1, total_clock_pulses):
                    self_playlist.append(
                        {
                            "time_ms": o.minutes_to_time_ms(single_pulse_duration_min * clock_pulse),
                            "midi_message": {
                                "status_byte": 0xF8     # Timing Clock
                            }
                        }
                    )

                # Last quarter note pulse (45 pulses where this last one sets the stop)
                self_playlist.append(
                    {
                        "time_ms": o.minutes_to_time_ms(single_pulse_duration_min * total_clock_pulses),
                        "midi_message": {
                            "status_byte": 0xFC         # Stop Track
                        }
                    }
                )

                if self._clock_stop_mode == 0 or self._clock_stop_mode == 3:

                    # Resets the position back to 0
                    self_playlist.append(
                        {
                            "time_ms": o.minutes_to_time_ms(single_pulse_duration_min * total_clock_pulses),
                            "midi_message": {
                                "status_byte": 0xF2,    # Send a Song Position Pointer (SPP)
                                "data_byte_1": 0,       # Reset
                                "data_byte_2": 0        # Reset
                            }
                        }
                    )

                if self._clock_stop_mode == 3:  # 3 - "Total"

                    # Sends a SysEx Stop Message
                    self_playlist.append(
                        {
                            "time_ms": o.minutes_to_time_ms(single_pulse_duration_min * total_clock_pulses),
                            "midi_message": {
                                "status_byte": 0xF0,    # Start of SysEx
                                "data_bytes": [0x7F, 0x7F, 0x06, 0x01]  # Universal Stop command
                                                    # Byte 0xF7 Ends the SysEx stream (implicit)
                            }
                        }
                    )

        return self_playlist


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["devices"]          = self.serialize( self._devices )
        serialization["parameters"]["clock_ppqn"]       = self.serialize( self._clock_ppqn )
        serialization["parameters"]["clock_stop_mode"]  = self.serialize( self._clock_stop_mode )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "devices" in serialization["parameters"] and "clock_ppqn" in serialization["parameters"] and "clock_stop_mode" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._devices           = self.deserialize( serialization["parameters"]["devices"] )
            self._clock_ppqn        = self.deserialize( serialization["parameters"]["clock_ppqn"] )
            self._clock_stop_mode   = self.deserialize( serialization["parameters"]["clock_stop_mode"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Clock():
                super().__lshift__(operand)
                self._devices           = operand._devices.copy()
                self._clock_ppqn        = operand._clock_ppqn
                self._clock_stop_mode   = operand._clock_stop_mode
            case od.Pipe():
                match operand._data:
                    case oc.ClockedDevices():   self._devices = operand._data % od.Pipe( list() )
                    case oc.Devices():          self._devices = operand._data % od.Pipe( list() )
                    case ou.PPQN():             self._clock_ppqn = operand._data._unit
                    case ou.ClockStopModes():   self._clock_stop_mode = operand._data._unit
                    case _:                     super().__lshift__(operand)
            case oc.ClockedDevices():   self._devices = operand % list()
            case oc.Devices():          self._devices = operand % list()
            case od.Device():           self._devices = oc.Devices(self._devices, operand) % od.Pipe( list() )
            case ou.PPQN():             self._clock_ppqn = operand._unit
            case ou.ClockStopModes():   self._clock_stop_mode = operand._unit
            case str():                 self._clock_stop_mode = ou.ClockStopModes(operand)._unit
            case _:                     super().__lshift__(operand)
        return self


class Rest(Element):
    """`Element -> Rest`

    A `Rest` element is essentially used to occupy space on a `Staff` for a process of `Clip` stacking or linking.

    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        if not self._enabled:
            return []
        
        if self._duration_beats == 0:
            return []

        if channels is not None:
            channels["note"].add(self._channel)

        self_plotlist: list[dict] = []
    
        position_on: Fraction = position_beats + self._position_beats
        position_off: Fraction = position_on + self._duration_beats

        self_plotlist.append(
            {
                "note": {
                    "position_on": position_on,
                    "position_off": position_off,
                    "pitch": 60,        # Middle C
                    "velocity": 127,    # Maximum contrast, no transparency
                    "channel": self._channel,
                    "plot_as_rest": True
                }
            }
        )

        return self_plotlist


class Note(Element):
    """`Element -> Note`

    A `Note` element is the most important `Element` and basically represents a Midi note message including Note On and Note Off.

    Parameters
    ----------
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._velocity: int         = og.settings._velocity
        self._gate: Fraction        = Fraction(1)
        self._tied: int             = False
        self._pitch: og.Pitch       = og.Pitch()._set_owner_element(self)
        super().__init__(*parameters)

    def velocity(self, velocity: int = 100) -> Self:
        self._velocity = velocity
        return self

    def gate(self, gate: float = None) -> Self:
        self._gate = ra.Gate(gate)._rational
        return self

    def tied(self, tied: bool = True) -> Self:
        self._tied = tied
        return self

    def pitch(self, key: Optional[int] = 0, octave: Optional[int] = 4) -> Self:
        self._pitch << ou.Key(key) << ou.Octave(octave)
        return self

    def __lt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Note():
                # Adds predictability in sorting and consistency in clipping
                if self._position_beats == other._position_beats:
                    self_pitch: int = self._pitch.pitch_int()
                    other_pitch: int = other._pitch.pitch_int()
                    if self_pitch == other_pitch:
                        return self._channel < other._channel
                    return self_pitch < other_pitch
                return self._position_beats < other._position_beats
            case Element():
                return super().__lt__(other)
            case _:
                return self % other < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Note():
                # Adds predictability in sorting and consistency in clipping
                if self._position_beats == other._position_beats:
                    self_pitch: int = self._pitch.pitch_int()
                    other_pitch: int = other._pitch.pitch_int()
                    if self_pitch == other_pitch:
                        return self._channel > other._channel
                    return self_pitch > other_pitch
                return self._position_beats > other._position_beats
            case Element():
                return super().__gt__(other)
            case _:
                return self % other > other
    
    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Note,
        those Parameters are the ones of the Element, like Position and Duration,
        plus the Rest's Duration and Pitch, Velocity and Gate, the last one
        with a value of 0.90 by default.

        Examples
        --------
        >>> note = Note("F")
        >>> note % Key() % str() >> Print()
        F
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Velocity():     return ou.Velocity() << od.Pipe(self._velocity)
                    case ra.Gate():         return ra.Gate() << od.Pipe(self._gate)
                    case ou.Tied():         return ou.Tied() << od.Pipe( self._tied )
                    case og.Pitch():        return self._pitch
                    case _:                 return super().__mod__(operand)
            case ou.Velocity():     return ou.Velocity() << od.Pipe(self._velocity)
            case ra.Gate():         return ra.Gate() << od.Pipe(self._gate)
            case ou.Tied():         return ou.Tied() << od.Pipe( self._tied )
            case og.Pitch():        return self._pitch.copy()
            case int():             return self._pitch.pitch_int()
            case ou.PitchParameter() | str() | og.Scale():
                                    return self._pitch % operand
            case ou.DrumKit():
                return ou.DrumKit(self._pitch.pitch_int(), ou.Channel(self._channel))
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._velocity  == other._velocity \
                    and self._gate      == other._gate \
                    and self._tied      == other._tied \
                    and self._pitch     == other._pitch
            case int(): # int() for Note concerns Degree
                return self._pitch._degree_0 == other
            case _:
                return super().__eq__(other)


    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        if not self._enabled:
            return []
        
        if self._duration_beats == 0:
            return []

        if channels is not None:
            channels["note"].add(self._channel)

        pitch_int: int = self._pitch.pitch_int()

        self_plotlist: list[dict] = []
    
        position_on: Fraction = position_beats + self._position_beats
        position_off: Fraction = position_on + self._duration_beats

        self_plotlist.append(
            {
                "note": {
                    "position_on": position_on,
                    "position_off": position_off,
                    "pitch": pitch_int,
                    "velocity": self._velocity,
                    "channel": self._channel,
                    "plot_as_rest": False
                }
            }
        )

        # This only applies for Clip owned Notes called by the Clip class!
        if midi_track is not None and self._owner_clip is not None:

            # Checks if it's a following tied note first
            if self._tied:

                def extend_note(note_off: dict, position_on_beats: Fraction, position_off_beats: Fraction):
                    note_off["position_off"] = position_off_beats


                tied_note: bool = self._get_staff()._tie_note(
                    get_channel_pitch(self._channel, pitch_int),
                    position_on, position_off,
                    self_plotlist[0]["note"], extend_note
                )

                if tied_note:
                    return []   # Discards note


            # Record present Note on the Staff stacked notes
            if not self._get_staff()._stack_note(
                self_plotlist[0]['note']["position_on"],
                self._channel - 1,
                pitch_int
            ):
                print(f"Warning (PLL): Ignored redundant Note on Channel {self._channel} "
                    f"and Pitch {self_plotlist[0]['note']['pitch']} with same time start!")
                return []

        return self_plotlist


    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        
        self_position_beats: Fraction = position_beats + self._position_beats
        self_position_min: Fraction = og.settings.beats_to_minutes(self_position_beats)
        self_duration_min: Fraction = og.settings.beats_to_minutes(self._duration_beats)

        if self_duration_min == 0:
            return []

        pitch_int: int = self._pitch.pitch_int()
        devices: list[str] = midi_track._devices if midi_track else og.settings._devices

        self_playlist: list[dict] = []
    
        if devices_header:
            self_playlist.append(
                {
                    "devices": devices
                }
            )

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist.append(
            {
                "time_ms": o.minutes_to_time_ms(self_position_min),
                "midi_message": {
                    "status_byte": 0x90 | 0x0F & self._channel - 1,
                    "data_byte_1": pitch_int,
                    "data_byte_2": self._velocity
                }
            }
        )
        self_playlist.append(
            {
                "time_ms": o.minutes_to_time_ms(self_position_min + self_duration_min * self._gate),
                "midi_message": {
                    "status_byte": 0x80 | 0x0F & self._channel - 1,
                    "data_byte_1": pitch_int,
                    "data_byte_2": 0
                }
            }
        )

        # Already with a Playlist at this point

        # This only applies for Clip owned Notes called by the Clip class!
        if midi_track is not None and self._owner_clip is not None:

            # Filers out any "devices" parameter, without "time_ms" one
            self_playlist_time_ms: list[dict] = self_playlist 
            if devices_header:
                self_playlist_time_ms = o.playlist_time_ms( self_playlist )

            # Checks if it's a tied note first
            if self._tied:

                def extend_note(note_off: dict, position_on: Fraction, position_off: Fraction):
                    note_off["time_ms"] = o.minutes_to_time_ms(position_off)


                tied_note: bool = self._get_staff()._tie_note(
                    get_channel_pitch(self._channel, pitch_int),
                    self_position_min, self_position_min + self_duration_min * self._gate,
                    self_playlist[1], extend_note
                )

                if tied_note:
                    return []   # Discards note


            # Record present Note on the Staff stacked notes
            if not self._get_staff()._stack_note(
                self_playlist_time_ms[0]["time_ms"],
                self_playlist_time_ms[0]["midi_message"]["status_byte"],
                self_playlist_time_ms[0]["midi_message"]["data_byte_1"]
            ):
                print(f"Warning (PL): Ignored redundant Note on Channel {self._channel} "
                    f"and Pitch {self_playlist_time_ms[0]['midi_message']['data_byte_1']} with same time start!")
                return []

        return self_playlist


    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list:
        if not self._enabled:
            return []
        
        self_duration_beats: Fraction = self._duration_beats * self._gate
        self_duration: float = float(self_duration_beats)
        if self_duration == 0:
            return []

        pitch_int: int = self._pitch.pitch_int()

        self_midilist: list = super().getMidilist(midi_track, position_beats)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "Note"
        self_midilist[0]["duration"]    = self_duration
        self_midilist[0]["velocity"]    = self._velocity
        self_midilist[0]["pitch"]       = pitch_int

        # This only applies for Clip owned Notes called by the Clip class!
        if midi_track is not None and self._owner_clip is not None:

            # Checks if it's a tied note first
            if self._tied:

                def extend_note(note: dict, position_on: Fraction, position_off: Fraction):
                    note["duration"] = float(position_off - position_on)

                self_position: Fraction = (Fraction(0) if position_beats is None else position_beats) + self._position_beats

                tied_note: bool = self._get_staff()._tie_note(
                    get_channel_pitch(self._channel, pitch_int),
                    self_position, self_position + self_duration_beats,
                    self_midilist[0], extend_note
                )

                if tied_note:
                    return []   # Discards note


            # Record present Note on the Staff stacked notes
            if not self._get_staff()._stack_note(
                self_midilist[0]["time"],
                self_midilist[0]["channel"],
                self_midilist[0]["pitch"]
            ):
                print(f"Warning (ML): Ignored redundant Note on Channel {self_midilist[0]['channel'] + 1} "
                    f"and Pitch {self_midilist[0]['pitch']} with same time start!")
                return []

        return self_midilist


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["velocity"] = self.serialize( self._velocity )
        serialization["parameters"]["gate"]     = self.serialize( self._gate )
        serialization["parameters"]["tied"]     = self.serialize( self._tied )
        serialization["parameters"]["pitch"]    = self.serialize( self._pitch )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Note':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "velocity" in serialization["parameters"] and "gate" in serialization["parameters"] and
            "tied" in serialization["parameters"] and "pitch" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._velocity  = self.deserialize( serialization["parameters"]["velocity"] )
            self._gate      = self.deserialize( serialization["parameters"]["gate"] )
            self._tied      = self.deserialize( serialization["parameters"]["tied"] )
            self._pitch     = self.deserialize( serialization["parameters"]["pitch"] )
            self._pitch._set_owner_element(self)
        return self


    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Note():
                super().__lshift__(operand)
                self._velocity      = operand._velocity
                self._gate          = operand._gate
                self._tied          = operand._tied
                self._pitch         << operand._pitch
            case od.Pipe():
                match operand._data:
                    case ou.Velocity():     self._velocity  = operand._data._unit
                    case ra.Gate():         self._gate      = operand._data._rational
                    case ou.Tied():         self._tied      = operand._data.__mod__(od.Pipe( bool() ))
                    case og.Pitch():        self._pitch     = operand._data
                    case _:                 super().__lshift__(operand)
            case ou.Velocity():     self._velocity = operand._unit
            case int():             self._pitch << operand
            case ra.Gate():         self._gate = operand._rational
            case ou.Tied():
                self._tied = operand % bool()
            case og.Pitch() | ou.PitchParameter() | None | og.Scale() | list() | str():
                self._pitch << operand
            case ou.DrumKit():
                self._channel = operand._channel
                self._pitch << operand
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> 'Note':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._velocity += operand
            case og.Pitch() | ou.PitchParameter() | int():
                self._pitch += operand  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> 'Note':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._velocity -= operand
            case og.Pitch() | ou.PitchParameter() | int():
                self._pitch -= operand  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)


class Cluster(Note):
    """`Element -> Note -> Cluster`

    A `Cluster` element aggregates multiple notes based on the list len and content. \
        That content is added to the present single `Note` configuration.
    The difference between a `Cluster` and a `PitchChord`, is that a `Cluster` hasn't its own scale,
        and thus always adders to the the Key Signature or `Staff` scale.

    Parameters
    ----------
    dict({0: [0, 2, 4]}) : Sets the specific offset pitches (list) to be pressed as `Note` for each `Octave` offset (int).
    Arpeggio("None") : Sets the `Arpeggio` intended to do with the simultaneously pressed notes.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._offsets: list = [0.0, 2.0, 4.0]
        self._arpeggio: og.Arpeggio = og.Arpeggio("None")
        super().__init__()
        self << self._get_staff().convertToDuration(ra.Measures(1))  # By default a Scale and a Chord has one Measure duration
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case list():            return self._offsets
                    case og.Arpeggio():     return self._arpeggio
                    case _:                 return super().__mod__(operand)
            case list():            return self.deep_copy(self._offsets)
            case og.Arpeggio():     return self._arpeggio.copy()
            case ou.Order() | ra.Swing() | ch.Chaos():
                                    return self._arpeggio % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._offsets == other._offsets \
                    and self._arpeggio == other._arpeggio
            case _:
                return super().__eq__(other)
    
    def get_component_elements(self) -> list[Element]:
        cluster_notes: list[Note] = []
        for pitch_offset in self._offsets:
            single_note: Note = Note(self)
            single_note._pitch += pitch_offset
            cluster_notes.append( single_note )
        return self._arpeggio.arpeggiate(cluster_notes)

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        self_plotlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_plotlist.extend(single_element.getPlotlist(midi_track, position_beats, channels))
        return self_plotlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_playlist.extend(single_element.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list[dict]:
        self_midilist: list[dict] = []
        for single_element in self.get_component_elements():
            self_midilist.extend(single_element.getMidilist(midi_track, position_beats))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["offsets"]  = self.serialize( self._offsets )
        serialization["parameters"]["arpeggio"] = self.serialize( self._arpeggio )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "offsets" in serialization["parameters"] and "arpeggio" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._offsets  = self.deserialize( serialization["parameters"]["offsets"] )
            self._arpeggio = self.deserialize( serialization["parameters"]["arpeggio"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Cluster():
                super().__lshift__(operand)
                self._offsets = self.deep_copy( operand._offsets )
                self._arpeggio  << operand._arpeggio
            case od.Pipe():
                match operand._data:
                    case list():
                        self._offsets = operand._data
                    case og.Arpeggio():
                        self._arpeggio = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                self._offsets = self.deep_copy( operand )
            case og.Arpeggio() | ou.Order() | ra.Swing() | ch.Chaos():
                self._arpeggio << operand
            case _:
                super().__lshift__(operand)
        return self


class KeyScale(Note):
    """`Element -> Note -> KeyScale`

    A `KeyScale` element allows the triggering of all notes concerning a specific `Scale`.

    Parameters
    ----------
    Arpeggio("None") : Sets the `Arpeggio` intended to do with the simultaneously pressed notes.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self << self._get_staff().convertToDuration(ra.Measures(1))  # By default a Scale and a Chord has one Measure duration
        self._inversion: int        = 0
        self._arpeggio: og.Arpeggio = og.Arpeggio("None")
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def inversion(self, inversion: int = 1) -> Self:
        self._inversion = inversion
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a KeyScale,
        those Parameters are the ones of the Element, like Position and Duration,
        together with the ones of a Note, like Duration and Pitch,
        plus the Scale and Mode, the last one as 1 by default.

        Examples
        --------
        >>> scale = KeyScale()
        >>> scale % str() >> Print()
        Major
        >>> scale << "minor"
        >>> scale % str() >> Print()
        minor
        >>> scale % list() >> Print()
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Inversion():    return ou.Inversion() << od.Pipe(self._inversion)
                    case og.Arpeggio():     return self._arpeggio
                    case _:                 return super().__mod__(operand)
            case ou.Inversion():    return ou.Inversion() << od.Pipe(self._inversion)
            case og.Arpeggio():     return self._arpeggio.copy()
            case ou.Order() | ra.Swing() | ch.Chaos():
                                    return self._arpeggio % operand
            case list():            return self.get_component_elements()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pitch._scale  == other._pitch._scale \
                    and self._inversion     == other._inversion \
                    and self._arpeggio      == other._arpeggio
            case _:
                return super().__eq__(other)
            
    def _apply_inversion(self, notes: list[Note]) -> list[Note]:
        # Where the inversions are done
        inversion: int = self._inversion % len(notes)
        if inversion > 0:
            first_note = notes[inversion]
            not_first_note = True
            while not_first_note:   # Try to implement while inversion > 0 here
                not_first_note = False
                for single_note in notes:
                    if single_note._pitch < first_note._pitch:   # Critical operation
                        single_note << single_note % ou.Octave() + 1
                        if single_note % od.Pipe( int() ) < 128:
                            not_first_note = True # to result in another while loop
            # Final Octave adjustment
            octave_offset: ou.Octave = ou.Octave( self._inversion // len(notes) )
            for single_note in notes:
                single_note += octave_offset
        return notes
            
    def get_component_elements(self) -> list[Element]:
        scale_notes: list[Note] = []
        active_scale: list[int] = self._pitch._scale
        if not active_scale:
            active_scale = self._get_staff() % list()
        total_keys: int = sum(1 for key in active_scale if key != 0)
        for shifting in range(total_keys):
            new_note: Note = Note(self)
            scale_notes.append( new_note )
            new_note._pitch._transposition += shifting
        return self._arpeggio.arpeggiate( self._apply_inversion(scale_notes) )
    

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        self_plotlist: list[dict] = []
        for single_note in self.get_component_elements():
            self_plotlist.extend(single_note.getPlotlist(midi_track, position_beats, channels))
        return self_plotlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_note in self.get_component_elements():
            self_playlist.extend(single_note.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list[dict]:
        self_midilist: list[dict] = []
        for single_note in self.get_component_elements():
            self_midilist.extend(single_note.getMidilist(midi_track, position_beats))
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["inversion"]    = self.serialize( self._inversion )
        serialization["parameters"]["arpeggio"]     = self.serialize( self._arpeggio )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeyScale':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "inversion" in serialization["parameters"] and "arpeggio" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._inversion = self.deserialize( serialization["parameters"]["inversion"] )
            self._arpeggio  = self.deserialize( serialization["parameters"]["arpeggio"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyScale():
                super().__lshift__(operand)
                self._inversion = operand._inversion
                self._arpeggio  << operand._arpeggio
            case od.Pipe():
                match operand._data:
                    case ou.Inversion():    self._inversion = operand._data._unit
                    case og.Arpeggio():     self._arpeggio = operand._data
                    case _:                 super().__lshift__(operand)
            case ou.Inversion():
                self._inversion = operand._unit
            case og.Arpeggio() | ou.Order() | ra.Swing() | ch.Chaos():
                self._arpeggio << operand
            case _:
                super().__lshift__(operand)
        return self


class PitchChord(KeyScale):
    """`Element -> Note -> KeyScale -> PitchChord`

    A `PitchChord` element allows the triggering of notes concerning specific degrees of a given `Scale`.
    Being a `Chord`, it's also able to have its own `Scale` to work on, besides being able to do inversions.

    Parameters
    ----------
    dict({0: [0, 2, 4]}) : Sets the specific offset pitches (list) to be pressed as `Note` for each `Octave` offset (int).
    Inversion(0) : The number of inversion of the `Chord`.
    Scale([]), KeySignature, str, None : Sets the `Scale` to be used, `None` uses the `defaults` scale.
    Arpeggio("None") : Sets the `Arpeggio` intended to do with the simultaneously pressed notes.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._offsets: list = [0.0, 2.0, 4.0]
        super().__init__( *parameters )

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.Pipe():
                match operand._data:
                    case dict():            return self._offsets
                    case _:                 return super().__mod__(operand)
            case dict():            return self.deep_copy(self._offsets)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) and self._offsets == other._offsets
            case _:
                return super().__eq__(other)
    
    def get_component_elements(self) -> list[Element]:
        chord_notes: list[Note] = []
        for pitch_offset in self._offsets:
            single_note: Note = Note(self)  # Owned by same clip
            chord_notes.append( single_note )
            single_note._pitch += pitch_offset
        return self._arpeggio.arpeggiate( self._apply_inversion(chord_notes) )


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["offsets"] = self.serialize( self._offsets )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "offsets" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._offsets = self.deserialize( serialization["parameters"]["offsets"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case PitchChord():
                super().__lshift__(operand)
                self._offsets = self.deep_copy( operand._offsets )
            case od.Pipe():
                match operand._data:
                    case list():
                        self._offsets = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                self._offsets = self.deep_copy( operand )
            case _:
                super().__lshift__(operand)
        return self

class Chord(KeyScale):
    """`Element -> Note -> KeyScale -> Chord`

    A `Chord` element allows the triggering of notes belonging to a specific `Scale`.

    Parameters
    ----------
    Size(3) : Sets the amount of nots being pressed, the default is a triad.
    Inversion(0) : The number of inversion of the `Chord`.
    Dominant(False) : Defines the chord as `Dominant`.
    Diminished(False) : Defines the chord as `Diminished`.
    Augmented(False) : Defines the chord as `Augmented`.
    Sus2(False) : Defines the chord with a 2nd Suspended.
    Sus4(False) : Defines the chord with a 4th Suspended.
    Scale([]), KeySignature, list, str, None : Sets the `Scale` to be used, `None` or `[]` uses the `defaults` scale.
    Arpeggio("None") : Sets the `Arpeggio` intended to do with the simultaneously pressed notes.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._size: int             = 3
        self._dominant: bool        = False
        self._diminished: bool      = False
        self._augmented: bool       = False
        self._sus2: bool            = False
        self._sus4: bool            = False
        super().__init__(*parameters)

    def size(self, size: int = 3) -> Self:
        self._size = size
        return self

    def dominant(self, dominant: bool = True) -> Self:
        self._dominant = dominant
        return self

    def diminished(self, diminished: bool = True) -> Self:
        self._diminished = diminished
        return self

    def augmented(self, augmented: bool = True) -> Self:
        self._augmented = augmented
        return self

    def sus2(self, sus2: bool = True) -> Self:
        self._sus2 = sus2
        return self

    def sus4(self, sus4: bool = True) -> Self:
        self._sus4 = sus4
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Chord,
        those Parameters are the ones of the Element, like Position and Duration,
        plus the ones of a Note, and the Scale, Degree, Inversion and others.

        Examples
        --------
        >>> chord = Chord("A") << Scale("minor") << Size("7th") << NoteValue(1/2)
        >>> chord % Degree() % str() >> Print()
        I
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Size():         return ou.Size() << od.Pipe(self._size)
                    case ou.Dominant():     return ou.Dominant() << od.Pipe(self._dominant)
                    case ou.Diminished():   return ou.Diminished() << od.Pipe(self._diminished)
                    case ou.Augmented():    return ou.Augmented() << od.Pipe(self._augmented)
                    case ou.Sus2():         return ou.Sus2() << od.Pipe(self._sus2)
                    case ou.Sus4():         return ou.Sus4() << od.Pipe(self._sus4)
                    case _:                 return super().__mod__(operand)
            case ou.Size():         return ou.Size() << od.Pipe(self._size)
            case ou.Dominant():     return ou.Dominant() << od.Pipe(self._dominant)
            case ou.Diminished():   return ou.Diminished() << od.Pipe(self._diminished)
            case ou.Augmented():    return ou.Augmented() << od.Pipe(self._augmented)
            case ou.Sus2():         return ou.Sus2() << od.Pipe(self._sus2)
            case ou.Sus4():         return ou.Sus4() << od.Pipe(self._sus4)
            case list():            return self.get_component_elements()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._size          == other._size \
                    and self._dominant      == other._dominant \
                    and self._diminished    == other._diminished \
                    and self._augmented     == other._augmented \
                    and self._sus2          == other._sus2 \
                    and self._sus4          == other._sus4
            case _:
                return super().__eq__(other)
    
    def get_component_elements(self) -> list[Element]:

        chord_notes: list[Note] = []
        for key_i in range(self._size):        # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...
            single_note: Note = Note(self)  # Owned by same clip
            chord_notes.append( single_note )
            key_degree: int = key_i * 2 + 1    # all odd numbers, 1, 3, 5, ...
            if key_degree == 3:   # Third
                if self._sus2:
                    key_degree -= 1
                if self._sus4:
                    key_degree += 1   # cancels out if both sus2 and sus4 are set to true
            single_note._pitch._transposition += key_degree - 1  # Sets the note Shifting by degrees (scale tones) (int is a degree)
            # Chromatic offsets by Semitones
            if key_degree == 7:         # flattens the Seventh
                if self._dominant:
                    single_note._pitch -= ou.Semitone(1)
            if key_degree == 3 or key_degree == 5:  # flattens the Third and Fifth
                if self._diminished:
                    single_note._pitch -= ou.Semitone(1)

        return self._arpeggio.arpeggiate( self._apply_inversion(chord_notes) )
    

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["size"]         = self.serialize( self._size )
        serialization["parameters"]["dominant"]     = self.serialize( self._dominant )
        serialization["parameters"]["diminished"]   = self.serialize( self._diminished )
        serialization["parameters"]["augmented"]    = self.serialize( self._augmented )
        serialization["parameters"]["sus2"]         = self.serialize( self._sus2 )
        serialization["parameters"]["sus4"]         = self.serialize( self._sus4 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "size" in serialization["parameters"] and "dominant" in serialization["parameters"] and "diminished" in serialization["parameters"] and 
            "augmented" in serialization["parameters"] and "sus2" in serialization["parameters"] and "sus4" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._size          = self.deserialize( serialization["parameters"]["size"] )
            self._dominant      = self.deserialize( serialization["parameters"]["dominant"] )
            self._diminished    = self.deserialize( serialization["parameters"]["diminished"] )
            self._augmented     = self.deserialize( serialization["parameters"]["augmented"] )
            self._sus2          = self.deserialize( serialization["parameters"]["sus2"] )
            self._sus4          = self.deserialize( serialization["parameters"]["sus4"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Chord():
                super().__lshift__(operand)
                self._size          = operand._size
                self._dominant      = operand._dominant
                self._diminished    = operand._diminished
                self._augmented     = operand._augmented
                self._sus2          = operand._sus2
                self._sus4          = operand._sus4
            case od.Pipe():
                match operand._data:
                    case ou.Size():                 self._size = operand._data._unit
                    case ou.Dominant():             self._dominant = operand._data.__mod__(od.Pipe( bool() ))
                    case ou.Diminished():           self._diminished = operand._data.__mod__(od.Pipe( bool() ))
                    case ou.Augmented():            self._augmented = operand._data.__mod__(od.Pipe( bool() ))
                    case ou.Sus2():                 self._sus2 = operand._data.__mod__(od.Pipe( bool() ))
                    case ou.Sus4():                 self._sus4 = operand._data.__mod__(od.Pipe( bool() ))
                    case _:                         super().__lshift__(operand)
            case ou.Size():                 self._size = operand._unit
            case str():
                operand = operand.strip()
                # Set Chord root note
                self._pitch << operand
                # Set Chord size
                self._size = ou.Size(od.Pipe( self._size ), operand)._unit
                # Set Chord scale
                if (operand.find("m") != -1 or operand.find("min") != -1 or operand in {'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'}) \
                    and operand.find("dim") == -1:
                    self._pitch << "minor"
                else:
                    self._pitch << "Major"
                self.set_all(operand)
            case ou.Dominant():
                if operand:
                    self.set_all()
                self._dominant = operand.__mod__(od.Pipe( bool() ))
            case ou.Diminished():
                if operand:
                    self.set_all()
                self._diminished = operand.__mod__(od.Pipe( bool() ))
            case ou.Augmented():
                if operand:
                    self.set_all()
                self._augmented = operand.__mod__(od.Pipe( bool() ))
            case ou.Sus2():
                if operand:
                    self.set_all()
                self._sus2 = operand.__mod__(od.Pipe( bool() ))
            case ou.Sus4():
                if operand:
                    self.set_all()
                self._sus4 = operand.__mod__(od.Pipe( bool() ))
            case _: super().__lshift__(operand)
        return self
    
    def set_all(self, data: any = False):    # mutual exclusive
        self._dominant      = ou.Dominant(od.Pipe( self._dominant ), data).__mod__(od.Pipe( bool() ))
        self._diminished    = ou.Diminished(od.Pipe( self._diminished ), data).__mod__(od.Pipe( bool() ))
        self._augmented     = ou.Augmented(od.Pipe( self._augmented ), data).__mod__(od.Pipe( bool() ))
        self._sus2          = ou.Sus2(od.Pipe( self._sus2 ), data).__mod__(od.Pipe( bool() ))
        self._sus4          = ou.Sus4(od.Pipe( self._sus4 ), data).__mod__(od.Pipe( bool() ))

class Retrigger(Note):
    """`Element -> Note -> Retrigger`

    A `Retrigger` element allows the repeated triggering of a `Note`.

    Parameters
    ----------
    Number(16) : The number above the notation beam with 3 as being a triplet.
    Swing(0.5) : The ratio of time the `Note` is pressed.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._number: int       = 16
        self._swing: Fraction   = ra.Swing(0.5)._rational
        super().__init__()
        self._duration_beats  *= 2 # Equivalent to twice single note duration
        self._gate      = ra.Gate(0.5)._rational
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def number(self, number: int = 16) -> Self:
        self._number = number
        return self

    def swing(self, swing: float = 0.5) -> Self:
        self._swing = Fraction(swing)
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Retrigger,
        those Parameters are the ones of the Element, like Position and Duration,
        plus the ones of a Note and the Number as 16 by default.

        Examples
        --------
        >>> retrigger = Retrigger("G") << Number(32)
        >>> retrigger % Number() % int() >> Print()
        32
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Number():       return operand._data << od.Pipe(self._number)
                    case ra.Swing():        return operand._data << od.Pipe(self._swing)
                    case _:                 return super().__mod__(operand)
            case ou.Number():       return ou.Number() << od.Pipe(self._number)
            case ra.Swing():        return ra.Swing() << od.Pipe(self._swing)
            # Returns the SYMBOLIC value of each note
            case ra.Duration():
                return operand.copy() << od.Pipe( self._duration_beats / 2 )
            case ra.NoteValue():
                return operand.copy() << self % ra.Duration()
            case float():           return self % ra.NoteValue() % float()
            case list():            return self.get_component_elements()
            case _:                 return super().__mod__(operand)

    def get_component_elements(self) -> list[Element]:
        retrigger_notes: list[Note] = []
        self_iteration: int = 0
        note_position: ra.Position = self._get_staff().convertToPosition(ra.Beats(self._position_beats))
        single_note_duration: ra.Duration = ra.Duration( self._duration_beats/(self._number) ) # Already 2x single note duration
        for _ in range(self._number):
            swing_ratio = self._swing
            if self_iteration % 2:
                swing_ratio = 1 - swing_ratio
            note_duration: ra.Duration = single_note_duration * 2 * swing_ratio
            retrigger_notes.append( Note(self, note_duration, note_position) )
            note_position += note_duration
            self_iteration += 1
        return retrigger_notes

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        self_plotlist: list[dict] = []
        for single_note in self.get_component_elements():
            self_plotlist.extend(single_note.getPlotlist(midi_track, position_beats, channels))
        return self_plotlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_note in self.get_component_elements():
            self_playlist.extend(single_note.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list[dict]:
        self_midilist: list[dict] = []
        for single_note in self.get_component_elements():
            self_midilist.extend(single_note.getMidilist(midi_track, position_beats))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["number"]   = self.serialize( self._number )
        serialization["parameters"]["swing"]    = self.serialize( self._swing )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "number" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._number    = self.deserialize( serialization["parameters"]["number"] )
            self._swing     = self.deserialize( serialization["parameters"]["swing"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Retrigger():
                super().__lshift__(operand)
                self._number  = operand._number
                self._swing     = operand._swing
            case od.Pipe():
                match operand._data:
                    case ou.Number():               self._number = operand._data.__mod__(od.Pipe( int() ))
                    case ra.Swing():                self._swing = operand._data._rational
                    case _:                         super().__lshift__(operand)
            case ou.Number():
                if operand > 0:
                    self._number = operand.__mod__(od.Pipe( int() ))
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ra.Duration():
                self._duration_beats = operand._rational * 2  # Equivalent to two sized Notes
            case ra.NoteValue():
                self << ra.Duration(self, operand)
            case float():
                self << ra.NoteValue(operand)
            case _:
                super().__lshift__(operand)
        return self

class Triplet(Retrigger):
    """`Element -> Note -> Retrigger -> Triplet`

    A `Triplet` is the repetition of a given Note three times on a row Triplets have each \
        Note Duration set to the following Values:

        +----------+-------------+-------------------+-----------------+
        | Notation | Note Value  | Note Duration     | Total Duration  |
        +----------+-------------+-------------------+-----------------+
        | 1T       | 1           | 1    * 2/3 = 2/3  | 1    * 2 = 2    |
        | 1/2T     | 1/2         | 1/2  * 2/3 = 1/3  | 1/2  * 2 = 1    |
        | 1/4T     | 1/4         | 1/4  * 2/3 = 1/6  | 1/4  * 2 = 1/2  |
        | 1/8T     | 1/8         | 1/8  * 2/3 = 1/12 | 1/8  * 2 = 1/4  |
        | 1/16T    | 1/16        | 1/16 * 2/3 = 1/24 | 1/16 * 2 = 1/8  |
        | 1/32T    | 1/32        | 1/32 * 2/3 = 1/48 | 1/32 * 2 = 1/16 |
        +----------+-------------+-------------------+-----------------+

    Parameters
    ----------
    Number(3) : The number above the notation beam with 3 as being a triplet, this can't be changed for `Triplet`.
    Swing(0.5) : The ratio of time the `Note` is pressed.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._number = 3
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ou.Number():
                return self # disables the setting of Number, always 3
            case _:
                super().__lshift__(operand)
        return self

class Tuplet(Element):
    """`Element -> Tuplet`

    A `Tuplet` is a group of elements played in sequence where its len is equivalent to the `Number` of a `Retrigger`.

    Parameters
    ----------
    list([Note(ra.Gate(0.5)), Note(ra.Gate(0.5)), Note(ra.Gate(0.5))]) : List with all Tuplet elements.
    Swing(0.5) : The ratio of time the `Note` is pressed.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(settings), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._swing: Fraction           = Fraction(0.5)
        self._elements: list[Element]   = [Note(ra.Gate(0.5)), Note(ra.Gate(0.5)), Note(ra.Gate(0.5))]
        super().__init__()
        self._duration_beats  *= 2 # Equivalent to twice single note duration
        self.set_elements_duration()
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def swing(self, swing: float = 0.5) -> Self:
        self._swing = Fraction(swing)
        return self

    def elements(self, elements: Optional[List['Element']] = None) -> Self:
        if isinstance(elements, list) and all(isinstance(element, Element) for element in elements):
            self._elements = elements
        return self

    def set_elements_duration(self):
        if len(self._elements) > 0:
             # Already 2x single note duration
            elements_duration = self._duration_beats / len(self._elements) # from 2 notes to division
            if len(self._elements) == 2:
                 # Already 2x single note duration
                elements_duration = self._duration_beats/2 * 3/2 # from 3 notes to 2
            for single_element in self._elements:
                single_element << ra.Duration( elements_duration )

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Tuplet,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Number and a List of Elements.

        Examples
        --------
        >>> tuplet = Tuplet( Note("C"), Note("F"), Note("G"), Note("C") )
        >>> tuplet % Number() % int() >> Print()
        4
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ra.Swing():        return ra.Swing() << od.Pipe(self._swing)
                    case list():            return self._elements
                    case _:                 return super().__mod__(operand)
            case ra.Swing():        return ra.Swing() << od.Pipe(self._swing)
            case ou.Number():       return ou.Number() << len(self._elements)
            case ra.Duration() | ra.NoteValue():
                return operand << od.Pipe( self._duration_beats / 2 )
            case list():            return self.get_component_elements()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._swing     == other._swing \
                    and self._elements  == other._elements
            case _:
                return super().__eq__(other)
    
    def get_component_elements(self) -> list[Element]:
        tuplet_elements: list[Element] = []
        element_position: ra.Position = self % ra.Position()
        self_iteration: int = 0
        for single_element in self._elements:
            element_duration = single_element % od.Pipe( ra.Duration() )
            tuplet_elements.append(single_element.copy() << element_position)
            swing_ratio = self._swing
            if self_iteration % 2:
                swing_ratio = 1 - swing_ratio
            element_position += element_duration * 2 * swing_ratio
            self_iteration += 1
        return tuplet_elements

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        self_plotlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_plotlist.extend(single_element.getPlotlist(midi_track, position_beats, channels))
        return self_plotlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_playlist.extend(single_element.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list[dict]:
        self_midilist: list[dict] = []
        for single_element in self.get_component_elements():
            self_midilist.extend(single_element.getMidilist(midi_track, position_beats))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["swing"]    = self.serialize( self._swing )
        serialization["parameters"]["elements"] = self.serialize( self._elements )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Tuplet':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "swing" in serialization["parameters"] and "elements" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._swing     = self.deserialize( serialization["parameters"]["swing"] )
            self._elements  = self.deserialize( serialization["parameters"]["elements"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        if not isinstance(operand, tuple):
            for single_element in self._elements:
                single_element << operand
        match operand:
            case Tuplet():
                super().__lshift__(operand)
                self._swing     = operand._swing
                self._elements  = self.deep_copy(operand % od.Pipe( list() ))
            case od.Pipe():
                match operand._data:
                    case ra.Swing():            self._swing = operand._data._rational
                    case list():                self._elements = operand._data
                    case _:                     super().__lshift__(operand)
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ra.Duration() | ra.NoteValue():
                self._duration_beats = operand._rational * 2  # Equivalent to two sized Notes
            case list():
                                                                     # Rest because is the root super class with Duration
                if len(operand) > 0 and all(isinstance(single_element, Rest) for single_element in operand):
                    self._elements = self.deep_copy(operand)
            case _:
                super().__lshift__(operand)
        self.set_elements_duration()
        return self


class Automation(Element):
    """`Element -> Automation`

    An `Automation` is an element that controls an continuous device parameter, like Volume, or a Pitch Bend.

    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._value: int = 0
        super().__init__()
        self._duration_beats = self._get_staff()._quantization   # Equivalent to one Step
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a ControlChange,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Controller Number and Value as Number and Value.

        Examples
        --------
        >>> controller = Controller("Modulation")
        >>> controller % Number() % int() >> Print()
        1
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Value():            return operand._data << od.Pipe(self._value)
                    case ou.MSB():              return ou.MSB() << od.Pipe(self._value)
                    case _:                     return super().__mod__(operand)
            case int():                 return self._value
            case ou.Value():            return operand.copy() << self._value
            case ou.MSB():              return ou.MSB() << self._value
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: Any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._value == other._value
            case _:
                return super().__eq__(other)

    def __lt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Automation():
                # Adds predictability in sorting and consistency in clipping
                if self._position_beats == other._position_beats:
                    if self._value == other._value:
                        return self._channel < other._channel
                    return self._value < other._value
                return self._position_beats < other._position_beats
            case Element():
                return super().__lt__(other)
            case _:
                return self % other < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Automation():
                # Adds predictability in sorting and consistency in clipping
                if self._position_beats == other._position_beats:
                    if self._value == other._value:
                        return self._channel > other._channel
                    return self._value > other._value
                return self._position_beats > other._position_beats
            case Element():
                return super().__gt__(other)
            case _:
                return self % other > other
    

    def _get_msb_value(self) -> int:
        return self._value

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), channels: dict[str, set[int]] = None) -> list[dict]:
        if not self._enabled:
            return []
        
        if channels is not None:
            channels["automation"].add(self._channel)

        self_plotlist: list[dict] = []
        
        position_on: Fraction = position_beats + self._position_beats

        # Midi validation is done in the JsonMidiPlayer program
        self_plotlist.append(
            {
                "automation": {
                    "position": position_on,
                    "value": self._get_msb_value(),
                    "channel": self._channel
                }
            }
        )

        return self_plotlist


    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["value"] = self.serialize( self._value )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "value" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._value = self.deserialize( serialization["parameters"]["value"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Automation():
                super().__lshift__(operand)
                self._value = operand._value
            case od.Pipe():
                match operand._data:
                    case ou.Value():            self._value = operand._data._unit
                    case ou.MSB():              self._value = operand._data._unit
                    case _:                     super().__lshift__(operand)
            case int():
                self._value = operand
            case ou.Value() | ou.MSB():
                self._value = operand._unit
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._value += operand  # Specific and compounded parameter
                return self
            case ou.Value() | ou.MSB():
                self._value += operand._unit  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._value -= operand  # Specific and compounded parameter
                return self
            case ou.Value() | ou.MSB():
                self._value -= operand._unit  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)


class ControlChange(Automation):
    """`Element -> Automation -> ControlChange`

    A `ControlChange` is an element that represents the CC midi messages of a Device.

    Parameters
    ----------
    Controller(settings) : An `Operand` that represents parameters like the `Number` of the controller being changed.
    Value(settings), int : The CC value to be set on the Device controller.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._controller: og.Controller = og.settings % og.Controller()
        self._value                     = ou.Number.getDefaultValue(self._controller._number_msb)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def controller(self, msb: Optional[int] = None, lsb: Optional[int] = None) -> Self:
        self._controller = og.Controller(
                ou.Number(msb), ou.LSB(lsb)
            )
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a ControlChange,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Controller Number and Value as Number and Value.

        Examples
        --------
        >>> controller = Controller("Modulation")
        >>> controller % Number() % int() >> Print()
        1
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case og.Controller():       return self._controller
                    case _:                     return super().__mod__(operand)
            case og.Controller():       return self._controller.copy()
            case ou.Number() | ou.LSB() | ou.HighResolution() | dict():
                return self._controller % operand
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: Any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._controller == other._controller
            case _:
                return super().__eq__(other)


    def _get_msb_value(self) -> int:
        
        if self._controller._nrpn:

            cc_99_msb, cc_98_lsb, cc_6_msb, cc_38_lsb = self._controller._midi_nrpn_values(self._value)
            return cc_6_msb
        else:

            msb_value, lsb_value = self._controller._midi_msb_lsb_values(self._value)
            return msb_value
            

    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        if not self._enabled:
            return []

        self_position_beats: Fraction = position_beats + self._position_beats
        self_position_min: Fraction = og.settings.beats_to_minutes(self_position_beats)

        time_ms: float = o.minutes_to_time_ms(self_position_min)
        devices: list[str] = midi_track._devices if midi_track else og.settings._devices

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist: list[dict] = []
        
        if devices_header:
            self_playlist.append(
                {
                    "devices": devices
                }
            )

        if self._controller._nrpn:

            cc_99_msb, cc_98_lsb, cc_6_msb, cc_38_lsb = self._controller._midi_nrpn_values(self._value)

            self_playlist.extend([
                {
                    "time_ms": time_ms,
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & self._channel - 1,
                        "data_byte_1": 99,
                        "data_byte_2": cc_99_msb
                    }
                },
                {
                    "time_ms": time_ms,
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & self._channel - 1,
                        "data_byte_1": 98,
                        "data_byte_2": cc_98_lsb
                    }
                },
                {
                    "time_ms": time_ms,
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & self._channel - 1,
                        "data_byte_1": 6,
                        "data_byte_2": cc_6_msb
                    }
                }
            ])

            if self._controller._high:

                self_playlist.append(
                    {
                        "time_ms": time_ms,
                        "midi_message": {
                            "status_byte": 0xB0 | 0x0F & self._channel - 1,
                            "data_byte_1": 38,
                            "data_byte_2": cc_38_lsb
                        }
                    }
                )

        else:

            msb_value, lsb_value = self._controller._midi_msb_lsb_values(self._value)

            self_playlist.append(
                {
                    "time_ms": time_ms,
                    "midi_message": {
                        "status_byte": 0xB0 | 0x0F & self._channel - 1,
                        "data_byte_1": self._controller._number_msb,
                        "data_byte_2": msb_value
                    }
                }
            )

            if self._controller._high:

                self_playlist.append(
                    {
                        "time_ms": time_ms,
                        "midi_message": {
                            "status_byte": 0xB0 | 0x0F & self._channel - 1,
                            "data_byte_1": self._controller._lsb,
                            "data_byte_2": lsb_value
                        }
                    }
                )
        
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list[dict]:
        if not self._enabled:
            return []
        self_midilist: list[dict] = super().getMidilist(midi_track, position_beats)
        self_midilist[0]["event"] = "ControllerEvent"

        # Validation is done by midiutil Midi Range Validation

        if self._controller._nrpn:

            cc_99_msb, cc_98_lsb, cc_6_msb, cc_38_lsb = self._controller._midi_nrpn_values(self._value)

            self_midilist[0]["number"]      = 99
            self_midilist[0]["value"]       = cc_99_msb

            self_midilist[1] = self_midilist[0].copy()
            self_midilist[1]["number"]      = 98
            self_midilist[1]["value"]       = cc_98_lsb

            self_midilist[2] = self_midilist[0].copy()
            self_midilist[2]["number"]      = 6
            self_midilist[2]["value"]       = cc_6_msb

            if self._controller._high:

                self_midilist[3] = self_midilist[0].copy()
                self_midilist[3]["number"]      = 38
                self_midilist[3]["value"]       = cc_38_lsb

        else:

            msb_value, lsb_value = self._controller._midi_msb_lsb_values(self._value)

            self_midilist[0]["number"]      = self._controller._number_msb
            self_midilist[0]["value"]       = msb_value

            if self._controller._high:

                self_midilist[1] = self_midilist[0].copy()
                self_midilist[1]["number"]      = self._controller._lsb
                self_midilist[1]["value"]       = lsb_value

        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["controller"]   = self.serialize( self._controller )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "controller" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._controller    = self.deserialize( serialization["parameters"]["controller"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ControlChange():
                super().__lshift__(operand)
                self._controller    << operand._controller
            case od.Pipe():
                match operand._data:
                    case og.Controller():       self._controller = operand._data
                    case _:                     super().__lshift__(operand)
            case og.Controller() | ou.Number() | ou.LSB() | ou.HighResolution() | str() | dict():
                self._controller << operand
            case _: super().__lshift__(operand)
        return self

class BankSelect(ControlChange):
    """`Element -> Automation -> ControlChange -> BankSelect`

    A `BankSelect` is a specific CC message that is used to select a Bank of presents.

    Parameters
    ----------
    Controller(ou.MSB(0), ou.LSB(32), ou.NRPN(False)) : The default and immutable `Controller` parameters \
        associated to Bank Select, namely, 0 and 32 for MSB and LSB respectively.
    Value(0), int : Selects the presets Bank in the Device.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        # 0 -  Bank Select (MSB)
        # 32 - Bank Select (LSB)
        self._controller << (ou.MSB(0), ou.LSB(32), ou.NRPN(False))
        self._value = 0  # Value Byte: 0 (Bank A) (Data Byte 2) (internally, -1 means no Bank selected)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a ControlChange,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Controller Number and Value as Number and Value.

        Examples
        --------
        >>> controller = Controller("Modulation")
        >>> controller % Number() % int() >> Print()
        1
        """
        match operand:
            # Bank Select is 1 based and not 0 based
            case int():                 return self._value + 1
            case ou.Value():            return ou.Value(self._value + 1)
            case _:                     return super().__mod__(operand)

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            # Bank Select is 1 based and not 0 based
            case int():
                self._value = operand - 1
            case ou.Value():
                self._value = operand._unit - 1
            case _:
                super().__lshift__(operand)
        self._controller << (ou.MSB(0), ou.LSB(32), ou.NRPN(False))
        return self


# Channel mode messages determine how an instrument will process MIDI voice messages.

# 1st Data Byte      Description                Meaning of 2nd Data Byte
# -------------   ----------------------        ------------------------
#     79        Reset all  controllers            None; set to 0
#     7A        Local control                     0 = off; 127  = on
#     7B        All notes off                     None; set to 0
#     7C        Omni mode off                     None; set to 0
#     7D        Omni mode on                      None; set to 0
#     7E        Mono mode on (Poly mode off)      **
#     7F        Poly mode on (Mono mode off)      None; set to 0

# ** if value = 0 then the number of channels used is determined by the receiver;
#   all other values set a specific number of channels, beginning with the current basic channel.

class ValueZero(ControlChange):
    """`Element -> Automation -> ControlChange -> ValueZero`

    A `ValueZero` is a specific CC message that has a `Value` of 0.

    Parameters
    ----------
    Controller(settings) : An `Operand` that represents parameters like the `Number` of the controller being changed.
    Value(0) : The default `Value` of 0 is immutable.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._value = 0                     # None
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        # No need to processes the tailed self operands or the Frame operand given the total delegation in super()
        super().__lshift__(operand)
        self._value = 0                     # None
        return self

    def __iadd__(self, operand: any) -> Self:
        return self

    def __isub__(self, operand: any) -> Self:
        return self

class ResetAllControllers(ValueZero):
    """`Element -> Automation -> ControlChange -> ValueZero -> ResetAllControllers`

    A `ResetAllControllers` is a specific CC message that results in a Device resting all its controller to their defaults.

    Parameters
    ----------
    Controller(ou.Number(121)) : The default and immutable `Controller` parameters that triggers a controllers reset.
    Value(0) : The default `Value` of 0 is immutable.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._controller << ou.Number(121)  # 0x79
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        # No need to processes the tailed self operands or the Frame operand given the total delegation in super()
        super().__lshift__(operand)
        self._controller << ou.Number(121)  # 0x79
        return self

class LocalControl(ControlChange):
    """`Element -> Automation -> ControlChange -> LocalControl`

    A `LocalControl` is a specific CC message that sets the Device Local control On or Off with 1 or 0 respectively.

    Parameters
    ----------
    Controller(ou.Number(122)) : The default and immutable `Controller` associated with the Device Local control.
    Value(0) : By default the value is 0, Local control Off.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._controller << ou.Number(122)  # 0x7A
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        # No need to processes the tailed self operands or the Frame operand given the total delegation in super()
        super().__lshift__(operand)
        self._controller << ou.Number(122)  # 0x7A
        return self

class AllNotesOff(ValueZero):
    """`Element -> Automation -> ControlChange -> ValueZero -> AllNotesOff`

    A `AllNotesOff` is a specific CC message that results in all notes being turned Off in the Device.

    Parameters
    ----------
    Controller(ou.Number(123)) : The default and immutable `Controller` parameters that turns notes Off.
    Value(0) : The default `Value` of 0 is immutable.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._controller << ou.Number(123)  # Control Change Number (CC): 123   (Data Byte 1)
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        # No need to processes the tailed self operands or the Frame operand given the total delegation in super()
        super().__lshift__(operand)
        self._controller << ou.Number(123)
        return self

class OmniModeOff(ValueZero):
    """`Element -> Automation -> ControlChange -> ValueZero -> OmniModeOff`

    A `OmniModeOff` is a specific CC message that results in turning Off the Device Omni Mode.

    Parameters
    ----------
    Controller(ou.Number(124)) : The default and immutable `Controller` parameters that turns Omni Mode Off.
    Value(0) : The default `Value` of 0 is immutable.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._controller << ou.Number(124)  # 0x7C
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        # No need to processes the tailed self operands or the Frame operand given the total delegation in super()
        super().__lshift__(operand)
        self._controller << ou.Number(124)  # 0x7C
        return self

class OmniModeOn(ValueZero):
    """`Element -> Automation -> ControlChange -> ValueZero -> OmniModeOn`

    A `OmniModeOn` is a specific CC message that results in turning On the Device Omni Mode.

    Parameters
    ----------
    Controller(ou.Number(125)) : The default and immutable `Controller` parameters that turns Omni Mode On.
    Value(0) : The default `Value` of 0 is immutable.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._controller << ou.Number(125)  # 0x7D
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        # No need to processes the tailed self operands or the Frame operand given the total delegation in super()
        super().__lshift__(operand)
        self._controller << ou.Number(125)  # 0x7D
        return self

class MonoMode(ControlChange):
    """`Element -> Automation -> ControlChange -> MonoMode`

    A `MonoMode` is a specific CC message that results in setting the Device Mono Mode.

    Parameters
    ----------
    Controller(ou.Number(126)) : The default and immutable `Controller` parameters that set the Mono Mode.
    Value(0) : By default the value is 0 , in which case the number of channels used is determined by the receiver; \
        all other values set a specific number of channels, beginning with the current basic channel.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._controller << ou.Number(126)  # 0x7E
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        # No need to processes the tailed self operands or the Frame operand given the total delegation in super()
        super().__lshift__(operand)
        self._controller << ou.Number(126)  # 0x7E
        return self

class PolyModeOn(ValueZero):
    """`Element -> Automation -> ControlChange -> ValueZero -> PolyModeOn`

    A `PolyModeOn` is a specific CC message that results in turning On the Device Poly Mode.

    Parameters
    ----------
    Controller(ou.Number(127)) : The default and immutable `Controller` parameters that turns Poly Mode On.
    Value(0) : The default `Value` of 0 is immutable.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._controller << ou.Number(127)  # 0x7F
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # CHAINABLE OPERATIONS

    def __lshift__(self, operand: any) -> Self:
        # No need to processes the tailed self operands or the Frame operand given the total delegation in super()
        super().__lshift__(operand)
        self._controller << ou.Number(127)  # 0x7F
        return self


class PitchBend(Automation):
    """`Element -> Automation -> PitchBend`

    A `PitchBend` is an element that controls the Device Pitch Bend wheel.

    Parameters
    ----------
    Bend(0), int: Value that ranges from -8192 to 8191, or, from -(64*128) to (64*128 - 1).
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._value: int    = 64
        self._lsb: int      = 0
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def bend(self, bend: int = 0) -> Self:
        self._value, self._lsb = self._get_msb_lsb( bend )
        return self


    @staticmethod
    def _get_msb_lsb(bend: int) -> tuple[int]:
        # from -8192 to 8191
        amount = 8192 + bend        # 2^14 = 16384, 16384 / 2 = 8192
        amount = max(min(amount, 16383), 0) # midi safe
        msb: int = amount >> 7      # MSB - total of 14 bits, 7 for each side, 2^7 = 128
        lsb: int = amount & 0x7F    # LSB - 0x7F = 127, 7 bits with 1s, 2^7 - 1
        return msb, lsb

    @staticmethod
    def _get_bend(msb: int, lsb: int) -> int:
        amount: int = msb << 7 | lsb & 0x7F
        amount = max(min(amount, 16383), 0) # midi safe
        # from -8192 to 8191
        bend: int = amount - 8192
        return bend


    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a PitchBend,
        those Parameters are the ones of the Element, like Position and Duration,
        and the PitchBend bend with 0 as default.

        Examples
        --------
        >>> pitch_bend = PitchBend(8190 / 2 + 1)
        >>> pitch_bend % int() >> Print()
        4096
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Bend():
                        return ou.Bend() << od.Pipe(self._get_bend(self._value, self._lsb))
                    case ou.LSB():
                        return ou.LSB() << od.Pipe(self._lsb)
                    case _:
                        return super().__mod__(operand)
            case int():
                return self._get_bend(self._value, self._lsb)
            case ou.Bend():
                return ou.Bend() << self._get_bend(self._value, self._lsb)
            case ou.LSB():
                return ou.LSB() << od.Pipe(self._lsb)
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._lsb == other._lsb
            case _:
                return super().__eq__(other)


    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        
        self_position_beats: Fraction = position_beats + self._position_beats
        self_position_min: Fraction = og.settings.beats_to_minutes(self_position_beats)
        
        devices: list[str] = midi_track._devices if midi_track else og.settings._devices

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist: list[dict] = []
        
        if devices_header:
            self_playlist.append(
                {
                    "devices": devices
                }
            )

        self_playlist.append(
            {
                "time_ms": o.minutes_to_time_ms(self_position_min),
                "midi_message": {
                    "status_byte": 0xE0 | 0x0F & self._channel - 1,
                    "data_byte_1": self._lsb,
                    "data_byte_2": self._value
                }
            }
        )

        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position_beats)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "PitchWheelEvent"
        self_midilist[0]["value"]       = self._get_bend(self._value, self._lsb)
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["lsb"] = self.serialize(self._lsb)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "lsb" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._lsb = self.deserialize( serialization["parameters"]["lsb"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case PitchBend():
                super().__lshift__(operand)
                self._value = operand._value
                self._lsb   = operand._lsb
            case od.Pipe():
                match operand._data:
                    case ou.Bend():
                        self._value = operand._data._unit
                    case ou.Bend():
                        self._lsb = operand._data._unit
                    case _:
                        super().__lshift__(operand)
            case int():
                self._value, self._lsb = self._get_msb_lsb( operand )
            case ou.Bend():
                self._value, self._lsb = self._get_msb_lsb( operand._unit )
            case ou.LSB():
                self._lsb = operand._unit
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                bend: int = self._get_bend(self._value, self._lsb)
                bend += operand
                self._value, self._lsb = self._get_msb_lsb( bend )
                return self
            case ou.Bend():
                bend: int = self._get_bend(self._value, self._lsb)
                bend += operand._unit
                self._value, self._lsb = self._get_msb_lsb( bend )
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                bend: int = self._get_bend(self._value, self._lsb)
                bend -= operand
                self._value, self._lsb = self._get_msb_lsb( bend )
                return self
            case ou.Bend():
                bend: int = self._get_bend(self._value, self._lsb)
                bend -= operand._unit
                self._value, self._lsb = self._get_msb_lsb( bend )
                return self
            case _:
                return super().__isub__(operand)


class Aftertouch(Automation):
    """`Element -> Automation -> Aftertouch`

    An `Aftertouch` is an element that controls the pressure on all keys being played.

    Parameters
    ----------
    Pressure(0), int: Value that ranges from 0 to 127, or, from (0) to (128 - 1).
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__(*parameters)

    def pressure(self, pressure: int = 0) -> Self:
        self._value = pressure
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a Aftertouch,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Aftertouch pressure with 0 as default.

        Examples
        --------
        >>> aftertouch = Aftertouch(2) << Pressure(128 / 2)
        >>> aftertouch % Pressure() % int() >> Print()
        64
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Pressure():     return ou.Pressure() << od.Pipe(self._value)
                    case _:                 return super().__mod__(operand)
            case int():             return self._value
            case ou.Pressure():     return ou.Pressure() << od.Pipe(self._value)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._value == other._value
            case _:
                return super().__eq__(other)
    
    
    def _get_msb_value(self) -> int:
        return self._value


    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list:
        if not self._enabled:
            return []
        
        self_position_beats: Fraction = position_beats + self._position_beats
        self_position_min: Fraction = og.settings.beats_to_minutes(self_position_beats)

        devices: list[str] = midi_track._devices if midi_track else og.settings._devices

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist: list[dict] = []
        
        if devices_header:
            self_playlist.append(
                {
                    "devices": devices
                }
            )

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist.append(
            {
                "time_ms": o.minutes_to_time_ms(self_position_min),
                "midi_message": {
                    "status_byte": 0xD0 | 0x0F & self._channel - 1,
                    "data_byte": self._value
                }
            }
        )

        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position_beats)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "ChannelPressure"
        self_midilist[0]["pressure"]    = self._value
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pressure"] = self.serialize( self._value )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pressure" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._value = self.deserialize( serialization["parameters"]["pressure"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Aftertouch():
                super().__lshift__(operand)
                self._value = operand._value
            case od.Pipe():
                match operand._data:
                    case ou.Pressure():         self._value = operand._data.__mod__(od.Pipe( int() ))
                    case _:                     super().__lshift__(operand)
            case int():
                self._value = operand
            case ou.Pressure():
                self._value = operand.__mod__(od.Pipe( int() ))
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._value += operand  # Specific and compounded parameter
                return self
            case ou.Pressure():
                self._value += operand._unit  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._value -= operand  # Specific and compounded parameter
                return self
            case ou.Pressure():
                self._value -= operand._unit  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)

class PolyAftertouch(Aftertouch):
    """`Element -> Automation -> PolyAftertouch`

    A `PolyAftertouch` is an element that controls the pressure on a particular key `Pitch` being played.

    Parameters
    ----------
    Pitch(settings) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Pressure(0), int: Value that ranges from 0 to 127, or, from (0) to (128 - 1).
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._pitch: og.Pitch  = og.Pitch()._set_owner_element(self)
        super().__init__(*parameters)

    def pitch(self, key: Optional[int] = 0, octave: Optional[int] = 4) -> Self:
        self._pitch << ou.Key(key) << ou.Octave(octave)
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a PolyAftertouch,
        those Parameters are the ones of the Element, like Position and Duration,
        and the Key together with the PolyAftertouch pressure with value 0 as default.

        Examples
        --------
        >>> poly_aftertouch = PolyAftertouch("E") << Pressure(128 / 2)
        >>> poly_aftertouch % Channel() >> Print(0)
        {'class': 'Channel', 'parameters': {'unit': 0}}
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case og.Pitch():    return self._pitch
                    case _:             return super().__mod__(operand)
            case og.Pitch():
                return self._pitch.copy()
            case ou.PitchParameter() | str() | og.Scale():
                return self._pitch % operand
            case ou.Octave():
                return self._pitch % ou.Octave()
            case _:
                return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pitch == other._pitch
            case _:
                return super().__eq__(other)
    

    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        if not self._enabled:
            return []

        self_position_beats: Fraction = position_beats + self._position_beats
        self_position_min: Fraction = og.settings.beats_to_minutes(self_position_beats)

        devices: list[str] = midi_track._devices if midi_track else og.settings._devices
        pitch_int: int = self._pitch.pitch_int()

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist: list[dict] = []
        
        if devices_header:
            self_playlist.append(
                {
                    "devices": devices
                }
            )

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist.append(
            {
                "time_ms": o.minutes_to_time_ms(self_position_min),
                "midi_message": {
                    "status_byte": 0xA0 | 0x0F & self._channel - 1,
                    "data_byte_1": pitch_int,
                    "data_byte_2": self._value
                }
            }
        )

        return self_playlist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pitch"] = self.serialize( self._pitch )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pitch" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pitch = self.deserialize( serialization["parameters"]["pitch"] )
            self._pitch._set_owner_element(self)
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case PolyAftertouch():
                super().__lshift__(operand)
                self._pitch << operand._pitch
            case od.Pipe():
                match operand._data:
                    case og.Pitch():            self._pitch = operand._data
                    case _:                     super().__lshift__(operand)
            case og.Pitch() | ou.PitchParameter() | None | og.Scale() | list() | str():
                                self._pitch << operand
            case _:             super().__lshift__(operand)
        return self

class ProgramChange(Element):
    """`Element -> ProgramChange`

    A `ProgramChange` is an element that selects the Device program or preset.

    Parameters
    ----------
    Program(1), int: Program number from 1 to 128.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._program: int  = 1
        self._bank: int     = 0
        self._high: bool    = False
        super().__init__(*parameters)

    def program(self, program: int | str = "Piano") -> Self:
        self._program = ou.Program(program)
        return self

    def __mod__(self, operand: o.T) -> o.T:
        """
        The % symbol is used to extract a Parameter, in the case of a ProgramChange,
        those Parameters are the ones of the Element, like Position and Duration,
        and the ProgramChange number with a value of 0 as default.

        Examples
        --------
        >>> program_change = ProgramChange(12)
        >>> program_change % Program() >> Print(0)
        {'class': 'Program', 'parameters': {'unit': 12}}
        """
        match operand:
            case od.Pipe():
                match operand._data:
                    case ou.Program():          return operand._data << self._program
                    case ou.Bank():             return operand._data << self._bank
                    case ou.HighResolution():   return operand._data << self._high
                    case _:                 return super().__mod__(operand)
            case int():                 return self._program
            case ou.Program():          return ou.Program(self._program)
            case ou.Bank():             return ou.Bank(self._bank)
            case ou.HighResolution():   return ou.HighResolution(self._high)
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._program == other._program \
                    and self._bank == other._bank and self._high == other._high
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        
        self_position_beats: Fraction = position_beats + self._position_beats
        self_position_min: Fraction = og.settings.beats_to_minutes(self_position_beats)

        devices: list[str] = midi_track._devices if midi_track else og.settings._devices

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist: list[dict] = []
        
        if devices_header:
            self_playlist.append(
                {
                    "devices": devices
                }
            )

        if self._bank > 0:
            # Has to pass self first to set equivalent parameters like position and staff
            self_playlist.extend(
                BankSelect(self, self % od.Pipe( ou.Bank() ), self % od.Pipe( ou.HighResolution() ))
                    .getPlaylist(devices_header=False)
            )

        self_playlist.append(
            {
                "time_ms": o.minutes_to_time_ms(self_position_min),
                "midi_message": {
                    "status_byte": 0xC0 | 0x0F & self._channel - 1,
                    "data_byte": self._program - 1
                }
            }
        )

        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0)) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position_beats)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "ProgramChange"
        self_midilist[0]["program"]     = self._program - 1
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["program"]  = self.serialize( self._program )
        serialization["parameters"]["bank"]     = self.serialize( self._bank )
        serialization["parameters"]["high"]     = self.serialize( self._high )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "program" in serialization["parameters"] and "bank" in serialization["parameters"] and "high" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._program   = self.deserialize( serialization["parameters"]["program"] )
            self._bank      = self.deserialize( serialization["parameters"]["bank"] )
            self._high      = self.deserialize( serialization["parameters"]["high"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ProgramChange():
                super().__lshift__(operand)
                self._program   = operand._program
                self._bank      = operand._bank
                self._high      = operand._high
            case od.Pipe():
                match operand._data:
                    case ou.Program():          self._program = operand._data._unit
                    case ou.Bank():             self._bank = operand._data._unit
                    case ou.HighResolution():   self._high = operand._data % bool()
                    case _:                     super().__lshift__(operand)
            case int():
                self._program = operand
            case ou.Program() | str():
                self._program = ou.Program(operand)._unit
            case ou.Bank():
                self._bank = operand._unit
            case ou.HighResolution():
                self._high = operand % bool()
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._program += operand  # Specific and compounded parameter
            case ou.Program():
                self += operand._unit
            case _:
                return super().__iadd__(operand)
        return self

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._program -= operand  # Specific and compounded parameter
            case ou.Program():
                self -= operand._unit
            case _:
                return super().__isub__(operand)
        return self


class Panic(Element):
    """`Element -> Panic`

    A `Panic` is an element used to do a full state reset on the midi Device on all channels.

    Parameters
    ----------
    Position(0), TimeValue, TimeUnit, int : The position on the staff in `Measures`.
    Duration(Quantization(settings)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16.
    Channel(settings) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = Fraction(0), devices_header = True) -> list[dict]:
        if not self._enabled:
            return []

        devices: list[str] = midi_track._devices if midi_track else og.settings._devices

        # Midi validation is done in the JsonMidiPlayer program
        self_playlist: list[dict] = []
        
        if devices_header:
            self_playlist.append(
                {
                    "devices": devices
                }
            )

        # Cycles all channels, from 1 to 16
        for channel in range(1, 17):

            # self needs to be given to each of these elements in order to preserve self parameters like position

            self_playlist.extend(AllNotesOff(self, ou.Channel(channel))
                .getPlaylist(midi_track, position_beats, False))
            self_playlist.extend(PitchBend(self, ou.Channel(channel), 0)
                .getPlaylist(midi_track, position_beats, False))

            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(10), ou.Value(64))
                .getPlaylist(midi_track, position_beats, False))   # 10 - Pan
            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(64), ou.Value(0))
                .getPlaylist(midi_track, position_beats, False))   # 64 - Pedal (sustain)
            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(1), ou.Value(0))
                .getPlaylist(midi_track, position_beats, False))   # 1 - Modulation
            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(7), ou.Value(100))
                .getPlaylist(midi_track, position_beats, False))   # 7 - Volume
            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(11), ou.Value(127))
                .getPlaylist(midi_track, position_beats, False))   # 11 - Expression

            self_playlist.extend(ResetAllControllers(self, ou.Channel(channel))
                .getPlaylist(midi_track, position_beats, False))

            # Starts by turning off All keys for all pitches, from 0 to 127
            for pitch in range(128):
                self_playlist.extend(
                    Note(self, ou.Channel(channel), og.Pitch(float(pitch), ra.NoteValue(1/16)), ou.Velocity(0))
                        .getPlaylist(midi_track, position_beats, False)
                )


        return self_playlist





# Voice Message           Status Byte      Data Byte1          Data Byte2
# -------------           -----------   -----------------   -----------------
# Note off                      8x      Key number          Note Off velocity
# Note on                       9x      Key number          Note on velocity
# Polyphonic Key Pressure       Ax      Key number          Amount of pressure
# Control Change                Bx      Controller number   Controller value
# Program Change                Cx      Program number      None
# Channel Pressure              Dx      Pressure value      None            
# Pitch Bend                    Ex      MSB                 LSB
# Reset Position                F2      0                   0

# System Real-Time Message         Status Byte 
# ------------------------         -----------
# Timing Clock                         F8
# Start Sequence                       FA
# Continue Sequence                    FB
# Stop Sequence                        FC
# Active Sensing                       FE
# System Reset                         FF
