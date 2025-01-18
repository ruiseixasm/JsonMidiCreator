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
import logging
from functools import cache
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Any
from fractions import Fraction
# Json Midi Creator Libraries
import creator as c

DEBUG = False

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

if TYPE_CHECKING:
    from operand import Operand  # Replace with the actual module name

TypeOperand = TypeVar('TypeOperand', bound='Operand')  # TypeOperand represents any subclass of Operand


# GLOBAL FUNCTIONS

@cache  # Important decorator to avoid repeated searches (class names are static, never change)
def find_class_by_name(root_class: type, name: str):
    """
    Recursively searches for a class with a given name in the hierarchy 
    starting from the root_class.

    Args:
        root_class: The starting class for the search.
        name (str): The name of the class to search for.

    Returns:
        The class if found, otherwise None.
    """
    if not isinstance(root_class, type):
        raise TypeError("root_class must be a class.")

    # Check if the current class matches the name (class NOT an object)
    if root_class.__name__ == name:
        return root_class
    
    # Recursively search in all subclasses (classes NOT objects)
    for subclass in root_class.__subclasses__():
        result = find_class_by_name(subclass, name)
        if result: return result
    
    # If no matching subclass is found, return None
    return None


def list_all_operand_classes(root_class: type, all_classes: list = None) -> list:
    if not all_classes:
        all_classes: list = []
    if not isinstance(root_class, type):
        return all_classes
    
    all_classes.append(root_class)
    # Recursively search in all subclasses (classes NOT objects)
    for subclass in root_class.__subclasses__():
        list_all_operand_classes(subclass, all_classes) # No need to catch the returned list because classes are already being appended    

    return all_classes


def get_root_classes_list(root_class: type) -> list:
    if not isinstance(root_class, type):
        return []   # Empty list
    
    # Recursively fills up (extends) self subclasses list (classes NOT objects)
    root_classes_list: list = [root_class]
    for subclass in root_class.__subclasses__():
        root_classes_list.extend( get_root_classes_list(subclass) )

    return root_classes_list


def found_dict_in_dict(dict_to_find: dict, in_dict: dict) -> bool:
    if isinstance(dict_to_find, dict) and isinstance(in_dict, dict):

        if dict_to_find == in_dict:
            return True
        
        for _, value in in_dict.items():
            result = found_dict_in_dict(dict_to_find, value)
            if result: return True
        
    return False


def get_dict_key_data(dict_key: str, in_dict: dict) -> any:
    if isinstance(dict_key, str) and isinstance(in_dict, dict):

        if dict_key in in_dict:
            return in_dict[dict_key]

        for _, value in in_dict.items():
            key_data = get_dict_key_data(dict_key, value)
            if key_data: return key_data       

    return None


def get_pair_key_data(pair_key: dict, in_dict: dict) -> any:
    if isinstance(pair_key, dict) and len(pair_key) > 0 and isinstance(in_dict, dict):
        # Get the first key-value pair
        first_key, second_key = next(iter(pair_key.items()))

        first_key_data: dict = get_dict_key_data(first_key, in_dict)
        if isinstance(first_key_data, dict):
            return get_dict_key_data(second_key, first_key_data)
        return first_key_data

    return None


def filter_list(items: List[Any], condition: Callable[[Any], bool]) -> List[Any]:
    """
    Removes all items from a list that don't satisfy a given condition.

    Args:
        items (list): The list to filter.
        condition (Callable): A function that takes an element and returns True if it should be kept.

    Returns:
        list: A new list containing only items that satisfy the condition.
    """
    return [item for item in items if condition(item)]


# GLOBAL CLASSES

class Operand:
    def __init__(self, *parameters):
        self._next_operand: Operand = None
        self._initiated: bool   = False
        self._set: bool = False # Intended to be used by Frame subclasses to flag set Operands
        self._index: int = 0
        self._source_operand: Operand = None    # Lets the receiver know where the Operand comes from
        for single_parameter in parameters: # Faster than passing a tuple
            self << single_parameter

    # It has to skip self, contrary to the Frame __next__ that includes the self!!
    def __iter__(self):
        self._current_node: Operand = self._next_operand    # Reset to the start node on new iteration
        return self
    
    # It has to skip self, contrary to the Frame __next__ that includes the self!!
    def __next__(self):
        if self._current_node is None: raise StopIteration
        previous_node = self._current_node
        match self._current_node:
            case Operand(): self._current_node = self._current_node._next_operand
            case _:         self._current_node = None
        return previous_node

    def set_source_operand(self, source_operand: 'Operand' = None) -> 'Operand':
        if isinstance(source_operand, Operand):
            self._source_operand = source_operand
        return self

    def get_source_operand(self) -> 'Operand':
        return self._source_operand

    def reset_source_operand(self) -> 'Operand':
        self._source_operand = None
        return self

    def len(self) -> int:
        list_size = 0
        for _ in self:
            list_size += 1
        return list_size

    def __pow__(self, operand: 'Operand') -> 'Operand':
        match operand:
            case Operand():     self._next_operand = operand
            case _:             self._next_operand = None
        return self

    def __mod__(self, operand: any) -> any:
        """
        The % symbol is used to extract a Parameter, each Operand
        has different types of Parameters, as an example, the
        Operand Note() has the Parameters Velocity and Duration,
        and recursively, the Operands' Parameters themselves.

        Examples
        --------
        >>> given_operand = Note("A") << Duration(1/2)
        >>> print(given_operand % Duration() % NoteValue() % float())
        0.5
        """
        import operand_label as ol
        import operand_frame as of
        import operand_data as od
        import operand_rational as ra
        match operand:
            case od.DataSource():
                return self.__mod__( operand % Operand() )
            case of.Frame():
                return self % (operand % Operand())
            case od.Playlist():
                position = operand % ra.Position()
                if isinstance(position, ra.Position):
                    return self.getPlaylist(position)
                return self.getPlaylist()
            case od.Serialization():
                return self.getSerialization()
            case dict():
                serialization: dict = self.getSerialization()
                if len(operand) > 0:
                    return get_pair_key_data(operand, serialization)
                return serialization
            case od.Len():
                return self.len()
            case od.Name():
                return self.name()
            case ra.Index():
                return ra.Index(self._index)
            case self.__class__():
                return self.copy()
            case _:
                return ol.Null()

    def __floordiv__(self, operand: any) -> any:
        import operand_data as od
        return self.__mod__( od.DataSource( operand ) )

    def __eq__(self, other: 'Operand') -> bool:
        return True # All subclasses are Operands. Useful for Framing
    
    def __ne__(self, other: 'Operand') -> bool:
        if self == other:
            return False
        return True
    
    def __lt__(self, other: 'Operand') -> bool:
        return False
    
    def __gt__(self, other: 'Operand') -> bool:
        return False
    
    def __le__(self, other: 'Operand') -> bool:
        return self.__eq__(other) or self.__lt__(other)
    
    def __ge__(self, other: 'Operand') -> bool:
        return self.__eq__(other) or self.__gt__(other)
    
    def start(self):
        import operand_label as ol
        return ol.Null()

    def finish(self):
        import operand_label as ol
        return ol.Null()
    
    def name(self) -> str:
        return self.__class__.__name__

    def getPlaylist(self, position = None) -> list:
        return []

    def getMidilist(self, midi_track = None, position = None) -> list:
        return []

    def getSerialization(self) -> dict:
        next_operand = self._next_operand
        if isinstance(self._next_operand, Operand):
            next_operand = self._next_operand.getSerialization()
        return { 
            "class": type(self).__name__,
            "parameters": {}
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self: TypeOperand, serialization: dict) -> TypeOperand:
        if type(self) == Operand:   # Means unknown instantiation from random dict class name
            if not isinstance(serialization, dict): # Non serializable data shall be returned as is
                return serialization
            if "class" in serialization and "parameters" in serialization:

                operand_name = serialization["class"]
                operand_class = find_class_by_name(Operand, operand_name)   # Heavy duty call
                if operand_class:
                    operand_instance: Operand = operand_class()
                    if operand_class == Operand:    # avoids infinite recursion
                        return operand_instance
                    
                    return operand_instance.loadSerialization(serialization)
                elif logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
                    logging.warning("Find class didn't found any class!")
            return None # Unable to recreate any Operand object from serialization !!
        
        return self
       
    def __lshift__(self: TypeOperand, operand: any) -> TypeOperand:
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(operand, type(self)):
            self._initiated = operand._initiated
            self._index = operand._index
            self._set = False   # by default a new copy of data unsets the Operand
            # COPY THE SELF OPERANDS RECURSIVELY
            self._next_operand = self.deep_copy(operand._next_operand)
        return self

    def __xor__(self: TypeOperand, operand: any) -> TypeOperand:
        import operand_data as od
        return self.__lshift__( od.DataSource( operand ) )

    def copy(self: TypeOperand, *parameters) -> TypeOperand:
        self_copy: TypeOperand = type(self)() << self
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG and not self_copy == self:   # CONSUMES TOO MUCH RESOURCES !!
            logging.error(f"Copied object {self.__class__.__name__} not identical!")
        for single_parameter in parameters: # Safe for Data class
            self_copy << single_parameter
        # !! DON'T DO THIS !!
        # return type(self)() << self << parameters
        return self_copy
    
    def reset(self: TypeOperand, *parameters) -> TypeOperand:
        # RESET THE SELF OPERANDS RECURSIVELY
        if self._next_operand is not None:
            self._next_operand.reset()
        self._initiated     = False
        self._set           = False
        self._index         = 0
        return self << parameters
    
    def clear(self: TypeOperand, *parameters) -> TypeOperand:
        self._next_operand = None
        return self.reset() << self.__class__() << parameters
    
    def __ilshift__(self: TypeOperand, other) -> TypeOperand:
        return self.__lshift__(other)
    
    # self is the pusher
    def __rshift__(self: TypeOperand, operand) -> TypeOperand:
        if isinstance(operand, tuple):
            last_operand = self
            for single_operand in operand:
                if isinstance(single_operand, Operand):
                    last_operand >>= single_operand
            return last_operand
        return operand.__rrshift__(self)

    # operand is the pusher
    def __rrshift__(self: TypeOperand, operand: any) -> TypeOperand:
        match operand:
            case tuple():
                rshift_operands = None
                for single_operand in operand:
                    if isinstance(single_operand, Operand):
                        if rshift_operands is not None:
                            rshift_operands >>= single_operand
                        else:
                            rshift_operands = single_operand
                return rshift_operands >> self
        return operand

    def __irshift__(self: TypeOperand, operand: any) -> TypeOperand:
        # Simply delegate to the __rshift__ method
        return self.__rshift__(operand)
    

    def __add__(self: TypeOperand, operand: any) -> TypeOperand:
        self_copy: Operand = self.copy()
        return self_copy.__iadd__(operand)
    
    def __iadd__(self: TypeOperand, operand: any) -> TypeOperand:
        return self
    
    def __radd__(self: TypeOperand, operand: any) -> TypeOperand:
        return self.__add__(operand)


    def __sub__(self: TypeOperand, operand: any) -> TypeOperand:
        self_copy: Operand = self.copy()
        return self_copy.__isub__(operand)
    
    def __isub__(self: TypeOperand, operand: any) -> TypeOperand:
        return self

    def __rsub__(self: TypeOperand, operand: any) -> TypeOperand:
        return self.__mul__(-1).__add__(operand)


    def __mul__(self: TypeOperand, operand: any) -> TypeOperand:
        self_copy: Operand = self.copy()
        return self_copy.__imul__(operand)
    
    def __imul__(self: TypeOperand, operand: any) -> TypeOperand:
        return self
    
    def __rmul__(self: TypeOperand, operand: any) -> TypeOperand:
        return self.__mul__(operand)


    def __truediv__(self: TypeOperand, operand: any) -> TypeOperand:
        self_copy: Operand = self.copy()
        return self_copy.__itruediv__(operand)
    
    def __itruediv__(self: TypeOperand, operand: any) -> TypeOperand:
        return self
    
    
    def __and__(self, operand: any) -> any:
        
        import operand_frame as of
        if isinstance(operand, of.Frame):   # Extracts the Frame operand first
            return self & (operand & self)
        if self._next_operand:
            result = self._next_operand & operand   # Recursively get result from the chain
            # Apply << operation between current next_operand and the result
            return self._next_operand << result     # Ensures << is applied only if more elements in the chain
    
        return operand  # Return operand if there is no next operand in the chain
    
    def __iand__(self, other: any) -> any:
        return self.__and__(other)
    
    def __or__(self, operand: any) -> any:
        return operand.__ror__(self)

    def __ror__(self, operand: any) -> any:
        return self
    

    # STATIC METHODS
    # @staticmethod decorator is needed in order to be possible to call it with self !!

    @staticmethod
    def serialize(data: any) -> any:
        match data:
            case Operand():
                return data.getSerialization()
            case dict():
                serialized_dict: dict = {}
                for key, value in data.items():
                    # Recursively copy each serialized value
                    serialized_dict[key] = __class__.serialize(value)
                return serialized_dict
            case list():
                serialized_list: list[any] = []
                for single_data in data:
                    serialized_list.append(__class__.serialize(single_data))
                return serialized_list
            case tuple():
                serialized_list: list = __class__.serialize(list(data))
                return tuple(serialized_list)
            case Fraction():
                return str(data)
            case _:
                return data

    @staticmethod
    def deserialize(data: any) -> any:
        match data:
            case dict():
                if "class" in data and "parameters" in data:
                    return Operand().loadSerialization(data)
                deserialized_dict: dict = {}
                for key, value in data.items(): # Makes sure it processes Operands in dict
                    # Recursively copy each deserialized value
                    deserialized_dict[key] = __class__.deserialize(value)
                return deserialized_dict
            case Operand(): # just a fail safe
                return data
            case list():
                data_list: list[any] = []
                for single_serialization in data:
                    data_list.append(__class__.deserialize(single_serialization))
                return data_list
            case tuple():   # JSON DOESN'T KEEP tuple() DATA TYPE !!!
                data_list: list = __class__.deserialize(list(data))
                return tuple(data_list)
            case str():
                try:
                    return Fraction(data)
                except ValueError:
                    return data
            case _:
                return data

    @staticmethod
    def deep_copy(data: TypeOperand) -> TypeOperand:
        match data:
            case Operand():
                return data.copy() # Only Operand has copy method
            case dict():
                many_dict: dict = {}
                for key, value in data.items():
                    many_dict[key] = __class__.deep_copy(value)
                return many_dict
            case list():
                many_list: list[any] = []
                for single_data in data:
                    many_list.append(__class__.deep_copy(single_data))
                return many_list
            case tuple():
                many_list: list = __class__.deep_copy(list(data))
                return tuple(many_list)
            case _:
                return data

    @staticmethod
    def deep_copy_dict(data: dict) -> dict:
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

    @staticmethod
    def deep_reset(data: any):
        match data:
            case Operand():
                return data.reset() # Only Operand has reset method
            case dict():
                for _, value in data.items():
                    __class__.deep_reset(value)
            case list():
                for single_data in data:
                    __class__.deep_reset(single_data)
            case tuple():
                __class__.deep_reset(list(data))

    @staticmethod
    def deep_clear(data: any):
        match data:
            case Operand():
                return data.clear() # Only Operand has clear method
            case dict():
                for _, value in data.items():
                    __class__.deep_clear(value)
            case list():
                for single_data in data:
                    __class__.deep_clear(single_data)
            case tuple():
                __class__.deep_clear(list(data))
