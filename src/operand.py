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
from typing import TypeVar, TYPE_CHECKING
from fractions import Fraction

if TYPE_CHECKING:
    from operand import Operand  # Replace with the actual module name

T = TypeVar('T', bound='Operand')  # T represents any subclass of Operand


class Operand:
    def __init__(self):
        self._next_operand: Operand = None
        self._initiated: bool   = False
        self._set: bool = False # Intended to be used by Frame subclasses to flag set Operands
        self._index: int = 0

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

    def __mod__(self, operand: 'Operand') -> 'Operand':
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
        import operand_time as ot
        import operand_rational as ra
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case od.Playlist():
                position = operand % ot.Position()
                if position: return self.getPlaylist(position)
                return self.getPlaylist()
            case od.Serialization():
                return self.getSerialization()
            case ol.Len():
                return self.len()
            case ol.Name():
                return self.name()
            case ra.Index():
                return ra.Index(self._index)
            case self.__class__():  return self.copy()
            case _:                 return ol.Null()

    def __eq__(self, operand: 'Operand') -> bool:
        return self is operand
    
    def __ne__(self, operand: 'Operand') -> bool:
        if self == operand:
            return False
        return True
    
    def __lt__(self, operand: 'Operand') -> bool:
        return False
    
    def __gt__(self, operand: 'Operand') -> bool:
        return False
    
    def __le__(self, operand: 'Operand') -> bool:
        return self.__eq__(operand) or self.__lt__(operand)
    
    def __ge__(self, operand: 'Operand') -> bool:
        return self.__eq__(operand) or self.__gt__(operand)
    
    def start(self):
        import operand_label as ol
        return ol.Null()

    def end(self):
        import operand_label as ol
        return ol.Null()
    
    def name(self) -> str:
        return self.__class__.__name__

    def getPlaylist(self):
        return []

    def getMidilist(self):
        return []

    def getSerialization(self) -> dict:
        next_operand = self._next_operand
        if isinstance(self._next_operand, Operand):
            next_operand = self._next_operand.getSerialization()
        return { 
            "class": type(self).__name__,
            "parameters": {
                "next_operand": next_operand,
                "initiated":    self._initiated,
                "set":          self._set,
                "index":        self._index
            }
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> 'Operand':
        if type(self) == Operand:   # Means unknown instantiation from random dict class name
            if not isinstance(serialization, dict): # Non serializable data shall be returned as is
                return serialization
            if "class" in serialization and "parameters" in serialization:
                operand_name = serialization["class"]
                operand_class = Operand.find_subclass_by_name(Operand, operand_name)    # Heavy duty call
                if operand_class:
                    operand_instance: Operand = operand_class()
                    if operand_class == Operand:    # avoids infinite recursion
                        if (serialization["class"] == Operand.__name__ and "parameters" in serialization and
                            "next_operand" in serialization["parameters"] and "initiated" in serialization["parameters"] and
                            "set" in serialization["parameters"] and "index" in serialization["parameters"]):
                            operand_instance._next_operand  = Operand().loadSerialization(serialization["parameters"]["next_operand"])
                            operand_instance._initiated     = serialization["parameters"]["initiated"]
                            operand_instance._set           = serialization["parameters"]["set"]
                            operand_instance._index         = serialization["parameters"]["index"]
                        return operand_instance
                    # if isinstance(operand_instance, ol.Label):
                    #     return operand_instance         # avoids infinite recursion
                    return operand_instance.loadSerialization(serialization)
            return None # Unable to recreate any Operand object from serialization !!
        elif isinstance(serialization, dict) and ("class" in serialization and serialization["class"] == self.__class__.__name__ and "parameters" in serialization and
            "next_operand" in serialization["parameters"] and "initiated" in serialization["parameters"] and
            "set" in serialization["parameters"] and "index" in serialization["parameters"]):

            self._next_operand  = Operand().loadSerialization(serialization["parameters"]["next_operand"])
            # self._next_operand  = None
            self._initiated     = serialization["parameters"]["initiated"]
            self._set           = serialization["parameters"]["set"]
            self._index         = serialization["parameters"]["index"]
            return self
        return self
       
    def __lshift__(self, operand: 'Operand') -> 'Operand':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        if isinstance(operand, type(self)):
            self._initiated = operand._initiated
            self._index = operand._index
            self._set = False   # by default a new copy of data unsets the Operand
            # COPY THE SELF OPERANDS RECURSIVELY
            if operand._next_operand is not None:
                self._next_operand = operand._next_operand.copy()
        return self

    def copy(self: T, *parameters) -> T:
        self_copy: T = type(self)() << self
        for single_parameter in parameters: # Safe for Data class
            self_copy << single_parameter
        # !! DON'T DO THIS !!
        # return type(self)() << self << parameters
        return self_copy
    
    def reset(self: T, *parameters) -> T:
        # RESET THE SELF OPERANDS RECURSIVELY
        if self._next_operand is not None:
            self._next_operand.reset()
        self._initiated     = False
        self._set           = False
        self._index         = 0
        return self << parameters
    
    def clear(self: T, *parameters) -> T:
        self._next_operand = None
        return self.reset() << self.__class__() << parameters
    
    @staticmethod
    def find_subclass_by_name(root_class, name: str):
        # Check if the current class matches the name
        if root_class.__name__ == name:
            return root_class
        
        # Recursively search in all subclasses
        for subclass in root_class.__subclasses__():
            found = __class__.find_subclass_by_name(subclass, name)
            if found: return found
        
        # If no matching subclass is found, return None
        return None

    def __ilshift__(self, other):
        return self.__lshift__(other)
    
    # self is the pusher
    def __rshift__(self, operand: T) -> T:
        if isinstance(operand, tuple):
            last_operand = self
            for single_operand in operand:
                if isinstance(single_operand, Operand):
                    last_operand >>= single_operand
            return last_operand
        return operand.__rrshift__(self)

    # operand is the pusher
    def __rrshift__(self, operand: T) -> T:
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

    def __irshift__(self, other):
        # Simply delegate to the __rshift__ method
        return self.__rshift__(other)
    
    def __add__(self, operand: 'Operand') -> 'Operand':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        return self.copy()

    def __radd__(self, operand: 'Operand') -> 'Operand':
        return self.__add__(operand)

    def __iadd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, operand: 'Operand') -> 'Operand':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        return self.copy()

    def __rsub__(self, operand: 'Operand') -> 'Operand':
        return self.__mul__(-1).__add__(operand)

    def __isub__(self, other):
        return self.__sub__(other)
    
    def __mul__(self, operand: 'Operand') -> 'Operand':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        return self.copy()
    
    def __rmul__(self, operand: 'Operand') -> 'Operand':
        return self.__mul__(operand)

    def __imul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self, operand: 'Operand') -> 'Operand':
        operand = self & operand    # Processes the tailed self operands or the Frame operand if any exists
        return self.copy()
    
    def __idiv__(self, other):
        return self.__truediv__(other)
    
    def __floordiv__(self, operand: 'Operand') -> 'Operand':
        return self.copy()

    def __and__(self, operand: 'Operand') -> 'Operand':
        import operand_frame as of
        if isinstance(operand, of.Frame):   # Extracts the Frame operand first
            return self & (operand & self)
        if self._next_operand is not None:
            result = self._next_operand & operand   # Recursively get result from the chain
            # Apply << operation between current next_operand and the result
            return self._next_operand << result     # Ensures << is applied only if more elements in the chain
        return operand  # Return operand if there is no next operand in the chain
    
    def __iand__(self, other):
        return self.__and__(other)
    
    def __or__(self, operand: 'Operand') -> 'Operand':
        return operand.__ror__(self)

    def __ror__(self, operand: 'Operand') -> 'Operand':
        return self
    
    def __xor__(self, operand: 'Operand') -> 'Operand':
        self & operand  # Processes the tailed self operands or the Frame operand if any exists
        return self

    @staticmethod
    def serialize(data: any) -> any:
        match data:
            case Operand():
                return data.getSerialization()
            case list():
                serialization_list: list[any] = []
                for single_data in data:
                    serialization_list.append(__class__.serialize(single_data))
                return serialization_list
            case tuple():
                serialization_list: list = __class__.serialize(list(data))
                return tuple(serialization_list)
            case Fraction():
                return str(data)
            case _:
                return data

    @staticmethod
    def deserialize(data: any) -> any:
        match data:
            case dict():
                return Operand().loadSerialization(data)
            case Operand():
                return data
            case list():
                data_list: list[any] = []
                for single_data in data:
                    data_list.append(__class__.deserialize(single_data))
                return data_list
            case tuple():
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
    def deep_copy(data: any) -> any:
        match data:
            case Operand():
                return data.copy()
            case list():
                many_data: list[any] = []
                for single_data in data:
                    many_data.append(__class__.deep_copy(single_data))
                return many_data
            case tuple():
                many_data: list = __class__.deep_copy(list(data))
                return tuple(many_data)
            case dict():
                return __class__.deep_copy_dict(data)
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
