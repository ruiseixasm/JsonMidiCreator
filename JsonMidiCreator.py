from staff import *
from operand import *
from element import *
from creator import *

# print("Test Creator")

# global objects

set_global_staff(Staff(tempo=110)).setData__measures(6)

# element ojects

global_clock = Clock()
clock_serialization = global_clock.getSerialization()
Creator().saveJsonMidiCreator(clock_serialization, "_Clock_jsonMidiCreator.json")
first_note = Note() << (Position() << Beat(3) << Step(2))
note_serialization = first_note.getSerialization()
Creator().saveJsonMidiCreator(note_serialization, "_Note_jsonMidiCreator.json")

# repeat_operand = Repeat(Channel(), 10)

base_note = Note() << (Duration() << NoteValue(1/16))
second_note = base_note / (Duration() << Identity() << NoteValue(2))
trigger_notes = [
        base_note.copy() << (Position() << Step(0)),
        base_note.copy() << (Position() << Step(1)),
        base_note.copy() << (Position() << Step(2)),
        base_note.copy() << (Position() << Step(3)),
        base_note.copy() << (Position() << Step(4)),
        base_note.copy() << (Position() << Step(5)),
        base_note.copy() << (Position() << Step(6)),
        base_note.copy() << (Position() << Step(7))
    ]
first_sequence = Sequence() << (Position() << Measure(1))
first_sequence << MultiElements(trigger_notes)
first_sequence << Channel(10)
sequence_serialization = first_sequence.getSerialization()
Creator().saveJsonMidiCreator(sequence_serialization, "_Sequence_jsonMidiCreator.json")

second_sequence = first_sequence.copy()
second_sequence << (Position() << Measure(2))
second_sequence /= Inner(Position() << Identity() << Step(2))
second_sequence /= Inner(Duration() << Identity() << NoteValue(2))

all_elements = MultiElements(first_sequence) + MultiElements(second_sequence)
all_elements += first_note
all_elements += global_clock

play_list = all_elements.getPlayList()
# print(play_list)

# first_sequence = Sequence(10, 60, Length(beats=2), trigger_notes)
# second_sequence = first_sequence.copy()
# second_sequence += Position(steps=2)

# print(second_sequence.getSerialization())
# print(Length(beats=4).getTime_ms())
# print(Length(measures=1).getTime_ms())
# print(Length(beats=4) == Length(measures=1))

# placed_elements = Composition()
# placed_elements.placeElement(default_clock, Position(0))
# placed_elements.placeElement(default_note, Position(beats=1))
# placed_elements.placeElement(first_sequence, Position(1))
# placed_elements.placeElement(second_sequence, Position(1))

# placed_elements.setData__device_list();
# elements_list = placed_elements.getPlayList()

# print(elements_list)
# print(isinstance(default_note.getData__device_list(), list))
# print(isinstance(placed_elements.getData__device_list(), list))

# creator objects

# default_creator = creator.PlayList()
# default_creator.saveJsonMidiPlay(elements_list, "example_play_file.json")
# default_creator.jsonMidiPlay(elements_list)

# default_creator.saveJsonMidiCreator(second_sequence.getSerialization(), "_jsonMidiCreator.json")
# print(default_creator.loadJsonMidiCreator("_jsonMidiCreator.json"))

Creator().jsonMidiPlay(play_list).saveJsonMidiPlay(play_list, "example_play_file.json")