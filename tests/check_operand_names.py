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


def find_all_subclasses(cls):
    subclasses = set(cls.__subclasses__())
    for subclass in cls.__subclasses__():
        subclasses.update(find_all_subclasses(subclass))
    return subclasses

def find_missing_classes(base_class, class_dict):
    # Get all subclasses of the base class recursively
    all_subclasses = find_all_subclasses(base_class)
    
    # Extract names of the derived classes
    all_class_names = {cls.__name__ for cls in all_subclasses}
    all_class_names.add(base_class.__name__)
    
    # Extract names from the provided dictionary
    dict_class_names = set(class_dict.keys())
    
    # Find classes that are in the derived list but not in the dictionary
    missing_classes = all_class_names - dict_class_names
    
    # Find names in the dictionary that have no corresponding class
    unmatched_names = dict_class_names - all_class_names
    
    return missing_classes, unmatched_names

operand_names = Names()._names

# Check which classes are missing
missing_classes, unmatched_names = find_missing_classes(Operand, operand_names)

if missing_classes:
    print("Missing classes:", missing_classes)
else:
    print("All Operand classes are listed in the dictionary.")

if unmatched_names:
    print("Unmatched names in the dictionary:", unmatched_names)
else:
    print("All class names in the dictionary match existing Operands class names.")
