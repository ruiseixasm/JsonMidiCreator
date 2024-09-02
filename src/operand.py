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

class Operand:
    def __init__(self):
        self._next_operand: Operand = None

    # It has to skip self, contrary to the Frame __next__ that includes the self!!
    def __iter__(self):
        self._current_node: Operand = self._next_operand    # Reset to the start node on new iteration
        return self
    
    # It has to skip self, contrary to the Frame __next__ that includes the self!!
    def __next__(self):
        import operand_label as ol
        if isinstance(self._current_node, ol.Null): raise StopIteration
        previous_node = self._current_node
        match self._current_node:
            case Operand(): self._current_node = self._current_node._next_operand
            case _:         self._current_node = ol.Null()
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
        match operand:
            case of.Frame():        return self % (operand % Operand())
            case ol.Null() | None:  return ol.Null()
            case _:                 return self.copy()

    def __eq__(self, operand: 'Operand') -> bool:
        return False
    
    def __ne__(self, operand: 'Operand') -> bool:
        if self == operand:
            return False
        return True
    
    def __lt__(self, operand: 'Operand') -> bool:
        return False
    
    def __gt__(self, operand: 'Operand') -> bool:
        return False
    
    def __le__(self, operand: 'Operand') -> bool:
        return False
    
    def __ge__(self, operand: 'Operand') -> bool:
        return False
    
    def start(self) -> 'ot.Position':
        import operand_label as ol
        return ol.Null()

    def end(self) -> 'ot.Position':
        import operand_label as ol
        return ol.Null()
    
    def name(self) -> str:
        return self.__class__.__name__

    def getPlayList(self):
        return []

    def getSerialization(self):
        return { 
            "class": self.__class__.__name__,
            "parameters": {}
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict):
        import operand_label as ol
        if isinstance(serialization, dict) and ("class" in serialization and "parameters" in serialization):
            operand_name = serialization["class"]
            operand_class = Operand.find_subclass_by_name(Operand, operand_name)
            if operand_class == __class__: return operand_class()   # avoids infinite recursion
            if operand_class: return operand_class().loadSerialization(serialization)
        return ol.Null()
       
    def copy(self) -> 'Operand':
        return self.__class__() << self
    
    def getOperand(self, operand_name: str) -> 'Operand':
        operand_class = Operand.find_subclass_by_name(Operand, operand_name)
        if operand_class: return operand_class()
        return operand_class
    
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
    
    def __xor__(self, operand: 'Operand') -> any:
        """
        ^ calls the respective Operand's method by name.
        """
        import operand_data as od
        import operand_time as ot
        import operand_label as ol
        match operand:
            case od.PlayList():
                position = operand % ot.Position()
                if position: return self.getPlayList(position)
                return self.getPlayList()
            case od.Serialization():
                return self.getSerialization()
            case ol.Name():
                return self.name()
        return self

    def __lshift__(self, operand: 'Operand') -> 'Operand':
        return self

    # self is the pusher
    def __rshift__(self, operand: 'Operand') -> 'Operand':
        return operand.__rrshift__(self)

    # operand is the pusher
    def __rrshift__(self, operand: 'Operand') -> 'Operand':
        return self

    def __add__(self, operand: 'Operand') -> 'Operand':
        return self.copy()

    def __radd__(self, operand: 'Operand') -> 'Operand':
        return self.__add__(operand)

    def __sub__(self, operand: 'Operand') -> 'Operand':
        return self.copy()

    def __rsub__(self, operand: 'Operand') -> 'Operand':
        return self.__mul__(-1).__add__(operand)

    def __mul__(self, operand: 'Operand') -> 'Operand':
        return self.copy()
    
    def __rmul__(self, operand: 'Operand') -> 'Operand':
        return self.__mul__(operand)

    def __truediv__(self, operand: 'Operand') -> 'Operand':
        return self.copy()
    
    def __floordiv__(self, operand: 'Operand') -> 'Operand':
        return self.copy()

    def __and__(self, operand: 'Operand') -> 'Operand':
        return self

    def __or__(self, operand: 'Operand') -> 'Operand':
        return operand.__ror__(self)

    def __ror__(self, operand: 'Operand') -> 'Operand':
        return self
    
    @staticmethod
    def copy_operands_list(operands_list: list['Operand'] | tuple['Operand']) -> list:
        copy_list: list[Operand] = []
        for single_operand in operands_list:
            if isinstance(single_operand, Operand):
                copy_list.append(single_operand.copy())
        return copy_list
