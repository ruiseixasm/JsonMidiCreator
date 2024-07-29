
class Length:
    
    def __init__(self, measures: float = 1, beats: float = 0, note: float = 0, steps: float = 0):
        self._measures = measures
        self._beats = beats
        self._note = note
        self._steps = steps


    # adding two lengths 
    def __add__(self, other_length):
        return Length(
                self._measures + other_length._measures,
                self._beats + other_length._beats,
                self._note + other_length._note,
                self._steps + other_length._steps
            )
    

class Duration(Length):
    
    def __init__(self, measures: float = 0, beats: float = 0, note: float = 1/4, steps: float = 0):
        super().__init__(measures, beats, note, steps)
    
    # adding two durations 
    def __add__(self, other_length: Length) -> 'Duration':
        return self + other_length
    

class Position:
    pass

class Duration:
    pass

class Velocity:
    pass

# Example list of note operands
trigger_note = [Position(), Duration(), Velocity()]

# Initialize variables
on_position = None
with_duration = None
with_velocity = None

# Match and assign
for note_operand in trigger_note:
    match note_operand:
        case Position():
            on_position = note_operand
        case Duration():
            with_duration = note_operand
        case Velocity():
            with_velocity = note_operand

# Print results
print(f"on_position: {on_position}")
print(f"with_duration: {with_duration}")
print(f"with_velocity: {with_velocity}")
