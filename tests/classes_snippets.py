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


# Global Staff setting up
staff << Tempo(90) << Measures(7)
# Global variable to simulate a key signature (number of sharps or flats)
global_key_signature = 0  # Example: 0 means C Major (no sharps or flats)

class Key:
    """
    A Key is an integer from 0 to 11 that describes the 12 keys of an octave,
    and optionally applies accidentals (sharps, flats) or a natural note.
    
    Parameters
    ----------
    key : integer_like or string_like
        A number from 0 to 11 with 0 as default or the equivalent string key "C".
    accidental: str
        An optional accidental ('sharp', 'flat', or 'natural') that overrides the global key signature.
    natural: bool
        Whether the note should be treated as a natural, unaffected by key signature.
    """

    _keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
             "B#", "Db", "D", "Eb", "Fb", "E#", "Gb", "G", "Ab", "A", "Bb", "Cb"]

    def __init__(self, key: int | str = None, accidental=None, natural=False):
        self._key: int = 0
        self.accidental = accidental  # Can be 'sharp', 'flat', 'natural', or None
        self.natural = natural        # Whether this key is natural (ignores key signature)
        if key is not None:
            match key:
                case str():
                    self._key = self.key_to_int(key)
                case int() | float():
                    self._key = int(key) % 12

    def __mod__(self, operand):
        """Overloads the % operator for extracting the key value."""
        match operand:
            case int():  # Return key as integer
                return self._key
            case str():  # Return key as string
                return self.int_to_key(self._key)
            case _:  # By default, return key as integer
                return self._key

    def __eq__(self, other: any) -> bool:
        return self % int() == other % int()
    
    def __lt__(self, other: any) -> bool:
        return self % int() < other % int()
    
    def __gt__(self, other: any) -> bool:
        return self % int() > other % int()
    
    def __le__(self, other: any) -> bool:
        return self == other or self < other
    
    def __ge__(self, other: any) -> bool:
        return self == other or self > other

    @staticmethod
    def int_to_key(note_key: int = 0) -> str:
        return Key._keys[note_key % 12]

    @staticmethod
    def key_to_int(key: str = "C") -> int:
        for index, value in enumerate(Key._keys):
            if value.lower().find(key.strip().lower()) != -1:
                return index % 12
        return 0

    def apply_accidental(self, note: int):
        """Apply accidental (sharp, flat, or natural) to the key if set."""
        match self.accidental:
            case 'sharp': return (note + 1) % 12
            case 'flat':  return (note - 1) % 12
            case 'natural': return note  # Return as natural, no alteration
            case _: return note  # No accidental, return the original note

    def apply_key_signature(self):
        """Applies the global key signature to the note, unless an accidental or natural is set."""
        global global_key_signature

        # If the note is set to be natural, return without applying key signature
        if self.natural:
            return self.int_to_key(self._key)

        # Apply accidental if explicitly set
        altered_note = self.apply_accidental(self._key)

        # Apply global key signature if no accidental or natural is set
        if not self.accidental:
            if global_key_signature > 0:  # Sharps
                # Modify notes affected by sharp key signatures (e.g., F# in G Major)
                for i in range(global_key_signature):
                    altered_note = self.apply_accidental(altered_note)
            elif global_key_signature < 0:  # Flats
                # Modify notes affected by flat key signatures (e.g., Bb in F Major)
                for i in range(-global_key_signature):
                    altered_note = self.apply_accidental(altered_note)

        return self.int_to_key(altered_note)

    def get_real_key(self):
        """Returns the real note after applying key signature or accidental."""
        return self.apply_key_signature()

    def diatonic_transpose(self, steps: int):
        """Transpose the key diatonically by a number of steps (e.g., C -> G)."""
        scale_degrees = [0, 2, 4, 5, 7, 9, 11]  # Major scale intervals (W-W-H-W-W-W-H)
        key_pos = scale_degrees.index(self._key % 12)
        new_pos = (key_pos + steps) % len(scale_degrees)
        return Key(scale_degrees[new_pos])

    def chromatic_transpose(self, steps: int):
        """Transpose the key chromatically by a number of semitones."""
        return Key((self._key + steps) % 12)

    def __str__(self):
        real_note = self.get_real_key()
        return f"Key: {real_note} (Natural: {self.natural}, Accidental: {self.accidental})"

# Global key signature (1 sharp, G Major)
global_key_signature = 1

# Create a Key with no accidental
c_key = Key("C")
print(c_key.get_real_key())  # Output: C (as affected by the global key signature, if any)

# Create a Key with a sharp accidental
c_sharp_key = Key("C", accidental='sharp')
print(c_sharp_key.get_real_key())  # Output: C# (overrides key signature)

# Create a natural note (ignores key signature)
f_natural = Key("F", natural=True)
print(f_natural.get_real_key())  # Output: F (even if key signature says F#)

# Chromatic transposition of a key
print(c_key.chromatic_transpose(2))  # Output: D

# Diatonic transposition (scale-based)
print(c_key.diatonic_transpose(2))  # Output: E
