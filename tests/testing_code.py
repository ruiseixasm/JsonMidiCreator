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
#     def __add__(self, other):
#         return Length(
#                 self._measures + other._measures,
#                 self._beats + other._beats,
#                 self._note + other._note,
#                 self._steps + other._steps
#             )
    

# class Duration(Length):
    
#     def __init__(self, measures: float = 0, beats: float = 0, note: float = 1/4, steps: float = 0):
#         super().__init__(measures, beats, note, steps)
    
#     # adding two durations 
#     def __add__(self, other: Length) -> 'Duration':
#         return self + other
    

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


# print(12 / 5)
# print(12 // 5)

# print(-12 / 5)
# print(-12 // 5)

number = 1234567890.123456789
print(f"{number:.16f}")  # This prints the number with 16 decimal places
number = 1234567890.123456789
print("{:.16f}".format(number))  # This prints the number with 16 decimal places
number = 1234567890.123456789
print("{:.20f}".format(number))  # This prints the number with up to 20 decimal places
number = 1234567890.123456789
print(repr(number))  # This prints the number with full precision
number = 1234567890.123456789
print(f"{number:.16f}")  # Example with f-string

# 64-bit (Double Precision): Safe to round to 15 decimal places.
# 32-bit (Single Precision): Safe to round to 7 decimal places.

numbers = [1/10, 2/3, 5/3, 2/3]

for number in numbers:
    print("---------------------")
    print(number)
    print("{:.25f}".format(number))
    print(round(number, 18))
    print(round(number, 15))
    print(round(number, 12))
    print("---------------------")

from fractions import Fraction

print("-------FRACTIONS---------")
for number in numbers:
    print(Fraction(number))
    print(Fraction(round(number, 12)))
    print(Fraction(number).limit_denominator())
    print()

print(Fraction(2/3).limit_denominator())
print(Fraction("2/3").limit_denominator())
print(Fraction("1.5").limit_denominator())
print(round(Fraction("1.5").limit_denominator()))
print(round(Fraction("2/3").limit_denominator()))

long_fraction = Fraction(2/3)
print(float(long_fraction))
print(round(float(long_fraction), 3))

# Creating Fraction objects
f1 = Fraction(1, 2)  # Represents 1/2
f2 = Fraction(3, 4)  # Represents 3/4

# Arithmetic operations
sum_fractions = f1 + f2  # Adds the fractions (1/2 + 3/4)
sub_fractions = f1 - f2  # Subtracts the fractions (1/2 - 3/4)
mul_fractions = f1 * f2  # Multiplies the fractions (1/2 * 3/4)
div_fractions = f1 / f2  # Divides the fractions (1/2 / 3/4)

# Output results
print(f"Sum: {sum_fractions}")       # Output: Sum: 5/4
print(f"Difference: {sub_fractions}") # Output: Difference: -1/4
print(f"Product: {mul_fractions}")    # Output: Product: 3/8
print(f"Division: {div_fractions}")   # Output: Division: 2/3

# Creating Fraction from float
f3 = Fraction(0.5)  # Represents 1/2
print(f"Fraction from float: {f3}")  # Output: Fraction from float: 1/2

# Creating Fraction from string
f4 = Fraction('1.25')  # Represents 5/4
print(f"Fraction from string: {f4}")  # Output: Fraction from string: 5/4

time_ms_1 = 60 * 1000 / Fraction(120.0).limit_denominator() * Fraction(1.0).limit_denominator()
time_ms_2 = Fraction(1.0).limit_denominator() / Fraction(120.0).limit_denominator() * 60 * 1000
time_ms_3 = Fraction(time_ms_2).limit_denominator()

print(time_ms_1)
print(time_ms_2)
print(time_ms_3)
