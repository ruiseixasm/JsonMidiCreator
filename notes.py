
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


print (1 % 12)
print (-1 % 12)