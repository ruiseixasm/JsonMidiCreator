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
import creator as c
import operand as o

import operand_unit as ou
import operand_rational as ra
import operand_data as od
import operand_label as ol
import operand_generic as og
import operand_element as oe
import operand_frame as of
import operand_container as oc
import operand_chaos as ch



class D_Blofeld:

    device          = od.Device("Blofeld")

    # Activate "Ctrl Receive" in "Shift + Global" and turn the data knob to select it on Global MIDI


    def program_change(sound: int, bank: str | int = "A") -> oe.ProgramChange:
        if isinstance(bank, str):
            bank = ou.Bank(D_Blofeld.banks[bank.strip().upper()])
        return oe.ProgramChange(sound, ou.Bank(bank))

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
        return oe.ControlChange(D_Blofeld.midi_cc[group][parameter])

    midi_cc: dict[str,
                dict[ str, dict[str, int] ]
            ] = {

                # Controllers
                "CONTROLLERS": {
                    "Modulation":   { "NUMBER": 1 },
                    "Breath":       { "NUMBER": 2 },
                    "Foot":         { "NUMBER": 4 },
                    "Sustain":      { "NUMBER": 64 }
                },

                # Oscillators
                "OSC COMMON": {
                    "Sync":         { "NUMBER": 49 },
                    "Pitchmod":     { "NUMBER": 50 },
                    "Glide Active": { "NUMBER": 65 },
                    "Glide Mode":   { "NUMBER": 51 },
                    "Glide Rate":   { "NUMBER": 5 }
                },
                "OSC 1": {
                    "Octave":       { "NUMBER": 63 },
                    "Semitone":     { "NUMBER": 64 },
                    "Detune":       { "NUMBER": 29 },
                    "FM":           { "NUMBER": 30 },
                    "Shape":        { "NUMBER": 31 },
                    "PW":           { "NUMBER": 33 },
                    "PWM":          { "NUMBER": 34 }
                },
                "OSC 2": {
                    "Octave":       { "NUMBER": 35 },
                    "Semitone":     { "NUMBER": 36 },
                    "Detune":       { "NUMBER": 37 },
                    "FM":           { "NUMBER": 38 },
                    "Shape":        { "NUMBER": 39 },
                    "PW":           { "NUMBER": 40 },
                    "PWM":          { "NUMBER": 41 }
                },
                "OSC 3": {
                    "Octave":       { "NUMBER": 42 },
                    "Semitone":     { "NUMBER": 43 },
                    "Detune":       { "NUMBER": 44 },
                    "FM":           { "NUMBER": 45 },
                    "Shape":        { "NUMBER": 46 },
                    "PW":           { "NUMBER": 47 },
                    "PWM":          { "NUMBER": 48 }
                },

                # Noise
                "NOISE": {
                    "Colour":       { "NUMBER": 62 }
                },

                # Filters
                "FILTER 1": {
                    "Type":         { "NUMBER": 68 },
                    "Cutoff":       { "NUMBER": 69 },
                    "Resonance":    { "NUMBER": 70 },
                    "Drive":        { "NUMBER": 71 },
                    "Keytrack":     { "NUMBER": 72 },
                    "Env Amount":   { "NUMBER": 73 },
                    "Env Velocity": { "NUMBER": 74 },
                    "Mod":          { "NUMBER": 75 },
                    "FM":           { "NUMBER": 76 },
                    "Pan":          { "NUMBER": 77 },
                    "Panmod":       { "NUMBER": 78 }
                },
                "FILTER COMMON": {
                    "Routing":      { "NUMBER": 67 }
                },
                "FILTER 2": {
                    "Type":         { "NUMBER": 79 },
                    "Cutoff":       { "NUMBER": 80 },
                    "Resonance":    { "NUMBER": 81 },
                    "Drive":        { "NUMBER": 82 },
                    "Keytrack":     { "NUMBER": 83 },
                    "Env Amount":   { "NUMBER": 84 },
                    "Env Velocity": { "NUMBER": 85 },
                    "Mod":          { "NUMBER": 86 },
                    "FM":           { "NUMBER": 87 },
                    "Pan":          { "NUMBER": 88 },
                    "Panmod":       { "NUMBER": 89 }
                },

                # Envelopes
                "FILTER ENV": {
                    "Attack":       { "NUMBER": 95 },
                    "Decay":        { "NUMBER": 96 },
                    "Sustain":      { "NUMBER": 97 },
                    "Decay 2":      { "NUMBER": 98 },
                    "Sustain 2":    { "NUMBER": 99 },
                    "Release":      { "NUMBER": 100 }
                },
                "AMP ENV": {
                    "Attack":       { "NUMBER": 101 },
                    "Decay":        { "NUMBER": 102 },
                    "Sustain":      { "NUMBER": 103 },
                    "Decay 2":      { "NUMBER": 104 },
                    "Sustain 2":    { "NUMBER": 105 },
                    "Release":      { "NUMBER": 106 }
                },
                "ENV 3": {
                    "Attack":       { "NUMBER": 107 },
                    "Decay":        { "NUMBER": 108 },
                    "Sustain":      { "NUMBER": 109 },
                    "Decay 2":      { "NUMBER": 110 },
                    "Sustain 2":    { "NUMBER": 111 },
                    "Release":      { "NUMBER": 112 }
                },
                "ENV 4": {
                    "Attack":       { "NUMBER": 113 },
                    "Decay":        { "NUMBER": 114 },
                    "Sustain":      { "NUMBER": 115 },
                    "Decay 2":      { "NUMBER": 116 },
                    "Sustain 2":    { "NUMBER": 117 },
                    "Release":      { "NUMBER": 118 }
                },

                # LFOs
                "LFO 1": {
                    "Shape":        { "NUMBER": 15 },
                    "Speed":        { "NUMBER": 16 },
                    "Sync":         { "NUMBER": 17 },
                    "Delay":        { "NUMBER": 18 }
                },
                "LFO 2": {
                    "Shape":        { "NUMBER": 19 },
                    "Speed":        { "NUMBER": 20 },
                    "Sync":         { "NUMBER": 21 },
                    "Delay":        { "NUMBER": 22 }
                },
                "LFO 3": {
                    "Shape":        { "NUMBER": 23 },
                    "Speed":        { "NUMBER": 24 },
                    "Sync":         { "NUMBER": 25 },
                    "Delay":        { "NUMBER": 26 }
                },

                # Amplifier
                "AMP COMMON": {
                    "Volume":       { "NUMBER": 90 },
                    "Velocity":     { "NUMBER": 91 },
                    "Mod":          { "NUMBER": 92 }
                },

                # Effects
                "EFFECTS": {
                    "Mix 1":        { "NUMBER": 93 },
                    "Mix 2":        { "NUMBER": 94 }
                },

                # Arpeggiator
                "ARPEGGIATOR": {
                    "Octave":       { "NUMBER": 12 },
                    "Length":       { "NUMBER": 13 },
                    "Mode":         { "NUMBER": 14 }
                },

                # Mixers
                "MIXER COMMON": {
                    "Volume":       { "NUMBER": 7 },
                    "Pan":          { "NUMBER": 10 }
                },
                "MIXER OSC 1": {
                    "Level":        { "NUMBER": 52 },
                    "Filter":       { "NUMBER": 53 }
                },
                "MIXER OSC 2": {
                    "Level":        { "NUMBER": 56 },
                    "Filter":       { "NUMBER": 57 }
                },
                "MIXER OSC 3": {
                    "Level":        { "NUMBER": 58 },
                    "Filter":       { "NUMBER": 59 }
                },
                "MIXER RING": {
                    "Level":        { "NUMBER": 54 },
                    "Filter":       { "NUMBER": 55 }
                },
                "MIXER NOISE": {
                    "Level":        { "NUMBER": 60 },
                    "Filter":       { "NUMBER": 61 }
                }
            }


class D_Digitakt:

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

    def program_change(pattern: int, bank: str | int = "A") -> oe.ProgramChange:
        if isinstance(bank, str):
            bank = D_Digitakt.bank_pattern[bank.strip().upper()][0]
        return oe.ProgramChange(bank + pattern)   # based 1 data

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
            return og.Controller(D_Digitakt.midi_nrpn[group][parameter])
        return og.Controller(D_Digitakt.midi_cc[group][parameter])

    midi_cc: dict[str,
                dict[str,
                    dict[str, int]
                ]
            ] = {
                # PER TRACK PARAMETERS (CHANNEL 1 TO 8)
                "TRACK": {
                    "Mute": {
                        "MSB": 94, "HIGH": False, "NRPN": False
                    },
                    "Level": {
                        "MSB": 95, "HIGH": False, "NRPN": False
                    }
                },
                "TRIG": {
                    "Note": {
                        "MSB": 3, "HIGH": False, "NRPN": False
                    },
                    "Velocity": {
                        "MSB": 4, "HIGH": False, "NRPN": False
                    },
                    "Length": {
                        "MSB": 5, "HIGH": False, "NRPN": False
                    },
                    "Filter": {
                        "MSB": 13, "HIGH": False, "NRPN": False
                    },
                    "LFO": {
                        "MSB": 14, "HIGH": False, "NRPN": False
                    }
                },
                "SOURCE": {
                    "Tune": {
                        "MSB": 16, "HIGH": False, "NRPN": False
                    },
                    "Mode": {
                        "MSB": 17, "HIGH": False, "NRPN": False
                    },
                    "Bit": {
                        "MSB": 18, "HIGH": False, "NRPN": False
                    },
                    "Sample": {
                        "MSB": 19, "HIGH": False, "NRPN": False
                    },
                    "Knob E": {
                        "MSB": 20, "HIGH": False, "NRPN": False
                    },
                    "Knob F": {
                        "MSB": 21, "HIGH": False, "NRPN": False
                    },
                    "Knob G": {
                        "MSB": 22, "HIGH": False, "NRPN": False
                    },
                    "Level": {
                        "MSB": 23, "HIGH": False, "NRPN": False
                    }
                },
                "FILTER": {
                    "Frequency": {
                        "MSB": 74, "HIGH": False, "NRPN": False
                    },
                    "Resonance": {
                        "MSB": 75, "HIGH": False, "NRPN": False
                    },
                    "Type": {
                        "MSB": 76, "HIGH": False, "NRPN": False
                    },
                    "Attack": {
                        "MSB": 70, "HIGH": False, "NRPN": False
                    },
                    "Decay": {
                        "MSB": 71, "HIGH": False, "NRPN": False
                    },
                    "Sustain": {
                        "MSB": 72, "HIGH": False, "NRPN": False
                    },
                    "Release": {
                        "MSB": 73, "HIGH": False, "NRPN": False
                    },
                    "Depth": {
                        "MSB": 77, "HIGH": False, "NRPN": False
                    },
                    "Delay": {
                        "MSB": 86, "HIGH": False, "NRPN": False
                    },
                    "Rate": {
                        "MSB": 87, "HIGH": False, "NRPN": False
                    },
                    "Base": {
                        "MSB": 84, "HIGH": False, "NRPN": False
                    },
                    "Width": {
                        "MSB": 85, "HIGH": False, "NRPN": False
                    },
                    "Routing": {
                        "MSB": 88, "HIGH": False, "NRPN": False
                    }
                },
                "AMP": {
                    "Attack": {
                        "MSB": 78, "HIGH": False, "NRPN": False
                    },
                    "Hold": {
                        "MSB": 79, "HIGH": False, "NRPN": False
                    },
                    "Decay": {
                        "MSB": 80, "HIGH": False, "NRPN": False
                    },
                    "Overdrive": {
                        "MSB": 81, "HIGH": False, "NRPN": False
                    },
                    "Delay": {
                        "MSB": 82, "HIGH": False, "NRPN": False
                    },
                    "Reverb": {
                        "MSB": 83, "HIGH": False, "NRPN": False
                    },
                    "Pan": {
                        "MSB": 10, "HIGH": False, "NRPN": False
                    },
                    "Volume": {
                        "MSB": 7, "HIGH": False, "NRPN": False
                    }
                },
                "LFO 1": {
                    "Speed": {
                        "MSB": 102, "HIGH": False, "NRPN": False
                    },
                    "Multiplier": {
                        "MSB": 103, "HIGH": False, "NRPN": False
                    },
                    "Fade": {
                        "MSB": 104, "HIGH": False, "NRPN": False
                    },
                    "Destination": {
                        "MSB": 105, "HIGH": False, "NRPN": False
                    },
                    "Waveform": {
                        "MSB": 106, "HIGH": False, "NRPN": False
                    },
                    "Phase": {
                        "MSB": 107, "HIGH": False, "NRPN": False
                    },
                    "Mode": {
                        "MSB": 108, "HIGH": False, "NRPN": False
                    },
                    "Depth": {
                        "MSB": 109, "LSB": 61, "HIGH": True, "NRPN": False
                    }
                },
                "LFO 2": {
                    "Speed": {
                        "MSB": 112, "HIGH": False, "NRPN": False
                    },
                    "Multiplier": {
                        "MSB": 113, "HIGH": False, "NRPN": False
                    },
                    "Fade": {
                        "MSB": 114, "HIGH": False, "NRPN": False
                    },
                    "Destination": {
                        "MSB": 115, "HIGH": False, "NRPN": False
                    },
                    "Waveform": {
                        "MSB": 116, "HIGH": False, "NRPN": False
                    },
                    "Phase": {
                        "MSB": 117, "HIGH": False, "NRPN": False
                    },
                    "Mode": {
                        "MSB": 118, "HIGH": False, "NRPN": False
                    },
                    "Depth": {
                        "MSB": 119, "LSB": 63, "HIGH": True, "NRPN": False
                    }
                },
                "MIDI": {
                    "Val1": {
                        "MSB": 70, "HIGH": False, "NRPN": False
                    },
                    "Val2": {
                        "MSB": 71, "HIGH": False, "NRPN": False
                    },
                    "Val3": {
                        "MSB": 72, "HIGH": False, "NRPN": False
                    },
                    "Val4": {
                        "MSB": 73, "HIGH": False, "NRPN": False
                    },
                    "Val5": {
                        "MSB": 74, "HIGH": False, "NRPN": False
                    },
                    "Val6": {
                        "MSB": 75, "HIGH": False, "NRPN": False
                    },
                    "Val7": {
                        "MSB": 76, "HIGH": False, "NRPN": False
                    },
                    "Val8": {
                        "MSB": 77, "HIGH": False, "NRPN": False
                    }
                },

                # PER PATTERN PARAMETERS (CHANNEL 9)
                "DELAY": {
                    "Time": {
                        "MSB": 85, "HIGH": False, "NRPN": False
                    },
                    "Pingpong": {
                        "MSB": 86, "HIGH": False, "NRPN": False
                    },
                    "Width": {
                        "MSB": 87, "HIGH": False, "NRPN": False
                    },
                    "Feedback": {
                        "MSB": 88, "HIGH": False, "NRPN": False
                    },
                    "Highpass": {
                        "MSB": 89, "HIGH": False, "NRPN": False
                    },
                    "Lowpass": {
                        "MSB": 90, "HIGH": False, "NRPN": False
                    },
                    "Reverb": {
                        "MSB": 91, "HIGH": False, "NRPN": False
                    },
                    "Mix": {
                        "MSB": 92, "HIGH": False, "NRPN": False
                    }
                },
                "REVERB": {
                    "Predelay": {
                        "MSB": 24, "HIGH": False, "NRPN": False
                    },
                    "Decay": {
                        "MSB": 25, "HIGH": False, "NRPN": False
                    },
                    "Frequency": {
                        "MSB": 26, "HIGH": False, "NRPN": False
                    },
                    "Gain": {
                        "MSB": 27, "HIGH": False, "NRPN": False
                    },
                    "Highpass": {
                        "MSB": 28, "HIGH": False, "NRPN": False
                    },
                    "Lowpass": {
                        "MSB": 29, "HIGH": False, "NRPN": False
                    },
                    "Reverb": {
                        "MSB": 30, "HIGH": False, "NRPN": False
                    },
                    "Mix": {
                        "MSB": 31, "HIGH": False, "NRPN": False
                    }
                },
                "COMPRESSOR": {
                    "Threshold": {
                        "MSB": 111, "HIGH": False, "NRPN": False
                    },
                    "Attack": {
                        "MSB": 112, "HIGH": False, "NRPN": False
                    },
                    "Release": {
                        "MSB": 113, "HIGH": False, "NRPN": False
                    },
                    "Gain": {
                        "MSB": 114, "HIGH": False, "NRPN": False
                    },
                    "Volume": {
                        "MSB": 119, "HIGH": False, "NRPN": False
                    },
                    "Ratio": {
                        "MSB": 115, "HIGH": False, "NRPN": False
                    },
                    "Source": {
                        "MSB": 116, "HIGH": False, "NRPN": False
                    },
                    "Filter": {
                        "MSB": 117, "HIGH": False, "NRPN": False
                    },
                    "Mix": {
                        "MSB": 118, "HIGH": False, "NRPN": False
                    }
                },
                "MIXER": {
                    "Level L": {
                        "MSB": 102, "HIGH": False, "NRPN": False
                    },
                    "Pan L": {
                        "MSB": 103, "HIGH": False, "NRPN": False
                    },
                    "Level R": {
                        "MSB": 104, "HIGH": False, "NRPN": False
                    },
                    "Pan R": {
                        "MSB": 105, "HIGH": False, "NRPN": False
                    },
                    "Delay L": {
                        "MSB": 106, "HIGH": False, "NRPN": False
                    },
                    "Delay R": {
                        "MSB": 107, "HIGH": False, "NRPN": False
                    },
                    "Reverb L": {
                        "MSB": 108, "HIGH": False, "NRPN": False
                    },
                    "Reverb R": {
                        "MSB": 109, "HIGH": False, "NRPN": False
                    },
                    "Stereo": {
                        "MSB": 84, "HIGH": False, "NRPN": False
                    },
                    "LR Level": {
                        "MSB": 102, "HIGH": False, "NRPN": False
                    },
                    "LR Balance": {
                        "MSB": 103, "HIGH": False, "NRPN": False
                    },
                    "LR Delay": {
                        "MSB": 106, "HIGH": False, "NRPN": False
                    },
                    "LR Reverb": {
                        "MSB": 108, "HIGH": False, "NRPN": False
                    }
                },
                "PATTERN": {
                    "Mute": {
                        "MSB": 110, "HIGH": False, "NRPN": False
                    }
                }
            }


    midi_nrpn: dict[str,
                dict[str,
                    dict[str, int]
                ]
            ] = {
                # PER TRACK PARAMETERS (CHANNEL 1 TO 8)
                "TRACK": {
                    "Mute": {
                        "MSB": 1, "LSB": 101, "HIGH": False, "NRPN": True
                    },
                    "Level": {
                        "MSB": 1, "LSB": 100, "HIGH": False, "NRPN": True
                    }
                },
                "TRIG": {
                    "Note": {
                        "MSB": 3, "LSB": 0, "HIGH": False, "NRPN": True
                    },
                    "Velocity": {
                        "MSB": 3, "LSB": 1, "HIGH": False, "NRPN": True
                    },
                    "Length": {
                        "MSB": 3, "LSB": 2, "HIGH": False, "NRPN": True
                    },
                    "Filter": {
                    },
                    "LFO": {
                    }
                },
                "SOURCE": {
                    "Tune": {
                        "MSB": 1, "LSB": 0, "HIGH": False, "NRPN": True
                    },
                    "Mode": {
                        "MSB": 1, "LSB": 1, "HIGH": False, "NRPN": True
                    },
                    "Bit": {
                        "MSB": 1, "LSB": 2, "HIGH": False, "NRPN": True
                    },
                    "Sample": {
                        "MSB": 1, "LSB": 3, "HIGH": False, "NRPN": True
                    },
                    "Knob E": {
                        "MSB": 1, "LSB": 4, "HIGH": False, "NRPN": True
                    },
                    "Knob F": {
                        "MSB": 1, "LSB": 5, "HIGH": False, "NRPN": True
                    },
                    "Knob G": {
                        "MSB": 1, "LSB": 6, "HIGH": False, "NRPN": True
                    },
                    "Level": {
                        "MSB": 1, "LSB": 7, "HIGH": False, "NRPN": True
                    }
                },
                "FILTER": {
                    "Frequency": {
                        "MSB": 1, "LSB": 20, "HIGH": False, "NRPN": True
                    },
                    "Resonance": {
                        "MSB": 1, "LSB": 21, "HIGH": False, "NRPN": True
                    },
                    "Type": {
                        "MSB": 1, "LSB": 22, "HIGH": False, "NRPN": True
                    },
                    "Attack": {
                        "MSB": 1, "LSB": 16, "HIGH": False, "NRPN": True
                    },
                    "Decay": {
                        "MSB": 1, "LSB": 17, "HIGH": False, "NRPN": True
                    },
                    "Sustain": {
                        "MSB": 1, "LSB": 18, "HIGH": False, "NRPN": True
                    },
                    "Release": {
                        "MSB": 1, "LSB": 19, "HIGH": False, "NRPN": True
                    },
                    "Depth": {
                        "MSB": 1, "LSB": 23, "HIGH": False, "NRPN": True
                    },
                    "Delay": {
                        "MSB": 1, "LSB": 50, "HIGH": False, "NRPN": True
                    },
                    "Rate": {
                        "MSB": 1, "LSB": 53, "HIGH": False, "NRPN": True
                    },
                    "Base": {
                        "MSB": 1, "LSB": 51, "HIGH": False, "NRPN": True
                    },
                    "Width": {
                        "MSB": 1, "LSB": 52, "HIGH": False, "NRPN": True
                    },
                    "Routing": {
                        "MSB": 1, "LSB": 54, "HIGH": False, "NRPN": True
                    }
                },
                "AMP": {
                    "Attack": {
                        "MSB": 1, "LSB": 24, "HIGH": False, "NRPN": True
                    },
                    "Hold": {
                        "MSB": 1, "LSB": 25, "HIGH": False, "NRPN": True
                    },
                    "Decay": {
                        "MSB": 1, "LSB": 26, "HIGH": False, "NRPN": True
                    },
                    "Overdrive": {
                        "MSB": 1, "LSB": 27, "HIGH": False, "NRPN": True
                    },
                    "Delay": {
                        "MSB": 1, "LSB": 28, "HIGH": False, "NRPN": True
                    },
                    "Reverb": {
                        "MSB": 1, "LSB": 29, "HIGH": False, "NRPN": True
                    },
                    "Pan": {
                        "MSB": 1, "LSB": 30, "HIGH": False, "NRPN": True
                    },
                    "Volume": {
                        "MSB": 1, "LSB": 31, "HIGH": False, "NRPN": True
                    }
                },
                "LFO 1": {
                    "Speed": {
                        "MSB": 1, "LSB": 32, "HIGH": False, "NRPN": True
                    },
                    "Multiplier": {
                        "MSB": 1, "LSB": 33, "HIGH": False, "NRPN": True
                    },
                    "Fade": {
                        "MSB": 1, "LSB": 34, "HIGH": False, "NRPN": True
                    },
                    "Destination": {
                        "MSB": 1, "LSB": 35, "HIGH": False, "NRPN": True
                    },
                    "Waveform": {
                        "MSB": 1, "LSB": 36, "HIGH": False, "NRPN": True
                    },
                    "Phase": {
                        "MSB": 1, "LSB": 37, "HIGH": False, "NRPN": True
                    },
                    "Mode": {
                        "MSB": 1, "LSB": 38, "HIGH": False, "NRPN": True
                    },
                    "Depth": {
                        "MSB": 1, "LSB": 39, "HIGH": False, "NRPN": True
                    }
                },
                "LFO 2": {
                    "Speed": {
                        "MSB": 1, "LSB": 40, "HIGH": False, "NRPN": True
                    },
                    "Multiplier": {
                        "MSB": 1, "LSB": 41, "HIGH": False, "NRPN": True
                    },
                    "Fade": {
                        "MSB": 1, "LSB": 42, "HIGH": False, "NRPN": True
                    },
                    "Destination": {
                        "MSB": 1, "LSB": 43, "HIGH": False, "NRPN": True
                    },
                    "Waveform": {
                        "MSB": 1, "LSB": 44, "HIGH": False, "NRPN": True
                    },
                    "Phase": {
                        "MSB": 1, "LSB": 45, "HIGH": False, "NRPN": True
                    },
                    "Mode": {
                        "MSB": 1, "LSB": 46, "HIGH": False, "NRPN": True
                    },
                    "Depth": {
                        "MSB": 1, "LSB": 47, "HIGH": False, "NRPN": True
                    }
                },
                "MIDI": {
                    "Val1": {
                    },
                    "Val2": {
                    },
                    "Val3": {
                    },
                    "Val4": {
                    },
                    "Val5": {
                    },
                    "Val6": {
                    },
                    "Val7": {
                    },
                    "Val8": {
                    }
                },

                # PER PATTERN PARAMETERS (CHANNEL 9)
                "DELAY": {
                    "Time": {
                        "MSB": 2, "LSB": 0, "HIGH": False, "NRPN": True
                    },
                    "Pingpong": {
                        "MSB": 2, "LSB": 1, "HIGH": False, "NRPN": True
                    },
                    "Width": {
                        "MSB": 2, "LSB": 2, "HIGH": False, "NRPN": True
                    },
                    "Feedback": {
                        "MSB": 2, "LSB": 3, "HIGH": False, "NRPN": True
                    },
                    "Highpass": {
                        "MSB": 2, "LSB": 4, "HIGH": False, "NRPN": True
                    },
                    "Lowpass": {
                        "MSB": 2, "LSB": 5, "HIGH": False, "NRPN": True
                    },
                    "Reverb": {
                        "MSB": 2, "LSB": 6, "HIGH": False, "NRPN": True
                    },
                    "Mix": {
                        "MSB": 2, "LSB": 7, "HIGH": False, "NRPN": True
                    }
                },
                "REVERB": {
                    "Predelay": {
                        "MSB": 2, "LSB": 8, "HIGH": False, "NRPN": True
                    },
                    "Decay": {
                        "MSB": 2, "LSB": 9, "HIGH": False, "NRPN": True
                    },
                    "Frequency": {
                        "MSB": 2, "LSB": 10, "HIGH": False, "NRPN": True
                    },
                    "Gain": {
                        "MSB": 2, "LSB": 11, "HIGH": False, "NRPN": True
                    },
                    "Highpass": {
                        "MSB": 2, "LSB": 12, "HIGH": False, "NRPN": True
                    },
                    "Lowpass": {
                        "MSB": 2, "LSB": 13, "HIGH": False, "NRPN": True
                    },
                    "Reverb": {
                        "MSB": 2, "LSB": 14, "HIGH": False, "NRPN": True
                    },
                    "Mix": {
                        "MSB": 2, "LSB": 15, "HIGH": False, "NRPN": True
                    }
                },
                "COMPRESSOR": {
                    "Threshold": {
                        "MSB": 2, "LSB": 16, "HIGH": False, "NRPN": True
                    },
                    "Attack": {
                        "MSB": 2, "LSB": 17, "HIGH": False, "NRPN": True
                    },
                    "Release": {
                        "MSB": 2, "LSB": 18, "HIGH": False, "NRPN": True
                    },
                    "Gain": {
                        "MSB": 2, "LSB": 19, "HIGH": False, "NRPN": True
                    },
                    "Volume": {
                        "MSB": 2, "LSB": 24, "HIGH": False, "NRPN": True
                    },
                    "Ratio": {
                        "MSB": 2, "LSB": 20, "HIGH": False, "NRPN": True
                    },
                    "Source": {
                        "MSB": 2, "LSB": 21, "HIGH": False, "NRPN": True
                    },
                    "Filter": {
                        "MSB": 2, "LSB": 22, "HIGH": False, "NRPN": True
                    },
                    "Mix": {
                        "MSB": 2, "LSB": 23, "HIGH": False, "NRPN": True
                    }
                },
                "MIXER": {
                    "Level L": {
                        "MSB": 2, "LSB": 30, "HIGH": False, "NRPN": True
                    },
                    "Pan L": {
                        "MSB": 2, "LSB": 31, "HIGH": False, "NRPN": True
                    },
                    "Level R": {
                        "MSB": 2, "LSB": 32, "HIGH": False, "NRPN": True
                    },
                    "Pan R": {
                        "MSB": 2, "LSB": 33, "HIGH": False, "NRPN": True
                    },
                    "Delay L": {
                        "MSB": 2, "LSB": 34, "HIGH": False, "NRPN": True
                    },
                    "Delay R": {
                        "MSB": 2, "LSB": 35, "HIGH": False, "NRPN": True
                    },
                    "Reverb L": {
                        "MSB": 2, "LSB": 36, "HIGH": False, "NRPN": True
                    },
                    "Reverb R": {
                        "MSB": 2, "LSB": 37, "HIGH": False, "NRPN": True
                    },
                    "Stereo": {
                        "MSB": 2, "LSB": 38, "HIGH": False, "NRPN": True
                    },
                    "LR Level": {
                        "MSB": 2, "LSB": 30, "HIGH": False, "NRPN": True
                    },
                    "LR Balance": {
                        "MSB": 2, "LSB": 31, "HIGH": False, "NRPN": True
                    },
                    "LR Delay": {
                        "MSB": 2, "LSB": 34, "HIGH": False, "NRPN": True
                    },
                    "LR Reverb": {
                        "MSB": 2, "LSB": 36, "HIGH": False, "NRPN": True
                    }
                },
                "PATTERN": {
                    "Mute": {
                        "MSB": 1, "LSB": 104, "HIGH": False, "NRPN": True
                    }
                }
            }


class D_UnoSynth:

    device          = od.Device("UNO")

    def control_change(parameter: str = "Cutoff", group: str = "FILTER") -> oe.ControlChange:
        parameter = parameter.strip()
        group = group.strip().upper()
        return oe.ControlChange(D_UnoSynth.midi_cc[group][parameter])

    midi_cc: dict[str,
                dict[ str, dict[str, int] ]
            ] = {

                # Controllers
                "CONTROLLERS": {
                    "Modulation":   { "NUMBER": 1 },
                    "Glide":        { "NUMBER": 65 },
                    "Sustain":      { "NUMBER": 64 }
                },

                # Oscillators
                "OSC COMMON": {
                    "Glide Time":   { "NUMBER": 5 }
                },
                "OSC 1": {
                    "Level":        { "NUMBER": 12 },
                    "Wave":         { "NUMBER": 15 },
                    "Tune":         { "NUMBER": 17 },
                    "PWM":          { "NUMBER": 48 },
                    "Wave":         { "NUMBER": 50 }
                },
                "OSC 2": {
                    "Level":        { "NUMBER": 13 },
                    "Wave":         { "NUMBER": 16 },
                    "Tune":         { "NUMBER": 18 },
                    "PWM":          { "NUMBER": 49 },
                    "Wave":         { "NUMBER": 51 }
                },

                # Noise
                "NOISE": {
                    "Level":        { "NUMBER": 14 }
                },

                # On Off
                "ON OFF": {
                    "Vibrato":      { "NUMBER": 77 },
                    "Wah":          { "NUMBER": 78 },
                    "Tremolo":      { "NUMBER": 79 },
                    "Arpeggiator":  { "NUMBER": 82 },
                    "Dive":         { "NUMBER": 89 },
                    "Scoop":        { "NUMBER": 91 }
                },

                # Effects
                "EFFECTS": {
                    "Dive":         { "NUMBER": 90 },
                    "Scoop":        { "NUMBER": 92 },
                    "Pitch Bend Range":
                                    { "NUMBER": 101 }
                },

                # Delay
                "DELAY": {
                    "Time":         { "NUMBER": 80 },
                    "Mix":          { "NUMBER": 81 }
                },

                # Modulation
                "MODULATION": {
                    "LFO":          { "NUMBER": 93 },
                    "Vibrato":      { "NUMBER": 94 },
                    "Wah":          { "NUMBER": 95 },
                    "Tremolo":      { "NUMBER": 96 },
                    "Cutoff":       { "NUMBER": 97 }
                },

                # Velocity
                "VELOCITY": {
                    "VCA Amount":   { "NUMBER": 102 },
                    "Cutoff":       { "NUMBER": 103 },
                    "Envelop":      { "NUMBER": 104 },
                    "LFO Rate":     { "NUMBER": 105 },
                    "Notes Off":    { "NUMBER": 123 }
                },

                # Filters
                "FILTER": {
                    "Mode":         { "NUMBER": 19 },
                    "Cutoff":       { "NUMBER": 20 },
                    "Resonance":    { "NUMBER": 21 },
                    "Drive":        { "NUMBER": 22 },
                    "Env Amount":   { "NUMBER": 23 },
                    "Keytrack":     { "NUMBER": 106 }
                },

                # Envelopes
                "FILTER ENV": {
                    "Attack":       { "NUMBER": 44 },
                    "Decay":        { "NUMBER": 45 },
                    "Sustain":      { "NUMBER": 46 },
                    "Release":      { "NUMBER": 47 }
                },
                "AMP ENV": {
                    "Attack":       { "NUMBER": 24 },
                    "Decay":        { "NUMBER": 25 },
                    "Sustain":      { "NUMBER": 26 },
                    "Release":      { "NUMBER": 27 }
                },

                # LFOs
                "LFO": {
                    "Wave":         { "NUMBER": 66 },
                    "Rate":         { "NUMBER": 67 },
                    "Pitch":        { "NUMBER": 68 },
                    "Cutoff":       { "NUMBER": 69 },
                    "Tremolo":      { "NUMBER": 70 },
                    "Wah":          { "NUMBER": 71 },
                    "Vibrato":      { "NUMBER": 72 },
                    "PWM 1":        { "NUMBER": 73 },
                    "PWM 2":        { "NUMBER": 74 },
                    "Waveform 1":   { "NUMBER": 75 },
                    "Waveform 2":   { "NUMBER": 76 }
                },

                # Arpeggiator
                "ARPEGGIATOR": {
                    "Direction":    { "NUMBER": 83 },
                    "Range":        { "NUMBER": 84 },
                    "Gate":         { "NUMBER": 85 },
                    "Swing":        { "NUMBER": 9 }
                },

                # Sequencer
                "SEQUENCER": {
                    "Direction":    { "NUMBER": 86 },
                    "Range":        { "NUMBER": 87 },
                    "Gate":         { "NUMBER": 85 },
                    "Swing":        { "NUMBER": 9 }
                },

                # Mixers
                "MIXER COMMON": {
                    "Volume":       { "NUMBER": 7 },
                    "Balance":      { "NUMBER": 8 }
                },

                # Scale
                "SCALE": {
                    "Type":         { "NUMBER": 120 }
                }
            }


