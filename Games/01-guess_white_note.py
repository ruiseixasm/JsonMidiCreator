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
import sys
import os
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from JsonMidiCreator import *
# import random  
from random import randrange 


choices = ("C", "D", "E", "F", "G", "A", "B")
elements = (
    Note(1/1, choices[0]),
    Note(1/1, choices[1]),
    Note(1/1, choices[2]),
    Note(1/1, choices[3]),
    Note(1/1, choices[4]),
    Note(1/1, choices[5]),
    Note(1/1, choices[6])
)

def print_menu():
    for choice_i, choice in enumerate(choices):
        print(f"{choice_i + 1} - {choice}", end=" | ")
    print(f"r to repeat | q to quit")

def press_enter():
    print("Press ENTER to try again.")
    return input()

user_choice = ""
while user_choice != 'q':
    if user_choice != 'r':
        right_choice_int = randrange(len(choices))
    elements[right_choice_int] >> Play()
    print_menu()
    user_choice = input()
    if user_choice == 'r' or user_choice == 'q':
        continue
    elif user_choice == str(right_choice_int + 1):
        print(f"You guess it!")
    else:
        print(f"Wrong, it's \"{choices[right_choice_int]}\"! Better luck next time...")
    user_choice = press_enter()
