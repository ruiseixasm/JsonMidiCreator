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
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        import operand_container as oc
        super().__init__()
        self._position_beats: Fraction      = Fraction(0)   # in Beats
        self._duration_notevalue: Fraction  = og.defaults._duration
        self._channel: int                  = og.defaults._channel
        self._enabled: bool                 = True

        # Clip sets the Staff, this is just a reference
        self._staff_reference: og.Staff     = og.defaults._staff
        self._clip_reference: oc.Clip       = None

        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter


    def _set_staff_reference(self, staff_reference: 'og.Staff' = None) -> Self:
        if isinstance(staff_reference, og.Staff):
            self._staff_reference = staff_reference
        return self

    def _get_staff_reference(self) -> 'og.Staff':
        return self._staff_reference

    def _reset_staff_reference(self) -> Self:
        self._staff_reference = og.defaults._staff
        return self

    def set_clip_reference(self, clip_reference: 'Clip' = None) -> Self:
        import operand_container as oc
        if isinstance(clip_reference, oc.Clip):
            self._clip_reference = clip_reference
        return self

    def get_clip_reference(self) -> 'Clip':
        return self._clip_reference

    def reset_clip_reference(self) -> Self:
        self._clip_reference = None
        return self


    def position(self, position_measures: float = None) -> Self:
        self._position_beats = self._staff_reference.convertToPosition(ra.Measures(position_measures))._rational
        return self

    def duration(self, duration: float = None) -> Self:
        self._duration_notevalue = ra.Duration(duration)._rational
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
            case od.DataSource():
                match operand._data:
                    case ra.Duration():
                        return operand._data._set_staff_reference(self._staff_reference) << od.DataSource( self._duration_notevalue )
                    case ra.Position():
                        return operand._data._set_staff_reference(self._staff_reference) << od.DataSource( self._position_beats )
                    case ra.Length():
                        return operand._data._set_staff_reference(self._staff_reference) \
                            << self._staff_reference.convertToLength(ra.Duration(self._duration_notevalue))
                    case ou.Channel():      return ou.Channel() << od.DataSource( self._channel )
                    case Element():         return self
                    case ou.Enable():       return ou.Enable(self._enabled)
                    case ou.Disable():      return ou.Disable(not self._enabled)
                    case int():
                        return self._staff_reference.convertToMeasures(ra.Beats(self._position_beats)) % int()
                    case float():           return float( self._duration_notevalue )
                    case Fraction():        return self._duration_notevalue
                    case _:                 return super().__mod__(operand)
            case of.Frame():        return self % operand
            case ra.Duration():
                return operand.copy()._set_staff_reference(self._staff_reference) << od.DataSource( self._duration_notevalue )
            case ra.Position():
                return self._staff_reference.convertToPosition(ra.Beats(self._position_beats))
            case ra.Length():
                return self._staff_reference.convertToLength(ra.Duration(self._duration_notevalue))
            case ra.TimeValue() | ou.TimeUnit():
                return self._staff_reference.convertToPosition(ra.Beats(self._position_beats)) % operand
            case ou.Channel():      return ou.Channel() << od.DataSource( self._channel )
            case Element():         return self.copy()
            case int():
                return self._staff_reference.convertToMeasures(ra.Beats(self._position_beats)) % int()
            case float():           return float( self._duration_notevalue )
            case Fraction():
                self_duration: ra.Duration = self % ra.Duration()
                duration_steps: ra.Steps = self._staff_reference.convertToSteps(self_duration)
                return duration_steps._rational
            case ou.Enable():       return ou.Enable(self._enabled)
            case ou.Disable():      return ou.Disable(not self._enabled)
            case oc.Clip():
                notes: oc.Clip = oc.Clip(self._staff_reference)
                cluster_notes: list[Note] = self.get_component_elements()
                for single_note in cluster_notes:
                    notes += single_note
                return notes
            case _:                 return super().__mod__(operand)

    def get_component_elements(self) -> list['Element']:
        return [ self ]

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Element():
                return self % ra.Position() == other % ra.Position() \
                    and self % ra.Duration() == other % ra.Duration() \
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
                return self % ra.Position() < other % ra.Position()
            case _:
                return self % other < other
    
    def __gt__(self, other: 'o.Operand') -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case Element():
                return self % ra.Position() > other % ra.Position()
            case _:
                return self % other > other
    
    def start(self) -> ra.Position:
        return self._staff_reference.convertToPosition(ra.Beats(self._position_beats))

    def finish(self) -> ra.Position:
        return self._staff_reference.convertToPosition(ra.Beats(self._position_beats)) + self // ra.Length()


    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, channels: dict[str, set[int]] = None) -> list[dict]:
        return []

    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)
        return [
                {
                    "time_ms": o.minutes_to_time_ms(self_position_min)
                }
            ]

    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list:
        if not self._enabled:
            return []
        midi_track: ou.MidiTrack = ou.MidiTrack() if not isinstance(midi_track, ou.MidiTrack) else midi_track

        self_numerator: int = self._staff_reference._time_signature._top
        self_denominator: int = self._staff_reference._time_signature._bottom
        self_position: float = float(self._position_beats)
        self_duration: float = self._staff_reference.convertToBeats(ra.Duration(self._duration_notevalue)) % od.DataSource( float() )
        self_tempo: float = float(self._staff_reference._tempo)
        if isinstance(position_beats, Fraction):
            self_position = float(position_beats + self._position_beats)

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
        serialization["parameters"]["duration"]     = self.serialize(self._duration_notevalue)
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
            self._duration_notevalue    = self.deserialize(serialization["parameters"]["duration"])
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
                # Makes sure isn't a Clip owned Element first
                if self._clip_reference is None:
                    # Has to use the staff setting method in order to propagate setting
                    self._set_staff_reference(operand._staff_reference)
                if self._staff_reference is operand._staff_reference:
                    self._position_beats        = operand._position_beats
                    self._duration_notevalue    = operand._duration_notevalue
                else:
                    self << operand % ra.Position()
                    self << operand % ra.Duration()

            case od.DataSource():
                match operand._data:
                    case ra.Position():     self._position_beats  = operand._data._rational
                    case ra.Duration():     self._duration_notevalue  = operand._data._rational
                    case ou.Channel():      self._channel = operand._data._unit

            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Duration():
                self._duration_notevalue    = self._staff_reference.convertToDuration(operand)._rational
            case ra.Position() | ra.TimeValue():
                self._position_beats        = self._staff_reference.convertToBeats(operand)._rational
            case ou.TimeUnit():
                self_position: ra.Position  = ra.Position(od.DataSource( self._position_beats ))._set_staff_reference(self._staff_reference) << operand
                self._position_beats        = self_position._rational
            case Fraction():
                steps: ra.Steps = ra.Steps(operand)
                duration: ra.Duration = self._staff_reference.convertToDuration(steps)
                self._duration_notevalue    = duration._rational
            case float():
                self._duration_notevalue    = ra.Duration(operand)._rational
            case ra.Length():
                self._duration_notevalue    = self._staff_reference.convertToDuration(operand)._rational
            case int():
                self._position_beats        = self._staff_reference.convertToBeats(ra.Measures(operand))._rational
            case ou.Channel():
                self._channel               = operand._unit
            case ou.Enable():
                self._enabled               = operand._unit != 0
            case ou.Disable():
                self._enabled               = operand._unit == 0
            case oc.Composition():
                # Makes sure isn't a Clip owned Element first
                if self._clip_reference is None:
                    self._set_staff_reference(operand._get_staff_reference())
            case og.Staff():
                # Makes sure isn't a Clip owned Element first
                if self._clip_reference is None:
                    self._set_staff_reference(operand)

            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self


    def __rshift__(self, operand: o.T) -> Self:
        match operand:
            case od.Serialization():
                return self << operand % od.DataSource()
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
    

    def __radd__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.__add__(operand)

    def __rsub__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.__mul__(-1).__add__(operand)

    def __rmul__(self, operand: any) -> Union[TypeElement, 'Clip']:
        return self.__mul__(operand)


    def __iadd__(self, operand: any) -> Union[TypeElement, 'Clip']:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Element():
                return oc.Clip(od.DataSource( [self, operand.copy()] ))._set_staff_reference()._sort_position()
            case oc.Clip():
                self_clip: oc.Clip = operand.empty_copy()
                self_clip += self
                self_clip += operand
                return self_clip
            # For efficient reasons
            case ra.Position():
                self._position_beats += operand._rational
            case _:
                if isinstance(operand, ou.TimeUnit):    # avoids erroneous behavior
                    operand = self._staff_reference.convertToBeats(operand)
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
            case _:
                if isinstance(operand, ou.TimeUnit):    # avoid erroneous behavior
                    operand = self._staff_reference.convertToBeats(operand)
                self_operand: any = self % operand
                self_operand -= operand
                return self << self_operand
        return self

    def __imul__(self, operand: any) -> Union[TypeElement, 'Clip']:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:  # Allows Frame skipping to be applied to the elements' parameters!
            case Element():
                extended_clip: Clip = self + operand
                next_position: ra.Position = ra.Position( od.DataSource( extended_clip[0] % ra.Length() ) )
                extended_clip[1] << next_position   # Two elements Clip
                return extended_clip
            case oc.Clip():
                self_clip: oc.Clip = operand.copy()
                self._set_staff_reference(self_clip._staff).set_clip_reference(self_clip)
                if self_clip.len() > 0:
                    self_clip += ( self % ra.Length() ).convertToPosition()
                    self_clip._insert([ self ], self_clip[0])
                else:
                    self_clip._insert([ self ])
                return self_clip
            case int():
                new_clip: oc.Clip = oc.Clip(self._staff_reference)
                if operand > 0:
                    new_clip._items.append( self )
                    for _ in range(operand - 1):
                        new_clip._items.append( self.copy() )
                return new_clip.stack()._set_staff_reference()
            case ra.TimeValue() | ou.TimeUnit():
                self_repeating: int = 0
                if self._duration_notevalue > 0:
                    operand_duration: Fraction = self._staff_reference.convertToDuration(operand)._rational
                    self_repeating: int = operand_duration // self._duration_notevalue
                return self.__imul__(self_repeating)
        self_operand: any = self % operand
        self_operand *= operand
        return self << self_operand

    def __itruediv__(self, operand: any) -> Union[TypeElement, 'Clip']:
        import operand_container as oc
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:  # Allows Frame skipping to be applied to the elements' parameters!
            case Element():
                return self + operand
            case oc.Clip():
                self_clip: oc.Clip = operand.copy()
                self._set_staff_reference(self_clip._staff).set_clip_reference(self_clip)
                if self_clip.len() > 0:
                    self_clip._insert([ self ], self_clip[0])
                else:
                    self_clip._insert([ self ])
                return self_clip
            case int():
                new_clip: oc.Clip = oc.Clip(self._staff_reference)
                if operand > 0:
                    new_clip._items.append( self )
                    for _ in range(operand - 1):
                        new_clip._items.append( self.copy() )
                return new_clip._set_staff_reference()
            case _:
                if operand != 0:
                    self_operand: any = self % operand
                    self_operand /= operand
                    return self << self_operand
        return self

    def get_position_duration_minutes(self, position_beats: Fraction = None) -> tuple[Fraction]:

        if isinstance(position_beats, Fraction):
            self_position_min: Fraction = self._staff_reference.getMinutes(
                ra.Beats(position_beats + self._position_beats)
            )
        else:
            self_position_min: Fraction = self._staff_reference.getMinutes( ra.Beats(self._position_beats) )
        self_duration_min: Fraction = self._staff_reference.getMinutes( ra.Duration(self._duration_notevalue) )

        return self_position_min, self_duration_min

    def get_beats_minutes(self, beats: Fraction) -> Fraction:
        return self._staff_reference.getMinutes( ra.Beats(beats) )


class Group(Element):
    """`Element -> Group`

    A `Group` element aggregates any other type of `Element` of any amount.

    Parameters
    ----------
    list([ControlChange(ou.Number("Pan"), 0), Note()]) : A list with all the elements grouped by `Group`.
    Position(0), TimeValue, TimeUnit, int : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
            case od.DataSource():
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

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, channels: dict[str, set[int]] = None) -> list[dict]:
        self_playlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_playlist.extend(single_element.getPlotlist(midi_track, position_beats, channels))
        return self_playlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_playlist.extend(single_element.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list[dict]:
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
            case od.DataSource():
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
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
            case od.DataSource():
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
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)

        pulses_per_note: int = self._clock_ppqn * 4
        pulses_per_beat: Fraction = self._staff_reference // ra.BeatNoteValue() % Fraction() * pulses_per_note
        total_clock_pulses: int = self._staff_reference.convertToBeats( ra.Duration(self._duration_notevalue) ) * pulses_per_beat % int()

        self_playlist: list[dict] = []

        if not devices_header and midi_track is None:

            single_devices: set[str] = set()
            self_clock_devices: list[list[str]] = []

            for clocked_device in self._devices:
                if clocked_device not in single_devices:
                    self_clock_devices.append(clocked_device)
                    single_devices.add(clocked_device)

            self_playlist.append(
                {
                    "clock": {
                        # Has to add the extra Stop pulse message afterwards at (single_pulse_duration_min * total_clock_pulses)
                        "total_clock_pulses": total_clock_pulses,
                        "pulse_duration_min_numerator": 0,
                        "pulse_duration_min_denominator": 1,
                        "stop_mode": self._clock_stop_mode,
                        "devices": self_clock_devices
                    }
                }
            )

            if total_clock_pulses > 0:
                single_pulse_duration_min: Fraction = self_duration_min / total_clock_pulses
                self_playlist[0]["clock"]["pulse_duration_min_numerator"] = single_pulse_duration_min.numerator
                self_playlist[0]["clock"]["pulse_duration_min_denominator"] = single_pulse_duration_min.denominator

        else:

            if total_clock_pulses > 0:

                # Starts by setting the Devices
                if devices_header:
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
            case od.DataSource():
                match operand._data:
                    case oc.ClockedDevices():   self._devices = operand._data // list()
                    case oc.Devices():          self._devices = operand._data // list()
                    case ou.PPQN():             self._clock_ppqn = operand._data._unit
                    case ou.ClockStopModes():   self._clock_stop_mode = operand._data._unit
                    case _:                     super().__lshift__(operand)
            case oc.ClockedDevices():   self._devices = operand % list()
            case oc.Devices():          self._devices = operand % list()
            case od.Device():           self._devices = oc.Devices(self._devices, operand) // list()
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
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    pass

class Note(Element):
    """`Element -> Note`

    A `Note` element is the most important `Element` and basically represents a Midi note message including Note On and Note Off.

    Parameters
    ----------
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._velocity: int         = og.defaults._velocity
        self._gate: Fraction        = Fraction(1)
        self._tied: int             = 0
        self._pitch: og.Pitch       = og.Pitch()
        super().__init__(*parameters)


    def _set_staff_reference(self, staff_reference: 'og.Staff' = None) -> 'Note':
        super()._set_staff_reference(staff_reference)
        self._pitch._staff_reference = self._staff_reference
        return self

    def _reset_staff_reference(self) -> 'Note':
        super()._reset_staff_reference()
        self._pitch._reset_staff_reference()
        return self


    def velocity(self, velocity: int = 100) -> Self:
        self._velocity = velocity
        return self

    def gate(self, gate: float = None) -> Self:
        self._gate = ra.Gate(gate)._rational
        return self

    def tied(self, tied: int = 1) -> Self:
        self._tied = tied
        return self

    def pitch(self, key: Optional[int] = 0, octave: Optional[int] = 4) -> Self:
        self._pitch = og.Pitch(ou.Key(key), ou.Octave(octave))._set_staff_reference(self._staff_reference)
        return self

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
            case od.DataSource():
                match operand._data:
                    case ou.Velocity():     return ou.Velocity() << od.DataSource(self._velocity)
                    case ra.Gate():         return ra.Gate() << od.DataSource(self._gate)
                    case ou.Tied():         return ou.Tied() << od.DataSource( self._tied )
                    case og.Pitch():        return self._pitch
                    case int():             return self._velocity
                    case _:                 return super().__mod__(operand)
            case ou.Velocity():     return ou.Velocity() << od.DataSource(self._velocity)
            case ra.Gate():         return ra.Gate() << od.DataSource(self._gate)
            case ou.Tied():         return ou.Tied() << od.DataSource( self._tied )
            case og.Pitch():        return self._pitch.copy()
            case int():             return self._velocity
            case ou.PitchParameter() | str():
                                    return self._pitch % operand
            case ou.DrumKit():
                return ou.DrumKit(self._pitch % ( self // ra.Position() % Fraction() ), ou.Channel(self._channel))
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
                return self._pitch._degree == other
            case _:
                return super().__eq__(other)


    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, channels: dict[str, set[int]] = None) -> list[dict]:
        if not self._enabled:
            return []
        
        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)
        if self_duration_min == 0:
            return []

        if channels is not None:
            channels["note"].add(self._channel)

        pitch_int: int = int(self._pitch % ( self // ra.Position() % Fraction() ))

        self_plotlist: list[dict] = []
    
        # Midi validation is done in the JsonMidiPlayer program
        self_plotlist.append(
            {
                "note": {
                    "position_on": self._position_beats,
                    "position_off": self._position_beats + self % ra.Length() // Fraction(),
                    "pitch": int( self % og.Pitch() % float() ),
                    "velocity": self._velocity,
                    "channel": self._channel
                }
            }
        )

        # This only applies for Clip owned Notes!
        if self._clip_reference is not None:

            # Checks if it's a following tied note first
            if self._tied > 0:
                self_position: Fraction = self._position_beats
                self_length: Fraction = self // ra.Length() // Fraction()   # In Beats
                if self._tied > 1:
                    position_off: Fraction = self_position + self_length
                    last_tied_note = self._staff_reference._get_tied_note(pitch_int)
                    if last_tied_note and last_tied_note["position"] + last_tied_note["length"] == self_position:
                        # Extend last note
                        position_off = last_tied_note["position"] + last_tied_note["length"] + self_length * self._gate
                        last_tied_note["note_list"][0]['note']["position_off"] = position_off
                        self._staff_reference._set_tied_note_length(pitch_int, last_tied_note["position"] + last_tied_note["length"] + self_length)
                        return []   # Discard self_plotlist, adjusts just the duration of the previous note
                else:   # Must be the first tied note
                    # This note becomes the last tied note, position_off inplace of length has no problem
                    self._staff_reference._add_tied_note(pitch_int, 
                        self_position, self_length, self_plotlist
                    )

            # Record present Note on the Staff stacked notes
            if not self._staff_reference._stack_note(
                self_plotlist[0]['note']["position_on"],
                self._channel - 1,
                pitch_int
            ):
                print(f"Warning (PL): Removed redundant Note on Channel {self._channel} "
                    f"and Pitch {self_plotlist[0]['note']['pitch']} with same time start!")
                return []

        return self_plotlist

    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        
        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)
        if self_duration_min == 0:
            return []

        pitch_int: int = int(self._pitch % ( self // ra.Position() % Fraction() ))
        devices: list[str] = midi_track._devices if midi_track else og.defaults._devices

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

        # This only applies for Clip owned Notes!
        if self._clip_reference is not None:

            # Filers out any "devices" parameter, without "time_ms" one
            self_playlist_time_ms: list[dict] = self_playlist 
            if devices_header:
                self_playlist_time_ms = o.playlist_time_ms( self_playlist )

            # Checks if it's a tied note first
            if self._tied > 0:
                self_position: Fraction = self._position_beats
                self_length: Fraction = self // ra.Length() // Fraction()   # In Beats
                if self._tied > 1:
                    last_tied_note = self._staff_reference._get_tied_note(pitch_int)
                    if last_tied_note and last_tied_note["position"] + last_tied_note["length"] == self_position:
                        # Extend last note
                        position_off_ms: float = o.minutes_to_time_ms(
                            self.get_beats_minutes(last_tied_note["position"] + last_tied_note["length"] + self_length * self._gate)
                        )
                        last_tied_note["note_list"][1]["time_ms"] = position_off_ms
                        self._staff_reference._set_tied_note_length(pitch_int, last_tied_note["length"] + self_length)
                        return []   # Discard self_playlist, adjusts just the duration of the previous note
                else:
                    # This note becomes the last tied note
                    self._staff_reference._add_tied_note(pitch_int, 
                        self_position, self_length, self_playlist_time_ms
                    )

            # Record present Note on the Staff stacked notes
            if not self._staff_reference._stack_note(
                self_playlist_time_ms[0]["time_ms"],
                self_playlist_time_ms[0]["midi_message"]["status_byte"],
                self_playlist_time_ms[0]["midi_message"]["data_byte_1"]
            ):
                print(f"Warning (PL): Removed redundant Note on Channel {self._channel} "
                    f"and Pitch {self_playlist_time_ms[0]['midi_message']['data_byte_1']} with same time start!")
                return []

        return self_playlist

    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list:
        if not self._enabled:
            return []
        
        self_duration: float = float(self._staff_reference.convertToBeats( ra.Duration(self._duration_notevalue) )._rational * self._gate)
        if self_duration == 0:
            return []

        pitch_int: int = int(self._pitch % ( self // ra.Position() % Fraction() ))

        self_midilist: list = super().getMidilist(midi_track, position_beats)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "Note"
        self_midilist[0]["duration"]    = self_duration
        self_midilist[0]["velocity"]    = self._velocity
        self_midilist[0]["pitch"]       = pitch_int

        # This only applies for Clip owned Notes!
        if self._clip_reference is not None:

            # Checks if it's a tied note first
            if self._tied:
                self_position: Fraction = self._position_beats
                self_length: Fraction = self // ra.Length() // Fraction()   # In Beats
                self_pitch: int = pitch_int
                last_tied_note = self._staff_reference._get_tied_note(self_pitch)
                if last_tied_note and last_tied_note["position"] + last_tied_note["length"] == self_position:
                    # Extend last note
                    last_tied_note["note_list"][0]["duration"] = float(last_tied_note["length"] + self_length * self._gate)
                    self._staff_reference._set_tied_note_length(self_pitch, last_tied_note["length"] + self_length)
                    return []   # Discard self_midilist
                else:
                    # This note becomes the last tied note
                    self._staff_reference._add_tied_note(self_pitch, 
                        self_position, self_length, self_midilist
                    )

            # Record present Note on the Staff stacked notes
            if not self._staff_reference._stack_note(
                self_midilist[0]["time"],
                self_midilist[0]["channel"],
                self_midilist[0]["pitch"]
            ):
                print(f"Warning (ML): Removed redundant Note on Channel {self_midilist[0]['channel'] + 1} "
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
            case od.DataSource():
                match operand._data:
                    case ou.Velocity():     self._velocity  = operand._data._unit
                    case ra.Gate():         self._gate      = operand._data._rational
                    case ou.Tied():         self._tied      = operand._data._unit
                    case og.Pitch():        self._pitch     = operand._data
                    case int():             self._velocity  = operand._data
                    case _:                 super().__lshift__(operand)
            case ou.Velocity():     self._velocity = operand._unit
            case int():             self._velocity = operand
            case ra.Gate():         self._gate = operand._rational
            case ou.Tied():
                self._tied = operand._unit
                if operand._unit > 0:
                    operand._unit += 1
            case og.Pitch():
                self._pitch << operand
                self._pitch._set_staff_reference(self._staff_reference)
            case ou.PitchParameter() | str() | None:
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
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | Fraction():
                self._pitch += operand  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> 'Note':
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._velocity -= operand
            case og.Pitch() | ou.Key() | ou.Tone() | ou.Semitone() | ou.Degree() | Fraction():
                self._pitch -= operand  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)


class Cluster(Note):
    """`Element -> Note -> Cluster`

    A `Cluster` element aggregates multiple notes based on the list len and content. \
        That content is added to the present single `Note` configuration.

    Parameters
    ----------
    list([ou.Degree(0), ou.Degree(2), ou.Degree(4)]) : A list with parameters to be added with `+=` to the self reference `Note`.
    Arpeggio("None") : Sets the `Arpeggio` intended to do with the simultaneously pressed notes.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._sets: list = [
            ou.Degree(0), ou.Degree(2), ou.Degree(4)
        ]
        self._arpeggio: og.Arpeggio = og.Arpeggio("None")
        super().__init__()
        self << self._staff_reference.convertToDuration(ra.Measures(1))  # By default a Scale and a Chord has one Measure duration
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case list():            return self._sets
                    case og.Arpeggio():     return self._arpeggio
                    case _:                 return super().__mod__(operand)
            case list():            return self._sets.copy()
            case og.Arpeggio():     return self._arpeggio.copy()
            case ou.Order() | ra.Swing() | ch.Chaos():
                                    return self._arpeggio % operand
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._sets == other._sets \
                    and self._arpeggio == other._arpeggio
            case _:
                return super().__eq__(other)
    
    def get_component_elements(self) -> list[Element]:
        cluster_notes: list[Note] = []
        for single_set in self._sets:
            new_note: Note = Note(self).set_clip_reference(self._clip_reference)
            new_note += single_set
            cluster_notes.append( new_note )
        return self._arpeggio.arpeggiate(cluster_notes)

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, channels: dict[str, set[int]] = None) -> list[dict]:
        self_plotlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_plotlist.extend(single_element.getPlotlist(midi_track, position_beats, channels))
        return self_plotlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_playlist.extend(single_element.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list[dict]:
        self_midilist: list[dict] = []
        for single_element in self.get_component_elements():
            self_midilist.extend(single_element.getMidilist(midi_track, position_beats))    # extends the list with other list
        return self_midilist
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["sets"] = self.serialize( self._sets )
        serialization["parameters"]["arpeggio"] = self.serialize( self._arpeggio )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "sets" in serialization["parameters"] and "arpeggio" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._sets  = self.deserialize( serialization["parameters"]["sets"] )
            self._arpeggio = self.deserialize( serialization["parameters"]["arpeggio"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Cluster():
                super().__lshift__(operand)
                self._sets = self.deep_copy( operand._sets )
                self._arpeggio  << operand._arpeggio
            case od.DataSource():
                match operand._data:
                    case list():
                        self._sets = operand._data
                    case og.Arpeggio():
                        self._arpeggio = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                self._sets = self.deep_copy( operand )
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
    Scale([]), KeySignature, list, str, None : Sets the `Scale` to be used, `None` or `[]` uses the `defaults` scale.
    Arpeggio("None") : Sets the `Arpeggio` intended to do with the simultaneously pressed notes.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self << self._staff_reference.convertToDuration(ra.Measures(1))  # By default a Scale and a Chord has one Measure duration
        self._scale: og.Scale       = og.Scale( [] ) # Sets the default Scale based on the Staff Key Signature
        self._arpeggio: og.Arpeggio = og.Arpeggio("None")
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def scale(self, scale: list[int] | str = None) -> Self:
        self._scale = og.Scale(scale)
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
            case od.DataSource():
                match operand._data:
                    case og.Scale():        return self._scale
                    case og.Arpeggio():     return self._arpeggio
                    case list():            return self._scale % list()
                    case _:                 return super().__mod__(operand)
            case og.Scale():        return self._scale.copy()
            case ou.Mode():         return self._scale % operand
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
                    and self._scale == other._scale \
                    and self._arpeggio == other._arpeggio
            case _:
                return super().__eq__(other)
            
    def get_component_elements(self) -> list[Element]:
        scale_notes: list[Note] = []
        # Sets Scale to be used
        if self._scale.hasScale():
            for key_note_i in range(self._scale.keys()): # presses entire scale, 7 keys for diatonic scales
                transposition: int = self._scale.transposition(key_note_i)
                new_note: Note = Note(self).set_clip_reference(self._clip_reference)
                new_note._pitch += float(transposition) # Jumps by semitones (chromatic tones)
                scale_notes.append( new_note )
        else:   # Uses the staff keys straight away
            staff_scale: list = self._staff_reference % list()
            total_degrees: int = sum(1 for key in staff_scale if key != 0)
            for degree_i in range(total_degrees):
                new_note: Note = Note(self).set_clip_reference(self._clip_reference)
                new_note._pitch += degree_i # Jumps by degrees (scale tones)
                scale_notes.append( new_note )
        return self._arpeggio.arpeggiate(scale_notes)
    
    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, channels: dict[str, set[int]] = None) -> list[dict]:
        self_plotlist: list[dict] = []
        for single_note in self.get_component_elements():
            self_plotlist.extend(single_note.getPlotlist(midi_track, position_beats, channels))
        return self_plotlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_note in self.get_component_elements():
            self_playlist.extend(single_note.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list[dict]:
        self_midilist: list[dict] = []
        for single_note in self.get_component_elements():
            self_midilist.extend(single_note.getMidilist(midi_track, position_beats))
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["self_scale"] = self.serialize( self._scale )
        serialization["parameters"]["arpeggio"] = self.serialize( self._arpeggio )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'KeyScale':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "self_scale" in serialization["parameters"] and "arpeggio" in serialization["parameters"]):
            
            super().loadSerialization(serialization)
            self._scale = self.deserialize( serialization["parameters"]["self_scale"] )
            self._arpeggio = self.deserialize( serialization["parameters"]["arpeggio"] )
        return self
        
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case KeyScale():
                super().__lshift__(operand)
                self._scale     << operand._scale
                self._arpeggio  << operand._arpeggio
            case od.DataSource():
                match operand._data:
                    case og.Scale():        self._scale = operand._data
                    case og.Arpeggio():     self._arpeggio = operand._data
                    case _:                 super().__lshift__(operand)
            case og.Scale() | list() | ou.Mode() | None:    # It's the element scale that is set
                self._scale << operand
            case ou.KeySignature():
                super().__lshift__(operand)
                self._scale << operand % list()
            case str():
                operand = operand.strip()
                # Set root note and Scale
                self._pitch << operand
                self._scale << operand
            case og.Arpeggio() | ou.Order() | ra.Swing() | ch.Chaos():
                self._arpeggio << operand
            case _:
                super().__lshift__(operand)
        return self
    
class Polychord(KeyScale):
    """`Element -> Note -> KeyScale -> Polychord`

    A `Polychord` element allows the triggering of notes concerning specific degrees of a `Scale`.

    Parameters
    ----------
    list([1, 3, 5]) : Sets the specific key degrees to be pressed as `Note`.
    Scale([]), KeySignature, str, None : Sets the `Scale` to be used, `None` uses the `defaults` scale.
    Arpeggio("None") : Sets the `Arpeggio` intended to do with the simultaneously pressed notes.
    Velocity(100), int : Sets the velocity of the note being pressed.
    Gate(1.0) : Sets the `Gate` as a ratio of Duration as the respective midi message from Note On to Note Off lag.
    Tied(False) : Sets a `Note` as tied if set as `True`.
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._degrees: list[int | float] = [1, 3, 5]
        super().__init__( *parameters )

    def __mod__(self, operand: o.T) -> o.T:
        match operand:
            case od.DataSource():
                match operand._data:
                    case list():            return self._degrees
                    case _:                 return super().__mod__(operand)
            case list():            return self._degrees.copy()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._degrees == other._degrees
            case _:
                return super().__eq__(other)
    
    def get_component_elements(self) -> list[Element]:
        polychord_notes: list[Note] = []
        for single_degree in self._degrees:
            polychord_notes.append( Note(self).set_clip_reference(self._clip_reference) << ou.Degree(single_degree) )
        return self._arpeggio.arpeggiate(polychord_notes)

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["degrees"] = self.serialize( self._degrees )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "degrees" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._degrees  = self.deserialize( serialization["parameters"]["degrees"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Polychord():
                super().__lshift__(operand)
                self._degrees = self.deep_copy( operand._degrees )
            case od.DataSource():
                match operand._data:
                    case list():
                        if all(isinstance(single_degree, (int, float, Fraction)) for single_degree in operand._data):
                            self._degrees = operand._data
                    case _:
                        super().__lshift__(operand)
            case list():
                if all(isinstance(single_degree, (int, float, Fraction)) for single_degree in operand):
                    self._degrees = self.deep_copy( operand )
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
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._size: int             = 3
        self._inversion: int        = 0
        self._dominant: bool        = False
        self._diminished: bool      = False
        self._augmented: bool       = False
        self._sus2: bool            = False
        self._sus4: bool            = False
        super().__init__(*parameters)

    def size(self, size: int = 3) -> Self:
        self._size = size
        return self

    def inversion(self, inversion: int = 1) -> Self:
        self._inversion = inversion
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
            case od.DataSource():
                match operand._data:
                    case ou.Size():         return ou.Size() << od.DataSource(self._size)
                    case ou.Inversion():    return ou.Inversion() << od.DataSource(self._inversion)
                    case ou.Dominant():     return ou.Dominant() << od.DataSource(self._dominant)
                    case ou.Diminished():   return ou.Diminished() << od.DataSource(self._diminished)
                    case ou.Augmented():    return ou.Augmented() << od.DataSource(self._augmented)
                    case ou.Sus2():         return ou.Sus2() << od.DataSource(self._sus2)
                    case ou.Sus4():         return ou.Sus4() << od.DataSource(self._sus4)
                    case _:                 return super().__mod__(operand)
            case ou.Size():         return ou.Size() << od.DataSource(self._size)
            case ou.Inversion():    return ou.Inversion() << od.DataSource(self._inversion)
            case ou.Dominant():     return ou.Dominant() << od.DataSource(self._dominant)
            case ou.Diminished():   return ou.Diminished() << od.DataSource(self._diminished)
            case ou.Augmented():    return ou.Augmented() << od.DataSource(self._augmented)
            case ou.Sus2():         return ou.Sus2() << od.DataSource(self._sus2)
            case ou.Sus4():         return ou.Sus4() << od.DataSource(self._sus4)
            case list():            return self.get_component_elements()
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._size          == other._size \
                    and self._inversion     == other._inversion \
                    and self._dominant      == other._dominant \
                    and self._diminished    == other._diminished \
                    and self._augmented     == other._augmented \
                    and self._sus2          == other._sus2 \
                    and self._sus4          == other._sus4
            case _:
                return super().__eq__(other)
    
    def get_component_elements(self) -> list[Element]:
        chord_notes: list[Note] = []
        # Sets Scale to be used
        if self._scale.hasScale():
            # modulated_scale: og.Scale = self._scale.copy().modulate(self._mode)
            for note_i in range(self._size):          # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...
                key_degree: int = note_i * 2 + 1    # all odd numbers, 1, 3, 5, ...
                if key_degree == 3:   # Third
                    if self._sus2:
                        key_degree -= 1
                    if self._sus4:
                        key_degree += 1   # cancels out if both sus2 and sus4 are set to true
                transposition: int = self._scale.transposition(key_degree - 1)
                if key_degree == 7:   # Seventh
                    if self._dominant:
                        transposition -= 1
                if key_degree == 3 or key_degree == 5:   # flattens Third and Fifth
                    if self._diminished:
                        transposition -= 1   # cancels out if both dominant and diminished are set to true
                new_note: Note = Note(self).set_clip_reference(self._clip_reference)
                new_note._pitch += float(transposition) # Jumps by semitones (chromatic tones)
                chord_notes.append( new_note )
        else:   # Uses the staff keys straight away
            # modulated_scale: og.Scale = og.defaults % og.Scale(self._mode) # already modulated
            for note_i in range(self._size):          # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ...
                key_degree: int = note_i * 2
                if key_degree == 3:   # Third
                    if self._sus2:
                        key_degree -= 1
                    if self._sus4:
                        key_degree += 1   # cancels out if both sus2 and sus4 are set to true
                new_note: Note = Note(self).set_clip_reference(self._clip_reference)
                new_note._pitch += key_degree # Jumps by degrees (scale tones)
                chord_notes.append( new_note )

        # Where the inversions are done
        inversion = min(self._inversion, len(chord_notes) - 1)
        if inversion > 0:
            first_note = chord_notes[inversion]
            not_first_note = True
            while not_first_note:   # Try to implement while inversion > 0 here
                not_first_note = False
                for single_note in chord_notes:
                    if single_note._pitch < first_note._pitch:   # Critical operation
                        single_note << single_note % ou.Octave() + 1
                        if single_note % od.DataSource( int() ) < 128:
                            not_first_note = True # to result in another while loop
        return self._arpeggio.arpeggiate(chord_notes)
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["size"]         = self.serialize( self._size )
        serialization["parameters"]["inversion"]    = self.serialize( self._inversion )
        serialization["parameters"]["dominant"]     = self.serialize( self._dominant )
        serialization["parameters"]["diminished"]   = self.serialize( self._diminished )
        serialization["parameters"]["augmented"]    = self.serialize( self._augmented )
        serialization["parameters"]["sus2"]         = self.serialize( self._sus2 )
        serialization["parameters"]["sus4"]         = self.serialize( self._sus4 )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "inversion" in serialization["parameters"] and "size" in serialization["parameters"] and 
            "dominant" in serialization["parameters"] and "diminished" in serialization["parameters"] and 
            "augmented" in serialization["parameters"] and "sus2" in serialization["parameters"] and "sus4" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._size          = self.deserialize( serialization["parameters"]["size"] )
            self._inversion     = self.deserialize( serialization["parameters"]["inversion"] )
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
                self._inversion     = operand._inversion
                self._dominant      = operand._dominant
                self._diminished    = operand._diminished
                self._augmented     = operand._augmented
                self._sus2          = operand._sus2
                self._sus4          = operand._sus4
            case od.DataSource():
                match operand._data:
                    case ou.Size():                 self._size = operand._data._unit
                    case ou.Inversion():            self._inversion = operand._data._unit
                    case ou.Dominant():             self._dominant = operand._data // bool()
                    case ou.Diminished():           self._diminished = operand._data // bool()
                    case ou.Augmented():            self._augmented = operand._data // bool()
                    case ou.Sus2():                 self._sus2 = operand._data // bool()
                    case ou.Sus4():                 self._sus4 = operand._data // bool()
                    case _:                         super().__lshift__(operand)
            case ou.Size():                 self._size = operand._unit
            case ou.Inversion():            self._inversion = operand._unit
            case str():
                operand = operand.strip()
                # Set Chord root note
                self._pitch << operand
                # Set Chord size
                self._size = ou.Size(od.DataSource( self._size ), operand)._unit
                # Set Chord scale
                if (operand.find("m") != -1 or operand.find("min") != -1 or operand in {'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'}) \
                    and operand.find("dim") == -1:
                    self._scale << "minor"
                else:
                    self._scale << "Major"
                self.set_all(operand)
            case ou.Dominant():
                if operand:
                    self.set_all()
                self._dominant = operand // bool()
            case ou.Diminished():
                if operand:
                    self.set_all()
                self._diminished = operand // bool()
            case ou.Augmented():
                if operand:
                    self.set_all()
                self._augmented = operand // bool()
            case ou.Sus2():
                if operand:
                    self.set_all()
                self._sus2 = operand // bool()
            case ou.Sus4():
                if operand:
                    self.set_all()
                self._sus4 = operand // bool()
            case _: super().__lshift__(operand)
        return self
    
    def set_all(self, data: any = False):    # mutual exclusive
        self._dominant      = ou.Dominant(od.DataSource( self._dominant ), data) // bool()
        self._diminished    = ou.Diminished(od.DataSource( self._diminished ), data) // bool()
        self._augmented     = ou.Augmented(od.DataSource( self._augmented ), data) // bool()
        self._sus2          = ou.Sus2(od.DataSource( self._sus2 ), data) // bool()
        self._sus4          = ou.Sus4(od.DataSource( self._sus4 ), data) // bool()

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
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._number: int       = 16
        self._swing: Fraction   = ra.Swing(0.5)._rational
        super().__init__()
        self._duration_notevalue  *= 2 # Equivalent to twice single note duration
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
            case od.DataSource():
                match operand._data:
                    case ou.Number():       return operand._data << od.DataSource(self._number)
                    case ra.Swing():        return operand._data << od.DataSource(self._swing)
                    case _:                 return super().__mod__(operand)
            case ou.Number():       return ou.Number() << od.DataSource(self._number)
            case ra.Swing():        return ra.Swing() << od.DataSource(self._swing)
            # Returns the SYMBOLIC value of each note
            case ra.Duration():     return operand.copy() << od.DataSource( self._duration_notevalue / 2 )
            case float():           return float( self._duration_notevalue / 2 )
            case Fraction():        return self._duration_notevalue / 2
            case list():            return self.get_component_elements()
            case _:                 return super().__mod__(operand)

    def get_component_elements(self) -> list[Element]:
        retrigger_notes: list[Note] = []
        self_iteration: int = 0
        note_position: ra.Position = self._staff_reference.convertToPosition(ra.Beats(self._position_beats))
        single_note_duration: ra.Duration = ra.Duration( self._duration_notevalue/(self._number) ) # Already 2x single note duration
        for _ in range(self._number):
            swing_ratio = self._swing
            if self_iteration % 2:
                swing_ratio = 1 - swing_ratio
            note_duration: ra.Duration = single_note_duration * 2 * swing_ratio
            retrigger_notes.append( Note(self, note_duration, note_position).set_clip_reference(self._clip_reference) )
            note_position += note_duration
            self_iteration += 1
        return retrigger_notes

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, channels: dict[str, set[int]] = None) -> list[dict]:
        self_plotlist: list[dict] = []
        for single_note in self.get_component_elements():
            self_plotlist.extend(single_note.getPlotlist(midi_track, position_beats, channels))
        return self_plotlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_note in self.get_component_elements():
            self_playlist.extend(single_note.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list[dict]:
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
            case od.DataSource():
                match operand._data:
                    case ou.Number():               self._number = operand._data // int()
                    case ra.Swing():                self._swing = operand._data._rational
                    case _:                         super().__lshift__(operand)
            case ou.Number():
                if operand > 0:
                    self._number = operand // int()
            case ra.Swing():
                if operand < 0:
                    self._swing = Fraction(0)
                elif operand > 1:
                    self._swing = Fraction(1)
                else:
                    self._swing = operand._rational
            case ra.Duration():
                self._duration_notevalue    = operand._rational * 2  # Equivalent to two sized Notes
            case Fraction():
                self._duration_notevalue    = operand * 2
            case float():
                self._duration_notevalue    = ra.Duration(operand)._rational * 2
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
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(defaults), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._swing: Fraction           = Fraction(0.5)
        self._elements: list[Element]   = [Note(ra.Gate(0.5)), Note(ra.Gate(0.5)), Note(ra.Gate(0.5))]
        super().__init__()
        self._duration_notevalue  *= 2 # Equivalent to twice single note duration
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
            elements_duration = self._duration_notevalue / len(self._elements) # from 2 notes to division
            if len(self._elements) == 2:
                 # Already 2x single note duration
                elements_duration = self._duration_notevalue/2 * 3/2 # from 3 notes to 2
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
            case od.DataSource():
                match operand._data:
                    case ra.Swing():        return ra.Swing() << od.DataSource(self._swing)
                    case list():            return self._elements
                    case _:                 return super().__mod__(operand)
            case ra.Swing():        return ra.Swing() << od.DataSource(self._swing)
            case ou.Number():       return ou.Number() << len(self._elements)
            case ra.Duration():     return operand << od.DataSource( self._duration_notevalue / 2 )
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
            element_duration = single_element % od.DataSource( ra.Duration() )
            tuplet_elements.append(single_element.copy() << element_position)
            swing_ratio = self._swing
            if self_iteration % 2:
                swing_ratio = 1 - swing_ratio
            element_position += element_duration * 2 * swing_ratio
            self_iteration += 1
        return tuplet_elements

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, channels: dict[str, set[int]] = None) -> list[dict]:
        self_plotlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_plotlist.extend(single_element.getPlotlist(midi_track, position_beats, channels))
        return self_plotlist
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        self_playlist: list[dict] = []
        for single_element in self.get_component_elements():
            self_playlist.extend(single_element.getPlaylist(midi_track, position_beats, devices_header))
        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list[dict]:
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
                self._elements  = self.deep_copy(operand % od.DataSource( list() ))
            case od.DataSource():
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
            case ra.Duration():
                self._duration_notevalue = operand._rational * 2  # Equivalent to two sized Notes
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        super().__init__()
        self._duration_notevalue = self._staff_reference._quantization   # Equivalent to one Step
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    def _get_msb_value(self) -> int:
        return 0

    def getPlotlist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, channels: dict[str, set[int]] = None) -> list[dict]:
        if not self._enabled:
            return []
        
        if channels is not None:
            channels["automation"].add(self._channel)

        self_plotlist: list[dict] = []
        
        # Midi validation is done in the JsonMidiPlayer program
        self_plotlist.append(
            {
                "automation": {
                    "position": self._position_beats,
                    "value": self._get_msb_value(),
                    "channel": self._channel
                }
            }
        )

        return self_plotlist


class ControlChange(Automation):
    """`Element -> Automation -> ControlChange`

    A `ControlChange` is an element that represents the CC midi messages of a Device.

    Parameters
    ----------
    Controller(defaults) : An `Operand` that represents parameters like the `Number` of the controller being changed.
    Value(Controller(defaults)), int : The CC value to be set on the Device controller.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._controller: og.Controller = og.defaults % og.Controller()
        self._value: int                = ou.Number.getDefault(self._controller._number_msb)
        super().__init__(*parameters)

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
            case od.DataSource():
                match operand._data:
                    case og.Controller():       return self._controller
                    case ou.Value():            return operand._data << od.DataSource(self._value)
                    case _:                     return super().__mod__(operand)
            case og.Controller():       return self._controller.copy()
            case int():                 return self._value
            case ou.Value():            return operand.copy() << self._value
            case ou.Number() | ou.LSB() | ou.HighResolution() | dict():
                return self._controller % operand
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: Any) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._controller == other._controller and self._value == other._value
            case _:
                return super().__eq__(other)


    def _get_msb_value(self) -> int:
        
        if self._controller._nrpn:

            cc_99_msb, cc_98_lsb, cc_6_msb, cc_38_lsb = self._controller._midi_nrpn_values(self._value)
            return cc_6_msb
        else:

            msb_value, lsb_value = self._controller._midi_msb_lsb_values(self._value)
            return msb_value
            

    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        if not self._enabled:
            return []

        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)
        time_ms: float = o.minutes_to_time_ms(self_position_min)
        devices: list[str] = midi_track._devices if midi_track else og.defaults._devices

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
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list[dict]:
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
        serialization["parameters"]["value"]        = self.serialize( self._value )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "controller" in serialization["parameters"] and "value" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._controller    = self.deserialize( serialization["parameters"]["controller"] )
            self._value         = self.deserialize( serialization["parameters"]["value"] )
        return self

    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case ControlChange():
                super().__lshift__(operand)
                self._controller    << operand._controller
                self._value         = operand._value
            case od.DataSource():
                match operand._data:
                    case og.Controller():       self._controller = operand._data
                    case ou.Value():            self._value = operand._data._unit
                    case _:                     super().__lshift__(operand)
            case og.Controller() | ou.Number() | ou.LSB() | ou.HighResolution() | str() | dict():
                self._controller << operand
            case int():
                self._value = operand
            case ou.Value():
                self._value = operand._unit
            case _: super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._value += operand  # Specific and compounded parameter
                return self
            case ou.Value():
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
            case ou.Value():
                self._value -= operand._unit  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)

class BankSelect(ControlChange):
    """`Element -> Automation -> ControlChange -> BankSelect`

    A `BankSelect` is a specific CC message that is used to select a Bank of presents.

    Parameters
    ----------
    Controller(ou.MSB(0), ou.LSB(32), ou.NRPN(False)) : The default and immutable `Controller` parameters \
        associated to Bank Select, namely, 0 and 32 for MSB and LSB respectively.
    Value(0), int : Selects the presets Bank in the Device.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Controller(defaults) : An `Operand` that represents parameters like the `Number` of the controller being changed.
    Value(0) : The default `Value` of 0 is immutable.
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._bend: int = 0
        super().__init__(*parameters)

    def bend(self, bend: int = 0) -> Self:
        self._bend = bend
        return self

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
            case od.DataSource():
                match operand._data:
                    case ou.Bend():         return ou.Bend() << od.DataSource(self._bend)
                    case _:                 return super().__mod__(operand)
            case int():             return self._bend
            case ou.Bend():         return ou.Bend() << od.DataSource(self._bend)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._bend == other._bend
            case _:
                return super().__eq__(other)


    def _get_msb_value(self) -> int:
        
        # from -8192 to 8191
        amount = 8192 + self._bend          # 2^14 = 16384, 16384 / 2 = 8192
        amount = max(min(amount, 16383), 0) # midi safe

        msb_midi: int = amount >> 7         # MSB - total of 14 bits, 7 for each side, 2^7 = 128
        lsb_midi: int = amount & 0x7F       # LSB - 0x7F = 127, 7 bits with 1s, 2^7 - 1
    
        return msb_midi


    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)
        devices: list[str] = midi_track._devices if midi_track else og.defaults._devices

        # from -8192 to 8191
        amount = 8192 + self._bend          # 2^14 = 16384, 16384 / 2 = 8192
        amount = max(min(amount, 16383), 0) # midi safe

        msb_midi: int = amount >> 7         # MSB - total of 14 bits, 7 for each side, 2^7 = 128
        lsb_midi: int = amount & 0x7F       # LSB - 0x7F = 127, 7 bits with 1s, 2^7 - 1
    
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
                    "data_byte_1": lsb_midi,
                    "data_byte_2": msb_midi
                }
            }
        )

        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position_beats)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "PitchWheelEvent"
        self_midilist[0]["value"]       = self._bend
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["bend"] = self.serialize( self._bend )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "bend" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._bend = self.deserialize( serialization["parameters"]["bend"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case PitchBend():
                super().__lshift__(operand)
                self._bend = operand._bend
            case od.DataSource():
                match operand._data:
                    case ou.Bend():             self._bend = operand._data._unit
                    case _:                     super().__lshift__(operand)
            case int():
                self._bend = operand
            case ou.Bend():
                self._bend = operand._unit
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._bend += operand  # Specific and compounded parameter
                return self
            case ou.Bend():
                self._bend += operand._unit  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._bend -= operand  # Specific and compounded parameter
                return self
            case ou.Bend():
                self._bend -= operand._unit  # Specific and compounded parameter
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._pressure: int = 0
        super().__init__(*parameters)

    def pressure(self, pressure: int = 0) -> Self:
        self._pressure = pressure
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
            case od.DataSource():
                match operand._data:
                    case ou.Pressure():     return ou.Pressure() << od.DataSource(self._pressure)
                    case _:                 return super().__mod__(operand)
            case int():             return self._pressure
            case ou.Pressure():     return ou.Pressure() << od.DataSource(self._pressure)
            case _:                 return super().__mod__(operand)

    def __eq__(self, other: o.Operand) -> bool:
        other ^= self    # Processes the Frame operand if any exists
        match other:
            case self.__class__():
                return super().__eq__(other) \
                    and self._pressure == other._pressure
            case _:
                return super().__eq__(other)
    
    
    def _get_msb_value(self) -> int:
        return self._pressure


    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list:
        if not self._enabled:
            return []
        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)
        devices: list[str] = midi_track._devices if midi_track else og.defaults._devices

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
                    "data_byte": self._pressure
                }
            }
        )

        return self_playlist
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list:
        if not self._enabled:
            return []
        self_midilist: list = super().getMidilist(midi_track, position_beats)
        # Validation is done by midiutil Midi Range Validation
        self_midilist[0]["event"]       = "ChannelPressure"
        self_midilist[0]["pressure"]    = self._pressure
        return self_midilist

    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["pressure"] = self.serialize( self._pressure )
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "pressure" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._pressure = self.deserialize( serialization["parameters"]["pressure"] )
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case Aftertouch():
                super().__lshift__(operand)
                self._pressure = operand._pressure
            case od.DataSource():
                match operand._data:
                    case ou.Pressure():         self._pressure = operand._data // int()
                    case _:                     super().__lshift__(operand)
            case int():
                self._pressure = operand
            case ou.Pressure():
                self._pressure = operand // int()
            case _:
                super().__lshift__(operand)
        return self

    def __iadd__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._pressure += operand  # Specific and compounded parameter
                return self
            case ou.Pressure():
                self._pressure += operand._unit  # Specific and compounded parameter
                return self
            case _:
                return super().__iadd__(operand)

    def __isub__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case int():
                self._pressure -= operand  # Specific and compounded parameter
                return self
            case ou.Pressure():
                self._pressure -= operand._unit  # Specific and compounded parameter
                return self
            case _:
                return super().__isub__(operand)

class PolyAftertouch(Aftertouch):
    """`Element -> Automation -> PolyAftertouch`

    A `PolyAftertouch` is an element that controls the pressure on a particular key `Pitch` being played.

    Parameters
    ----------
    Pitch(defaults) : As the name implies, sets the absolute Pitch of the `Note`, the `Pitch` operand itself add many functionalities, like, \
        `Scale`, `Degree` and `KeySignature`.
    Pressure(0), int: Value that ranges from 0 to 127, or, from (0) to (128 - 1).
    Position(0), TimeValue, TimeUnit : The position on the staff in `Measures`.
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def __init__(self, *parameters):
        self._pitch: og.Pitch  = og.Pitch()
        super().__init__(*parameters)


    def _set_staff_reference(self, staff_reference: 'og.Staff' = None) -> 'PolyAftertouch':
        super()._set_staff_reference(staff_reference)
        self._pitch._staff_reference = self._staff_reference
        return self

    def _reset_staff_reference(self) -> 'PolyAftertouch':
        super()._reset_staff_reference()
        self._pitch._reset_staff_reference()
        return self


    def pitch(self, key: Optional[int] = 0, octave: Optional[int] = 4) -> Self:
        self._pitch = og.Pitch(ou.Key(key), ou.Octave(octave))._set_staff_reference(self._staff_reference)
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
            case od.DataSource():
                match operand._data:
                    case og.Pitch():    return self._pitch
                    case _:             return super().__mod__(operand)
            case og.Pitch():
                return self._pitch.copy()
            case ou.PitchParameter() | str():
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
                    and self._pitch == other % od.DataSource( og.Pitch() )
            case _:
                return super().__eq__(other)
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        if not self._enabled:
            return []

        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)
        devices: list[str] = midi_track._devices if midi_track else og.defaults._devices
        pitch_int: int = int(self._pitch % ( self // ra.Position() % Fraction() ))

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
                    "data_byte_2": self._pressure
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
        return self
      
    def __lshift__(self, operand: any) -> Self:
        operand = self._tail_lshift(operand)    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case PolyAftertouch():
                super().__lshift__(operand)
                self._pitch << operand._pitch
            case od.DataSource():
                match operand._data:
                    case og.Pitch():            self._pitch = operand._data
                    case _:                     super().__lshift__(operand)
            case og.Pitch() | ou.PitchParameter() | str() | None:
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
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
            case od.DataSource():
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
    
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        if not self._enabled:
            return []
        self_position_min, self_duration_min = self.get_position_duration_minutes(position_beats)
        devices: list[str] = midi_track._devices if midi_track else og.defaults._devices

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
                BankSelect(self, self // ou.Bank(), self // ou.HighResolution())
                    .set_clip_reference(self._clip_reference).getPlaylist(devices_header=False)
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
    
    def getMidilist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None) -> list:
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
            case od.DataSource():
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
    Duration(Quantization(defaults)), float, Fraction : The `Duration` is expressed as a Note Value, like, 1/4 or 1/16..
    Channel(defaults) : The Midi channel where the midi message will be sent to.
    Enable(True) : Sets if the Element is enabled or not, resulting in messages or not.
    """
    def getPlaylist(self, midi_track: ou.MidiTrack = None, position_beats: Fraction = None, devices_header = True) -> list[dict]:
        if not self._enabled:
            return []

        devices: list[str] = midi_track._devices if midi_track else og.defaults._devices

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
                .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False))
            self_playlist.extend(PitchBend(self, ou.Channel(channel), 0)
                .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False))

            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(10), ou.Value(64))
                .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False))   # 10 - Pan
            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(64), ou.Value(0))
                .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False))   # 64 - Pedal (sustain)
            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(1), ou.Value(0))
                .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False))   # 1 - Modulation
            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(7), ou.Value(100))
                .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False))   # 7 - Volume
            self_playlist.extend(ControlChange(self, ou.Channel(channel), ou.Number(11), ou.Value(127))
                .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False))   # 11 - Expression

            self_playlist.extend(ResetAllControllers(self, ou.Channel(channel))
                .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False))

            # Starts by turning off All keys for all pitches, from 0 to 127
            for pitch in range(128):
                self_playlist.extend(
                    Note(self, ou.Channel(channel), og.Pitch(float(pitch), ra.Duration(1/16)), ou.Velocity(0))
                        .set_clip_reference(self._clip_reference).getPlaylist(midi_track, position_beats, False)
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
