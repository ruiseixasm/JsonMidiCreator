from jsonmidicreator import *


def articulator_1(clip: 'Clip', axes: list[int]) -> 'Clip':
    parameter_1 = axes[0]
    if parameter_1 > 0:
        clip << Note(Gate(0.5)) * parameter_1 % list()
        clip << Resize(Beats(2))
        clip *= 4
    return clip



def articulator_2(clip: 'Clip', axes: list[int]) -> 'Clip':
    cv0 = axes[0]
    if cv0 > 0:
        splitter = Split() * (10 * cv0)
        clip << splitter
    cv1 = axes[1]
    if cv1 > 0:
        degrees = [Degree()] * 10
        untamed = Modulo() * (10 * cv1)
        clip << untamed % degrees
    return clip



# Clip([Note(Measures(2))]) >> ArticulatedPlot(articulator_2, "MPK")




def articulator_3(clip: 'Clip', axes: list[int]) -> 'Clip':
    cv0 = axes[0]
    setting_durations = IChooseDuration()
    for _ in range(cv0):
        clip << setting_durations
    return clip



Note() * 4 >> ArticulatedPlot(articulator_3)


