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
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Tuple, Optional, Any, Generic
from typing import Self

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
    from operand_data import Inline


T = TypeVar('T')
TypeNumeral = TypeVar('TypeNumeral', 'Operand', int, float, Fraction)   # TypeNumeral represents any class similar to a number

# GENERIC HANDY FUNCTIONS

def minutes_to_time_ms(minutes: Fraction) -> float:
    # Validation is done by JsonMidiPlayer and midiutil Midi Range Validation
    return round(float(minutes * 60_000), 3)

def time_ms_to_minutes(time_ms: float | int) -> Fraction:
    import operand_rational as ra
    return ra.Minutes(time_ms / 60_000)._rational


#                           C      C#    D      D#    E      F      F#    G      G#    A      A#    B
_black_keys: tuple[bool] = (False, True, False, True, False, False, True, False, True, False, True, False)

def is_black_key(midi_note: int) -> bool:
    """Returns True if the given MIDI note is a black key."""
    return _black_keys[midi_note % 12]

def list_increment(size: int = 4) -> list[int]:
    return [i for i in range(size)]

def list_spread(content: any, size: int) -> list:
    return [Operand.deep_copy(content) for _ in range(size)]

def list_wrap(list_in: list, wrapper: 'Operand') -> list['Operand']:
    return [wrapper.copy(value) for value in list_in]


def list_mod(list_in: list, mod: any = 2) -> list:
    return [item % mod for item in list_in]

def list_floor(list_in: list, floor: any = 12) -> list:
    return [item // floor for item in list_in]

def list_add(list_in: list, add: any = 0) -> list:
    return [item + add for item in list_in]

def list_sub(list_in: list, sub: any = 0) -> list:
    return [item - sub for item in list_in]

def list_mul(list_in: list, mul: any = 1) -> list:
    return [item * mul for item in list_in]

def list_div(list_in: list, div: any = 1) -> list:
    return [item / div for item in list_in]

def list_max(list_in: list, max: any = 15) -> list:
    return [Operand.deep_copy(max) if item > max else Operand.deep_copy(item)
            for item in list_in]

def list_min(list_in: list, min: any = 0) -> list:
    return [Operand.deep_copy(min) if item < min else Operand.deep_copy(item)
            for item in list_in]

def list_int(list_in: list) -> list:
    list_out: list[int] = []
    for number in list_in:
        if isinstance(number, (float, Fraction)):
            list_out.append(int(number))
        elif isinstance(number, Operand):
            list_out.append(number % int())
        else:   # Must be an integer
            list_out.append(number)
    return list_out

def list_float(list_in: list) -> list:
    list_out: list[float] = []
    for number in list_in:
        if isinstance(number, (int, Fraction)):
            list_out.append(float(number))
        elif isinstance(number, Operand):
            list_out.append(number % float())
        else:   # Must be a float
            list_out.append(number)
    return list_out

def list_round(list_in: list, ndigits: int = 0) -> list:
    list_out: list[float] = []
    for number in list_in:
        if isinstance(number, (int, float, Fraction)):
            list_out.append(round(number, ndigits))
        elif isinstance(number, Operand):
            list_out.append(number.copy(round(number % Fraction(), ndigits)))
        else:   # Must be a floatAppends whatever
            list_out.append(number)
    return list_out

def list_swap(list_in: list, left: int, right: int) -> list:
    list_out: list = list_in.copy() # Shallow copy
    if list_in:
        list_len: int = len(list_in)
        list_out[left % list_len] = list_in[right % list_len]
        list_out[right % list_len] = list_in[left % list_len]
    return list_out

def list_repeat(items: list, repeats: list[int]) -> list:
    list_out: list = []
    if len(items) > len(repeats):
        repeats += [0] * (len(items) - len(repeats))
    elif len(items) < len(repeats):
        repeats = repeats[:len(items) - (len(repeats) - len(items))]
    if len(items) == len(repeats):
        for item, repeat in zip(items, repeats):
            list_out.extend([item] * repeat)
    return list_out

def list_choose(items: list, indexes: list[int]) -> list:
    list_out: list = []
    total_items: int = len(items)
    for single_index in indexes:
        list_out.append(Operand.deep_copy(items[single_index % total_items]))
    return list_out

def list_pick(items: list, indexes: list[int]) -> list:
    list_out: list = []
    available_items: list = Operand.deep_copy(items)
    total_items: int = len(items)
    for picked_items, single_index in enumerate(indexes):
        remaining_items: int = total_items - picked_items
        if remaining_items > 0:
            pick_index: int = single_index % remaining_items
            list_out.append( available_items.pop(pick_index) )
        else:
            break
    return list_out

def list_deplete(items: list, amount: list[int], indexes: list[int]) -> list:
    list_out: list = []
    available_items: list = Operand.deep_copy(items)
    available_amounts: list = Operand.deep_copy(amount)
    for single_index in indexes:
        if available_items and available_amounts:
            if available_amounts[single_index % len(available_amounts)] > 1:
                available_amounts[single_index % len(available_amounts)] -= 1
                list_out.append( available_items[single_index % len(available_items)] )
            elif available_amounts[single_index % len(available_amounts)] == 1:
                available_amounts.pop(single_index % len(available_amounts))
                list_out.append( available_items.pop(single_index % len(available_items)) )
            else:
                available_amounts.pop(single_index % len(available_amounts))
                available_items.pop(single_index % len(available_items))
        else:
            break
    return list_out


def list_trim(items: list, at: any) -> list:
    list_out: list = []
    total_items: int = len(items)
    if total_items > 0 and at > 0:
        next_position: any = items[0] * 0
        for item_index in range(total_items):
            list_out.append(Operand.deep_copy(items[item_index]))
            next_position += list_out[item_index]
            if not next_position < at:
                list_out[item_index] -= next_position - at
                break
    return list_out

def list_extend(items: list, to: any) -> list:
    list_out: list = Operand.deep_copy(items)
    total_items: int = len(items)
    if total_items > 0 and to > 0:
        total_extent: any = items[0] * 0
        for item_index in range(total_items):
            total_extent += items[item_index]
        if total_extent < to:
            list_out[-1] += to - total_extent
    return list_out

def list_snap(items: list, on: any) -> list:
    list_out: list = list_trim(items, on)
    list_out = list_extend(list_out, on)
    return list_out

def list_rotate(items: list, left: int = 1) -> list:
    """Rotate list left by given number of positions (positive for left, negative for right)."""
    if not items:  # Handle empty list case
        return []
    left %= len(items)  # Normalize rotation amount
    return items[left:] + items[:left]

def list_get(operands: list['Operand'], parameters: any) -> list:
    list_parameters: list = []
    if isinstance(parameters, list):
        total_parameters: int = len(parameters)
        for index, single_operand in enumerate(operands):
            list_parameters.append(single_operand % parameters[index % total_parameters])
    else:
        for single_operand in operands:
            list_parameters.append(single_operand % parameters)
    return list_parameters

def list_set(operands: list['Operand'], parameters: any) -> list:
    list_set_operands: list = Operand.deep_copy(operands)
    if isinstance(parameters, list):
        total_parameters: int = len(parameters)
        for index, single_operand in enumerate(list_set_operands):
            single_operand << parameters[index % total_parameters]
    else:
        for single_operand in list_set_operands:
            single_operand << parameters
    return list_set_operands

def list_range(range_in: range) -> list:
    return list(range_in)


def string_to_list(pattern: str = "1... 1... 1... 1...") -> list[int]:
    return [1 if char == '1' else 0 for char in pattern if char == '.' or char == '1']

def list_to_string(places: list[int] = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]) -> str:
    pattern: str = ""
    for index, value in enumerate(places):
        if index > 0 and index % 4 == 0:
            pattern += ' '
        if value == 1:
            pattern += '1'
        else:
            pattern += '.'
    return pattern


def list_and(left: list[int], right: list[int]) -> list[int]:
    """Element-wise binary AND of two lists. Pads with 0s if lengths differ."""
    max_len = max(len(left), len(right))
    left_padded = left + [0] * (max_len - len(left))
    right_padded = right + [0] * (max_len - len(right))
    return [a & b for a, b in zip(left_padded, right_padded)]


def list_or(left: list[int], right: list[int]) -> list[int]:
    """Element-wise binary OR of two lists. Pads with 0s if lengths differ."""
    max_len = max(len(left), len(right))
    left_padded = left + [0] * (max_len - len(left))
    right_padded = right + [0] * (max_len - len(right))
    return [a | b for a, b in zip(left_padded, right_padded)]


def list_xor(left: list[int], right: list[int]) -> list[int]:
    """Element-wise binary XOR of two lists. Pads with 0s if lengths differ."""
    max_len = max(len(left), len(right))
    left_padded = left + [0] * (max_len - len(left))
    right_padded = right + [0] * (max_len - len(right))
    return [a ^ b for a, b in zip(left_padded, right_padded)]


def list_nor(left: list[int], right: list[int]) -> list[int]:
    """Element-wise binary NOR (NOT OR). Returns 1 only if both inputs are 0."""
    max_len = max(len(left), len(right))
    left_padded = left + [0] * (max_len - len(left))
    right_padded = right + [0] * (max_len - len(right))
    return [0 if a == 1 or b == 1 else 1 for a, b in zip(left_padded, right_padded)]


def list_not(left: list[int]) -> list[int]:
    """Element-wise binary NOT. Converts 1→0 and 0→1."""
    return [0 if a == 1 else 1 for a in left]  # Or: [1 - a for a in left]


def list_lshift(left: list[int], shift: int) -> list[int]:
    """Element-wise binary `<<`. Converts 01→10."""
    shift = max(min(shift, len(left)), 0)
    return left[shift:] + [0] * shift


def list_rshift(left: list[int], shift: int) -> list[int]:
    """Element-wise binary `>>`. Converts 10→01."""
    shift = max(min(shift, len(left)), 0)
    return [0] * shift + left[:shift]


def string_and(left: str, right: str) -> str:
    """Element-wise binary AND of two strings. Pads with 0s if lengths differ."""
    left_list: list[int] = string_to_list(left)
    right_list: list[int] = string_to_list(right)
    return list_to_string(list_and(left_list, right_list))


def string_or(left: str, right: str) -> str:
    """Element-wise binary OR of two strings. Pads with 0s if lengths differ."""
    left_list: list[int] = string_to_list(left)
    right_list: list[int] = string_to_list(right)
    return list_to_string(list_or(left_list, right_list))


def string_xor(left: str, right: str) -> str:
    """Element-wise binary XOR of two strings. Pads with 0s if lengths differ."""
    left_list: list[int] = string_to_list(left)
    right_list: list[int] = string_to_list(right)
    return list_to_string(list_xor(left_list, right_list))


def string_nor(left: str, right: str) -> str:
    """Element-wise binary NOR of two strings. Pads with 0s if lengths differ."""
    left_list: list[int] = string_to_list(left)
    right_list: list[int] = string_to_list(right)
    return list_to_string(list_nor(left_list, right_list))


def string_not(left: str) -> str:
    """Element-wise binary NOT of two strings. Pads with 0s if lengths differ."""
    left_list: list[int] = string_to_list(left)
    return list_to_string(list_not(left_list))


def string_lshift(left: str, shift: int) -> str:
    """Element-wise binary `<<`. Converts 01→10."""
    left_list: list[int] = string_to_list(left)
    return list_to_string(list_lshift(left_list, shift))


def string_rshift(left: str, shift: int) -> str:
    """Element-wise binary `>>`. Converts 10→01."""
    left_list: list[int] = string_to_list(left)
    return list_to_string(list_rshift(left_list, shift))



# GLOBAL FUNCTIONS

@cache  # Important decorator to avoid repeated searches (class names are static, never change)
def find_class_by_name(root_class: type, name: str) -> type:
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


def playlist_index(playlist: list[dict], index: int) -> dict:
    for single_dict in playlist:
        if "time_ms" in single_dict:
            if index == 0:
                return single_dict
            index -= 1
    return {"time_ms": 0}


def playlist_time_ms(playlist: list[dict]) -> list[dict]:
    return [
        single_dict for single_dict in playlist
        if "time_ms" in single_dict
    ]


# GLOBAL CLASSES

class Operand:
    """`Operand`

    Operand is the root of all other classes, this is why it's omitted in the documented hierarchy
    given it's omnipresence. Operand has no self parameters despite keeping some state variables.
    It is possible to chain multiple operands with the operator `**` that result in operands being
    processed from right to left as if the left ones were wrapped by the right ones.

    Parameters
    ----------
    None : It has no parameters.
    """
    def __init__(self, *parameters):
        self._next_operand: Operand | None = None
        self._initiated: bool   = False
        self._set: bool = False # Intended to be used by Frame subclasses to flag set Operands
        self._index: int = 0
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

    
    def inline(self) -> 'Inline':
        """
        Temporary disables the `Operand` implicit copy by wrapping it in an `Inline` operand.
        """
        import operand_data as od
        return od.Inline(self)

    def len(self) -> int:
        list_size = 0
        for _ in self:
            list_size += 1
        return list_size

    def get(self, operand: T) -> T:
        """Applies `% operand` returning the same type operand"""
        return self.__mod__(operand)

    def access(self, operand: T) -> T:
        """Applies `% Pipe(operand)` returning the same the operand directly"""
        import operand_data as od
        return self.__mod__(od.Pipe(operand))

    def __mod__(self, operand: T) -> T:
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
            case od.Pipe():
                return self.__mod__( operand % Operand() )
            case od.Playlist():
                return od.Playlist() << od.Pipe( self.getPlaylist() )
            case od.Serialization():
                return od.Serialization(self)
            case ra.Index():
                return ra.Index(self._index)
            case tuple():
                results: list = []
                for single_parameter in operand:
                    if isinstance(single_parameter, tuple):
                        chained_results = self
                        for chained_parameter in single_parameter:
                            chained_results %= chained_parameter
                        results.append( chained_results )
                    else:
                        results.append( self % single_parameter )
                return tuple( results )
            case dict():
                serialization: dict = self.getSerialization()
                if len(operand) > 0:
                    return get_pair_key_data(operand, serialization)
                return serialization
            case _:
                return ol.Null()    # Has no equivalent parameter

    # Makes sure no Non Operand has `% Operand` applied
    def __rmod__(self, operand: any) -> Self:
        import operand_label as ol
        return ol.Null()


    # & and | will not do a copy
    def __and__(self, operand: Any) -> Self:
        return self.__iadd__(operand)

    def __or__(self, operand: Any) -> Self:
        return self.__itruediv__(operand)


    def __eq__(self, other: any) -> bool:
        import operand_label as ol
        import operand_data as od
        if other.__class__ == Operand:
            return True
        match other:
            case self.__class__():
                return True
            case ol.Null():
                return False
            case ol.NotNull():
                return True
            case od.Conditional():
                return other == self
        return self % other == other
    
    def __ne__(self, other: any) -> bool:
        return not self == other
    
    def __lt__(self, other: any) -> bool:
        return True     # By default tells any sorting method that is already sorted
    
    def __gt__(self, other: any) -> bool:
        return False    # By default tells any sorting method that is already sorted
    
    def __le__(self, other: any) -> bool:
        return self.__eq__(other) or self.__lt__(other)
    
    def __ge__(self, other: any) -> bool:
        return self.__eq__(other) or self.__gt__(other)
    
    def start(self):
        import operand_label as ol
        return ol.Null()

    def finish(self):
        import operand_label as ol
        return ol.Null()
    
    def name(self) -> str:
        return self.__class__.__name__

    def getPlaylist(self, position_beats: Fraction = Fraction(0)) -> list[dict]:
        return []

    def getMidilist(self, midi_track = None, position_beats: Fraction = Fraction(0)) -> list[dict]:
        return []

    def getSerialization(self) -> dict:
        next_operand = self._next_operand
        if isinstance(self._next_operand, Operand):
            next_operand = self._next_operand.getSerialization()
        return { 
            "class": type(self).__name__,
            "parameters": {},
            "next_operand": next_operand
        }

    # CHAINABLE OPERATIONS

    def loadSerialization(self, serialization: dict) -> Self:
        if "next_operand" in serialization:
            self._next_operand = self.deserialize(serialization["next_operand"])
        return self
       
    def set(self, operand: any) -> Self:
        """Applies `<<` on the operand while keeping self"""
        return self.__lshift__(operand)

    def __lshift__(self, operand: any) -> Self:
        import operand_label as ol
        import operand_data as od
        match operand:
            case od.Serialization():
                self.loadSerialization( operand.getSerialization() )
            case ol.Null():
                return self
            case Operand():
                self._initiated = operand._initiated
                self._index = operand._index
                self._set = False   # by default a new copy of data unsets the Operand
                # COPY THE SELF OPERANDS RECURSIVELY
                self._next_operand = self.deep_copy(operand._next_operand)
            case tuple():
                for single_parameter in operand:
                    self.__lshift__(single_parameter)
        return self
    
    def left(self, operand: any) -> Self:
        """Applies `<<=` on the operand while keeping self"""
        return self.__ilshift__(operand)

    def __ilshift__(self, operand: any) -> Self:
        import operand_data as od
        return self << od.Pipe( operand )
    
    # Makes sure no Non Operand has `<< Operand` applied
    def __rlshift__(self, operand: T) -> T:
        return operand


    def __invert__(self) -> Self:
        '''Same as ~operand will return a copy of operand'''
        return self.copy()

    def copy(self, *parameters) -> Self:
        self_copy = type(self)() << self
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG and not self_copy == self:   # CONSUMES TOO MUCH RESOURCES !!
            logging.error(f"Copied object {self.__class__.__name__} not identical!")
        for single_parameter in parameters: # Safe for Data class
            self_copy << single_parameter
        # !! DON'T DO THIS !!
        # return type(self)() << self << parameters
        return self_copy
    
    def reset(self, *parameters) -> Self:
        # RESET THE SELF OPERANDS RECURSIVELY
        if self._next_operand is not None:
            self << self._next_operand.reset()
        self._initiated     = False
        self._set           = False
        self._index         = 0
        return self << parameters
    
    def clear(self, *parameters) -> Self:
        self._next_operand = None
        return self.reset() << self.__class__() << parameters
    
    # self is the pusher
    def __rshift__(self, operand: any) -> Self:
        return self.copy().__irshift__(operand)

    def right(self, operand: any) -> Self:
        """Applies `>>=` on the operand while keeping self"""
        return self.__irshift__(operand)

    # self is the pusher
    def __irshift__(self, operand: any) -> Self:
        if isinstance(operand, tuple):
            last_operand = self
            for single_operand in operand:
                last_operand >>= single_operand
            return last_operand
        return operand.__rrshift__(self)    # Reverses papers

    # The @ operator in Python is used for matrix multiplication
    # Works as >> with top precedence than >>
    def __matmul__(self, operand) -> Self:
        return self.__rshift__( operand )
    
    
    # operand is the pusher
    def __rrshift__(self, operand: T) -> T:
        operand_copy = Operand.deep_copy(operand)
        return self.__irrshift__(operand_copy)

    def __irrshift__(self, operand: T) -> T:
        if isinstance(operand, tuple):
            for single_operand in operand:
                self.__irrshift__(single_operand)
        return operand


    def __add__(self, operand: any) -> Self:
        return self.copy().__iadd__(operand)
    
    def __sub__(self, operand: any) -> Self:
        return self.copy().__isub__(operand)
    
    def __mul__(self, operand: any) -> Self:
        return self.copy().__imul__(operand)
    
    def __truediv__(self, operand: any) -> Self:
        return self.copy().__itruediv__(operand)
    
    def __floordiv__(self, operand: any) -> Self:
        return self.copy().__ifloordiv__(operand)
    
    # Makes sure no Non Operand has `// Operand` applied
    def __rfloordiv__(self, operand: any) -> Self:
        import operand_label as ol
        return ol.Null()

    # Single word callers

    def add(self, operand: any) -> Self:
        """Applies `+=` with the operand while keeping self"""
        return self.__iadd__(operand)

    def sub(self, operand: any) -> Self:
        """Applies `-=` with the operand while keeping self"""
        return self.__isub__(operand)

    def mul(self, operand: any) -> Self:
        """Applies `*=` with the operand while keeping self"""
        return self.__imul__(operand)

    def div(self, operand: any) -> Self:
        """Applies `/=` with the operand while keeping self"""
        return self.__itruediv__(operand)

    def floordiv(self, operand: any) -> Self:
        """Applies `//=` with the operand while keeping self"""
        return self.__ifloordiv__(operand)


    def __iadd__(self, operand: any) -> Self:
        return self
    
    def __isub__(self, operand: any) -> Self:
        return self

    def __imul__(self, operand: any) -> Self:
        return self
    
    def __itruediv__(self, operand: any) -> Self:
        return self
    
    def __ifloordiv__(self, operand: any) -> Self:
        return self
    

    # Makes sure no Non Operand has `+= Operand` applied
    def __riadd__(self, operand: T) -> T:
        return operand

    # Makes sure no Non Operand has `-= Operand` applied
    def __risub__(self, operand: T) -> T:
        return operand

    # Makes sure no Non Operand has `*= Operand` applied
    def __rimul__(self, operand: T) -> T:
        return operand

    # Makes sure no Non Operand has `/= Operand` applied
    def __ritruediv__(self, operand: T) -> T:
        return operand

    # Makes sure no Non Operand has `//= Operand` applied
    def __rifloordiv__(self, operand: T) -> T:
        return operand

    
    def __pow__(self, operand: 'Operand') -> Self:
        '''
        This operator ** tags another Operand to self that will be the target of the << operation and \
            be passed to self afterwards in a chained fashion.
        '''
        if isinstance(operand, Operand) or operand is None:
            if isinstance(operand, Operand):
                self << operand
            self._next_operand = operand
        return self
    

    def _tail_wrap(self, source: T) -> T:
        """
        While doing a `<<` on self, this wraps the inputted source with the tailed parameters \
            set with `**` operator and returns the result.

        This excludes the classes `Frame`, `Chaos` and `Tamer` that have their own means of \
            processing tailed parameters.
        """
        if isinstance(self._next_operand, Operand):
            # Recursively get result from the tail chain
            next_result = self._next_operand._tail_wrap(source)
            # Apply << operation between current next_operand and the result
            return self._next_operand << next_result     
        return source  # Return source if there is no next operand in the chain


    # STATIC METHODS
    # @staticmethod decorator is needed in order to be possible to call it with self !!

    @staticmethod
    def convert_to_int(number: any) -> int:
        import operand_unit as ou
        import operand_rational as ra
        match number:
            case int():         return number
            case float():       return int(number)
            case Fraction():    return int(number)
            case ou.Unit():     return number._unit
            case ra.Rational(): return int(number._rational)
            case _:             return 0

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
                if "class" in data and "parameters" in data and "next_operand" in data:

                    operand_name = data["class"]
                    operand_class: type[Operand] = find_class_by_name(Operand, operand_name)   # Heavy duty call
                    if operand_class:
                        # Now able to load from the Operand perspective
                        return operand_class().loadSerialization(data)
                    elif logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
                        logging.warning("Find class didn't found any class!")
                    return None
                
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
    def deep_copy(data: T) -> T:
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
