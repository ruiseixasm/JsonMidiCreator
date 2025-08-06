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
from jsonmidicreator_import import *    # This ensures src is added & JsonMidiCreator is imported



# Devices to sync
# defaults << ClockedDevices("Digitakt", "Blofeld", "Virtual")
settings << ClockedDevices("VMPK")
# defaults += Device("Digitakt")

# Four Measures clips for Pattern Change
pattern_change_1 = Clip(ProgramChange(2, RD_Digitakt.auto_channel), Measures(3.5))   # Sets the NEXT pattern
pattern_change_2 = Clip(ProgramChange(1, RD_Digitakt.auto_channel), Measures(3.5))   # Returns to the Original pattern

# virtual_pattern_change = pattern_change_1 * pattern_change_2 << Device("Virtual")
# virtual_pattern_change = pattern_change_1 * pattern_change_2 << Device("Virtual")

# Cycle patterns change
entire_part = Part() << pattern_change_1 * pattern_change_2 * 1
# entire_part = Part() << virtual_pattern_change
# entire_part >> Play(1)
entire_part >> Export("json/Linux/_Export_Clock_basic.json")


