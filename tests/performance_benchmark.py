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
import time


def instantiate_classes(iterations: int = 100):
    results_dict: dict = {}
    list_all_classes: list[type] = list_all_operand_classes(Operand)
    for single_class in list_all_classes:
        start_time = time.time()
        for _ in range(iterations):
            single_class()
        results_dict[single_class.__name__] = round((time.time() - start_time) * 1000)
    sorted_results_dict = dict(sorted(results_dict.items(), key=lambda item: item[1], reverse=True))
    print(sorted_results_dict)

def copy_classes(iterations: int = 100):
    results_dict: dict = {}
    list_all_classes: list[type] = list_all_operand_classes(Operand)
    for single_class in list_all_classes:
        class_instantiation: Operand = single_class()
        start_time = time.time()
        for _ in range(iterations):
            class_instantiation.copy()
        results_dict[single_class.__name__] = round((time.time() - start_time) * 1000)
    sorted_results_dict = dict(sorted(results_dict.items(), key=lambda item: item[1], reverse=True))
    print(sorted_results_dict)


print('\nINSTANTIATION PERFORMANCE TEST\n')
instantiate_classes(1000)
print('\nCOPY PERFORMANCE TEST\n')
copy_classes(1000)
