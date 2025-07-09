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

settings % Devices() % list() >> Print()
settings += D_Digitakt.device
settings % Devices() % list() >> Print()

# Send Clock signal to the Digitakt
settings % ClockedDevices() % list() >> Print()
settings << ClockedDevices(D_Digitakt.device)
# defaults << ClockedDevices("loopMIDI", "VMPK", "FLUID")
settings % ClockedDevices() % list() >> Print()


long_rest = Rest(4/1)
long_element = Element(4/1)

long_rest % Length() % float() >> Print()
long_element % Length() % float() >> Print()

long_rest >> P
time.sleep(0.5)
long_element >> P

half_measure_element = Element(1/2)
time.sleep(0.5)
half_measure_element >> P


settings -= D_Digitakt.device
settings % Devices() % list() >> Print()


settings << ClockedDevices()
AllNotesOff() >> Pv >> Export("json/_Export_all_notes_off.json")
