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

# Json Midi Creator Libraries
from . import creator as c
from . import operand as o

from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_data as od
from . import operand_label as ol
from . import operand_generic as og
from . import operand_element as oe
from . import operand_frame as of
from . import operand_container as oc
from . import operand_chaos as ch


class RD_Devices:

    @classmethod
    def Clip_instrument_change(cls, sound: int, bank: str | int = "A") -> 'oc.Clip':
        clip = oc.Clip()
        if isinstance(bank, str):
            clip += oe.BankSelectMSB(cls.banks[bank.strip().upper()])
        else:
            clip += oe.BankSelectMSB(bank)
        clip += oe.ProgramChange(sound)
        return clip
    
    @classmethod
    def Clip_control_change(cls, parameter: str = "Cutoff", group: str = "FILTER 1") -> 'oc.Clip':
        clip = oc.Clip()
        parameter = parameter.strip()
        group = group.strip().upper()
        clip += oe.ControlChange(cls.midi_cc[group][parameter])
        return clip
    


class RD_Blofeld(RD_Devices):

    device          = od.Device("Blofeld")

    # Activate "Ctrl Receive" in "Shift + Global" and turn the data knob to select it on Global MIDI


    # A total of 8 banks
    banks: dict[str, int] = {
        "A":    1,
        "B":    2,
        "C":    3,
        "D":    4,
        "E":    5,
        "F":    6,
        "G":    7,
        "H":    8
    }


    def control_change(parameter: str = "Cutoff", group: str = "FILTER 1") -> oe.ControlChange:
        parameter = parameter.strip()
        group = group.strip().upper()
        return oe.ControlChange(RD_Blofeld.midi_cc[group][parameter])

    midi_cc: dict[str,
                dict[ str, dict[str, int] ]
            ] = {

                # Controllers
                "CONTROLLERS": {
                    "Modulation":   {"NUMBER": 1},
                    "Breath":       {"NUMBER": 2},
                    "Foot":         {"NUMBER": 4},
                    "Sustain":      {"NUMBER": 64}
                },

                # Oscillators
                "OSC COMMON": {
                    "Sync":         {"NUMBER": 49},
                    "Pitchmod":     {"NUMBER": 50},
                    "Glide Active": {"NUMBER": 65},
                    "Glide Mode":   {"NUMBER": 51},
                    "Glide Rate":   {"NUMBER": 5}
                },
                "OSC 1": {
                    "Octave":       {"NUMBER": 63},
                    "Semitone":     {"NUMBER": 64},
                    "Detune":       {"NUMBER": 29},
                    "FM":           {"NUMBER": 30},
                    "Shape":        {"NUMBER": 31},
                    "PW":           {"NUMBER": 33},
                    "PWM":          {"NUMBER": 34}
                },
                "OSC 2": {
                    "Octave":       {"NUMBER": 35},
                    "Semitone":     {"NUMBER": 36},
                    "Detune":       {"NUMBER": 37},
                    "FM":           {"NUMBER": 38},
                    "Shape":        {"NUMBER": 39},
                    "PW":           {"NUMBER": 40},
                    "PWM":          {"NUMBER": 41}
                },
                "OSC 3": {
                    "Octave":       {"NUMBER": 42},
                    "Semitone":     {"NUMBER": 43},
                    "Detune":       {"NUMBER": 44},
                    "FM":           {"NUMBER": 45},
                    "Shape":        {"NUMBER": 46},
                    "PW":           {"NUMBER": 47},
                    "PWM":          {"NUMBER": 48}
                },

                # Noise
                "NOISE": {
                    "Colour":       {"NUMBER": 62}
                },

                # Filters
                "FILTER 1": {
                    "Type":         {"NUMBER": 68},
                    "Cutoff":       {"NUMBER": 69},
                    "Resonance":    {"NUMBER": 70},
                    "Drive":        {"NUMBER": 71},
                    "Keytrack":     {"NUMBER": 72},
                    "Env Amount":   {"NUMBER": 73},
                    "Env Velocity": {"NUMBER": 74},
                    "Mod":          {"NUMBER": 75},
                    "FM":           {"NUMBER": 76},
                    "Pan":          {"NUMBER": 77},
                    "Panmod":       {"NUMBER": 78}
                },
                "FILTER COMMON": {
                    "Routing":      {"NUMBER": 67}
                },
                "FILTER 2": {
                    "Type":         {"NUMBER": 79},
                    "Cutoff":       {"NUMBER": 80},
                    "Resonance":    {"NUMBER": 81},
                    "Drive":        {"NUMBER": 82},
                    "Keytrack":     {"NUMBER": 83},
                    "Env Amount":   {"NUMBER": 84},
                    "Env Velocity": {"NUMBER": 85},
                    "Mod":          {"NUMBER": 86},
                    "FM":           {"NUMBER": 87},
                    "Pan":          {"NUMBER": 88},
                    "Panmod":       {"NUMBER": 89}
                },

                # Envelopes
                "FILTER ENV": {
                    "Attack":       {"NUMBER": 95},
                    "Decay":        {"NUMBER": 96},
                    "Sustain":      {"NUMBER": 97},
                    "Decay 2":      {"NUMBER": 98},
                    "Sustain 2":    {"NUMBER": 99},
                    "Release":      {"NUMBER": 100}
                },
                "AMP ENV": {
                    "Attack":       {"NUMBER": 101},
                    "Decay":        {"NUMBER": 102},
                    "Sustain":      {"NUMBER": 103},
                    "Decay 2":      {"NUMBER": 104},
                    "Sustain 2":    {"NUMBER": 105},
                    "Release":      {"NUMBER": 106}
                },
                "ENV 3": {
                    "Attack":       {"NUMBER": 107},
                    "Decay":        {"NUMBER": 108},
                    "Sustain":      {"NUMBER": 109},
                    "Decay 2":      {"NUMBER": 110},
                    "Sustain 2":    {"NUMBER": 111},
                    "Release":      {"NUMBER": 112}
                },
                "ENV 4": {
                    "Attack":       {"NUMBER": 113},
                    "Decay":        {"NUMBER": 114},
                    "Sustain":      {"NUMBER": 115},
                    "Decay 2":      {"NUMBER": 116},
                    "Sustain 2":    {"NUMBER": 117},
                    "Release":      {"NUMBER": 118}
                },

                # LFOs
                "LFO 1": {
                    "Shape":        {"NUMBER": 15},
                    "Speed":        {"NUMBER": 16},
                    "Sync":         {"NUMBER": 17},
                    "Delay":        {"NUMBER": 18}
                },
                "LFO 2": {
                    "Shape":        {"NUMBER": 19},
                    "Speed":        {"NUMBER": 20},
                    "Sync":         {"NUMBER": 21},
                    "Delay":        {"NUMBER": 22}
                },
                "LFO 3": {
                    "Shape":        {"NUMBER": 23},
                    "Speed":        {"NUMBER": 24},
                    "Sync":         {"NUMBER": 25},
                    "Delay":        {"NUMBER": 26}
                },

                # Amplifier
                "AMP COMMON": {
                    "Volume":       {"NUMBER": 90},
                    "Velocity":     {"NUMBER": 91},
                    "Mod":          {"NUMBER": 92}
                },

                # Effects
                "EFFECTS": {
                    "Mix 1":        {"NUMBER": 93},
                    "Mix 2":        {"NUMBER": 94}
                },

                # Arpeggiator
                "ARPEGGIATOR": {
                    "Octave":       {"NUMBER": 12},
                    "Length":       {"NUMBER": 13},
                    "Mode":         {"NUMBER": 14}
                },

                # Mixers
                "MIXER COMMON": {
                    "Volume":       {"NUMBER": 7},
                    "Pan":          {"NUMBER": 10}
                },
                "MIXER OSC 1": {
                    "Level":        {"NUMBER": 52},
                    "Filter":       {"NUMBER": 53}
                },
                "MIXER OSC 2": {
                    "Level":        {"NUMBER": 56},
                    "Filter":       {"NUMBER": 57}
                },
                "MIXER OSC 3": {
                    "Level":        {"NUMBER": 58},
                    "Filter":       {"NUMBER": 59}
                },
                "MIXER RING": {
                    "Level":        {"NUMBER": 54},
                    "Filter":       {"NUMBER": 55}
                },
                "MIXER NOISE": {
                    "Level":        {"NUMBER": 60},
                    "Filter":       {"NUMBER": 61}
                }
            }


class RD_Digitakt(RD_Devices):

    device          = od.Device("Digitakt")

    kick            = ou.Channel(1)
    snare           = ou.Channel(2)
    tom             = ou.Channel(3)
    clap            = ou.Channel(4)
    cowbell         = ou.Channel(5)
    closed_hat      = ou.Channel(6)
    open_hat        = ou.Channel(7)
    cymbal          = ou.Channel(8)

    fx_control_ch   = ou.Channel(9)
    auto_channel    = ou.Channel(10)

    
    bank_pattern: dict[str, list[int]] = {
        # The first column is just for offset purposes
        "A": list(range(0 * 16, 1 * 16 + 1)),   # 1 to 16
        "B": list(range(1 * 16, 2 * 16 + 1)),   # 17 to 32
        "C": list(range(2 * 16, 3 * 16 + 1)),   # 33 to 48
        "D": list(range(3 * 16, 4 * 16 + 1)),   # 49 to 64
        "E": list(range(4 * 16, 5 * 16 + 1)),   # 65 to 80
        "F": list(range(5 * 16, 6 * 16 + 1)),   # 81 to 96
        "G": list(range(6 * 16, 7 * 16 + 1)),   # 97 to 112
        "H": list(range(7 * 16, 8 * 16 + 1))    # 113 to 128
    }

    def controller(parameter: str = "Frequency", group: str = "FILTER", nrpn: bool = False) -> og.Controller:
        parameter = parameter.strip()
        group = group.strip().upper()
        if nrpn:
            return og.Controller(RD_Digitakt.midi_nrpn[group][parameter])
        return og.Controller(RD_Digitakt.midi_cc[group][parameter])

    midi_cc: dict[str,
                dict[str,
                    dict[str, int]
                ]
            ] = {
                # PER TRACK PARAMETERS (CHANNEL 1 TO 8)
                "TRACK": {
                    "Mute":         {"NUMBER": 94},
                    "Level":        {"NUMBER": 95}
                },
                "TRIG": {
                    "Note":         {"NUMBER": 3},
                    "Velocity":     {"NUMBER": 4},
                    "Length":       {"NUMBER": 5},
                    "Filter":       {"NUMBER": 13},
                    "LFO":          {"NUMBER": 14}
                },
                "SOURCE": {
                    "Tune":         {"NUMBER": 16},
                    "Mode":         {"NUMBER": 17},
                    "Bit":          {"NUMBER": 18},
                    "Sample":       {"NUMBER": 19},
                    "Knob E":       {"NUMBER": 20},
                    "Knob F":       {"NUMBER": 21},
                    "Knob G":       {"NUMBER": 22},
                    "Level":        {"NUMBER": 23}
                },
                "FILTER": {
                    "Frequency":    {"NUMBER": 74},
                    "Resonance":    {"NUMBER": 75},
                    "Type":         {"NUMBER": 76},
                    "Attack":       {"NUMBER": 70},
                    "Decay":        {"NUMBER": 71},
                    "Sustain":      {"NUMBER": 72},
                    "Release":      {"NUMBER": 73},
                    "Depth":        {"NUMBER": 77},
                    "Delay":        {"NUMBER": 86},
                    "Rate":         {"NUMBER": 87},
                    "Base":         {"NUMBER": 84},
                    "Width":        {"NUMBER": 85},
                    "Routing":      {"NUMBER": 88}
                },
                "AMP": {
                    "Attack":       {"NUMBER": 78},
                    "Hold":         {"NUMBER": 79},
                    "Decay":        {"NUMBER": 80},
                    "Overdrive":    {"NUMBER": 81},
                    "Delay":        {"NUMBER": 82},
                    "Reverb":       {"NUMBER": 83},
                    "Pan":          {"NUMBER": 10},
                    "Volume":       {"NUMBER": 7}
                },
                "LFO 1": {
                    "Speed":        {"NUMBER": 102},
                    "Multiplier":   {"NUMBER": 103},
                    "Fade":         {"NUMBER": 104},
                    "Destination":  {"NUMBER": 105},
                    "Waveform":     {"NUMBER": 106},
                    "Phase":        {"NUMBER": 107},
                    "Mode":         {"NUMBER": 108},
                    "Depth":        {"MSB": 109, "LSB": 61}
                },
                "LFO 2": {
                    "Speed":        {"NUMBER": 112},
                    "Multiplier":   {"NUMBER": 113},
                    "Fade":         {"NUMBER": 114},
                    "Destination":  {"NUMBER": 115},
                    "Waveform":     {"NUMBER": 116},
                    "Phase":        {"NUMBER": 117},
                    "Mode":         {"NUMBER": 118},
                    "Depth":        {"MSB": 119, "LSB": 63}
                },
                "MIDI": {
                    "Val1":         {"NUMBER": 70},
                    "Val2":         {"NUMBER": 71},
                    "Val3":         {"NUMBER": 72},
                    "Val4":         {"NUMBER": 73},
                    "Val5":         {"NUMBER": 74},
                    "Val6":         {"NUMBER": 75},
                    "Val7":         {"NUMBER": 76},
                    "Val8":         {"NUMBER": 77}
                },

                # PER PATTERN PARAMETERS (CHANNEL 9)
                "DELAY": {
                    "Time":         {"NUMBER": 85},
                    "Pingpong":     {"NUMBER": 86},
                    "Width":        {"NUMBER": 87},
                    "Feedback":     {"NUMBER": 88},
                    "Highpass":     {"NUMBER": 89},
                    "Lowpass":      {"NUMBER": 90},
                    "Reverb":       {"NUMBER": 91},
                    "Mix":          {"NUMBER": 92}
                },
                "REVERB": {
                    "Predelay":     {"NUMBER": 24},
                    "Decay":        {"NUMBER": 25},
                    "Frequency":    {"NUMBER": 26},
                    "Gain":         {"NUMBER": 27},
                    "Highpass":     {"NUMBER": 28},
                    "Lowpass":      {"NUMBER": 29},
                    "Reverb":       {"NUMBER": 30},
                    "Mix":          {"NUMBER": 31}
                },
                "COMPRESSOR": {
                    "Threshold":    {"NUMBER": 111},
                    "Attack":       {"NUMBER": 112},
                    "Release":      {"NUMBER": 113},
                    "Gain":         {"NUMBER": 114},
                    "Volume":       {"NUMBER": 119},
                    "Ratio":        {"NUMBER": 115},
                    "Source":       {"NUMBER": 116},
                    "Filter":       {"NUMBER": 117},
                    "Mix":          {"NUMBER": 118}
                },
                "MIXER": {
                    "Level L":      {"NUMBER": 102},
                    "Pan L":        {"NUMBER": 103},
                    "Level R":      {"NUMBER": 104},
                    "Pan R":        {"NUMBER": 105},
                    "Delay L":      {"NUMBER": 106},
                    "Delay R":      {"NUMBER": 107},
                    "Reverb L":     {"NUMBER": 108},
                    "Reverb R":     {"NUMBER": 109},
                    "Stereo":       {"NUMBER": 84},
                    "LR Level":     {"NUMBER": 102},
                    "LR Balance":   {"NUMBER": 103},
                    "LR Delay":     {"NUMBER": 106},
                    "LR Reverb":    {"NUMBER": 108}
                },
                "PATTERN": {
                    "Mute":         {"NUMBER": 110}
                }
            }


    midi_nrpn: dict[str,
                dict[str,
                    dict[str, int]
                ]
            ] = {
                # PER TRACK PARAMETERS (CHANNEL 1 TO 8)
                "TRACK": {
                    "Mute":         {"MSB": 1, "LSB": 101},
                    "Level":        {"MSB": 1, "LSB": 100}
                },
                "TRIG": {
                    "Note":         {"MSB": 3, "LSB": 0},
                    "Velocity":     {"MSB": 3, "LSB": 1},
                    "Length":       {"MSB": 3, "LSB": 2},
                    "Filter":       {},
                    "LFO":          {}
                },
                "SOURCE": {
                    "Tune":         {"MSB": 1, "LSB": 0},
                    "Mode":         {"MSB": 1, "LSB": 1},
                    "Bit":          {"MSB": 1, "LSB": 2},
                    "Sample":       {"MSB": 1, "LSB": 3},
                    "Knob E":       {"MSB": 1, "LSB": 4},
                    "Knob F":       {"MSB": 1, "LSB": 5},
                    "Knob G":       {"MSB": 1, "LSB": 6},
                    "Level":        {"MSB": 1, "LSB": 7}
                },
                "FILTER": {
                    "Frequency":    {"MSB": 1, "LSB": 20},
                    "Resonance":    {"MSB": 1, "LSB": 21},
                    "Type":         {"MSB": 1, "LSB": 22},
                    "Attack":       {"MSB": 1, "LSB": 16},
                    "Decay":        {"MSB": 1, "LSB": 17},
                    "Sustain":      {"MSB": 1, "LSB": 18},
                    "Release":      {"MSB": 1, "LSB": 19},
                    "Depth":        {"MSB": 1, "LSB": 23},
                    "Delay":        {"MSB": 1, "LSB": 50},
                    "Rate":         {"MSB": 1, "LSB": 53},
                    "Base":         {"MSB": 1, "LSB": 51},
                    "Width":        {"MSB": 1, "LSB": 52},
                    "Routing":      {"MSB": 1, "LSB": 54}
                },
                "AMP": {
                    "Attack":       {"MSB": 1, "LSB": 24},
                    "Hold":         {"MSB": 1, "LSB": 25},
                    "Decay":        {"MSB": 1, "LSB": 26},
                    "Overdrive":    {"MSB": 1, "LSB": 27},
                    "Delay":        {"MSB": 1, "LSB": 28},
                    "Reverb":       {"MSB": 1, "LSB": 29},
                    "Pan":          {"MSB": 1, "LSB": 30},
                    "Volume":       {"MSB": 1, "LSB": 31}
                },
                "LFO 1": {
                    "Speed":        {"MSB": 1, "LSB": 32},
                    "Multiplier":   {"MSB": 1, "LSB": 33},
                    "Fade":         {"MSB": 1, "LSB": 34},
                    "Destination":  {"MSB": 1, "LSB": 35},
                    "Waveform":     {"MSB": 1, "LSB": 36},
                    "Phase":        {"MSB": 1, "LSB": 37},
                    "Mode":         {"MSB": 1, "LSB": 38},
                    "Depth":        {"MSB": 1, "LSB": 39}
                },
                "LFO 2": {
                    "Speed":        {"MSB": 1, "LSB": 40},
                    "Multiplier":   {"MSB": 1, "LSB": 41},
                    "Fade":         {"MSB": 1, "LSB": 42},
                    "Destination":  {"MSB": 1, "LSB": 43},
                    "Waveform":     {"MSB": 1, "LSB": 44},
                    "Phase":        {"MSB": 1, "LSB": 45},
                    "Mode":         {"MSB": 1, "LSB": 46},
                    "Depth":        {"MSB": 1, "LSB": 47}
                },
                "MIDI": {
                    "Val1":         {},
                    "Val2":         {},
                    "Val3":         {},
                    "Val4":         {},
                    "Val5":         {},
                    "Val6":         {},
                    "Val7":         {},
                    "Val8":         {}
                },

                # PER PATTERN PARAMETERS (CHANNEL 9)
                "DELAY": {
                    "Time":         {"MSB": 2, "LSB": 0},
                    "Pingpong":     {"MSB": 2, "LSB": 1},
                    "Width":        {"MSB": 2, "LSB": 2},
                    "Feedback":     {"MSB": 2, "LSB": 3},
                    "Highpass":     {"MSB": 2, "LSB": 4},
                    "Lowpass":      {"MSB": 2, "LSB": 5},
                    "Reverb":       {"MSB": 2, "LSB": 6},
                    "Mix":          {"MSB": 2, "LSB": 7}
                },
                "REVERB": {
                    "Predelay":     {"MSB": 2, "LSB": 8},
                    "Decay":        {"MSB": 2, "LSB": 9},
                    "Frequency":    {"MSB": 2, "LSB": 10},
                    "Gain":         {"MSB": 2, "LSB": 11},
                    "Highpass":     {"MSB": 2, "LSB": 12},
                    "Lowpass":      {"MSB": 2, "LSB": 13},
                    "Reverb":       {"MSB": 2, "LSB": 14},
                    "Mix":          {"MSB": 2, "LSB": 15}
                },
                "COMPRESSOR": {
                    "Threshold":    {"MSB": 2, "LSB": 16},
                    "Attack":       {"MSB": 2, "LSB": 17},
                    "Release":      {"MSB": 2, "LSB": 18},
                    "Gain":         {"MSB": 2, "LSB": 19},
                    "Volume":       {"MSB": 2, "LSB": 24},
                    "Ratio":        {"MSB": 2, "LSB": 20},
                    "Source":       {"MSB": 2, "LSB": 21},
                    "Filter":       {"MSB": 2, "LSB": 22},
                    "Mix":          {"MSB": 2, "LSB": 23}
                },
                "MIXER": {
                    "Level L":      {"MSB": 2, "LSB": 30},
                    "Pan L":        {"MSB": 2, "LSB": 31},
                    "Level R":      {"MSB": 2, "LSB": 32},
                    "Pan R":        {"MSB": 2, "LSB": 33},
                    "Delay L":      {"MSB": 2, "LSB": 34},
                    "Delay R":      {"MSB": 2, "LSB": 35},
                    "Reverb L":     {"MSB": 2, "LSB": 36},
                    "Reverb R":     {"MSB": 2, "LSB": 37},
                    "Stereo":       {"MSB": 2, "LSB": 38},
                    "LR Level":     {"MSB": 2, "LSB": 30},
                    "LR Balance":   {"MSB": 2, "LSB": 31},
                    "LR Delay":     {"MSB": 2, "LSB": 34},
                    "LR Reverb":    {"MSB": 2, "LSB": 36}
                },
                "PATTERN": {
                    "Mute":         {"MSB": 1, "LSB": 104}
                }
            }


class RD_UnoSynth(RD_Devices):

    device          = od.Device("UNO")

    def control_change(parameter: str = "Cutoff", group: str = "FILTER") -> oe.ControlChange:
        parameter = parameter.strip()
        group = group.strip().upper()
        return oe.ControlChange(RD_UnoSynth.midi_cc[group][parameter])

    midi_cc: dict[str,
                dict[ str, dict[str, int] ]
            ] = {

                # Controllers
                "CONTROLLERS": {
                    "Modulation":   {"NUMBER": 1},
                    "Glide":        {"NUMBER": 65},
                    "Sustain":      {"NUMBER": 64}
                },

                # Oscillators
                "OSC COMMON": {
                    "Glide Time":   {"NUMBER": 5}
                },
                "OSC 1": {
                    "Level":        {"NUMBER": 12},
                    "Wave":         {"NUMBER": 15},
                    "Tune":         {"NUMBER": 17},
                    "PWM":          {"NUMBER": 48},
                    "Wave":         {"NUMBER": 50}
                },
                "OSC 2": {
                    "Level":        {"NUMBER": 13},
                    "Wave":         {"NUMBER": 16},
                    "Tune":         {"NUMBER": 18},
                    "PWM":          {"NUMBER": 49},
                    "Wave":         {"NUMBER": 51}
                },

                # Noise
                "NOISE": {
                    "Level":        {"NUMBER": 14}
                },

                # On Off
                "ON OFF": {
                    "Vibrato":      {"NUMBER": 77},
                    "Wah":          {"NUMBER": 78},
                    "Tremolo":      {"NUMBER": 79},
                    "Arpeggiator":  {"NUMBER": 82},
                    "Dive":         {"NUMBER": 89},
                    "Scoop":        {"NUMBER": 91}
                },

                # Effects
                "EFFECTS": {
                    "Dive":         {"NUMBER": 90},
                    "Scoop":        {"NUMBER": 92},
                    "Pitch Bend Range":
                                    {"NUMBER": 101}
                },

                # Delay
                "DELAY": {
                    "Time":         {"NUMBER": 80},
                    "Mix":          {"NUMBER": 81}
                },

                # Modulation
                "MODULATION": {
                    "LFO":          {"NUMBER": 93},
                    "Vibrato":      {"NUMBER": 94},
                    "Wah":          {"NUMBER": 95},
                    "Tremolo":      {"NUMBER": 96},
                    "Cutoff":       {"NUMBER": 97}
                },

                # Velocity
                "VELOCITY": {
                    "VCA Amount":   {"NUMBER": 102},
                    "Cutoff":       {"NUMBER": 103},
                    "Envelop":      {"NUMBER": 104},
                    "LFO Rate":     {"NUMBER": 105},
                    "Notes Off":    {"NUMBER": 123}
                },

                # Filters
                "FILTER": {
                    "Mode":         {"NUMBER": 19},
                    "Cutoff":       {"NUMBER": 20},
                    "Resonance":    {"NUMBER": 21},
                    "Drive":        {"NUMBER": 22},
                    "Env Amount":   {"NUMBER": 23},
                    "Keytrack":     {"NUMBER": 106}
                },

                # Envelopes
                "FILTER ENV": {
                    "Attack":       {"NUMBER": 44},
                    "Decay":        {"NUMBER": 45},
                    "Sustain":      {"NUMBER": 46},
                    "Release":      {"NUMBER": 47}
                },
                "AMP ENV": {
                    "Attack":       {"NUMBER": 24},
                    "Decay":        {"NUMBER": 25},
                    "Sustain":      {"NUMBER": 26},
                    "Release":      {"NUMBER": 27}
                },

                # LFOs
                "LFO": {
                    "Wave":         {"NUMBER": 66},
                    "Rate":         {"NUMBER": 67},
                    "Pitch":        {"NUMBER": 68},
                    "Cutoff":       {"NUMBER": 69},
                    "Tremolo":      {"NUMBER": 70},
                    "Wah":          {"NUMBER": 71},
                    "Vibrato":      {"NUMBER": 72},
                    "PWM 1":        {"NUMBER": 73},
                    "PWM 2":        {"NUMBER": 74},
                    "Waveform 1":   {"NUMBER": 75},
                    "Waveform 2":   {"NUMBER": 76}
                },

                # Arpeggiator
                "ARPEGGIATOR": {
                    "Direction":    {"NUMBER": 83},
                    "Range":        {"NUMBER": 84},
                    "Gate":         {"NUMBER": 85},
                    "Swing":        {"NUMBER": 9}
                },

                # Sequencer
                "SEQUENCER": {
                    "Direction":    {"NUMBER": 86},
                    "Range":        {"NUMBER": 87},
                    "Gate":         {"NUMBER": 85},
                    "Swing":        {"NUMBER": 9}
                },

                # Mixers
                "MIXER COMMON": {
                    "Volume":       {"NUMBER": 7},
                    "Balance":      {"NUMBER": 8}
                },

                # Scale
                "SCALE": {
                    "Type":         {"NUMBER": 120}
                }
            }



class RD_Hybrid(RD_Devices):

    device          = od.Device("loop")

    # Activate "Ctrl Receive" in "Shift + Global" and turn the data knob to select it on Global MIDI


    # A total of 8 banks
    banks: dict[str, int] = {
        "A":    1,
        "B":    2,
        "C":    3,
        "D":    4,
        "E":    5,
        "F":    6,
        "G":    7,
        "H":    8
    }


    def control_change(parameter: str = "Cutoff", group: str = "FILTER 1") -> oe.ControlChange:
        parameter = parameter.strip()
        group = group.strip().upper()
        return oe.ControlChange(RD_Hybrid.midi_cc[group][parameter])

    midi_cc: dict[str,
                dict[ str, dict[str, int] ]
            ] = {

                # Controllers
                "CONTROLLERS": {
                    "Modulation":   {"NUMBER": 1},
                    "Breath":       {"NUMBER": 2},
                    "Foot":         {"NUMBER": 4},
                    "Sustain":      {"NUMBER": 64}
                },

                # Oscillators
                "OSC COMMON": {
                    "Sync":         {"NUMBER": 49},
                    "Pitchmod":     {"NUMBER": 50},
                    "Glide Active": {"NUMBER": 65},
                    "Glide Mode":   {"NUMBER": 51},
                    "Glide Rate":   {"NUMBER": 5}
                },
                "OSC 1": {
                    "Octave":       {"NUMBER": 63},
                    "Semitone":     {"NUMBER": 64},
                    "Detune":       {"NUMBER": 29},
                    "FM":           {"NUMBER": 30},
                    "Shape":        {"NUMBER": 31},
                    "PW":           {"NUMBER": 33},
                    "PWM":          {"NUMBER": 34}
                },
                "OSC 2": {
                    "Octave":       {"NUMBER": 35},
                    "Semitone":     {"NUMBER": 36},
                    "Detune":       {"NUMBER": 37},
                    "FM":           {"NUMBER": 38},
                    "Shape":        {"NUMBER": 39},
                    "PW":           {"NUMBER": 40},
                    "PWM":          {"NUMBER": 41}
                },
                "OSC 3": {
                    "Octave":       {"NUMBER": 42},
                    "Semitone":     {"NUMBER": 43},
                    "Detune":       {"NUMBER": 44},
                    "FM":           {"NUMBER": 45},
                    "Shape":        {"NUMBER": 46},
                    "PW":           {"NUMBER": 47},
                    "PWM":          {"NUMBER": 48}
                },

                # Noise
                "NOISE": {
                    "Colour":       {"NUMBER": 62}
                },

                # Filters
                "FILTER 1": {
                    "Type":         {"NUMBER": 68},
                    "Cutoff":       {"NUMBER": 69},
                    "Resonance":    {"NUMBER": 70},
                    "Drive":        {"NUMBER": 71},
                    "Keytrack":     {"NUMBER": 72},
                    "Env Amount":   {"NUMBER": 73},
                    "Env Velocity": {"NUMBER": 74},
                    "Mod":          {"NUMBER": 75},
                    "FM":           {"NUMBER": 76},
                    "Pan":          {"NUMBER": 77},
                    "Panmod":       {"NUMBER": 78}
                },
                "FILTER COMMON": {
                    "Routing":      {"NUMBER": 67}
                },
                "FILTER 2": {
                    "Type":         {"NUMBER": 79},
                    "Cutoff":       {"NUMBER": 80},
                    "Resonance":    {"NUMBER": 81},
                    "Drive":        {"NUMBER": 82},
                    "Keytrack":     {"NUMBER": 83},
                    "Env Amount":   {"NUMBER": 84},
                    "Env Velocity": {"NUMBER": 85},
                    "Mod":          {"NUMBER": 86},
                    "FM":           {"NUMBER": 87},
                    "Pan":          {"NUMBER": 88},
                    "Panmod":       {"NUMBER": 89}
                },

                # Envelopes
                "FILTER ENV": {
                    "Attack":       {"NUMBER": 95},
                    "Decay":        {"NUMBER": 96},
                    "Sustain":      {"NUMBER": 97},
                    "Decay 2":      {"NUMBER": 98},
                    "Sustain 2":    {"NUMBER": 99},
                    "Release":      {"NUMBER": 100}
                },
                "AMP ENV": {
                    "Attack":       {"NUMBER": 101},
                    "Decay":        {"NUMBER": 102},
                    "Sustain":      {"NUMBER": 103},
                    "Decay 2":      {"NUMBER": 104},
                    "Sustain 2":    {"NUMBER": 105},
                    "Release":      {"NUMBER": 106}
                },
                "ENV 3": {
                    "Attack":       {"NUMBER": 107},
                    "Decay":        {"NUMBER": 108},
                    "Sustain":      {"NUMBER": 109},
                    "Decay 2":      {"NUMBER": 110},
                    "Sustain 2":    {"NUMBER": 111},
                    "Release":      {"NUMBER": 112}
                },
                "ENV 4": {
                    "Attack":       {"NUMBER": 113},
                    "Decay":        {"NUMBER": 114},
                    "Sustain":      {"NUMBER": 115},
                    "Decay 2":      {"NUMBER": 116},
                    "Sustain 2":    {"NUMBER": 117},
                    "Release":      {"NUMBER": 118}
                },

                # LFOs
                "LFO 1": {
                    "Shape":        {"NUMBER": 15},
                    "Speed":        {"NUMBER": 16},
                    "Sync":         {"NUMBER": 17},
                    "Delay":        {"NUMBER": 18}
                },
                "LFO 2": {
                    "Shape":        {"NUMBER": 19},
                    "Speed":        {"NUMBER": 20},
                    "Sync":         {"NUMBER": 21},
                    "Delay":        {"NUMBER": 22}
                },
                "LFO 3": {
                    "Shape":        {"NUMBER": 23},
                    "Speed":        {"NUMBER": 24},
                    "Sync":         {"NUMBER": 25},
                    "Delay":        {"NUMBER": 26}
                },

                # Amplifier
                "AMP COMMON": {
                    "Volume":       {"NUMBER": 90},
                    "Velocity":     {"NUMBER": 91},
                    "Mod":          {"NUMBER": 92}
                },

                # Effects
                "EFFECTS": {
                    "Mix 1":        {"NUMBER": 93},
                    "Mix 2":        {"NUMBER": 94}
                },

                # Arpeggiator
                "ARPEGGIATOR": {
                    "Octave":       {"NUMBER": 12},
                    "Length":       {"NUMBER": 13},
                    "Mode":         {"NUMBER": 14}
                },

                # Mixers
                "MIXER COMMON": {
                    "Volume":       {"NUMBER": 7},
                    "Pan":          {"NUMBER": 10}
                },
                "MIXER OSC 1": {
                    "Level":        {"NUMBER": 52},
                    "Filter":       {"NUMBER": 53}
                },
                "MIXER OSC 2": {
                    "Level":        {"NUMBER": 56},
                    "Filter":       {"NUMBER": 57}
                },
                "MIXER OSC 3": {
                    "Level":        {"NUMBER": 58},
                    "Filter":       {"NUMBER": 59}
                },
                "MIXER RING": {
                    "Level":        {"NUMBER": 54},
                    "Filter":       {"NUMBER": 55}
                },
                "MIXER NOISE": {
                    "Level":        {"NUMBER": 60},
                    "Filter":       {"NUMBER": 61}
                }
            }

