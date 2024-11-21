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
from fractions import Fraction
import time
import sys
# Json Midi Creator Libraries
import operand as o
import operand_unit as ou
import operand_rational as ra
import operand_time as ot
import operand_data as od
import operand_generic as og
import operand_frame as of
import operand_label as ol
import operand_chaos as ch


class Staff(o.Operand):
    def __init__(self, *parameters):
        super().__init__()
        # Set Global Staff Defaults at the end of this file bottom bellow
        self._measure: ra.Measure                   = ra.Measure(8)
        self._tempo: ra.Tempo                       = ra.Tempo(120.0)
        self._time_signature: og.TimeSignature      = og.TimeSignature(4, 4)
        # Key Signature is an alias of Sharps and Flats of a Scale
        self._key_signature: ou.KeySignature        = ou.KeySignature(0)
        self._key: ou.Key                           = ou.Key("C")
        self._tonic_key: ou.Key                     = ou.Key("C")
        self._scale: og.Scale                       = og.Scale([])  # By default, it has no scale besides the one given by the Key Signature
        self._quantization: ra.Quantization         = ra.Quantization(1/16)
        self._duration: ot.Duration                 = ot.Duration() << ra.NoteValue(1/4)
        self._octave: ou.Octave                     = ou.Octave(4)
        self._velocity: ou.Velocity                 = ou.Velocity(100)
        self._controller: og.Controller             = og.Controller("Pan") \
                                                        << ou.Value( ou.Number.getDefault("Pan") )
        self._channel: ou.Channel                   = ou.Channel(1)
        self._device: od.Device                     = od.Device(["Microsoft", "FLUID", "Apple"])
        self._chaos: ch.Chaos                       = ch.SinX() * (int(time.time() * 10000) % 100)
        self._chaos << ra.Lambda( self._chaos % ra.Lambda() + int(time.time() * 10000) % 100 )   # Lambda is the SinX chaotic blueprint !!
        self._tracks: dict[str, og.TrackData]       = {}    # where the multiple tracks will be saved
        if len(parameters) > 0:
            self << parameters

    def set_tonic_key(self):
        self._tonic_key._unit = self._key._unit
        if self._scale % od.DataSource( list() ) == []:
            major_scale: tuple = (1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)   # Major scale
            num_accidentals: int = self._key_signature._unit
            while num_accidentals > 0:
                white_keys: int = 4 # Jumps the tonic, so, 5 - 1
                while white_keys > 0:
                    self._tonic_key._unit += 1
                    self._tonic_key._unit %= 12
                    if major_scale[self._tonic_key._unit]:
                        white_keys -= 1
                num_accidentals -= 1
            while num_accidentals < 0:
                white_keys: int = -4 # Jumps the tonic, so, -5 + 1
                while white_keys < 0:
                    self._tonic_key._unit -= 1
                    self._tonic_key._unit %= 12
                    if major_scale[self._tonic_key._unit]:
                        white_keys += 1
                num_accidentals += 1

    def clean_tracks(self) -> dict[str, og.TrackData]:
        tracks_to_remove: set[str] = set()
        for key, value in self._tracks.items():
            track_data_ref_count: int = sys.getrefcount(value)                
            # print(f"{key}: {track_data_ref_count}")
            if track_data_ref_count < 4:    # sys + for + _tracks = 3
                tracks_to_remove.add(key)
        for track in tracks_to_remove:
            self._tracks.pop(track)
            if o.logging.getLogger().getEffectiveLevel() <= o.logging.DEBUG:
                o.logging.info(f"Track named '{track}' was removed for no long being used!")
        return self._tracks

    def __mod__(self, operand: o.Operand) -> o.Operand:
        """
        The % symbol is used to extract a Parameter, in the case of a Staff,
        those Parameters are the ones that define a Staff as global defaults,
        they include the ones relative to the time signature like Beats per Measure
        and Neat Note Value, the Tempo, the Quantization among others.

        Examples
        --------
        >>> staff % Tempo() % float()
        120.0
        >>> staff << BeatsPerMeasure(3)
        >>> staff % BeatsPerMeasure() % float()
        3.0
        """
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case of.Frame():            return self % od.DataSource( operand % o.Operand() )
                    case ra.Measure():          return self._measure
                    case ra.Tempo():            return self._tempo
                    case og.TimeSignature():    return self._time_signature
                    case ou.KeySignature():     return self._key_signature
                    case ou.Key():              return self._key
                    case ra.BeatsPerMeasure():  return self._time_signature % od.DataSource( ra.BeatsPerMeasure() )
                    case ra.BeatNoteValue():    return self._time_signature % od.DataSource( ra.BeatNoteValue() )
                    case og.Scale():            return self._scale
                    case ra.Quantization():     return self._quantization
                    case ot.Duration():         return self._duration
                    case ou.Octave():           return self._octave
                    case ou.Velocity():         return self._velocity
                    case og.Controller():       return self._controller
                    case ou.Channel():          return self._channel
                    case od.Device():           return self._device
                    case ch.Chaos():            return self._chaos
                    case dict():                return self.clean_tracks()
                    # Calculated Values
                    case ra.NotesPerMeasure():
                        return self._time_signature % od.DataSource( ra.NotesPerMeasure() )
                    case ra.StepsPerNote():
                        return ra.StepsPerNote() << od.DataSource( 1 / (self._quantization % od.DataSource( Fraction() )) )
                    case ra.StepsPerMeasure():
                        return ra.StepsPerMeasure() \
                            << od.DataSource( self % od.DataSource( ra.StepsPerNote() ) % od.DataSource( Fraction() ) \
                                * (self % od.DataSource( ra.NotesPerMeasure() ) % od.DataSource( Fraction() )))
                    case Staff():               return self
                    case _:                     return ol.Null()
            case of.Frame():            return self % (operand % o.Operand())
            # Direct Values
            case ra.Measure():          return self._measure.copy()
            case ra.Tempo():            return self._tempo.copy()
            case og.TimeSignature():    return self._time_signature.copy()
            case ou.KeySignature():     return self._key_signature.copy()
            case ou.Key():              return self._key.copy()
            case ra.BeatsPerMeasure():  return self._time_signature % ra.BeatsPerMeasure()
            case ra.BeatNoteValue():    return self._time_signature % ra.BeatNoteValue()
            case og.Scale():
                                    if self._scale.hasScale():
                                        return self._scale.copy()
                                    else:
                                        return self._key_signature % og.Scale()
            case ra.Quantization():     return self._quantization.copy()
            case ot.Duration():         return self._duration.copy()
            case ou.Octave():           return self._octave.copy()
            case ou.Velocity():         return self._velocity.copy()
            case og.Controller():       return self._controller.copy()
            case ou.Number():           return self._controller % ou.Number()
            case ou.Value():            return self._controller % ou.Value()
            case ou.Channel():          return self._channel.copy()
            case od.Device():           return self._device.copy()
            case ch.Chaos():            return self._chaos.copy()
            case str():
                if operand in self._tracks:
                    return self._tracks[operand]    # Tracks are identified by name (str)
                return None
            # Calculated Values
            case ra.NotesPerMeasure():
                return self._time_signature % ra.NotesPerMeasure()
            case ra.StepsPerNote():
                return ra.StepsPerNote() << 1 / (self._quantization % Fraction())
            case ra.StepsPerMeasure():
                return ra.StepsPerMeasure() \
                    << (self % ra.StepsPerNote() % Fraction()) * (self % ra.NotesPerMeasure() % Fraction())
            case Staff():               return self.copy()
            case _:                     return super().__mod__(operand)

    def __eq__(self, other: 'Staff') -> bool:
        other = self & other    # Processes the tailed self operands or the Frame operand if any exists
        if other.__class__ == o.Operand:
            return True
        if type(self) != type(other):
            return False
        return  self._measure           == other % od.DataSource( ra.Measure() ) \
            and self._tempo             == other % od.DataSource( ra.Tempo() ) \
            and self._time_signature    == other % od.DataSource( og.TimeSignature() ) \
            and self._key_signature     == other % od.DataSource( ou.KeySignature() ) \
            and self._key               == other % od.DataSource( ou.Key() ) \
            and self._scale             == other % od.DataSource( og.Scale() ) \
            and self._quantization      == other % od.DataSource( ra.Quantization() ) \
            and self._duration          == other % od.DataSource( ot.Duration() ) \
            and self._octave            == other % od.DataSource( ou.Octave() ) \
            and self._velocity          == other % od.DataSource( ou.Velocity() ) \
            and self._controller        == other % od.DataSource( og.Controller() ) \
            and self._channel           == other % od.DataSource( ou.Channel() ) \
            and self._device            == other % od.DataSource( od.Device() ) \
            and self._chaos             == other % od.DataSource( ch.Chaos() ) \
            and self._tracks            == other % od.DataSource( dict() )
    
    def getSerialization(self) -> dict:
        serialization = super().getSerialization()
        serialization["parameters"]["measures"]         = self._measure % od.DataSource( str() )
        serialization["parameters"]["tempo"]            = self._tempo % od.DataSource( str() )
        serialization["parameters"]["time_signature"]   = self._time_signature.getSerialization()
        serialization["parameters"]["key_signature"]    = self._key_signature.getSerialization()
        serialization["parameters"]["key"]              = self._key % od.DataSource( int() )
        serialization["parameters"]["scale"]            = self._scale % od.DataSource( list() )
        serialization["parameters"]["quantization"]     = self._quantization % od.DataSource( str() )
        serialization["parameters"]["duration"]         = self._duration.getSerialization()
        serialization["parameters"]["octave"]           = self._octave % od.DataSource( int() )
        serialization["parameters"]["velocity"]         = self._velocity % od.DataSource( int() )
        serialization["parameters"]["controller"]       = self._controller.getSerialization()
        serialization["parameters"]["channel"]          = self._channel % od.DataSource( int() )
        serialization["parameters"]["device"]           = self._device % od.DataSource( list() )
        serialization["parameters"]["chaos"]            = self.serialize(self._chaos)
        serialization["parameters"]["tracks"]           = self.serialize(self._tracks)
        return serialization

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Staff':
        if isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "measures" in serialization["parameters"] and "tempo" in serialization["parameters"] and "time_signature" in serialization["parameters"] and
            "key_signature" in serialization["parameters"] and "quantization" in serialization["parameters"] and
            "scale" in serialization["parameters"] and "duration" in serialization["parameters"] and "key" in serialization["parameters"] and
            "octave" in serialization["parameters"] and "velocity" in serialization["parameters"] and "controller" in serialization["parameters"] and
            "channel" in serialization["parameters"] and "device" in serialization["parameters"] and
            "chaos" in serialization["parameters"] and "tracks" in serialization["parameters"]):

            super().loadSerialization(serialization)
            self._measures          = ra.Measure()          << od.DataSource( serialization["parameters"]["measures"] )
            self._tempo             = ra.Tempo()            << od.DataSource( serialization["parameters"]["tempo"] )
            self._time_signature    = og.TimeSignature().loadSerialization(serialization["parameters"]["time_signature"])
            self._key_signature     = ou.KeySignature().loadSerialization(serialization["parameters"]["key_signature"])
            self._key               = ou.Key()              << od.DataSource( serialization["parameters"]["key"] )
            self._scale             = og.Scale()            << od.DataSource( serialization["parameters"]["scale"] )
            self._quantization      = ra.Quantization()     << od.DataSource( serialization["parameters"]["quantization"] )
            self._duration          = ot.Duration()         << od.DataSource( serialization["parameters"]["duration"] )
            self._octave            = ou.Octave()           << od.DataSource( serialization["parameters"]["octave"] )
            self._velocity          = ou.Velocity()         << od.DataSource( serialization["parameters"]["velocity"] )
            self._controller        = og.Controller().loadSerialization(serialization["parameters"]["controller"])
            self._channel           = ou.Channel()          << od.DataSource( serialization["parameters"]["channel"] )
            self._device            = od.Device()           << od.DataSource( serialization["parameters"]["device"] )
            self._chaos             = self.deserialize( serialization["parameters"]["chaos"] )
            self._tracks            = self.deserialize( serialization["parameters"]["tracks"] )
            self.set_tonic_key()
        return self
    
    def __lshift__(self, operand: o.Operand) -> 'Staff':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        match operand:
            case od.DataSource():
                match operand % o.Operand():
                    case ra.Measure():          self._measure = operand % o.Operand()
                    case ra.Tempo():            self._tempo = operand % o.Operand()
                    case og.TimeSignature():    self._time_signature = operand % o.Operand()
                    case ou.KeySignature():
                        self._key_signature = operand % o.Operand()
                        self.set_tonic_key()
                    case ou.Key():
                        self._key._unit = operand % o.Operand() % int() % 12
                        self.set_tonic_key()
                    case ra.BeatsPerMeasure() | ra.BeatNoteValue():
                                                self._time_signature << od.DataSource( operand % o.Operand() )
                    case og.Scale():
                        self._scale = operand % o.Operand()
                        self.set_tonic_key()
                    case ra.Quantization():     self._quantization = operand % o.Operand()    # Note Value
                    case ot.Duration():         self._duration = operand % o.Operand()
                    case ou.Octave():           self._octave = operand % o.Operand()
                    case ou.Velocity():         self._velocity = operand % o.Operand()
                    case og.Controller():       self._controller = operand % o.Operand()
                    case ou.Channel():          self._channel = operand % o.Operand()
                    case od.Device():           self._device = operand % o.Operand()
                    case ch.Chaos():            self._chaos = operand % o.Operand()
                    case dict():                self._tracks = operand % o.Operand()
            case Staff():
                super().__lshift__(operand)
                self._measure           << operand._measure
                self._tempo             << operand._tempo
                self._time_signature    << operand._time_signature
                self._key_signature     << operand._key_signature
                self._key               << operand._key
                self._scale             << operand._scale
                self._quantization      << operand._quantization
                self._duration          << operand._duration
                self._octave            << operand._octave
                self._velocity          << operand._velocity
                self._controller        << operand._controller
                self._channel           << operand._channel
                self._device            << operand._device
                self._chaos             << operand._chaos
                self._tracks            = operand._tracks
                self.set_tonic_key()
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ra.Measure():          self._measure << operand
            case ra.Tempo():            self._tempo << operand
            case og.TimeSignature() | ra.BeatsPerMeasure() | ra.BeatNoteValue():
                                        self._time_signature << operand
            case ou.KeySignature():
                                        self._key_signature << operand
                                        self.set_tonic_key()
            case ou.Key():
                                        self._key._unit = operand % int() % 12
                                        self.set_tonic_key()
            case og.Scale():
                                        self._scale << operand
                                        self.set_tonic_key()
            case ra.Quantization():     self._quantization << operand # Note Value
            case ot.Duration():         self._duration << operand
            case ou.Octave():           self._octave << operand
            case ou.Velocity():         self._velocity << operand
            case og.Controller() | ou.Number() | ou.Value():
                                        self._controller << operand
            case ou.Channel():          self._channel << operand
            case od.Device():           self._device << operand
            case ch.Chaos():            self._chaos << operand
            case og.Track():            self._tracks[operand % str()] = operand
            # Calculated Values
            case ra.StepsPerMeasure():
                self._quantization = ra.Quantization( (self % ra.NotesPerMeasure()) / (operand % Fraction()) )
            case ra.StepsPerNote():
                self._quantization = ra.Quantization( 1 / (operand % Fraction()) )
            case int():
                self._tempo << operand
            case float():
                self._tempo << operand
            case Fraction():
                ...
            case str():
                self._tempo << operand
                self._key_signature << operand
                self.set_tonic_key()
            case tuple():
                for single_operand in operand:
                    self << single_operand
        return self

# Instantiate the Global Staff here.
staff: Staff = Staff()
# DON'T DO THIS !!
# og.Track()   # No need, this "Staff" Track is created on demand!
