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
# https://www.geeksforgeeks.org/operator-overloading-in-python/

# Python magic methods or special functions for operator overloading
# Binary Operators:
# Operator	Magic Method
# +	__add__(self, other)
# –	__sub__(self, other)
# *	__mul__(self, other)
# /	__truediv__(self, other)
# //	__floordiv__(self, other)
# %	__mod__(self, other)
# **	__pow__(self, other)
# >>	__rshift__(self, other)
# <<	__lshift__(self, other)
# &	__and__(self, other)
# |	__or__(self, other)
# ^	__xor__(self, other)
# Comparison Operators:
# Operator	Magic Method
# <	__lt__(self, other)
# >	__gt__(self, other)
# <=	__le__(self, other)
# >=	__ge__(self, other)
# ==	__eq__(self, other)
# !=	__ne__(self, other)
# Assignment Operators:

# Operator	Magic Method
# -=	__isub__(self, other)
# +=	__iadd__(self, other)
# *=	__imul__(self, other)
# /=	__idiv__(self, other)
# //=	__ifloordiv__(self, other)
# %=	__imod__(self, other)
# **=	__ipow__(self, other)
# >>=	__irshift__(self, other)
# <<=	__ilshift__(self, other)
# &=	__iand__(self, other)
# |=	__ior__(self, other)
# ^=	__ixor__(self, other)
# Unary Operators:

# Operator	Magic Method
# –	__neg__(self)
# +	__pos__(self)
# ~	__invert__(self)
# Note: It is not possible to change the number of operands of an operator. For example: If we can not overload a unary operator as a binary operator. The following code will throw a syntax error.


# class Length:
    
#     def __init__(self, measures: float = 1, beats: float = 0, note: float = 0, steps: float = 0):
#         self._measures = measures
#         self._beats = beats
#         self._note = note
#         self._steps = steps


#     # adding two lengths 
#     def __add__(self, other_length):
#         return Length(
#                 self._measures + other_length._measures,
#                 self._beats + other_length._beats,
#                 self._note + other_length._note,
#                 self._steps + other_length._steps
#             )
    

# class Duration(Length):
    
#     def __init__(self, measures: float = 0, beats: float = 0, note: float = 1/4, steps: float = 0):
#         super().__init__(measures, beats, note, steps)
    
#     # adding two durations 
#     def __add__(self, other_length: Length) -> 'Duration':
#         return self + other_length
    

# class Position:
#     pass

# class Duration:
#     pass

# class Velocity:
#     pass

# # Example list of note operands
# trigger_note = [Position(), Duration(), Velocity()]

# # Initialize variables
# on_position = None
# with_duration = None
# with_velocity = None

# # Match and assign
# for note_operand in trigger_note:
#     match note_operand:
#         case Position():
#             on_position = note_operand
#         case Duration():
#             with_duration = note_operand
#         case Velocity():
#             with_velocity = note_operand

# # Print results
# print(f"on_position: {on_position}")
# print(f"with_duration: {with_duration}")
# print(f"with_velocity: {with_velocity}")


# print (1 % 12)
# print (-1 % 12)


# class Element:
#     # Your Element class definition here
#     pass

# class ChildElement(Element):
#     # Your ChildElement class definition here
#     pass

# class Sequence:
#     def __init__(self):
#         self._multi_elements = []

#     def add_elements(self, single_element):
#         match single_element:
#             case Element():
#                 self._multi_elements.append(single_element)
#             case [Element()]:
#                 self._multi_elements.extend(single_element) # Using extend to add multiple elements from the list
#             case _:
#                 raise ValueError("Unsupported type provided")

# # Example usage:
# multi_elements = Sequence()

# # Assuming you have some Element instances
# elem1 = Element()
# child_elem1 = ChildElement()
# child_elem2 = ChildElement()

# # Adding a single Element
# multi_elements.add_elements(elem1)

# # Adding a single ChildElement (child of Element)
# multi_elements.add_elements(child_elem1)

# # Adding a list of ChildElements
# multi_elements.add_elements([child_elem2])

# # Adding a mixed list of Elements and ChildElements
# multi_elements.add_elements([elem1, child_elem1, child_elem2])

# print(multi_elements._multi_elements)

# class Element:
#     def __init__(self, name="Element"):
#         self.name = name
    
#     def __repr__(self):
#         return f"{self.name}"

# class ChildElement(Element):
#     def __init__(self, name="ChildElement"):
#         super().__init__(name)

# class Sequence:
#     def __init__(self):
#         self._multi_elements = []

#     def add_elements(self, single_element):
#         if isinstance(single_element, Element):
#             self._multi_elements.append(single_element)
#         elif isinstance(single_element, list) and all(isinstance(elem, Element) for elem in single_element):
#             self._multi_elements.extend(single_element)
#         else:
#             raise ValueError(f"Unsupported type provided: {single_element}")

# # Example usage:
# multi_elements = Sequence()

# # Assuming you have some Element instances
# elem1 = Element("Element1")
# child_elem1 = ChildElement("ChildElement1")
# child_elem2 = ChildElement("ChildElement2")

# # Adding a single Element
# multi_elements.add_elements(elem1)

# # Adding a single ChildElement (child of Element)
# multi_elements.add_elements(child_elem1)

# # Adding a list of ChildElements
# multi_elements.add_elements([child_elem2])

# # Adding a mixed list of Elements and ChildElements
# multi_elements.add_elements([elem1, child_elem1, child_elem2])

# print(multi_elements._multi_elements)


# def itsMeasure(operand_type):
#     match operand_type:
#         case Measure():     print("It's a Measure too!")


# class Measure:
#     pass

# class SubMeasure(Measure):
#     pass

# operand = Measure()
# match operand:
#     case Measure():     print("It's a Measure()")

# operand_type = Measure
# match operand_type:
#     case Measure:     print("It's a Measure")

# operand_type = SubMeasure
# match operand_type:
#     case Measure:     print("It's a Measure too!")

# itsMeasure(SubMeasure())

# itsMeasure(SubMeasure)


print(12 / 5)
print(12 // 5)


print(-12 / 5)
print(-12 // 5)

