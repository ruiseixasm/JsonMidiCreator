from jsonmidicreator import *


def generator(clip: 'Clip', controller_values: list[int]) -> 'Clip':
    parameter_1 = controller_values[0]
    if parameter_1 > 0:
        clip << Note(Gate(0.5)) * parameter_1 % list(),
        clip << Resize(Beats(2)),
        clip * 4
    return clip

Clip() >> ControlledPlot(generator, "MPK")


