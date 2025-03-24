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


class Variables(o.Operand):
    pass


class Blofeld(Variables):

    device          = od.Device("Blofeld")


class Digitakt(Variables):

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

    midi_cc: dict[str,
                dict[str,
                    dict[str, int]
                ]
            ] = {
                # PER TRACK PARAMETERS (CHANNEL 1 TO 8)
                "TRACK": {
                    "Mute": {
                        "MSB": 94, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Level": {
                        "MSB": 95, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "TRIG": {
                    "Note": {
                        "MSB": 3, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Velocity": {
                        "MSB": 4, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Length": {
                        "MSB": 5, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Filter": {
                        "MSB": 13, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "LFO": {
                        "MSB": 14, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "SOURCE": {
                    "Tune": {
                        "MSB": 16, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Mode": {
                        "MSB": 17, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Bit": {
                        "MSB": 18, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Sample": {
                        "MSB": 19, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Knob E": {
                        "MSB": 20, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Knob F": {
                        "MSB": 21, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Knob G": {
                        "MSB": 22, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Level": {
                        "MSB": 23, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "FILTER": {
                    "Frequency": {
                        "MSB": 74, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Resonance": {
                        "MSB": 75, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Type": {
                        "MSB": 76, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Attack": {
                        "MSB": 70, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Decay": {
                        "MSB": 71, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Sustain": {
                        "MSB": 72, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Release": {
                        "MSB": 73, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Depth": {
                        "MSB": 77, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Delay": {
                        "MSB": 86, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Rate": {
                        "MSB": 87, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Base": {
                        "MSB": 84, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Width": {
                        "MSB": 85, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Routing": {
                        "MSB": 88, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "AMP": {
                    "Attack": {
                        "MSB": 78, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Hold": {
                        "MSB": 79, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Decay": {
                        "MSB": 80, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Overdrive": {
                        "MSB": 81, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Delay": {
                        "MSB": 82, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Reverb": {
                        "MSB": 83, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Pan": {
                        "MSB": 10, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Volume": {
                        "MSB": 7, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "LFO 1": {
                    "Speed": {
                        "MSB": 102, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Multiplier": {
                        "MSB": 103, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Fade": {
                        "MSB": 104, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Destination": {
                        "MSB": 105, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Waveform": {
                        "MSB": 106, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Phase": {
                        "MSB": 107, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Mode": {
                        "MSB": 108, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Depth": {
                        "MSB": 109, "LSB": 61   # Non blank, with LSB, 14 bits
                    }
                },
                "LFO 2": {
                    "Speed": {
                        "MSB": 112, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Multiplier": {
                        "MSB": 113, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Fade": {
                        "MSB": 114, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Destination": {
                        "MSB": 115, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Waveform": {
                        "MSB": 116, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Phase": {
                        "MSB": 117, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Mode": {
                        "MSB": 118, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Depth": {
                        "MSB": 119, "LSB": 63   # Non blank, with LSB, 14 bits
                    }
                },
                "MIDI": {
                    "Val1": {
                        "MSB": 70, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Val2": {
                        "MSB": 71, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Val3": {
                        "MSB": 72, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Val4": {
                        "MSB": 73, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Val5": {
                        "MSB": 74, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Val6": {
                        "MSB": 75, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Val7": {
                        "MSB": 76, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Val8": {
                        "MSB": 77, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },

                # PER PATTERN PARAMETERS (CHANNEL 9)
                "DELAY": {
                    "Time": {
                        "MSB": 85, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Pingpong": {
                        "MSB": 86, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Width": {
                        "MSB": 87, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Feedback": {
                        "MSB": 88, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Highpass": {
                        "MSB": 89, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Lowpass": {
                        "MSB": 90, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Reverb": {
                        "MSB": 91, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Mix": {
                        "MSB": 92, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "REVERB": {
                    "Predelay": {
                        "MSB": 24, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Decay": {
                        "MSB": 25, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Frequency": {
                        "MSB": 26, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Gain": {
                        "MSB": 27, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Highpass": {
                        "MSB": 28, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Lowpass": {
                        "MSB": 29, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Reverb": {
                        "MSB": 30, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Mix": {
                        "MSB": 31, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "COMPRESSOR": {
                    "Threshold": {
                        "MSB": 111, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Attack": {
                        "MSB": 112, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Release": {
                        "MSB": 113, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Gain": {
                        "MSB": 114, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Volume": {
                        "MSB": 119, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Ratio": {
                        "MSB": 115, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Source": {
                        "MSB": 116, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Filter": {
                        "MSB": 117, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Mix": {
                        "MSB": 118, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "MIXER": {
                    "Level L": {
                        "MSB": 102, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Pan L": {
                        "MSB": 103, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Level R": {
                        "MSB": 104, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Pan R": {
                        "MSB": 105, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Delay L": {
                        "MSB": 106, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Delay R": {
                        "MSB": 107, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Reverb L": {
                        "MSB": 108, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Reverb R": {
                        "MSB": 109, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "Stereo": {
                        "MSB": 84, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "LR Level": {
                        "MSB": 102, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "LR Balance": {
                        "MSB": 103, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "LR Delay": {
                        "MSB": 106, "LSB": -1   # Blank, no LSB, 7 bits
                    },
                    "LR Reverb": {
                        "MSB": 108, "LSB": -1   # Blank, no LSB, 7 bits
                    }
                },
                "PATTERN": {
                    "Mute": {
                        "MSB": 110, "LSB": -1   # Blank, no LSB, 7 bits
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
                        "MSB": 1, "LSB": 101, "NRPN": True
                    },
                    "Level": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    }
                },
                "TRIG": {
                    "Note": {
                        "MSB": 3, "LSB": 0, "NRPN": True
                    },
                    "Velocity": {
                        "MSB": 3, "LSB": 1, "NRPN": True
                    },
                    "Length": {
                        "MSB": 3, "LSB": 2, "NRPN": True
                    },
                    "Filter": {
                    },
                    "LFO": {
                    }
                },
                "SOURCE": {
                    "Tune": {
                        "MSB": 1, "LSB": 0, "NRPN": True
                    },
                    "Mode": {
                        "MSB": 1, "LSB": 1, "NRPN": True
                    },
                    "Bit": {
                        "MSB": 1, "LSB": 2, "NRPN": True
                    },
                    "Sample": {
                        "MSB": 1, "LSB": 3, "NRPN": True
                    },
                    "Knob E": {
                        "MSB": 1, "LSB": 4, "NRPN": True
                    },
                    "Knob F": {
                        "MSB": 1, "LSB": 5, "NRPN": True
                    },
                    "Knob G": {
                        "MSB": 1, "LSB": 6, "NRPN": True
                    },
                    "Level": {
                        "MSB": 1, "LSB": 7, "NRPN": True
                    }
                },
                "FILTER": {
                    "Frequency": {
                        "MSB": 1, "LSB": 20, "NRPN": True
                    },
                    "Resonance": {
                        "MSB": 1, "LSB": 21, "NRPN": True
                    },
                    "Type": {
                        "MSB": 1, "LSB": 22, "NRPN": True
                    },
                    "Attack": {
                        "MSB": 1, "LSB": 16, "NRPN": True
                    },
                    "Decay": {
                        "MSB": 1, "LSB": 17, "NRPN": True
                    },
                    "Sustain": {
                        "MSB": 1, "LSB": 18, "NRPN": True
                    },
                    "Release": {
                        "MSB": 1, "LSB": 19, "NRPN": True
                    },
                    "Depth": {
                        "MSB": 1, "LSB": 23, "NRPN": True
                    },
                    "Delay": {
                        "MSB": 1, "LSB": 50, "NRPN": True
                    },
                    "Rate": {
                        "MSB": 1, "LSB": 53, "NRPN": True
                    },
                    "Base": {
                        "MSB": 1, "LSB": 51, "NRPN": True
                    },
                    "Width": {
                        "MSB": 1, "LSB": 52, "NRPN": True
                    },
                    "Routing": {
                        "MSB": 1, "LSB": 54, "NRPN": True
                    }
                },
                "AMP": {
                    "Attack": {
                        "MSB": 1, "LSB": 24, "NRPN": True
                    },
                    "Hold": {
                        "MSB": 1, "LSB": 25, "NRPN": True
                    },
                    "Decay": {
                        "MSB": 1, "LSB": 26, "NRPN": True
                    },
                    "Overdrive": {
                        "MSB": 1, "LSB": 27, "NRPN": True
                    },
                    "Delay": {
                        "MSB": 1, "LSB": 28, "NRPN": True
                    },
                    "Reverb": {
                        "MSB": 1, "LSB": 29, "NRPN": True
                    },
                    "Pan": {
                        "MSB": 1, "LSB": 30, "NRPN": True
                    },
                    "Volume": {
                        "MSB": 1, "LSB": 31, "NRPN": True
                    }
                },
                "LFO 1": {
                    "Speed": {
                        "MSB": 1, "LSB": 32, "NRPN": True
                    },
                    "Multiplier": {
                        "MSB": 1, "LSB": 33, "NRPN": True
                    },
                    "Fade": {
                        "MSB": 1, "LSB": 34, "NRPN": True
                    },
                    "Destination": {
                        "MSB": 1, "LSB": 35, "NRPN": True
                    },
                    "Waveform": {
                        "MSB": 1, "LSB": 36, "NRPN": True
                    },
                    "Phase": {
                        "MSB": 1, "LSB": 37, "NRPN": True
                    },
                    "Mode": {
                        "MSB": 1, "LSB": 38, "NRPN": True
                    },
                    "Depth": {
                        "MSB": 1, "LSB": 39, "NRPN": True
                    }
                },
                "LFO 2": {
                    "Speed": {
                        "MSB": 1, "LSB": 40, "NRPN": True
                    },
                    "Multiplier": {
                        "MSB": 1, "LSB": 41, "NRPN": True
                    },
                    "Fade": {
                        "MSB": 1, "LSB": 42, "NRPN": True
                    },
                    "Destination": {
                        "MSB": 1, "LSB": 43, "NRPN": True
                    },
                    "Waveform": {
                        "MSB": 1, "LSB": 44, "NRPN": True
                    },
                    "Phase": {
                        "MSB": 1, "LSB": 45, "NRPN": True
                    },
                    "Mode": {
                        "MSB": 1, "LSB": 46, "NRPN": True
                    },
                    "Depth": {
                        "MSB": 1, "LSB": 47, "NRPN": True
                    }
                },
                "MIDI": {
                    "Val1": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Val2": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Val3": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Val4": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Val5": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Val6": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Val7": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Val8": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    }
                },

                # PER PATTERN PARAMETERS (CHANNEL 9)
                "DELAY": {
                    "Time": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Pingpong": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Width": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Feedback": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Highpass": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Lowpass": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Reverb": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Mix": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    }
                },
                "REVERB": {
                    "Predelay": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Decay": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Frequency": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Gain": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Highpass": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Lowpass": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Reverb": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Mix": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    }
                },
                "COMPRESSOR": {
                    "Threshold": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Attack": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Release": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Gain": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Volume": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Ratio": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Source": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Filter": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Mix": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    }
                },
                "MIXER": {
                    "Level L": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Pan L": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Level R": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Pan R": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Delay L": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Delay R": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Reverb L": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Reverb R": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "Stereo": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "LR Level": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "LR Balance": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "LR Delay": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    },
                    "LR Reverb": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    }
                },
                "PATTERN": {
                    "Mute": {
                        "MSB": 1, "LSB": 100, "NRPN": True
                    }
                }
            }

