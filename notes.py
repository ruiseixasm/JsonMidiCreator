
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
    