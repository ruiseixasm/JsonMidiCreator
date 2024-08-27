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

class Obsolete():

    @staticmethod
    def addSequences(left_sequence: dict, right_sequence: dict) -> dict:
        if __class__.isSequence(left_sequence) and __class__.isSequence(right_sequence):
            added_sequence = __class__.copySerialization(left_sequence)
            added_sequence["parameters"]["operands"] += right_sequence["parameters"]["operands"]
            return __class__.copySerialization(added_sequence)
        if __class__.isSequence(left_sequence):
            added_sequence = __class__.copySerialization(left_sequence)
            added_sequence["parameters"]["operands"] += [ right_sequence ]
            return __class__.copySerialization(added_sequence)
        if __class__.isSequence(right_sequence):
            added_sequence = __class__.copySerialization(left_sequence)
            added_sequence["parameters"]["operands"] = [ right_sequence ] + added_sequence["parameters"]["operands"]
            return __class__.copySerialization(added_sequence)
        added_sequence = {
                "class": "Sequence",
                "parameters": {
                    "operands": [left_sequence, right_sequence]
                }
            }
        return __class__.copySerialization(added_sequence)

    @staticmethod
    def isSequence(serialization: dict) -> bool:
        if isinstance(serialization, dict) and "class" in serialization and serialization["class"] == "Sequence":
            return True
        return False

    @staticmethod
    def getStart(serialization: any) -> any:
        min_position: ot.Position = None

        if isinstance(serialization, dict):
            for key, value in serialization.items():
                # Recursively copy each value
                if isinstance(value, dict) and "class" in value and "Position" in value["class"]:
                    # {
                    #     "class": "Position",
                    #     "parameters": {
                    #         "measure": 0.0,
                    #         "beat": 0.0,
                    #         "note_value": 0.0,
                    #         "step": 0.0
                    #     }
                    # }
                    value_position = ot.Position().loadSerialization(value) # It's a leaf value (no children, not a node)
                    if min_position is None or value_position < min_position:
                        min_position = value_position
                else:
                    # Recursively check nested structures
                    nested_min = __class__.getStart(value)
                    if nested_min is not None and (min_position is None or nested_min < min_position):
                        min_position = nested_min

        elif isinstance(serialization, list):
            for element in serialization:
                nested_min = __class__.getStart(element)
                if nested_min is not None and (min_position is None or nested_min < min_position):
                    min_position = nested_min

        return min_position     # Final exit point

    @staticmethod
    def setStart(serialization: any, increase_position: ot.Length) -> any:
        if isinstance(serialization, dict):
            # Create a new dictionary
            copy_dict = {}
            for key, value in serialization.items():
                # Recursively copy each value
                if isinstance(value, dict) and "class" in value and "Position" in value["class"]:
                    # {
                    #     "class": "Position",
                    #     "parameters": {
                    #         "measure": 0.0,
                    #         "beat": 0.0,
                    #         "note_value": 0.0,
                    #         "step": 0.0
                    #     }
                    # }
                    value_position = ot.Position().loadSerialization(value)
                    new_position = value_position + increase_position
                    new_position_dict = new_position.getSerialization()
                    value["parameters"] = new_position_dict["parameters"]

                copy_dict[key] = __class__.setStart(value, increase_position)

            return copy_dict    # Final exit point
        
        elif isinstance(serialization, list):
            # Create a new list and recursively copy each element
            return [__class__.setStart(element, increase_position) for element in serialization]
        else:
            # Base case: return the value directly if it's neither a list nor a dictionary
            return serialization

    @staticmethod
    def copySerialization(serialization: any) -> any:
        if isinstance(serialization, dict):
            # Create a new dictionary
            copy_dict = {}
            for key, value in serialization.items():
                # Recursively copy each value
                copy_dict[key] = __class__.copySerialization(value)

            return copy_dict    # Final exit point
        
        elif isinstance(serialization, list):
            # Create a new list and recursively copy each element
            return [__class__.copySerialization(element) for element in serialization]
        else:
            # Base case: return the value directly if it's neither a list nor a dictionary
            return serialization

    @staticmethod
    def deep_copy_dict(data):
        """
        Recursively creates a deep copy of a dictionary that may contain lists and other dictionaries.

        Args:
            data (dict): The dictionary to copy.

        Returns:
            dict: A deep copy of the original dictionary.
        """
        if isinstance(data, dict):
            # Create a new dictionary
            copy_dict = {}
            for key, value in data.items():
                # Recursively copy each value
                copy_dict[key] = __class__.deep_copy_dict(value)
            return copy_dict
        elif isinstance(data, list):
            # Create a new list and recursively copy each element
            return [__class__.deep_copy_dict(element) for element in data]
        else:
            # Base case: return the value directly if it's neither a list nor a dictionary
            return data
