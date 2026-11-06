from jsonmidicreator import *


def generator_1(clip: 'Clip', controller_values: list[int]) -> 'Clip':
    parameter_1 = controller_values[0]
    if parameter_1 > 0:
        clip << Note(Gate(0.5)) * parameter_1 % list()
        clip << Resize(Beats(2))
        clip *= 4
    return clip



def generator_2(clip: 'Clip', controller_values: list[int]) -> 'Clip':
    cv0 = controller_values[0]
    if cv0 > 0:
        splitter = Split() * (10 * cv0)
        clip << splitter
    cv1 = controller_values[1]
    if cv1 > 0:
        degrees = [Degree()] * 10
        untamed = Untamed() * (10 * cv1)
        clip << untamed % degrees
    return clip



Clip([Note(Measures(2))]) >> ControlledPlot(generator_2, "MPK")


