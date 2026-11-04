from jsonmidicreator import *

# Start by defining the sweeper function, where n is the number of notes being sweep
sweeper = lambda clip, n: (
	clip << Note() * (n + 1) % list(),
    clip << Resize(Beats(2)),
    clip * 4
)

# Now one creates the Sweep iterator
i_sweep = ISweep(sweeper)

phone_ring = Clip(Title("Office Phone Ring Sound"), TimeSignature(6), Gate(0.5))

# As you can see, the operator `>>` on a `Transformation` operand, auto calls the usual `Plot` operand.
phone_ring >>= i_sweep